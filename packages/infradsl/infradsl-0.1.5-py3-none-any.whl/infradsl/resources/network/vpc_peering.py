from typing import Optional, Dict, Any, Self, List, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

if TYPE_CHECKING:
    from infradsl.core.interfaces.provider import ProviderInterface
    from .vpc import VPCNetwork

from ...core.nexus.base_resource import BaseResource, ResourceSpec


class PeeringState(Enum):
    """VPC peering connection state"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


@dataclass
class VPCPeeringSpec(ResourceSpec):
    """Specification for VPC Network Peering"""
    
    # Peering configuration
    network: str = ""  # Local network name
    peer_network: str = ""  # Peer network name/URL
    peer_project: Optional[str] = None  # For cross-project peering
    
    # Auto-create reverse peering
    auto_create_routes: bool = True
    
    # Import/export custom routes
    import_custom_routes: bool = False
    export_custom_routes: bool = False
    
    # Import/export subnet routes with public IP
    import_subnet_routes_with_public_ip: bool = True
    export_subnet_routes_with_public_ip: bool = True
    
    # Stack type
    stack_type: str = "IPV4_ONLY"  # IPV4_ONLY, IPV4_IPV6
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SharedVPCSpec(ResourceSpec):
    """Specification for Shared VPC"""
    
    # Host project configuration
    host_project: str = ""
    
    # Service projects
    service_projects: List[str] = field(default_factory=list)
    
    # Subnet sharing configuration
    shared_subnets: Dict[str, List[str]] = field(default_factory=dict)  # subnet -> service_projects
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class VPCPeering(BaseResource):
    """
    GCP VPC Network Peering for connecting VPC networks with Rails-like conventions.
    
    Examples:
        # Simple VPC peering within same project
        peering = (VPCPeering("prod-to-staging")
                   .local_network("production-vpc")
                   .peer_network("staging-vpc")
                   .bidirectional()
                   .custom_routes())
        
        # Cross-project VPC peering
        cross_project = (VPCPeering("prod-to-shared")
                        .local_network("production-vpc")
                        .peer_network("shared-services-vpc", "shared-services-project")
                        .bidirectional()
                        .import_routes()
                        .export_routes())
                        
        # Hub and spoke architecture
        hub_peering = (VPCPeering("spoke1-to-hub")
                      .local_network("spoke1-vpc")
                      .peer_network("hub-vpc", "hub-project")
                      .import_routes()
                      .production())
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.spec: VPCPeeringSpec = self._create_spec()
        self.metadata.annotations["resource_type"] = "VPCPeering"
        
    def _create_spec(self) -> VPCPeeringSpec:
        return VPCPeeringSpec()
        
    def _validate_spec(self) -> None:
        """Validate VPC peering specification"""
        if not self.spec.network:
            raise ValueError("Local network name is required")
            
        if not self.spec.peer_network:
            raise ValueError("Peer network name is required")
            
        if self.spec.network == self.spec.peer_network and not self.spec.peer_project:
            raise ValueError("Cannot peer network with itself in same project")
            
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        config = {
            "name": self.metadata.name,
            "network": self.spec.network,
            "peer_network": self.spec.peer_network,
            "auto_create_routes": self.spec.auto_create_routes,
            "import_custom_routes": self.spec.import_custom_routes,
            "export_custom_routes": self.spec.export_custom_routes,
            "import_subnet_routes_with_public_ip": self.spec.import_subnet_routes_with_public_ip,
            "export_subnet_routes_with_public_ip": self.spec.export_subnet_routes_with_public_ip,
            "stack_type": self.spec.stack_type,
            "labels": {**self.spec.labels, **self.metadata.to_tags()},
        }
        
        if self.spec.peer_project:
            config["peer_project"] = self.spec.peer_project

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
        """Convert to GCP VPC Peering configuration"""
        config = {
            "resource_type": "vpc_peering"
        }
        return config
        
    # Fluent interface methods
    
    def local_network(self, network_name: str) -> Self:
        """Set local network (chainable)"""
        self.spec.network = network_name
        return self
        
    def peer_network(self, network_name: str, project: str = None) -> Self:
        """Set peer network (chainable)"""
        self.spec.peer_network = network_name
        self.spec.peer_project = project
        return self
        
    def cross_project(self, peer_project: str) -> Self:
        """Set peer project for cross-project peering (chainable)"""
        self.spec.peer_project = peer_project
        return self
        
    # Route configuration
    
    def auto_routes(self, enabled: bool = True) -> Self:
        """Enable/disable automatic route creation (chainable)"""
        self.spec.auto_create_routes = enabled
        return self
        
    def custom_routes(self, import_routes: bool = True, export_routes: bool = True) -> Self:
        """Enable custom route import/export (chainable)"""
        self.spec.import_custom_routes = import_routes
        self.spec.export_custom_routes = export_routes
        return self
        
    def import_routes(self, custom: bool = True, public_ip: bool = True) -> Self:
        """Enable route import (chainable)"""
        self.spec.import_custom_routes = custom
        self.spec.import_subnet_routes_with_public_ip = public_ip
        return self
        
    def export_routes(self, custom: bool = True, public_ip: bool = True) -> Self:
        """Enable route export (chainable)"""
        self.spec.export_custom_routes = custom
        self.spec.export_subnet_routes_with_public_ip = public_ip
        return self
        
    def bidirectional(self, custom_routes: bool = False) -> Self:
        """Enable bidirectional peering (chainable)"""
        self.spec.import_custom_routes = custom_routes
        self.spec.export_custom_routes = custom_routes
        self.spec.import_subnet_routes_with_public_ip = True
        self.spec.export_subnet_routes_with_public_ip = True
        return self
        
    # Stack type
    
    def ipv4_only(self) -> Self:
        """Use IPv4 only (chainable)"""
        self.spec.stack_type = "IPV4_ONLY"
        return self
        
    def ipv4_ipv6(self) -> Self:
        """Use IPv4 and IPv6 (chainable)"""
        self.spec.stack_type = "IPV4_IPV6"
        return self
        
    # LEGO principle - integration with VPC resources
    
    def connect_vpcs(self, vpc1: "VPCNetwork", vpc2: "VPCNetwork", 
                    project2: str = None) -> Self:
        """Connect two VPC networks (chainable)"""
        return (self
                .local_network(vpc1.name)
                .peer_network(vpc2.name, project2))
                
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
                .auto_routes()
                .import_routes(custom=True)
                .export_routes(custom=False)  # More restrictive export
                .label("environment", "production"))
                
    def staging(self) -> Self:
        """Configure for staging environment (chainable)"""
        return (self
                .bidirectional(custom_routes=True)
                .label("environment", "staging"))
                
    def development(self) -> Self:
        """Configure for development environment (chainable)"""
        return (self
                .bidirectional(custom_routes=True)
                .label("environment", "development"))
                
    # Provider implementation methods (similar pattern to other resources)
    def _provider_create(self) -> Dict[str, Any]:
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


class SharedVPC(BaseResource):
    """
    GCP Shared VPC for centralized network management with Rails-like conventions.
    
    Examples:
        # Basic shared VPC
        shared = (SharedVPC("organization-shared")
                  .host_project("networking-project")
                  .service_project("web-app-project")
                  .service_project("api-project")
                  .share_subnet("frontend-subnet", ["web-app-project"])
                  .share_subnet("backend-subnet", ["web-app-project", "api-project"]))
        
        # Multi-tier shared VPC
        multi_tier = (SharedVPC("enterprise-shared")
                     .host_project("network-hub")
                     .service_projects([
                         "prod-web", "prod-api", "prod-db",
                         "staging-web", "staging-api"
                     ])
                     .share_all_subnets(["prod-web", "prod-api"])
                     .production())
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.spec: SharedVPCSpec = self._create_spec()
        self.metadata.annotations["resource_type"] = "SharedVPC"
        
    def _create_spec(self) -> SharedVPCSpec:
        return SharedVPCSpec()
        
    def _validate_spec(self) -> None:
        """Validate Shared VPC specification"""
        if not self.spec.host_project:
            raise ValueError("Host project is required for Shared VPC")
            
        if not self.spec.service_projects:
            raise ValueError("At least one service project is required")
            
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        config = {
            "name": self.metadata.name,
            "host_project": self.spec.host_project,
            "service_projects": self.spec.service_projects,
            "shared_subnets": self.spec.shared_subnets,
            "labels": {**self.spec.labels, **self.metadata.to_tags()},
        }

        # Provider-specific mappings
        if hasattr(self._provider, 'config') and hasattr(self._provider.config, 'type'):
            provider_type_str = self._provider.config.type.value.lower()
        else:
            provider_type_str = str(self._provider).lower()

        if provider_type_str == "gcp":
            config.update(self._to_gcp_config())

        config.update(self.spec.provider_config)
        return config

    def _to_gcp_config(self) -> Dict[str, Any]:
        """Convert to GCP Shared VPC configuration"""
        return {"resource_type": "shared_vpc"}
        
    # Fluent interface methods
    
    def host_project(self, project_id: str) -> Self:
        """Set host project (chainable)"""
        self.spec.host_project = project_id
        return self
        
    def service_project(self, project_id: str) -> Self:
        """Add service project (chainable)"""
        if project_id not in self.spec.service_projects:
            self.spec.service_projects.append(project_id)
        return self
        
    def service_projects(self, project_ids: List[str]) -> Self:
        """Set multiple service projects (chainable)"""
        self.spec.service_projects = project_ids.copy()
        return self
        
    def share_subnet(self, subnet_name: str, service_projects: List[str]) -> Self:
        """Share subnet with specific projects (chainable)"""
        self.spec.shared_subnets[subnet_name] = service_projects.copy()
        return self
        
    def share_all_subnets(self, service_projects: List[str]) -> Self:
        """Share all subnets with projects (chainable)"""
        # This would be implemented by the provider to share all existing subnets
        for project in service_projects:
            if project not in self.spec.service_projects:
                self.spec.service_projects.append(project)
        return self
        
    def production(self) -> Self:
        """Configure for production environment (chainable)"""
        return self.label("environment", "production")
        
    def staging(self) -> Self:
        """Configure for staging environment (chainable)"""
        return self.label("environment", "staging")
        
    def development(self) -> Self:
        """Configure for development environment (chainable)"""
        return self.label("environment", "development")
        
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
        
    # Provider implementation methods
    def _provider_create(self) -> Dict[str, Any]:
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