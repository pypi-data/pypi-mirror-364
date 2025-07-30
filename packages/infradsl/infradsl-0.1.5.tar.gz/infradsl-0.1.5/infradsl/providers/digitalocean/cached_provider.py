"""
Cached DigitalOcean Provider

This module demonstrates how to integrate the intelligent caching layer
with the DigitalOcean provider for improved performance.
"""

from typing import Any, Dict, List, Optional
import logging

from .provider import DigitalOceanProvider
from ...core.cache import (
    CachedProviderMixin,
    cache_provider_api,
    cache_resource_discovery,
    cache_plan_operation,
    invalidate_on_change,
)
from ...core.interfaces.provider import ResourceQuery, ProviderConfig
from ...core.nexus.base_resource import ResourceMetadata

logger = logging.getLogger(__name__)


class CachedDigitalOceanProvider(DigitalOceanProvider, CachedProviderMixin):
    """
    DigitalOcean provider with intelligent caching capabilities
    """
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        logger.info("DigitalOcean provider initialized with caching enabled")
    
    # Cache API responses for common operations
    @cache_provider_api("digitalocean", "get_regions")
    async def get_regions(self) -> List[str]:
        """Get available regions with caching"""
        return super().get_regions()
    
    @cache_provider_api("digitalocean", "get_resource_types")
    async def get_resource_types(self) -> List[str]:
        """Get resource types with caching"""
        return super().get_resource_types()
    
    # Cache resource discovery operations
    @cache_resource_discovery("digitalocean")
    async def discover_resources(
        self, resource_type: str, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """Discover resources with caching"""
        return super().discover_resources(resource_type, query)
    
    @cache_resource_discovery("digitalocean")
    async def list_resources(
        self, resource_type: str, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """List resources with caching"""
        return super().list_resources(resource_type, query)
    
    # Cache plan operations
    @cache_plan_operation("digitalocean", "create")
    async def plan_create(
        self,
        resource_type: str,
        config: Dict[str, Any],
        metadata: ResourceMetadata,
    ) -> Dict[str, Any]:
        """Plan resource creation with caching"""
        return super().plan_create(resource_type, config, metadata)
    
    @cache_plan_operation("digitalocean", "update")
    async def plan_update(
        self,
        resource_id: str,
        resource_type: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Plan resource update with caching"""
        return super().plan_update(resource_id, resource_type, updates)
    
    @cache_plan_operation("digitalocean", "delete")
    async def plan_delete(
        self,
        resource_id: str,
        resource_type: str,
    ) -> Dict[str, Any]:
        """Plan resource deletion with caching"""
        return super().plan_delete(resource_id, resource_type)
    
    # Invalidate cache on resource changes
    @invalidate_on_change("digitalocean", "droplet")
    async def create_resource(
        self,
        resource_type: str,
        config: Dict[str, Any],
        metadata: ResourceMetadata,
    ) -> Dict[str, Any]:
        """Create resource and invalidate cache"""
        return super().create_resource(resource_type, config, metadata)
    
    @invalidate_on_change("digitalocean", "droplet")
    async def update_resource(
        self, resource_id: str, resource_type: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update resource and invalidate cache"""
        return super().update_resource(resource_id, resource_type, updates)
    
    @invalidate_on_change("digitalocean", "droplet")
    async def delete_resource(self, resource_id: str, resource_type: str) -> None:
        """Delete resource and invalidate cache"""
        return super().delete_resource(resource_id, resource_type)
    
    # Non-cached operations that need real-time data
    async def get_resource(
        self, resource_id: str, resource_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get resource - not cached to ensure real-time state"""
        return super().get_resource(resource_id, resource_type)
    
    async def tag_resource(
        self, resource_id: str, resource_type: str, tags: Dict[str, str]
    ) -> None:
        """Tag resource and invalidate cache"""
        result = super().tag_resource(resource_id, resource_type, tags)
        # Invalidate cache after tagging
        await self._invalidate_resource_cache(resource_type)
        return result
    
    # Cache cost estimation
    @cache_provider_api("digitalocean", "estimate_cost")
    async def estimate_cost(
        self, resource_type: str, config: Dict[str, Any]
    ) -> Dict[str, float]:
        """Estimate cost with caching"""
        return super().estimate_cost(resource_type, config)
    
    # Cache validation results
    @cache_provider_api("digitalocean", "validate_config")
    async def validate_config(
        self, resource_type: str, config: Dict[str, Any]
    ) -> List[str]:
        """Validate config with caching"""
        return super().validate_config(resource_type, config)
    
    async def health_check(self) -> bool:
        """Health check - not cached for real-time status"""
        return super().health_check()
    
    async def clear_cache(self) -> None:
        """Clear all cache for this provider"""
        await self._invalidate_cache()
        logger.info("Cleared all DigitalOcean provider cache")
    
    async def clear_resource_cache(self, resource_type: str) -> None:
        """Clear cache for a specific resource type"""
        await self._invalidate_resource_cache(resource_type)
        logger.info(f"Cleared DigitalOcean cache for {resource_type}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for this provider"""
        from ...core.cache import get_cache_manager
        
        cache_manager = get_cache_manager()
        return cache_manager.get_statistics()


# Factory function for creating cached provider
def create_cached_digitalocean_provider(config: ProviderConfig) -> CachedDigitalOceanProvider:
    """Create a cached DigitalOcean provider instance"""
    return CachedDigitalOceanProvider(config)