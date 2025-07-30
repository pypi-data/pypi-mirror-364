"""
InfraDSL Intelligent Caching Layer

This package provides comprehensive caching capabilities for InfraDSL:
- API response caching
- Resource discovery caching  
- Plan operation caching
- Provider-specific cache management
- Configurable TTL and eviction policies
"""

from .cache_manager import (
    CacheManager,
    CacheConfig,
    CacheType,
    CacheEntry,
    get_cache_manager,
    configure_cache,
    cache_async,
    cache_sync,
)

from .provider_cache import (
    ProviderCacheManager,
    get_provider_cache_manager,
    cache_provider_api,
    cache_resource_discovery,
    cache_plan_operation,
    invalidate_on_change,
    cache_provider_api_sync,
    cache_resource_discovery_sync,
    cache_plan_operation_sync,
    invalidate_on_change_sync,
    CachedProviderMixin,
)

from .postgresql_cache import (
    PostgreSQLCacheManager,
    get_postgresql_cache_manager,
    is_postgresql_cache_enabled,
)

__all__ = [
    # Cache Manager
    "CacheManager",
    "CacheConfig",
    "CacheType",
    "CacheEntry",
    "get_cache_manager",
    "configure_cache",
    "cache_async",
    "cache_sync",
    
    # Provider Cache
    "ProviderCacheManager",
    "get_provider_cache_manager",
    "cache_provider_api",
    "cache_resource_discovery",
    "cache_plan_operation",
    "invalidate_on_change",
    "cache_provider_api_sync",
    "cache_resource_discovery_sync",
    "cache_plan_operation_sync",
    "invalidate_on_change_sync",
    "CachedProviderMixin",
    
    # PostgreSQL Cache
    "PostgreSQLCacheManager",
    "get_postgresql_cache_manager",
    "is_postgresql_cache_enabled",
]