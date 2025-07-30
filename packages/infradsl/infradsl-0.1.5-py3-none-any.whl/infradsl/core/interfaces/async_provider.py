from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Union, Sequence
from dataclasses import dataclass
from enum import Enum

from .provider import ProviderType, ProviderConfig, ResourceQuery
from ..nexus.base_resource import ResourceMetadata


class AsyncProviderInterface(ABC):
    """
    Async interface that all cloud providers can implement for enhanced performance.
    This is the async contract between the Nexus Engine and provider implementations.
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
    async def create_resource(
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
    async def update_resource(
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
    async def delete_resource(self, resource_id: str, resource_type: str) -> None:
        """
        Delete a resource.

        Args:
            resource_id: Provider-specific resource ID
            resource_type: Type of resource
        """
        pass

    @abstractmethod
    async def get_resource(
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
    async def list_resources(
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
    async def plan_create(
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
    async def plan_update(
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
    async def plan_delete(
            self,
            resource_id: str,
            resource_type: str,
    ) -> Dict[str, Any]:
        """
        Preview the deletion of a resource. Should return a plan or diff of what would be deleted.
        """
        pass

    @abstractmethod
    async def discover_resources(
            self, resource_type: str, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """
        Discover resources in the provider, possibly using broader or external discovery mechanisms.
        """
        pass

    async def get_resource_state(
            self, metadata: ResourceMetadata
    ) -> Optional[Dict[str, Any]]:
        """
        Get resource state using InfraDSL metadata.
        Default implementation uses tags to find resources.
        """
        query = ResourceQuery().by_labels(**metadata.to_tags())
        resources = await self.list_resources("*", query)

        if not resources:
            return None

        # Return first match (there should only be one)
        return resources[0]

    @abstractmethod
    async def tag_resource(
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
    async def estimate_cost(
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
    async def validate_config(self, resource_type: str, config: Dict[str, Any]) -> List[str]:
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
    async def get_resource_types(self) -> List[str]:
        """Get list of supported resource types for this provider"""
        pass

    @abstractmethod
    async def get_regions(self) -> List[str]:
        """Get list of available regions"""
        pass

    async def health_check(self) -> bool:
        """Check if provider connection is healthy"""
        try:
            # Simple implementation - try to list regions
            regions = await self.get_regions()
            return len(regions) > 0
        except Exception:
            return False

    # Batch operations for enhanced performance
    async def batch_create_resources(
            self,
            resource_specs: List[Dict[str, Any]],
    ) -> Sequence[Union[Dict[str, Any], BaseException]]:
        """
        Create multiple resources in parallel.
        
        Args:
            resource_specs: List of resource specifications, each containing:
                - resource_type: Type of resource
                - config: Provider-specific configuration
                - metadata: InfraDSL metadata
        
        Returns:
            Sequence of created resource data or exceptions
        """
        import asyncio
        
        tasks = []
        for spec in resource_specs:
            task = self.create_resource(
                spec["resource_type"], spec["config"], spec["metadata"]
            )
            tasks.append(task)
        
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def batch_get_resources(
            self,
            resource_specs: List[Dict[str, str]],
    ) -> Sequence[Union[Optional[Dict[str, Any]], BaseException]]:
        """
        Get multiple resources in parallel.
        
        Args:
            resource_specs: List of resource specifications, each containing:
                - resource_id: Provider-specific resource ID
                - resource_type: Type of resource
        
        Returns:
            Sequence of resource data (None for not found) or exceptions
        """
        import asyncio
        
        tasks = []
        for spec in resource_specs:
            task = self.get_resource(spec["resource_id"], spec["resource_type"])
            tasks.append(task)
        
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def batch_plan_operations(
            self,
            operations: List[Dict[str, Any]],
    ) -> Sequence[Union[Dict[str, Any], BaseException]]:
        """
        Plan multiple operations in parallel.
        
        Args:
            operations: List of operation specifications, each containing:
                - action: "create", "update", or "delete"
                - resource_type: Type of resource
                - config/updates: Configuration or updates
                - metadata: InfraDSL metadata (for create)
                - resource_id: Resource ID (for update/delete)
        
        Returns:
            Sequence of plan results or exceptions
        """
        import asyncio
        
        tasks = []
        for op in operations:
            if op["action"] == "create":
                task = self.plan_create(
                    op["resource_type"], op["config"], op["metadata"]
                )
            elif op["action"] == "update":
                task = self.plan_update(
                    op["resource_id"], op["resource_type"], op["updates"]
                )
            elif op["action"] == "delete":
                task = self.plan_delete(op["resource_id"], op["resource_type"])
            else:
                raise ValueError(f"Unknown operation action: {op['action']}")
            
            tasks.append(task)
        
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def discover_all_resources(
            self,
            resource_types: Optional[List[str]] = None,
            query: Optional[ResourceQuery] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Discover all resources across multiple types in parallel.
        
        Args:
            resource_types: List of resource types to discover (None for all)
            query: Optional query filters
        
        Returns:
            Dictionary mapping resource type to list of resources
        """
        import asyncio
        
        if resource_types is None:
            resource_types = await self.get_resource_types()
        
        tasks = []
        for resource_type in resource_types:
            task = self.discover_resources(resource_type, query)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Build result dictionary
        discovery_results = {}
        for i, resource_type in enumerate(resource_types):
            result = results[i]
            if isinstance(result, Exception):
                # Log error but continue with other resource types
                discovery_results[resource_type] = []
            else:
                discovery_results[resource_type] = result
        
        return discovery_results