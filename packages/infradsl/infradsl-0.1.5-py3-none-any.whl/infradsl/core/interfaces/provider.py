from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from dataclasses import dataclass
from enum import Enum

from ..nexus.base_resource import ResourceMetadata


class ProviderType(Enum):
    """Supported cloud providers"""

    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    DIGITAL_OCEAN = "digitalocean"
    CLOUDFLARE = "cloudflare"
    KUBERNETES = "kubernetes"
    LOCAL = "local"


@dataclass
class ProviderConfig:
    """Configuration for a provider"""

    type: ProviderType
    region: Optional[str] = None
    project: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = None
    endpoints: Optional[Dict[str, str]] = None
    options: Optional[Dict[str, Any]] = None


class ResourceQuery:
    """Query builder for finding resources"""

    def __init__(self):
        self.filters: Dict[str, Any] = {}

    def by_id(self, resource_id: str) -> "ResourceQuery":
        self.filters["id"] = resource_id
        return self

    def by_name(self, name: str) -> "ResourceQuery":
        self.filters["name"] = name
        return self

    def by_project(self, project: str) -> "ResourceQuery":
        self.filters["project"] = project
        return self

    def by_environment(self, env: str) -> "ResourceQuery":
        self.filters["environment"] = env
        return self

    def by_labels(self, **labels: str) -> "ResourceQuery":
        self.filters["labels"] = labels
        return self

    def by_type(self, resource_type: str) -> "ResourceQuery":
        self.filters["type"] = resource_type
        return self


class ProviderInterface(ABC):
    """
    Interface that all cloud providers must implement.
    This is the contract between the Nexus Engine and provider implementations.
    """

    def __init__(self, config: ProviderConfig):
        self.config = config
        self._validate_config()
        self._initialize()

    @abstractmethod
    def _validate_config(self) -> None:
        """Validate provider configuration"""
        pass

    @abstractmethod
    def _initialize(self) -> None:
        """Initialize provider connection"""
        pass

    @abstractmethod
    def create_resource(
        self,
        resource_type: str,
        config: Dict[str, Any],
        metadata: ResourceMetadata,
    ) -> Dict[str, Any]:
        """
        Create a new resource in the cloud provider.

        Args:
            resource_type: Type of resource (e.g., "instance", "database")
            config: Provider-specific configuration
            metadata: InfraDSL metadata for tracking

        Returns:
            Provider-specific resource data including ID
        """
        pass

    @abstractmethod
    def update_resource(
        self, resource_id: str, resource_type: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing resource.

        Args:
            resource_id: Provider-specific resource ID
            resource_type: Type of resource
            updates: Fields to update

        Returns:
            Updated resource data
        """
        pass

    @abstractmethod
    def delete_resource(self, resource_id: str, resource_type: str) -> None:
        """
        Delete a resource.

        Args:
            resource_id: Provider-specific resource ID
            resource_type: Type of resource
        """
        pass

    @abstractmethod
    def get_resource(
        self, resource_id: str, resource_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a single resource by ID.

        Args:
            resource_id: Provider-specific resource ID
            resource_type: Type of resource

        Returns:
            Resource data or None if not found
        """
        pass

    @abstractmethod
    def list_resources(
        self, resource_type: str, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """
        List resources matching query criteria.

        Args:
            resource_type: Type of resource to list
            query: Optional query filters

        Returns:
            List of matching resources
        """
        pass

    @abstractmethod
    def plan_create(
        self,
        resource_type: str,
        config: Dict[str, Any],
        metadata: ResourceMetadata,
    ) -> Dict[str, Any]:
        """
        Preview the creation of a resource. Should return a plan or diff of what would be created.
        """
        pass

    @abstractmethod
    def plan_update(
        self,
        resource_id: str,
        resource_type: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Preview the update of a resource. Should return a plan or diff of what would be changed.
        """
        pass

    @abstractmethod
    def plan_delete(
        self,
        resource_id: str,
        resource_type: str,
    ) -> Dict[str, Any]:
        """
        Preview the deletion of a resource. Should return a plan or diff of what would be deleted.
        """
        pass

    @abstractmethod
    def discover_resources(
        self, resource_type: str, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """
        Discover resources in the provider, possibly using broader or external discovery mechanisms.
        """
        pass

    def get_resource_state(
        self, metadata: ResourceMetadata
    ) -> Optional[Dict[str, Any]]:
        """
        Get resource state using InfraDSL metadata.
        Default implementation uses tags to find resources.
        """
        query = ResourceQuery().by_labels(**metadata.to_tags())
        resources = self.list_resources("*", query)

        if not resources:
            return None

        # Return first match (there should only be one)
        return resources[0]

    @abstractmethod
    def tag_resource(
        self, resource_id: str, resource_type: str, tags: Dict[str, str]
    ) -> None:
        """
        Apply tags to a resource for tracking.

        Args:
            resource_id: Provider-specific resource ID
            resource_type: Type of resource
            tags: Tags to apply
        """
        pass

    @abstractmethod
    def estimate_cost(
        self, resource_type: str, config: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Estimate cost for a resource configuration.

        Args:
            resource_type: Type of resource
            config: Resource configuration

        Returns:
            Cost estimates (hourly, monthly, etc.)
        """
        pass

    @abstractmethod
    def validate_config(self, resource_type: str, config: Dict[str, Any]) -> List[str]:
        """
        Validate a resource configuration without creating it.

        Args:
            resource_type: Type of resource
            config: Resource configuration

        Returns:
            List of validation errors (empty if valid)
        """
        pass

    @abstractmethod
    def get_resource_types(self) -> List[str]:
        """Get list of supported resource types for this provider"""
        pass

    @abstractmethod
    def get_regions(self) -> List[str]:
        """Get list of available regions"""
        pass

    def health_check(self) -> bool:
        """Check if provider connection is healthy"""
        try:
            # Simple implementation - try to list regions
            regions = self.get_regions()
            return len(regions) > 0
        except Exception:
            return False
