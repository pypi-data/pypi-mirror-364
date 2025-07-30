"""
Provider-agnostic state discovery interface

This interface defines how providers discover and identify managed resources
across different cloud platforms with consistent behavior.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
from ...interfaces.provider import ProviderInterface


class StateDiscoverer(ABC):
    """
    Abstract base class for provider-specific resource discovery.

    Each cloud provider implements this interface to enable consistent
    state discovery and resource identification across platforms.
    """

    def __init__(self, provider: ProviderInterface):
        """
        Initialize discoverer with a provider instance.

        Args:
            provider: The cloud provider implementation
        """
        self.provider = provider

    @abstractmethod
    def discover_resources(
        self, include_unmanaged: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Discover resources from the provider.

        Args:
            include_unmanaged: If True, include ALL resources (for import).
                              If False, only include managed resources (for state).

        Returns:
            List of resource dictionaries with standardized format:
            {
                "name": str,
                "id": str,
                "type": str,
                "provider": str,
                "state": str,
                "metadata": Dict[str, Any],
                "discovered_at": str,
                ...
            }
        """
        pass

    @abstractmethod
    def is_managed_resource(self, resource: Dict[str, Any]) -> bool:
        """
        Check if a cloud resource is managed by InfraDSL.

        Args:
            resource: Raw resource data from cloud provider

        Returns:
            True if resource is managed by InfraDSL, False otherwise
        """
        pass

    @abstractmethod
    def extract_metadata(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract InfraDSL metadata from resource tags/labels.

        Args:
            resource: Raw resource data from cloud provider

        Returns:
            Dictionary of InfraDSL metadata (id, project, environment, etc.)
        """
        pass

    def normalize_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize resource to standardized InfraDSL format.

        This method can be overridden by providers for custom normalization,
        but provides sensible defaults for common resource fields.

        Args:
            resource: Raw resource data from cloud provider

        Returns:
            Normalized resource dictionary
        """
        metadata = self.extract_metadata(resource)

        return {
            "name": resource.get("name"),
            "id": metadata.get("infradsl.id", resource.get("id")),
            "type": "VirtualMachine",  # Default type, override in subclasses
            "provider": self.provider.config.type.value.lower(),
            "state": self._normalize_state(resource.get("status", "unknown")),
            "project": metadata.get("infradsl.project", "default"),
            "environment": metadata.get("infradsl.environment", "unknown"),
            "cloud_id": resource.get("id"),
            "region": resource.get("region"),
            "zone": resource.get("zone"),
            "ip_address": resource.get("ip_address"),
            "private_ip_address": resource.get("private_ip_address"),
            "created_at": resource.get("created_at"),
            "tags": resource.get("tags", []),
            "discovered_at": datetime.utcnow().isoformat(),
            "metadata": metadata,
            "configuration": self._extract_configuration(resource),
        }

    def _normalize_state(self, provider_state: str) -> str:
        """
        Normalize provider-specific state to standard values.

        Args:
            provider_state: Raw state from cloud provider

        Returns:
            Normalized state: "active", "inactive", "pending", "error", "unknown"
        """
        state_lower = provider_state.lower()

        # Common active states across providers
        if state_lower in ["running", "active", "available", "up"]:
            return "active"

        # Common inactive states
        if state_lower in ["stopped", "shutoff", "down", "terminated"]:
            return "inactive"

        # Common transitional states
        if state_lower in [
            "pending",
            "starting",
            "stopping",
            "creating",
            "provisioning",
        ]:
            return "pending"

        # Common error states
        if state_lower in ["error", "failed", "fault"]:
            return "error"

        return "unknown"

    def _extract_configuration(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract configuration details for the resource.

        Args:
            resource: Raw resource data from cloud provider

        Returns:
            Configuration dictionary with common fields
        """
        return {
            "size": resource.get("size"),
            "machine_type": resource.get("machine_type"),
            "image": resource.get("image"),
            "backups": resource.get("backups", False),
            "monitoring": resource.get("monitoring", True),
            "ipv6": resource.get("ipv6", False),
        }
