"""
AWS Provider Implementation
"""

import logging
from typing import Any, Dict, List, Optional

from ...core.interfaces.provider import ProviderInterface, ProviderType, ResourceQuery
from ...core.nexus.base_resource import ResourceMetadata
from ...core.nexus.provider_registry import ProviderMetadata

from .services.cloudfront import CloudFrontService
from .services.s3 import S3Service
from .services.route53 import Route53Service
from .services.ec2 import EC2Service
from .services.acm import ACMService
from .services.route53domains import Route53DomainsService

logger = logging.getLogger(__name__)


class AWSProvider(ProviderInterface):
    """AWS provider implementation"""

    def __init__(self, config):
        self.config = config
        self._boto3_session = None
        self._clients = {}
        super().__init__(config)

        # Initialize services
        self.cloudfront = CloudFrontService(self)
        self.s3 = S3Service(self)
        self.route53 = Route53Service(self)
        self.ec2 = EC2Service(self)
        self.acm = ACMService(self)
        self.route53domains = Route53DomainsService(self)

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
        if not self._boto3_session:
            raise RuntimeError("Failed to initialize AWS boto3 session")
        if service_name not in self._clients:
            self._clients[service_name] = self._boto3_session.client(service_name)  # type: ignore
        return self._clients[service_name]

    def create_resource(
        self, resource_type: str, config: Dict[str, Any], metadata: ResourceMetadata
    ) -> Dict[str, Any]:
        """Create AWS resource"""
        if resource_type == "CloudFront":
            return self.cloudfront.create_distribution(config)
        elif resource_type == "S3":
            return self.s3.create_bucket(config)
        elif resource_type == "Route53":
            return self.route53.create_zone(config)
        elif resource_type == "DomainRegistration":
            return self.route53domains.create_domain_registration(config)
        elif resource_type == "CertificateManager":
            return self.acm.create_certificate(config)
        elif resource_type == "EC2":
            return self.ec2.create_instance(config)
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")

    # Legacy method names for backward compatibility
    def create_s3_bucket(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create S3 bucket - legacy method name for backward compatibility"""
        return self.s3.create_bucket(config)

    def update_resource(
        self, resource_id: str, resource_type: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update AWS resource"""
        if resource_type == "CloudFront":
            return self.cloudfront.update_distribution(resource_id, updates)
        elif resource_type == "S3":
            return self.s3.update_bucket(resource_id, updates)
        elif resource_type == "Route53":
            return self.route53.update_zone(resource_id, updates)
        elif resource_type == "EC2":
            return self.ec2.update_instance(resource_id, updates)
        elif resource_type == "DomainRegistration":
            return self.route53domains.update_domain_registration(resource_id, updates)
        elif resource_type == "CertificateManager":
            return self.acm.update_certificate(resource_id, updates)
        else:
            return {}

    # Direct method delegation for resource classes
    def update_domain_registration(self, domain_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate to route53domains service"""
        return self.route53domains.update_domain_registration(domain_name, config)

    def update_certificate(self, certificate_arn: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate to ACM service"""
        return self.acm.update_certificate(certificate_arn, config)

    def create_domain_registration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate to route53domains service"""
        return self.route53domains.create_domain_registration(config)

    def create_certificate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate to ACM service"""
        return self.acm.create_certificate(config)

    def update_cloudfront_distribution(self, distribution_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate to CloudFront service"""
        return self.cloudfront.update_distribution(distribution_id, config)

    def create_route53_zone(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate to Route53 service"""
        return self.route53.create_zone(config)

    def update_s3_bucket(self, bucket_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate to S3 service"""
        return self.s3.update_bucket(bucket_name, config)

    def create_cloudfront_distribution(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate to CloudFront service"""
        return self.cloudfront.create_distribution(config)

    def get_resource_state(self, metadata) -> Optional[Dict[str, Any]]:
        """Override state detection to prevent false positives for domain registrations and certificates"""
        from ...core.nexus.base_resource import ResourceMetadata
        
        # For domain registrations and certificates, we need specific logic
        # to prevent false positive matches with other resource types
        
        # If the resource name looks like a domain (contains dot), check domain registrations only
        if "." in metadata.name and not metadata.name.startswith("CLOUDFRONT"):
            # This is likely a domain registration - only check domain registrations
            try:
                domains = self.route53domains.list_domain_registrations()
                for domain in domains:
                    if domain.get("DomainName") == metadata.name:
                        return domain
            except Exception:
                pass
            # Domain not found in domain registrations, so it doesn't exist
            return None
                
        # If the resource name suggests it's a certificate, check certificates only
        if "domains" in metadata.name or "cert" in metadata.name.lower():
            # This is likely a certificate - only check certificates
            try:
                certificates = self.acm.list_certificates()
                for cert in certificates:
                    # Match by domain name since certificate name is not reliable
                    domain_to_match = metadata.name.replace("-domains", "").replace("nolimitcity-", "")
                    if cert.get("DomainName") == domain_to_match:
                        return cert
            except Exception:
                pass
            # Certificate not found, so it doesn't exist
            return None
            
        # If the resource name suggests it's a CloudFront distribution, check CloudFront only
        if "cdn-" in metadata.name or "game-" in metadata.name or "cloudfront" in metadata.name.lower():
            # This is likely a CloudFront distribution - only check CloudFront distributions
            try:
                distributions = self.cloudfront.list_distributions()
                for dist in distributions:
                    # Match by exact name from comment field (set during creation)
                    if dist.get("Comment") == metadata.name:
                        # Get full distribution details to ensure we have domain name
                        full_dist = self.cloudfront.get_distribution(dist.get("Id"))
                        return full_dist or dist
            except Exception:
                pass
            # Distribution not found, so it doesn't exist
            return None
        
        # For other resource types, fall back to default implementation
        return super().get_resource_state(metadata)

    def delete_resource(self, resource_id: str, resource_type: str) -> None:
        """Delete AWS resource"""
        if resource_type == "CloudFront":
            self.cloudfront.delete_distribution(resource_id)
        elif resource_type == "S3":
            self.s3.delete_bucket(resource_id)
        elif resource_type == "Route53":
            self.route53.delete_zone(resource_id)
        elif resource_type == "EC2":
            self.ec2.delete_instance(resource_id)

    def get_resource(
        self, resource_id: str, resource_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get AWS resource"""
        if resource_type == "CloudFront":
            return self.cloudfront.get_distribution(resource_id)
        elif resource_type == "S3":
            return self.s3.get_bucket(resource_id)
        elif resource_type == "Route53":
            return self.route53.get_zone(resource_id)
        elif resource_type == "EC2":
            return self.ec2.get_instance(resource_id)
        return None

    def list_resources(
        self, resource_type: str, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """List AWS resources"""
        try:
            if resource_type == "*":
                # List all resources when wildcard is used
                all_resources = []
                all_resources.extend(self.cloudfront.list_distributions(query))
                all_resources.extend(self.s3.list_buckets(query))
                all_resources.extend(self.route53.list_zones(query))
                all_resources.extend(self.ec2.list_instances(query))
                return all_resources
            elif resource_type == "cloudfront_distribution":
                return self.cloudfront.list_distributions(query)
            elif resource_type == "s3_bucket":
                return self.s3.list_buckets(query)
            elif resource_type == "route53_zone":
                return self.route53.list_zones(query)
            elif resource_type == "ec2_instance":
                return self.ec2.list_instances(query)
            else:
                logger.warning(f"Unknown resource type for listing: {resource_type}")
                return []
        except Exception as e:
            logger.error(f"Error listing {resource_type}: {e}")
            return []

    def tag_resource(
        self, resource_id: str, resource_type: str, tags: Dict[str, str]
    ) -> None:
        """Tag AWS resource"""
        if resource_type == "CloudFront":
            self.cloudfront.tag_distribution(resource_id, tags)
        elif resource_type == "S3":
            self.s3.tag_bucket(resource_id, tags)
        elif resource_type == "Route53":
            self.route53.tag_zone(resource_id, tags)
        elif resource_type == "EC2":
            self.ec2.tag_instance(resource_id, tags)

    async def update_resource_tags(self, resource_id: str, tags: Dict[str, str]) -> None:
        """
        Update resource tags for Pillar 1: Enhanced "Codify My Cloud" Import Tool.
        
        This method is specifically for instant tagging during import to mark
        resources as InfraDSL-managed without requiring 'infra apply'.
        """
        try:
            # Determine resource type by inspecting the resource ID format and attempting lookups
            resource_type = await self._determine_resource_type(resource_id)
            
            if resource_type == "ec2_instance":
                # Use EC2 tagging API
                try:
                    ec2_client = self._get_client("ec2")
                    
                    # Convert tags to AWS format
                    aws_tags = [{"Key": k, "Value": v} for k, v in tags.items()]
                    
                    # Apply tags to EC2 instance
                    ec2_client.create_tags(
                        Resources=[resource_id],
                        Tags=aws_tags
                    )
                    
                    logger.info(f"Successfully tagged EC2 instance {resource_id} with {len(tags)} tags")
                    
                except Exception as e:
                    logger.error(f"Failed to tag EC2 instance {resource_id}: {e}")
                    raise Exception(f"Failed to tag EC2 instance: {e}")
                    
            elif resource_type == "s3_bucket":
                # Use S3 tagging API
                try:
                    s3_client = self._get_client("s3")
                    
                    # Convert tags to S3 format
                    s3_tags = [{"Key": k, "Value": v} for k, v in tags.items()]
                    
                    # Apply tags to S3 bucket
                    s3_client.put_bucket_tagging(
                        Bucket=resource_id,
                        Tagging={"TagSet": s3_tags}
                    )
                    
                    logger.info(f"Successfully tagged S3 bucket {resource_id} with {len(tags)} tags")
                    
                except Exception as e:
                    logger.error(f"Failed to tag S3 bucket {resource_id}: {e}")
                    raise Exception(f"Failed to tag S3 bucket: {e}")
                    
            elif resource_type == "rds_instance":
                # Use RDS tagging API
                try:
                    rds_client = self._get_client("rds")
                    
                    # Convert tags to RDS format
                    rds_tags = [{"Key": k, "Value": v} for k, v in tags.items()]
                    
                    # Build RDS ARN from instance identifier
                    # Format: arn:aws:rds:region:account:db:instance-id
                    region = self.config.region or "us-east-1"
                    account_id = self._get_account_id()
                    resource_arn = f"arn:aws:rds:{region}:{account_id}:db:{resource_id}"
                    
                    # Apply tags to RDS instance
                    rds_client.add_tags_to_resource(
                        ResourceName=resource_arn,
                        Tags=rds_tags
                    )
                    
                    logger.info(f"Successfully tagged RDS instance {resource_id} with {len(tags)} tags")
                    
                except Exception as e:
                    logger.error(f"Failed to tag RDS instance {resource_id}: {e}")
                    raise Exception(f"Failed to tag RDS instance: {e}")
                    
            elif resource_type == "cloudfront_distribution":
                # Use CloudFront tagging API
                try:
                    cloudfront_client = self._get_client("cloudfront")
                    
                    # Convert tags to CloudFront format
                    cf_tags = [{"Key": k, "Value": v} for k, v in tags.items()]
                    
                    # Apply tags to CloudFront distribution
                    cloudfront_client.tag_resource(
                        Resource=f"arn:aws:cloudfront::{self._get_account_id()}:distribution/{resource_id}",
                        Tags={"Items": cf_tags}
                    )
                    
                    logger.info(f"Successfully tagged CloudFront distribution {resource_id} with {len(tags)} tags")
                    
                except Exception as e:
                    logger.error(f"Failed to tag CloudFront distribution {resource_id}: {e}")
                    raise Exception(f"Failed to tag CloudFront distribution: {e}")
                    
            else:
                logger.warning(f"Unknown resource type '{resource_type}' for {resource_id}, skipping tagging")
                
        except Exception as e:
            logger.error(f"Failed to update tags for resource {resource_id}: {e}")
            raise Exception(f"Tag update failed: {e}")

    async def _determine_resource_type(self, resource_id: str) -> str:
        """Determine the AWS resource type for a given resource ID"""
        try:
            # AWS resource IDs have predictable patterns
            if resource_id.startswith("i-"):
                return "ec2_instance"
            elif resource_id.startswith("vol-"):
                return "ebs_volume"
            elif resource_id.startswith("snap-"):
                return "ebs_snapshot"
            elif resource_id.startswith("sg-"):
                return "security_group"
            elif resource_id.startswith("subnet-"):
                return "subnet"
            elif resource_id.startswith("vpc-"):
                return "vpc"
            elif resource_id.startswith("db-") or "-db-" in resource_id:
                return "rds_instance"
            elif resource_id.startswith("E") and len(resource_id) == 14:  # CloudFront distribution ID
                return "cloudfront_distribution"
            elif not resource_id.startswith("arn:") and "." not in resource_id:
                # Likely an S3 bucket name
                return "s3_bucket"
            else:
                # Try to determine by making API calls
                return await self._determine_resource_type_by_lookup(resource_id)
                
        except Exception as e:
            logger.error(f"Error determining resource type for {resource_id}: {e}")
            return "ec2_instance"  # Default fallback

    async def _determine_resource_type_by_lookup(self, resource_id: str) -> str:
        """Determine resource type by making API calls"""
        try:
            # Try EC2 first (most common)
            try:
                ec2_client = self._get_client("ec2")
                response = ec2_client.describe_instances(InstanceIds=[resource_id])
                if response.get("Reservations"):
                    return "ec2_instance"
            except Exception:
                pass
            
            # Try S3
            try:
                s3_client = self._get_client("s3")
                s3_client.head_bucket(Bucket=resource_id)
                return "s3_bucket"
            except Exception:
                pass
            
            # Try RDS
            try:
                rds_client = self._get_client("rds")
                response = rds_client.describe_db_instances(DBInstanceIdentifier=resource_id)
                if response.get("DBInstances"):
                    return "rds_instance"
            except Exception:
                pass
            
            # Default to EC2 instance
            logger.warning(f"Could not determine resource type for {resource_id}, defaulting to ec2_instance")
            return "ec2_instance"
            
        except Exception as e:
            logger.error(f"Error in resource type lookup for {resource_id}: {e}")
            return "ec2_instance"

    def _get_account_id(self) -> str:
        """Get AWS account ID"""
        try:
            sts_client = self._get_client("sts")
            return sts_client.get_caller_identity()["Account"]
        except Exception:
            return "123456789012"  # Fallback for testing

    def estimate_cost(
        self, resource_type: str, config: Dict[str, Any]
    ) -> Dict[str, float]:
        """Estimate AWS resource cost"""
        if resource_type == "CloudFront":
            return self.cloudfront.estimate_cost(config)
        elif resource_type == "S3":
            return self.s3.estimate_cost(config)
        elif resource_type == "Route53":
            return self.route53.estimate_cost(config)
        elif resource_type == "EC2":
            return self.ec2.estimate_cost(config)
        return {"monthly": 0.0}

    def validate_config(self, resource_type: str, config: Dict[str, Any]) -> List[str]:
        """Validate AWS resource configuration"""
        if resource_type == "CloudFront":
            return self.cloudfront.validate_config(config)
        elif resource_type == "S3":
            return self.s3.validate_config(config)
        elif resource_type == "Route53":
            return self.route53.validate_config(config)
        elif resource_type == "EC2":
            return self.ec2.validate_config(config)
        return []

    def get_resource_types(self) -> List[str]:
        """Get supported resource types"""
        return ["CloudFront", "S3", "Route53", "EC2"]

    def get_regions(self) -> List[str]:
        """Get available AWS regions"""
        return ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]

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
                plan["preview"] = self.cloudfront.preview_create(config)
            elif resource_type == "S3":
                plan["preview"] = self.s3.preview_create(config)
            elif resource_type == "Route53":
                plan["preview"] = self.route53.preview_create(config)
            elif resource_type == "EC2":
                plan["preview"] = self.ec2.preview_create(config)

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
                plan["preview"] = self.cloudfront.preview_update(resource_id, updates)
            elif resource_type == "S3":
                plan["preview"] = self.s3.preview_update(resource_id, updates)
            elif resource_type == "Route53":
                plan["preview"] = self.route53.preview_update(resource_id, updates)

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
                plan["warnings"] = self.cloudfront.get_delete_warnings()
            elif resource_type == "S3":
                plan["warnings"] = self.s3.get_delete_warnings()
            elif resource_type == "Route53":
                plan["warnings"] = self.route53.get_delete_warnings()

            return plan
        except Exception as e:
            return {
                "action": "delete",
                "resource_type": resource_type,
                "resource_id": resource_id,
                "error": str(e),
            }
