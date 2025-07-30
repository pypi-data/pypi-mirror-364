"""
AWS Certificate Manager (ACM) SSL Certificate
"""

from typing import Any, Dict, List, Optional, Union
from ...core.nexus.base_resource import BaseResource, ResourceSpec
from enum import Enum


class ValidationMethod(Enum):
    """Certificate validation methods"""

    DNS = "DNS"
    EMAIL = "EMAIL"


class CertificateStatus(Enum):
    """Certificate status values"""

    PENDING_VALIDATION = "PENDING_VALIDATION"
    ISSUED = "ISSUED"
    INACTIVE = "INACTIVE"
    EXPIRED = "EXPIRED"
    VALIDATION_TIMED_OUT = "VALIDATION_TIMED_OUT"
    REVOKED = "REVOKED"
    FAILED = "FAILED"


class CertificateManager(BaseResource):
    """
    AWS Certificate Manager (ACM) SSL Certificate with fluent API

    Usage:
        certificate = AWS.CertificateManager("my-cert")
                     .domain("example.com")
                     .wildcard()
                     .dns_validation()
                     .auto_renew(True)
                     .cloudfront_compatible()
                     .create()
    """

    def __init__(self, name: str):
        super().__init__(name)
        self._config = {
            "name": name,
            "domain_name": None,
            "subject_alternative_names": [],
            "validation_method": ValidationMethod.DNS,
            "validation_domain": None,
            "validation_emails": [],
            "auto_renew": True,
            "cloudfront_compatible": False,
            "key_algorithm": "RSA_2048",
            "certificate_transparency_logging": True,
            "tags": {},
        }
        self._certificate_arn = None
        self._certificate_status = None
        self._domain_validation_options = []
        self._validation_records = []
        self._expiration_date = None
        self._issued_at = None

    def _create_spec(self) -> ResourceSpec:
        """Create the resource-specific specification"""
        return ResourceSpec()

    def _validate_spec(self) -> None:
        """Validate the resource specification"""
        if not self._config["domain_name"]:
            raise ValueError("Domain name is required")

        if self._config["validation_method"] == ValidationMethod.EMAIL:
            if not self._config["validation_emails"]:
                raise ValueError("Validation emails are required for email validation")

    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        return self._config

    def _provider_create(self) -> Dict[str, Any]:
        """Provider-specific create implementation"""
        if not self._provider:
            raise ValueError(
                "Provider not configured. Use AWS.CertificateManager() to create this resource."
            )

        if isinstance(self._provider, str):
            raise ValueError(
                f"Provider '{self._provider}' is not resolved to an actual provider instance. Use AWS.CertificateManager() to create this resource."
            )

        # Type cast to help type checker
        from typing import cast

        provider = cast(
            "Any", self._provider
        )  # Use Any since we don't have the AWS provider interface imported

        # Create the certificate using the provider
        result = provider.create_certificate(self._config)

        # Store the certificate info for later use
        if result:
            self._certificate_arn = result.get("CertificateArn")
            self._certificate_status = result.get("Status")
            self._domain_validation_options = result.get("DomainValidationOptions", [])
            self._validation_records = result.get("ValidationRecords", [])

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

        return provider.update_certificate(self._certificate_arn, self._config)

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

        provider.delete_certificate(self._certificate_arn)

    def domain(self, domain_name: Union[str, Any]) -> "CertificateManager":
        """Set the primary domain name for the certificate"""
        if isinstance(domain_name, str):
            self._config["domain_name"] = domain_name
        elif hasattr(domain_name, "domain_name"):
            # DomainRegistration resource
            self.add_implicit_dependency(domain_name)
            self._config["domain_name"] = domain_name.domain_name
        else:
            self._config["domain_name"] = str(domain_name)
        return self

    def wildcard(self, enabled: bool = True) -> "CertificateManager":
        """Add wildcard subdomain to the certificate"""
        if enabled and self._config["domain_name"]:
            wildcard_domain = f"*.{self._config['domain_name']}"
            if wildcard_domain not in self._config["subject_alternative_names"]:
                self._config["subject_alternative_names"].append(wildcard_domain)
        return self

    def alternative_names(self, *domains: str) -> "CertificateManager":
        """Add subject alternative names (SANs) to the certificate"""
        for domain in domains:
            if domain not in self._config["subject_alternative_names"]:
                self._config["subject_alternative_names"].append(domain)
        return self

    def dns_validation(
        self, validation_domain: Optional[str] = None
    ) -> "CertificateManager":
        """Use DNS validation method"""
        self._config["validation_method"] = ValidationMethod.DNS
        if validation_domain:
            self._config["validation_domain"] = validation_domain
        return self

    def email_validation(self, *emails: str) -> "CertificateManager":
        """Use email validation method"""
        self._config["validation_method"] = ValidationMethod.EMAIL
        self._config["validation_emails"] = list(emails)
        return self

    def auto_renew(self, enabled: bool = True) -> "CertificateManager":
        """Enable or disable automatic renewal"""
        self._config["auto_renew"] = enabled
        return self

    def cloudfront_compatible(self, enabled: bool = True) -> "CertificateManager":
        """
        Make certificate compatible with CloudFront
        Note: CloudFront requires certificates to be in us-east-1
        """
        self._config["cloudfront_compatible"] = enabled
        return self

    def key_algorithm(self, algorithm: str) -> "CertificateManager":
        """Set the key algorithm (RSA_2048, RSA_4096, EC_prime256v1, EC_secp384r1)"""
        valid_algorithms = ["RSA_2048", "RSA_4096", "EC_prime256v1", "EC_secp384r1"]
        if algorithm not in valid_algorithms:
            raise ValueError(
                f"Invalid key algorithm. Must be one of: {valid_algorithms}"
            )
        self._config["key_algorithm"] = algorithm
        return self

    def transparency_logging(self, enabled: bool = True) -> "CertificateManager":
        """Enable or disable certificate transparency logging"""
        self._config["certificate_transparency_logging"] = enabled
        return self

    def tags(self, **tags: str) -> "CertificateManager":
        """Add tags to the certificate"""
        self._config["tags"].update(tags)
        return self

    def get_validation_records(self) -> List[Dict[str, Any]]:
        """Get DNS validation records that need to be created"""
        if not self._validation_records and self._provider:
            if isinstance(self._provider, str):
                # Provider is a string, can't get validation records
                return []

            # Try to get validation records from provider
            if self._certificate_arn:
                # Type cast to help type checker
                from typing import cast

                provider = cast("Any", self._provider)
                self._validation_records = provider.get_certificate_validation_records(
                    self._certificate_arn
                )

        return self._validation_records

    def wait_for_validation(self, timeout: int = 300) -> bool:
        """Wait for certificate validation to complete"""
        if not self._provider:
            raise ValueError("Provider not configured.")

        if isinstance(self._provider, str):
            raise ValueError(
                f"Provider '{self._provider}' is not resolved to an actual provider instance."
            )

        if not self._certificate_arn:
            raise ValueError(
                "Certificate must be created before waiting for validation"
            )

        # Type cast to help type checker
        from typing import cast

        provider = cast("Any", self._provider)
        return provider.wait_for_certificate_validation(self._certificate_arn, timeout)

    def auto_validate_dns(
        self, route53_zone_id: Optional[str] = None
    ) -> "CertificateManager":
        """
        Automatically create DNS validation records in Route53

        Args:
            route53_zone_id: Optional hosted zone ID. If not provided, will try to find automatically
        """
        if not self._provider:
            raise ValueError("Provider not configured.")

        if isinstance(self._provider, str):
            raise ValueError(
                f"Provider '{self._provider}' is not resolved to an actual provider instance."
            )

        if not self._certificate_arn:
            raise ValueError("Certificate must be created before auto-validating")

        # Type cast to help type checker
        from typing import cast

        provider = cast("Any", self._provider)
        provider.auto_validate_certificate_dns(self._certificate_arn, route53_zone_id)
        return self

    @property
    def certificate_arn(self) -> Optional[str]:
        """Get the certificate ARN"""
        return self._certificate_arn

    @property
    def certificate_status(self) -> Optional[str]:
        """Get the certificate status"""
        return self._certificate_status

    @property
    def domain_validation_options(self) -> List[Dict[str, Any]]:
        """Get the domain validation options"""
        return self._domain_validation_options

    @property
    def expiration_date(self) -> Optional[str]:
        """Get the certificate expiration date"""
        return self._expiration_date

    @property
    def issued_at(self) -> Optional[str]:
        """Get the certificate issue date"""
        return self._issued_at

    @property
    def is_valid(self) -> bool:
        """Check if certificate is valid and issued"""
        return self._certificate_status == CertificateStatus.ISSUED.value

    @property
    def _resource_type(self) -> str:
        """Get resource type name for state detection"""
        return "CertificateManager"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "config": self._config,
                "certificate_arn": self._certificate_arn,
                "certificate_status": self._certificate_status,
                "domain_validation_options": self._domain_validation_options,
                "validation_records": self._validation_records,
                "expiration_date": self._expiration_date,
                "issued_at": self._issued_at,
            }
        )
        return base_dict
