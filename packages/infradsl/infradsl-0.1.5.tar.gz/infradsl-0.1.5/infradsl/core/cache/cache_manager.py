"""
Intelligent Caching Layer for InfraDSL

This module provides a comprehensive caching system for API responses,
resource discovery, and plan caching to improve performance.
"""

import asyncio
import hashlib
import json
import time
from typing import Any, Dict, Optional, Union, List, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CacheType(Enum):
    """Different types of cache with different TTL strategies"""
    API_RESPONSE = "api_response"
    RESOURCE_DISCOVERY = "resource_discovery"
    PLAN_CACHE = "plan_cache"
    PROVIDER_METADATA = "provider_metadata"


@dataclass
class CacheEntry:
    """Represents a cache entry with metadata"""
    key: str
    value: Any
    cache_type: CacheType
    created_at: float
    ttl: int
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return time.time() - self.created_at > self.ttl
    
    def access(self) -> None:
        """Mark cache entry as accessed"""
        self.access_count += 1
        self.last_access = time.time()


class CacheConfig:
    """Configuration for the cache system"""
    
    def __init__(self):
        # Default TTL values in seconds
        self.ttl_config = {
            CacheType.API_RESPONSE: 300,      # 5 minutes
            CacheType.RESOURCE_DISCOVERY: 180, # 3 minutes
            CacheType.PLAN_CACHE: 600,        # 10 minutes
            CacheType.PROVIDER_METADATA: 3600, # 1 hour
        }
        
        # Maximum cache size per type
        self.max_size_config = {
            CacheType.API_RESPONSE: 1000,
            CacheType.RESOURCE_DISCOVERY: 500,
            CacheType.PLAN_CACHE: 200,
            CacheType.PROVIDER_METADATA: 100,
        }
        
        # Global cache settings
        self.enable_cache = True
        self.enable_compression = True
        self.enable_statistics = True
        self.cleanup_interval = 300  # 5 minutes
    
    def get_ttl(self, cache_type: CacheType) -> int:
        """Get TTL for a specific cache type"""
        return self.ttl_config.get(cache_type, 300)
    
    def get_max_size(self, cache_type: CacheType) -> int:
        """Get max size for a specific cache type"""
        return self.max_size_config.get(cache_type, 1000)


class CacheManager:
    """
    Intelligent cache manager with TTL, LRU eviction, and statistics
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self.cache: Dict[str, CacheEntry] = {}
        self.cache_by_type: Dict[CacheType, Dict[str, CacheEntry]] = {
            cache_type: {} for cache_type in CacheType
        }
        self.statistics = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "invalidations": 0,
        }
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        # Don't start cleanup task in __init__ to avoid event loop issues
        self._cleanup_started = False
    
    def _start_cleanup_task(self):
        """Start the background cleanup task"""
        if self._cleanup_task is None and not self._cleanup_started:
            try:
                self._cleanup_task = asyncio.create_task(self._cleanup_loop())
                self._cleanup_started = True
            except RuntimeError:
                # No event loop running, cleanup will be started when needed
                pass
    
    async def _cleanup_loop(self):
        """Background task to clean up expired cache entries"""
        while True:
            try:
                await asyncio.sleep(self.config.cleanup_interval)
                await self._cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")
    
    def _generate_cache_key(self, cache_type: CacheType, *args, **kwargs) -> str:
        """Generate a cache key from arguments"""
        key_data = {
            "type": cache_type.value,
            "args": args,
            "kwargs": kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def get(self, cache_type: CacheType, *args, **kwargs) -> Optional[Any]:
        """Get value from cache"""
        if not self.config.enable_cache:
            return None
        
        # Ensure cleanup task is started
        self._start_cleanup_task()
        
        cache_key = self._generate_cache_key(cache_type, *args, **kwargs)
        
        async with self._lock:
            entry = self.cache.get(cache_key)
            if entry is None:
                self.statistics["misses"] += 1
                return None
            
            if entry.is_expired():
                await self._remove_entry(cache_key)
                self.statistics["misses"] += 1
                return None
            
            entry.access()
            self.statistics["hits"] += 1
            return entry.value
    
    async def set(self, cache_type: CacheType, value: Any, *args, **kwargs) -> None:
        """Set value in cache"""
        if not self.config.enable_cache:
            return
        
        # Ensure cleanup task is started
        self._start_cleanup_task()
        
        cache_key = self._generate_cache_key(cache_type, *args, **kwargs)
        ttl = self.config.get_ttl(cache_type)
        
        async with self._lock:
            entry = CacheEntry(
                key=cache_key,
                value=value,
                cache_type=cache_type,
                created_at=time.time(),
                ttl=ttl
            )
            
            self.cache[cache_key] = entry
            self.cache_by_type[cache_type][cache_key] = entry
            
            # Check if we need to evict entries
            await self._evict_if_needed(cache_type)
    
    async def invalidate(self, cache_type: CacheType, *args, **kwargs) -> None:
        """Invalidate specific cache entry"""
        cache_key = self._generate_cache_key(cache_type, *args, **kwargs)
        
        async with self._lock:
            if cache_key in self.cache:
                await self._remove_entry(cache_key)
                self.statistics["invalidations"] += 1
    
    async def invalidate_type(self, cache_type: CacheType) -> None:
        """Invalidate all entries of a specific type"""
        async with self._lock:
            keys_to_remove = list(self.cache_by_type[cache_type].keys())
            for key in keys_to_remove:
                await self._remove_entry(key)
            self.statistics["invalidations"] += len(keys_to_remove)
    
    async def clear(self) -> None:
        """Clear all cache entries"""
        async with self._lock:
            self.cache.clear()
            for cache_type_dict in self.cache_by_type.values():
                cache_type_dict.clear()
            self.statistics["invalidations"] += 1

    async def append_to_list(self, list_key: str, item: Any) -> None:
        """Append an item to a list cache entry (for discovery cache)"""
        async with self._lock:
            # Get existing list or create new one
            if list_key in self.cache:
                entry = self.cache[list_key]
                if isinstance(entry.value, list):
                    entry.value.append(item)
                else:
                    # Convert single item to list and append
                    entry.value = [entry.value, item]
                entry.access()
            else:
                # Create new list entry
                cache_entry = CacheEntry(
                    key=list_key,
                    value=[item],
                    cache_type=CacheType.RESOURCE_DISCOVERY,
                    created_at=time.time(),
                    ttl=3600  # 1 hour default
                )
                self.cache[list_key] = cache_entry
                self.cache_by_type[CacheType.RESOURCE_DISCOVERY][list_key] = cache_entry
    
    async def _remove_entry(self, cache_key: str) -> None:
        """Remove a cache entry"""
        entry = self.cache.pop(cache_key, None)
        if entry:
            self.cache_by_type[entry.cache_type].pop(cache_key, None)
    
    async def _evict_if_needed(self, cache_type: CacheType) -> None:
        """Evict entries if cache size exceeds limit"""
        max_size = self.config.get_max_size(cache_type)
        type_cache = self.cache_by_type[cache_type]
        
        if len(type_cache) > max_size:
            # Sort by last access time (LRU)
            sorted_entries = sorted(
                type_cache.values(), 
                key=lambda e: e.last_access
            )
            
            # Remove oldest entries
            entries_to_remove = sorted_entries[:len(type_cache) - max_size]
            for entry in entries_to_remove:
                await self._remove_entry(entry.key)
                self.statistics["evictions"] += 1
    
    async def _cleanup_expired(self) -> None:
        """Clean up expired cache entries"""
        async with self._lock:
            expired_keys = []
            for key, entry in self.cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            for key in expired_keys:
                await self._remove_entry(key)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.config.enable_statistics:
            return {}
        
        total_requests = self.statistics["hits"] + self.statistics["misses"]
        hit_rate = (self.statistics["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hits": self.statistics["hits"],
            "misses": self.statistics["misses"],
            "hit_rate": hit_rate,
            "evictions": self.statistics["evictions"],
            "invalidations": self.statistics["invalidations"],
            "total_entries": len(self.cache),
            "entries_by_type": {
                cache_type.value: len(entries)
                for cache_type, entries in self.cache_by_type.items()
            }
        }
    
    async def shutdown(self) -> None:
        """Shutdown the cache manager"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        await self.clear()


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager():
    """Get the global cache manager instance"""
    import os
    
    # Check if PostgreSQL cache is configured
    if (os.getenv("INFRADSL_CACHE_ENABLED", "false").lower() == "true" and
        os.getenv("INFRADSL_CACHE_BACKEND", "memory").lower() == "postgresql"):
        # For now, always use memory cache in CLI to avoid event loop issues
        # PostgreSQL cache is better suited for long-running services
        logger.info("Using memory cache for CLI operations (PostgreSQL cache is better for services)")
    
    # Use in-memory cache manager
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def configure_cache(config: CacheConfig) -> None:
    """Configure the global cache manager"""
    global _cache_manager
    if _cache_manager is not None:
        asyncio.create_task(_cache_manager.shutdown())
    _cache_manager = CacheManager(config)


# Decorator for caching async functions
def cache_async(cache_type: CacheType, ttl: Optional[int] = None):
    """Decorator for caching async function results"""
    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        async def wrapper(*args, **kwargs) -> Any:
            cache_manager = get_cache_manager()
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_type, func.__name__, *args, **kwargs)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_type, result, func.__name__, *args, **kwargs)
            
            return result
        
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    
    return decorator


# Decorator for caching sync functions
def cache_sync(cache_type: CacheType, ttl: Optional[int] = None):
    """Decorator for caching sync function results"""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args, **kwargs) -> Any:
            cache_manager = get_cache_manager()
            
            # Try to get from cache (we need to run this in an async context)
            loop = asyncio.get_event_loop()
            cached_result = loop.run_until_complete(
                cache_manager.get(cache_type, func.__name__, *args, **kwargs)
            )
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            loop.run_until_complete(
                cache_manager.set(cache_type, result, func.__name__, *args, **kwargs)
            )
            
            return result
        
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    
    return decorator