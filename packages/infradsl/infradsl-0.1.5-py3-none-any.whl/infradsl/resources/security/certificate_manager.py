from typing import Optional, Dict, Any, Self, List, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

if TYPE_CHECKING:
    from infradsl.core.interfaces.provider import ProviderInterface

from ...core.nexus.base_resource import BaseResource, ResourceSpec


class CertificateType(Enum):
    """Certificate types"""
    MANAGED = "managed"       # Google-managed certificate
    SELF_MANAGED = "self_managed"  # User-provided certificate


class CertificateScope(Enum):
    """Certificate scopes"""
    DEFAULT = "DEFAULT"       # Global load balancer use
    EDGE_CACHE = "EDGE_CACHE"  # Cloud CDN use


@dataclass
class ManagedCertificateSpec:
    """Managed certificate configuration"""
    domains: List[str] = field(default_factory=list)
    dns_authorizations: List[str] = field(default_factory=list)


@dataclass
class SelfManagedCertificateSpec:
    """Self-managed certificate configuration"""
    certificate_pem: Optional[str] = None
    private_key_pem: Optional[str] = None
    certificate_file: Optional[str] = None
    private_key_file: Optional[str] = None


@dataclass
class CertificateManagerSpec(ResourceSpec):
    """Specification for a Certificate Manager resource"""
    
    # Core configuration
    certificate_type: CertificateType = CertificateType.MANAGED
    scope: CertificateScope = CertificateScope.DEFAULT
    
    # Managed certificate configuration
    managed_config: Optional[ManagedCertificateSpec] = None
    
    # Self-managed certificate configuration
    self_managed_config: Optional[SelfManagedCertificateSpec] = None
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class CertificateManager(BaseResource):
    """
    GCP Certificate Manager for SSL/TLS certificates with Rails-like conventions.
    
    Examples:
        # Managed certificate for single domain
        cert = (CertificateManager("my-app-cert")
                .managed()
                .domain("myapp.com")
                .global_scope())
        
        # Managed certificate for multiple domains
        multi_cert = (CertificateManager("multi-domain-cert")
                     .managed()
                     .domains(["example.com", "www.example.com", "api.example.com"])
                     .dns_authorization("example-dns-auth"))
        
        # Self-managed certificate from files
        custom_cert = (CertificateManager("custom-cert")
                      .self_managed()
                      .certificate_file("./ssl/cert.pem")
                      .private_key_file("./ssl/key.pem"))
        
        # Certificate for Cloud CDN
        cdn_cert = (CertificateManager("cdn-cert")
                   .managed()
                   .domain("cdn.myapp.com")
                   .edge_cache_scope())
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.spec: CertificateManagerSpec = self._create_spec()
        # Store resource type in annotations for cache fingerprinting
        self.metadata.annotations["resource_type"] = "CertificateManager"
        
    def _create_spec(self) -> CertificateManagerSpec:
        return CertificateManagerSpec()
        
    def _validate_spec(self) -> None:
        """Validate certificate specification"""
        if self.spec.certificate_type == CertificateType.MANAGED:
            if not self.spec.managed_config or not self.spec.managed_config.domains:
                raise ValueError("Managed certificate requires at least one domain")
        elif self.spec.certificate_type == CertificateType.SELF_MANAGED:
            if not self.spec.self_managed_config:
                raise ValueError("Self-managed certificate requires certificate configuration")
            config = self.spec.self_managed_config
            if not ((config.certificate_pem and config.private_key_pem) or 
                   (config.certificate_file and config.private_key_file)):
                raise ValueError("Self-managed certificate requires both certificate and private key")
                
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        config = {
            "name": self.metadata.name,
            "scope": self.spec.scope.value,
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

    def _to_gcp_config(self) -> Dict[str, Any]:
        """Convert to GCP Certificate Manager configuration"""
        config = {
            "resource_type": "certificate_manager_certificate"
        }
        
        if self.spec.certificate_type == CertificateType.MANAGED:
            config["managed"] = {
                "domains": self.spec.managed_config.domains
            }
            
            if self.spec.managed_config.dns_authorizations:
                config["managed"]["dns_authorizations"] = self.spec.managed_config.dns_authorizations
                
        elif self.spec.certificate_type == CertificateType.SELF_MANAGED:
            self_managed = {}
            
            if self.spec.self_managed_config.certificate_pem:
                self_managed["certificate_pem"] = self.spec.self_managed_config.certificate_pem
                self_managed["private_key_pem"] = self.spec.self_managed_config.private_key_pem
            elif self.spec.self_managed_config.certificate_file:
                # Read certificate files
                import os
                cert_path = os.path.expanduser(self.spec.self_managed_config.certificate_file)
                key_path = os.path.expanduser(self.spec.self_managed_config.private_key_file)
                
                with open(cert_path, 'r') as f:
                    self_managed["certificate_pem"] = f.read()
                with open(key_path, 'r') as f:
                    self_managed["private_key_pem"] = f.read()
                    
            config["self_managed"] = self_managed

        return config
        
    # Fluent interface methods
    
    # Certificate type methods
    
    def managed(self) -> Self:
        """Use Google-managed certificate (chainable)"""
        self.spec.certificate_type = CertificateType.MANAGED
        if not self.spec.managed_config:
            self.spec.managed_config = ManagedCertificateSpec()
        return self
        
    def self_managed(self) -> Self:
        """Use self-managed certificate (chainable)"""
        self.spec.certificate_type = CertificateType.SELF_MANAGED
        if not self.spec.self_managed_config:
            self.spec.self_managed_config = SelfManagedCertificateSpec()
        return self
        
    # Scope methods
    
    def global_scope(self) -> Self:
        """Use for global load balancers (chainable)"""
        self.spec.scope = CertificateScope.DEFAULT
        return self
        
    def edge_cache_scope(self) -> Self:
        """Use for Cloud CDN (chainable)"""
        self.spec.scope = CertificateScope.EDGE_CACHE
        return self
        
    # Managed certificate methods
    
    def domain(self, domain_name: str) -> Self:
        """Add domain to managed certificate (chainable)"""
        if not self.spec.managed_config:
            self.spec.managed_config = ManagedCertificateSpec()
        if domain_name not in self.spec.managed_config.domains:
            self.spec.managed_config.domains.append(domain_name)
        return self
        
    def domains(self, domain_list: List[str]) -> Self:
        """Set domains for managed certificate (chainable)"""
        if not self.spec.managed_config:
            self.spec.managed_config = ManagedCertificateSpec()
        self.spec.managed_config.domains = domain_list.copy()
        return self
        
    def dns_authorization(self, auth_name: str) -> Self:
        """Add DNS authorization (chainable)"""
        if not self.spec.managed_config:
            self.spec.managed_config = ManagedCertificateSpec()
        if auth_name not in self.spec.managed_config.dns_authorizations:
            self.spec.managed_config.dns_authorizations.append(auth_name)
        return self
        
    def wildcard_domain(self, base_domain: str) -> Self:
        """Add wildcard domain (chainable)"""
        return self.domain(f"*.{base_domain}")
        
    # Self-managed certificate methods
    
    def certificate_pem(self, cert_pem: str) -> Self:
        """Set certificate PEM content (chainable)"""
        if not self.spec.self_managed_config:
            self.spec.self_managed_config = SelfManagedCertificateSpec()
        self.spec.self_managed_config.certificate_pem = cert_pem
        return self
        
    def private_key_pem(self, key_pem: str) -> Self:
        """Set private key PEM content (chainable)"""
        if not self.spec.self_managed_config:
            self.spec.self_managed_config = SelfManagedCertificateSpec()
        self.spec.self_managed_config.private_key_pem = key_pem
        return self
        
    def certificate_file(self, file_path: str) -> Self:
        """Set certificate file path (chainable)"""
        if not self.spec.self_managed_config:
            self.spec.self_managed_config = SelfManagedCertificateSpec()
        self.spec.self_managed_config.certificate_file = file_path
        return self
        
    def private_key_file(self, file_path: str) -> Self:
        """Set private key file path (chainable)"""
        if not self.spec.self_managed_config:
            self.spec.self_managed_config = SelfManagedCertificateSpec()
        self.spec.self_managed_config.private_key_file = file_path
        return self
        
    def from_files(self, cert_file: str, key_file: str) -> Self:
        """Set certificate from files (chainable)"""
        return self.certificate_file(cert_file).private_key_file(key_file)
        
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
    
    def production(self, domains: List[str]) -> Self:
        """Configure for production environment (chainable)"""
        return (self
                .managed()
                .domains(domains)
                .global_scope()
                .label("environment", "production"))
                
    def staging(self, domain: str) -> Self:
        """Configure for staging environment (chainable)"""
        return (self
                .managed()
                .domain(domain)
                .global_scope()
                .label("environment", "staging"))
                
    def development(self, domain: str) -> Self:
        """Configure for development environment (chainable)"""
        return (self
                .managed()
                .domain(domain)
                .global_scope()
                .label("environment", "development"))
                
    # Provider implementation methods
    
    def _provider_create(self) -> Dict[str, Any]:
        """Create the certificate via provider"""
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
        """Update the certificate via provider"""
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
        """Destroy the certificate via provider"""
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
    
    def get_certificate_id(self) -> Optional[str]:
        """Get certificate ID"""
        return self.status.provider_data.get("certificate_id")
        
    def get_status(self) -> Optional[str]:
        """Get certificate status"""
        return self.status.provider_data.get("state")
        
    def is_active(self) -> bool:
        """Check if certificate is active"""
        return self.get_status() == "ACTIVE"