from typing import Optional, Dict, Any, Self, List
from dataclasses import dataclass, field
from enum import Enum

from ...core.nexus.base_resource import BaseResource, ResourceSpec


class StorageClass(Enum):
    """GCS storage classes"""
    STANDARD = "STANDARD"
    NEARLINE = "NEARLINE" 
    COLDLINE = "COLDLINE"
    ARCHIVE = "ARCHIVE"


class AccessControl(Enum):
    """Access control types"""
    UNIFORM = "uniform"
    FINE_GRAINED = "finegrained"


@dataclass  
class LifecycleRule:
    """Storage lifecycle rule"""
    action: str
    condition: Dict[str, Any]
    
    
@dataclass
class CloudStorageSpec(ResourceSpec):
    """Specification for a GCS bucket resource"""
    
    # Core configuration
    location: str = "US"
    storage_class: StorageClass = StorageClass.STANDARD
    
    # Access control
    access_control: AccessControl = AccessControl.UNIFORM
    public_read: bool = False
    
    # Features
    versioning: bool = False
    retention_days: Optional[int] = None
    
    # Lifecycle management
    lifecycle_rules: List[LifecycleRule] = field(default_factory=list)
    
    # Website hosting
    website_config: Optional[Dict[str, str]] = None
    
    # CORS configuration
    cors_config: Optional[List[Dict[str, Any]]] = None
    
    # Logging
    logging_bucket: Optional[str] = None
    logging_prefix: str = ""
    
    # Encryption
    kms_key: Optional[str] = None
    
    # Labels (GCP metadata)
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class CloudStorage(BaseResource):
    """
    GCP Cloud Storage bucket with Rails-like conventions.
    
    Examples:
        # Simple storage bucket
        bucket = (CloudStorage("my-data")
                 .location("us-central1")
                 .standard())
        
        # Website bucket with CDN
        site_bucket = (CloudStorage("my-site")
                      .website("index.html")
                      .public_read()
                      .cors())
        
        # Production backup bucket  
        backup_bucket = (CloudStorage("prod-backups")
                        .location("us-east1")
                        .coldline()
                        .versioning()
                        .retention(90)
                        .lifecycle_archive(365))
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.spec: CloudStorageSpec = self._create_spec()
        # Store resource type in annotations for cache fingerprinting
        self.metadata.annotations["resource_type"] = "CloudStorage"
        
        # Set smart defaults based on name patterns
        if any(keyword in name.lower() for keyword in ["backup", "archive", "log"]):
            self.spec.storage_class = StorageClass.COLDLINE
        elif "static" in name.lower() or "website" in name.lower():
            self.spec.public_read = True
            
    def _create_spec(self) -> CloudStorageSpec:
        return CloudStorageSpec()
        
    def _validate_spec(self) -> None:
        """Validate bucket specification"""
        if self.spec.website_config and not self.spec.public_read:
            raise ValueError("Website hosting requires public read access")
            
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        config = {
            "name": self.metadata.name,
            "location": self.spec.location,
            "storage_class": self.spec.storage_class.value,
            "uniform_bucket_level_access": self.spec.access_control == AccessControl.UNIFORM,
            "versioning": {"enabled": self.spec.versioning},
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
        """Convert to GCP Cloud Storage configuration"""
        config = {
            "resource_type": "storage_bucket"
        }
        
        # Public access
        if self.spec.public_read:
            config["default_object_acl"] = [
                {
                    "entity": "allUsers",
                    "role": "READER"
                }
            ]
            
        # Retention policy
        if self.spec.retention_days:
            config["retention_policy"] = {
                "retention_period": self.spec.retention_days * 24 * 60 * 60  # Convert days to seconds
            }
            
        # Lifecycle configuration
        if self.spec.lifecycle_rules:
            lifecycle_config = {"rule": []}
            for rule in self.spec.lifecycle_rules:
                lifecycle_config["rule"].append({
                    "action": {"type": rule.action},
                    "condition": rule.condition
                })
            config["lifecycle_rule"] = lifecycle_config
            
        # Website configuration
        if self.spec.website_config:
            config["website"] = self.spec.website_config
            
        # CORS configuration
        if self.spec.cors_config:
            config["cors"] = self.spec.cors_config
            
        # Logging
        if self.spec.logging_bucket:
            config["logging"] = {
                "log_bucket": self.spec.logging_bucket,
                "log_object_prefix": self.spec.logging_prefix
            }
            
        # Encryption
        if self.spec.kms_key:
            config["encryption"] = {
                "default_kms_key_name": self.spec.kms_key
            }

        return config
        
    # Fluent interface methods
    
    def location(self, location_name: str) -> Self:
        """Set bucket location (chainable)"""
        self.spec.location = location_name
        return self
        
    def region(self, region_name: str) -> Self:
        """Set bucket region (chainable)"""
        self.spec.location = region_name
        return self
        
    # Storage class methods
    
    def standard(self) -> Self:
        """Use standard storage class (chainable)"""
        self.spec.storage_class = StorageClass.STANDARD
        return self
        
    def nearline(self) -> Self:
        """Use nearline storage class (chainable)"""
        self.spec.storage_class = StorageClass.NEARLINE
        return self
        
    def coldline(self) -> Self:
        """Use coldline storage class (chainable)"""
        self.spec.storage_class = StorageClass.COLDLINE
        return self
        
    def archive(self) -> Self:
        """Use archive storage class (chainable)"""
        self.spec.storage_class = StorageClass.ARCHIVE
        return self
        
    # Access control methods
    
    def uniform_access(self) -> Self:
        """Use uniform bucket-level access (chainable)"""
        self.spec.access_control = AccessControl.UNIFORM
        return self
        
    def fine_grained_access(self) -> Self:
        """Use fine-grained access control (chainable)"""
        self.spec.access_control = AccessControl.FINE_GRAINED
        return self
        
    def public_read(self, enable: bool = True) -> Self:
        """Enable public read access (chainable)"""
        self.spec.public_read = enable
        return self
        
    # Feature methods
    
    def versioning(self, enable: bool = True) -> Self:
        """Enable object versioning (chainable)"""
        self.spec.versioning = enable
        return self
        
    def retention(self, days: int) -> Self:
        """Set retention policy in days (chainable)"""
        self.spec.retention_days = days
        return self
        
    def kms_encryption(self, kms_key: str) -> Self:
        """Enable KMS encryption with key (chainable)"""
        self.spec.kms_key = kms_key
        return self
        
    # Lifecycle management
    
    def lifecycle_delete(self, days: int, prefix: str = "") -> Self:
        """Delete objects after specified days (chainable)"""
        rule = LifecycleRule(
            action="Delete",
            condition={"age": days}
        )
        if prefix:
            rule.condition["matchesPrefix"] = [prefix]
        self.spec.lifecycle_rules.append(rule)
        return self
        
    def lifecycle_archive(self, days: int, prefix: str = "") -> Self:
        """Move to archive storage after specified days (chainable)"""
        rule = LifecycleRule(
            action="SetStorageClass",
            condition={"age": days, "storageClass": "ARCHIVE"}
        )
        if prefix:
            rule.condition["matchesPrefix"] = [prefix]
        self.spec.lifecycle_rules.append(rule)
        return self
        
    def lifecycle_nearline(self, days: int, prefix: str = "") -> Self:
        """Move to nearline storage after specified days (chainable)"""
        rule = LifecycleRule(
            action="SetStorageClass", 
            condition={"age": days, "storageClass": "NEARLINE"}
        )
        if prefix:
            rule.condition["matchesPrefix"] = [prefix]
        self.spec.lifecycle_rules.append(rule)
        return self
        
    def lifecycle_coldline(self, days: int, prefix: str = "") -> Self:
        """Move to coldline storage after specified days (chainable)"""
        rule = LifecycleRule(
            action="SetStorageClass",
            condition={"age": days, "storageClass": "COLDLINE"}
        )
        if prefix:
            rule.condition["matchesPrefix"] = [prefix]
        self.spec.lifecycle_rules.append(rule)
        return self
        
    # Website hosting
    
    def website(self, index_document: str = "index.html", error_document: str = "404.html") -> Self:
        """Configure bucket for static website hosting (chainable)"""
        self.spec.website_config = {
            "main_page_suffix": index_document,
            "not_found_page": error_document
        }
        # Website hosting requires public read
        self.spec.public_read = True
        return self
        
    # CORS configuration
    
    def cors(self, origins: List[str] = None, methods: List[str] = None, headers: List[str] = None, max_age: int = 3600) -> Self:
        """Configure CORS for the bucket (chainable)"""
        if origins is None:
            origins = ["*"]
        if methods is None:
            methods = ["GET", "HEAD", "PUT", "POST", "DELETE"]
        if headers is None:
            headers = ["*"]
            
        cors_rule = {
            "origin": origins,
            "method": methods,
            "responseHeader": headers,
            "maxAgeSeconds": max_age
        }
        
        if self.spec.cors_config is None:
            self.spec.cors_config = []
        self.spec.cors_config.append(cors_rule)
        return self
        
    # Logging
    
    def logging(self, log_bucket: str, prefix: str = "") -> Self:
        """Enable access logging (chainable)"""
        self.spec.logging_bucket = log_bucket
        self.spec.logging_prefix = prefix
        return self
        
    # Labels and metadata
    
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
                .standard()
                .versioning()
                .uniform_access()
                .label("environment", "production"))
                
    def staging(self) -> Self:
        """Configure for staging environment (chainable)"""
        return (self
                .standard()
                .uniform_access()
                .label("environment", "staging"))
                
    def development(self) -> Self:
        """Configure for development environment (chainable)"""
        return (self
                .standard()
                .uniform_access()
                .label("environment", "development"))
                
    # Provider implementation methods
    
    def _provider_create(self) -> Dict[str, Any]:
        """Create the bucket via provider"""
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
        """Update the bucket via provider"""
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
        """Destroy the bucket via provider"""
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
    
    def get_url(self) -> Optional[str]:
        """Get bucket URL"""
        return self.status.provider_data.get("self_link")
        
    def get_website_url(self) -> Optional[str]:
        """Get website URL (if website hosting is enabled)"""
        if self.spec.website_config:
            return f"https://storage.googleapis.com/{self.metadata.name}/index.html"
        return None