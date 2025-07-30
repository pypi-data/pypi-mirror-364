"""
AWS S3 Bucket
"""

from typing import Any, Dict, List, Optional, Union
from ...core.nexus.base_resource import BaseResource, ResourceSpec


class S3(BaseResource):
    """
    AWS S3 Bucket with fluent API

    Usage:
        bucket = AWS.S3("my-bucket")
                .use_existing_bucket("existing-bucket")
                .allow_cloudfront(cdn)
                .website()
                .create()
    """

    def __init__(self, name: str):
        super().__init__(name)
        self._config = {
            "name": name,
            "existing_bucket": None,
            "cloudfront_access": [],
            "website_config": None,
            "cors_config": None,
            "policy": None,
            "versioning": False,
            "public_access_block": True,
            "encryption": None,
            "lifecycle_rules": [],
            "logging": None,
            "notification_config": None,
        }
        self._bucket_name = None
        self._website_endpoint = None

    def _create_spec(self) -> ResourceSpec:
        """Create the resource-specific specification"""
        return ResourceSpec()

    def _validate_spec(self) -> None:
        """Validate the resource specification"""
        pass

    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        return self._config

    def _provider_create(self) -> Dict[str, Any]:
        """Provider-specific create implementation"""
        if not self._provider:
            raise ValueError(
                "Provider not configured. Use AWS.S3() to create this resource."
            )

        if isinstance(self._provider, str):
            raise ValueError(
                f"Provider '{self._provider}' is not resolved to an actual provider instance. Use AWS.S3() to create this resource."
            )

        # Type cast to help type checker
        from typing import cast

        provider = cast("Any", self._provider)

        # Create the bucket using the provider
        result = provider.create_s3_bucket(self._config)

        # Store the bucket name for later use
        if result and "BucketName" in result:
            self._bucket_name = result["BucketName"]
        if result and "WebsiteURL" in result:
            self._website_endpoint = result["WebsiteURL"]

        return result

    def _provider_update(self, diff: Dict[str, Any]) -> Dict[str, Any]:
        """Provider-specific update implementation"""
        if not self._provider:
            raise ValueError("Provider not configured.")

        if isinstance(self._provider, str):
            raise ValueError(
                f"Provider '{self._provider}' is not resolved to an actual provider instance."
            )

        # Type cast to help type checker
        from typing import cast

        provider = cast("Any", self._provider)

        bucket_name = self._bucket_name or self._config.get(
            "existing_bucket", self.metadata.name
        )
        return provider.update_s3_bucket(bucket_name, self._config)

    def _provider_destroy(self) -> None:
        """Provider-specific destroy implementation"""
        if not self._provider:
            raise ValueError("Provider not configured.")

        if isinstance(self._provider, str):
            raise ValueError(
                f"Provider '{self._provider}' is not resolved to an actual provider instance."
            )

        # Type cast to help type checker
        from typing import cast

        provider = cast("Any", self._provider)

        bucket_name = self._bucket_name or self._config.get(
            "existing_bucket", self.metadata.name
        )
        provider.delete_s3_bucket(bucket_name)

    def use_existing_bucket(self, bucket_name: str) -> "S3":
        """Use an existing S3 bucket instead of creating a new one"""
        self._config["existing_bucket"] = bucket_name
        self._bucket_name = bucket_name
        return self

    def allow_cloudfront(self, cloudfront_distribution) -> "S3":
        """Allow CloudFront distribution to access this bucket"""
        
        if isinstance(cloudfront_distribution, str):
            # Handle string distribution ID
            distribution_config = {
                "distribution_id": cloudfront_distribution,
                "domain_name": None,
                "distribution_resource": None,
                "distribution_id_string": cloudfront_distribution,  # Store the actual distribution ID
            }
        else:
            # Handle CloudFront resource object
            self.add_implicit_dependency(cloudfront_distribution)
            distribution_config = {
                "distribution_id": cloudfront_distribution.name,
                "domain_name": getattr(cloudfront_distribution, "domain_name", None),
                "distribution_resource": cloudfront_distribution,  # Store reference to resource
            }
            
        self._config["cloudfront_access"].append(distribution_config)
        return self

    def website(
        self, index_document: str = "index.html", error_document: str = "error.html"
    ) -> "S3":
        """Configure bucket for static website hosting"""
        self._config["website_config"] = {
            "IndexDocument": {"Suffix": index_document},
            "ErrorDocument": {"Key": error_document},
        }
        return self

    def cors(
        self,
        allowed_origins: Optional[List[str]] = None,
        allowed_methods: Optional[List[str]] = None,
    ) -> "S3":
        """Configure CORS for the bucket"""
        if allowed_origins is None:
            allowed_origins = ["*"]
        if allowed_methods is None:
            allowed_methods = ["GET", "HEAD"]

        self._config["cors_config"] = {
            "CORSRules": [
                {
                    "AllowedOrigins": allowed_origins,
                    "AllowedMethods": allowed_methods,
                    "AllowedHeaders": ["*"],
                    "MaxAgeSeconds": 3600,
                }
            ]
        }
        return self

    def policy(self, policy: Dict[str, Any]) -> "S3":
        """Set bucket policy"""
        self._config["policy"] = policy
        return self

    def public_read(self) -> "S3":
        """Allow public read access to the bucket"""
        self._config["public_access_block"] = False
        self._config["policy"] = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": ["s3:GetObject"],
                    "Resource": f"arn:aws:s3:::{self._bucket_name or self.name}/*",
                }
            ],
        }
        return self

    def versioning(self, enabled: bool = True) -> "S3":
        """Enable or disable versioning"""
        self._config["versioning"] = enabled
        return self

    def encryption(self, kms_key_id: Optional[str] = None) -> "S3":
        """Enable server-side encryption"""
        if kms_key_id:
            self._config["encryption"] = {
                "Rules": [
                    {
                        "ApplyServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "aws:kms",
                            "KMSMasterKeyID": kms_key_id,
                        }
                    }
                ]
            }
        else:
            self._config["encryption"] = {
                "Rules": [
                    {
                        "ApplyServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256",
                        }
                    }
                ]
            }
        return self

    def lifecycle_rule(
        self,
        rule_id: str,
        prefix: str = "",
        transitions: Optional[List[Dict]] = None,
        expiration_days: Optional[int] = None,
    ) -> "S3":
        """Add a lifecycle rule"""
        rule = {
            "ID": rule_id,
            "Status": "Enabled",
            "Filter": {"Prefix": prefix},
        }

        if transitions:
            rule["Transitions"] = transitions

        if expiration_days:
            rule["Expiration"] = {"Days": expiration_days}

        self._config["lifecycle_rules"].append(rule)
        return self

    def logging(self, target_bucket: str, target_prefix: str = "") -> "S3":
        """Enable access logging"""
        self._config["logging"] = {
            "TargetBucket": target_bucket,
            "TargetPrefix": target_prefix,
        }
        return self

    @property
    def bucket_name(self) -> Optional[str]:
        """Get the bucket name"""
        return self._bucket_name or self.name

    @property
    def website_endpoint(self) -> Optional[str]:
        """Get the website endpoint (available after creation if website is enabled)"""
        return self._website_endpoint

    @property
    def _resource_type(self) -> str:
        """Get resource type name for state detection"""
        return "S3"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "config": self._config,
                "bucket_name": self._bucket_name,
                "website_endpoint": self._website_endpoint,
            }
        )
        return base_dict
