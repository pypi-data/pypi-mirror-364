"""
AWS S3 Service
"""

import json
import logging
from typing import Any, Dict, List, Optional

from .base import BaseAWSService
from ....core.interfaces.provider import ResourceQuery

logger = logging.getLogger(__name__)


class S3Service(BaseAWSService):
    """AWS S3 service implementation"""
    
    def create_bucket(self, config: Dict[str, Any]) -> Dict[str, Any]:
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
        self._configure_bucket(bucket_name, config)

        result = {"BucketName": bucket_name}

        # Set website endpoint if website is configured
        if config.get("website_config"):
            result["WebsiteURL"] = (
                f"http://{bucket_name}.s3-website-{self.config.region}.amazonaws.com"
            )

        return result

    def _configure_bucket(self, bucket_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
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

        # Get existing bucket policy to merge with new CloudFront distributions
        existing_policy = None
        try:
            existing_policy_response = s3.get_bucket_policy(Bucket=bucket_name)
            existing_policy = json.loads(existing_policy_response["Policy"])
        except s3.exceptions.NoSuchBucketPolicy:
            logger.info(f"No existing bucket policy found for {bucket_name}, creating new one")
        except Exception as e:
            logger.warning(f"Could not read existing bucket policy for {bucket_name}: {e}")

        # Collect new distribution IDs to add
        new_distribution_ids = []
        for access_config in cloudfront_access:
            distribution_resource = access_config.get("distribution_resource")
            distribution_id = None

            # Check if we have a direct distribution ID string
            if access_config.get("distribution_id_string"):
                distribution_id = access_config["distribution_id_string"]
            elif distribution_resource:
                # Try to get distribution ID from the resource (this will auto-lookup if needed)
                distribution_id = getattr(distribution_resource, "distribution_id", None)
                
                # Fallback: try to get from provider data
                if not distribution_id and (
                    distribution_resource.status.provider_data
                    and "Id" in distribution_resource.status.provider_data
                ):
                    distribution_id = distribution_resource.status.provider_data["Id"]
                
                # Final fallback: try to look up the distribution by name
                if not distribution_id:
                    try:
                        cloudfront_client = self._get_client("cloudfront")
                        distributions = cloudfront_client.list_distributions()
                        for dist in distributions.get("DistributionList", {}).get("Items", []):
                            if dist.get("Comment") == distribution_resource.metadata.name:
                                distribution_id = dist.get("Id")
                                break
                    except Exception as e:
                        logger.warning(f"Could not look up CloudFront distribution {distribution_resource.metadata.name}: {e}")

            if distribution_id:
                new_distribution_ids.append(distribution_id)

        if new_distribution_ids:
            # Try to get AWS account ID for proper ARN format
            try:
                sts = self._get_client("sts")
                account_id = sts.get_caller_identity()["Account"]
            except Exception:
                account_id = "*"  # Fallback to wildcard

            # Build new CloudFront ARNs
            new_source_arns = [f"arn:aws:cloudfront::{account_id}:distribution/{dist_id}" for dist_id in new_distribution_ids]

            if existing_policy:
                # Find the CloudFront service statement and add to it
                cloudfront_statement_found = False
                for statement in existing_policy.get("Statement", []):
                    if (statement.get("Principal", {}).get("Service") == "cloudfront.amazonaws.com" and
                        "aws:SourceArn" in statement.get("Condition", {}).get("StringEquals", {})):
                        # Found existing CloudFront statement, merge the source ARNs
                        existing_arns = statement["Condition"]["StringEquals"]["aws:SourceArn"]
                        if isinstance(existing_arns, str):
                            existing_arns = [existing_arns]
                        
                        # Add new ARNs that aren't already present
                        for arn in new_source_arns:
                            if arn not in existing_arns:
                                existing_arns.append(arn)
                        
                        statement["Condition"]["StringEquals"]["aws:SourceArn"] = existing_arns
                        cloudfront_statement_found = True
                        break
                
                if not cloudfront_statement_found:
                    # Add new CloudFront statement
                    existing_policy["Statement"].append({
                        "Sid": "AllowCloudFrontServicePrincipal",
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "cloudfront.amazonaws.com"
                        },
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{bucket_name}/*",
                        "Condition": {
                            "StringEquals": {
                                "aws:SourceArn": new_source_arns
                            }
                        }
                    })
                
                bucket_policy = existing_policy
            else:
                # Create new policy
                bucket_policy = {
                    "Version": "2008-10-17",
                    "Id": "PolicyForCloudFrontPrivateContent",
                    "Statement": [{
                        "Sid": "AllowCloudFrontServicePrincipal",
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "cloudfront.amazonaws.com"
                        },
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{bucket_name}/*",
                        "Condition": {
                            "StringEquals": {
                                "aws:SourceArn": new_source_arns
                            }
                        }
                    }]
                }

            try:
                s3.put_bucket_policy(
                    Bucket=bucket_name, Policy=json.dumps(bucket_policy)
                )
                logger.info(f"Added CloudFront distributions {new_distribution_ids} to bucket policy for {bucket_name}")
            except Exception as e:
                logger.error(
                    f"Failed to apply CloudFront access policy to bucket {bucket_name}: {e}"
                )
                raise

    def update_bucket(self, bucket_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update S3 bucket configuration"""
        return self._configure_bucket(bucket_name, config)

    def delete_bucket(self, bucket_name: str) -> None:
        """Delete S3 bucket"""
        s3 = self._get_client("s3")
        try:
            s3.delete_bucket(Bucket=bucket_name)
        except Exception as e:
            logger.error(f"Failed to delete S3 bucket {bucket_name}: {e}")

    def get_bucket(self, bucket_name: str) -> Optional[Dict[str, Any]]:
        """Get S3 bucket by name"""
        try:
            s3 = self._get_client("s3")
            response = s3.head_bucket(Bucket=bucket_name)
            
            return {
                "Name": bucket_name,
                "Status": "active",
                "name": bucket_name,
                "type": "S3",
                "provider": "aws",
                "state": "active",
            }
        except Exception:
            return None

    def list_buckets(self, query: Optional[ResourceQuery] = None) -> List[Dict[str, Any]]:
        """List S3 buckets"""
        s3 = self._get_client("s3")
        buckets = []

        try:
            response = s3.list_buckets()
            if "Buckets" in response:
                for bucket in response["Buckets"]:
                    bucket_info = {
                        "Name": bucket["Name"],
                        "CreationDate": bucket["CreationDate"],
                        "Tags": [],
                        "Status": "active",
                        "name": bucket["Name"],
                        "type": "S3",
                        "provider": "aws",
                        "state": "active",
                    }
                    buckets.append(bucket_info)
        except Exception as e:
            logger.error(f"Error listing S3 buckets: {e}")

        return buckets

    def tag_bucket(self, bucket_name: str, tags: Dict[str, str]) -> None:
        """Tag S3 bucket"""
        s3 = self._get_client("s3")
        try:
            tag_set = [{"Key": key, "Value": value} for key, value in tags.items()]
            s3.put_bucket_tagging(
                Bucket=bucket_name,
                Tagging={"TagSet": tag_set}
            )
        except Exception as e:
            logger.error(f"Failed to tag S3 bucket {bucket_name}: {e}")

    def preview_create(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Preview S3 bucket creation"""
        return {
            "bucket_name": config.get("existing_bucket") or config.get("name"),
            "website_hosting": bool(config.get("website_config")),
            "versioning": config.get("versioning", False),
            "encryption": bool(config.get("encryption")),
        }

    def preview_update(self, resource_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Preview S3 bucket update"""
        return {
            "bucket_name": resource_id,
            "configuration_changes": list(updates.keys()),
        }

    def get_delete_warnings(self) -> List[str]:
        """Get warnings for S3 bucket deletion"""
        return [
            "Bucket must be empty before deletion",
            "All objects and versions will be permanently deleted",
        ]

    def estimate_cost(self, config: Dict[str, Any]) -> Dict[str, float]:
        """Estimate S3 bucket cost"""
        # Basic cost estimation
        return {"monthly": 5.0}  # Placeholder