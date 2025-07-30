from typing import Optional, Dict, Any, Self, List, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

if TYPE_CHECKING:
    from infradsl.core.interfaces.provider import ProviderInterface

from ...core.nexus.base_resource import BaseResource, ResourceSpec


class FirewallDirection(Enum):
    """Firewall rule direction"""
    INGRESS = "INGRESS"
    EGRESS = "EGRESS"


class FirewallAction(Enum):
    """Firewall rule action"""
    ALLOW = "allow"
    DENY = "deny"


class Protocol(Enum):
    """Network protocols"""
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    ESP = "esp"
    AH = "ah"
    SCTP = "sctp"
    ALL = "all"


@dataclass
class FirewallRule:
    """Individual firewall rule"""
    name: str
    direction: FirewallDirection
    action: FirewallAction
    priority: int = 1000
    
    # Traffic specification
    source_ranges: List[str] = field(default_factory=list)
    destination_ranges: List[str] = field(default_factory=list)
    source_tags: List[str] = field(default_factory=list)
    target_tags: List[str] = field(default_factory=list)
    
    # Protocol and ports
    protocols: List[Dict[str, Any]] = field(default_factory=list)
    
    # Description
    description: str = ""


@dataclass
class VPCSpec(ResourceSpec):
    """VPC specification"""
    name: str
    auto_create_subnetworks: bool = False
    routing_mode: str = "REGIONAL"  # REGIONAL or GLOBAL
    
    
@dataclass
class SubnetSpec(ResourceSpec):
    """Subnet specification"""  
    name: str
    ip_cidr_range: str
    region: str
    private_ip_google_access: bool = True
    
    
@dataclass
class VPCFirewallSpec(ResourceSpec):
    """Specification for VPC with firewall rules"""
    
    # VPC configuration
    vpc_config: Optional[VPCSpec] = None
    
    # Subnets
    subnets: List[SubnetSpec] = field(default_factory=list)
    
    # Firewall rules
    firewall_rules: List[FirewallRule] = field(default_factory=list)
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class VPCFirewall(BaseResource):
    """
    GCP VPC with firewall rules using Rails-like conventions.
    
    Examples:
        # Simple VPC with basic rules
        vpc = (VPCFirewall("my-vpc")
               .custom_mode()
               .subnet("web-subnet", "10.0.1.0/24", "us-central1")
               .subnet("db-subnet", "10.0.2.0/24", "us-central1")
               .allow_http_https()
               .allow_ssh())
        
        # Production VPC with comprehensive rules
        prod_vpc = (VPCFirewall("prod-vpc")
                   .custom_mode()
                   .subnet("public-subnet", "10.1.1.0/24", "us-central1")
                   .subnet("private-subnet", "10.1.2.0/24", "us-central1")
                   .allow_internal()
                   .allow_ssh_from("203.0.113.0/24")
                   .allow_port(443, source_ranges=["0.0.0.0/0"])
                   .deny_all_ingress()
                   .production())
        
        # Development VPC (permissive)
        dev_vpc = (VPCFirewall("dev-vpc")
                  .auto_mode()
                  .allow_all_internal()
                  .allow_ssh()
                  .allow_http_https()
                  .development())
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.spec: VPCFirewallSpec = self._create_spec()
        self.metadata.annotations["resource_type"] = "VPCFirewall"
        
        # Initialize VPC config
        self.spec.vpc_config = VPCSpec(name=name)
        
    def _create_spec(self) -> VPCFirewallSpec:
        return VPCFirewallSpec()
        
    def _validate_spec(self) -> None:
        """Validate VPC and firewall specification"""
        if not self.spec.vpc_config:
            raise ValueError("VPC configuration is required")
            
        # Validate CIDR ranges for custom mode
        if not self.spec.vpc_config.auto_create_subnetworks and not self.spec.subnets:
            raise ValueError("Custom mode VPC requires at least one subnet")
            
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        config = {
            "vpc_name": self.spec.vpc_config.name,
            "auto_create_subnetworks": self.spec.vpc_config.auto_create_subnetworks,
            "routing_mode": self.spec.vpc_config.routing_mode,
            "subnets": [self._subnet_to_config(subnet) for subnet in self.spec.subnets],
            "firewall_rules": [self._firewall_rule_to_config(rule) for rule in self.spec.firewall_rules],
            "labels": {**self.spec.labels, **self.metadata.to_tags()},
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
        
    def _subnet_to_config(self, subnet: SubnetSpec) -> Dict[str, Any]:
        """Convert subnet spec to configuration"""
        return {
            "name": subnet.name,
            "ip_cidr_range": subnet.ip_cidr_range,
            "region": subnet.region,
            "private_ip_google_access": subnet.private_ip_google_access
        }
        
    def _firewall_rule_to_config(self, rule: FirewallRule) -> Dict[str, Any]:
        """Convert firewall rule to configuration"""
        config = {
            "name": rule.name,
            "direction": rule.direction.value,
            "priority": rule.priority,
            "network": self.spec.vpc_config.name,
            "description": rule.description or f"Firewall rule {rule.name}"
        }
        
        # Action and protocol
        if rule.action == FirewallAction.ALLOW:
            config["allow"] = rule.protocols
        else:
            config["deny"] = rule.protocols
            
        # Source/destination configuration
        if rule.direction == FirewallDirection.INGRESS:
            if rule.source_ranges:
                config["source_ranges"] = rule.source_ranges
            if rule.source_tags:
                config["source_tags"] = rule.source_tags
        else:  # EGRESS
            if rule.destination_ranges:
                config["destination_ranges"] = rule.destination_ranges
                
        if rule.target_tags:
            config["target_tags"] = rule.target_tags
            
        return config

    def _to_gcp_config(self) -> Dict[str, Any]:
        """Convert to GCP VPC configuration"""
        config = {
            "resource_type": "compute_network"
        }
        
        return config
        
    # Fluent interface methods
    
    # VPC mode configuration
    
    def auto_mode(self) -> Self:
        """Use auto mode (automatic subnets) (chainable)"""
        self.spec.vpc_config.auto_create_subnetworks = True
        return self
        
    def custom_mode(self) -> Self:
        """Use custom mode (manual subnets) (chainable)"""
        self.spec.vpc_config.auto_create_subnetworks = False
        return self
        
    def global_routing(self) -> Self:
        """Use global routing mode (chainable)"""
        self.spec.vpc_config.routing_mode = "GLOBAL"
        return self
        
    def regional_routing(self) -> Self:
        """Use regional routing mode (chainable)"""
        self.spec.vpc_config.routing_mode = "REGIONAL"
        return self
        
    # Subnet management
    
    def subnet(self, name: str, cidr: str, region: str, private_google_access: bool = True) -> Self:
        """Add subnet (chainable)"""
        subnet = SubnetSpec(
            name=name,
            ip_cidr_range=cidr,
            region=region,
            private_ip_google_access=private_google_access
        )
        self.spec.subnets.append(subnet)
        return self
        
    def public_subnet(self, name: str, cidr: str, region: str) -> Self:
        """Add public subnet (chainable)"""
        return self.subnet(name, cidr, region, private_google_access=False)
        
    def private_subnet(self, name: str, cidr: str, region: str) -> Self:
        """Add private subnet (chainable)"""
        return self.subnet(name, cidr, region, private_google_access=True)
        
    # Firewall rule helpers
    
    def _add_firewall_rule(self, rule: FirewallRule) -> Self:
        """Add firewall rule"""
        self.spec.firewall_rules.append(rule)
        return self
        
    def firewall_rule(self, name: str, direction: FirewallDirection, action: FirewallAction,
                     protocol: str, ports: List[Union[int, str]] = None,
                     source_ranges: List[str] = None, target_tags: List[str] = None,
                     priority: int = 1000) -> Self:
        """Add custom firewall rule (chainable)"""
        protocols = []
        
        if protocol.lower() == "all":
            protocols = [{"IPProtocol": "all"}]
        else:
            proto_config = {"IPProtocol": protocol.lower()}
            if ports:
                proto_config["ports"] = [str(p) for p in ports]
            protocols.append(proto_config)
            
        rule = FirewallRule(
            name=f"{self.name}-{name}",
            direction=direction,
            action=action,
            priority=priority,
            protocols=protocols,
            source_ranges=source_ranges or [],
            target_tags=target_tags or []
        )
        
        return self._add_firewall_rule(rule)
        
    # Common firewall rules
    
    def allow_ssh(self, source_ranges: List[str] = None, target_tags: List[str] = None) -> Self:
        """Allow SSH access (chainable)"""
        return self.firewall_rule(
            "allow-ssh",
            FirewallDirection.INGRESS,
            FirewallAction.ALLOW,
            "tcp",
            [22],
            source_ranges or ["0.0.0.0/0"],
            target_tags
        )
        
    def allow_ssh_from(self, source_range: str, target_tags: List[str] = None) -> Self:
        """Allow SSH from specific source (chainable)"""
        return self.allow_ssh([source_range], target_tags)
        
    def allow_http_https(self, target_tags: List[str] = None) -> Self:
        """Allow HTTP and HTTPS traffic (chainable)"""
        self.allow_http(target_tags)
        self.allow_https(target_tags)
        return self
        
    def allow_http(self, target_tags: List[str] = None) -> Self:
        """Allow HTTP traffic (chainable)"""
        return self.firewall_rule(
            "allow-http",
            FirewallDirection.INGRESS,
            FirewallAction.ALLOW,
            "tcp",
            [80],
            ["0.0.0.0/0"],
            target_tags
        )
        
    def allow_https(self, target_tags: List[str] = None) -> Self:
        """Allow HTTPS traffic (chainable)"""
        return self.firewall_rule(
            "allow-https",
            FirewallDirection.INGRESS,
            FirewallAction.ALLOW,
            "tcp",
            [443],
            ["0.0.0.0/0"],
            target_tags
        )
        
    def allow_port(self, port: int, protocol: str = "tcp", source_ranges: List[str] = None,
                  target_tags: List[str] = None) -> Self:
        """Allow specific port (chainable)"""
        return self.firewall_rule(
            f"allow-{protocol}-{port}",
            FirewallDirection.INGRESS,
            FirewallAction.ALLOW,
            protocol,
            [port],
            source_ranges or ["0.0.0.0/0"],
            target_tags
        )
        
    def allow_ports(self, ports: List[int], protocol: str = "tcp", 
                   source_ranges: List[str] = None, target_tags: List[str] = None) -> Self:
        """Allow multiple ports (chainable)"""
        port_range = f"{min(ports)}-{max(ports)}" if len(ports) > 1 else str(ports[0])
        return self.firewall_rule(
            f"allow-{protocol}-ports",
            FirewallDirection.INGRESS,
            FirewallAction.ALLOW,
            protocol,
            ports,
            source_ranges or ["0.0.0.0/0"],
            target_tags
        )
        
    def allow_internal(self, internal_ranges: List[str] = None) -> Self:
        """Allow internal VPC traffic (chainable)"""
        ranges = internal_ranges or ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
        return self.firewall_rule(
            "allow-internal",
            FirewallDirection.INGRESS,
            FirewallAction.ALLOW,
            "all",
            None,
            ranges
        )
        
    def allow_all_internal(self) -> Self:
        """Allow all internal traffic (chainable)"""
        # Get CIDR ranges from subnets
        internal_ranges = [subnet.ip_cidr_range for subnet in self.spec.subnets]
        if not internal_ranges:
            internal_ranges = ["10.0.0.0/8"]  # Default private range
        return self.allow_internal(internal_ranges)
        
    def deny_all_ingress(self, priority: int = 65534) -> Self:
        """Deny all ingress traffic (low priority) (chainable)"""
        return self.firewall_rule(
            "deny-all-ingress",
            FirewallDirection.INGRESS,
            FirewallAction.DENY,
            "all",
            None,
            ["0.0.0.0/0"],
            None,
            priority
        )
        
    def deny_all_egress(self, priority: int = 65534) -> Self:
        """Deny all egress traffic (low priority) (chainable)"""
        rule = FirewallRule(
            name=f"{self.name}-deny-all-egress",
            direction=FirewallDirection.EGRESS,
            action=FirewallAction.DENY,
            priority=priority,
            protocols=[{"IPProtocol": "all"}],
            destination_ranges=["0.0.0.0/0"]
        )
        return self._add_firewall_rule(rule)
        
    # Application-specific rules
    
    def allow_database(self, port: int = 5432, source_tags: List[str] = None) -> Self:
        """Allow database access (chainable)"""
        return self.firewall_rule(
            "allow-database",
            FirewallDirection.INGRESS,
            FirewallAction.ALLOW,
            "tcp",
            [port],
            None,  # No source ranges, use tags
            source_tags or ["app-server"]
        )
        
    def allow_redis(self, source_tags: List[str] = None) -> Self:
        """Allow Redis access (chainable)"""
        return self.allow_database(6379, source_tags)
        
    def allow_mysql(self, source_tags: List[str] = None) -> Self:
        """Allow MySQL access (chainable)"""
        return self.allow_database(3306, source_tags)
        
    def allow_postgresql(self, source_tags: List[str] = None) -> Self:
        """Allow PostgreSQL access (chainable)"""
        return self.allow_database(5432, source_tags)
        
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
                .custom_mode()
                .regional_routing()
                .label("environment", "production"))
                
    def staging(self) -> Self:
        """Configure for staging environment (chainable)"""
        return (self
                .custom_mode()
                .regional_routing()
                .label("environment", "staging"))
                
    def development(self) -> Self:
        """Configure for development environment (chainable)"""
        return (self
                .auto_mode()
                .regional_routing()
                .label("environment", "development"))
                
    # Provider implementation methods
    
    def _provider_create(self) -> Dict[str, Any]:
        """Create the VPC and firewall rules via provider"""
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
        """Update the VPC and firewall rules via provider"""
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
        """Destroy the VPC and firewall rules via provider"""
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
    
    def get_vpc_name(self) -> str:
        """Get VPC name"""
        return self.spec.vpc_config.name
        
    def get_subnets(self) -> List[SubnetSpec]:
        """Get subnet configurations"""
        return self.spec.subnets.copy()