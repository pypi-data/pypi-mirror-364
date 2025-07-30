"""
AWS ACM (Certificate Manager) Service
"""

import logging
from typing import Any, Dict, List, Optional

from .base import BaseAWSService
from ....core.interfaces.provider import ResourceQuery

logger = logging.getLogger(__name__)


class ACMService(BaseAWSService):
    """AWS ACM service implementation"""

    def create_certificate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create SSL certificate"""
        # Use us-east-1 for CloudFront compatibility if specified
        region = (
            "us-east-1"
            if config.get("cloudfront_compatible", False)
            else self.config.region
        )
        acm = self.provider._get_client("acm")

        domain_name = config["domain_name"]
        subject_alternative_names = config.get("subject_alternative_names", [])
        validation_method = config.get("validation_method", "DNS")

        # Build certificate request
        certificate_request = {
            "DomainName": domain_name,
            "ValidationMethod": (
                validation_method.value
                if hasattr(validation_method, "value")
                else validation_method
            ),
            "KeyAlgorithm": config.get("key_algorithm", "RSA_2048"),
            "Options": {
                "CertificateTransparencyLoggingPreference": (
                    "ENABLED"
                    if config.get("certificate_transparency_logging", True)
                    else "DISABLED"
                ),
            },
        }

        # Add subject alternative names if provided
        if subject_alternative_names:
            certificate_request["SubjectAlternativeNames"] = subject_alternative_names

        # Add tags if provided
        tags = config.get("tags", {})
        if tags:
            certificate_request["Tags"] = [
                {"Key": key, "Value": value} for key, value in tags.items()
            ]

        try:
            # Request certificate
            response = acm.request_certificate(**certificate_request)
            certificate_arn = response["CertificateArn"]

            # Get certificate details
            cert_details = acm.describe_certificate(CertificateArn=certificate_arn)
            certificate = cert_details["Certificate"]

            result = {
                "CertificateArn": certificate_arn,
                "Status": certificate["Status"],
                "DomainName": certificate["DomainName"],
                "SubjectAlternativeNames": certificate.get(
                    "SubjectAlternativeNames", []
                ),
                "DomainValidationOptions": certificate.get(
                    "DomainValidationOptions", []
                ),
                "ValidationRecords": [],
                "CreatedAt": certificate.get("CreatedAt"),
                "IssuedAt": certificate.get("IssuedAt"),
                "NotBefore": certificate.get("NotBefore"),
                "NotAfter": certificate.get("NotAfter"),
            }

            # Extract validation records for DNS validation
            if validation_method == "DNS":
                validation_records = []
                for domain_validation in certificate.get("DomainValidationOptions", []):
                    if "ResourceRecord" in domain_validation:
                        validation_records.append(
                            {
                                "Name": domain_validation["ResourceRecord"]["Name"],
                                "Type": domain_validation["ResourceRecord"]["Type"],
                                "Value": domain_validation["ResourceRecord"]["Value"],
                                "Domain": domain_validation["DomainName"],
                            }
                        )
                result["ValidationRecords"] = validation_records

            return result

        except Exception as e:
            logger.error(f"Failed to create certificate for {domain_name}: {e}")
            raise

    def get_certificate_validation_records(
        self, certificate_arn: str
    ) -> List[Dict[str, Any]]:
        """Get DNS validation records for certificate"""
        acm = self._get_client("acm")

        try:
            response = acm.describe_certificate(CertificateArn=certificate_arn)
            certificate = response["Certificate"]

            validation_records = []
            for domain_validation in certificate.get("DomainValidationOptions", []):
                if "ResourceRecord" in domain_validation:
                    validation_records.append(
                        {
                            "Name": domain_validation["ResourceRecord"]["Name"],
                            "Type": domain_validation["ResourceRecord"]["Type"],
                            "Value": domain_validation["ResourceRecord"]["Value"],
                            "Domain": domain_validation["DomainName"],
                        }
                    )

            return validation_records

        except Exception as e:
            logger.error(
                f"Failed to get validation records for certificate {certificate_arn}: {e}"
            )
            return []

    def update_certificate(
        self, certificate_arn: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update certificate"""
        # Certificates can't be updated directly, would need to be re-issued
        return {"CertificateArn": certificate_arn}

    def delete_certificate(self, certificate_arn: str) -> None:
        """Delete certificate"""
        acm = self._get_client("acm")

        try:
            acm.delete_certificate(CertificateArn=certificate_arn)
            logger.info(f"Deleted certificate {certificate_arn}")
        except Exception as e:
            logger.error(f"Failed to delete certificate {certificate_arn}: {e}")
            raise

    def list_certificates(self) -> List[Dict[str, Any]]:
        """List ACM certificates"""
        # Use us-east-1 for CloudFront compatibility by default
        acm = self.provider._get_client("acm")
        certificates = []

        try:
            response = acm.list_certificates()
            if "CertificateSummaryList" in response:
                for cert_summary in response["CertificateSummaryList"]:
                    certificates.append({
                        "CertificateArn": cert_summary["CertificateArn"],
                        "DomainName": cert_summary["DomainName"],
                        "Status": cert_summary.get("Status", "UNKNOWN"),
                        "SubjectAlternativeNames": cert_summary.get("SubjectAlternativeNames", []),
                    })
        except Exception as e:
            logger.debug(f"Error listing certificates: {e}")

        return certificates

    def estimate_cost(self, config: Dict[str, Any]) -> Dict[str, float]:
        """Estimate ACM certificate cost"""
        return {"monthly": 0.0}  # ACM certificates are free
