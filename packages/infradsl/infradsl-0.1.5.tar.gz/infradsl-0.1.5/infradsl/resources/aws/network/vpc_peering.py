from typing import Optional, Dict, Any, Self, List, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

if TYPE_CHECKING:
    from infradsl.core.interfaces.provider import ProviderInterface
    from .vpc import AWSVPC

from ....core.nexus.base_resource import BaseResource, ResourceSpec


class PeeringStatus(Enum):
    """VPC peering connection status"""
    INITIATING_REQUEST = "initiating-request"
    PENDING_ACCEPTANCE = "pending-acceptance"
    ACTIVE = "active"
    DELETED = "deleted"
    REJECTED = "rejected"
    FAILED = "failed"
    EXPIRED = "expired"
    PROVISIONING = "provisioning"
    DELETING = "deleting"


@dataclass
class AWSVPCPeeringSpec(ResourceSpec):
    """Specification for AWS VPC Peering Connection"""
    
    # Peering configuration
    vpc_id: str = ""  # Local VPC ID
    peer_vpc_id: str = ""  # Peer VPC ID
    peer_region: Optional[str] = None  # For cross-region peering
    peer_owner_id: Optional[str] = None  # For cross-account peering
    
    # DNS resolution options
    allow_dns_resolution_from_remote_vpc: bool = False
    allow_remote_vpc_dns_resolution: bool = False
    
    # Route table updates
    route_tables: List[str] = field(default_factory=list)
    peer_route_tables: List[str] = field(default_factory=list)
    
    # Auto accept (for same account peering)
    auto_accept: bool = True
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class AWSVPCPeering(BaseResource):
    """
    AWS VPC Peering Connection for connecting VPCs with Rails-like conventions.
    
    Examples:
        # Simple same-account VPC peering
        peering = (AWSVPCPeering("prod-to-staging")
                   .local_vpc("vpc-12345678")
                   .peer_vpc("vpc-87654321")
                   .dns_resolution()
                   .auto_accept()
                   .production())
        
        # Cross-region VPC peering
        cross_region = (AWSVPCPeering("east-to-west")
                       .local_vpc("vpc-east")
                       .peer_vpc("vpc-west", region="us-west-2")
                       .dns_resolution()
                       .route_tables(["rt-local1", "rt-local2"])
                       .peer_route_tables(["rt-peer1", "rt-peer2"])
                       .production())
        
        # Cross-account VPC peering
        cross_account = (AWSVPCPeering("org-to-partner")
                        .local_vpc("vpc-12345678")
                        .peer_vpc("vpc-87654321", account_id="123456789012")
                        .dns_resolution(local=True, remote=False)  # One-way DNS
                        .manual_accept()  # Requires manual acceptance
                        .production())
                        
        # Hub and spoke architecture
        hub_peering = (AWSVPCPeering("spoke1-to-hub")
                      .local_vpc("vpc-spoke1")
                      .peer_vpc("vpc-hub")
                      .dns_resolution()
                      .route_tables(["rt-spoke1"])
                      .peer_route_tables(["rt-hub"])
                      .production())
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.spec: AWSVPCPeeringSpec = self._create_spec()
        self.metadata.annotations["resource_type"] = "AWSVPCPeering"
        
    def _create_spec(self) -> AWSVPCPeeringSpec:
        return AWSVPCPeeringSpec()
        
    def _validate_spec(self) -> None:
        """Validate AWS VPC Peering specification"""
        if not self.spec.vpc_id:
            raise ValueError("Local VPC ID is required")
            
        if not self.spec.peer_vpc_id:
            raise ValueError("Peer VPC ID is required")
            
        if self.spec.vpc_id == self.spec.peer_vpc_id and not self.spec.peer_region and not self.spec.peer_owner_id:
            raise ValueError("Cannot peer VPC with itself in same region and account")
            
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        config = {
            "name": self.metadata.name,
            "vpc_id": self.spec.vpc_id,
            "peer_vpc_id": self.spec.peer_vpc_id,
            "allow_dns_resolution_from_remote_vpc": self.spec.allow_dns_resolution_from_remote_vpc,
            "allow_remote_vpc_dns_resolution": self.spec.allow_remote_vpc_dns_resolution,
            "auto_accept": self.spec.auto_accept,
            "route_tables": self.spec.route_tables,
            "peer_route_tables": self.spec.peer_route_tables,
            "tags": {**self.spec.tags, **self.metadata.to_tags()},
        }
        
        if self.spec.peer_region:
            config["peer_region"] = self.spec.peer_region
            
        if self.spec.peer_owner_id:
            config["peer_owner_id"] = self.spec.peer_owner_id

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
        """Convert to AWS VPC Peering configuration"""
        return {
            "resource_type": "aws_vpc_peering_connection"
        }
        
    # Fluent interface methods
    
    def local_vpc(self, vpc_id: str) -> Self:
        """Set local VPC ID (chainable)"""
        self.spec.vpc_id = vpc_id
        return self
        
    def peer_vpc(self, vpc_id: str, region: str = None, account_id: str = None) -> Self:
        """Set peer VPC ID with optional cross-region/cross-account (chainable)"""
        self.spec.peer_vpc_id = vpc_id
        self.spec.peer_region = region
        self.spec.peer_owner_id = account_id
        return self
        
    def cross_region(self, region: str) -> Self:
        """Enable cross-region peering (chainable)"""
        self.spec.peer_region = region
        return self
        
    def cross_account(self, account_id: str) -> Self:
        """Enable cross-account peering (chainable)"""
        self.spec.peer_owner_id = account_id
        return self
        
    # DNS resolution
    
    def dns_resolution(self, local: bool = True, remote: bool = True) -> Self:
        """Enable DNS resolution (chainable)"""
        self.spec.allow_dns_resolution_from_remote_vpc = local
        self.spec.allow_remote_vpc_dns_resolution = remote
        return self
        
    def local_dns_resolution(self, enabled: bool = True) -> Self:
        """Enable DNS resolution from remote VPC (chainable)"""
        self.spec.allow_dns_resolution_from_remote_vpc = enabled
        return self
        
    def remote_dns_resolution(self, enabled: bool = True) -> Self:
        """Enable remote VPC DNS resolution (chainable)"""
        self.spec.allow_remote_vpc_dns_resolution = enabled
        return self
        
    def bidirectional_dns(self) -> Self:
        """Enable bidirectional DNS resolution (chainable)"""
        return self.dns_resolution(local=True, remote=True)
        
    # Acceptance
    
    def auto_accept(self, enabled: bool = True) -> Self:
        """Enable/disable auto-acceptance (chainable)"""
        self.spec.auto_accept = enabled
        return self
        
    def manual_accept(self) -> Self:
        """Require manual acceptance (chainable)"""
        self.spec.auto_accept = False
        return self
        
    # Route table management
    
    def route_tables(self, route_table_ids: List[str]) -> Self:
        """Set local route tables to update (chainable)"""
        self.spec.route_tables = route_table_ids.copy()
        return self
        
    def peer_route_tables(self, route_table_ids: List[str]) -> Self:
        """Set peer route tables to update (chainable)"""
        self.spec.peer_route_tables = route_table_ids.copy()
        return self
        
    def add_route_table(self, route_table_id: str) -> Self:
        """Add local route table (chainable)"""
        if route_table_id not in self.spec.route_tables:
            self.spec.route_tables.append(route_table_id)
        return self
        
    def add_peer_route_table(self, route_table_id: str) -> Self:
        """Add peer route table (chainable)"""
        if route_table_id not in self.spec.peer_route_tables:
            self.spec.peer_route_tables.append(route_table_id)
        return self
        
    # LEGO principle - integration with VPC resources
    
    def connect_vpcs(self, vpc1: "AWSVPC", vpc2: "AWSVPC", 
                    vpc2_region: str = None, vpc2_account: str = None) -> Self:
        """Connect two VPC resources (chainable)"""
        return (self
                .local_vpc(vpc1.name)
                .peer_vpc(vpc2.name, vpc2_region, vpc2_account))
                
    # Common patterns
    
    def hub_and_spoke(self, spoke_vpc_id: str, hub_vpc_id: str, 
                     hub_region: str = None) -> Self:
        """Configure hub-and-spoke peering (chainable)"""
        return (self
                .local_vpc(spoke_vpc_id)
                .peer_vpc(hub_vpc_id, hub_region)
                .dns_resolution(local=True, remote=False)  # Spoke can resolve hub, not vice versa
                .auto_accept())
                
    def mesh_peering(self, vpc1_id: str, vpc2_id: str) -> Self:
        """Configure mesh peering (full connectivity) (chainable)"""
        return (self
                .local_vpc(vpc1_id)
                .peer_vpc(vpc2_id)
                .bidirectional_dns()
                .auto_accept())
                
    def transit_peering(self, transit_vpc_id: str, workload_vpc_id: str) -> Self:
        """Configure transit gateway-style peering (chainable)"""
        return (self
                .local_vpc(workload_vpc_id)
                .peer_vpc(transit_vpc_id)
                .dns_resolution(local=False, remote=True)  # Only transit can resolve workloads
                .auto_accept())
                
    # Multi-environment patterns
    
    def production_to_shared(self, prod_vpc_id: str, shared_vpc_id: str, shared_account: str = None) -> Self:
        """Production to shared services peering (chainable)"""
        config = (self
                 .local_vpc(prod_vpc_id)
                 .peer_vpc(shared_vpc_id, account_id=shared_account)
                 .dns_resolution(local=True, remote=False))  # Prod can use shared, not vice versa
                 
        if shared_account:
            config = config.manual_accept()  # Cross-account requires manual acceptance
        else:
            config = config.auto_accept()
            
        return config
        
    def staging_to_shared(self, staging_vpc_id: str, shared_vpc_id: str) -> Self:
        """Staging to shared services peering (chainable)"""
        return (self
                .local_vpc(staging_vpc_id)
                .peer_vpc(shared_vpc_id)
                .bidirectional_dns()
                .auto_accept())
                
    def disaster_recovery_peering(self, primary_vpc_id: str, dr_vpc_id: str, dr_region: str) -> Self:
        """Disaster recovery cross-region peering (chainable)"""
        return (self
                .local_vpc(primary_vpc_id)
                .peer_vpc(dr_vpc_id, dr_region)
                .bidirectional_dns()
                .auto_accept()
                .tag("Purpose", "DisasterRecovery")
                .tag("PrimaryRegion", "current")
                .tag("DRRegion", dr_region))
                
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
                .auto_accept()
                .tag("Environment", "production")
                .tag("Criticality", "high")
                .tag("Monitoring", "enabled"))
                
    def staging(self) -> Self:
        """Configure for staging environment (chainable)"""
        return (self
                .auto_accept()
                .bidirectional_dns()
                .tag("Environment", "staging")
                .tag("Criticality", "medium"))
                
    def development(self) -> Self:
        """Configure for development environment (chainable)"""
        return (self
                .auto_accept()
                .bidirectional_dns()
                .tag("Environment", "development")
                .tag("Criticality", "low"))
                
    # Provider implementation methods
    
    def _provider_create(self) -> Dict[str, Any]:
        """Create the VPC Peering Connection via provider"""
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
        """Update the VPC Peering Connection via provider"""
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
        """Destroy the VPC Peering Connection via provider"""
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
    
    def get_local_vpc(self) -> str:
        """Get local VPC ID"""
        return self.spec.vpc_id
        
    def get_peer_vpc(self) -> str:
        """Get peer VPC ID"""
        return self.spec.peer_vpc_id
        
    def is_cross_region(self) -> bool:
        """Check if this is cross-region peering"""
        return self.spec.peer_region is not None
        
    def is_cross_account(self) -> bool:
        """Check if this is cross-account peering"""
        return self.spec.peer_owner_id is not None
        
    def has_dns_resolution(self) -> bool:
        """Check if DNS resolution is enabled"""
        return (self.spec.allow_dns_resolution_from_remote_vpc or 
                self.spec.allow_remote_vpc_dns_resolution)
                
    def get_route_tables(self) -> Dict[str, List[str]]:
        """Get all route table configurations"""
        return {
            "local": self.spec.route_tables.copy(),
            "peer": self.spec.peer_route_tables.copy()
        }