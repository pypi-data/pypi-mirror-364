"""
Provider-specific caching layer for InfraDSL

This module provides caching decorators and utilities specifically
designed for cloud provider operations.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Union, Callable, Awaitable
from functools import wraps
import logging

from .cache_manager import CacheManager, CacheType, cache_async, cache_sync, get_cache_manager
from ..interfaces.provider import ResourceQuery
from ..nexus.base_resource import ResourceMetadata

logger = logging.getLogger(__name__)


class ProviderCacheManager:
    """
    Provider-specific cache manager that understands provider patterns
    """
    
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.cache_manager = cache_manager or get_cache_manager()
    
    async def cache_api_response(
        self, 
        provider_name: str, 
        method_name: str, 
        response: Any, 
        *args, 
        **kwargs
    ) -> None:
        """Cache an API response from a provider"""
        await self.cache_manager.set(
            CacheType.API_RESPONSE,
            response,
            provider_name,
            method_name,
            *args,
            **kwargs
        )
    
    async def get_cached_api_response(
        self, 
        provider_name: str, 
        method_name: str, 
        *args, 
        **kwargs
    ) -> Optional[Any]:
        """Get cached API response"""
        return await self.cache_manager.get(
            CacheType.API_RESPONSE,
            provider_name,
            method_name,
            *args,
            **kwargs
        )
    
    async def cache_resource_discovery(
        self, 
        provider_name: str, 
        resource_type: str, 
        resources: List[Dict[str, Any]], 
        query: Optional[ResourceQuery] = None
    ) -> None:
        """Cache resource discovery results"""
        query_key = self._serialize_query(query) if query else None
        await self.cache_manager.set(
            CacheType.RESOURCE_DISCOVERY,
            resources,
            provider_name,
            resource_type,
            query_key
        )
    
    async def get_cached_resource_discovery(
        self, 
        provider_name: str, 
        resource_type: str, 
        query: Optional[ResourceQuery] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Get cached resource discovery results"""
        query_key = self._serialize_query(query) if query else None
        return await self.cache_manager.get(
            CacheType.RESOURCE_DISCOVERY,
            provider_name,
            resource_type,
            query_key
        )
    
    async def cache_plan_result(
        self, 
        provider_name: str, 
        action: str, 
        resource_type: str, 
        plan: Dict[str, Any], 
        config: Dict[str, Any], 
        metadata: Optional[ResourceMetadata] = None
    ) -> None:
        """Cache plan results"""
        metadata_key = self._serialize_metadata(metadata) if metadata else None
        await self.cache_manager.set(
            CacheType.PLAN_CACHE,
            plan,
            provider_name,
            action,
            resource_type,
            config,
            metadata_key
        )
    
    async def get_cached_plan_result(
        self, 
        provider_name: str, 
        action: str, 
        resource_type: str, 
        config: Dict[str, Any], 
        metadata: Optional[ResourceMetadata] = None
    ) -> Optional[Dict[str, Any]]:
        """Get cached plan results"""
        metadata_key = self._serialize_metadata(metadata) if metadata else None
        return await self.cache_manager.get(
            CacheType.PLAN_CACHE,
            provider_name,
            action,
            resource_type,
            config,
            metadata_key
        )
    
    async def invalidate_provider_cache(self, provider_name: str) -> None:
        """Invalidate all cache entries for a specific provider"""
        # This is a bit tricky since we need to find all entries for this provider
        # For now, we'll invalidate all cache types
        for cache_type in CacheType:
            await self.cache_manager.invalidate_type(cache_type)
    
    async def invalidate_resource_cache(
        self, 
        provider_name: str, 
        resource_type: str
    ) -> None:
        """Invalidate cache entries for a specific resource type"""
        # Invalidate discovery cache
        await self.cache_manager.invalidate(
            CacheType.RESOURCE_DISCOVERY,
            provider_name,
            resource_type,
            None  # query_key
        )
        
        # Invalidate plan cache for this resource type
        for action in ["create", "update", "delete"]:
            await self.cache_manager.invalidate(
                CacheType.PLAN_CACHE,
                provider_name,
                action,
                resource_type
            )
    
    def _serialize_query(self, query: ResourceQuery) -> str:
        """Serialize ResourceQuery to a cache key"""
        if query is None:
            return "no_query"
        
        return json.dumps(query.filters, sort_keys=True)
    
    def _serialize_metadata(self, metadata: ResourceMetadata) -> str:
        """Serialize ResourceMetadata to a cache key"""
        if metadata is None:
            return "no_metadata"
        
        return json.dumps({
            "id": metadata.id,
            "name": metadata.name,
            "project": metadata.project,
            "environment": metadata.environment,
            "labels": metadata.labels
        }, sort_keys=True)


# Global provider cache manager
_provider_cache_manager: Optional[ProviderCacheManager] = None


def get_provider_cache_manager() -> ProviderCacheManager:
    """Get the global provider cache manager"""
    global _provider_cache_manager
    if _provider_cache_manager is None:
        _provider_cache_manager = ProviderCacheManager()
    return _provider_cache_manager


# Decorators for provider methods
def cache_provider_api(provider_name: str, method_name: str):
    """Decorator for caching provider API calls"""
    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            cache_manager = get_provider_cache_manager()
            
            # Try to get from cache
            cached_result = await cache_manager.get_cached_api_response(
                provider_name, method_name, *args, **kwargs
            )
            if cached_result is not None:
                logger.debug(f"Cache hit for {provider_name}.{method_name}")
                return cached_result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {provider_name}.{method_name}")
            result = await func(*args, **kwargs)
            await cache_manager.cache_api_response(
                provider_name, method_name, result, *args, **kwargs
            )
            
            return result
        
        return wrapper
    
    return decorator


def cache_resource_discovery(provider_name: str):
    """Decorator for caching resource discovery operations"""
    def decorator(func: Callable[..., Awaitable[List[Dict[str, Any]]]]) -> Callable[..., Awaitable[List[Dict[str, Any]]]]:
        @wraps(func)
        async def wrapper(resource_type: str, query: Optional[ResourceQuery] = None, *args, **kwargs) -> List[Dict[str, Any]]:
            cache_manager = get_provider_cache_manager()
            
            # Try to get from cache
            cached_result = await cache_manager.get_cached_resource_discovery(
                provider_name, resource_type, query
            )
            if cached_result is not None:
                logger.debug(f"Cache hit for {provider_name} discovery of {resource_type}")
                return cached_result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {provider_name} discovery of {resource_type}")
            result = await func(resource_type, query, *args, **kwargs)
            await cache_manager.cache_resource_discovery(
                provider_name, resource_type, result, query
            )
            
            return result
        
        return wrapper
    
    return decorator


def cache_plan_operation(provider_name: str, action: str):
    """Decorator for caching plan operations"""
    def decorator(func: Callable[..., Awaitable[Dict[str, Any]]]) -> Callable[..., Awaitable[Dict[str, Any]]]:
        @wraps(func)
        async def wrapper(
            resource_type: str, 
            config: Dict[str, Any], 
            metadata: Optional[ResourceMetadata] = None,
            *args, 
            **kwargs
        ) -> Dict[str, Any]:
            cache_manager = get_provider_cache_manager()
            
            # Try to get from cache
            cached_result = await cache_manager.get_cached_plan_result(
                provider_name, action, resource_type, config, metadata
            )
            if cached_result is not None:
                logger.debug(f"Cache hit for {provider_name} {action} plan of {resource_type}")
                return cached_result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {provider_name} {action} plan of {resource_type}")
            result = await func(resource_type, config, metadata, *args, **kwargs)
            await cache_manager.cache_plan_result(
                provider_name, action, resource_type, result, config, metadata
            )
            
            return result
        
        return wrapper
    
    return decorator


def invalidate_on_change(provider_name: str, resource_type: str):
    """Decorator that invalidates cache when resource changes"""
    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Execute the function first
            result = await func(*args, **kwargs)
            
            # Invalidate cache for this resource type
            cache_manager = get_provider_cache_manager()
            await cache_manager.invalidate_resource_cache(provider_name, resource_type)
            
            return result
        
        return wrapper
    
    return decorator


# Sync versions of cache decorators for sync providers
def cache_provider_api_sync(provider_name: str, method_name: str):
    """Decorator for caching provider API calls (sync version)"""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            cache_manager = get_provider_cache_manager()
            
            try:
                # Try to get from cache (exclude self from cache key)
                cached_result = asyncio.run(
                    cache_manager.get_cached_api_response(
                        provider_name, method_name, *args, **kwargs
                    )
                )
                if cached_result is not None:
                    logger.debug(f"Cache hit for {provider_name}.{method_name}")
                    return cached_result
            except Exception as e:
                logger.debug(f"Error getting cache entry {e}")
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {provider_name}.{method_name}")
            result = func(self, *args, **kwargs)
            
            try:
                asyncio.run(
                    cache_manager.cache_api_response(
                        provider_name, method_name, result, *args, **kwargs
                    )
                )
            except Exception as e:
                logger.debug(f"Error setting cache entry {e}")
            
            return result
        
        return wrapper
    
    return decorator


def cache_resource_discovery_sync(provider_name: str):
    """Decorator for caching resource discovery operations (sync version)"""
    def decorator(func: Callable[..., List[Dict[str, Any]]]) -> Callable[..., List[Dict[str, Any]]]:
        @wraps(func)
        def wrapper(self, resource_type: str, query: Optional[ResourceQuery] = None, *args, **kwargs) -> List[Dict[str, Any]]:
            cache_manager = get_provider_cache_manager()
            
            try:
                # Try to get from cache
                cached_result = asyncio.run(
                    cache_manager.get_cached_resource_discovery(
                        provider_name, resource_type, query
                    )
                )
                if cached_result is not None:
                    logger.debug(f"Cache hit for {provider_name} discovery of {resource_type}")
                    return cached_result
            except Exception as e:
                logger.debug(f"Error getting cache entry {e}")
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {provider_name} discovery of {resource_type}")
            result = func(self, resource_type, query, *args, **kwargs)
            
            try:
                asyncio.run(
                    cache_manager.cache_resource_discovery(
                        provider_name, resource_type, result, query
                    )
                )
            except Exception as e:
                logger.debug(f"Error setting cache entry {e}")
            
            return result
        
        return wrapper
    
    return decorator


def cache_plan_operation_sync(provider_name: str, action: str):
    """Decorator for caching plan operations (sync version)"""
    def decorator(func: Callable[..., Dict[str, Any]]) -> Callable[..., Dict[str, Any]]:
        @wraps(func)
        def wrapper(
            self,
            resource_type: str, 
            config: Dict[str, Any], 
            metadata: Optional[ResourceMetadata] = None,
            *args, 
            **kwargs
        ) -> Dict[str, Any]:
            cache_manager = get_provider_cache_manager()
            
            # Create event loop for async operations
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Try to get from cache
                cached_result = loop.run_until_complete(
                    cache_manager.get_cached_plan_result(
                        provider_name, action, resource_type, config, metadata
                    )
                )
                if cached_result is not None:
                    logger.debug(f"Cache hit for {provider_name} {action} plan of {resource_type}")
                    return cached_result
                
                # Execute function and cache result
                logger.debug(f"Cache miss for {provider_name} {action} plan of {resource_type}")
                result = func(self, resource_type, config, metadata, *args, **kwargs)
                loop.run_until_complete(
                    cache_manager.cache_plan_result(
                        provider_name, action, resource_type, result, config, metadata
                    )
                )
                
                return result
            finally:
                loop.close()
        
        return wrapper
    
    return decorator


def invalidate_on_change_sync(provider_name: str, resource_type: str):
    """Decorator that invalidates cache when resource changes (sync version)"""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            # Execute the function first
            result = func(self, *args, **kwargs)
            
            # Create event loop for async operations
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Invalidate cache for this resource type
                cache_manager = get_provider_cache_manager()
                loop.run_until_complete(
                    cache_manager.invalidate_resource_cache(provider_name, resource_type)
                )
            finally:
                loop.close()
            
            return result
        
        return wrapper
    
    return decorator


class CachedProviderMixin:
    """
    Mixin class that adds caching capabilities to providers
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache_manager = get_provider_cache_manager()
        self._provider_name = self.__class__.__name__
    
    async def _cache_api_call(self, method_name: str, result: Any, *args, **kwargs) -> None:
        """Cache an API call result"""
        await self._cache_manager.cache_api_response(
            self._provider_name, method_name, result, *args, **kwargs
        )
    
    async def _get_cached_api_call(self, method_name: str, *args, **kwargs) -> Optional[Any]:
        """Get cached API call result"""
        return await self._cache_manager.get_cached_api_response(
            self._provider_name, method_name, *args, **kwargs
        )
    
    async def _invalidate_cache(self) -> None:
        """Invalidate all cache for this provider"""
        await self._cache_manager.invalidate_provider_cache(self._provider_name)
    
    async def _invalidate_resource_cache(self, resource_type: str) -> None:
        """Invalidate cache for a specific resource type"""
        await self._cache_manager.invalidate_resource_cache(
            self._provider_name, resource_type
        )