from typing import Optional, Dict, Any, Self, List, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

if TYPE_CHECKING:
    from infradsl.core.interfaces.provider import ProviderInterface

from ....core.nexus.base_resource import BaseResource, ResourceSpec


class LoadBalancerType(Enum):
    """Load balancer type"""
    APPLICATION = "application"  # ALB
    NETWORK = "network"          # NLB
    CLASSIC = "classic"          # CLB (legacy)
    GATEWAY = "gateway"          # GWLB


class LoadBalancerScheme(Enum):
    """Load balancer scheme"""
    INTERNET_FACING = "internet-facing"
    INTERNAL = "internal"


class TargetType(Enum):
    """Target group target type"""
    INSTANCE = "instance"
    IP = "ip"
    LAMBDA = "lambda"
    ALB = "alb"


class ProtocolType(Enum):
    """Load balancer protocol"""
    HTTP = "HTTP"
    HTTPS = "HTTPS"
    TCP = "TCP"
    TLS = "TLS"
    UDP = "UDP"
    TCP_UDP = "TCP_UDP"
    GENEVE = "GENEVE"


class HealthCheckProtocol(Enum):
    """Health check protocol"""
    HTTP = "HTTP"
    HTTPS = "HTTPS"
    TCP = "TCP"


@dataclass
class TargetGroupConfig:
    """Target group configuration"""
    name: str
    port: int
    protocol: ProtocolType
    target_type: TargetType = TargetType.INSTANCE
    health_check_path: str = "/"
    health_check_port: Optional[int] = None
    health_check_protocol: HealthCheckProtocol = HealthCheckProtocol.HTTP
    healthy_threshold: int = 2
    unhealthy_threshold: int = 2
    timeout: int = 5
    interval: int = 30
    matcher: str = "200"
    targets: List[Dict[str, Any]] = field(default_factory=list)
    

@dataclass
class ListenerConfig:
    """Load balancer listener configuration"""
    port: int
    protocol: ProtocolType
    ssl_certificate_arn: Optional[str] = None
    default_action_type: str = "forward"
    default_target_group: Optional[str] = None
    rules: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AWSLoadBalancerSpec(ResourceSpec):
    """Specification for AWS Load Balancer"""
    
    # Basic configuration
    load_balancer_type: LoadBalancerType = LoadBalancerType.APPLICATION
    scheme: LoadBalancerScheme = LoadBalancerScheme.INTERNET_FACING
    
    # Network configuration
    subnets: List[str] = field(default_factory=list)
    security_groups: List[str] = field(default_factory=list)  # ALB only
    
    # Target groups
    target_groups: List[TargetGroupConfig] = field(default_factory=list)
    
    # Listeners
    listeners: List[ListenerConfig] = field(default_factory=list)
    
    # Advanced configuration
    enable_cross_zone_load_balancing: bool = True
    enable_deletion_protection: bool = False
    enable_http2: bool = True  # ALB only
    idle_timeout: int = 60     # ALB only
    
    # Access logs
    access_logs_enabled: bool = False
    access_logs_bucket: str = ""
    access_logs_prefix: str = ""
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class AWSLoadBalancer(BaseResource):
    """
    AWS Load Balancer (ALB, NLB, CLB) with comprehensive features and Rails-like conventions.
    
    Examples:
        # Application Load Balancer for web applications
        alb = (AWSLoadBalancer("web-alb")
               .application()
               .internet_facing()
               .subnets(["subnet-web-1a", "subnet-web-1b"])
               .security_groups(["sg-alb"])
               .target_group("web-servers", 80, "HTTP")
               .add_targets("web-servers", [
                   {"id": "i-1234567890abcdef0", "port": 80},
                   {"id": "i-0987654321fedcba0", "port": 80}
               ])
               .listener(80, "HTTP", target_group="web-servers")
               .listener(443, "HTTPS", ssl_cert="arn:aws:acm:...", target_group="web-servers")
               .health_check("/health")
               .access_logs("my-logs-bucket", "alb-logs/")
               .production())
        
        # Network Load Balancer for high performance
        nlb = (AWSLoadBalancer("api-nlb")
               .network()
               .internet_facing()
               .subnets(["subnet-public-1a", "subnet-public-1b"])
               .target_group("api-servers", 8080, "TCP")
               .add_targets("api-servers", [
                   {"id": "10.0.1.100", "port": 8080},
                   {"id": "10.0.2.100", "port": 8080}
               ])
               .listener(80, "TCP", target_group="api-servers")
               .cross_zone_load_balancing()
               .production())
               
        # Internal Application Load Balancer
        internal_alb = (AWSLoadBalancer("internal-alb")
                       .application()
                       .internal()
                       .subnets(["subnet-app-1a", "subnet-app-1b"])
                       .security_groups(["sg-internal-alb"])
                       .target_group("backend-services", 8080, "HTTP")
                       .listener(80, "HTTP", target_group="backend-services")
                       .health_check("/api/health", port=8080)
                       .production())
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.spec: AWSLoadBalancerSpec = self._create_spec()
        self.metadata.annotations["resource_type"] = "AWSLoadBalancer"
        
    def _create_spec(self) -> AWSLoadBalancerSpec:
        return AWSLoadBalancerSpec()
        
    def _validate_spec(self) -> None:
        """Validate AWS Load Balancer specification"""
        if not self.spec.subnets:
            raise ValueError("At least one subnet is required")
            
        if (self.spec.load_balancer_type == LoadBalancerType.APPLICATION and 
            not self.spec.security_groups):
            raise ValueError("Application Load Balancer requires security groups")
            
        if not self.spec.target_groups:
            raise ValueError("At least one target group is required")
            
        if not self.spec.listeners:
            raise ValueError("At least one listener is required")
            
        # Validate target groups reference valid listeners
        tg_names = {tg.name for tg in self.spec.target_groups}
        for listener in self.spec.listeners:
            if listener.default_target_group and listener.default_target_group not in tg_names:
                raise ValueError(f"Listener references unknown target group: {listener.default_target_group}")
                
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        config = {
            "name": self.metadata.name,
            "load_balancer_type": self.spec.load_balancer_type.value,
            "scheme": self.spec.scheme.value,
            "subnets": self.spec.subnets,
            "enable_cross_zone_load_balancing": self.spec.enable_cross_zone_load_balancing,
            "enable_deletion_protection": self.spec.enable_deletion_protection,
            "target_groups": [self._target_group_to_config(tg) for tg in self.spec.target_groups],
            "listeners": [self._listener_to_config(listener) for listener in self.spec.listeners],
            "tags": {**self.spec.tags, **self.metadata.to_tags()},
        }
        
        # ALB-specific configuration
        if self.spec.load_balancer_type == LoadBalancerType.APPLICATION:
            config.update({
                "security_groups": self.spec.security_groups,
                "enable_http2": self.spec.enable_http2,
                "idle_timeout": self.spec.idle_timeout
            })
            
        # Access logs configuration
        if self.spec.access_logs_enabled:
            config["access_logs"] = {
                "enabled": True,
                "bucket": self.spec.access_logs_bucket,
                "prefix": self.spec.access_logs_prefix
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
        
    def _target_group_to_config(self, tg: TargetGroupConfig) -> Dict[str, Any]:
        """Convert target group to configuration"""
        config = {
            "name": tg.name,
            "port": tg.port,
            "protocol": tg.protocol.value,
            "target_type": tg.target_type.value,
            "health_check_path": tg.health_check_path,
            "health_check_protocol": tg.health_check_protocol.value,
            "healthy_threshold": tg.healthy_threshold,
            "unhealthy_threshold": tg.unhealthy_threshold,
            "timeout": tg.timeout,
            "interval": tg.interval,
            "matcher": tg.matcher,
            "targets": tg.targets
        }
        
        if tg.health_check_port:
            config["health_check_port"] = tg.health_check_port
            
        return config
        
    def _listener_to_config(self, listener: ListenerConfig) -> Dict[str, Any]:
        """Convert listener to configuration"""
        config = {
            "port": listener.port,
            "protocol": listener.protocol.value,
            "default_action": {
                "type": listener.default_action_type
            }
        }
        
        if listener.ssl_certificate_arn:
            config["ssl_policy"] = "ELBSecurityPolicy-TLS-1-2-2017-01"
            config["certificate_arn"] = listener.ssl_certificate_arn
            
        if listener.default_target_group:
            config["default_action"]["target_group_arn"] = listener.default_target_group
            
        if listener.rules:
            config["rules"] = listener.rules
            
        return config

    def _to_aws_config(self) -> Dict[str, Any]:
        """Convert to AWS Load Balancer configuration"""
        return {
            "resource_type": "aws_lb"
        }
        
    # Fluent interface methods
    
    # Load balancer type
    
    def application(self) -> Self:
        """Use Application Load Balancer (chainable)"""
        self.spec.load_balancer_type = LoadBalancerType.APPLICATION
        return self
        
    def network(self) -> Self:
        """Use Network Load Balancer (chainable)"""
        self.spec.load_balancer_type = LoadBalancerType.NETWORK
        return self
        
    def classic(self) -> Self:
        """Use Classic Load Balancer (chainable)"""
        self.spec.load_balancer_type = LoadBalancerType.CLASSIC
        return self
        
    def gateway(self) -> Self:
        """Use Gateway Load Balancer (chainable)"""
        self.spec.load_balancer_type = LoadBalancerType.GATEWAY
        return self
        
    # Scheme
    
    def internet_facing(self) -> Self:
        """Make load balancer internet-facing (chainable)"""
        self.spec.scheme = LoadBalancerScheme.INTERNET_FACING
        return self
        
    def internal(self) -> Self:
        """Make load balancer internal (chainable)"""
        self.spec.scheme = LoadBalancerScheme.INTERNAL
        return self
        
    # Network configuration
    
    def subnets(self, subnet_ids: List[str]) -> Self:
        """Set subnets (chainable)"""
        self.spec.subnets = subnet_ids.copy()
        return self
        
    def subnet(self, subnet_id: str) -> Self:
        """Add subnet (chainable)"""
        if subnet_id not in self.spec.subnets:
            self.spec.subnets.append(subnet_id)
        return self
        
    def security_groups(self, sg_ids: List[str]) -> Self:
        """Set security groups (ALB only) (chainable)"""
        self.spec.security_groups = sg_ids.copy()
        return self
        
    def security_group(self, sg_id: str) -> Self:
        """Add security group (ALB only) (chainable)"""
        if sg_id not in self.spec.security_groups:
            self.spec.security_groups.append(sg_id)
        return self
        
    # Target groups
    
    def target_group(self, name: str, port: int, protocol: str, 
                    target_type: str = "instance") -> Self:
        """Add target group (chainable)"""
        tg_config = TargetGroupConfig(
            name=f"{self.name}-{name}" if not name.startswith(self.name) else name,
            port=port,
            protocol=ProtocolType(protocol.upper()),
            target_type=TargetType(target_type)
        )
        self.spec.target_groups.append(tg_config)
        return self
        
    def add_targets(self, target_group_name: str, targets: List[Dict[str, Any]]) -> Self:
        """Add targets to target group (chainable)"""
        full_tg_name = f"{self.name}-{target_group_name}" if not target_group_name.startswith(self.name) else target_group_name
        
        for tg in self.spec.target_groups:
            if tg.name == full_tg_name:
                tg.targets.extend(targets)
                return self
                
        raise ValueError(f"Target group '{full_tg_name}' not found")
        
    def health_check(self, path: str = "/", port: int = None, protocol: str = "HTTP",
                    healthy_threshold: int = 2, unhealthy_threshold: int = 2,
                    timeout: int = 5, interval: int = 30, matcher: str = "200") -> Self:
        """Configure health check for most recent target group (chainable)"""
        if not self.spec.target_groups:
            raise ValueError("No target groups defined")
            
        tg = self.spec.target_groups[-1]
        tg.health_check_path = path
        tg.health_check_port = port
        tg.health_check_protocol = HealthCheckProtocol(protocol.upper())
        tg.healthy_threshold = healthy_threshold
        tg.unhealthy_threshold = unhealthy_threshold
        tg.timeout = timeout
        tg.interval = interval
        tg.matcher = matcher
        
        return self
        
    # Listeners
    
    def listener(self, port: int, protocol: str, ssl_cert: str = None, 
                target_group: str = None) -> Self:
        """Add listener (chainable)"""
        if target_group and not target_group.startswith(self.name):
            target_group = f"{self.name}-{target_group}"
            
        listener_config = ListenerConfig(
            port=port,
            protocol=ProtocolType(protocol.upper()),
            ssl_certificate_arn=ssl_cert,
            default_target_group=target_group
        )
        self.spec.listeners.append(listener_config)
        return self
        
    def http_listener(self, port: int = 80, target_group: str = None) -> Self:
        """Add HTTP listener (chainable)"""
        return self.listener(port, "HTTP", target_group=target_group)
        
    def https_listener(self, port: int = 443, ssl_cert: str = None, target_group: str = None) -> Self:
        """Add HTTPS listener (chainable)"""
        return self.listener(port, "HTTPS", ssl_cert, target_group)
        
    def tcp_listener(self, port: int, target_group: str = None) -> Self:
        """Add TCP listener (NLB) (chainable)"""
        return self.listener(port, "TCP", target_group=target_group)
        
    # Advanced configuration
    
    def cross_zone_load_balancing(self, enabled: bool = True) -> Self:
        """Enable/disable cross-zone load balancing (chainable)"""
        self.spec.enable_cross_zone_load_balancing = enabled
        return self
        
    def deletion_protection(self, enabled: bool = True) -> Self:
        """Enable/disable deletion protection (chainable)"""
        self.spec.enable_deletion_protection = enabled
        return self
        
    def http2(self, enabled: bool = True) -> Self:
        """Enable/disable HTTP/2 (ALB only) (chainable)"""
        self.spec.enable_http2 = enabled
        return self
        
    def idle_timeout(self, seconds: int) -> Self:
        """Set idle timeout (ALB only) (chainable)"""
        self.spec.idle_timeout = seconds
        return self
        
    # Access logs
    
    def access_logs(self, bucket: str, prefix: str = "", enabled: bool = True) -> Self:
        """Configure access logs (chainable)"""
        self.spec.access_logs_enabled = enabled
        self.spec.access_logs_bucket = bucket
        self.spec.access_logs_prefix = prefix or f"{self.name}-logs/"
        return self
        
    # Common patterns
    
    def web_application_alb(self, subnets: List[str], security_groups: List[str],
                           ssl_cert: str = None) -> Self:
        """Configure for web applications (chainable)"""
        config = (self
                 .application()
                 .internet_facing()
                 .subnets(subnets)
                 .security_groups(security_groups)
                 .target_group("web-servers", 80, "HTTP")
                 .health_check("/health")
                 .http_listener(80, "web-servers"))
                 
        if ssl_cert:
            config = (config
                     .https_listener(443, ssl_cert, "web-servers")
                     .http2())
                     
        return config
        
    def api_gateway_alb(self, subnets: List[str], security_groups: List[str],
                       ssl_cert: str, api_port: int = 8080) -> Self:
        """Configure for API gateway (chainable)"""
        return (self
                .application()
                .internet_facing()
                .subnets(subnets)
                .security_groups(security_groups)
                .target_group("api-servers", api_port, "HTTP")
                .health_check("/health", port=api_port)
                .https_listener(443, ssl_cert, "api-servers")
                .http2()
                .idle_timeout(30))
                
    def high_performance_nlb(self, subnets: List[str], port: int = 80) -> Self:
        """Configure for high performance (chainable)"""
        return (self
                .network()
                .internet_facing()
                .subnets(subnets)
                .target_group("servers", port, "TCP")
                .tcp_listener(port, "servers")
                .cross_zone_load_balancing())
                
    def internal_microservices_alb(self, subnets: List[str], security_groups: List[str]) -> Self:
        """Configure for internal microservices (chainable)"""
        return (self
                .application()
                .internal()
                .subnets(subnets)
                .security_groups(security_groups)
                .target_group("services", 8080, "HTTP")
                .health_check("/health", port=8080)
                .http_listener(80, "services")
                .idle_timeout(60))
                
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
                .deletion_protection()
                .cross_zone_load_balancing()
                .tag("Environment", "production")
                .tag("Backup", "required")
                .tag("Monitoring", "enabled"))
                
    def staging(self) -> Self:
        """Configure for staging environment (chainable)"""
        return (self
                .cross_zone_load_balancing()
                .tag("Environment", "staging")
                .tag("Monitoring", "basic"))
                
    def development(self) -> Self:
        """Configure for development environment (chainable)"""
        return (self
                .tag("Environment", "development")
                .tag("AutoShutdown", "enabled"))
                
    # Provider implementation methods
    
    def _provider_create(self) -> Dict[str, Any]:
        """Create the Load Balancer via provider"""
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
        """Update the Load Balancer via provider"""
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
        """Destroy the Load Balancer via provider"""
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
    
    def get_load_balancer_type(self) -> str:
        """Get load balancer type"""
        return self.spec.load_balancer_type.value
        
    def is_internet_facing(self) -> bool:
        """Check if load balancer is internet-facing"""
        return self.spec.scheme == LoadBalancerScheme.INTERNET_FACING
        
    def get_target_groups(self) -> List[str]:
        """Get target group names"""
        return [tg.name for tg in self.spec.target_groups]
        
    def get_listeners(self) -> List[Dict[str, Any]]:
        """Get listener configurations"""
        return [
            {
                "port": listener.port,
                "protocol": listener.protocol.value,
                "ssl_enabled": listener.ssl_certificate_arn is not None
            }
            for listener in self.spec.listeners
        ]