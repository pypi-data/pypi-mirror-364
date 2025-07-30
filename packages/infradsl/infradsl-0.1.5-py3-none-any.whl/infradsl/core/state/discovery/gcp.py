"""
GCP-specific state discovery implementation

Discovers and normalizes GCP Compute Engine instances with proper
label-to-tag conversion and InfraDSL metadata extraction.
"""

from typing import Dict, List, Any
import uuid
from datetime import datetime
from ..interfaces.state_discoverer import StateDiscoverer


class GCPStateDiscoverer(StateDiscoverer):
    """
    GCP-specific resource discovery implementation.

    Handles GCP Compute Engine instances with proper label format
    conversion and InfraDSL management tag identification.
    """

    def discover_resources(
        self, include_unmanaged: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Discover GCP Compute Engine instances.

        Args:
            include_unmanaged: If True, include ALL instances (for import).
                              If False, only include managed instances (for state).

        Returns:
            List of discovered and normalized GCP instances
        """
        resources = []

        try:
            # List instances from GCP provider
            instances = self.provider.list_resources("instance")

            for instance in instances:
                # For import mode, include all resources
                # For state mode, only include managed resources
                if include_unmanaged or self.is_managed_resource(instance):
                    normalized = self.normalize_resource(instance)
                    resources.append(normalized)

        except Exception as e:
            # Log but don't fail - provider might not be available
            import logging

            logger = logging.getLogger(__name__)
            logger.debug(f"Error discovering GCP resources: {e}")

        return resources

    def is_managed_resource(self, resource: Dict[str, Any]) -> bool:
        """
        Check if GCP resource is managed by InfraDSL.

        Args:
            resource: Raw GCP instance data

        Returns:
            True if resource is managed by InfraDSL
        """
        tags = resource.get("tags", [])

        # Handle both formats: string list and dict
        if isinstance(tags, dict):
            # Dict format from GCP provider: {'infradsl_id': 'true', 'infradsl_managed': 'true'}
            for key in tags.keys():
                if key.startswith("infradsl_") or key.startswith("infradsl."):
                    return True
        elif isinstance(tags, list):
            # List format: ['infradsl.id:value', 'infradsl.managed:true']
            for tag in tags:
                if tag.startswith("infradsl.id:") or tag.startswith(
                    "infradsl.managed:"
                ):
                    return True

        # Also check for user-defined tags that suggest management
        user_tags = []
        if isinstance(tags, dict):
            user_tags = [key for key in tags.keys() if not key.startswith("infradsl")]
        elif isinstance(tags, list):
            user_tags = [tag for tag in tags if not tag.startswith("infradsl.")]

        return len(user_tags) > 0

    def extract_metadata(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract InfraDSL metadata from GCP labels.

        Args:
            resource: Raw GCP instance data

        Returns:
            Dictionary of InfraDSL metadata
        """
        metadata = {}
        tags = resource.get("tags", [])

        # Handle both formats: string list and dict
        if isinstance(tags, dict):
            # Dict format from GCP provider: {'infradsl_id': 'true', 'infradsl_managed': 'true'}
            for key, value in tags.items():
                if key.startswith("infradsl_"):
                    # Convert underscore back to dot notation
                    normalized_key = key.replace("_", ".")
                    metadata[normalized_key] = value
                elif key.startswith("infradsl."):
                    metadata[key] = value
        elif isinstance(tags, list):
            # List format: ['infradsl.id:value', 'infradsl.managed:true']
            for tag in tags:
                if ":" in tag:
                    key, value = tag.split(":", 1)
                    if key.startswith("infradsl."):
                        metadata[key] = value

        # Generate missing infradsl.id if needed
        if "infradsl.id" not in metadata:
            metadata["infradsl.id"] = str(uuid.uuid4())

        return metadata

    def normalize_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize GCP resource to standardized InfraDSL format.

        Args:
            resource: Raw GCP instance data

        Returns:
            Normalized resource dictionary
        """
        metadata = self.extract_metadata(resource)

        # Normalize tags format - convert dict to list if needed
        tags = resource.get("tags", [])
        if isinstance(tags, dict):
            # Convert dict format to list format for consistency
            tag_list = []
            for key, value in tags.items():
                if key.startswith("infradsl_"):
                    # Convert back to dot notation
                    normalized_key = key.replace("_", ".")
                    tag_list.append(f"{normalized_key}:{value}")
                else:
                    tag_list.append(f"{key}:{value}")
            tags = tag_list

        return {
            "name": resource.get("name"),
            "id": metadata.get("infradsl.id", resource.get("id")),
            "type": "VirtualMachine",
            "provider": "gcp",
            "state": self._normalize_state(resource.get("status", "unknown")),
            "project": metadata.get("infradsl.project", "default"),
            "environment": metadata.get("infradsl.environment", "unknown"),
            "cloud_id": resource.get("id"),
            "region": resource.get("region"),
            "zone": resource.get("zone"),
            "machine_type": resource.get("machine_type"),
            "size": resource.get("size"),
            "image": resource.get("image"),
            "ip_address": resource.get("ip_address"),
            "private_ip_address": resource.get("private_ip_address"),
            "created_at": resource.get("created_at"),
            "tags": tags,
            "discovered_at": datetime.utcnow().isoformat(),
            "metadata": metadata,
            "configuration": {
                "machine_type": resource.get("machine_type"),
                "size": resource.get("size"),
                "image": resource.get("image"),
                "backups": resource.get("backups", False),
                "monitoring": resource.get("monitoring", True),
                "ipv6": resource.get("ipv6", False),
            },
        }

    def _normalize_state(self, gcp_status: str) -> str:
        """
        Normalize GCP instance status to standard values.

        Args:
            gcp_status: Raw GCP instance status

        Returns:
            Normalized state: "active", "inactive", "pending", "error", "unknown"
        """
        status_lower = gcp_status.lower()

        # GCP-specific status mappings
        if status_lower == "running":
            return "active"
        elif status_lower in ["stopped", "terminated"]:
            return "inactive"
        elif status_lower in ["provisioning", "staging", "stopping", "starting"]:
            return "pending"
        elif status_lower in ["error", "crashed", "suspended"]:
            return "error"
        else:
            return "unknown"
