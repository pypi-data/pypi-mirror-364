from typing import Optional, Dict, Any, Self, List, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
import ipaddress

if TYPE_CHECKING:
    from infradsl.core.interfaces.provider import ProviderInterface

from ...core.nexus.base_resource import BaseResource, ResourceSpec


class RoutingMode(Enum):
    """VPC routing mode"""

    GLOBAL = "GLOBAL"
    REGIONAL = "REGIONAL"


class SubnetPurpose(Enum):
    """Subnet purpose for specialized subnets"""

    PRIVATE = "PRIVATE"
    INTERNAL_HTTPS_LOAD_BALANCER = "INTERNAL_HTTPS_LOAD_BALANCER"
    PRIVATE_SERVICE_CONNECT = "PRIVATE_SERVICE_CONNECT"
    REGIONAL_MANAGED_PROXY = "REGIONAL_MANAGED_PROXY"


@dataclass
class SecondaryRange:
    """Secondary IP range for subnets"""

    range_name: str
    ip_cidr_range: str


@dataclass
class SubnetConfig:
    """Subnet configuration"""

    name: str
    region: str
    ip_cidr_range: str
    purpose: Optional[SubnetPurpose] = None
    secondary_ip_ranges: List[SecondaryRange] = field(default_factory=list)
    private_ip_google_access: bool = True
    enable_flow_logs: bool = False
    log_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VPCSpec(ResourceSpec):
    """Specification for VPC Network"""

    # VPC configuration
    routing_mode: RoutingMode = RoutingMode.REGIONAL
    description: str = ""

    # Subnets
    subnets: List[SubnetConfig] = field(default_factory=list)
    auto_create_subnetworks: bool = False

    # MTU
    mtu: int = 1460  # Default GCP MTU

    # Firewall rules (enable default or not)
    enable_default_firewall_rules: bool = False

    # Labels
    labels: Dict[str, str] = field(default_factory=dict)

    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class VPCNetwork(BaseResource):
    """
    GCP VPC Network with subnets, secondary ranges, and advanced networking with Rails-like conventions.

    Examples:
        # Simple VPC with auto subnets
        vpc = (VPCNetwork("main-vpc")
               .description("Main application VPC")
               .regional_routing()
               .subnet("frontend", "us-central1", "10.0.1.0/24")
               .subnet("backend", "us-central1", "10.0.2.0/24")
               .subnet("database", "us-central1", "10.0.3.0/24")
               .private_google_access()
               .flow_logs())

        # Production VPC with secondary ranges for GKE
        gke_vpc = (VPCNetwork("gke-vpc")
                   .description("GKE cluster VPC with secondary ranges")
                   .global_routing()
                   .subnet("gke-nodes", "us-central1", "10.1.0.0/20")
                   .secondary_range("gke-nodes", "pods", "10.2.0.0/14")
                   .secondary_range("gke-nodes", "services", "10.6.0.0/20")
                   .private_google_access()
                   .production())

        # Multi-region VPC
        multi_region = (VPCNetwork("multi-region-vpc")
                       .global_routing()
                       .subnet("us-central", "us-central1", "10.10.0.0/16")
                       .subnet("europe-west", "europe-west1", "10.20.0.0/16")
                       .subnet("asia-east", "asia-east1", "10.30.0.0/16")
                       .private_google_access()
                       .flow_logs()
                       .production())

        # Specialized subnets for load balancers
        lb_vpc = (VPCNetwork("lb-vpc")
                  .subnet("main", "us-central1", "10.0.0.0/24")
                  .internal_lb_subnet("lb-subnet", "us-central1", "10.0.1.0/28")
                  .proxy_subnet("proxy-subnet", "us-central1", "10.0.2.0/24"))
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.spec: VPCSpec = self._create_spec()
        self.metadata.annotations["resource_type"] = "VPCNetwork"

    def _create_spec(self) -> VPCSpec:
        # Initialize with sensible defaults
        spec = VPCSpec(description=f"VPC network for {self.name}")
        return spec

    def _validate_spec(self) -> None:
        """Validate VPC specification"""
        # Validate CIDR ranges don't overlap
        primary_ranges = [subnet.ip_cidr_range for subnet in self.spec.subnets]
        self._validate_non_overlapping_cidrs(primary_ranges, "Primary subnet")

        # Validate secondary ranges within each subnet don't overlap
        for subnet in self.spec.subnets:
            if subnet.secondary_ip_ranges:
                secondary_ranges = [
                    sr.ip_cidr_range for sr in subnet.secondary_ip_ranges
                ]
                self._validate_non_overlapping_cidrs(
                    secondary_ranges, f"Secondary ranges in {subnet.name}"
                )

        # Validate MTU
        if self.spec.mtu < 1460 or self.spec.mtu > 1500:
            raise ValueError("MTU must be between 1460 and 1500")

    def _validate_non_overlapping_cidrs(self, cidrs: List[str], context: str) -> None:
        """Validate that CIDR ranges don't overlap"""
        networks = []
        for cidr in cidrs:
            try:
                network = ipaddress.ip_network(cidr, strict=False)
                networks.append(network)
            except ValueError as e:
                raise ValueError(f"Invalid CIDR range '{cidr}' in {context}: {e}")

        # Check for overlaps
        for i, net1 in enumerate(networks):
            for j, net2 in enumerate(networks[i + 1:], i + 1):
                if net1.overlaps(net2):
                    raise ValueError(
                        f"{context} CIDR ranges overlap: {cidrs[i]} and {cidrs[j]}"
                    )

    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        config = {
            "name": self.metadata.name,
            "routing_mode": self.spec.routing_mode.value,
            "description": self.spec.description,
            "auto_create_subnetworks": self.spec.auto_create_subnetworks,
            "mtu": self.spec.mtu,
            "subnets": [self._subnet_to_config(subnet) for subnet in self.spec.subnets],
            "labels": {**self.spec.labels, **self.metadata.to_tags()},
        }

        # Provider-specific mappings
        if hasattr(self._provider, "config") and hasattr(self._provider.config, "type"):
            provider_type_str = self._provider.config.type.value.lower()
        else:
            provider_type_str = str(self._provider).lower()

        if provider_type_str == "gcp":
            config.update(self._to_gcp_config())

        # Apply provider-specific overrides
        config.update(self.spec.provider_config)

        return config

    def _subnet_to_config(self, subnet: SubnetConfig) -> Dict[str, Any]:
        """Convert subnet configuration"""
        config = {
            "name": subnet.name,
            "region": subnet.region,
            "ip_cidr_range": subnet.ip_cidr_range,
            "private_ip_google_access": subnet.private_ip_google_access,
            "enable_flow_logs": subnet.enable_flow_logs,
        }

        if subnet.purpose:
            config["purpose"] = subnet.purpose.value

        if subnet.secondary_ip_ranges:
            config["secondary_ip_ranges"] = [
                {"range_name": sr.range_name, "ip_cidr_range": sr.ip_cidr_range}
                for sr in subnet.secondary_ip_ranges
            ]

        if subnet.log_config:
            config["log_config"] = subnet.log_config

        return config

    def _to_gcp_config(self) -> Dict[str, Any]:
        """Convert to GCP VPC configuration"""
        config = {"resource_type": "vpc_network"}

        # Add firewall rules if enabled
        if self.spec.enable_default_firewall_rules:
            config["enable_default_firewall_rules"] = True

        return config

    # Fluent interface methods

    # VPC configuration

    def description(self, desc: str) -> Self:
        """Set VPC description (chainable)"""
        self.spec.description = desc
        return self

    def global_routing(self) -> Self:
        """Enable global routing (chainable)"""
        self.spec.routing_mode = RoutingMode.GLOBAL
        return self

    def regional_routing(self) -> Self:
        """Enable regional routing (chainable)"""
        self.spec.routing_mode = RoutingMode.REGIONAL
        return self

    def auto_subnets(self, enabled: bool = True) -> Self:
        """Enable/disable auto subnet creation (chainable)"""
        self.spec.auto_create_subnetworks = enabled
        if enabled:
            # Clear manual subnets if auto is enabled
            self.spec.subnets = []
        return self

    def mtu(self, mtu_size: int) -> Self:
        """Set MTU size (chainable)"""
        if mtu_size < 1460 or mtu_size > 1500:
            raise ValueError("MTU must be between 1460 and 1500")
        self.spec.mtu = mtu_size
        return self

    def default_firewall_rules(self, enabled: bool = True) -> Self:
        """Enable default firewall rules (chainable)"""
        self.spec.enable_default_firewall_rules = enabled
        return self

    # Subnet management

    def subnet(
            self, name: str, region: str, cidr: str, purpose: SubnetPurpose = None
    ) -> Self:
        """Add subnet (chainable)"""
        subnet_config = SubnetConfig(
            name=f"{self.name}-{name}" if not name.startswith(self.name) else name,
            region=region,
            ip_cidr_range=cidr,
            purpose=purpose,
        )
        self.spec.subnets.append(subnet_config)
        return self

    def private_subnet(self, name: str, region: str, cidr: str) -> Self:
        """Add private subnet (chainable)"""
        return self.subnet(name, region, cidr, SubnetPurpose.PRIVATE)

    def internal_lb_subnet(self, name: str, region: str, cidr: str) -> Self:
        """Add internal load balancer subnet (chainable)"""
        return self.subnet(
            name, region, cidr, SubnetPurpose.INTERNAL_HTTPS_LOAD_BALANCER
        )

    def proxy_subnet(self, name: str, region: str, cidr: str) -> Self:
        """Add regional managed proxy subnet (chainable)"""
        return self.subnet(name, region, cidr, SubnetPurpose.REGIONAL_MANAGED_PROXY)

    def psc_subnet(self, name: str, region: str, cidr: str) -> Self:
        """Add Private Service Connect subnet (chainable)"""
        return self.subnet(name, region, cidr, SubnetPurpose.PRIVATE_SERVICE_CONNECT)

    # Secondary IP ranges

    def secondary_range(self, subnet_name: str, range_name: str, cidr: str) -> Self:
        """Add secondary IP range to subnet (chainable)"""
        # Find the subnet and add secondary range
        full_subnet_name = (
            f"{self.name}-{subnet_name}"
            if not subnet_name.startswith(self.name)
            else subnet_name
        )

        for subnet in self.spec.subnets:
            if subnet.name == full_subnet_name:
                secondary_range = SecondaryRange(
                    range_name=range_name, ip_cidr_range=cidr
                )
                subnet.secondary_ip_ranges.append(secondary_range)
                return self

        raise ValueError(f"Subnet '{full_subnet_name}' not found")

    # GKE-specific secondary ranges

    def gke_secondary_ranges(
            self, subnet_name: str, pods_cidr: str, services_cidr: str
    ) -> Self:
        """Add GKE secondary ranges for pods and services (chainable)"""
        return self.secondary_range(subnet_name, "gke-pods", pods_cidr).secondary_range(
            subnet_name, "gke-services", services_cidr
        )

    # Subnet features

    def private_google_access(
            self, subnet_name: str = None, enabled: bool = True
    ) -> Self:
        """Enable Private Google Access (chainable)"""
        if subnet_name:
            # Enable for specific subnet
            full_subnet_name = (
                f"{self.name}-{subnet_name}"
                if not subnet_name.startswith(self.name)
                else subnet_name
            )
            for subnet in self.spec.subnets:
                if subnet.name == full_subnet_name:
                    subnet.private_ip_google_access = enabled
                    return self
            raise ValueError(f"Subnet '{full_subnet_name}' not found")
        else:
            # Enable for all subnets
            for subnet in self.spec.subnets:
                subnet.private_ip_google_access = enabled
        return self

    def flow_logs(
            self,
            subnet_name: str = None,
            enabled: bool = True,
            aggregation_interval: str = "INTERVAL_5_SEC",
            flow_sampling: float = 0.5,
            metadata: str = "INCLUDE_ALL_METADATA",
    ) -> Self:
        """Enable VPC Flow Logs (chainable)"""
        log_config = {
            "aggregation_interval": aggregation_interval,
            "flow_sampling": flow_sampling,
            "metadata": metadata,
        }

        if subnet_name:
            # Enable for specific subnet
            full_subnet_name = (
                f"{self.name}-{subnet_name}"
                if not subnet_name.startswith(self.name)
                else subnet_name
            )
            for subnet in self.spec.subnets:
                if subnet.name == full_subnet_name:
                    subnet.enable_flow_logs = enabled
                    if enabled:
                        subnet.log_config = log_config
                    return self
            raise ValueError(f"Subnet '{full_subnet_name}' not found")
        else:
            # Enable for all subnets
            for subnet in self.spec.subnets:
                subnet.enable_flow_logs = enabled
                if enabled:
                    subnet.log_config = log_config
        return self

    # Multi-region helpers

    def us_regions(self, base_cidr: str = "10.0.0.0/8") -> Self:
        """Add subnets for common US regions (chainable)"""
        base_network = ipaddress.ip_network(base_cidr, strict=False)
        subnets = list(base_network.subnets(new_prefix=16))

        regions = [
            ("us-central1", "us-central"),
            ("us-east1", "us-east"),
            ("us-west1", "us-west"),
            ("us-west2", "us-west2"),
        ]

        for i, (region, name) in enumerate(regions[: len(subnets)]):
            self.subnet(name, region, str(subnets[i]))

        return self

    def europe_regions(self, base_cidr: str = "10.16.0.0/12") -> Self:
        """Add subnets for common Europe regions (chainable)"""
        base_network = ipaddress.ip_network(base_cidr, strict=False)
        subnets = list(base_network.subnets(new_prefix=16))

        regions = [
            ("europe-west1", "eu-west1"),
            ("europe-west2", "eu-west2"),
            ("europe-west3", "eu-west3"),
            ("europe-north1", "eu-north"),
        ]

        for i, (region, name) in enumerate(regions[: len(subnets)]):
            self.subnet(name, region, str(subnets[i]))

        return self

    def asia_regions(self, base_cidr: str = "10.32.0.0/12") -> Self:
        """Add subnets for common Asia regions (chainable)"""
        base_network = ipaddress.ip_network(base_cidr, strict=False)
        subnets = list(base_network.subnets(new_prefix=16))

        regions = [
            ("asia-east1", "asia-east1"),
            ("asia-northeast1", "asia-northeast1"),
            ("asia-southeast1", "asia-southeast1"),
            ("asia-south1", "asia-south1"),
        ]

        for i, (region, name) in enumerate(regions[: len(subnets)]):
            self.subnet(name, region, str(subnets[i]))

        return self

    # Common patterns

    def three_tier(self, region: str, base_cidr: str = "10.0.0.0/16") -> Self:
        """Create three-tier architecture subnets (chainable)"""
        base_network = ipaddress.ip_network(base_cidr, strict=False)
        subnets = list(base_network.subnets(new_prefix=24))

        return (
            self.subnet("web", region, str(subnets[0]))
            .subnet("app", region, str(subnets[1]))
            .subnet("db", region, str(subnets[2]))
        )

    def gke_cluster_subnets(
            self,
            region: str,
            nodes_cidr: str = "10.0.0.0/20",
            pods_cidr: str = "10.1.0.0/14",
            services_cidr: str = "10.5.0.0/20",
    ) -> Self:
        """Create GKE cluster subnets with secondary ranges (chainable)"""
        return self.subnet("gke-nodes", region, nodes_cidr).gke_secondary_ranges(
            "gke-nodes", pods_cidr, services_cidr
        )

    # Labels

    def label(self, key: str, value: str) -> Self:
        """Add a label (chainable)"""
        self.spec.labels[key] = value
        return self

    def labels(self, labels_dict: Dict[str, str] = None, **labels) -> Self:
        """Set multiple labels (chainable)"""
        if labels_dict:
            self.spec.labels.update(labels_dict)
        if labels:
            self.spec.labels.update(labels)
        return self

    # Environment-based conveniences

    def production(self) -> Self:
        """Configure for production environment (chainable)"""
        return (
            self.global_routing()
            .flow_logs()
            .private_google_access()
            .label("environment", "production")
        )

    def staging(self) -> Self:
        """Configure for staging environment (chainable)"""
        return (
            self.regional_routing()
            .private_google_access()
            .label("environment", "staging")
        )

    def development(self) -> Self:
        """Configure for development environment (chainable)"""
        return self.regional_routing().label("environment", "development")

    # Provider implementation methods

    def _provider_create(self) -> Dict[str, Any]:
        """Create the VPC via provider"""
        if not self._provider:
            raise ValueError("No provider attached")

        from typing import cast

        provider = cast("ProviderInterface", self._provider)

        config = self._to_provider_config()
        resource_type = config.pop("resource_type")

        return provider.create_resource(
            resource_type=resource_type, config=config, metadata=self.metadata
        )

    def _provider_update(self, diff: Dict[str, Any]) -> Dict[str, Any]:
        """Update the VPC via provider"""
        if not self._provider:
            raise ValueError("No provider attached")

        if not self.status.cloud_id:
            raise ValueError("Resource has no cloud ID")

        from typing import cast

        provider = cast("ProviderInterface", self._provider)

        config = self._to_provider_config()
        resource_type = config.pop("resource_type")

        return provider.update_resource(
            resource_id=self.status.cloud_id, resource_type=resource_type, updates=diff
        )

    def _provider_destroy(self) -> None:
        """Destroy the VPC via provider"""
        if not self._provider:
            raise ValueError("No provider attached")

        if not self.status.cloud_id:
            raise ValueError("Resource has no cloud ID")

        from typing import cast

        provider = cast("ProviderInterface", self._provider)

        config = self._to_provider_config()
        resource_type = config.pop("resource_type")

        provider.delete_resource(
            resource_id=self.status.cloud_id, resource_type=resource_type
        )

    # Convenience methods

    def get_subnet(self, name: str) -> Optional[SubnetConfig]:
        """Get subnet configuration by name"""
        full_name = f"{self.name}-{name}" if not name.startswith(self.name) else name
        for subnet in self.spec.subnets:
            if subnet.name == full_name:
                return subnet
        return None

    def get_subnet_cidr(self, name: str) -> Optional[str]:
        """Get subnet CIDR by name"""
        subnet = self.get_subnet(name)
        return subnet.ip_cidr_range if subnet else None

    def list_subnets(self) -> List[str]:
        """List all subnet names"""
        return [subnet.name for subnet in self.spec.subnets]

    def get_secondary_ranges(self, subnet_name: str) -> List[SecondaryRange]:
        """Get secondary ranges for a subnet"""
        subnet = self.get_subnet(subnet_name)
        return subnet.secondary_ip_ranges if subnet else []
