"""
Async Nexus Engine - High-performance async orchestration engine
"""

import asyncio
from typing import Any, Dict, List, Optional, Union, Type, Sequence
from dataclasses import dataclass
from enum import Enum
import logging

from ..interfaces.async_provider import AsyncProviderInterface
from ..interfaces.provider import ProviderInterface, ResourceQuery
from ..nexus.base_resource import ResourceMetadata
from ..exceptions import ProviderException


logger = logging.getLogger(__name__)


class OperationStatus(Enum):
    """Status of async operations"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AsyncOperation:
    """Represents an async operation"""
    id: str
    action: str
    resource_type: str
    provider: str
    status: OperationStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    

class AsyncNexusEngine:
    """
    High-performance async orchestration engine for InfraDSL.
    
    This engine provides:
    - Async operations for improved performance
    - Batch operations for resource management
    - Concurrent provider operations
    - Resource dependency resolution
    - Operation monitoring and status tracking
    """
    
    def __init__(self):
        self.providers: Dict[str, Union[AsyncProviderInterface, ProviderInterface]] = {}
        self.operations: Dict[str, AsyncOperation] = {}
        self._operation_counter = 0
        self._semaphore = asyncio.Semaphore(10)  # Limit concurrent operations
        
    def register_provider(
        self, 
        name: str, 
        provider: Union[AsyncProviderInterface, ProviderInterface]
    ) -> None:
        """Register a provider with the async engine"""
        self.providers[name] = provider
        logger.info(f"Registered provider: {name} ({'async' if isinstance(provider, AsyncProviderInterface) else 'sync'})")
    
    def _generate_operation_id(self) -> str:
        """Generate unique operation ID"""
        self._operation_counter += 1
        return f"op_{self._operation_counter}"
    
    async def _execute_with_provider(
        self, 
        provider: Union[AsyncProviderInterface, ProviderInterface], 
        method_name: str, 
        *args, 
        **kwargs
    ) -> Any:
        """Execute method with provider, handling both sync and async providers"""
        method = getattr(provider, method_name)
        
        if isinstance(provider, AsyncProviderInterface):
            # Async provider - call directly
            return await method(*args, **kwargs)
        else:
            # Sync provider - wrap in executor
            import concurrent.futures
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                return await loop.run_in_executor(executor, method, *args, **kwargs)
    
    async def create_resource(
        self,
        provider_name: str,
        resource_type: str,
        config: Dict[str, Any],
        metadata: ResourceMetadata,
    ) -> Dict[str, Any]:
        """Create a resource asynchronously"""
        if provider_name not in self.providers:
            raise ProviderException(f"Provider {provider_name} not registered")
        
        provider = self.providers[provider_name]
        
        async with self._semaphore:
            return await self._execute_with_provider(
                provider, "create_resource", resource_type, config, metadata
            )
    
    async def update_resource(
        self,
        provider_name: str,
        resource_id: str,
        resource_type: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a resource asynchronously"""
        if provider_name not in self.providers:
            raise ProviderException(f"Provider {provider_name} not registered")
        
        provider = self.providers[provider_name]
        
        async with self._semaphore:
            return await self._execute_with_provider(
                provider, "update_resource", resource_id, resource_type, updates
            )
    
    async def delete_resource(
        self,
        provider_name: str,
        resource_id: str,
        resource_type: str,
    ) -> None:
        """Delete a resource asynchronously"""
        if provider_name not in self.providers:
            raise ProviderException(f"Provider {provider_name} not registered")
        
        provider = self.providers[provider_name]
        
        async with self._semaphore:
            return await self._execute_with_provider(
                provider, "delete_resource", resource_id, resource_type
            )
    
    async def get_resource(
        self,
        provider_name: str,
        resource_id: str,
        resource_type: str,
    ) -> Optional[Dict[str, Any]]:
        """Get a resource asynchronously"""
        if provider_name not in self.providers:
            raise ProviderException(f"Provider {provider_name} not registered")
        
        provider = self.providers[provider_name]
        
        return await self._execute_with_provider(
            provider, "get_resource", resource_id, resource_type
        )
    
    async def list_resources(
        self,
        provider_name: str,
        resource_type: str,
        query: Optional[ResourceQuery] = None,
    ) -> List[Dict[str, Any]]:
        """List resources asynchronously"""
        if provider_name not in self.providers:
            raise ProviderException(f"Provider {provider_name} not registered")
        
        provider = self.providers[provider_name]
        
        return await self._execute_with_provider(
            provider, "list_resources", resource_type, query
        )
    
    async def plan_create(
        self,
        provider_name: str,
        resource_type: str,
        config: Dict[str, Any],
        metadata: ResourceMetadata,
    ) -> Dict[str, Any]:
        """Plan resource creation asynchronously"""
        if provider_name not in self.providers:
            raise ProviderException(f"Provider {provider_name} not registered")
        
        provider = self.providers[provider_name]
        
        return await self._execute_with_provider(
            provider, "plan_create", resource_type, config, metadata
        )
    
    async def plan_update(
        self,
        provider_name: str,
        resource_id: str,
        resource_type: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Plan resource update asynchronously"""
        if provider_name not in self.providers:
            raise ProviderException(f"Provider {provider_name} not registered")
        
        provider = self.providers[provider_name]
        
        return await self._execute_with_provider(
            provider, "plan_update", resource_id, resource_type, updates
        )
    
    async def plan_delete(
        self,
        provider_name: str,
        resource_id: str,
        resource_type: str,
    ) -> Dict[str, Any]:
        """Plan resource deletion asynchronously"""
        if provider_name not in self.providers:
            raise ProviderException(f"Provider {provider_name} not registered")
        
        provider = self.providers[provider_name]
        
        return await self._execute_with_provider(
            provider, "plan_delete", resource_id, resource_type
        )
    
    async def discover_resources(
        self,
        provider_name: str,
        resource_type: str,
        query: Optional[ResourceQuery] = None,
    ) -> List[Dict[str, Any]]:
        """Discover resources asynchronously"""
        if provider_name not in self.providers:
            raise ProviderException(f"Provider {provider_name} not registered")
        
        provider = self.providers[provider_name]
        
        return await self._execute_with_provider(
            provider, "discover_resources", resource_type, query
        )
    
    # Batch operations for enhanced performance
    async def batch_create_resources(
        self,
        operations: List[Dict[str, Any]],
    ) -> Sequence[Union[Dict[str, Any], BaseException]]:
        """
        Create multiple resources in parallel across providers.
        
        Args:
            operations: List of operations, each containing:
                - provider: Provider name
                - resource_type: Type of resource
                - config: Provider-specific configuration
                - metadata: InfraDSL metadata
        
        Returns:
            Sequence of created resource data or exceptions
        """
        tasks = []
        for op in operations:
            task = self.create_resource(
                op["provider"], op["resource_type"], op["config"], op["metadata"]
            )
            tasks.append(task)
        
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def batch_plan_operations(
        self,
        operations: List[Dict[str, Any]],
    ) -> Sequence[Union[Dict[str, Any], BaseException]]:
        """
        Plan multiple operations in parallel across providers.
        
        Args:
            operations: List of operations, each containing:
                - provider: Provider name
                - action: "create", "update", or "delete"
                - resource_type: Type of resource
                - config/updates: Configuration or updates
                - metadata: InfraDSL metadata (for create)
                - resource_id: Resource ID (for update/delete)
        
        Returns:
            Sequence of plan results or exceptions
        """
        tasks = []
        for op in operations:
            if op["action"] == "create":
                task = self.plan_create(
                    op["provider"], op["resource_type"], op["config"], op["metadata"]
                )
            elif op["action"] == "update":
                task = self.plan_update(
                    op["provider"], op["resource_id"], op["resource_type"], op["updates"]
                )
            elif op["action"] == "delete":
                task = self.plan_delete(
                    op["provider"], op["resource_id"], op["resource_type"]
                )
            else:
                raise ValueError(f"Unknown operation action: {op['action']}")
            
            tasks.append(task)
        
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def discover_all_resources(
        self,
        provider_names: Optional[List[str]] = None,
        resource_types: Optional[List[str]] = None,
        query: Optional[ResourceQuery] = None,
    ) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        Discover all resources across multiple providers and types in parallel.
        
        Args:
            provider_names: List of provider names (None for all)
            resource_types: List of resource types (None for all)
            query: Optional query filters
        
        Returns:
            Dictionary mapping provider -> resource_type -> list of resources
        """
        if provider_names is None:
            provider_names = list(self.providers.keys())
        
        provider_tasks = []
        for provider_name in provider_names:
            provider = self.providers[provider_name]
            
            # Get resource types for this provider
            if resource_types is None:
                provider_resource_types = await self._execute_with_provider(
                    provider, "get_resource_types"
                )
            else:
                provider_resource_types = resource_types
            
            # Create discovery tasks for each resource type
            for resource_type in provider_resource_types:
                task = self.discover_resources(provider_name, resource_type, query)
                provider_tasks.append((provider_name, resource_type, task))
        
        # Execute all tasks in parallel
        results = await asyncio.gather(
            *[task for _, _, task in provider_tasks], 
            return_exceptions=True
        )
        
        # Build result dictionary
        discovery_results = {}
        for i, (provider_name, resource_type, _) in enumerate(provider_tasks):
            result = results[i]
            
            if provider_name not in discovery_results:
                discovery_results[provider_name] = {}
            
            if isinstance(result, Exception):
                # Log error but continue with other resource types
                logger.error(f"Discovery failed for {provider_name}.{resource_type}: {result}")
                discovery_results[provider_name][resource_type] = []
            else:
                discovery_results[provider_name][resource_type] = result
        
        return discovery_results
    
    async def health_check_all_providers(self) -> Dict[str, bool]:
        """Check health of all registered providers in parallel"""
        tasks = []
        for provider_name, provider in self.providers.items():
            task = self._execute_with_provider(provider, "health_check")
            tasks.append((provider_name, task))
        
        results = await asyncio.gather(
            *[task for _, task in tasks], 
            return_exceptions=True
        )
        
        health_status = {}
        for i, (provider_name, _) in enumerate(tasks):
            result = results[i]
            if isinstance(result, Exception):
                health_status[provider_name] = False
            else:
                health_status[provider_name] = result
        
        return health_status
    
    async def get_operation_status(self, operation_id: str) -> Optional[AsyncOperation]:
        """Get the status of an async operation"""
        return self.operations.get(operation_id)
    
    async def cancel_operation(self, operation_id: str) -> bool:
        """Cancel an async operation"""
        if operation_id in self.operations:
            operation = self.operations[operation_id]
            operation.status = OperationStatus.CANCELLED
            return True
        return False
    
    async def get_all_operations(self) -> List[AsyncOperation]:
        """Get all operations"""
        return list(self.operations.values())
    
    async def cleanup_completed_operations(self) -> int:
        """Clean up completed operations to prevent memory leaks"""
        completed_statuses = {
            OperationStatus.SUCCESS, 
            OperationStatus.FAILED, 
            OperationStatus.CANCELLED
        }
        
        operations_to_remove = [
            op_id for op_id, op in self.operations.items()
            if op.status in completed_statuses
        ]
        
        for op_id in operations_to_remove:
            del self.operations[op_id]
        
        return len(operations_to_remove)