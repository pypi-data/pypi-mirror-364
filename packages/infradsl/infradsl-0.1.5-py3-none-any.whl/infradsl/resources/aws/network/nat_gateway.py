from typing import Optional, Dict, Any, Self, List, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

if TYPE_CHECKING:
    from infradsl.core.interfaces.provider import ProviderInterface
    from .vpc import AWSVPC

from ....core.nexus.base_resource import BaseResource, ResourceSpec


class ConnectivityType(Enum):
    """NAT Gateway connectivity type"""
    PUBLIC = "public"
    PRIVATE = "private"


@dataclass
class AWSNATGatewaySpec(ResourceSpec):
    """Specification for AWS NAT Gateway"""
    
    # Basic configuration
    subnet_id: str = ""
    connectivity_type: ConnectivityType = ConnectivityType.PUBLIC
    
    # Elastic IP (for public NAT gateways)
    allocation_id: str = ""  # EIP allocation ID
    auto_allocate_eip: bool = True
    
    # Private NAT Gateway configuration
    private_ip_address: str = ""
    secondary_allocation_ids: List[str] = field(default_factory=list)
    
    # Route table associations
    route_tables: List[str] = field(default_factory=list)
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class AWSNATGateway(BaseResource):
    """
    AWS NAT Gateway for outbound internet connectivity from private subnets with Rails-like conventions.
    
    Examples:
        # Simple public NAT Gateway
        nat = (AWSNATGateway("main-nat")
               .public_subnet("public-subnet-id")
               .auto_eip()
               .route_to(["private-route-table-id"])
               .production())
        
        # Multi-AZ NAT Gateways for high availability
        nat_1a = (AWSNATGateway("nat-1a")
                  .public_subnet("public-subnet-1a")
                  .auto_eip()
                  .route_to(["private-rt-1a"])
                  .tag("AZ", "us-east-1a")
                  .production())
                  
        nat_1b = (AWSNATGateway("nat-1b")
                  .public_subnet("public-subnet-1b")
                  .auto_eip()
                  .route_to(["private-rt-1b"])
                  .tag("AZ", "us-east-1b")
                  .production())
        
        # Private NAT Gateway (for VPC-to-VPC communication)
        private_nat = (AWSNATGateway("private-nat")
                      .private_subnet("private-subnet-id")
                      .private_connectivity()
                      .private_ip("10.0.1.100")
                      .route_to(["internal-rt"])
                      .staging())
                      
        # Cost-optimized single NAT for development
        dev_nat = (AWSNATGateway("dev-nat")
                   .public_subnet("dev-public-subnet")
                   .auto_eip()
                   .route_to(["dev-private-rt"])
                   .development())
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.spec: AWSNATGatewaySpec = self._create_spec()
        self.metadata.annotations["resource_type"] = "AWSNATGateway"
        
    def _create_spec(self) -> AWSNATGatewaySpec:
        return AWSNATGatewaySpec()
        
    def _validate_spec(self) -> None:
        """Validate AWS NAT Gateway specification"""
        if not self.spec.subnet_id:
            raise ValueError("Subnet ID is required for NAT Gateway")
            
        if self.spec.connectivity_type == ConnectivityType.PUBLIC:
            if not self.spec.auto_allocate_eip and not self.spec.allocation_id:
                raise ValueError("Public NAT Gateway requires either auto EIP allocation or explicit allocation ID")
                
        if self.spec.connectivity_type == ConnectivityType.PRIVATE:
            if self.spec.allocation_id or self.spec.auto_allocate_eip:
                raise ValueError("Private NAT Gateway cannot have Elastic IP")
                
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        config = {
            "name": self.metadata.name,
            "subnet_id": self.spec.subnet_id,
            "connectivity_type": self.spec.connectivity_type.value,
            "route_tables": self.spec.route_tables,
            "tags": {**self.spec.tags, **self.metadata.to_tags()},
        }
        
        # Public NAT Gateway configuration
        if self.spec.connectivity_type == ConnectivityType.PUBLIC:
            if self.spec.auto_allocate_eip:
                config["auto_allocate_eip"] = True
            elif self.spec.allocation_id:
                config["allocation_id"] = self.spec.allocation_id
                
        # Private NAT Gateway configuration
        if self.spec.connectivity_type == ConnectivityType.PRIVATE:
            if self.spec.private_ip_address:
                config["private_ip_address"] = self.spec.private_ip_address
            if self.spec.secondary_allocation_ids:
                config["secondary_allocation_ids"] = self.spec.secondary_allocation_ids

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

    def _to_aws_config(self) -> Dict[str, Any]:
        """Convert to AWS NAT Gateway configuration"""
        return {
            "resource_type": "aws_nat_gateway"
        }
        
    # Fluent interface methods
    
    # Basic configuration
    
    def subnet(self, subnet_id: str) -> Self:
        """Set subnet for NAT Gateway (chainable)"""
        self.spec.subnet_id = subnet_id
        return self
        
    def public_subnet(self, subnet_id: str) -> Self:
        """Set public subnet and enable public connectivity (chainable)"""
        self.spec.subnet_id = subnet_id
        self.spec.connectivity_type = ConnectivityType.PUBLIC
        return self
        
    def private_subnet(self, subnet_id: str) -> Self:
        """Set private subnet and enable private connectivity (chainable)"""
        self.spec.subnet_id = subnet_id
        self.spec.connectivity_type = ConnectivityType.PRIVATE
        return self
        
    # Connectivity type
    
    def public_connectivity(self) -> Self:
        """Enable public connectivity (chainable)"""
        self.spec.connectivity_type = ConnectivityType.PUBLIC
        return self
        
    def private_connectivity(self) -> Self:
        """Enable private connectivity (chainable)"""
        self.spec.connectivity_type = ConnectivityType.PRIVATE
        return self
        
    # Elastic IP configuration
    
    def auto_eip(self) -> Self:
        """Auto-allocate Elastic IP for public NAT Gateway (chainable)"""
        self.spec.auto_allocate_eip = True
        self.spec.allocation_id = ""
        return self
        
    def eip(self, allocation_id: str) -> Self:
        """Use existing Elastic IP allocation (chainable)"""
        self.spec.allocation_id = allocation_id
        self.spec.auto_allocate_eip = False
        return self
        
    def private_ip(self, ip_address: str) -> Self:
        """Set private IP address for private NAT Gateway (chainable)"""
        self.spec.private_ip_address = ip_address
        return self
        
    def secondary_eip(self, allocation_id: str) -> Self:
        """Add secondary EIP allocation for private NAT Gateway (chainable)"""
        if allocation_id not in self.spec.secondary_allocation_ids:
            self.spec.secondary_allocation_ids.append(allocation_id)
        return self
        
    # Route table associations
    
    def route_to(self, route_table_ids: List[str]) -> Self:
        """Associate with route tables (chainable)"""
        self.spec.route_tables = route_table_ids.copy()
        return self
        
    def add_route_table(self, route_table_id: str) -> Self:
        """Add route table association (chainable)"""
        if route_table_id not in self.spec.route_tables:
            self.spec.route_tables.append(route_table_id)
        return self
        
    # LEGO principle - integration with VPC
    
    def for_vpc_private_subnets(self, vpc: "AWSVPC", public_subnet_name: str = None) -> Self:
        """Configure NAT for VPC private subnets (chainable)"""
        if public_subnet_name:
            public_subnet = vpc.get_subnet(public_subnet_name)
            if not public_subnet:
                raise ValueError(f"Public subnet '{public_subnet_name}' not found in VPC")
        else:
            # Use first public subnet
            public_subnets = vpc.get_public_subnets()
            if not public_subnets:
                raise ValueError("No public subnets found in VPC")
            public_subnet = public_subnets[0]
            
        return self.public_subnet(public_subnet.name)
        
    # Common patterns
    
    def high_availability_pair(self, vpc: "AWSVPC", az_suffix: str) -> Self:
        """Configure as part of HA NAT Gateway pair (chainable)"""
        # Find public subnet for this AZ
        public_subnets = [s for s in vpc.get_public_subnets() 
                         if s.availability_zone.endswith(az_suffix)]
        
        if not public_subnets:
            raise ValueError(f"No public subnet found for AZ ending with '{az_suffix}'")
            
        return (self
                .public_subnet(public_subnets[0].name)
                .auto_eip()
                .tag("HighAvailability", "true")
                .tag("AZ", public_subnets[0].availability_zone))
                
    def cost_optimized(self) -> Self:
        """Configure for cost optimization (chainable)"""
        return (self
                .auto_eip()
                .tag("CostOptimization", "single-nat"))
                
    def high_availability(self, allocation_ids: List[str] = None) -> Self:
        """Configure for high availability (chainable)"""
        if allocation_ids:
            # Use pre-allocated EIPs for predictable IP addresses
            if len(allocation_ids) > 1:
                self.eip(allocation_ids[0])
                for alloc_id in allocation_ids[1:]:
                    self.secondary_eip(alloc_id)
            else:
                self.eip(allocation_ids[0])
        else:
            self.auto_eip()
            
        return (self
                .tag("HighAvailability", "true")
                .tag("SLA", "99.9"))
                
    def enterprise_grade(self, allocation_ids: List[str] = None) -> Self:
        """Configure for enterprise requirements (chainable)"""
        if allocation_ids:
            # Use pre-allocated EIPs for predictable IP addresses
            if len(allocation_ids) > 1:
                self.eip(allocation_ids[0])
                for alloc_id in allocation_ids[1:]:
                    self.secondary_eip(alloc_id)
            else:
                self.eip(allocation_ids[0])
        else:
            self.auto_eip()
            
        return (self
                .tag("Tier", "enterprise")
                .tag("SLA", "99.95"))
                
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
        
    # Environment-based conveniences
    
    def production(self) -> Self:
        """Configure for production environment (chainable)"""
        return (self
                .auto_eip()
                .tag("Environment", "production")
                .tag("Backup", "required")
                .tag("Monitoring", "enabled"))
                
    def staging(self) -> Self:
        """Configure for staging environment (chainable)"""
        return (self
                .auto_eip()
                .tag("Environment", "staging")
                .tag("Monitoring", "basic"))
                
    def development(self) -> Self:
        """Configure for development environment (chainable)"""
        return (self
                .auto_eip()
                .tag("Environment", "development")
                .tag("CostOptimization", "enabled"))
                
    # Provider implementation methods
    
    def _provider_create(self) -> Dict[str, Any]:
        """Create the NAT Gateway via provider"""
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
        """Update the NAT Gateway via provider"""
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
        """Destroy the NAT Gateway via provider"""
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
    
    def get_subnet_id(self) -> str:
        """Get subnet ID"""
        return self.spec.subnet_id
        
    def get_connectivity_type(self) -> str:
        """Get connectivity type"""
        return self.spec.connectivity_type.value
        
    def is_public(self) -> bool:
        """Check if NAT Gateway is public"""
        return self.spec.connectivity_type == ConnectivityType.PUBLIC
        
    def is_private(self) -> bool:
        """Check if NAT Gateway is private"""
        return self.spec.connectivity_type == ConnectivityType.PRIVATE
        
    def get_route_tables(self) -> List[str]:
        """Get associated route table IDs"""
        return self.spec.route_tables.copy()