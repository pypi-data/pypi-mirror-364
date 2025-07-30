from typing import Optional, Dict, Any, Self, List, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

if TYPE_CHECKING:
    from infradsl.core.interfaces.provider import ProviderInterface
    from .vpc import VPCNetwork

from ...core.nexus.base_resource import BaseResource, ResourceSpec


class NATSourceType(Enum):
    """Source type for Cloud NAT"""
    ALL_SUBNETWORKS_ALL_IP_RANGES = "ALL_SUBNETWORKS_ALL_IP_RANGES"
    ALL_SUBNETWORKS_ALL_PRIMARY_IP_RANGES = "ALL_SUBNETWORKS_ALL_PRIMARY_IP_RANGES"
    LIST_OF_SUBNETWORKS = "LIST_OF_SUBNETWORKS"


class LoggingFilter(Enum):
    """Cloud NAT logging filter"""
    ERRORS_ONLY = "ERRORS_ONLY"
    TRANSLATIONS_ONLY = "TRANSLATIONS_ONLY"
    ALL = "ALL"


@dataclass
class SubnetToNAT:
    """Subnet configuration for NAT"""
    name: str
    source_ip_ranges_to_nat: List[str] = field(default_factory=lambda: ["ALL_IP_RANGES"])
    secondary_ip_range_names: List[str] = field(default_factory=list)


@dataclass
class CloudNATSpec(ResourceSpec):
    """Specification for Cloud NAT"""
    
    # Basic configuration
    region: str = ""
    router_name: str = ""
    
    # Source configuration
    source_subnetwork_ip_ranges_to_nat: NATSourceType = NATSourceType.ALL_SUBNETWORKS_ALL_IP_RANGES
    subnetworks: List[SubnetToNAT] = field(default_factory=list)
    
    # IP allocation
    nat_ip_allocate_option: str = "AUTO_ONLY"  # AUTO_ONLY, MANUAL_ONLY
    nat_ips: List[str] = field(default_factory=list)  # Static IP addresses
    
    # Port allocation
    min_ports_per_vm: int = 64
    max_ports_per_vm: Optional[int] = None
    enable_dynamic_port_allocation: bool = False
    
    # Timeouts
    udp_idle_timeout_sec: int = 30
    tcp_established_idle_timeout_sec: int = 1200
    tcp_transitory_idle_timeout_sec: int = 30
    tcp_time_wait_timeout_sec: int = 120
    icmp_idle_timeout_sec: int = 30
    
    # Logging
    enable_logging: bool = False
    log_filter: LoggingFilter = LoggingFilter.ERRORS_ONLY
    
    # Advanced features
    enable_endpoint_independent_mapping: bool = True
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class CloudNAT(BaseResource):
    """
    GCP Cloud NAT for outbound internet connectivity from private instances with Rails-like conventions.
    
    Examples:
        # Simple auto NAT for all subnets
        nat = (CloudNAT("main-nat")
               .region("us-central1")
               .router("main-router")
               .auto_allocate_ips()
               .all_subnets()
               .logging())
        
        # NAT with manual IP allocation
        nat = (CloudNAT("prod-nat")
               .region("us-central1")
               .router("prod-router")
               .manual_ips(["34.123.45.67", "34.123.45.68"])
               .all_subnets()
               .port_range(128, 1024)
               .timeouts(tcp_established=3600, udp=60)
               .production())
        
        # NAT for specific subnets only
        selective_nat = (CloudNAT("backend-nat")
                        .region("us-central1")
                        .router("backend-router")
                        .subnet("backend-subnet", ["PRIMARY_IP_RANGE"])
                        .subnet("database-subnet", ["ALL_IP_RANGES"])
                        .auto_allocate_ips()
                        .logging(filter="ALL"))
                        
        # High-performance NAT
        perf_nat = (CloudNAT("high-perf-nat")
                   .region("us-central1")
                   .router("perf-router")
                   .manual_ips(static_ips)  # List of reserved IPs
                   .port_range(256, 2048)
                   .dynamic_ports()
                   .endpoint_independent_mapping()
                   .production())
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.spec: CloudNATSpec = self._create_spec()
        self.metadata.annotations["resource_type"] = "CloudNAT"
        
    def _create_spec(self) -> CloudNATSpec:
        # Initialize with sensible defaults
        spec = CloudNATSpec()
        return spec
        
    def _validate_spec(self) -> None:
        """Validate Cloud NAT specification"""
        if not self.spec.region:
            raise ValueError("Region is required for Cloud NAT")
            
        if not self.spec.router_name:
            raise ValueError("Cloud Router name is required for Cloud NAT")
            
        if self.spec.nat_ip_allocate_option == "MANUAL_ONLY" and not self.spec.nat_ips:
            raise ValueError("Manual IP allocation requires at least one static IP")
            
        if self.spec.source_subnetwork_ip_ranges_to_nat == NATSourceType.LIST_OF_SUBNETWORKS and not self.spec.subnetworks:
            raise ValueError("LIST_OF_SUBNETWORKS requires at least one subnet configuration")
            
        if self.spec.max_ports_per_vm and self.spec.max_ports_per_vm < self.spec.min_ports_per_vm:
            raise ValueError("max_ports_per_vm must be greater than min_ports_per_vm")
            
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        config = {
            "name": self.metadata.name,
            "region": self.spec.region,
            "router": self.spec.router_name,
            "source_subnetwork_ip_ranges_to_nat": self.spec.source_subnetwork_ip_ranges_to_nat.value,
            "nat_ip_allocate_option": self.spec.nat_ip_allocate_option,
            "min_ports_per_vm": self.spec.min_ports_per_vm,
            "udp_idle_timeout_sec": self.spec.udp_idle_timeout_sec,
            "tcp_established_idle_timeout_sec": self.spec.tcp_established_idle_timeout_sec,
            "tcp_transitory_idle_timeout_sec": self.spec.tcp_transitory_idle_timeout_sec,
            "tcp_time_wait_timeout_sec": self.spec.tcp_time_wait_timeout_sec,
            "icmp_idle_timeout_sec": self.spec.icmp_idle_timeout_sec,
            "enable_endpoint_independent_mapping": self.spec.enable_endpoint_independent_mapping,
            "labels": {**self.spec.labels, **self.metadata.to_tags()},
        }
        
        # Optional configurations
        if self.spec.nat_ips:
            config["nat_ips"] = self.spec.nat_ips
            
        if self.spec.max_ports_per_vm:
            config["max_ports_per_vm"] = self.spec.max_ports_per_vm
            
        if self.spec.enable_dynamic_port_allocation:
            config["enable_dynamic_port_allocation"] = True
            
        if self.spec.subnetworks:
            config["subnetworks"] = [
                {
                    "name": subnet.name,
                    "source_ip_ranges_to_nat": subnet.source_ip_ranges_to_nat,
                    "secondary_ip_range_names": subnet.secondary_ip_range_names
                }
                for subnet in self.spec.subnetworks
            ]
            
        # Logging configuration
        if self.spec.enable_logging:
            config["log_config"] = {
                "enable": True,
                "filter": self.spec.log_filter.value
            }

        # Provider-specific mappings
        if hasattr(self._provider, 'config') and hasattr(self._provider.config, 'type'):
            provider_type_str = self._provider.config.type.value.lower()
        else:
            provider_type_str = str(self._provider).lower()

        if provider_type_str == "gcp":
            config.update(self._to_gcp_config())

        # Apply provider-specific overrides
        config.update(self.spec.provider_config)

        return config

    def _to_gcp_config(self) -> Dict[str, Any]:
        """Convert to GCP Cloud NAT configuration"""
        config = {
            "resource_type": "cloud_nat"
        }
        return config
        
    # Fluent interface methods
    
    # Basic configuration
    
    def region(self, region_name: str) -> Self:
        """Set region (chainable)"""
        self.spec.region = region_name
        return self
        
    def router(self, router_name: str) -> Self:
        """Set Cloud Router name (chainable)"""
        self.spec.router_name = router_name
        return self
        
    # Source configuration
    
    def all_subnets(self, include_secondary: bool = True) -> Self:
        """NAT for all subnets (chainable)"""
        if include_secondary:
            self.spec.source_subnetwork_ip_ranges_to_nat = NATSourceType.ALL_SUBNETWORKS_ALL_IP_RANGES
        else:
            self.spec.source_subnetwork_ip_ranges_to_nat = NATSourceType.ALL_SUBNETWORKS_ALL_PRIMARY_IP_RANGES
        self.spec.subnetworks = []
        return self
        
    def subnet(self, subnet_name: str, ip_ranges: List[str] = None, 
              secondary_ranges: List[str] = None) -> Self:
        """Add specific subnet for NAT (chainable)"""
        if self.spec.source_subnetwork_ip_ranges_to_nat != NATSourceType.LIST_OF_SUBNETWORKS:
            self.spec.source_subnetwork_ip_ranges_to_nat = NATSourceType.LIST_OF_SUBNETWORKS
            
        ip_ranges = ip_ranges or ["ALL_IP_RANGES"]
        secondary_ranges = secondary_ranges or []
        
        subnet_config = SubnetToNAT(
            name=subnet_name,
            source_ip_ranges_to_nat=ip_ranges,
            secondary_ip_range_names=secondary_ranges
        )
        
        self.spec.subnetworks.append(subnet_config)
        return self
        
    def primary_ranges_only(self, subnet_name: str) -> Self:
        """NAT only primary IP ranges for subnet (chainable)"""
        return self.subnet(subnet_name, ["PRIMARY_IP_RANGE"])
        
    def secondary_range(self, subnet_name: str, range_name: str) -> Self:
        """Add secondary range to existing subnet NAT config (chainable)"""
        for subnet in self.spec.subnetworks:
            if subnet.name == subnet_name:
                subnet.secondary_ip_range_names.append(range_name)
                return self
        raise ValueError(f"Subnet '{subnet_name}' not found in NAT configuration")
        
    # IP allocation
    
    def auto_allocate_ips(self) -> Self:
        """Use automatic IP allocation (chainable)"""
        self.spec.nat_ip_allocate_option = "AUTO_ONLY"
        self.spec.nat_ips = []
        return self
        
    def manual_ips(self, ip_addresses: List[str]) -> Self:
        """Use manual IP allocation (chainable)"""
        self.spec.nat_ip_allocate_option = "MANUAL_ONLY"
        self.spec.nat_ips = ip_addresses.copy()
        return self
        
    def add_ip(self, ip_address: str) -> Self:
        """Add IP address for manual allocation (chainable)"""
        if self.spec.nat_ip_allocate_option != "MANUAL_ONLY":
            self.spec.nat_ip_allocate_option = "MANUAL_ONLY"
        if ip_address not in self.spec.nat_ips:
            self.spec.nat_ips.append(ip_address)
        return self
        
    # Port allocation
    
    def port_range(self, min_ports: int, max_ports: int = None) -> Self:
        """Set port range per VM (chainable)"""
        self.spec.min_ports_per_vm = min_ports
        self.spec.max_ports_per_vm = max_ports
        return self
        
    def dynamic_ports(self, enabled: bool = True) -> Self:
        """Enable dynamic port allocation (chainable)"""
        self.spec.enable_dynamic_port_allocation = enabled
        return self
        
    # Timeouts
    
    def timeouts(self, udp: int = None, tcp_established: int = None, 
                tcp_transitory: int = None, tcp_time_wait: int = None, 
                icmp: int = None) -> Self:
        """Set timeout values (chainable)"""
        if udp is not None:
            self.spec.udp_idle_timeout_sec = udp
        if tcp_established is not None:
            self.spec.tcp_established_idle_timeout_sec = tcp_established
        if tcp_transitory is not None:
            self.spec.tcp_transitory_idle_timeout_sec = tcp_transitory
        if tcp_time_wait is not None:
            self.spec.tcp_time_wait_timeout_sec = tcp_time_wait
        if icmp is not None:
            self.spec.icmp_idle_timeout_sec = icmp
        return self
        
    def web_timeouts(self) -> Self:
        """Set timeouts optimized for web traffic (chainable)"""
        return self.timeouts(
            udp=30,
            tcp_established=1800,  # 30 minutes
            tcp_transitory=30,
            tcp_time_wait=60,
            icmp=30
        )
        
    def long_lived_timeouts(self) -> Self:
        """Set timeouts for long-lived connections (chainable)"""
        return self.timeouts(
            udp=300,
            tcp_established=7200,  # 2 hours
            tcp_transitory=120,
            tcp_time_wait=300,
            icmp=300
        )
        
    # Logging
    
    def logging(self, enabled: bool = True, filter: str = "ERRORS_ONLY") -> Self:
        """Enable Cloud NAT logging (chainable)"""
        self.spec.enable_logging = enabled
        if filter.upper() in [f.value for f in LoggingFilter]:
            self.spec.log_filter = LoggingFilter(filter.upper())
        return self
        
    def log_all(self) -> Self:
        """Log all NAT translations (chainable)"""
        return self.logging(True, "ALL")
        
    def log_errors_only(self) -> Self:
        """Log only errors (chainable)"""
        return self.logging(True, "ERRORS_ONLY")
        
    def log_translations_only(self) -> Self:
        """Log only successful translations (chainable)"""
        return self.logging(True, "TRANSLATIONS_ONLY")
        
    # Advanced features
    
    def endpoint_independent_mapping(self, enabled: bool = True) -> Self:
        """Enable endpoint independent mapping (chainable)"""
        self.spec.enable_endpoint_independent_mapping = enabled
        return self
        
    # Convenience methods for common patterns
    
    def high_availability(self, static_ips: List[str]) -> Self:
        """Configure for high availability (chainable)"""
        return (self
                .manual_ips(static_ips)
                .port_range(128, 1024)
                .dynamic_ports()
                .endpoint_independent_mapping()
                .long_lived_timeouts()
                .logging(True, "ERRORS_ONLY"))
                
    def cost_optimized(self) -> Self:
        """Configure for cost optimization (chainable)"""
        return (self
                .auto_allocate_ips()
                .port_range(64, 256)
                .web_timeouts()
                .logging(False))
                
    def high_throughput(self, static_ips: List[str]) -> Self:
        """Configure for high throughput (chainable)"""
        return (self
                .manual_ips(static_ips)
                .port_range(256, 2048)
                .dynamic_ports()
                .endpoint_independent_mapping()
                .web_timeouts()
                .log_errors_only())
                
    # LEGO principle - integration with other resources
    
    def for_vpc(self, vpc: "VPCNetwork", router_name: str = None) -> Self:
        """Configure NAT for a VPC network (chainable)"""
        if not router_name:
            router_name = f"{vpc.name}-router"
        return self.router(router_name)
        
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
        return (self
                .port_range(128, 512)
                .long_lived_timeouts()
                .endpoint_independent_mapping()
                .log_errors_only()
                .label("environment", "production"))
                
    def staging(self) -> Self:
        """Configure for staging environment (chainable)"""
        return (self
                .port_range(64, 256)
                .web_timeouts()
                .log_errors_only()
                .label("environment", "staging"))
                
    def development(self) -> Self:
        """Configure for development environment (chainable)"""
        return (self
                .auto_allocate_ips()
                .port_range(64, 128)
                .web_timeouts()
                .logging(False)
                .label("environment", "development"))
                
    # Provider implementation methods
    
    def _provider_create(self) -> Dict[str, Any]:
        """Create the Cloud NAT via provider"""
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
        """Update the Cloud NAT via provider"""
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
        """Destroy the Cloud NAT via provider"""
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
    
    def get_allocated_ips(self) -> List[str]:
        """Get allocated NAT IP addresses"""
        return self.spec.nat_ips.copy()
        
    def get_subnet_config(self, subnet_name: str) -> Optional[SubnetToNAT]:
        """Get subnet NAT configuration"""
        for subnet in self.spec.subnetworks:
            if subnet.name == subnet_name:
                return subnet
        return None