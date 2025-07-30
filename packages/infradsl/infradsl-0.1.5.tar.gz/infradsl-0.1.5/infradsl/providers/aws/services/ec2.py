"""
AWS EC2 Service
"""

import logging
from typing import Any, Dict, List, Optional

from .base import BaseAWSService
from ....core.interfaces.provider import ResourceQuery

logger = logging.getLogger(__name__)


class EC2Service(BaseAWSService):
    """AWS EC2 service implementation"""
    
    def create_instance(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create EC2 instance (placeholder)"""
        return {"InstanceId": "i-placeholder"}

    def update_instance(self, instance_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update EC2 instance"""
        return {"InstanceId": instance_id}

    def delete_instance(self, instance_id: str) -> None:
        """Delete EC2 instance"""
        pass

    def get_instance(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get EC2 instance by ID"""
        return None

    def list_instances(self, query: Optional[ResourceQuery] = None) -> List[Dict[str, Any]]:
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
                            "type": "EC2",
                            "provider": "aws",
                            "state": instance["State"]["Name"],
                        }
                        instances.append(instance_info)
        except Exception as e:
            logger.error(f"Error listing EC2 instances: {e}")

        return instances

    def tag_instance(self, instance_id: str, tags: Dict[str, str]) -> None:
        """Tag EC2 instance"""
        pass

    def preview_create(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Preview EC2 instance creation"""
        return {
            "instance_type": config.get("instance_type", "t2.micro"),
            "ami": config.get("ami"),
            "security_groups": config.get("security_groups", []),
        }

    def preview_update(self, resource_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Preview EC2 instance update"""
        return {
            "instance_id": resource_id,
            "changes": list(updates.keys()),
        }

    def get_delete_warnings(self) -> List[str]:
        """Get warnings for EC2 instance deletion"""
        return [
            "Instance will be permanently terminated",
            "All data on instance store volumes will be lost",
        ]

    def estimate_cost(self, config: Dict[str, Any]) -> Dict[str, float]:
        """Estimate EC2 instance cost"""
        # Basic cost estimation
        instance_type = config.get("instance_type", "t2.micro")
        if instance_type == "t2.micro":
            return {"monthly": 8.50}
        elif instance_type == "t2.small":
            return {"monthly": 17.00}
        else:
            return {"monthly": 35.00}  # Default estimate