from typing import Optional, Dict, Any, Self, List, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

if TYPE_CHECKING:
    from infradsl.core.interfaces.provider import ProviderInterface

from ....core.nexus.base_resource import BaseResource, ResourceSpec


class Protocol(Enum):
    """Network protocols"""
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    ALL = "-1"


class RuleType(Enum):
    """Security group rule type"""
    INGRESS = "ingress"
    EGRESS = "egress"


@dataclass
class SecurityGroupRule:
    """Security group rule specification"""
    rule_type: RuleType
    protocol: Protocol
    from_port: Optional[int] = None
    to_port: Optional[int] = None
    cidr_blocks: List[str] = field(default_factory=list)
    source_security_group_id: Optional[str] = None
    description: str = ""


@dataclass
class AWSSecurityGroupSpec(ResourceSpec):
    """Specification for AWS Security Group"""
    
    # Basic configuration
    vpc_id: str = ""
    description: str = ""
    
    # Rules
    rules: List[SecurityGroupRule] = field(default_factory=list)
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class AWSSecurityGroup(BaseResource):
    """
    AWS Security Group with comprehensive rule management and Rails-like conventions.
    
    Examples:
        # Web server security group
        web_sg = (AWSSecurityGroup("web-sg")
                   .vpc("vpc-12345678")
                   .description("Security group for web servers")
                   .allow_http()
                   .allow_https()
                   .allow_ssh_from("203.0.113.0/24")
                   .allow_outbound_all()
                   .production())
        
        # Database security group
        db_sg = (AWSSecurityGroup("db-sg")
                 .vpc("vpc-12345678")
                 .description("Security group for database servers")
                 .allow_mysql_from_sg("sg-app")
                 .allow_postgresql_from_sg("sg-app")
                 .allow_outbound_https()
                 .deny_all_other_inbound()
                 .production())
                 
        # Application server security group
        app_sg = (AWSSecurityGroup("app-sg")
                  .vpc("vpc-12345678")
                  .description("Security group for application servers")
                  .allow_port(8080, from_sg="sg-alb")
                  .allow_port(9090, from_cidr="10.0.0.0/8", description="Monitoring")
                  .allow_ssh_from("10.0.0.0/8")
                  .allow_outbound_all()
                  .production())
                  
        # Load balancer security group
        alb_sg = (AWSSecurityGroup("alb-sg")
                  .vpc("vpc-12345678")
                  .description("Security group for Application Load Balancer")
                  .allow_http_from_anywhere()
                  .allow_https_from_anywhere()
                  .allow_outbound_to_sg("sg-app", 8080)
                  .production())
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.spec: AWSSecurityGroupSpec = self._create_spec()
        self.metadata.annotations["resource_type"] = "AWSSecurityGroup"
        
    def _create_spec(self) -> AWSSecurityGroupSpec:
        return AWSSecurityGroupSpec()
        
    def _validate_spec(self) -> None:
        """Validate AWS Security Group specification"""
        if not self.spec.vpc_id:
            raise ValueError("VPC ID is required for Security Group")
            
        # Validate rules
        for rule in self.spec.rules:
            if rule.protocol != Protocol.ALL:
                if rule.protocol in [Protocol.TCP, Protocol.UDP]:
                    if rule.from_port is None or rule.to_port is None:
                        raise ValueError(f"TCP/UDP rules must specify from_port and to_port")
                elif rule.protocol == Protocol.ICMP:
                    # ICMP can have from_port/to_port for type/code, but they're optional
                    pass
                    
            # Either CIDR blocks or source security group must be specified
            if not rule.cidr_blocks and not rule.source_security_group_id:
                raise ValueError("Rule must specify either cidr_blocks or source_security_group_id")
                
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        config = {
            "name": self.metadata.name,
            "vpc_id": self.spec.vpc_id,
            "description": self.spec.description or f"Security group for {self.metadata.name}",
            "ingress": [self._rule_to_config(rule) for rule in self.spec.rules if rule.rule_type == RuleType.INGRESS],
            "egress": [self._rule_to_config(rule) for rule in self.spec.rules if rule.rule_type == RuleType.EGRESS],
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
        
    def _rule_to_config(self, rule: SecurityGroupRule) -> Dict[str, Any]:
        """Convert security group rule to configuration"""
        config = {
            "protocol": rule.protocol.value,
            "description": rule.description or f"{rule.rule_type.value} rule"
        }
        
        if rule.protocol != Protocol.ALL:
            if rule.from_port is not None:
                config["from_port"] = rule.from_port
            if rule.to_port is not None:
                config["to_port"] = rule.to_port
                
        if rule.cidr_blocks:
            config["cidr_blocks"] = rule.cidr_blocks
        elif rule.source_security_group_id:
            config["source_security_group_id"] = rule.source_security_group_id
            
        return config

    def _to_aws_config(self) -> Dict[str, Any]:
        """Convert to AWS Security Group configuration"""
        return {
            "resource_type": "aws_security_group"
        }
        
    # Fluent interface methods
    
    # Basic configuration
    
    def vpc(self, vpc_id: str) -> Self:
        """Set VPC ID (chainable)"""
        self.spec.vpc_id = vpc_id
        return self
        
    def description(self, desc: str) -> Self:
        """Set security group description (chainable)"""
        self.spec.description = desc
        return self
        
    # Rule management helpers
    
    def _add_rule(self, rule_type: RuleType, protocol: Protocol, from_port: int = None, 
                  to_port: int = None, cidr_blocks: List[str] = None, 
                  source_sg: str = None, description: str = "") -> Self:
        """Add security group rule"""
        rule = SecurityGroupRule(
            rule_type=rule_type,
            protocol=protocol,
            from_port=from_port,
            to_port=to_port,
            cidr_blocks=cidr_blocks or [],
            source_security_group_id=source_sg,
            description=description
        )
        self.spec.rules.append(rule)
        return self
        
    # Generic rule methods
    
    def allow_port(self, port: int, protocol: str = "tcp", from_cidr: str = None,
                   from_sg: str = None, description: str = "") -> Self:
        """Allow specific port (chainable)"""
        cidr_blocks = [from_cidr] if from_cidr else []
        return self._add_rule(
            RuleType.INGRESS, 
            Protocol(protocol), 
            port, port, 
            cidr_blocks, 
            from_sg, 
            description
        )
        
    def allow_port_range(self, from_port: int, to_port: int, protocol: str = "tcp",
                        from_cidr: str = None, from_sg: str = None, description: str = "") -> Self:
        """Allow port range (chainable)"""
        cidr_blocks = [from_cidr] if from_cidr else []
        return self._add_rule(
            RuleType.INGRESS, 
            Protocol(protocol), 
            from_port, to_port, 
            cidr_blocks, 
            from_sg, 
            description
        )
        
    def allow_outbound_port(self, port: int, protocol: str = "tcp", to_cidr: str = None,
                           to_sg: str = None, description: str = "") -> Self:
        """Allow outbound to specific port (chainable)"""
        cidr_blocks = [to_cidr] if to_cidr else []
        return self._add_rule(
            RuleType.EGRESS, 
            Protocol(protocol), 
            port, port, 
            cidr_blocks, 
            to_sg, 
            description
        )
        
    # Common web protocols
    
    def allow_http(self, from_cidr: str = "0.0.0.0/0") -> Self:
        """Allow HTTP traffic (chainable)"""
        return self.allow_port(80, "tcp", from_cidr, description="HTTP traffic")
        
    def allow_https(self, from_cidr: str = "0.0.0.0/0") -> Self:
        """Allow HTTPS traffic (chainable)"""
        return self.allow_port(443, "tcp", from_cidr, description="HTTPS traffic")
        
    def allow_http_from_anywhere(self) -> Self:
        """Allow HTTP from anywhere (chainable)"""
        return self.allow_http("0.0.0.0/0")
        
    def allow_https_from_anywhere(self) -> Self:
        """Allow HTTPS from anywhere (chainable)"""
        return self.allow_https("0.0.0.0/0")
        
    def allow_ssh(self, from_cidr: str = "0.0.0.0/0") -> Self:
        """Allow SSH traffic (chainable)"""
        return self.allow_port(22, "tcp", from_cidr, description="SSH access")
        
    def allow_ssh_from(self, cidr: str) -> Self:
        """Allow SSH from specific CIDR (chainable)"""
        return self.allow_ssh(cidr)
        
    def allow_ssh_from_sg(self, sg_id: str) -> Self:
        """Allow SSH from security group (chainable)"""
        return self.allow_port(22, "tcp", from_sg=sg_id, description="SSH from SG")
        
    # Database protocols
    
    def allow_mysql(self, from_cidr: str = None, from_sg: str = None) -> Self:
        """Allow MySQL traffic (chainable)"""
        return self.allow_port(3306, "tcp", from_cidr, from_sg, "MySQL traffic")
        
    def allow_mysql_from_sg(self, sg_id: str) -> Self:
        """Allow MySQL from security group (chainable)"""
        return self.allow_mysql(from_sg=sg_id)
        
    def allow_postgresql(self, from_cidr: str = None, from_sg: str = None) -> Self:
        """Allow PostgreSQL traffic (chainable)"""
        return self.allow_port(5432, "tcp", from_cidr, from_sg, "PostgreSQL traffic")
        
    def allow_postgresql_from_sg(self, sg_id: str) -> Self:
        """Allow PostgreSQL from security group (chainable)"""
        return self.allow_postgresql(from_sg=sg_id)
        
    def allow_redis(self, from_cidr: str = None, from_sg: str = None) -> Self:
        """Allow Redis traffic (chainable)"""
        return self.allow_port(6379, "tcp", from_cidr, from_sg, "Redis traffic")
        
    def allow_redis_from_sg(self, sg_id: str) -> Self:
        """Allow Redis from security group (chainable)"""
        return self.allow_redis(from_sg=sg_id)
        
    # Application protocols
    
    def allow_custom_app(self, port: int, from_sg: str = None, from_cidr: str = None) -> Self:
        """Allow custom application port (chainable)"""
        return self.allow_port(port, "tcp", from_cidr, from_sg, f"Custom app port {port}")
        
    def allow_monitoring(self, from_cidr: str = "10.0.0.0/8") -> Self:
        """Allow common monitoring ports (chainable)"""
        return (self
                .allow_port(9090, "tcp", from_cidr, description="Prometheus")
                .allow_port(3000, "tcp", from_cidr, description="Grafana")
                .allow_port(9100, "tcp", from_cidr, description="Node Exporter"))
                
    def allow_health_checks(self, port: int = 80, from_cidr: str = None) -> Self:
        """Allow health check traffic (chainable)"""
        # AWS ALB health check ranges
        alb_cidrs = ["172.31.0.0/16"] if not from_cidr else [from_cidr]
        return self.allow_port(port, "tcp", alb_cidrs[0], description="Health checks")
        
    # Outbound rules
    
    def allow_outbound_all(self) -> Self:
        """Allow all outbound traffic (chainable)"""
        return self._add_rule(
            RuleType.EGRESS, 
            Protocol.ALL, 
            cidr_blocks=["0.0.0.0/0"], 
            description="All outbound traffic"
        )
        
    def allow_outbound_https(self) -> Self:
        """Allow outbound HTTPS (chainable)"""
        return self.allow_outbound_port(443, "tcp", "0.0.0.0/0", description="Outbound HTTPS")
        
    def allow_outbound_http(self) -> Self:
        """Allow outbound HTTP (chainable)"""
        return self.allow_outbound_port(80, "tcp", "0.0.0.0/0", description="Outbound HTTP")
        
    def allow_outbound_dns(self) -> Self:
        """Allow outbound DNS (chainable)"""
        return (self
                .allow_outbound_port(53, "tcp", "0.0.0.0/0", description="Outbound DNS TCP")
                .allow_outbound_port(53, "udp", "0.0.0.0/0", description="Outbound DNS UDP"))
                
    def allow_outbound_to_sg(self, sg_id: str, port: int, protocol: str = "tcp") -> Self:
        """Allow outbound to specific security group (chainable)"""
        return self.allow_outbound_port(port, protocol, to_sg=sg_id, 
                                       description=f"Outbound to {sg_id}")
        
    # Security patterns
    
    def web_server_rules(self) -> Self:
        """Add standard web server rules (chainable)"""
        return (self
                .allow_http_from_anywhere()
                .allow_https_from_anywhere()
                .allow_ssh_from("10.0.0.0/8")
                .allow_outbound_all())
                
    def app_server_rules(self, app_port: int = 8080, alb_sg: str = None) -> Self:
        """Add standard application server rules (chainable)"""
        config = (self
                 .allow_port(app_port, from_cidr="10.0.0.0/8", description="App traffic")
                 .allow_ssh_from("10.0.0.0/8")
                 .allow_monitoring()
                 .allow_outbound_https()
                 .allow_outbound_dns())
                 
        if alb_sg:
            config = config.allow_port(app_port, from_sg=alb_sg, description="ALB to app")
            
        return config
        
    def database_rules(self, db_type: str = "mysql", app_sg: str = None) -> Self:
        """Add standard database rules (chainable)"""
        config = self.allow_ssh_from("10.0.0.0/8")
        
        if db_type == "mysql":
            if app_sg:
                config = config.allow_mysql_from_sg(app_sg)
            else:
                config = config.allow_mysql(from_cidr="10.0.0.0/8")
        elif db_type == "postgresql":
            if app_sg:
                config = config.allow_postgresql_from_sg(app_sg)
            else:
                config = config.allow_postgresql(from_cidr="10.0.0.0/8")
                
        return (config
                .allow_outbound_https()
                .allow_outbound_dns())
                
    def alb_rules(self, app_sg: str = None, app_port: int = 8080) -> Self:
        """Add Application Load Balancer rules (chainable)"""
        config = (self
                 .allow_http_from_anywhere()
                 .allow_https_from_anywhere())
                 
        if app_sg:
            config = config.allow_outbound_to_sg(app_sg, app_port)
        else:
            config = config.allow_outbound_port(app_port, to_cidr="10.0.0.0/8")
            
        return config
        
    # Restrictive patterns
    
    def deny_all_other_inbound(self) -> Self:
        """Add explicit deny rule (AWS default, but for clarity) (chainable)"""
        # AWS security groups are deny by default, so this is mostly for documentation
        return self.tag("DefaultBehavior", "DenyAllInbound")
        
    def internal_only(self) -> Self:
        """Restrict to internal traffic only (chainable)"""
        return self.tag("NetworkScope", "InternalOnly")
        
    def bastion_accessible(self, bastion_sg: str) -> Self:
        """Allow access from bastion host (chainable)"""
        return self.allow_ssh_from_sg(bastion_sg)
        
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
                .tag("Environment", "production")
                .tag("Monitoring", "enabled")
                .tag("Compliance", "required"))
                
    def staging(self) -> Self:
        """Configure for staging environment (chainable)"""
        return (self
                .tag("Environment", "staging")
                .tag("Monitoring", "basic"))
                
    def development(self) -> Self:
        """Configure for development environment (chainable)"""
        return (self
                .tag("Environment", "development")
                .tag("AutoShutdown", "enabled"))
                
    # Provider implementation methods
    
    def _provider_create(self) -> Dict[str, Any]:
        """Create the Security Group via provider"""
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
        """Update the Security Group via provider"""
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
        """Destroy the Security Group via provider"""
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
    
    def get_rules_count(self) -> Dict[str, int]:
        """Get count of ingress and egress rules"""
        return {
            "ingress": len([r for r in self.spec.rules if r.rule_type == RuleType.INGRESS]),
            "egress": len([r for r in self.spec.rules if r.rule_type == RuleType.EGRESS]),
            "total": len(self.spec.rules)
        }
        
    def get_vpc_id(self) -> str:
        """Get VPC ID"""
        return self.spec.vpc_id
        
    def has_rule_for_port(self, port: int, rule_type: RuleType = RuleType.INGRESS) -> bool:
        """Check if security group has rule for specific port"""
        for rule in self.spec.rules:
            if (rule.rule_type == rule_type and 
                rule.from_port is not None and rule.to_port is not None and
                rule.from_port <= port <= rule.to_port):
                return True
        return False