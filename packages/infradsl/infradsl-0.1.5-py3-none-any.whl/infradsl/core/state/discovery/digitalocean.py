"""
DigitalOcean-specific state discovery implementation

Discovers and normalizes DigitalOcean Droplets with proper
tag extraction and InfraDSL metadata identification.
"""

from typing import Dict, List, Any
import uuid
from datetime import datetime
from ..interfaces.state_discoverer import StateDiscoverer


class DigitalOceanStateDiscoverer(StateDiscoverer):
    """
    DigitalOcean-specific resource discovery implementation.

    Handles DigitalOcean Droplets with proper tag format handling
    and InfraDSL management tag identification.
    """

    def discover_resources(
        self, include_unmanaged: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Discover DigitalOcean Droplets and Managed Databases.

        Args:
            include_unmanaged: If True, include ALL resources (for import).
                              If False, only include managed resources (for state).

        Returns:
            List of discovered and normalized DigitalOcean resources
        """
        resources = []

        try:
            # List droplets from DigitalOcean provider
            import logging

            logger = logging.getLogger(__name__)
            logger.debug("Starting DigitalOcean droplet discovery")

            droplets = self.provider.list_resources("droplet")
            logger.debug(f"Found {len(droplets)} droplets from DigitalOcean")

            for droplet in droplets:
                # For import mode, include all resources
                # For state mode, only include managed resources
                if include_unmanaged or self.is_managed_resource(droplet):
                    normalized = self.normalize_resource(droplet)
                    resources.append(normalized)

            logger.debug(f"Found {len(resources)} droplets for processing")

            # List managed databases
            logger.debug("Starting DigitalOcean database discovery")
            databases = self.provider.list_resources("managed_database")
            logger.debug(f"Found {len(databases)} databases from DigitalOcean")

            for database in databases:
                # For import mode, include all resources
                # For state mode, only include managed resources
                if include_unmanaged or self.is_managed_resource(database):
                    normalized = self.normalize_resource(database)
                    resources.append(normalized)

            logger.debug(f"Total resources found: {len(resources)}")

        except Exception as e:
            # Log but don't fail - provider might not be available
            import logging

            logger = logging.getLogger(__name__)
            logger.debug(f"Error discovering DigitalOcean resources: {e}")

        return resources

    def is_managed_resource(self, resource: Dict[str, Any]) -> bool:
        """
        Check if DigitalOcean resource is managed by InfraDSL.

        Args:
            resource: Raw DigitalOcean droplet data

        Returns:
            True if resource is managed by InfraDSL
        """
        tags = resource.get("tags", [])

        # Look for InfraDSL management tags
        # Note: DigitalOcean converts dots to underscores in tag names
        for tag in tags:
            if tag.startswith("infradsl_id:") or tag.startswith("infradsl_managed:"):
                return True

        # Also check for user-defined tags that suggest management
        # Note: InfraDSL tags use underscores in DigitalOcean
        user_tags = [tag for tag in tags if not tag.startswith("infradsl_")]
        return len(user_tags) > 0

    def extract_metadata(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract InfraDSL metadata from DigitalOcean tags.

        Args:
            resource: Raw DigitalOcean droplet data

        Returns:
            Dictionary of InfraDSL metadata
        """
        metadata = {}
        tags = resource.get("tags", [])

        for tag in tags:
            if ":" in tag:
                key, value = tag.split(":", 1)
                # Convert DigitalOcean underscore format back to dot format
                if key.startswith("infradsl_"):
                    key_normalized = key.replace("_", ".")
                    metadata[key_normalized] = value

        # Generate missing infradsl.id if needed
        if "infradsl.id" not in metadata:
            metadata["infradsl.id"] = str(uuid.uuid4())

        return metadata

    def normalize_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize DigitalOcean resource to standardized InfraDSL format.

        Args:
            resource: Raw DigitalOcean resource data

        Returns:
            Normalized resource dictionary
        """
        metadata = self.extract_metadata(resource)

        # Determine resource type based on available fields
        if "engine" in resource:
            # This is a database
            return self._normalize_database(resource, metadata)
        else:
            # This is a droplet
            return self._normalize_droplet(resource, metadata)

    def _normalize_droplet(
        self, resource: Dict[str, Any], metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Normalize DigitalOcean droplet to standardized format"""
        return {
            "name": resource.get("name"),
            "id": metadata.get("infradsl.id", resource.get("id")),
            "type": "VirtualMachine",
            "provider": "digitalocean",
            "state": self._normalize_state(resource.get("status", "unknown")),
            "project": metadata.get("infradsl.project", "default"),
            "environment": metadata.get("infradsl.environment", "unknown"),
            "cloud_id": resource.get("id"),
            "region": resource.get("region"),
            "size": resource.get("size"),
            "image": resource.get("image"),
            "ip_address": resource.get("ip_address"),
            "private_ip_address": resource.get("private_ip_address"),
            "created_at": resource.get("created_at"),
            "tags": resource.get("tags", []),
            "discovered_at": datetime.utcnow().isoformat(),
            "metadata": metadata,
            "configuration": {
                "size": resource.get("size"),
                "image": resource.get("image"),
                "backups": resource.get("backups", False),
                "monitoring": resource.get("monitoring", True),
                "ipv6": resource.get("ipv6", True),
            },
        }

    def _normalize_database(
        self, resource: Dict[str, Any], metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Normalize DigitalOcean managed database to standardized format"""
        return {
            "name": resource.get("name"),
            "id": metadata.get("infradsl.id", resource.get("cloud_id")),
            "type": "ManagedDatabase",
            "provider": "digitalocean",
            "state": self._normalize_database_state(resource.get("status", "unknown")),
            "project": metadata.get("infradsl.project", "default"),
            "environment": metadata.get("infradsl.environment", "unknown"),
            "cloud_id": resource.get("cloud_id"),
            "region": resource.get("region"),
            "engine": resource.get("engine"),
            "version": resource.get("version"),
            "size": resource.get("size"),
            "host": resource.get("host"),
            "port": resource.get("port"),
            "database": resource.get("database"),
            "created_at": resource.get("created_at"),
            "tags": resource.get("tags", {}),
            "discovered_at": datetime.utcnow().isoformat(),
            "metadata": metadata,
            "configuration": {
                "size": resource.get("size"),
                "engine": resource.get("engine"),
                "version": resource.get("version"),
                "maintenance_window": resource.get("maintenance_window", {}),
            },
        }

    def _normalize_state(self, do_status: str) -> str:
        """
        Normalize DigitalOcean droplet status to standard values.

        Args:
            do_status: Raw DigitalOcean droplet status

        Returns:
            Normalized state: "active", "inactive", "pending", "error", "unknown"
        """
        status_lower = do_status.lower()

        # DigitalOcean-specific status mappings
        if status_lower == "active":
            return "active"
        elif status_lower in ["off", "powered-off"]:
            return "inactive"
        elif status_lower in [
            "new",
            "provisioning",
            "booting",
            "rebooting",
            "shutting-down",
        ]:
            return "pending"
        elif status_lower in ["error", "locked"]:
            return "error"
        else:
            return "unknown"

    def _normalize_database_state(self, db_status: str) -> str:
        """
        Normalize DigitalOcean database status to standard values.

        Args:
            db_status: Raw DigitalOcean database status

        Returns:
            Normalized state: "active", "inactive", "pending", "error", "unknown"
        """
        status_lower = db_status.lower()

        # DigitalOcean database-specific status mappings
        if status_lower == "online":
            return "active"
        elif status_lower == "offline":
            return "inactive"
        elif status_lower in ["creating", "migrating", "forking", "restoring"]:
            return "pending"
        elif status_lower in ["error", "degraded"]:
            return "error"
        else:
            return "unknown"
