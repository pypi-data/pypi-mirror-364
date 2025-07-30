"""
AWS Provider Implementation
"""

import json
import logging
from typing import Any, Dict, List, Optional
from ..core.interfaces.provider import ProviderInterface, ProviderType, ResourceQuery
from ..core.nexus.base_resource import ResourceMetadata
from ..core.nexus.provider_registry import ProviderMetadata

logger = logging.getLogger(__name__)

# Provider metadata
METADATA = {
    "name": "AWS",
    "provider_type": ProviderType.AWS,
    "version": "1.0.0",
    "author": "InfraDSL",
    "description": "AWS provider for CloudFront, S3, Route53, and EC2",
    "resource_types": ["CloudFront", "S3", "Route53", "EC2"],
    "regions": ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
    "required_config": [],
    "optional_config": [
        "profile",
        "access_key_id",
        "secret_access_key",
        "session_token",
    ],
}


class AWSProvider(ProviderInterface):
    """AWS provider implementation"""

    def __init__(self, config):
        self.config = config
        self._boto3_session = None
        self._clients = {}
        super().__init__(config)

    def _validate_config(self) -> None:
        """Validate AWS configuration"""
        # AWS credentials can come from many sources (env, profile, IAM role, etc.)
        # So we don't require specific credentials in config
        pass

    def _initialize(self) -> None:
        """Initialize AWS connection"""
        try:
            import boto3

            # Create session with optional credentials
            kwargs = {}
            if self.config.credentials:
                if "profile" in self.config.credentials:
                    kwargs["profile_name"] = self.config.credentials["profile"]
                if "access_key_id" in self.config.credentials:
                    kwargs["aws_access_key_id"] = self.config.credentials[
                        "access_key_id"
                    ]
                if "secret_access_key" in self.config.credentials:
                    kwargs["aws_secret_access_key"] = self.config.credentials[
                        "secret_access_key"
                    ]
                if "session_token" in self.config.credentials:
                    kwargs["aws_session_token"] = self.config.credentials[
                        "session_token"
                    ]

            # Set region
            if self.config.region:
                kwargs["region_name"] = self.config.region

            self._boto3_session = boto3.Session(**kwargs)

            # Test connection
            sts = self._get_client("sts")
            sts.get_caller_identity()

        except ImportError:
            raise Exception(
                "boto3 is required for AWS provider. Install with: pip install boto3"
            )
        except Exception as e:
            logger.error(f"Failed to initialize AWS provider: {e}")
            raise

    def _get_client(self, service_name: str):
        """Get or create AWS client"""
        if not self._boto3_session:
            self._initialize()
        if service_name not in self._clients:
            self._clients[service_name] = self._boto3_session.client(service_name)  # type: ignore
        return self._clients[service_name]

    def create_resource(
        self, resource_type: str, config: Dict[str, Any], metadata: ResourceMetadata
    ) -> Dict[str, Any]:
        """Create AWS resource"""
        if resource_type == "CloudFront":
            return self.create_cloudfront_distribution(config)
        elif resource_type == "S3":
            return self.create_s3_bucket(config)
        elif resource_type == "Route53":
            return self.create_route53_zone(config)
        elif resource_type == "DomainRegistration":
            return self.create_domain_registration(config)
        elif resource_type == "CertificateManager":
            return self.create_certificate(config)
        elif resource_type == "EC2":
            return self.create_ec2_instance(config)
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")

    def _find_ssl_certificate_for_domain(self, domain: str) -> Optional[str]:
        """Find SSL certificate ARN for a domain"""
        try:
            acm = self._get_client("acm")
            response = acm.list_certificates(CertificateStatuses=["ISSUED"])

            for cert_summary in response.get("CertificateSummaryList", []):
                cert_arn = cert_summary["CertificateArn"]

                # Get certificate details
                cert_details = acm.describe_certificate(CertificateArn=cert_arn)
                certificate = cert_details["Certificate"]

                # Check if this certificate covers the domain
                domain_name = certificate.get("DomainName", "")
                subject_alternative_names = certificate.get(
                    "SubjectAlternativeNames", []
                )

                all_domains = [domain_name] + subject_alternative_names

                # Check exact match or wildcard match
                for cert_domain in all_domains:
                    if cert_domain == domain or (
                        cert_domain.startswith("*.")
                        and domain.endswith(cert_domain[1:])
                    ):
                        return cert_arn

            return None
        except Exception as e:
            logger.debug(f"Error finding SSL certificate for domain {domain}: {e}")
            return None

    def create_cloudfront_distribution(self, config: Dict[str, Any]) -> Dict[str, Any]:
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
                # Fall back to basic config - origins will be configured below
                pass

        # Configure origins if not already from reference
        if not distribution_config.get("Origins"):
            origins = config.get("origins", [])
            if origins:
                distribution_config["Origins"] = {
                    "Quantity": len(origins),
                    "Items": origins,
                }

        # Configure custom domains (aliases) - override reference if specified
        aliases = config.get("custom_domains", [])
        if aliases:
            distribution_config["Aliases"] = {
                "Quantity": len(aliases),
                "Items": aliases,
            }

        # Configure SSL certificate - override reference if specified
        ssl_cert = config.get("ssl_certificate")
        aliases = config.get("custom_domains", [])
        auto_ssl = config.get("auto_ssl_certificate", False)

        if ssl_cert:
            # Handle different SSL certificate formats
            cert_arn = None
            if isinstance(ssl_cert, dict):
                if "arn" in ssl_cert:
                    cert_arn = ssl_cert["arn"]
                elif "resource" in ssl_cert:
                    # CertificateManager resource
                    cert_resource = ssl_cert["resource"]
                    if hasattr(cert_resource, "certificate_arn"):
                        cert_arn = cert_resource.certificate_arn
                    else:
                        logger.warning(
                            f"CertificateManager resource has no certificate_arn"
                        )

            if cert_arn:
                distribution_config["ViewerCertificate"] = {
                    "ACMCertificateArn": cert_arn,
                    "SSLSupportMethod": "sni-only",
                    "MinimumProtocolVersion": "TLSv1.2_2021",
                    "CertificateSource": "acm",
                }
            else:
                logger.warning(
                    "No valid certificate ARN found in ssl_certificate configuration"
                )
        elif aliases and auto_ssl:
            # Auto-discover SSL certificate for custom domains
            cert_arn = None
            for domain in aliases:
                cert_arn = self._find_ssl_certificate_for_domain(domain)
                if cert_arn:
                    logger.info(
                        f"Found SSL certificate for domain {domain}: {cert_arn}"
                    )
                    break

            if cert_arn:
                distribution_config["ViewerCertificate"] = {
                    "ACMCertificateArn": cert_arn,
                    "SSLSupportMethod": "sni-only",
                    "MinimumProtocolVersion": "TLSv1.2_2021",
                    "CertificateSource": "acm",
                }
            else:
                logger.warning(f"No SSL certificate found for domains: {aliases}")
                # Don't set custom domains if no SSL cert found
                distribution_config["Aliases"] = {"Quantity": 0, "Items": []}
        elif not distribution_config.get("ViewerCertificate"):
            # Only set default certificate if not copied from reference
            distribution_config["ViewerCertificate"] = {
                "CloudFrontDefaultCertificate": True,
                "MinimumProtocolVersion": "TLSv1.2_2021",
            }

        # Configure default cache behavior only if not from reference
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
        else:
            # For reference configurations, we preserve the existing origins and behaviors
            # Only update allowed methods if specified
            if config.get("methods"):
                methods = config["methods"]
                if set(methods) == {"GET", "HEAD"}:
                    distribution_config["DefaultCacheBehavior"]["AllowedMethods"] = {
                        "Quantity": 2,
                        "Items": ["GET", "HEAD"],
                        "CachedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]},
                    }
                else:
                    distribution_config["DefaultCacheBehavior"]["AllowedMethods"] = {
                        "Quantity": len(methods),
                        "Items": methods,
                        "CachedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]},
                    }

        # Create distribution
        response = cloudfront.create_distribution(
            DistributionConfig=distribution_config
        )

        return {
            "Id": response["Distribution"]["Id"],
            "DomainName": response["Distribution"]["DomainName"],
            "ARN": response["Distribution"]["ARN"],
            "Status": response["Distribution"]["Status"],
        }

    def create_s3_bucket(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create or configure S3 bucket"""
        s3 = self._get_client("s3")

        bucket_name = config.get("existing_bucket") or config["name"]

        # If not using existing bucket, create it
        if not config.get("existing_bucket"):
            try:
                if self.config.region and self.config.region != "us-east-1":
                    s3.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={
                            "LocationConstraint": self.config.region
                        },
                    )
                else:
                    s3.create_bucket(Bucket=bucket_name)
            except Exception as e:
                if "BucketAlreadyExists" not in str(e):
                    raise

        # Configure bucket
        self.configure_s3_bucket(bucket_name, config)

        result = {"BucketName": bucket_name}

        # Set website endpoint if website is configured
        if config.get("website_config"):
            result["WebsiteURL"] = (
                f"http://{bucket_name}.s3-website-{self.config.region}.amazonaws.com"
            )

        return result

    def configure_s3_bucket(
        self, bucket_name: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure existing S3 bucket"""
        s3 = self._get_client("s3")

        # Configure website hosting
        website_config = config.get("website_config")
        if website_config:
            s3.put_bucket_website(
                Bucket=bucket_name, WebsiteConfiguration=website_config
            )

        # Configure CORS
        cors_config = config.get("cors_config")
        if cors_config:
            s3.put_bucket_cors(Bucket=bucket_name, CORSConfiguration=cors_config)

        # Configure bucket policy
        policy = config.get("policy")
        if policy:
            s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy))

        # Configure CloudFront access
        cloudfront_access = config.get("cloudfront_access", [])
        if cloudfront_access:
            self._configure_cloudfront_access(bucket_name, cloudfront_access)

        # Configure public access block
        if not config.get("public_access_block", True):
            s3.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    "BlockPublicAcls": False,
                    "IgnorePublicAcls": False,
                    "BlockPublicPolicy": False,
                    "RestrictPublicBuckets": False,
                },
            )

        # Configure versioning
        if config.get("versioning"):
            s3.put_bucket_versioning(
                Bucket=bucket_name, VersioningConfiguration={"Status": "Enabled"}
            )

        # Configure encryption
        encryption = config.get("encryption")
        if encryption:
            s3.put_bucket_encryption(
                Bucket=bucket_name, ServerSideEncryptionConfiguration=encryption
            )

        # Configure lifecycle
        lifecycle_rules = config.get("lifecycle_rules", [])
        if lifecycle_rules:
            s3.put_bucket_lifecycle_configuration(
                Bucket=bucket_name, LifecycleConfiguration={"Rules": lifecycle_rules}
            )

        # Configure logging
        logging_config = config.get("logging")
        if logging_config:
            s3.put_bucket_logging(
                Bucket=bucket_name,
                BucketLoggingStatus={
                    "LoggingEnabled": {
                        "TargetBucket": logging_config["TargetBucket"],
                        "TargetPrefix": logging_config.get("TargetPrefix", ""),
                    }
                },
            )

        return {"BucketName": bucket_name}

    def _configure_cloudfront_access(
        self, bucket_name: str, cloudfront_access: List[Dict[str, Any]]
    ) -> None:
        """Configure CloudFront access for S3 bucket"""
        s3 = self._get_client("s3")

        # Generate bucket policy for CloudFront access
        policy_statements = []

        for access_config in cloudfront_access:
            distribution_resource = access_config.get("distribution_resource")

            if distribution_resource:
                # Get the actual distribution ID/ARN from the created CloudFront resource
                distribution_id = None
                distribution_arn = None

                # Check if the CloudFront resource has been created and has provider data
                if (
                    distribution_resource.status.provider_data
                    and "Id" in distribution_resource.status.provider_data
                ):
                    distribution_id = distribution_resource.status.provider_data["Id"]
                    distribution_arn = distribution_resource.status.provider_data.get(
                        "ARN"
                    )

                if distribution_id:
                    # Create policy statement for CloudFront access
                    policy_statements.append(
                        {
                            "Sid": f"AllowCloudFrontAccess{distribution_id}",
                            "Effect": "Allow",
                            "Principal": {
                                "AWS": f"arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity {distribution_id}"
                            },
                            "Action": ["s3:GetObject"],
                            "Resource": f"arn:aws:s3:::{bucket_name}/*",
                        }
                    )
                else:
                    logger.warning(
                        f"CloudFront distribution {distribution_resource.metadata.name} has no ID - skipping bucket policy configuration"
                    )

        if policy_statements:
            # Create and apply bucket policy
            bucket_policy = {"Version": "2012-10-17", "Statement": policy_statements}

            try:
                s3.put_bucket_policy(
                    Bucket=bucket_name, Policy=json.dumps(bucket_policy)
                )
                logger.info(f"Applied CloudFront access policy to bucket {bucket_name}")
            except Exception as e:
                logger.error(
                    f"Failed to apply CloudFront access policy to bucket {bucket_name}: {e}"
                )
                raise

    def create_route53_zone(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create or configure Route53 zone"""
        route53 = self._get_client("route53")

        zone_name = config.get("existing_zone") or config["name"]

        # Get hosted zone ID
        hosted_zone_id = None
        if config.get("existing_zone"):
            # Find existing zone
            zones = route53.list_hosted_zones()["HostedZones"]
            for zone in zones:
                if zone["Name"].rstrip(".") == zone_name.rstrip("."):
                    hosted_zone_id = zone["Id"].split("/")[-1]
                    break

        if not hosted_zone_id:
            # Create new zone
            response = route53.create_hosted_zone(
                Name=zone_name, CallerReference=f"infradsl-{config['name']}"
            )
            hosted_zone_id = response["HostedZone"]["Id"].split("/")[-1]

        # Create records
        records = config.get("records", [])
        if records:
            changes = []
            for record in records:
                # Resolve CloudFront resource objects to domain names
                if "AliasTarget" in record and "DNSName" in record["AliasTarget"]:
                    # Handle A alias records (apex domain)
                    dns_name = record["AliasTarget"]["DNSName"]
                    if hasattr(dns_name, "domain_name"):
                        actual_domain_name = dns_name.domain_name
                        if actual_domain_name:
                            record["AliasTarget"]["DNSName"] = actual_domain_name
                        else:
                            logger.error(
                                f"CloudFront resource {dns_name.metadata.name} has no domain_name. Was it created successfully?"
                            )
                            continue
                elif "ResourceRecords" in record:
                    # Handle CNAME records
                    skip_record = False
                    for resource_record in record["ResourceRecords"]:
                        if "Value" in resource_record:
                            value = resource_record["Value"]
                            if hasattr(value, "domain_name"):
                                actual_domain_name = value.domain_name
                                if actual_domain_name:
                                    resource_record["Value"] = actual_domain_name
                                else:
                                    logger.error(
                                        f"CloudFront resource {value.metadata.name} has no domain_name. Was it created successfully?"
                                    )
                                    skip_record = True
                                    break

                    if skip_record:
                        continue

                change = {"Action": "UPSERT", "ResourceRecordSet": record}
                changes.append(change)

            if changes:
                route53.change_resource_record_sets(
                    HostedZoneId=hosted_zone_id, ChangeBatch={"Changes": changes}
                )

        return {"HostedZoneId": hosted_zone_id}

    def create_ec2_instance(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create EC2 instance (placeholder)"""
        # This would implement EC2 instance creation
        # For now, return placeholder
        return {"InstanceId": "i-placeholder"}

    def update_resource(
        self, resource_id: str, resource_type: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update AWS resource"""
        if resource_type == "CloudFront":
            return self.update_cloudfront_distribution(resource_id, updates)
        elif resource_type == "S3":
            return self.update_s3_bucket(resource_id, updates)
        elif resource_type == "Route53":
            return self.update_route53_zone(resource_id, updates)
        elif resource_type == "DomainRegistration":
            return self.update_domain_registration(resource_id, updates)
        elif resource_type == "CertificateManager":
            return self.update_certificate(resource_id, updates)
        elif resource_type == "EC2":
            # EC2 updates are complex, would need specific implementation
            logger.warning(f"EC2 instance updates not yet implemented")
            return {}
        else:
            raise ValueError(f"Unsupported resource type for update: {resource_type}")

    def delete_resource(self, resource_id: str, resource_type: str) -> None:
        """Delete AWS resource"""
        # Implementation would depend on resource type
        pass

    def get_resource(
        self, resource_id: str, resource_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get AWS resource"""
        # Implementation would depend on resource type
        return None

    def list_resources(
        self, resource_type: str, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """List AWS resources"""
        try:
            if resource_type == "*":
                # List all resources when wildcard is used
                all_resources = []
                all_resources.extend(self._list_cloudfront_distributions(query))
                all_resources.extend(self._list_s3_buckets(query))
                all_resources.extend(self._list_route53_zones(query))
                all_resources.extend(self._list_ec2_instances(query))
                # Don't include domain registrations and certificates in wildcard queries
                # This prevents false positive matches during state detection
                logger.debug(f"Wildcard resource listing returned {len(all_resources)} resources")
                return all_resources
            elif resource_type == "cloudfront_distribution":
                return self._list_cloudfront_distributions(query)
            elif resource_type == "s3_bucket":
                return self._list_s3_buckets(query)
            elif resource_type == "route53_zone":
                return self._list_route53_zones(query)
            elif resource_type == "ec2_instance":
                return self._list_ec2_instances(query)
            elif resource_type == "domain_registration":
                return self._list_domain_registrations(query)
            elif resource_type == "certificate_manager":
                return self._list_certificates(query)
            else:
                logger.warning(f"Unknown resource type for listing: {resource_type}")
                return []
        except Exception as e:
            logger.error(f"Error listing {resource_type}: {e}")
            return []

    def _list_cloudfront_distributions(
        self, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """List CloudFront distributions"""
        cloudfront = self._get_client("cloudfront")
        distributions = []

        try:
            response = cloudfront.list_distributions()
            if (
                "DistributionList" in response
                and "Items" in response["DistributionList"]
            ):
                for dist in response["DistributionList"]["Items"]:
                    # Skip tag fetching for performance - tags can be fetched separately if needed
                    distribution = {
                        "Id": dist["Id"],
                        "Comment": dist.get("Comment", ""),
                        "Status": dist["Status"],
                        "DomainName": dist["DomainName"],
                        "ARN": dist["ARN"],
                        "Tags": [],  # Skip tags for performance
                        "name": dist.get("Comment", ""),  # Use comment as name
                        "type": "CloudFront",  # Add type for state tracking
                        "provider": "aws",  # Add provider for state tracking
                        "state": (
                            "active" if dist["Status"] == "Deployed" else "pending"
                        ),
                    }
                    distributions.append(distribution)
        except Exception as e:
            logger.error(f"Error listing CloudFront distributions: {e}")

        return distributions

    def _list_s3_buckets(
        self, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """List S3 buckets"""
        s3 = self._get_client("s3")
        buckets = []

        try:
            response = s3.list_buckets()
            if "Buckets" in response:
                for bucket in response["Buckets"]:
                    # Skip tag fetching for performance
                    bucket_info = {
                        "Name": bucket["Name"],
                        "CreationDate": bucket["CreationDate"],
                        "Tags": [],  # Skip tags for performance
                        "Status": "active",  # S3 buckets are always active if they exist
                        "name": bucket["Name"],
                        "type": "S3",  # Add type for state tracking
                        "provider": "aws",  # Add provider for state tracking
                        "state": "active",
                    }
                    buckets.append(bucket_info)
        except Exception as e:
            logger.error(f"Error listing S3 buckets: {e}")

        return buckets

    def _list_route53_zones(
        self, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """List Route53 hosted zones"""
        route53 = self._get_client("route53")
        zones = []

        try:
            response = route53.list_hosted_zones()
            if "HostedZones" in response:
                for zone in response["HostedZones"]:
                    # Skip tag fetching for performance
                    zone_info = {
                        "Id": zone["Id"],
                        "Name": zone["Name"].rstrip("."),
                        "Status": "active",  # Route53 zones are always active if they exist
                        "Tags": [],  # Skip tags for performance
                        "ResourceRecordSetCount": zone.get("ResourceRecordSetCount", 0),
                        "name": zone["Name"].rstrip("."),
                        "type": "Route53",  # Add type for state tracking
                        "provider": "aws",  # Add provider for state tracking
                        "state": "active",
                    }
                    zones.append(zone_info)
        except Exception as e:
            logger.error(f"Error listing Route53 zones: {e}")

        return zones

    def _list_ec2_instances(
        self, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """List EC2 instances"""
        ec2 = self._get_client("ec2")
        instances = []

        try:
            response = ec2.describe_instances()
            if "Reservations" in response:
                for reservation in response["Reservations"]:
                    for instance in reservation["Instances"]:
                        # Get tags
                        tags = []
                        if "Tags" in instance:
                            tags = [
                                f"{tag['Key']}:{tag['Value']}"
                                for tag in instance["Tags"]
                            ]

                        # Get instance name from tags
                        name = instance["InstanceId"]
                        for tag in instance.get("Tags", []):
                            if tag["Key"] == "Name":
                                name = tag["Value"]
                                break

                        instance_info = {
                            "InstanceId": instance["InstanceId"],
                            "State": instance["State"],
                            "InstanceType": instance["InstanceType"],
                            "Tags": tags,
                            "name": name,
                        }
                        instances.append(instance_info)
        except Exception as e:
            logger.error(f"Error listing EC2 instances: {e}")

        return instances

    def _list_domain_registrations(
        self, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """List Route53 domain registrations"""
        route53domains = self._get_client("route53domains", region="us-east-1")
        domains = []

        try:
            response = route53domains.list_domains()
            if "Domains" in response:
                for domain in response["Domains"]:
                    domain_info = {
                        "DomainName": domain["DomainName"],
                        "Status": domain.get("StatusList", ["UNKNOWN"])[0] if domain.get("StatusList") else "UNKNOWN",
                        "AutoRenew": domain.get("AutoRenew", False),
                        "ExpirationDate": domain.get("Expiry"),
                        "Name": domain["DomainName"],  # For compatibility with mapping
                        "Tags": [],  # Route53 domains don't support tags in list operation
                    }

                    # Apply query filter if provided
                    if query and not self._matches_query(domain_info, query):
                        continue

                    domains.append(domain_info)

        except Exception as e:
            logger.debug(f"Error listing domain registrations: {e}")

        return domains

    def _list_certificates(
        self, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """List ACM certificates"""
        acm = self._get_client("acm", region="us-east-1")
        certificates = []

        try:
            response = acm.list_certificates()
            if "CertificateSummaryList" in response:
                for cert_summary in response["CertificateSummaryList"]:
                    # Get detailed certificate information
                    cert_arn = cert_summary["CertificateArn"]
                    try:
                        cert_detail = acm.describe_certificate(CertificateArn=cert_arn)["Certificate"]
                        
                        cert_info = {
                            "CertificateArn": cert_arn,
                            "DomainName": cert_detail["DomainName"],
                            "Status": cert_detail["Status"],
                            "Name": cert_detail["DomainName"],  # For compatibility with mapping
                            "SubjectAlternativeNames": cert_detail.get("SubjectAlternativeNames", []),
                            "ValidationMethod": cert_detail.get("ValidationMethod"),
                            "IssuedAt": cert_detail.get("IssuedAt"),
                            "NotAfter": cert_detail.get("NotAfter"),
                            "Tags": [],  # Will be populated if needed
                        }

                        # Apply query filter if provided
                        if query and not self._matches_query(cert_info, query):
                            continue

                        certificates.append(cert_info)
                    except Exception as e:
                        logger.debug(f"Error getting certificate details for {cert_arn}: {e}")

        except Exception as e:
            logger.debug(f"Error listing certificates: {e}")

        return certificates

    def _matches_query(self, resource_data: Dict[str, Any], query: ResourceQuery) -> bool:
        """Check if resource matches query filters"""
        if not query:
            return True
            
        # Check tag filters
        if query.tags:
            resource_tags = resource_data.get("Tags", [])
            
            # Handle different tag formats (list vs dict)
            if isinstance(resource_tags, list):
                # Convert list format to dict for easier comparison
                tag_dict = {}
                for tag in resource_tags:
                    if isinstance(tag, dict) and "Key" in tag and "Value" in tag:
                        tag_dict[tag["Key"]] = tag["Value"]
                    elif isinstance(tag, str) and ":" in tag:
                        key, value = tag.split(":", 1)
                        tag_dict[key] = value
                resource_tags = tag_dict
            
            # Check if all query tags match
            for key, value in query.tags.items():
                if resource_tags.get(key) != value:
                    return False
        
        # Check name filter
        if query.name_filter:
            name = resource_data.get("Name", "")
            if query.name_filter not in name:
                return False
                
        return True

    def get_resource_state(self, metadata: ResourceMetadata) -> Optional[Dict[str, Any]]:
        """Override state detection to prevent false positives for new resource types"""
        # For domain registrations and certificates, we need to be very specific
        # because the generic tag-based approach can cause false positives
        
        # If the resource name matches domain patterns, check domain registrations only
        if "." in metadata.name and not metadata.name.startswith("CLOUDFRONT"):
            # This might be a domain, check domain registrations first
            try:
                domains = self._list_domain_registrations()
                for domain in domains:
                    if domain.get("DomainName") == metadata.name:
                        return domain
            except Exception:
                pass
                
        # If the resource name suggests it's a certificate, check certificates only
        if "domains" in metadata.name or "cert" in metadata.name.lower():
            try:
                certificates = self._list_certificates()
                for cert in certificates:
                    # Match by domain name since certificate name is not reliable
                    if cert.get("DomainName") == metadata.name.replace("-domains", "").replace("nolimitcity-", ""):
                        return cert
            except Exception:
                pass
        
        # Fall back to default implementation for other resource types
        return super().get_resource_state(metadata)

    def tag_resource(
        self, resource_id: str, resource_type: str, tags: Dict[str, str]
    ) -> None:
        """Tag AWS resource"""
        # Implementation would depend on resource type
        pass

    def estimate_cost(
        self, resource_type: str, config: Dict[str, Any]
    ) -> Dict[str, float]:
        """Estimate AWS resource cost"""
        # Placeholder implementation
        return {"monthly": 0.0}

    def validate_config(self, resource_type: str, config: Dict[str, Any]) -> List[str]:
        """Validate AWS resource configuration"""
        # Placeholder implementation
        return []

    def get_resource_types(self) -> List[str]:
        """Get supported resource types"""
        return ["CloudFront", "S3", "Route53", "EC2"]

    def get_regions(self) -> List[str]:
        """Get available AWS regions"""
        return ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]

    # Resource-specific methods for direct use by resources
    def update_cloudfront_distribution(
        self, name: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update CloudFront distribution"""
        # Implementation for updating distribution
        return {}

    def delete_cloudfront_distribution(self, name: str) -> None:
        """Delete CloudFront distribution"""
        # Implementation for deleting distribution
        pass

    def update_s3_bucket(
        self, bucket_name: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update S3 bucket configuration"""
        return self.configure_s3_bucket(bucket_name, config)

    def delete_s3_bucket(self, bucket_name: str) -> None:
        """Delete S3 bucket"""
        s3 = self._get_client("s3")
        # Empty bucket first
        try:
            s3.delete_bucket(Bucket=bucket_name)
        except Exception as e:
            logger.error(f"Failed to delete S3 bucket {bucket_name}: {e}")

    def update_route53_zone(
        self, zone_name: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update Route53 zone"""
        return self.create_route53_zone(config)

    def delete_route53_zone(self, zone_name: str) -> None:
        """Delete Route53 zone"""
        # Implementation for deleting zone
        pass

    def create_domain_registration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create domain registration"""
        route53domains = self._get_client("route53domains")

        domain_name = config["domain_name"]
        contact_info = config["contact_info"]
        duration = config["duration_in_years"]

        # Convert contact info to AWS format
        aws_contact = {
            "FirstName": contact_info.first_name,
            "LastName": contact_info.last_name,
            "ContactType": "PERSON" if not contact_info.organization else "COMPANY",
            "OrganizationName": contact_info.organization or "",
            "AddressLine1": contact_info.address,
            "City": contact_info.city,
            "State": contact_info.state or "",
            "CountryCode": contact_info.country,
            "ZipCode": contact_info.zip_code,
            "PhoneNumber": contact_info.phone,
            "Email": contact_info.email,
        }

        # Use same contact for all types unless specified
        admin_contact = aws_contact.copy()
        tech_contact = aws_contact.copy()
        billing_contact = aws_contact.copy()

        # Override with specific contacts if provided
        if hasattr(config["admin_contact"], "first_name"):
            admin_contact = self._convert_contact_to_aws(config["admin_contact"])
        if hasattr(config["tech_contact"], "first_name"):
            tech_contact = self._convert_contact_to_aws(config["tech_contact"])
        if hasattr(config["billing_contact"], "first_name"):
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
                "ExpirationDate": None,  # Will be set after registration completes
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
        return {
            "FirstName": contact_info.first_name,
            "LastName": contact_info.last_name,
            "ContactType": "PERSON" if not contact_info.organization else "COMPANY",
            "OrganizationName": contact_info.organization or "",
            "AddressLine1": contact_info.address,
            "City": contact_info.city,
            "State": contact_info.state or "",
            "CountryCode": contact_info.country,
            "ZipCode": contact_info.zip_code,
            "PhoneNumber": contact_info.phone,
            "Email": contact_info.email,
        }

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

        # Get name servers
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

    def update_domain_registration(
        self, domain_name: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update domain registration"""
        # Implementation for updating domain registration
        return {"DomainName": domain_name}

    def delete_domain_registration(self, domain_name: str) -> None:
        """Delete domain registration"""
        # Note: Domain deletion is usually not immediate and has restrictions
        # Implementation would depend on specific requirements
        pass

    def create_certificate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create SSL certificate"""
        # Use us-east-1 for CloudFront compatibility if specified
        region = (
            "us-east-1"
            if config.get("cloudfront_compatible", False)
            else self.config.region
        )
        acm = self._boto3_session.client("acm", region_name=region)  # type: ignore

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

        # Add domain validation options for email validation
        if validation_method == "EMAIL":
            validation_emails = config.get("validation_emails", [])
            if validation_emails:
                certificate_request["DomainValidationOptions"] = [
                    {
                        "DomainName": domain_name,
                        "ValidationDomain": config.get(
                            "validation_domain", domain_name
                        ),
                    }
                ]

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

    def wait_for_certificate_validation(
        self, certificate_arn: str, timeout: int = 300
    ) -> bool:
        """Wait for certificate validation to complete"""
        acm = self._get_client("acm")

        try:
            waiter = acm.get_waiter("certificate_validated")
            waiter.wait(
                CertificateArn=certificate_arn,
                WaiterConfig={"Delay": 30, "MaxAttempts": timeout // 30},
            )
            return True

        except Exception as e:
            logger.error(
                f"Certificate validation timeout or failed for {certificate_arn}: {e}"
            )
            return False

    def auto_validate_certificate_dns(
        self, certificate_arn: str, route53_zone_id: Optional[str] = None
    ) -> None:
        """Automatically create DNS validation records in Route53"""
        acm = self._get_client("acm")
        route53 = self._get_client("route53")

        try:
            # Get certificate details
            response = acm.describe_certificate(CertificateArn=certificate_arn)
            certificate = response["Certificate"]

            # Create DNS validation records
            for domain_validation in certificate.get("DomainValidationOptions", []):
                if "ResourceRecord" in domain_validation:
                    record = domain_validation["ResourceRecord"]
                    domain_name = domain_validation["DomainName"]

                    # Find hosted zone if not provided
                    zone_id = route53_zone_id
                    if not zone_id:
                        zone_id = self._find_hosted_zone_for_domain(domain_name)

                    if zone_id:
                        # Create validation record
                        route53.change_resource_record_sets(
                            HostedZoneId=zone_id,
                            ChangeBatch={
                                "Changes": [
                                    {
                                        "Action": "UPSERT",
                                        "ResourceRecordSet": {
                                            "Name": record["Name"],
                                            "Type": record["Type"],
                                            "TTL": 300,
                                            "ResourceRecords": [
                                                {"Value": record["Value"]}
                                            ],
                                        },
                                    }
                                ]
                            },
                        )
                        logger.info(f"Created DNS validation record for {domain_name}")
                    else:
                        logger.warning(f"No hosted zone found for domain {domain_name}")

        except Exception as e:
            logger.error(f"Failed to auto-validate certificate {certificate_arn}: {e}")
            raise

    def _find_hosted_zone_for_domain(self, domain_name: str) -> Optional[str]:
        """Find Route53 hosted zone for domain"""
        route53 = self._get_client("route53")

        try:
            response = route53.list_hosted_zones()

            # Look for exact match or parent domain match
            for zone in response["HostedZones"]:
                zone_name = zone["Name"].rstrip(".")
                if domain_name == zone_name or domain_name.endswith(f".{zone_name}"):
                    return zone["Id"].split("/")[-1]

            return None

        except Exception as e:
            logger.error(f"Failed to find hosted zone for domain {domain_name}: {e}")
            return None

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

    def discover_resources(
        self, resource_type: str, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """Discover resources in AWS using broader discovery mechanisms"""
        return self.list_resources(resource_type, query)

    def plan_create(
        self, resource_type: str, config: Dict[str, Any], metadata: ResourceMetadata
    ) -> Dict[str, Any]:
        """Preview the creation of an AWS resource"""
        try:
            # Return a plan showing what would be created
            plan = {
                "action": "create",
                "resource_type": resource_type,
                "name": config.get("name", "unnamed"),
                "provider": "aws",
                "config": config,
                "metadata": {
                    "id": metadata.id,
                    "name": metadata.name,
                    "project": metadata.project,
                    "environment": metadata.environment,
                },
                "estimated_cost": self.estimate_cost(resource_type, config),
            }

            # Add resource-specific preview information
            if resource_type == "CloudFront":
                plan["preview"] = {
                    "distribution_name": config.get("name"),
                    "enabled": config.get("enabled", True),
                    "custom_domains": config.get("custom_domains", []),
                    "origins": config.get("origins", []),
                }
            elif resource_type == "S3":
                plan["preview"] = {
                    "bucket_name": config.get("existing_bucket") or config.get("name"),
                    "website_hosting": bool(config.get("website_config")),
                    "versioning": config.get("versioning", False),
                    "encryption": bool(config.get("encryption")),
                }
            elif resource_type == "Route53":
                plan["preview"] = {
                    "zone_name": config.get("existing_zone") or config.get("name"),
                    "records_count": len(config.get("records", [])),
                }
            elif resource_type == "EC2":
                plan["preview"] = {
                    "instance_type": config.get("instance_type", "t2.micro"),
                    "ami": config.get("ami"),
                    "security_groups": config.get("security_groups", []),
                }

            return plan
        except Exception as e:
            return {
                "action": "create",
                "resource_type": resource_type,
                "error": str(e),
            }

    def plan_update(
        self, resource_id: str, resource_type: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Preview the update of an AWS resource"""
        try:
            # Get current resource state
            current_resource = self.get_resource(resource_id, resource_type)
            
            plan = {
                "action": "update",
                "resource_type": resource_type,
                "resource_id": resource_id,
                "provider": "aws",
                "changes": updates,
                "current_state": current_resource,
            }

            # Add resource-specific update preview
            if resource_type == "CloudFront":
                plan["preview"] = {
                    "distribution_id": resource_id,
                    "changes": list(updates.keys()),
                    "requires_redeployment": any(
                        key in updates for key in ["origins", "custom_domains", "ssl_certificate"]
                    ),
                }
            elif resource_type == "S3":
                plan["preview"] = {
                    "bucket_name": resource_id,
                    "configuration_changes": list(updates.keys()),
                }
            elif resource_type == "Route53":
                plan["preview"] = {
                    "zone_id": resource_id,
                    "records_changes": updates.get("records", []),
                }

            return plan
        except Exception as e:
            return {
                "action": "update",
                "resource_type": resource_type,
                "resource_id": resource_id,
                "error": str(e),
            }

    def plan_delete(self, resource_id: str, resource_type: str) -> Dict[str, Any]:
        """Preview the deletion of an AWS resource"""
        try:
            # Get current resource state
            current_resource = self.get_resource(resource_id, resource_type)
            
            plan = {
                "action": "delete",
                "resource_type": resource_type,
                "resource_id": resource_id,
                "provider": "aws",
                "current_state": current_resource,
            }

            # Add resource-specific deletion warnings
            if resource_type == "CloudFront":
                plan["warnings"] = [
                    "CloudFront distribution deletion can take up to 15 minutes",
                    "Distribution must be disabled before deletion",
                ]
            elif resource_type == "S3":
                plan["warnings"] = [
                    "Bucket must be empty before deletion",
                    "All objects and versions will be permanently deleted",
                ]
            elif resource_type == "Route53":
                plan["warnings"] = [
                    "All DNS records in the zone will be deleted",
                    "Domain resolution will stop working",
                ]

            return plan
        except Exception as e:
            return {
                "action": "delete",
                "resource_type": resource_type,
                "resource_id": resource_id,
                "error": str(e),
            }
