"""
AWS Route53 Domain Registration
"""

from typing import Any, Dict, List, Optional
from ...core.nexus.base_resource import BaseResource, ResourceSpec
from dataclasses import dataclass


@dataclass
class ContactInfo:
    """Contact information for domain registration"""

    email: str
    first_name: str
    last_name: str
    phone: str
    address: str
    city: str
    zip_code: str
    country: str
    organization: Optional[str] = None
    state: Optional[str] = None  # Required for some countries


class DomainRegistration(BaseResource):
    """
    AWS Route53 Domain Registration with fluent API

    Usage:
        domain = AWS.DomainRegistration("my-domain")
                .domain("example.com")
                .contact(
                    email="admin@example.com",
                    first_name="John",
                    last_name="Doe",
                    phone="+1234567890",
                    address="123 Main St",
                    city="New York",
                    zip_code="10001",
                    country="US"
                )
                .duration(1)
                .privacy(True)
                .nexus_dns_setup()
                .auto_renew(False)
                .create()
    """

    def __init__(self, name: str):
        super().__init__(name)
        self._config = {
            "name": name,
            "domain_name": None,
            "contact_info": None,
            "duration_in_years": 1,
            "privacy_protection": True,
            "auto_renew": False,
            "nexus_dns_setup": False,
            "name_servers": [],
            "admin_contact": None,
            "tech_contact": None,
            "billing_contact": None,
        }
        self._domain_name = None
        self._registration_status = None
        self._expiration_date = None
        self._name_servers = []

    def _create_spec(self) -> ResourceSpec:
        """Create the resource-specific specification"""
        return ResourceSpec()

    def _validate_spec(self) -> None:
        """Validate the resource specification"""
        if not self._config["domain_name"]:
            raise ValueError("Domain name is required")
        if not self._config["contact_info"]:
            raise ValueError("Contact information is required")

    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        return self._config

    def _provider_create(self) -> Dict[str, Any]:
        """Provider-specific create implementation"""
        if not self._provider:
            raise ValueError(
                "Provider not configured. Use AWS.DomainRegistration() to create this resource."
            )

        if isinstance(self._provider, str):
            raise ValueError(
                f"Provider '{self._provider}' is not resolved to an actual provider instance. Use a provider factory or ensure proper provider setup."
            )

        # Type cast to help type checker
        from typing import cast

        provider = cast("Any", self._provider)

        # Create the domain registration using the provider
        result = provider.create_domain_registration(self._config)

        # Store the domain info for later use
        if result:
            self._domain_name = result.get("DomainName")
            self._registration_status = result.get("Status")
            self._expiration_date = result.get("ExpirationDate")
            self._name_servers = result.get("NameServers", [])

        return result

    def _provider_update(self, diff: Dict[str, Any]) -> Dict[str, Any]:
        """Provider-specific update implementation"""
        if not self._provider:
            raise ValueError("Provider not configured.")

        if isinstance(self._provider, str):
            raise ValueError(
                f"Provider '{self._provider}' is not resolved to an actual provider instance. Use a provider factory or ensure proper provider setup."
            )

        # Type cast to help type checker
        from typing import cast

        provider = cast("Any", self._provider)

        return provider.update_domain_registration(self._domain_name, self._config)

    def _provider_destroy(self) -> None:
        """Provider-specific destroy implementation"""
        if not self._provider:
            raise ValueError("Provider not configured.")

        if isinstance(self._provider, str):
            raise ValueError(
                f"Provider '{self._provider}' is not resolved to an actual provider instance. Use a provider factory or ensure proper provider setup."
            )

        # Type cast to help type checker
        from typing import cast

        provider = cast("Any", self._provider)

        # Note: Domain deletion is usually not immediate and has restrictions
        provider.delete_domain_registration(self._domain_name)

    def domain(self, domain_name: str) -> "DomainRegistration":
        """Set the domain name to register"""
        self._config["domain_name"] = domain_name
        return self

    def contact(
        self,
        email: str,
        first_name: str,
        last_name: str,
        phone: str,
        address: str,
        city: str,
        zip_code: str,
        country: str,
        organization: Optional[str] = None,
        state: Optional[str] = None,
    ) -> "DomainRegistration":
        """Set contact information for domain registration"""
        contact_info = ContactInfo(
            email=email,
            first_name=first_name,
            last_name=last_name,
            organization=organization,
            phone=phone,
            address=address,
            city=city,
            zip_code=zip_code,
            country=country,
            state=state,
        )

        self._config["contact_info"] = contact_info
        # Use same contact for all contact types unless specified otherwise
        self._config["admin_contact"] = contact_info
        self._config["tech_contact"] = contact_info
        self._config["billing_contact"] = contact_info

        return self

    def admin_contact(self, contact_info: ContactInfo) -> "DomainRegistration":
        """Set separate admin contact information"""
        self._config["admin_contact"] = contact_info
        return self

    def tech_contact(self, contact_info: ContactInfo) -> "DomainRegistration":
        """Set separate technical contact information"""
        self._config["tech_contact"] = contact_info
        return self

    def billing_contact(self, contact_info: ContactInfo) -> "DomainRegistration":
        """Set separate billing contact information"""
        self._config["billing_contact"] = contact_info
        return self

    def duration(self, years: int) -> "DomainRegistration":
        """Set registration duration in years (1-10)"""
        if years < 1 or years > 10:
            raise ValueError("Duration must be between 1 and 10 years")
        self._config["duration_in_years"] = years
        return self

    def privacy(self, enabled: bool = True) -> "DomainRegistration":
        """Enable or disable privacy protection"""
        self._config["privacy_protection"] = enabled
        return self

    def auto_renew(self, enabled: bool = True) -> "DomainRegistration":
        """Enable or disable auto-renewal"""
        self._config["auto_renew"] = enabled
        return self

    def nexus_dns_setup(self, enabled: bool = True) -> "DomainRegistration":
        """Automatically set up Route53 hosted zone and name servers"""
        self._config["nexus_dns_setup"] = enabled
        return self

    def name_servers(self, name_servers: List[str]) -> "DomainRegistration":
        """Set custom name servers"""
        self._config["name_servers"] = name_servers
        return self

    def check_availability(self) -> bool:
        """Check if domain is available for registration"""
        if not self._provider:
            raise ValueError("Provider not configured.")

        if isinstance(self._provider, str):
            raise ValueError(
                f"Provider '{self._provider}' is not resolved to an actual provider instance. Use a provider factory or ensure proper provider setup."
            )

        if not self._config["domain_name"]:
            raise ValueError("Domain name must be set before checking availability")

        # Type cast to help type checker
        from typing import cast

        provider = cast("Any", self._provider)

        return provider.check_domain_availability(self._config["domain_name"])

    def get_pricing(self) -> Dict[str, Any]:
        """Get pricing information for the domain"""
        if not self._provider:
            raise ValueError("Provider not configured.")

        if isinstance(self._provider, str):
            raise ValueError(
                f"Provider '{self._provider}' is not resolved to an actual provider instance. Use a provider factory or ensure proper provider setup."
            )

        if not self._config["domain_name"]:
            raise ValueError("Domain name must be set before getting pricing")

        # Type cast to help type checker
        from typing import cast

        provider = cast("Any", self._provider)

        return provider.get_domain_pricing(self._config["domain_name"])

    @property
    def domain_name(self) -> Optional[str]:
        """Get the registered domain name"""
        return self._domain_name or self._config["domain_name"]

    @property
    def registration_status(self) -> Optional[str]:
        """Get the registration status"""
        return self._registration_status

    @property
    def expiration_date(self) -> Optional[str]:
        """Get the domain expiration date"""
        return self._expiration_date

    @property
    def name_servers_list(self) -> List[str]:
        """Get the name servers for the domain"""
        return self._name_servers

    @property
    def _resource_type(self) -> str:
        """Get resource type name for state detection"""
        return "DomainRegistration"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "config": self._config,
                "domain_name": self._domain_name,
                "registration_status": self._registration_status,
                "expiration_date": self._expiration_date,
                "name_servers": self._name_servers,
            }
        )
        return base_dict
