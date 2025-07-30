"""
AWS CloudFront CDN Distribution
"""

from typing import Any, Dict, List, Optional, Union
from ...core.nexus.base_resource import BaseResource, ResourceSpec
import logging

logger = logging.getLogger(__name__)


class CloudFront(BaseResource):
    """
    AWS CloudFront CDN Distribution with fluent API

    Usage:
        cdn = AWS.CloudFront("my-cdn")
              .copy_from(reference_distribution)
              .clear_domains()
              .custom_domain("example.com")
              .ssl_certificate(cert)
              .create()
    """

    def __init__(self, name: str):
        super().__init__(name)
        self._config = {
            "name": name,
            "custom_domains": [],
            "origin_id": None,
            "ssl_certificate": None,
            "methods": ["GET", "HEAD"],
            "reference_config": None,
            "origins": [],
            "behaviors": [],
            "comment": f"CloudFront distribution for {name}",
            "enabled": True,
            "price_class": "PriceClass_All",
            "default_root_object": "index.html",
        }
        self._domain_name = None  # Will be set after creation

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
                "Provider not configured. Use AWS.CloudFront() to create this resource."
            )

        if isinstance(self._provider, str):
            raise ValueError(
                f"Provider '{self._provider}' is not resolved to an actual provider instance. Use AWS.CloudFront() to create this resource."
            )

        # Type cast to help type checker
        from typing import cast

        provider = cast("Any", self._provider)

        # Create the distribution using the provider
        result = provider.create_cloudfront_distribution(self._config)

        # Store the domain name for later use
        if result and "DomainName" in result:
            self._domain_name = result["DomainName"]

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

        return provider.update_cloudfront_distribution(self.metadata.name, self._config)

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

        provider.delete_cloudfront_distribution(self.metadata.name)

    def copy_from(self, reference_distribution_id: str) -> "CloudFront":
        """Copy configuration from an existing distribution by ID"""
        self._config["reference_distribution_id"] = reference_distribution_id
        return self

    def clear_domains(self) -> "CloudFront":
        """Clear all custom domains"""
        self._config["custom_domains"] = []
        return self

    def custom_domain(self, domain: str) -> "CloudFront":
        """Add a custom domain (CNAME)"""
        if domain not in self._config["custom_domains"]:
            self._config["custom_domains"].append(domain)
        return self

    def target_origin_id(self, origin_id: str) -> "CloudFront":
        """Set the target origin ID"""
        self._config["origin_id"] = origin_id
        return self

    def ssl_certificate(
        self, certificate: Union[str, Dict[str, Any], Any]
    ) -> "CloudFront":
        """Set SSL certificate (ARN, certificate object, or CertificateManager resource)"""
        if isinstance(certificate, str):
            self._config["ssl_certificate"] = {"arn": certificate}
        elif hasattr(certificate, "certificate_arn"):
            # CertificateManager resource
            self.add_implicit_dependency(certificate)  # type: ignore
            self._config["ssl_certificate"] = {"resource": certificate}
        else:
            self._config["ssl_certificate"] = certificate
        return self

    def auto_ssl_certificate(self) -> "CloudFront":
        """Automatically find and use SSL certificate for custom domains"""
        self._config["auto_ssl_certificate"] = True
        return self

    def enable_all_methods(self) -> "CloudFront":
        """Enable all HTTP methods (GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE)"""
        self._config["methods"] = [
            "GET",
            "HEAD",
            "OPTIONS",
            "PUT",
            "POST",
            "PATCH",
            "DELETE",
        ]
        return self

    def methods(self, methods: List[str]) -> "CloudFront":
        """Set allowed HTTP methods"""
        self._config["methods"] = methods
        return self

    def origin(
        self, origin_id: str, domain_name: str, origin_path: str = ""
    ) -> "CloudFront":
        """Add an origin"""
        origin = {
            "Id": origin_id,
            "DomainName": domain_name,
            "OriginPath": origin_path,
            "CustomOriginConfig": {
                "HTTPPort": 80,
                "HTTPSPort": 443,
                "OriginProtocolPolicy": "https-only",
            },
        }
        self._config["origins"].append(origin)
        return self

    def s3_origin(
        self, origin_id: str, bucket_name: str, origin_path: str = ""
    ) -> "CloudFront":
        """Add an S3 origin"""
        origin = {
            "Id": origin_id,
            "DomainName": f"{bucket_name}.s3.amazonaws.com",
            "OriginPath": origin_path,
            "S3OriginConfig": {"OriginAccessIdentity": ""},
        }
        self._config["origins"].append(origin)
        return self

    def price_class(self, price_class: str) -> "CloudFront":
        """Set price class (PriceClass_All, PriceClass_100, PriceClass_200)"""
        self._config["price_class"] = price_class
        return self

    def comment(self, comment: str) -> "CloudFront":
        """Set distribution comment"""
        self._config["comment"] = comment
        return self

    def default_root_object(self, object_name: str) -> "CloudFront":
        """Set default root object"""
        self._config["default_root_object"] = object_name
        return self

    def enabled(self, enabled: bool = True) -> "CloudFront":
        """Enable or disable the distribution"""
        self._config["enabled"] = enabled
        return self

    @property
    def domain_name(self) -> Optional[str]:
        """Get the CloudFront domain name (available after creation)"""
        # Check if domain name is available from status provider data
        if self._domain_name:
            return self._domain_name

        # Try to get from provider data if not set
        if self.status.provider_data and "DomainName" in self.status.provider_data:
            self._domain_name = self.status.provider_data["DomainName"]
            return self._domain_name

        # Note: We intentionally do NOT use the reference distribution's domain name
        # when using .copy_from(), as that would return the wrong domain name.
        # The domain name should only be available after this distribution is created.

        # If not available locally, try to look up the distribution from AWS
        if self._provider and not isinstance(self._provider, str):
            try:
                # Check if this distribution exists in AWS by looking it up
                state = self._provider.get_resource_state(self.metadata)
                if state and "DomainName" in state:
                    self._domain_name = state["DomainName"]
                    # Also populate the provider data for future use
                    self.status.provider_data = state
                    return self._domain_name
            except Exception:
                # If lookup fails, return None
                pass

        return None

    def _get_reference_domain_name(self, reference_id: str) -> Optional[str]:
        """Get domain name from a reference CloudFront distribution"""
        try:
            # Use the provider to get the reference distribution info
            if hasattr(self._provider, 'cloudfront'):
                # New modular provider
                dist_info = self._provider.cloudfront.get_distribution(reference_id)
                if dist_info and "DomainName" in dist_info:
                    return dist_info["DomainName"]
            else:
                # Legacy provider - access boto3 client directly
                import boto3
                cloudfront = boto3.client('cloudfront')
                response = cloudfront.get_distribution(Id=reference_id)
                if response and "Distribution" in response:
                    return response["Distribution"].get("DomainName")
        except Exception as e:
            logger.debug(f"Failed to get reference distribution {reference_id}: {e}")
            return None
        
        return None

    @property
    def distribution_id(self) -> Optional[str]:
        """Get the CloudFront distribution ID (available after creation or lookup)"""
        # Check if ID is available from status provider data
        if self.status.provider_data and "Id" in self.status.provider_data:
            return self.status.provider_data["Id"]

        # If not available locally, try to look up the distribution from AWS
        if self._provider and not isinstance(self._provider, str):
            try:
                # Check if this distribution exists in AWS by looking it up
                state = self._provider.get_resource_state(self.metadata)
                if state and "Id" in state:
                    # Also populate the provider data for future use
                    self.status.provider_data = state
                    # Cache domain name too if available
                    if "DomainName" in state:
                        self._domain_name = state["DomainName"]
                    return state["Id"]
            except Exception:
                # If lookup fails, return None
                pass

        return None

    @property
    def _resource_type(self) -> str:
        """Get resource type name for state detection"""
        return "CloudFront"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "config": self._config,
                "domain_name": self._domain_name,
            }
        )
        return base_dict
