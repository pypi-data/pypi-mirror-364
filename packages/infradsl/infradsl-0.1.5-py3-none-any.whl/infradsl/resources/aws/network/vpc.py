from typing import Optional, Dict, Any, Self, List, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
import ipaddress

if TYPE_CHECKING:
    from infradsl.core.interfaces.provider import ProviderInterface

from ....core.nexus.base_resource import BaseResource, ResourceSpec


class Tenancy(Enum):
    """VPC instance tenancy"""
    DEFAULT = "default"
    DEDICATED = "dedicated"


class SubnetType(Enum):
    """Subnet type for AWS"""
    PUBLIC = "public"
    PRIVATE = "private"
    ISOLATED = "isolated"


@dataclass
class SubnetConfig:
    """AWS Subnet configuration"""
    name: str
    availability_zone: str
    cidr_block: str
    subnet_type: SubnetType = SubnetType.PRIVATE
    map_public_ip: bool = False
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class RouteTableConfig:
    """Route table configuration"""
    name: str
    subnets: List[str] = field(default_factory=list)
    routes: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AWSVPCSpec(ResourceSpec):
    """Specification for AWS VPC"""
    
    # VPC configuration
    cidr_block: str = "10.0.0.0/16"
    secondary_cidr_blocks: List[str] = field(default_factory=list)
    
    # DNS configuration
    enable_dns_hostnames: bool = True
    enable_dns_support: bool = True
    
    # Tenancy
    instance_tenancy: Tenancy = Tenancy.DEFAULT
    
    # Subnets
    subnets: List[SubnetConfig] = field(default_factory=list)
    
    # Route tables
    route_tables: List[RouteTableConfig] = field(default_factory=list)
    
    # Internet Gateway
    enable_internet_gateway: bool = True
    
    # VPC Flow Logs
    enable_flow_logs: bool = False
    flow_logs_destination: str = "cloud-watch-logs"  # cloud-watch-logs, s3
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class AWSVPC(BaseResource):
    """
    AWS VPC with subnets, routing, and advanced networking with Rails-like conventions.
    
    Examples:
        # Simple VPC with public/private subnets
        vpc = (AWSVPC("main-vpc")
               .cidr("10.0.0.0/16")
               .public_subnet("web", "us-east-1a", "10.0.1.0/24")
               .private_subnet("app", "us-east-1a", "10.0.2.0/24")
               .private_subnet("db", "us-east-1b", "10.0.3.0/24")
               .internet_gateway()
               .flow_logs()
               .production())
        
        # Multi-AZ VPC with three-tier architecture
        multi_az = (AWSVPC("prod-vpc")
                    .cidr("10.0.0.0/16")
                    .three_tier_multi_az("us-east-1", ["a", "b", "c"])
                    .internet_gateway()
                    .dns_hostnames()
                    .production())
        
        # Complex VPC with custom routing
        complex_vpc = (AWSVPC("complex-vpc")
                      .cidr("10.0.0.0/16")
                      .secondary_cidr("10.1.0.0/16")
                      .public_subnet("dmz", "us-east-1a", "10.0.1.0/24")
                      .private_subnet("apps", "us-east-1a", "10.0.2.0/24")
                      .isolated_subnet("data", "us-east-1a", "10.0.3.0/24")
                      .custom_route_table("apps-rt", ["apps"], [
                          {"destination": "0.0.0.0/0", "nat_gateway": "nat-gateway-id"}
                      ])
                      .production())
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.spec: AWSVPCSpec = self._create_spec()
        self.metadata.annotations["resource_type"] = "AWSVPC"
        
    def _create_spec(self) -> AWSVPCSpec:
        return AWSVPCSpec()
        
    def _validate_spec(self) -> None:
        """Validate AWS VPC specification"""
        # Validate CIDR blocks
        try:
            primary_network = ipaddress.ip_network(self.spec.cidr_block, strict=False)
        except ValueError as e:
            raise ValueError(f"Invalid primary CIDR block: {e}")
            
        # Validate secondary CIDR blocks
        for secondary in self.spec.secondary_cidr_blocks:
            try:
                ipaddress.ip_network(secondary, strict=False)
            except ValueError as e:
                raise ValueError(f"Invalid secondary CIDR block {secondary}: {e}")
                
        # Validate subnet CIDR blocks are within VPC CIDR
        all_cidrs = [self.spec.cidr_block] + self.spec.secondary_cidr_blocks
        for subnet in self.spec.subnets:
            subnet_network = ipaddress.ip_network(subnet.cidr_block, strict=False)
            
            # Check if subnet is within any of the VPC CIDR blocks
            subnet_within_vpc = False
            for vpc_cidr in all_cidrs:
                vpc_network = ipaddress.ip_network(vpc_cidr, strict=False)
                if subnet_network.subnet_of(vpc_network):
                    subnet_within_vpc = True
                    break
                    
            if not subnet_within_vpc:
                raise ValueError(f"Subnet {subnet.name} CIDR {subnet.cidr_block} is not within VPC CIDR blocks")
                
        # Validate no overlapping subnets
        subnet_cidrs = [subnet.cidr_block for subnet in self.spec.subnets]
        self._validate_non_overlapping_cidrs(subnet_cidrs, "Subnets")
        
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
            for j, net2 in enumerate(networks[i+1:], i+1):
                if net1.overlaps(net2):
                    raise ValueError(f"{context} CIDR ranges overlap: {cidrs[i]} and {cidrs[j]}")
                    
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        config = {
            "vpc_name": self.metadata.name,
            "cidr_block": self.spec.cidr_block,
            "secondary_cidr_blocks": self.spec.secondary_cidr_blocks,
            "enable_dns_hostnames": self.spec.enable_dns_hostnames,
            "enable_dns_support": self.spec.enable_dns_support,
            "instance_tenancy": self.spec.instance_tenancy.value,
            "enable_internet_gateway": self.spec.enable_internet_gateway,
            "enable_flow_logs": self.spec.enable_flow_logs,
            "flow_logs_destination": self.spec.flow_logs_destination,
            "subnets": [self._subnet_to_config(subnet) for subnet in self.spec.subnets],
            "route_tables": [self._route_table_to_config(rt) for rt in self.spec.route_tables],
            "tags": {**self.spec.tags, **self.metadata.to_tags()},
        }

        # Provider-specific mappings
        if hasattr(self._provider, 'config') and hasattr(self._provider.config, 'type'):
            provider_type_str = self._provider.config.type.value.lower()
        else:
            provider_type_str = str(self._provider).lower()

        if provider_type_str == "aws":
            config.update(self._to_aws_config())

        # Apply provider-specific overrides
        config.update(self.spec.provider_config)

        return config
        
    def _subnet_to_config(self, subnet: SubnetConfig) -> Dict[str, Any]:
        """Convert subnet configuration"""
        return {
            "name": subnet.name,
            "availability_zone": subnet.availability_zone,
            "cidr_block": subnet.cidr_block,
            "subnet_type": subnet.subnet_type.value,
            "map_public_ip": subnet.map_public_ip,
            "tags": subnet.tags
        }
        
    def _route_table_to_config(self, rt: RouteTableConfig) -> Dict[str, Any]:
        """Convert route table configuration"""
        return {
            "name": rt.name,
            "subnets": rt.subnets,
            "routes": rt.routes
        }

    def _to_aws_config(self) -> Dict[str, Any]:
        """Convert to AWS VPC configuration"""
        return {
            "resource_type": "aws_vpc"
        }
        
    # Fluent interface methods
    
    # VPC configuration
    
    def cidr(self, cidr_block: str) -> Self:
        """Set primary CIDR block (chainable)"""
        self.spec.cidr_block = cidr_block
        return self
        
    def secondary_cidr(self, cidr_block: str) -> Self:
        """Add secondary CIDR block (chainable)"""
        if cidr_block not in self.spec.secondary_cidr_blocks:
            self.spec.secondary_cidr_blocks.append(cidr_block)
        return self
        
    def dns_hostnames(self, enabled: bool = True) -> Self:
        """Enable DNS hostnames (chainable)"""
        self.spec.enable_dns_hostnames = enabled
        return self
        
    def dns_support(self, enabled: bool = True) -> Self:
        """Enable DNS support (chainable)"""
        self.spec.enable_dns_support = enabled
        return self
        
    def dedicated_tenancy(self) -> Self:
        """Use dedicated tenancy (chainable)"""
        self.spec.instance_tenancy = Tenancy.DEDICATED
        return self
        
    def default_tenancy(self) -> Self:
        """Use default tenancy (chainable)"""
        self.spec.instance_tenancy = Tenancy.DEFAULT
        return self
        
    def internet_gateway(self, enabled: bool = True) -> Self:
        """Enable/disable Internet Gateway (chainable)"""
        self.spec.enable_internet_gateway = enabled
        return self
        
    def flow_logs(self, enabled: bool = True, destination: str = "cloud-watch-logs") -> Self:
        """Enable VPC Flow Logs (chainable)"""
        self.spec.enable_flow_logs = enabled
        self.spec.flow_logs_destination = destination
        return self
        
    # Subnet management
    
    def subnet(self, name: str, az: str, cidr: str, subnet_type: SubnetType = SubnetType.PRIVATE,
              map_public_ip: bool = None) -> Self:
        """Add subnet (chainable)"""
        # Auto-configure map_public_ip based on subnet type
        if map_public_ip is None:
            map_public_ip = (subnet_type == SubnetType.PUBLIC)
            
        subnet_config = SubnetConfig(
            name=f"{self.name}-{name}" if not name.startswith(self.name) else name,
            availability_zone=az,
            cidr_block=cidr,
            subnet_type=subnet_type,
            map_public_ip=map_public_ip
        )
        self.spec.subnets.append(subnet_config)
        return self
        
    def public_subnet(self, name: str, az: str, cidr: str) -> Self:
        """Add public subnet (chainable)"""
        return self.subnet(name, az, cidr, SubnetType.PUBLIC, True)
        
    def private_subnet(self, name: str, az: str, cidr: str) -> Self:
        """Add private subnet (chainable)"""
        return self.subnet(name, az, cidr, SubnetType.PRIVATE, False)
        
    def isolated_subnet(self, name: str, az: str, cidr: str) -> Self:
        """Add isolated subnet (no internet access) (chainable)"""
        return self.subnet(name, az, cidr, SubnetType.ISOLATED, False)
        
    # Multi-AZ patterns
    
    def us_regions(self, base_cidr: str = "10.0.0.0/8") -> Self:
        """Add subnets for US regions (chainable)"""
        base_network = ipaddress.ip_network(base_cidr, strict=False)
        subnets = list(base_network.subnets(new_prefix=16))
        
        regions = [
            ("us-east-1", ["a", "b", "c"]),
            ("us-west-2", ["a", "b", "c"]),
            ("us-west-1", ["a", "c"]),
            ("us-east-2", ["a", "b", "c"])
        ]
        
        subnet_idx = 0
        for region, azs in regions:
            if subnet_idx >= len(subnets):
                break
            for az in azs:
                if subnet_idx >= len(subnets):
                    break
                full_az = f"{region}{az}"
                self.private_subnet(f"{region}-{az}", full_az, str(subnets[subnet_idx]))
                subnet_idx += 1
                
        return self
        
    def three_tier(self, region: str, az: str, base_cidr: str = "10.0.0.0/16") -> Self:
        """Create three-tier architecture in single AZ (chainable)"""
        base_network = ipaddress.ip_network(base_cidr, strict=False)
        subnets = list(base_network.subnets(new_prefix=24))
        
        full_az = f"{region}{az}" if not az.startswith(region) else az
        
        return (self
                .public_subnet("web", full_az, str(subnets[0]))
                .private_subnet("app", full_az, str(subnets[1]))
                .isolated_subnet("db", full_az, str(subnets[2])))
                
    def three_tier_multi_az(self, region: str, azs: List[str], base_cidr: str = "10.0.0.0/16") -> Self:
        """Create three-tier architecture across multiple AZs (chainable)"""
        base_network = ipaddress.ip_network(base_cidr, strict=False)
        subnets = list(base_network.subnets(new_prefix=24))
        
        subnet_idx = 0
        for i, az in enumerate(azs):
            full_az = f"{region}{az}" if not az.startswith(region) else az
            
            # Web tier (public)
            if subnet_idx < len(subnets):
                self.public_subnet(f"web-{az}", full_az, str(subnets[subnet_idx]))
                subnet_idx += 1
                
            # App tier (private)
            if subnet_idx < len(subnets):
                self.private_subnet(f"app-{az}", full_az, str(subnets[subnet_idx]))
                subnet_idx += 1
                
            # DB tier (isolated)
            if subnet_idx < len(subnets):
                self.isolated_subnet(f"db-{az}", full_az, str(subnets[subnet_idx]))
                subnet_idx += 1
                
        return self
        
    # Route table management
    
    def route_table(self, name: str, subnets: List[str]) -> Self:
        """Create custom route table (chainable)"""
        rt_config = RouteTableConfig(
            name=f"{self.name}-{name}" if not name.startswith(self.name) else name,
            subnets=subnets
        )
        self.spec.route_tables.append(rt_config)
        return self
        
    def custom_route_table(self, name: str, subnets: List[str], routes: List[Dict[str, Any]]) -> Self:
        """Create route table with custom routes (chainable)"""
        rt_config = RouteTableConfig(
            name=f"{self.name}-{name}" if not name.startswith(self.name) else name,
            subnets=subnets,
            routes=routes
        )
        self.spec.route_tables.append(rt_config)
        return self
        
    def add_route(self, route_table_name: str, destination: str, target: str, target_type: str = "gateway") -> Self:
        """Add route to existing route table (chainable)"""
        full_rt_name = f"{self.name}-{route_table_name}" if not route_table_name.startswith(self.name) else route_table_name
        
        route = {
            "destination": destination,
            target_type: target
        }
        
        for rt in self.spec.route_tables:
            if rt.name == full_rt_name:
                rt.routes.append(route)
                return self
                
        raise ValueError(f"Route table '{full_rt_name}' not found")
        
    # Tags
    
    def tag(self, key: str, value: str) -> Self:
        """Add a tag (chainable)"""
        self.spec.tags[key] = value
        return self
        
    def tags(self, tags_dict: Dict[str, str] = None, **tags) -> Self:
        """Set multiple tags (chainable)"""
        if tags_dict:
            self.spec.tags.update(tags_dict)
        if tags:
            self.spec.tags.update(tags)
        return self
        
    def subnet_tag(self, subnet_name: str, key: str, value: str) -> Self:
        """Add tag to specific subnet (chainable)"""
        full_subnet_name = f"{self.name}-{subnet_name}" if not subnet_name.startswith(self.name) else subnet_name
        
        for subnet in self.spec.subnets:
            if subnet.name == full_subnet_name:
                subnet.tags[key] = value
                return self
                
        raise ValueError(f"Subnet '{full_subnet_name}' not found")
        
    # Environment-based conveniences
    
    def production(self) -> Self:
        """Configure for production environment (chainable)"""
        return (self
                .dns_hostnames()
                .dns_support()
                .flow_logs()
                .tag("Environment", "production")
                .tag("Backup", "required")
                .tag("Monitoring", "enabled"))
                
    def staging(self) -> Self:
        """Configure for staging environment (chainable)"""
        return (self
                .dns_hostnames()
                .dns_support()
                .tag("Environment", "staging")
                .tag("Backup", "optional"))
                
    def development(self) -> Self:
        """Configure for development environment (chainable)"""
        return (self
                .dns_hostnames()
                .tag("Environment", "development")
                .tag("Backup", "none"))
                
    # Common AWS patterns
    
    def web_application_vpc(self, region: str, azs: List[str]) -> Self:
        """Configure VPC for web applications (chainable)"""
        return (self
                .cidr("10.0.0.0/16")
                .three_tier_multi_az(region, azs)
                .internet_gateway()
                .production())
                
    def microservices_vpc(self, region: str, azs: List[str]) -> Self:
        """Configure VPC for microservices (chainable)"""
        base_network = ipaddress.ip_network("10.0.0.0/16", strict=False)
        subnets = list(base_network.subnets(new_prefix=20))  # Larger subnets for more IPs
        
        subnet_idx = 0
        for az in azs:
            full_az = f"{region}{az}" if not az.startswith(region) else az
            
            # Public ALB subnet
            if subnet_idx < len(subnets):
                self.public_subnet(f"alb-{az}", full_az, str(subnets[subnet_idx]))
                subnet_idx += 1
                
            # Private app subnet (larger for many services)
            if subnet_idx < len(subnets):
                self.private_subnet(f"app-{az}", full_az, str(subnets[subnet_idx]))
                subnet_idx += 1
                
            # Database subnet
            if subnet_idx < len(subnets):
                self.isolated_subnet(f"db-{az}", full_az, str(subnets[subnet_idx]))
                subnet_idx += 1
                
        return (self
                .internet_gateway()
                .production())
                
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
        return subnet.cidr_block if subnet else None
        
    def list_subnets(self) -> List[str]:
        """List all subnet names"""
        return [subnet.name for subnet in self.spec.subnets]
        
    def get_public_subnets(self) -> List[SubnetConfig]:
        """Get all public subnets"""
        return [s for s in self.spec.subnets if s.subnet_type == SubnetType.PUBLIC]
        
    def get_private_subnets(self) -> List[SubnetConfig]:
        """Get all private subnets"""
        return [s for s in self.spec.subnets if s.subnet_type == SubnetType.PRIVATE]
        
    def get_isolated_subnets(self) -> List[SubnetConfig]:
        """Get all isolated subnets"""
        return [s for s in self.spec.subnets if s.subnet_type == SubnetType.ISOLATED]