"""
Async Provider Adapter - Wraps sync providers to work with async operations
"""

import asyncio
import concurrent.futures
from typing import Any, Dict, List, Optional

from ..interfaces.provider import ProviderInterface, ResourceQuery
from ..interfaces.async_provider import AsyncProviderInterface
from ..nexus.base_resource import ResourceMetadata


class AsyncProviderAdapter(AsyncProviderInterface):
    """
    Adapter that wraps a synchronous provider to make it work with async operations.
    
    This allows gradual migration from sync to async without breaking existing providers.
    """
    
    def __init__(self, sync_provider: ProviderInterface, max_workers: int = 10):
        """
        Initialize the async adapter.
        
        Args:
            sync_provider: The synchronous provider to wrap
            max_workers: Maximum number of worker threads for async operations
        """
        self.sync_provider = sync_provider
        self.config = sync_provider.config
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        
    def _validate_config(self) -> None:
        """Validate provider configuration - delegate to sync provider"""
        return self.sync_provider._validate_config()
    
    def _initialize(self) -> None:
        """Initialize provider connection - delegate to sync provider"""
        return self.sync_provider._initialize()
    
    async def _run_in_executor(self, method, *args, **kwargs) -> Any:
        """Run a sync method in a thread executor"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, lambda: method(*args, **kwargs)
        )
    
    async def create_resource(
        self,
        resource_type: str,
        config: Dict[str, Any],
        metadata: ResourceMetadata,
    ) -> Dict[str, Any]:
        """Create a resource asynchronously"""
        return await self._run_in_executor(
            self.sync_provider.create_resource, resource_type, config, metadata
        )
    
    async def update_resource(
        self, resource_id: str, resource_type: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a resource asynchronously"""
        return await self._run_in_executor(
            self.sync_provider.update_resource, resource_id, resource_type, updates
        )
    
    async def delete_resource(self, resource_id: str, resource_type: str) -> None:
        """Delete a resource asynchronously"""
        return await self._run_in_executor(
            self.sync_provider.delete_resource, resource_id, resource_type
        )
    
    async def get_resource(
        self, resource_id: str, resource_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get a resource asynchronously"""
        return await self._run_in_executor(
            self.sync_provider.get_resource, resource_id, resource_type
        )
    
    async def list_resources(
        self, resource_type: str, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """List resources asynchronously"""
        return await self._run_in_executor(
            self.sync_provider.list_resources, resource_type, query
        )
    
    async def plan_create(
        self,
        resource_type: str,
        config: Dict[str, Any],
        metadata: ResourceMetadata,
    ) -> Dict[str, Any]:
        """Plan resource creation asynchronously"""
        return await self._run_in_executor(
            self.sync_provider.plan_create, resource_type, config, metadata
        )
    
    async def plan_update(
        self,
        resource_id: str,
        resource_type: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Plan resource update asynchronously"""
        return await self._run_in_executor(
            self.sync_provider.plan_update, resource_id, resource_type, updates
        )
    
    async def plan_delete(
        self,
        resource_id: str,
        resource_type: str,
    ) -> Dict[str, Any]:
        """Plan resource deletion asynchronously"""
        return await self._run_in_executor(
            self.sync_provider.plan_delete, resource_id, resource_type
        )
    
    async def discover_resources(
        self, resource_type: str, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """Discover resources asynchronously"""
        return await self._run_in_executor(
            self.sync_provider.discover_resources, resource_type, query
        )
    
    async def tag_resource(
        self, resource_id: str, resource_type: str, tags: Dict[str, str]
    ) -> None:
        """Tag a resource asynchronously"""
        return await self._run_in_executor(
            self.sync_provider.tag_resource, resource_id, resource_type, tags
        )
    
    async def estimate_cost(
        self, resource_type: str, config: Dict[str, Any]
    ) -> Dict[str, float]:
        """Estimate cost asynchronously"""
        return await self._run_in_executor(
            self.sync_provider.estimate_cost, resource_type, config
        )
    
    async def validate_config(
        self, resource_type: str, config: Dict[str, Any]
    ) -> List[str]:
        """Validate config asynchronously"""
        return await self._run_in_executor(
            self.sync_provider.validate_config, resource_type, config
        )
    
    async def get_resource_types(self) -> List[str]:
        """Get resource types asynchronously"""
        return await self._run_in_executor(self.sync_provider.get_resource_types)
    
    async def get_regions(self) -> List[str]:
        """Get regions asynchronously"""
        return await self._run_in_executor(self.sync_provider.get_regions)
    
    async def health_check(self) -> bool:
        """Check health asynchronously"""
        return await self._run_in_executor(self.sync_provider.health_check)
    
    def __del__(self):
        """Cleanup executor when adapter is destroyed"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)


class AsyncProviderManager:
    """
    Manager for handling both sync and async providers in a unified way.
    """
    
    def __init__(self):
        self.providers: Dict[str, AsyncProviderInterface] = {}
        self.adapters: Dict[str, AsyncProviderAdapter] = {}
    
    def register_sync_provider(
        self, 
        name: str, 
        provider: ProviderInterface, 
        max_workers: int = 10
    ) -> None:
        """Register a sync provider with async adapter"""
        adapter = AsyncProviderAdapter(provider, max_workers)
        self.adapters[name] = adapter
        self.providers[name] = adapter
    
    def register_async_provider(
        self, 
        name: str, 
        provider: AsyncProviderInterface
    ) -> None:
        """Register an async provider directly"""
        self.providers[name] = provider
    
    def get_provider(self, name: str) -> Optional[AsyncProviderInterface]:
        """Get a provider by name"""
        return self.providers.get(name)
    
    def list_providers(self) -> List[str]:
        """List all registered provider names"""
        return list(self.providers.keys())
    
    def is_sync_provider(self, name: str) -> bool:
        """Check if a provider is a sync provider (wrapped in adapter)"""
        return name in self.adapters
    
    def is_async_provider(self, name: str) -> bool:
        """Check if a provider is a native async provider"""
        return name in self.providers and name not in self.adapters
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all providers"""
        tasks = []
        for name, provider in self.providers.items():
            tasks.append((name, provider.health_check()))
        
        results = await asyncio.gather(
            *[task for _, task in tasks], 
            return_exceptions=True
        )
        
        health_status = {}
        for i, (name, _) in enumerate(tasks):
            result = results[i]
            if isinstance(result, Exception):
                health_status[name] = False
            else:
                health_status[name] = result
        
        return health_status
    
    def cleanup(self) -> None:
        """Cleanup all adapters"""
        for adapter in self.adapters.values():
            if hasattr(adapter, 'executor'):
                adapter.executor.shutdown(wait=True)
        
        self.adapters.clear()
        self.providers.clear()