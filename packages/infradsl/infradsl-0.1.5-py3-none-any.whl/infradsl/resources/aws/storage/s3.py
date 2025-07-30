from typing import Optional, Dict, Any, Self, List, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

if TYPE_CHECKING:
    from infradsl.core.interfaces.provider import ProviderInterface

from ....core.nexus.base_resource import BaseResource, ResourceSpec


class StorageClass(Enum):
    """S3 storage classes"""
    STANDARD = "STANDARD"
    REDUCED_REDUNDANCY = "REDUCED_REDUNDANCY"
    STANDARD_IA = "STANDARD_IA"
    ONEZONE_IA = "ONEZONE_IA"
    INTELLIGENT_TIERING = "INTELLIGENT_TIERING"
    GLACIER = "GLACIER"
    DEEP_ARCHIVE = "DEEP_ARCHIVE"
    GLACIER_IR = "GLACIER_IR"  # Instant Retrieval


class AccessTier(Enum):
    """S3 access tiers for lifecycle"""
    FREQUENT = "frequent"
    INFREQUENT = "infrequent"
    ARCHIVE = "archive"
    DEEP_ARCHIVE = "deep_archive"


class VersioningStatus(Enum):
    """S3 versioning status"""
    ENABLED = "Enabled"
    SUSPENDED = "Suspended"
    DISABLED = "Disabled"


class MfaDelete(Enum):
    """S3 MFA delete status"""
    ENABLED = "Enabled"
    DISABLED = "Disabled"


class ServerSideEncryption(Enum):
    """S3 server-side encryption types"""
    AES256 = "AES256"
    AWS_KMS = "aws:kms"
    AWS_KMS_DSSE = "aws:kms:dsse"


@dataclass
class LifecycleRule:
    """S3 lifecycle rule configuration"""
    id: str
    status: str = "Enabled"
    prefix: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Expiration settings
    expiration_days: Optional[int] = None
    expired_object_delete_marker: bool = False
    
    # Noncurrent version expiration
    noncurrent_version_expiration_days: Optional[int] = None
    
    # Transitions
    transitions: List[Dict[str, Any]] = field(default_factory=list)
    noncurrent_version_transitions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Abort incomplete multipart uploads
    abort_incomplete_multipart_upload_days: Optional[int] = None


@dataclass
class CorsRule:
    """S3 CORS rule configuration"""
    allowed_headers: List[str] = field(default_factory=list)
    allowed_methods: List[str] = field(default_factory=list)
    allowed_origins: List[str] = field(default_factory=list)
    expose_headers: List[str] = field(default_factory=list)
    max_age_seconds: Optional[int] = None


@dataclass
class NotificationConfig:
    """S3 notification configuration"""
    lambda_configurations: List[Dict[str, Any]] = field(default_factory=list)
    topic_configurations: List[Dict[str, Any]] = field(default_factory=list)
    queue_configurations: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ReplicationRule:
    """S3 replication rule configuration"""
    id: str
    status: str = "Enabled"
    priority: int = 0
    prefix: str = ""
    destination_bucket: str = ""
    destination_region: str = ""
    destination_storage_class: Optional[StorageClass] = None
    replica_kms_key_id: Optional[str] = None
    delete_marker_replication: str = "Disabled"
    replica_metadata_status: str = "Enabled"


@dataclass
class LoggingConfig:
    """S3 access logging configuration"""
    target_bucket: str
    target_prefix: str = ""


@dataclass
class WebsiteConfig:
    """S3 static website configuration"""
    index_document: str = "index.html"
    error_document: str = "error.html"
    routing_rules: List[Dict[str, Any]] = field(default_factory=list)
    redirect_all_requests_to: Optional[str] = None


@dataclass
class PublicAccessBlockConfig:
    """S3 public access block configuration"""
    block_public_acls: bool = True
    block_public_policy: bool = True
    ignore_public_acls: bool = True
    restrict_public_buckets: bool = True


@dataclass
class AWSS3Spec(ResourceSpec):
    """Specification for AWS S3 Bucket"""
    
    # Basic configuration
    region: Optional[str] = None
    force_destroy: bool = False
    object_lock_enabled: bool = False
    existing_bucket: Optional[str] = None
    
    # Versioning
    versioning_enabled: bool = False
    mfa_delete: MfaDelete = MfaDelete.DISABLED
    
    # Encryption
    server_side_encryption_configuration: Dict[str, Any] = field(default_factory=dict)
    default_kms_key_id: Optional[str] = None
    bucket_key_enabled: bool = False
    
    # Access control
    acl: str = "private"
    public_access_block: PublicAccessBlockConfig = field(default_factory=PublicAccessBlockConfig)
    bucket_policy: Optional[Dict[str, Any]] = None
    
    # Lifecycle management
    lifecycle_rules: List[LifecycleRule] = field(default_factory=list)
    
    # CORS
    cors_rules: List[CorsRule] = field(default_factory=list)
    
    # Notifications
    notification_config: NotificationConfig = field(default_factory=NotificationConfig)
    
    # Replication
    replication_configuration: List[ReplicationRule] = field(default_factory=list)
    replication_role_arn: Optional[str] = None
    
    # Logging
    logging_config: Optional[LoggingConfig] = None
    
    # Website hosting
    website_config: Optional[WebsiteConfig] = None
    
    # Request payment
    request_payer: str = "BucketOwner"  # or "Requester"
    
    # Transfer acceleration
    acceleration_status: Optional[str] = None  # "Enabled" or "Suspended"
    
    # Intelligent tiering
    intelligent_tiering_configurations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Inventory configurations
    inventory_configurations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metrics configurations
    metrics_configurations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Analytics configurations
    analytics_configurations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class AWSS3(BaseResource):
    """
    AWS S3 Bucket with comprehensive features and Rails-like conventions.
    
    Examples:
        # Simple private bucket
        bucket = (AWSS3("my-app-data")
                  .region("us-east-1")
                  .private()
                  .versioning()
                  .encryption()
                  .production())
        
        # Website hosting bucket
        website_bucket = (AWSS3("my-website")
                         .region("us-east-1")
                         .website("index.html", "404.html")
                         .public_read()
                         .cors_for_website()
                         .production())
                         
        # Data archival bucket with lifecycle
        archive_bucket = (AWSS3("company-archives")
                         .region("us-west-2")
                         .private()
                         .versioning()
                         .encryption()
                         .lifecycle_transition("logs/", 30, "STANDARD_IA")
                         .lifecycle_transition("logs/", 90, "GLACIER")
                         .lifecycle_transition("logs/", 365, "DEEP_ARCHIVE")
                         .lifecycle_expiration("temp/", 7)
                         .intelligent_tiering("data/")
                         .production())
                         
        # Multi-region replication bucket
        primary_bucket = (AWSS3("app-data-primary")
                         .region("us-east-1")
                         .private()
                         .versioning()
                         .encryption()
                         .replication("app-data-backup", "us-west-2", "GLACIER")
                         .cross_region_replication()
                         .production())
                         
        # Static assets with CDN
        assets_bucket = (AWSS3("app-static-assets")
                        .region("us-east-1")
                        .public_read()
                        .website("index.html")
                        .cors_for_cdn()
                        .transfer_acceleration()
                        .cache_optimization()
                        .production())
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.spec: AWSS3Spec = self._create_spec()
        self.metadata.annotations["resource_type"] = "AWSS3"
        
    def _create_spec(self) -> AWSS3Spec:
        return AWSS3Spec()
        
    def _validate_spec(self) -> None:
        """Validate AWS S3 specification"""
        # Validate bucket name
        if not self._is_valid_bucket_name(self.metadata.name):
            raise ValueError(f"Invalid bucket name: {self.metadata.name}")
            
        # Validate replication
        if self.spec.replication_configuration and not self.spec.versioning_enabled:
            raise ValueError("Versioning must be enabled for replication")
            
        if self.spec.replication_configuration and not self.spec.replication_role_arn:
            raise ValueError("Replication role ARN is required for replication")
            
        # Validate website configuration
        if self.spec.website_config and self.spec.public_access_block.restrict_public_buckets:
            raise ValueError("Cannot enable website hosting with public access blocked")
            
    def _is_valid_bucket_name(self, name: str) -> bool:
        """Validate S3 bucket name according to AWS rules"""
        if len(name) < 3 or len(name) > 63:
            return False
        if not name.replace('-', '').replace('.', '').isalnum():
            return False
        if name.startswith('-') or name.endswith('-'):
            return False
        return True
            
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        config = {
            "bucket": self.metadata.name,
            "force_destroy": self.spec.force_destroy,
            "object_lock_enabled": self.spec.object_lock_enabled,
            "tags": {**self.spec.tags, **self.metadata.to_tags()},
        }
        
        # Use existing bucket if specified
        if self.spec.existing_bucket:
            config["existing_bucket"] = self.spec.existing_bucket
        
        # Optional configurations
        if self.spec.region:
            config["region"] = self.spec.region
            
        # Versioning
        if self.spec.versioning_enabled:
            config["versioning"] = {
                "enabled": True,
                "mfa_delete": self.spec.mfa_delete.value
            }
            
        # Encryption
        if self.spec.server_side_encryption_configuration:
            config["server_side_encryption_configuration"] = self.spec.server_side_encryption_configuration
            
        # ACL and public access
        if self.spec.acl != "private":
            config["acl"] = self.spec.acl
            
        config["public_access_block"] = {
            "block_public_acls": self.spec.public_access_block.block_public_acls,
            "block_public_policy": self.spec.public_access_block.block_public_policy,
            "ignore_public_acls": self.spec.public_access_block.ignore_public_acls,
            "restrict_public_buckets": self.spec.public_access_block.restrict_public_buckets
        }
        
        # Bucket policy
        if self.spec.bucket_policy:
            config["bucket_policy"] = self.spec.bucket_policy
        
        # Lifecycle
        if self.spec.lifecycle_rules:
            config["lifecycle_configuration"] = {
                "rules": [self._lifecycle_rule_to_config(rule) for rule in self.spec.lifecycle_rules]
            }
            
        # CORS
        if self.spec.cors_rules:
            config["cors_configuration"] = {
                "cors_rules": [self._cors_rule_to_config(rule) for rule in self.spec.cors_rules]
            }
            
        # Notifications
        if (self.spec.notification_config.lambda_configurations or 
            self.spec.notification_config.topic_configurations or 
            self.spec.notification_config.queue_configurations):
            config["notification_configuration"] = {
                "lambda_configurations": self.spec.notification_config.lambda_configurations,
                "topic_configurations": self.spec.notification_config.topic_configurations,
                "queue_configurations": self.spec.notification_config.queue_configurations
            }
            
        # Replication
        if self.spec.replication_configuration:
            config["replication_configuration"] = {
                "role": self.spec.replication_role_arn,
                "rules": [self._replication_rule_to_config(rule) for rule in self.spec.replication_configuration]
            }
            
        # Logging
        if self.spec.logging_config:
            config["logging"] = {
                "target_bucket": self.spec.logging_config.target_bucket,
                "target_prefix": self.spec.logging_config.target_prefix
            }
            
        # Website
        if self.spec.website_config:
            config["website"] = self._website_config_to_config()
            
        # Request payment
        if self.spec.request_payer != "BucketOwner":
            config["request_payer"] = self.spec.request_payer
            
        # Transfer acceleration
        if self.spec.acceleration_status:
            config["acceleration_status"] = self.spec.acceleration_status
            
        # Advanced configurations
        if self.spec.intelligent_tiering_configurations:
            config["intelligent_tiering_configurations"] = self.spec.intelligent_tiering_configurations
            
        if self.spec.inventory_configurations:
            config["inventory_configurations"] = self.spec.inventory_configurations
            
        if self.spec.metrics_configurations:
            config["metrics_configurations"] = self.spec.metrics_configurations
            
        if self.spec.analytics_configurations:
            config["analytics_configurations"] = self.spec.analytics_configurations

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
        
    def _lifecycle_rule_to_config(self, rule: LifecycleRule) -> Dict[str, Any]:
        """Convert lifecycle rule to configuration"""
        config = {
            "id": rule.id,
            "status": rule.status
        }
        
        # Filter
        filter_config = {}
        if rule.prefix:
            filter_config["prefix"] = rule.prefix
        if rule.tags:
            filter_config["tags"] = rule.tags
        if filter_config:
            config["filter"] = filter_config
            
        # Expiration
        if rule.expiration_days:
            config["expiration"] = {"days": rule.expiration_days}
        if rule.expired_object_delete_marker:
            config["expiration"]["expired_object_delete_marker"] = True
            
        # Noncurrent version expiration
        if rule.noncurrent_version_expiration_days:
            config["noncurrent_version_expiration"] = {
                "noncurrent_days": rule.noncurrent_version_expiration_days
            }
            
        # Transitions
        if rule.transitions:
            config["transitions"] = rule.transitions
        if rule.noncurrent_version_transitions:
            config["noncurrent_version_transitions"] = rule.noncurrent_version_transitions
            
        # Abort incomplete multipart uploads
        if rule.abort_incomplete_multipart_upload_days:
            config["abort_incomplete_multipart_upload"] = {
                "days_after_initiation": rule.abort_incomplete_multipart_upload_days
            }
            
        return config
        
    def _cors_rule_to_config(self, rule: CorsRule) -> Dict[str, Any]:
        """Convert CORS rule to configuration"""
        config = {}
        if rule.allowed_headers:
            config["allowed_headers"] = rule.allowed_headers
        if rule.allowed_methods:
            config["allowed_methods"] = rule.allowed_methods
        if rule.allowed_origins:
            config["allowed_origins"] = rule.allowed_origins
        if rule.expose_headers:
            config["expose_headers"] = rule.expose_headers
        if rule.max_age_seconds:
            config["max_age_seconds"] = rule.max_age_seconds
        return config
        
    def _replication_rule_to_config(self, rule: ReplicationRule) -> Dict[str, Any]:
        """Convert replication rule to configuration"""
        config = {
            "id": rule.id,
            "status": rule.status,
            "priority": rule.priority,
            "destination": {
                "bucket": f"arn:aws:s3:::{rule.destination_bucket}",
                "replica_kms_key_id": rule.replica_kms_key_id,
                "storage_class": rule.destination_storage_class.value if rule.destination_storage_class else None
            },
            "delete_marker_replication": {"status": rule.delete_marker_replication}
        }
        
        if rule.prefix:
            config["filter"] = {"prefix": rule.prefix}
            
        return config
        
    def _website_config_to_config(self) -> Dict[str, Any]:
        """Convert website configuration"""
        config = {}
        if self.spec.website_config:
            if self.spec.website_config.redirect_all_requests_to:
                config["redirect_all_requests_to"] = {
                    "host_name": self.spec.website_config.redirect_all_requests_to
                }
            else:
                config["index_document"] = {"suffix": self.spec.website_config.index_document}
                if self.spec.website_config.error_document:
                    config["error_document"] = {"key": self.spec.website_config.error_document}
                if self.spec.website_config.routing_rules:
                    config["routing_rules"] = self.spec.website_config.routing_rules
        return config

    def _to_aws_config(self) -> Dict[str, Any]:
        """Convert to AWS S3 configuration"""
        return {
            "resource_type": "S3"
        }
        
    # Fluent interface methods
    
    # Basic configuration
    
    def region(self, region: str) -> Self:
        """Set AWS region (chainable)"""
        self.spec.region = region
        return self
        
    def existing_bucket(self, bucket_name: str) -> Self:
        """Use existing bucket instead of creating new one (chainable)"""
        self.spec.existing_bucket = bucket_name
        return self
        
    def force_destroy(self, enabled: bool = True) -> Self:
        """Enable force destroy (chainable)"""
        self.spec.force_destroy = enabled
        return self
        
    def object_lock(self, enabled: bool = True) -> Self:
        """Enable object lock (chainable)"""
        self.spec.object_lock_enabled = enabled
        if enabled:
            self.spec.versioning_enabled = True  # Object lock requires versioning
        return self
        
    # Versioning
    
    def versioning(self, enabled: bool = True) -> Self:
        """Enable versioning (chainable)"""
        self.spec.versioning_enabled = enabled
        return self
        
    def mfa_delete(self, enabled: bool = True) -> Self:
        """Enable MFA delete (chainable)"""
        self.spec.mfa_delete = MfaDelete.ENABLED if enabled else MfaDelete.DISABLED
        return self
        
    # Encryption
    
    def encryption(self, kms_key: str = None, bucket_key: bool = True) -> Self:
        """Enable server-side encryption (chainable)"""
        if kms_key:
            self.spec.server_side_encryption_configuration = {
                "rule": {
                    "apply_server_side_encryption_by_default": {
                        "sse_algorithm": ServerSideEncryption.AWS_KMS.value,
                        "kms_master_key_id": kms_key
                    },
                    "bucket_key_enabled": bucket_key
                }
            }
            self.spec.default_kms_key_id = kms_key
        else:
            self.spec.server_side_encryption_configuration = {
                "rule": {
                    "apply_server_side_encryption_by_default": {
                        "sse_algorithm": ServerSideEncryption.AES256.value
                    }
                }
            }
        self.spec.bucket_key_enabled = bucket_key
        return self
        
    def kms_encryption(self, kms_key: str, bucket_key: bool = True) -> Self:
        """Enable KMS encryption (chainable)"""
        return self.encryption(kms_key, bucket_key)
        
    # Access control
    
    def private(self) -> Self:
        """Make bucket private (chainable)"""
        self.spec.acl = "private"
        self.spec.public_access_block = PublicAccessBlockConfig(
            block_public_acls=True,
            block_public_policy=True,
            ignore_public_acls=True,
            restrict_public_buckets=True
        )
        return self
        
    def public_read(self) -> Self:
        """Allow public read access (chainable)"""
        self.spec.acl = "public-read"
        self.spec.public_access_block = PublicAccessBlockConfig(
            block_public_acls=False,
            block_public_policy=False,
            ignore_public_acls=False,
            restrict_public_buckets=False
        )
        return self
        
    def public_read_write(self) -> Self:
        """Allow public read-write access (chainable)"""
        self.spec.acl = "public-read-write"
        self.spec.public_access_block = PublicAccessBlockConfig(
            block_public_acls=False,
            block_public_policy=False,
            ignore_public_acls=False,
            restrict_public_buckets=False
        )
        return self
        
    def acl(self, acl: str) -> Self:
        """Set ACL (chainable)"""
        self.spec.acl = acl
        return self
        
    def block_public_access(self, block_acls: bool = True, block_policy: bool = True,
                           ignore_acls: bool = True, restrict_buckets: bool = True) -> Self:
        """Configure public access block (chainable)"""
        self.spec.public_access_block = PublicAccessBlockConfig(
            block_public_acls=block_acls,
            block_public_policy=block_policy,
            ignore_public_acls=ignore_acls,
            restrict_public_buckets=restrict_buckets
        )
        return self
        
    def allow_cloudfront(self, cloudfront_distribution) -> Self:
        """Allow CloudFront distribution to access bucket (chainable)"""
        import json
        
        # Get the CloudFront distribution's origin access identity or domain name
        # This method accepts either a CloudFront resource or a string
        if hasattr(cloudfront_distribution, 'origin_access_identity'):
            principal = f"arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity {cloudfront_distribution.origin_access_identity}"
        elif hasattr(cloudfront_distribution, 'domain_name'):
            # For newer CloudFront with Origin Access Control, we'll use a more general policy
            principal = "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity *"
        else:
            # Assume it's a string with the distribution ID or OAI
            principal = f"arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity {cloudfront_distribution}"
        
        # Create CloudFront access policy
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowCloudFrontAccess",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": principal
                    },
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{self.spec.existing_bucket or self.metadata.name}/*"
                }
            ]
        }
        
        self.spec.bucket_policy = policy
        
        # Allow CloudFront access by adjusting public access block
        self.spec.public_access_block.block_public_policy = False
        self.spec.public_access_block.restrict_public_buckets = False
        
        return self
        
    # Lifecycle management
    
    def lifecycle_expiration(self, prefix: str, days: int, rule_id: str = None) -> Self:
        """Add lifecycle expiration rule (chainable)"""
        rule = LifecycleRule(
            id=rule_id or f"expiration-{prefix.replace('/', '-')}-{days}d",
            prefix=prefix,
            expiration_days=days
        )
        self.spec.lifecycle_rules.append(rule)
        return self
        
    def lifecycle_transition(self, prefix: str, days: int, storage_class: str, 
                           rule_id: str = None) -> Self:
        """Add lifecycle transition rule (chainable)"""
        existing_rule = None
        rule_id = rule_id or f"transition-{prefix.replace('/', '-')}"
        
        # Find existing rule for the same prefix
        for rule in self.spec.lifecycle_rules:
            if rule.prefix == prefix and rule.id == rule_id:
                existing_rule = rule
                break
                
        if not existing_rule:
            existing_rule = LifecycleRule(id=rule_id, prefix=prefix)
            self.spec.lifecycle_rules.append(existing_rule)
            
        existing_rule.transitions.append({
            "days": days,
            "storage_class": storage_class
        })
        return self
        
    def lifecycle_noncurrent_expiration(self, days: int, rule_id: str = "noncurrent-expiration") -> Self:
        """Add noncurrent version expiration rule (chainable)"""
        rule = LifecycleRule(
            id=rule_id,
            noncurrent_version_expiration_days=days
        )
        self.spec.lifecycle_rules.append(rule)
        return self
        
    def lifecycle_abort_multipart(self, days: int = 7, rule_id: str = "abort-multipart") -> Self:
        """Add rule to abort incomplete multipart uploads (chainable)"""
        rule = LifecycleRule(
            id=rule_id,
            abort_incomplete_multipart_upload_days=days
        )
        self.spec.lifecycle_rules.append(rule)
        return self
        
    def intelligent_tiering(self, prefix: str = "", config_id: str = None) -> Self:
        """Enable intelligent tiering (chainable)"""
        config = {
            "id": config_id or f"intelligent-tiering-{prefix or 'all'}",
            "status": "Enabled",
            "filter": {"prefix": prefix} if prefix else {},
            "tierings": [{
                "access_tier": "ARCHIVE_ACCESS",
                "days": 90
            }, {
                "access_tier": "DEEP_ARCHIVE_ACCESS", 
                "days": 180
            }]
        }
        self.spec.intelligent_tiering_configurations.append(config)
        return self
        
    # CORS configuration
    
    def cors(self, allowed_origins: List[str], allowed_methods: List[str] = None,
             allowed_headers: List[str] = None, expose_headers: List[str] = None,
             max_age: int = 3000) -> Self:
        """Add CORS rule (chainable)"""
        rule = CorsRule(
            allowed_origins=allowed_origins,
            allowed_methods=allowed_methods or ["GET", "POST", "PUT", "DELETE"],
            allowed_headers=allowed_headers or ["*"],
            expose_headers=expose_headers or [],
            max_age_seconds=max_age
        )
        self.spec.cors_rules.append(rule)
        return self
        
    def cors_for_website(self) -> Self:
        """Add CORS rules for website hosting (chainable)"""
        return self.cors(
            allowed_origins=["*"],
            allowed_methods=["GET", "HEAD"],
            allowed_headers=["*"],
            max_age=3000
        )
        
    def cors_for_cdn(self) -> Self:
        """Add CORS rules optimized for CDN (chainable)"""
        return self.cors(
            allowed_origins=["*"],
            allowed_methods=["GET", "HEAD"],
            allowed_headers=["Origin", "Accept", "Content-Type"],
            expose_headers=["ETag"],
            max_age=86400
        )
        
    # Website hosting
    
    def website(self, index_document: str = "index.html", error_document: str = "error.html") -> Self:
        """Enable static website hosting (chainable)"""
        self.spec.website_config = WebsiteConfig(
            index_document=index_document,
            error_document=error_document
        )
        # Website hosting requires public read access
        self.public_read()
        return self
        
    def redirect_website(self, hostname: str) -> Self:
        """Redirect all requests to another hostname (chainable)"""
        self.spec.website_config = WebsiteConfig(
            redirect_all_requests_to=hostname
        )
        return self
        
    # Replication
    
    def replication(self, destination_bucket: str, destination_region: str = None,
                   storage_class: str = None, role_arn: str = None) -> Self:
        """Add cross-region replication (chainable)"""
        if not self.spec.versioning_enabled:
            self.versioning()
            
        rule = ReplicationRule(
            id=f"replicate-to-{destination_bucket}",
            destination_bucket=destination_bucket,
            destination_region=destination_region or self.spec.region or "us-west-2",
            destination_storage_class=StorageClass(storage_class) if storage_class else None
        )
        
        self.spec.replication_configuration.append(rule)
        
        # Set replication role if provided
        if role_arn:
            self.spec.replication_role_arn = role_arn
        elif not self.spec.replication_role_arn:
            # Generate a default role name
            self.spec.replication_role_arn = f"arn:aws:iam::ACCOUNT:role/{self.name}-replication-role"
            
        return self
        
    def cross_region_replication(self, enabled: bool = True) -> Self:
        """Enable cross-region replication with default settings (chainable)"""
        if enabled and not self.spec.replication_configuration:
            backup_name = f"{self.name}-backup"
            backup_region = "us-west-2" if self.spec.region != "us-west-2" else "us-east-1"
            self.replication(backup_name, backup_region, "STANDARD_IA")
        return self
        
    # Transfer and performance
    
    def transfer_acceleration(self, enabled: bool = True) -> Self:
        """Enable transfer acceleration (chainable)"""
        self.spec.acceleration_status = "Enabled" if enabled else "Suspended"
        return self
        
    def requester_pays(self, enabled: bool = True) -> Self:
        """Enable requester pays (chainable)"""
        self.spec.request_payer = "Requester" if enabled else "BucketOwner"
        return self
        
    # Logging and monitoring
    
    def access_logging(self, target_bucket: str, prefix: str = "") -> Self:
        """Enable access logging (chainable)"""
        self.spec.logging_config = LoggingConfig(
            target_bucket=target_bucket,
            target_prefix=prefix or f"{self.name}-access-logs/"
        )
        return self
        
    def cloudtrail_logging(self, trail_name: str = None) -> Self:
        """Configure for CloudTrail logging (chainable)"""
        # This would set up the bucket policy for CloudTrail
        return self.tag("CloudTrail", trail_name or f"{self.name}-trail")
        
    # Notifications
    
    def lambda_notification(self, lambda_arn: str, events: List[str] = None, 
                           prefix: str = "", suffix: str = "") -> Self:
        """Add Lambda notification (chainable)"""
        config = {
            "lambda_function_arn": lambda_arn,
            "events": events or ["s3:ObjectCreated:*"],
            "filter": {}
        }
        
        if prefix or suffix:
            config["filter"]["key"] = {}
            if prefix:
                config["filter"]["key"]["filter_prefix"] = prefix
            if suffix:
                config["filter"]["key"]["filter_suffix"] = suffix
                
        self.spec.notification_config.lambda_configurations.append(config)
        return self
        
    def sns_notification(self, topic_arn: str, events: List[str] = None,
                        prefix: str = "", suffix: str = "") -> Self:
        """Add SNS notification (chainable)"""
        config = {
            "topic_arn": topic_arn,
            "events": events or ["s3:ObjectCreated:*"],
            "filter": {}
        }
        
        if prefix or suffix:
            config["filter"]["key"] = {}
            if prefix:
                config["filter"]["key"]["filter_prefix"] = prefix
            if suffix:
                config["filter"]["key"]["filter_suffix"] = suffix
                
        self.spec.notification_config.topic_configurations.append(config)
        return self
        
    def sqs_notification(self, queue_arn: str, events: List[str] = None,
                        prefix: str = "", suffix: str = "") -> Self:
        """Add SQS notification (chainable)"""
        config = {
            "queue_arn": queue_arn,
            "events": events or ["s3:ObjectCreated:*"],
            "filter": {}
        }
        
        if prefix or suffix:
            config["filter"]["key"] = {}
            if prefix:
                config["filter"]["key"]["filter_prefix"] = prefix
            if suffix:
                config["filter"]["key"]["filter_suffix"] = suffix
                
        self.spec.notification_config.queue_configurations.append(config)
        return self
        
    # Common patterns
    
    def data_lake_bucket(self) -> Self:
        """Configure for data lake use case (chainable)"""
        return (self
                .private()
                .versioning()
                .encryption()
                .intelligent_tiering("raw-data/")
                .lifecycle_transition("processed/", 30, "STANDARD_IA")
                .lifecycle_transition("processed/", 90, "GLACIER")
                .lifecycle_transition("archive/", 1, "GLACIER")
                .lifecycle_abort_multipart(7))
                
    def backup_bucket(self) -> Self:
        """Configure for backup storage (chainable)"""
        return (self
                .private()
                .versioning()
                .encryption()
                .lifecycle_transition("", 30, "STANDARD_IA")
                .lifecycle_transition("", 90, "GLACIER")
                .lifecycle_noncurrent_expiration(365)
                .cross_region_replication())
                
    def content_distribution_bucket(self) -> Self:
        """Configure for content distribution (chainable)"""
        return (self
                .public_read()
                .transfer_acceleration()
                .cors_for_cdn()
                .cache_optimization())
                
    def log_storage_bucket(self) -> Self:
        """Configure for log storage (chainable)"""
        return (self
                .private()
                .lifecycle_transition("", 30, "STANDARD_IA")
                .lifecycle_transition("", 90, "GLACIER")
                .lifecycle_transition("", 365, "DEEP_ARCHIVE")
                .lifecycle_expiration("temp-logs/", 30)
                .intelligent_tiering())
                
    def cache_optimization(self) -> Self:
        """Optimize for caching and CDN (chainable)"""
        return (self
                .tag("CacheOptimized", "true")
                .tag("CDNFriendly", "true"))
                
    # Analytics and inventory
    
    def inventory_report(self, destination_bucket: str, frequency: str = "Daily",
                        prefix: str = "inventory-reports/") -> Self:
        """Enable inventory reports (chainable)"""
        config = {
            "id": f"{self.name}-inventory",
            "enabled": True,
            "destination": {
                "bucket": f"arn:aws:s3:::{destination_bucket}",
                "prefix": prefix,
                "format": "CSV"
            },
            "frequency": frequency,
            "included_object_versions": "Current",
            "optional_fields": ["Size", "LastModifiedDate", "ETag", "StorageClass"]
        }
        self.spec.inventory_configurations.append(config)
        return self
        
    def storage_analytics(self, prefix: str = "", config_id: str = None) -> Self:
        """Enable storage class analysis (chainable)"""
        config = {
            "id": config_id or f"analytics-{prefix or 'all'}",
            "filter": {"prefix": prefix} if prefix else {}
        }
        self.spec.analytics_configurations.append(config)
        return self
        
    def request_metrics(self, prefix: str = "", config_id: str = None) -> Self:
        """Enable request metrics (chainable)"""
        config = {
            "id": config_id or f"metrics-{prefix or 'all'}",
            "filter": {"prefix": prefix} if prefix else {}
        }
        self.spec.metrics_configurations.append(config)
        return self
        
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
                .versioning()
                .encryption()
                .lifecycle_abort_multipart(1)
                .tag("Environment", "production")
                .tag("Backup", "required")
                .tag("Monitoring", "enabled"))
                
    def staging(self) -> Self:
        """Configure for staging environment (chainable)"""
        return (self
                .versioning()
                .encryption()
                .lifecycle_abort_multipart(7)
                .tag("Environment", "staging")
                .tag("AutoCleanup", "enabled"))
                
    def development(self) -> Self:
        """Configure for development environment (chainable)"""
        return (self
                .force_destroy()
                .lifecycle_expiration("temp/", 7)
                .lifecycle_abort_multipart(1)
                .tag("Environment", "development")
                .tag("AutoCleanup", "enabled"))
                
    # Provider implementation methods
    
    def _provider_create(self) -> Dict[str, Any]:
        """Create the S3 bucket via provider"""
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
        """Update the S3 bucket via provider"""
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
        """Destroy the S3 bucket via provider"""
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
    
    def get_bucket_name(self) -> str:
        """Get bucket name"""
        return self.metadata.name
        
    def is_versioning_enabled(self) -> bool:
        """Check if versioning is enabled"""
        return self.spec.versioning_enabled
        
    def is_encrypted(self) -> bool:
        """Check if encryption is enabled"""
        return bool(self.spec.server_side_encryption_configuration)
        
    def is_website_enabled(self) -> bool:
        """Check if website hosting is enabled"""
        return self.spec.website_config is not None
        
    def is_public(self) -> bool:
        """Check if bucket allows public access"""
        return not self.spec.public_access_block.restrict_public_buckets
        
    def get_lifecycle_rules_count(self) -> int:
        """Get number of lifecycle rules"""
        return len(self.spec.lifecycle_rules)
        
    def has_replication(self) -> bool:
        """Check if replication is configured"""
        return len(self.spec.replication_configuration) > 0