"""
AWS State Discovery Implementation

This module provides AWS-specific resource discovery for state management.
"""

import logging
import boto3
from typing import Dict, List, Any, Optional
from botocore.exceptions import ClientError, NoCredentialsError

from ..interfaces.state_discoverer import StateDiscoverer
from ...nexus.base_resource import ResourceMetadata
from ...interfaces.provider import ProviderInterface

logger = logging.getLogger(__name__)


class AWSStateDiscoverer(StateDiscoverer):
    """AWS implementation of state discovery"""

    def __init__(self, provider: ProviderInterface):
        super().__init__(provider)
        self.region = provider.config.region or "us-east-1"
        self._ec2_client = None
        self._s3_client = None
        self._rds_client = None

    @property
    def ec2_client(self):
        """Lazy initialization of EC2 client"""
        if self._ec2_client is None:
            self._ec2_client = boto3.client("ec2", region_name=self.region)
        return self._ec2_client

    @property
    def s3_client(self):
        """Lazy initialization of S3 client"""
        if self._s3_client is None:
            self._s3_client = boto3.client("s3", region_name=self.region)
        return self._s3_client

    @property
    def rds_client(self):
        """Lazy initialization of RDS client"""
        if self._rds_client is None:
            self._rds_client = boto3.client("rds", region_name=self.region)
        return self._rds_client

    def discover_resources(
        self, include_unmanaged: bool = False
    ) -> List[Dict[str, Any]]:
        """Discover AWS resources"""
        try:
            resources = []

            # Discover EC2 instances
            resources.extend(self._discover_ec2_instances(include_unmanaged))

            # Discover S3 buckets
            resources.extend(self._discover_s3_buckets(include_unmanaged))

            # Discover RDS instances
            resources.extend(self._discover_rds_instances(include_unmanaged))

            return resources

        except NoCredentialsError:
            logger.error("AWS credentials not found. Please configure AWS credentials.")
            return []
        except Exception as e:
            logger.error(f"Error discovering AWS resources: {e}")
            return []

    def _discover_ec2_instances(
        self, include_unmanaged: bool = False
    ) -> List[Dict[str, Any]]:
        """Discover EC2 instances"""
        try:
            response = self.ec2_client.describe_instances()
            resources = []

            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    # Skip terminated instances
                    if instance["State"]["Name"] == "terminated":
                        continue

                    # Extract tags
                    tags = {
                        tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])
                    }

                    # For import mode, include all resources
                    # For state mode, only include managed resources
                    if not include_unmanaged and "infradsl.id" not in tags:
                        continue

                    # Filter by project if specified - get from provider config
                    if (
                        hasattr(self.provider.config, "project")
                        and self.provider.config.project
                    ):
                        if tags.get("infradsl.project") != self.provider.config.project:
                            continue

                    # Build resource info
                    resource = {
                        "id": tags["infradsl.id"],
                        "name": tags.get("infradsl.name", instance["InstanceId"]),
                        "type": "instance",
                        "provider": "aws",
                        "cloud_id": instance["InstanceId"],
                        "region": self.region,
                        "project": tags.get("infradsl.project", "default"),
                        "environment": tags.get("infradsl.environment", "default"),
                        "state": instance["State"]["Name"],
                        "tags": tags,
                        "configuration": {
                            "instance_type": instance["InstanceType"],
                            "image_id": instance["ImageId"],
                            "key_name": instance.get("KeyName"),
                            "security_groups": [
                                sg["GroupId"]
                                for sg in instance.get("SecurityGroups", [])
                            ],
                            "subnet_id": instance.get("SubnetId"),
                            "availability_zone": instance.get("Placement", {}).get(
                                "AvailabilityZone"
                            ),
                            "public_ip": instance.get("PublicIpAddress"),
                            "private_ip": instance.get("PrivateIpAddress"),
                            "launch_time": (
                                instance.get("LaunchTime").isoformat()
                                if instance.get("LaunchTime")
                                else None
                            ),
                            "state": instance["State"]["Name"],
                            "monitoring": instance.get("Monitoring", {}).get("State"),
                            "platform": instance.get("Platform"),
                            "vpc_id": instance.get("VpcId"),
                            "architecture": instance.get("Architecture"),
                            "hypervisor": instance.get("Hypervisor"),
                            "virtualization_type": instance.get("VirtualizationType"),
                            "instance_lifecycle": instance.get("InstanceLifecycle"),
                            "spot_instance_request_id": instance.get(
                                "SpotInstanceRequestId"
                            ),
                            "tenancy": instance.get("Placement", {}).get("Tenancy"),
                            "host_id": instance.get("Placement", {}).get("HostId"),
                            "affinity": instance.get("Placement", {}).get("Affinity"),
                            "block_device_mappings": [
                                {
                                    "device_name": bdm["DeviceName"],
                                    "volume_id": bdm.get("Ebs", {}).get("VolumeId"),
                                    "volume_size": bdm.get("Ebs", {}).get("VolumeSize"),
                                    "volume_type": bdm.get("Ebs", {}).get("VolumeType"),
                                    "encrypted": bdm.get("Ebs", {}).get("Encrypted"),
                                    "delete_on_termination": bdm.get("Ebs", {}).get(
                                        "DeleteOnTermination"
                                    ),
                                }
                                for bdm in instance.get("BlockDeviceMappings", [])
                            ],
                        },
                        "created_at": (
                            instance.get("LaunchTime").isoformat()
                            if instance.get("LaunchTime")
                            else None
                        ),
                        "updated_at": None,  # AWS doesn't provide last modified time
                        "managed": True,
                        "fingerprint": self._calculate_ec2_fingerprint(instance),
                    }

                    resources.append(resource)

            return resources

        except ClientError as e:
            logger.error(f"Error discovering EC2 instances: {e}")
            return []

    def _discover_s3_buckets(
        self, include_unmanaged: bool = False
    ) -> List[Dict[str, Any]]:
        """Discover S3 buckets"""
        try:
            response = self.s3_client.list_buckets()
            resources = []

            for bucket in response["Buckets"]:
                bucket_name = bucket["Name"]

                try:
                    # Get bucket tags
                    tags_response = self.s3_client.get_bucket_tagging(
                        Bucket=bucket_name
                    )
                    tags = {tag["Key"]: tag["Value"] for tag in tags_response["TagSet"]}
                except ClientError as e:
                    if e.response.get("Error", {}).get("Code") == "NoSuchTagSet":
                        tags = {}
                    else:
                        logger.debug(
                            f"Error getting tags for bucket {bucket_name}: {e}"
                        )
                        continue

                # For import mode, include all resources
                # For state mode, only include managed resources
                if not include_unmanaged and "infradsl.id" not in tags:
                    continue

                # Filter by project if specified - get from provider config
                if (
                    hasattr(self.provider.config, "project")
                    and self.provider.config.project
                ):
                    if tags.get("infradsl.project") != self.provider.config.project:
                        continue

                try:
                    # Get bucket location
                    location_response = self.s3_client.get_bucket_location(
                        Bucket=bucket_name
                    )
                    bucket_region = (
                        location_response["LocationConstraint"] or "us-east-1"
                    )

                    # Get bucket versioning
                    versioning_response = self.s3_client.get_bucket_versioning(
                        Bucket=bucket_name
                    )
                    versioning_enabled = versioning_response.get("Status") == "Enabled"

                    # Get bucket encryption
                    encryption_enabled = False
                    try:
                        self.s3_client.get_bucket_encryption(Bucket=bucket_name)
                        encryption_enabled = True
                    except ClientError as e:
                        if (
                            e.response.get("Error", {}).get("Code")
                            != "ServerSideEncryptionConfigurationNotFoundError"
                        ):
                            logger.debug(
                                f"Error checking encryption for bucket {bucket_name}: {e}"
                            )

                    # Get bucket public access block
                    public_access_blocked = True
                    try:
                        pab_response = self.s3_client.get_public_access_block(
                            Bucket=bucket_name
                        )
                        pab = pab_response["PublicAccessBlockConfiguration"]
                        public_access_blocked = all(
                            [
                                pab.get("BlockPublicAcls", False),
                                pab.get("IgnorePublicAcls", False),
                                pab.get("BlockPublicPolicy", False),
                                pab.get("RestrictPublicBuckets", False),
                            ]
                        )
                    except ClientError as e:
                        if (
                            e.response.get("Error", {}).get("Code")
                            != "NoSuchPublicAccessBlockConfiguration"
                        ):
                            logger.debug(
                                f"Error checking public access block for bucket {bucket_name}: {e}"
                            )

                    # Build resource info
                    resource = {
                        "id": tags["infradsl.id"],
                        "name": tags.get("infradsl.name", bucket_name),
                        "type": "bucket",
                        "provider": "aws",
                        "cloud_id": bucket_name,
                        "region": bucket_region,
                        "project": tags.get("infradsl.project", "default"),
                        "environment": tags.get("infradsl.environment", "default"),
                        "state": "active",
                        "tags": tags,
                        "configuration": {
                            "bucket_name": bucket_name,
                            "region": bucket_region,
                            "versioning": versioning_enabled,
                            "encryption": encryption_enabled,
                            "public_access": not public_access_blocked,
                            "creation_date": (
                                bucket["CreationDate"].isoformat()
                                if bucket.get("CreationDate")
                                else None
                            ),
                        },
                        "created_at": (
                            bucket["CreationDate"].isoformat()
                            if bucket.get("CreationDate")
                            else None
                        ),
                        "updated_at": None,  # S3 doesn't provide last modified time for buckets
                        "managed": True,
                        "fingerprint": self._calculate_s3_fingerprint(
                            bucket,
                            versioning_enabled,
                            encryption_enabled,
                            public_access_blocked,
                        ),
                    }

                    resources.append(resource)

                except ClientError as e:
                    logger.debug(f"Error getting details for bucket {bucket_name}: {e}")
                    continue

            return resources

        except ClientError as e:
            logger.error(f"Error discovering S3 buckets: {e}")
            return []

    def _discover_rds_instances(
        self, include_unmanaged: bool = False
    ) -> List[Dict[str, Any]]:
        """Discover RDS instances"""
        try:
            response = self.rds_client.describe_db_instances()
            resources = []

            for instance in response["DBInstances"]:
                # Skip if instance is being deleted
                if instance["DBInstanceStatus"] == "deleting":
                    continue

                # Get tags
                tags_response = self.rds_client.list_tags_for_resource(
                    ResourceName=instance["DBInstanceArn"]
                )
                tags = {tag["Key"]: tag["Value"] for tag in tags_response["TagList"]}

                # For import mode, include all resources
                # For state mode, only include managed resources
                if not include_unmanaged and "infradsl.id" not in tags:
                    continue

                # Filter by project if specified - get from provider config
                if (
                    hasattr(self.provider.config, "project")
                    and self.provider.config.project
                ):
                    if tags.get("infradsl.project") != self.provider.config.project:
                        continue

                # Build resource info
                resource = {
                    "id": tags["infradsl.id"],
                    "name": tags.get("infradsl.name", instance["DBInstanceIdentifier"]),
                    "type": "database",
                    "provider": "aws",
                    "cloud_id": instance["DBInstanceIdentifier"],
                    "region": self.region,
                    "project": tags.get("infradsl.project", "default"),
                    "environment": tags.get("infradsl.environment", "default"),
                    "state": instance["DBInstanceStatus"],
                    "tags": tags,
                    "configuration": {
                        "db_instance_identifier": instance["DBInstanceIdentifier"],
                        "db_instance_class": instance["DBInstanceClass"],
                        "engine": instance["Engine"],
                        "engine_version": instance["EngineVersion"],
                        "master_username": instance["MasterUsername"],
                        "allocated_storage": instance["AllocatedStorage"],
                        "storage_type": instance["StorageType"],
                        "storage_encrypted": instance["StorageEncrypted"],
                        "kms_key_id": instance.get("KmsKeyId"),
                        "db_name": instance.get("DBName"),
                        "endpoint": instance.get("Endpoint", {}).get("Address"),
                        "port": instance.get("Endpoint", {}).get("Port"),
                        "availability_zone": instance.get("AvailabilityZone"),
                        "subnet_group": instance.get("DBSubnetGroup", {}).get(
                            "DBSubnetGroupName"
                        ),
                        "vpc_security_groups": [
                            sg["VpcSecurityGroupId"]
                            for sg in instance.get("VpcSecurityGroups", [])
                        ],
                        "parameter_group": instance.get("DBParameterGroups", [{}])[
                            0
                        ].get("DBParameterGroupName"),
                        "backup_retention_period": instance.get(
                            "BackupRetentionPeriod"
                        ),
                        "preferred_backup_window": instance.get(
                            "PreferredBackupWindow"
                        ),
                        "preferred_maintenance_window": instance.get(
                            "PreferredMaintenanceWindow"
                        ),
                        "multi_az": instance.get("MultiAZ"),
                        "publicly_accessible": instance.get("PubliclyAccessible"),
                        "auto_minor_version_upgrade": instance.get(
                            "AutoMinorVersionUpgrade"
                        ),
                        "license_model": instance.get("LicenseModel"),
                        "iops": instance.get("Iops"),
                        "option_group": instance.get("OptionGroupMemberships", [{}])[
                            0
                        ].get("OptionGroupName"),
                        "character_set_name": instance.get("CharacterSetName"),
                        "secondary_availability_zone": instance.get(
                            "SecondaryAvailabilityZone"
                        ),
                        "deletion_protection": instance.get("DeletionProtection"),
                        "performance_insights_enabled": instance.get(
                            "PerformanceInsightsEnabled"
                        ),
                        "monitoring_interval": instance.get("MonitoringInterval"),
                        "monitoring_role_arn": instance.get("MonitoringRoleArn"),
                        "domain_memberships": instance.get("DomainMemberships", []),
                        "copy_tags_to_snapshot": instance.get("CopyTagsToSnapshot"),
                        "timezone": instance.get("Timezone"),
                    },
                    "created_at": (
                        instance.get("InstanceCreateTime").isoformat()
                        if instance.get("InstanceCreateTime")
                        else None
                    ),
                    "updated_at": None,  # RDS doesn't provide last modified time
                    "managed": True,
                    "fingerprint": self._calculate_rds_fingerprint(instance),
                }

                resources.append(resource)

            return resources

        except ClientError as e:
            logger.error(f"Error discovering RDS instances: {e}")
            return []

    def _calculate_ec2_fingerprint(self, instance: Dict[str, Any]) -> str:
        """Calculate fingerprint for EC2 instance"""
        # Include only stable fields that represent the desired configuration
        stable_fields = {
            "instance_type": instance["InstanceType"],
            "image_id": instance["ImageId"],
            "key_name": instance.get("KeyName"),
            "security_groups": sorted(
                [sg["GroupId"] for sg in instance.get("SecurityGroups", [])]
            ),
            "subnet_id": instance.get("SubnetId"),
            "vpc_id": instance.get("VpcId"),
            "monitoring": instance.get("Monitoring", {}).get("State"),
            "tenancy": instance.get("Placement", {}).get("Tenancy"),
            "instance_lifecycle": instance.get("InstanceLifecycle"),
            # Only include stable user data, not dynamic system data
            "user_data": instance.get(
                "UserData"
            ),  # This would need to be fetched separately
            "block_device_mappings": [
                {
                    "device_name": bdm["DeviceName"],
                    "volume_size": bdm.get("Ebs", {}).get("VolumeSize"),
                    "volume_type": bdm.get("Ebs", {}).get("VolumeType"),
                    "encrypted": bdm.get("Ebs", {}).get("Encrypted"),
                    "delete_on_termination": bdm.get("Ebs", {}).get(
                        "DeleteOnTermination"
                    ),
                }
                for bdm in instance.get("BlockDeviceMappings", [])
            ],
        }

        import hashlib
        import json

        # Create a stable string representation
        stable_string = json.dumps(stable_fields, sort_keys=True, default=str)
        return hashlib.md5(stable_string.encode()).hexdigest()

    def _calculate_s3_fingerprint(
        self,
        bucket: Dict[str, Any],
        versioning: bool,
        encryption: bool,
        public_access_blocked: bool,
    ) -> str:
        """Calculate fingerprint for S3 bucket"""
        # Include only stable fields that represent the desired configuration
        stable_fields = {
            "bucket_name": bucket["Name"],
            "versioning": versioning,
            "encryption": encryption,
            "public_access": not public_access_blocked,
        }

        import hashlib
        import json

        # Create a stable string representation
        stable_string = json.dumps(stable_fields, sort_keys=True, default=str)
        return hashlib.md5(stable_string.encode()).hexdigest()

    def _calculate_rds_fingerprint(self, instance: Dict[str, Any]) -> str:
        """Calculate fingerprint for RDS instance"""
        # Include only stable fields that represent the desired configuration
        stable_fields = {
            "db_instance_class": instance["DBInstanceClass"],
            "engine": instance["Engine"],
            "engine_version": instance["EngineVersion"],
            "allocated_storage": instance["AllocatedStorage"],
            "storage_type": instance["StorageType"],
            "storage_encrypted": instance["StorageEncrypted"],
            "master_username": instance["MasterUsername"],
            "db_name": instance.get("DBName"),
            "port": instance.get("Endpoint", {}).get("Port"),
            "subnet_group": instance.get("DBSubnetGroup", {}).get("DBSubnetGroupName"),
            "vpc_security_groups": sorted(
                [
                    sg["VpcSecurityGroupId"]
                    for sg in instance.get("VpcSecurityGroups", [])
                ]
            ),
            "parameter_group": instance.get("DBParameterGroups", [{}])[0].get(
                "DBParameterGroupName"
            ),
            "backup_retention_period": instance.get("BackupRetentionPeriod"),
            "preferred_backup_window": instance.get("PreferredBackupWindow"),
            "preferred_maintenance_window": instance.get("PreferredMaintenanceWindow"),
            "multi_az": instance.get("MultiAZ"),
            "publicly_accessible": instance.get("PubliclyAccessible"),
            "auto_minor_version_upgrade": instance.get("AutoMinorVersionUpgrade"),
            "license_model": instance.get("LicenseModel"),
            "iops": instance.get("Iops"),
            "option_group": instance.get("OptionGroupMemberships", [{}])[0].get(
                "OptionGroupName"
            ),
            "deletion_protection": instance.get("DeletionProtection"),
            "performance_insights_enabled": instance.get("PerformanceInsightsEnabled"),
            "monitoring_interval": instance.get("MonitoringInterval"),
            "copy_tags_to_snapshot": instance.get("CopyTagsToSnapshot"),
        }

        import hashlib
        import json

        # Create a stable string representation
        stable_string = json.dumps(stable_fields, sort_keys=True, default=str)
        return hashlib.md5(stable_string.encode()).hexdigest()

    def get_resource_by_id(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific resource by ID"""
        # Search through all resources to find the one with matching ID
        all_resources = self.discover_resources()

        for resource in all_resources:
            if resource["id"] == resource_id:
                return resource

        return None

    def get_managed_resources(self) -> List[Dict[str, Any]]:
        """Get all managed resources"""
        return self.discover_resources()

    def is_resource_managed(self, resource_id: str) -> bool:
        """Check if a resource is managed by InfraDSL"""
        return self.get_resource_by_id(resource_id) is not None

    def get_provider_name(self) -> str:
        """Get the provider name"""
        return "aws"

    def validate_credentials(self) -> bool:
        """Validate AWS credentials"""
        try:
            # Try to make a simple API call to validate credentials
            sts_client = boto3.client("sts")
            sts_client.get_caller_identity()
            return True
        except Exception:
            return False

    def is_managed_resource(self, resource: Dict[str, Any]) -> bool:
        """Check if a cloud resource is managed by InfraDSL"""
        # Check for InfraDSL management tags
        tags = resource.get("tags", {})
        if isinstance(tags, list):
            # AWS format: [{"Key": "...", "Value": "..."}]
            tag_dict = {tag["Key"]: tag["Value"] for tag in tags}
            return "infradsl.id" in tag_dict
        elif isinstance(tags, dict):
            # Already in dict format
            return "infradsl.id" in tags
        return False

    def extract_metadata(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Extract InfraDSL metadata from resource tags"""
        tags = resource.get("tags", {})
        if isinstance(tags, list):
            # AWS format: [{"Key": "...", "Value": "..."}]
            tag_dict = {tag["Key"]: tag["Value"] for tag in tags}
        else:
            # Already in dict format
            tag_dict = tags

        # Extract InfraDSL metadata
        metadata = {}
        for key, value in tag_dict.items():
            if key.startswith("infradsl."):
                metadata[key] = value

        return metadata
