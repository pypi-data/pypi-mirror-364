"""
AWS Route53 Domains Service
"""

import logging
from typing import Any, Dict, List, Optional

from .base import BaseAWSService
from ....core.interfaces.provider import ResourceQuery

logger = logging.getLogger(__name__)


class Route53DomainsService(BaseAWSService):
    """AWS Route53 Domains service implementation"""
    
    def create_domain_registration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create domain registration"""
        route53domains = self._get_client("route53domains")

        domain_name = config["domain_name"]
        contact_info = config["contact_info"]
        duration = config["duration_in_years"]

        # Convert contact info to AWS format
        aws_contact = self._convert_contact_to_aws(contact_info)

        # Use same contact for all types unless specified
        admin_contact = aws_contact.copy()
        tech_contact = aws_contact.copy()
        billing_contact = aws_contact.copy()

        # Override with specific contacts if provided
        if config.get("admin_contact") and hasattr(config["admin_contact"], "first_name"):
            admin_contact = self._convert_contact_to_aws(config["admin_contact"])
        if config.get("tech_contact") and hasattr(config["tech_contact"], "first_name"):
            tech_contact = self._convert_contact_to_aws(config["tech_contact"])
        if config.get("billing_contact") and hasattr(config["billing_contact"], "first_name"):
            billing_contact = self._convert_contact_to_aws(config["billing_contact"])

        try:
            # Register domain
            response = route53domains.register_domain(
                DomainName=domain_name,
                DurationInYears=duration,
                AutoRenew=config.get("auto_renew", False),
                AdminContact=admin_contact,
                RegistrantContact=aws_contact,
                TechContact=tech_contact,
                BillingContact=billing_contact,
                PrivacyProtectAdminContact=config.get("privacy_protection", True),
                PrivacyProtectRegistrantContact=config.get("privacy_protection", True),
                PrivacyProtectTechContact=config.get("privacy_protection", True),
                PrivacyProtectBillingContact=config.get("privacy_protection", True),
            )

            result = {
                "DomainName": domain_name,
                "OperationId": response["OperationId"],
                "Status": "PENDING",
                "ExpirationDate": None,
                "NameServers": config.get("name_servers", []),
            }

            # Set up Route53 hosted zone if requested
            if config.get("nexus_dns_setup", False):
                hosted_zone_result = self._setup_route53_hosted_zone(domain_name)
                result["HostedZoneId"] = hosted_zone_result.get("HostedZoneId")
                result["NameServers"] = hosted_zone_result.get("NameServers", [])

            return result

        except Exception as e:
            logger.error(f"Failed to register domain {domain_name}: {e}")
            raise

    def _convert_contact_to_aws(self, contact_info) -> Dict[str, Any]:
        """Convert contact info to AWS format"""
        # Format phone number for AWS requirements
        phone = contact_info.phone
        if phone.startswith("+46"):
            # Convert Swedish phone number to AWS format (+999.12345678)
            # Remove country code and format as required
            phone_digits = phone[3:].replace(" ", "").replace("-", "")
            phone = f"+46.{phone_digits}"
        
        # Handle state field based on country requirements
        country = contact_info.country.upper()
        state = ""
        if country in ["US", "CA", "AU"]:  # Countries that require state
            state = contact_info.state or ""
        # For countries like Sweden (SE), state should not be set
        
        contact = {
            "FirstName": contact_info.first_name,
            "LastName": contact_info.last_name,
            "ContactType": "PERSON" if not contact_info.organization else "COMPANY",
            "OrganizationName": contact_info.organization or "",
            "AddressLine1": contact_info.address,
            "City": contact_info.city,
            "CountryCode": country,
            "ZipCode": contact_info.zip_code,
            "PhoneNumber": phone,
            "Email": contact_info.email,
        }
        
        # Only add state if it's required for this country
        if state:
            contact["State"] = state
            
        return contact

    def _setup_route53_hosted_zone(self, domain_name: str) -> Dict[str, Any]:
        """Set up Route53 hosted zone for domain"""
        route53 = self._get_client("route53")

        # Create hosted zone
        response = route53.create_hosted_zone(
            Name=domain_name,
            CallerReference=f"domain-registration-{domain_name}-{hash(domain_name) % 1000000}",
            HostedZoneConfig={
                "Comment": f"Hosted zone for {domain_name}",
                "PrivateZone": False,
            },
        )

        hosted_zone_id = response["HostedZone"]["Id"].split("/")[-1]
        name_servers = [ns["Value"] for ns in response["DelegationSet"]["NameServers"]]

        return {
            "HostedZoneId": hosted_zone_id,
            "NameServers": name_servers,
        }

    def check_domain_availability(self, domain_name: str) -> bool:
        """Check if domain is available for registration"""
        route53domains = self._get_client("route53domains")

        try:
            response = route53domains.check_domain_availability(DomainName=domain_name)
            return response["Availability"] == "AVAILABLE"
        except Exception as e:
            logger.error(f"Failed to check domain availability for {domain_name}: {e}")
            return False

    def get_domain_pricing(self, domain_name: str) -> Dict[str, Any]:
        """Get pricing information for domain"""
        route53domains = self._get_client("route53domains")

        try:
            # Extract TLD from domain name
            tld = domain_name.split(".")[-1]
            response = route53domains.list_prices(Tld=tld)

            if response["Prices"]:
                price_info = response["Prices"][0]
                return {
                    "tld": tld,
                    "registration_price": price_info["RegistrationPrice"],
                    "renewal_price": price_info["RenewalPrice"],
                    "transfer_price": price_info["TransferPrice"],
                    "currency": price_info["RegistrationPrice"]["Currency"],
                }
            else:
                return {"error": f"No pricing information found for {tld}"}

        except Exception as e:
            logger.error(f"Failed to get domain pricing for {domain_name}: {e}")
            return {"error": str(e)}

    def update_domain_registration(self, domain_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update domain registration"""
        return {"DomainName": domain_name}

    def delete_domain_registration(self, domain_name: str) -> None:
        """Delete domain registration"""
        pass

    def list_domain_registrations(self) -> List[Dict[str, Any]]:
        """List domain registrations"""
        route53domains = self._get_client("route53domains")
        domains = []

        try:
            response = route53domains.list_domains()
            if "Domains" in response:
                for domain in response["Domains"]:
                    domains.append({
                        "DomainName": domain["DomainName"],
                        "Status": domain.get("StatusList", ["UNKNOWN"])[0] if domain.get("StatusList") else "UNKNOWN",
                        "AutoRenew": domain.get("AutoRenew", False),
                        "ExpirationDate": domain.get("Expiry"),
                    })
        except Exception as e:
            logger.debug(f"Error listing domain registrations: {e}")

        return domains

    def estimate_cost(self, config: Dict[str, Any]) -> Dict[str, float]:
        """Estimate domain registration cost"""
        # Basic cost estimation - varies by TLD
        return {"monthly": 1.0}  # Placeholder