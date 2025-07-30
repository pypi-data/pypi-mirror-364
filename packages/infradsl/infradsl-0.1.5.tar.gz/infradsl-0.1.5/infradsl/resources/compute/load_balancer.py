from typing import Optional, Dict, Any, Self, List, TYPE_CHECKING

if TYPE_CHECKING:
    from infradsl.core.interfaces.provider import ProviderInterface
    from .virtual_machine import VirtualMachine
    from .instance_group import InstanceGroup

from dataclasses import dataclass, field
from enum import Enum

from ...core.nexus.base_resource import BaseResource, ResourceSpec


class LoadBalancerType(Enum):
    """Load balancer types"""
    HTTP_HTTPS = "HTTP_HTTPS"
    TCP = "TCP"
    UDP = "UDP"
    INTERNAL = "INTERNAL"


class HealthCheckType(Enum):
    """Health check types"""
    HTTP = "HTTP"
    HTTPS = "HTTPS"
    TCP = "TCP"
    HTTP2 = "HTTP2"


@dataclass
class HealthCheckSpec(ResourceSpec):
    """Health check specification"""
    check_type: HealthCheckType = HealthCheckType.HTTP
    port: int = 80
    path: str = "/"
    interval_sec: int = 10
    timeout_sec: int = 5
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3


@dataclass
class LoadBalancerSpec(ResourceSpec):
    """Specification for a load balancer resource"""
    
    # Core configuration
    lb_type: LoadBalancerType = LoadBalancerType.HTTP_HTTPS
    global_lb: bool = True
    region: Optional[str] = None
    
    # Backend configuration
    backend_groups: List[str] = field(default_factory=list)
    backend_instances: List[str] = field(default_factory=list)
    
    # Health check
    health_check: Optional[HealthCheckSpec] = None
    
    # SSL configuration
    ssl_certificates: List[str] = field(default_factory=list)
    redirect_http_to_https: bool = True
    
    # Port configuration
    port: int = 80
    ssl_port: int = 443
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class LoadBalancer(BaseResource):
    """
    Load balancer resource for distributing traffic across instances.
    
    Examples:
        # Simple HTTP load balancer
        lb = (LoadBalancer("web-lb")
              .http()
              .add_instance_group(group)
              .health_check("/health"))
        
        # HTTPS load balancer with SSL
        lb = (LoadBalancer("secure-lb")
              .https()
              .ssl_cert("my-cert")
              .add_instance_group(group))
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.spec: LoadBalancerSpec = self._create_spec()
        # Store resource type in annotations for cache fingerprinting
        self.metadata.annotations["resource_type"] = "LoadBalancer"
        
    def _create_spec(self) -> LoadBalancerSpec:
        return LoadBalancerSpec()
        
    def _validate_spec(self) -> None:
        """Validate load balancer specification"""
        if not self.spec.backend_groups and not self.spec.backend_instances:
            raise ValueError("Load balancer requires at least one backend group or instance")
            
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        config = {
            "name": self.metadata.name,
            "lb_type": self.spec.lb_type.value,
            "global": self.spec.global_lb,
            "port": self.spec.port,
            "tags": self.metadata.to_tags(),
        }

        # Provider-specific mappings
        if hasattr(self._provider, 'config') and hasattr(self._provider.config, 'type'):
            provider_type_str = self._provider.config.type.value.lower()
        else:
            provider_type_str = str(self._provider).lower()

        if provider_type_str == "gcp":
            config.update(self._to_gcp_config())
        elif provider_type_str == "aws":
            config.update(self._to_aws_config())

        # Apply provider-specific overrides
        config.update(self.spec.provider_config)

        return config

    def _to_gcp_config(self) -> Dict[str, Any]:
        """Convert to GCP load balancer configuration"""
        config = {
            "resource_type": "global_forwarding_rule" if self.spec.global_lb else "forwarding_rule"
        }
        
        # Configure based on load balancer type
        if self.spec.lb_type == LoadBalancerType.HTTP_HTTPS:
            config.update({
                "resource_type": "global_forwarding_rule",
                "port_range": "80-80" if self.spec.port == 80 else str(self.spec.port),
                "target": f"global/targetHttpProxies/{self.name}-proxy",
                "ip_protocol": "TCP"
            })
            
            # Add URL map and backend service
            config["url_map"] = f"global/urlMaps/{self.name}-map"
            config["backend_service"] = f"global/backendServices/{self.name}-backend"
            
        elif self.spec.lb_type == LoadBalancerType.TCP:
            config.update({
                "resource_type": "global_forwarding_rule",
                "port_range": str(self.spec.port),
                "target": f"global/targetTcpProxies/{self.name}-proxy",
                "ip_protocol": "TCP"
            })
            
        # Regional vs global
        if not self.spec.global_lb and self.spec.region:
            config["region"] = self.spec.region
            # Update resource types for regional
            config["resource_type"] = "forwarding_rule"
            
        # Health check configuration
        if self.spec.health_check:
            config["health_check"] = {
                "type": self.spec.health_check.check_type.value,
                "port": self.spec.health_check.port,
                "request_path": self.spec.health_check.path,
                "check_interval_sec": self.spec.health_check.interval_sec,
                "timeout_sec": self.spec.health_check.timeout_sec,
                "healthy_threshold": self.spec.health_check.healthy_threshold,
                "unhealthy_threshold": self.spec.health_check.unhealthy_threshold
            }
            
        # Backend configuration
        if self.spec.backend_groups:
            config["backend_groups"] = self.spec.backend_groups
        if self.spec.backend_instances:
            config["backend_instances"] = self.spec.backend_instances
            
        # SSL configuration
        if self.spec.ssl_certificates:
            config["ssl_certificates"] = self.spec.ssl_certificates
            config["ssl_port"] = self.spec.ssl_port

        return config

    def _to_aws_config(self) -> Dict[str, Any]:
        """Convert to AWS load balancer configuration"""
        if self.spec.lb_type == LoadBalancerType.HTTP_HTTPS:
            resource_type = "lb"  # Application Load Balancer
            lb_type = "application"
        else:
            resource_type = "lb"  # Network Load Balancer  
            lb_type = "network"
            
        config = {
            "resource_type": resource_type,
            "load_balancer_type": lb_type,
            "port": self.spec.port,
        }
        
        # Add target group configuration
        config["target_group"] = {
            "port": self.spec.port,
            "protocol": "HTTP" if self.spec.lb_type == LoadBalancerType.HTTP_HTTPS else "TCP",
            "target_type": "instance"
        }

        return config
        
    # Fluent interface methods
    
    def http(self, port: int = 80) -> Self:
        """Configure as HTTP load balancer (chainable)"""
        self.spec.lb_type = LoadBalancerType.HTTP_HTTPS
        self.spec.port = port
        return self
        
    def https(self, port: int = 443) -> Self:
        """Configure as HTTPS load balancer (chainable)"""
        self.spec.lb_type = LoadBalancerType.HTTP_HTTPS
        self.spec.ssl_port = port
        return self
        
    def tcp(self, port: int) -> Self:
        """Configure as TCP load balancer (chainable)"""
        self.spec.lb_type = LoadBalancerType.TCP
        self.spec.port = port
        return self
        
    def internal(self) -> Self:
        """Configure as internal load balancer (chainable)"""
        self.spec.lb_type = LoadBalancerType.INTERNAL
        self.spec.global_lb = False
        return self
        
    def global_lb(self, enable: bool = True) -> Self:
        """Enable/disable global load balancing (chainable)"""
        self.spec.global_lb = enable
        return self
        
    def region(self, region_name: str) -> Self:
        """Set region for regional load balancer (chainable)"""
        self.spec.region = region_name
        self.spec.global_lb = False
        return self
        
    def health_check(self, path: str = "/", port: int = None, check_type: HealthCheckType = None) -> Self:
        """Configure health check (chainable)"""
        self.spec.health_check = HealthCheckSpec(
            check_type=check_type or HealthCheckType.HTTP,
            port=port or self.spec.port,
            path=path
        )
        return self
        
    def ssl_cert(self, cert_name: str) -> Self:
        """Add SSL certificate (chainable)"""
        if cert_name not in self.spec.ssl_certificates:
            self.spec.ssl_certificates.append(cert_name)
        return self
        
    def redirect_http(self, enable: bool = True) -> Self:
        """Enable HTTP to HTTPS redirect (chainable)"""
        self.spec.redirect_http_to_https = enable
        return self
        
    def add_instance_group(self, group: "InstanceGroup") -> Self:
        """Add instance group as backend (chainable)"""
        if group.name not in self.spec.backend_groups:
            self.spec.backend_groups.append(group.name)
        return self
        
    def add_instance(self, instance: "VirtualMachine") -> Self:
        """Add single instance as backend (chainable)"""
        if instance.name not in self.spec.backend_instances:
            self.spec.backend_instances.append(instance.name)
        return self
        
    def with_provider(self, provider) -> Self:
        """Associate with provider (chainable)"""
        self._provider = provider
        return self
        
    # Provider implementation methods
    
    def _provider_create(self) -> Dict[str, Any]:
        """Create the load balancer via provider"""
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
        """Update the load balancer via provider"""
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
        """Destroy the load balancer via provider"""
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
    
    def get_ip_address(self) -> Optional[str]:
        """Get load balancer IP address"""
        return self.status.provider_data.get("ip_address")
        
    def get_backends(self) -> List[Dict[str, Any]]:
        """Get backend configuration"""
        return self.status.provider_data.get("backends", [])
        
    def is_healthy(self) -> bool:
        """Check if all backends are healthy"""
        backends = self.get_backends()
        return all(backend.get("healthy", False) for backend in backends)