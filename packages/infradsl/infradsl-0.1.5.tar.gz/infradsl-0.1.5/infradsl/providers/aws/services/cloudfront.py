"""
AWS CloudFront Service
"""

import logging
from typing import Any, Dict, List, Optional

from .base import BaseAWSService
from ....core.interfaces.provider import ResourceQuery

logger = logging.getLogger(__name__)


class CloudFrontService(BaseAWSService):
    """AWS CloudFront service implementation"""
    
    def create_distribution(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create CloudFront distribution"""
        cloudfront = self._get_client("cloudfront")

        # Build distribution config
        distribution_config = {
            "CallerReference": f"infradsl-{config['name']}",
            "Comment": config["name"],  # Use resource name for state detection
            "Enabled": config.get("enabled", True),
            "PriceClass": config.get("price_class", "PriceClass_All"),
        }

        # Set default root object
        if config.get("default_root_object"):
            distribution_config["DefaultRootObject"] = config["default_root_object"]

        # Get reference distribution configuration if specified
        reference_distribution_id = config.get("reference_distribution_id")
        if reference_distribution_id:
            try:
                # Fetch the reference distribution configuration
                reference_response = cloudfront.get_distribution_config(
                    Id=reference_distribution_id
                )
                reference_config = reference_response["DistributionConfig"]

                # Start with the reference configuration (deep copy)
                import copy
                distribution_config = copy.deepcopy(reference_config)

                # Remove fields that shouldn't be copied
                distribution_config.pop("ETag", None)

                # Update with InfraDSL-specific values
                distribution_config["CallerReference"] = (
                    f"infradsl-{config['name']}-{hash(config['name']) % 1000000}"
                )

                # Set custom comment with InfraDSL resource name (used for state detection)
                distribution_config["Comment"] = config["name"]

                # Clear existing aliases if we're going to set new ones
                if config.get("custom_domains"):
                    distribution_config["Aliases"] = {"Quantity": 0, "Items": []}

            except Exception as e:
                logger.error(
                    f"Error fetching reference distribution {reference_distribution_id}: {e}"
                )

        # Configure origins if not already from reference
        if not distribution_config.get("Origins"):
            origins = config.get("origins", [])
            if origins:
                distribution_config["Origins"] = {
                    "Quantity": len(origins),
                    "Items": origins,
                }

        # Configure custom domains (aliases)
        aliases = config.get("custom_domains", [])
        if aliases:
            distribution_config["Aliases"] = {
                "Quantity": len(aliases),
                "Items": aliases,
            }

        # Configure SSL certificate
        ssl_cert = config.get("ssl_certificate")
        auto_ssl = config.get("auto_ssl_certificate", False)

        if ssl_cert:
            cert_arn = self._extract_cert_arn(ssl_cert)
            if cert_arn:
                distribution_config["ViewerCertificate"] = {
                    "ACMCertificateArn": cert_arn,
                    "SSLSupportMethod": "sni-only",
                    "MinimumProtocolVersion": "TLSv1.2_2021",
                    "CertificateSource": "acm",
                }
        elif aliases and auto_ssl:
            cert_arn = self._find_ssl_certificate_for_domain(aliases[0])
            if cert_arn:
                distribution_config["ViewerCertificate"] = {
                    "ACMCertificateArn": cert_arn,
                    "SSLSupportMethod": "sni-only",
                    "MinimumProtocolVersion": "TLSv1.2_2021",
                    "CertificateSource": "acm",
                }
        elif not distribution_config.get("ViewerCertificate"):
            distribution_config["ViewerCertificate"] = {
                "CloudFrontDefaultCertificate": True,
                "MinimumProtocolVersion": "TLSv1.2_2021",
            }

        # Configure default cache behavior
        if not distribution_config.get("DefaultCacheBehavior"):
            default_behavior = {
                "TargetOriginId": config.get("origin_id", "default"),
                "ViewerProtocolPolicy": "redirect-to-https",
                "MinTTL": 0,
                "ForwardedValues": {
                    "QueryString": False,
                    "Cookies": {"Forward": "none"},
                },
                "TrustedSigners": {"Enabled": False, "Quantity": 0},
            }

            # Set allowed methods
            methods = config.get("methods", ["GET", "HEAD"])
            if set(methods) == {"GET", "HEAD"}:
                default_behavior["AllowedMethods"] = {
                    "Quantity": 2,
                    "Items": ["GET", "HEAD"],
                    "CachedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]},
                }
            else:
                default_behavior["AllowedMethods"] = {
                    "Quantity": len(methods),
                    "Items": methods,
                    "CachedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]},
                }

            distribution_config["DefaultCacheBehavior"] = default_behavior

        # Create distribution
        try:
            response = cloudfront.create_distribution(
                DistributionConfig=distribution_config
            )

            result = {
                "Id": response["Distribution"]["Id"],
                "DomainName": response["Distribution"]["DomainName"],
                "ARN": response["Distribution"]["ARN"],
                "Status": response["Distribution"]["Status"],
            }
            logger.info(f"Successfully created CloudFront distribution {config['name']} with ID {result['Id']} and domain {result['DomainName']}")
            return result
        except Exception as e:
            error_msg = str(e)
            if "InvalidViewerCertificate" in error_msg and "alternate domain name" in error_msg:
                # Extract domain names from config for better error message
                domains = config.get("custom_domains", [])
                cert_arn = config.get("ssl_certificate", "unknown")
                
                enhanced_msg = (
                    f"SSL certificate does not cover the alternate domain names: {', '.join(domains)}. "
                    f"Certificate ARN: {cert_arn}. "
                    f"Please ensure your SSL certificate covers all custom domains or use a wildcard certificate. "
                    f"Original error: {error_msg}"
                )
                logger.error(f"Failed to create CloudFront distribution {config['name']}: {enhanced_msg}")
                raise ValueError(enhanced_msg)
            else:
                logger.error(f"Failed to create CloudFront distribution {config['name']}: {e}")
                raise

    def _extract_cert_arn(self, ssl_cert: Any) -> Optional[str]:
        """Extract certificate ARN from various formats"""
        if isinstance(ssl_cert, dict):
            if "arn" in ssl_cert:
                return ssl_cert["arn"]
            elif "resource" in ssl_cert:
                cert_resource = ssl_cert["resource"]
                if hasattr(cert_resource, "certificate_arn"):
                    return cert_resource.certificate_arn
        return None

    def _find_ssl_certificate_for_domain(self, domain: str) -> Optional[str]:
        """Find SSL certificate ARN for a domain"""
        try:
            acm = self._get_client("acm")
            response = acm.list_certificates(CertificateStatuses=["ISSUED"])

            for cert_summary in response.get("CertificateSummaryList", []):
                cert_arn = cert_summary["CertificateArn"]
                cert_details = acm.describe_certificate(CertificateArn=cert_arn)
                certificate = cert_details["Certificate"]

                domain_name = certificate.get("DomainName", "")
                subject_alternative_names = certificate.get("SubjectAlternativeNames", [])
                all_domains = [domain_name] + subject_alternative_names

                for cert_domain in all_domains:
                    if cert_domain == domain or (
                        cert_domain.startswith("*.") and domain.endswith(cert_domain[1:])
                    ):
                        return cert_arn

            return None
        except Exception as e:
            logger.debug(f"Error finding SSL certificate for domain {domain}: {e}")
            return None

    def update_distribution(self, distribution_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update CloudFront distribution"""
        # Implementation for updating distribution
        return {"Id": distribution_id}

    def delete_distribution(self, distribution_id: str) -> None:
        """Delete CloudFront distribution"""
        # Implementation for deleting distribution
        pass

    def get_distribution(self, distribution_id: str) -> Optional[Dict[str, Any]]:
        """Get CloudFront distribution by ID"""
        try:
            cloudfront = self._get_client("cloudfront")
            response = cloudfront.get_distribution(Id=distribution_id)
            dist = response["Distribution"]
            
            return {
                "Id": dist["Id"],
                "Comment": dist.get("Comment", ""),
                "Status": dist["Status"],
                "DomainName": dist["DomainName"],
                "ARN": dist["ARN"],
                "name": dist.get("Comment", ""),
                "type": "CloudFront",
                "provider": "aws",
                "state": "active" if dist["Status"] == "Deployed" else "pending",
            }
        except Exception:
            return None

    def list_distributions(self, query: Optional[ResourceQuery] = None) -> List[Dict[str, Any]]:
        """List CloudFront distributions"""
        cloudfront = self._get_client("cloudfront")
        distributions = []

        try:
            response = cloudfront.list_distributions()
            if "DistributionList" in response and "Items" in response["DistributionList"]:
                for dist in response["DistributionList"]["Items"]:
                    distribution = {
                        "Id": dist["Id"],
                        "Comment": dist.get("Comment", ""),
                        "Status": dist["Status"],
                        "DomainName": dist["DomainName"],
                        "ARN": dist["ARN"],
                        "Tags": [],
                        "name": dist.get("Comment", ""),
                        "type": "CloudFront",
                        "provider": "aws",
                        "state": "active" if dist["Status"] == "Deployed" else "pending",
                    }
                    distributions.append(distribution)
        except Exception as e:
            logger.error(f"Error listing CloudFront distributions: {e}")

        return distributions

    def tag_distribution(self, distribution_id: str, tags: Dict[str, str]) -> None:
        """Tag CloudFront distribution"""
        # Implementation for tagging distribution
        pass

    def preview_create(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Preview CloudFront distribution creation"""
        return {
            "distribution_name": config.get("name"),
            "enabled": config.get("enabled", True),
            "custom_domains": config.get("custom_domains", []),
            "origins": config.get("origins", []),
        }

    def preview_update(self, resource_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Preview CloudFront distribution update"""
        return {
            "distribution_id": resource_id,
            "changes": list(updates.keys()),
            "requires_redeployment": any(
                key in updates for key in ["origins", "custom_domains", "ssl_certificate"]
            ),
        }

    def get_delete_warnings(self) -> List[str]:
        """Get warnings for CloudFront distribution deletion"""
        return [
            "CloudFront distribution deletion can take up to 15 minutes",
            "Distribution must be disabled before deletion",
        ]

    def estimate_cost(self, config: Dict[str, Any]) -> Dict[str, float]:
        """Estimate CloudFront distribution cost"""
        # Basic cost estimation
        return {"monthly": 10.0}  # Placeholder