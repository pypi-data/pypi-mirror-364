from typing import Optional, Dict, Any, Self, List, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
import base64
import json
import secrets
import string

if TYPE_CHECKING:
    from infradsl.core.interfaces.provider import ProviderInterface

from ...core.nexus.base_resource import BaseResource, ResourceSpec


class SecretDataType(Enum):
    """Secret data types"""
    STRING = "string"
    BINARY = "binary"
    JSON = "json"


@dataclass
class SecretReplication:
    """Secret replication configuration"""
    automatic: bool = True
    user_managed_replicas: List[str] = field(default_factory=list)


@dataclass
class SecretManagerSpec(ResourceSpec):
    """Specification for a Secret Manager resource"""
    
    # Secret data
    secret_data: Optional[str] = None
    secret_file: Optional[str] = None
    secret_type: SecretDataType = SecretDataType.STRING
    
    # Replication configuration
    replication: SecretReplication = field(default_factory=SecretReplication)
    
    # Version management
    ttl_seconds: Optional[int] = None  # Auto-delete after TTL
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class SecretManager(BaseResource):
    """
    GCP Secret Manager for secure secret storage with Rails-like conventions.
    
    Examples:
        # Simple string secret
        api_key = (SecretManager("api-key")
                  .value("sk-1234567890abcdef")
                  .automatic_replication())
        
        # Secret from file
        cert_secret = (SecretManager("ssl-certificate")
                      .from_file("./ssl/certificate.pem")
                      .regional_replication(["us-central1", "us-west1"]))
        
        # JSON configuration secret
        config_secret = (SecretManager("app-config")
                        .json_value({
                            "database_url": "postgres://...",
                            "api_endpoint": "https://api.example.com",
                            "debug": False
                        })
                        .automatic_replication())
        
        # Binary secret with TTL
        binary_secret = (SecretManager("binary-data")
                        .binary_from_file("./data.bin")
                        .ttl_days(30)
                        .production())
        
        # Database credentials
        db_creds = (SecretManager("database-credentials")
                   .json_value({
                       "username": "app_user",
                       "password": "secure_password_123",
                       "host": "db.example.com",
                       "port": 5432,
                       "database": "myapp_prod"
                   })
                   .regional_replication(["us-central1", "us-east1"]))
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.spec: SecretManagerSpec = self._create_spec()
        # Store resource type in annotations for cache fingerprinting
        self.metadata.annotations["resource_type"] = "SecretManager"
        
    def _create_spec(self) -> SecretManagerSpec:
        return SecretManagerSpec()
        
    def _validate_spec(self) -> None:
        """Validate secret specification"""
        if not self.spec.secret_data and not self.spec.secret_file:
            raise ValueError("Must specify either secret data or secret file")
            
        if self.spec.secret_data and self.spec.secret_file:
            raise ValueError("Cannot specify both secret data and secret file")
            
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        # Resolve secret data
        secret_data = self._resolve_secret_data()

        config = {
            "secret_id": self.metadata.name,
            "secret_data": secret_data,
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
        
    def _resolve_secret_data(self) -> str:
        """Resolve secret data from value or file"""
        if self.spec.secret_data:
            return self.spec.secret_data
        elif self.spec.secret_file:
            import os
            file_path = os.path.expanduser(self.spec.secret_file)
            
            if self.spec.secret_type == SecretDataType.BINARY:
                with open(file_path, 'rb') as f:
                    binary_data = f.read()
                    return base64.b64encode(binary_data).decode('utf-8')
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
        else:
            raise ValueError("No secret data specified")

    def _to_gcp_config(self) -> Dict[str, Any]:
        """Convert to GCP Secret Manager configuration"""
        config = {
            "resource_type": "secret_manager_secret"
        }
        
        # Replication configuration
        if self.spec.replication.automatic:
            config["replication"] = {"automatic": {}}
        else:
            config["replication"] = {
                "user_managed": {
                    "replicas": [
                        {"location": location} 
                        for location in self.spec.replication.user_managed_replicas
                    ]
                }
            }
            
        # TTL configuration
        if self.spec.ttl_seconds:
            config["ttl"] = f"{self.spec.ttl_seconds}s"

        return config
        
    # Fluent interface methods
    
    # Secret data methods
    
    def value(self, secret_value: str) -> Self:
        """Set secret string value (chainable)"""
        self.spec.secret_data = secret_value
        self.spec.secret_type = SecretDataType.STRING
        return self
        
    def random_value(self, length: int = 32, include_symbols: bool = True,
                    exclude_ambiguous: bool = True) -> Self:
        """Generate random secret value (chainable)"""
        # Character sets
        chars = string.ascii_letters + string.digits
        
        if include_symbols:
            # Safe symbols that work well in most contexts
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
            
        if exclude_ambiguous:
            # Remove ambiguous characters that can be confused
            ambiguous = "0O1lI"
            chars = ''.join(c for c in chars if c not in ambiguous)
            
        # Generate cryptographically secure random secret
        secret_value = ''.join(secrets.choice(chars) for _ in range(length))
        
        self.spec.secret_data = secret_value
        self.spec.secret_type = SecretDataType.STRING
        return self
        
    def random_password(self, length: int = 20, require_all_types: bool = True) -> Self:
        """Generate random password with character requirements (chainable)"""
        if require_all_types and length < 4:
            raise ValueError("Password length must be at least 4 when requiring all character types")
            
        # Character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        symbols = "!@#$%^&*"
        
        # Exclude ambiguous characters
        ambiguous = "0O1lI"
        lowercase = ''.join(c for c in lowercase if c not in ambiguous)
        uppercase = ''.join(c for c in uppercase if c not in ambiguous)
        digits = ''.join(c for c in digits if c not in ambiguous)
        
        password = []
        
        if require_all_types:
            # Ensure at least one of each type
            password.append(secrets.choice(lowercase))
            password.append(secrets.choice(uppercase))
            password.append(secrets.choice(digits))
            password.append(secrets.choice(symbols))
            
            # Fill the rest randomly
            all_chars = lowercase + uppercase + digits + symbols
            for _ in range(length - 4):
                password.append(secrets.choice(all_chars))
                
            # Shuffle to avoid predictable patterns
            secrets.SystemRandom().shuffle(password)
            secret_value = ''.join(password)
        else:
            # Simple random from all character types
            all_chars = lowercase + uppercase + digits + symbols
            secret_value = ''.join(secrets.choice(all_chars) for _ in range(length))
            
        self.spec.secret_data = secret_value
        self.spec.secret_type = SecretDataType.STRING
        return self
        
    def random_hex(self, bytes_length: int = 32) -> Self:
        """Generate random hex string (chainable)"""
        secret_value = secrets.token_hex(bytes_length)
        self.spec.secret_data = secret_value
        self.spec.secret_type = SecretDataType.STRING
        return self
        
    def random_alphanumeric(self, length: int = 32, uppercase_only: bool = False) -> Self:
        """Generate random alphanumeric string (chainable)"""
        if uppercase_only:
            chars = string.ascii_uppercase + string.digits
        else:
            chars = string.ascii_letters + string.digits
            
        # Exclude ambiguous characters
        ambiguous = "0O1lI"
        chars = ''.join(c for c in chars if c not in ambiguous)
        
        secret_value = ''.join(secrets.choice(chars) for _ in range(length))
        
        self.spec.secret_data = secret_value
        self.spec.secret_type = SecretDataType.STRING
        return self
        
    def random_api_key(self, prefix: str = "", length: int = 32) -> Self:
        """Generate random API key with optional prefix (chainable)"""
        # API keys are typically alphanumeric without ambiguous chars
        key_part = ''.join(secrets.choice(string.ascii_letters + string.digits) 
                          for _ in range(length))
        
        if prefix:
            secret_value = f"{prefix}_{key_part}"
        else:
            secret_value = key_part
            
        self.spec.secret_data = secret_value
        self.spec.secret_type = SecretDataType.STRING
        return self.label("type", "api-key")
        
    def random_token(self, length: int = 32) -> Self:
        """Generate URL-safe random token (chainable)"""
        # URL-safe base64 encoded random bytes
        secret_value = secrets.token_urlsafe(length)
        self.spec.secret_data = secret_value
        self.spec.secret_type = SecretDataType.STRING
        return self
        
    def json_value(self, json_data: Union[Dict, List]) -> Self:
        """Set secret JSON value (chainable)"""
        self.spec.secret_data = json.dumps(json_data, indent=2)
        self.spec.secret_type = SecretDataType.JSON
        return self
        
    def binary_value(self, binary_data: bytes) -> Self:
        """Set secret binary value (chainable)"""
        self.spec.secret_data = base64.b64encode(binary_data).decode('utf-8')
        self.spec.secret_type = SecretDataType.BINARY
        return self
        
    def from_file(self, file_path: str) -> Self:
        """Set secret from text file (chainable)"""
        self.spec.secret_file = file_path
        self.spec.secret_type = SecretDataType.STRING
        return self
        
    def json_from_file(self, file_path: str) -> Self:
        """Set secret from JSON file (chainable)"""
        self.spec.secret_file = file_path
        self.spec.secret_type = SecretDataType.JSON
        return self
        
    def binary_from_file(self, file_path: str) -> Self:
        """Set secret from binary file (chainable)"""
        self.spec.secret_file = file_path
        self.spec.secret_type = SecretDataType.BINARY
        return self
        
    # Replication methods
    
    def automatic_replication(self) -> Self:
        """Use automatic replication (chainable)"""
        self.spec.replication.automatic = True
        self.spec.replication.user_managed_replicas = []
        return self
        
    def regional_replication(self, regions: List[str]) -> Self:
        """Use regional replication (chainable)"""
        self.spec.replication.automatic = False
        self.spec.replication.user_managed_replicas = regions.copy()
        return self
        
    def single_region(self, region: str) -> Self:
        """Replicate to single region (chainable)"""
        return self.regional_replication([region])
        
    def multi_region(self, *regions: str) -> Self:
        """Replicate to multiple regions (chainable)"""
        return self.regional_replication(list(regions))
        
    # TTL methods
    
    def ttl_seconds(self, seconds: int) -> Self:
        """Set TTL in seconds (chainable)"""
        self.spec.ttl_seconds = seconds
        return self
        
    def ttl_minutes(self, minutes: int) -> Self:
        """Set TTL in minutes (chainable)"""
        self.spec.ttl_seconds = minutes * 60
        return self
        
    def ttl_hours(self, hours: int) -> Self:
        """Set TTL in hours (chainable)"""
        self.spec.ttl_seconds = hours * 3600
        return self
        
    def ttl_days(self, days: int) -> Self:
        """Set TTL in days (chainable)"""
        self.spec.ttl_seconds = days * 86400
        return self
        
    def no_ttl(self) -> Self:
        """Disable TTL (chainable)"""
        self.spec.ttl_seconds = None
        return self
        
    # Convenience methods for common secret types
    
    def database_url(self, url: str) -> Self:
        """Set database URL secret (chainable)"""
        return self.value(url).label("type", "database-url")
        
    def api_key(self, key: str) -> Self:
        """Set API key secret (chainable)"""
        return self.value(key).label("type", "api-key")
        
    def jwt_secret(self, secret: str) -> Self:
        """Set JWT secret (chainable)"""
        return self.value(secret).label("type", "jwt-secret")
        
    def oauth_credentials(self, client_id: str, client_secret: str, **kwargs) -> Self:
        """Set OAuth credentials (chainable)"""
        creds = {
            "client_id": client_id,
            "client_secret": client_secret,
            **kwargs
        }
        return self.json_value(creds).label("type", "oauth-credentials")
        
    def service_account_key(self, key_json: Dict[str, Any]) -> Self:
        """Set service account key (chainable)"""
        return self.json_value(key_json).label("type", "service-account-key")
        
    def tls_certificate(self, cert_pem: str, key_pem: str) -> Self:
        """Set TLS certificate and key (chainable)"""
        cert_data = {
            "certificate": cert_pem,
            "private_key": key_pem
        }
        return self.json_value(cert_data).label("type", "tls-certificate")
        
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
                .regional_replication(["us-central1", "us-east1"])
                .label("environment", "production"))
                
    def staging(self) -> Self:
        """Configure for staging environment (chainable)"""
        return (self
                .single_region("us-central1")
                .ttl_days(90)  # Auto-cleanup staging secrets
                .label("environment", "staging"))
                
    def development(self) -> Self:
        """Configure for development environment (chainable)"""
        return (self
                .automatic_replication()
                .ttl_days(30)  # Auto-cleanup dev secrets
                .label("environment", "development"))
                
    # Provider implementation methods
    
    def _provider_create(self) -> Dict[str, Any]:
        """Create the secret via provider"""
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
        """Update the secret via provider"""
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
        """Destroy the secret via provider"""
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
    
    def get_secret_name(self) -> str:
        """Get fully qualified secret name"""
        project_id = self._get_project_id()
        return f"projects/{project_id}/secrets/{self.metadata.name}"
        
    def get_latest_version(self) -> str:
        """Get reference to latest secret version"""
        return f"{self.get_secret_name()}/versions/latest"
        
    def get_version_reference(self, version: str = "latest") -> str:
        """Get reference to specific secret version"""
        return f"{self.get_secret_name()}/versions/{version}"
        
    def _get_project_id(self) -> str:
        """Get GCP project ID"""
        # Try to get from provider or environment
        if hasattr(self._provider, 'project_id'):
            return self._provider.project_id
        import os
        return os.environ.get('GOOGLE_CLOUD_PROJECT', 'my-project')