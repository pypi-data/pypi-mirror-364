"""
Cached Google Cloud Provider

This module integrates the intelligent caching layer with the GCP provider
for improved performance and reduced API calls.
"""

from typing import Any, Dict, List, Optional
import logging

from .provider import GCPComputeProvider
from ...core.cache import (
    CachedProviderMixin,
    cache_provider_api_sync,
    cache_resource_discovery_sync,
    cache_plan_operation_sync,
    invalidate_on_change_sync,
)
from ...core.interfaces.provider import ResourceQuery, ProviderConfig
from ...core.nexus.base_resource import ResourceMetadata

logger = logging.getLogger(__name__)


class CachedGCPComputeProvider(GCPComputeProvider, CachedProviderMixin):
    """
    Google Cloud provider with intelligent caching capabilities
    """
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        logger.info("GCP provider initialized with caching enabled")
    
    # Cache API responses for common operations
    @cache_provider_api_sync("gcp", "get_regions")
    def get_regions(self) -> List[str]:
        """Get available regions with caching"""
        return super().get_regions()
    
    @cache_provider_api_sync("gcp", "get_resource_types")
    def get_resource_types(self) -> List[str]:
        """Get resource types with caching"""
        return super().get_resource_types()
    
    # Cache resource discovery operations
    @cache_resource_discovery_sync("gcp")
    def discover_resources(
        self, resource_type: str, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """Discover resources with caching"""
        return super().discover_resources(resource_type, query)
    
    @cache_resource_discovery_sync("gcp")
    def list_resources(
        self, resource_type: str, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """List resources with caching"""
        return super().list_resources(resource_type, query)
    
    # Cache plan operations
    @cache_plan_operation_sync("gcp", "create")
    def plan_create(
        self,
        resource_type: str,
        config: Dict[str, Any],
        metadata: ResourceMetadata,
    ) -> Dict[str, Any]:
        """Plan resource creation with caching"""
        return super().plan_create(resource_type, config, metadata)
    
    @cache_plan_operation_sync("gcp", "update")
    def plan_update(
        self,
        resource_id: str,
        resource_type: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Plan resource update with caching"""
        return super().plan_update(resource_id, resource_type, updates)
    
    @cache_plan_operation_sync("gcp", "delete")
    def plan_delete(
        self,
        resource_id: str,
        resource_type: str,
    ) -> Dict[str, Any]:
        """Plan resource deletion with caching"""
        return super().plan_delete(resource_id, resource_type)
    
    # Invalidate cache on resource changes
    @invalidate_on_change_sync("gcp", "instance")
    @invalidate_on_change_sync("gcp", "cloud_run_service")
    @invalidate_on_change_sync("gcp", "dns_managed_zone")
    @invalidate_on_change_sync("gcp", "storage_bucket")
    @invalidate_on_change_sync("gcp", "sql_instance")
    @invalidate_on_change_sync("gcp", "compute_address")
    @invalidate_on_change_sync("gcp", "instance_group_manager")
    @invalidate_on_change_sync("gcp", "compute_network")
    @invalidate_on_change_sync("gcp", "compute_firewall")
    @invalidate_on_change_sync("gcp", "compute_router_nat")
    @invalidate_on_change_sync("gcp", "compute_network_peering")
    @invalidate_on_change_sync("gcp", "container_cluster")
    @invalidate_on_change_sync("gcp", "secret_manager_secret")
    @invalidate_on_change_sync("gcp", "compute_ssl_certificate")
    @invalidate_on_change_sync("gcp", "firebase_auth")
    @invalidate_on_change_sync("gcp", "firebase_hosting")
    def create_resource(
        self,
        resource_type: str,
        config: Dict[str, Any],
        metadata: ResourceMetadata,
    ) -> Dict[str, Any]:
        """Create resource and cache the result"""
        # Create the resource
        result = super().create_resource(resource_type, config, metadata)
        
        # Cache the created resource state
        if result:
            from ...core.cache.simple_postgres_cache import get_simple_cache
            cache = get_simple_cache()
            
            # Get resource type from annotations
            resource_type = metadata.annotations.get('resource_type', 'VirtualMachine')
            
            # Extract region from zone in annotations
            region = self.config.region or ""
            zone = metadata.annotations.get('zone')
            if zone and '-' in zone:
                region_parts = zone.split('-')
                if len(region_parts) >= 2:
                    region = '-'.join(region_parts[:-1])
            
            # Use environment from metadata
            environment = metadata.environment or getattr(metadata, 'environment', 'development')
            
            cache.cache_resource_state(
                provider="gcp",
                resource_type=resource_type,
                resource_id=result.get('id', metadata.id),
                resource_name=metadata.name,
                state_data=result,
                project=self.config.project or "",
                environment=environment,
                region=region,
                ttl_seconds=7200  # 2 hours TTL for better caching
            )
            logger.info(f"💾 Cached newly created resource: {metadata.name}")
        
        return result
    
    @invalidate_on_change_sync("gcp", "instance")
    @invalidate_on_change_sync("gcp", "cloud_run_service")
    @invalidate_on_change_sync("gcp", "dns_managed_zone")
    @invalidate_on_change_sync("gcp", "storage_bucket")
    @invalidate_on_change_sync("gcp", "sql_instance")
    @invalidate_on_change_sync("gcp", "compute_address")
    @invalidate_on_change_sync("gcp", "instance_group_manager")
    @invalidate_on_change_sync("gcp", "compute_network")
    @invalidate_on_change_sync("gcp", "compute_firewall")
    @invalidate_on_change_sync("gcp", "compute_router_nat")
    @invalidate_on_change_sync("gcp", "compute_network_peering")
    @invalidate_on_change_sync("gcp", "container_cluster")
    @invalidate_on_change_sync("gcp", "secret_manager_secret")
    @invalidate_on_change_sync("gcp", "compute_ssl_certificate")
    @invalidate_on_change_sync("gcp", "firebase_auth")
    @invalidate_on_change_sync("gcp", "firebase_hosting")
    def update_resource(
        self, resource_id: str, resource_type: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update resource and refresh cache"""
        # Perform the actual update
        result = super().update_resource(resource_id, resource_type, updates)
        
        # Refresh cache with updated state
        try:
            # Get the updated resource state
            updated_resources = self.list_resources("instance")
            for resource in updated_resources:
                if resource.get('id') == resource_id:
                    # Cache the updated resource state
                    from ...core.cache.simple_postgres_cache import get_simple_cache
                    cache = get_simple_cache()
                    
                    # Extract metadata from resource for proper cache key generation
                    resource_name = resource.get('name')
                    if resource_name:
                        # Use the same project/environment/region pattern as in get_resource_state
                        project_id = self.config.project or ""
                        environment = 'development'  # Default for now - should come from resource metadata
                        
                        # Extract region from zone
                        zone = resource.get('zone', '')
                        region = zone.rsplit('-', 1)[0] if zone and '-' in zone else self.config.region
                        
                        cache.cache_resource_state(
                            provider="gcp",
                            resource_type="VirtualMachine",
                            resource_id=resource_id,
                            resource_name=resource_name,
                            state_data=resource,
                            project=project_id,
                            environment=environment,
                            region=region,
                            ttl_seconds=7200  # 2 hours TTL
                        )
                        logger.info(f"💾 Refreshed cache for updated resource: {resource_name}")
                    break
        except Exception as e:
            logger.warning(f"Failed to refresh cache after update: {e}")
        
        return result
    
    @invalidate_on_change_sync("gcp", "instance")
    @invalidate_on_change_sync("gcp", "cloud_run_service")
    @invalidate_on_change_sync("gcp", "dns_managed_zone")
    @invalidate_on_change_sync("gcp", "storage_bucket")
    @invalidate_on_change_sync("gcp", "sql_instance")
    @invalidate_on_change_sync("gcp", "compute_address")
    @invalidate_on_change_sync("gcp", "instance_group_manager")
    @invalidate_on_change_sync("gcp", "compute_network")
    @invalidate_on_change_sync("gcp", "compute_firewall")
    @invalidate_on_change_sync("gcp", "compute_router_nat")
    @invalidate_on_change_sync("gcp", "compute_network_peering")
    @invalidate_on_change_sync("gcp", "container_cluster")
    @invalidate_on_change_sync("gcp", "secret_manager_secret")
    @invalidate_on_change_sync("gcp", "compute_ssl_certificate")
    @invalidate_on_change_sync("gcp", "firebase_auth")
    @invalidate_on_change_sync("gcp", "firebase_hosting")
    def delete_resource(self, resource_id: str, resource_type: str) -> None:
        """Delete resource and invalidate cache"""
        # First delete the resource
        super().delete_resource(resource_id, resource_type)
        
        # Remove from PostgreSQL cache
        try:
            from ...core.cache.simple_postgres_cache import get_simple_cache
            cache = get_simple_cache()
            cache.invalidate_resource("gcp", resource_type, resource_id)
            logger.info(f"🗑️ Removed {resource_type} {resource_id} from cache after deletion")
        except Exception as e:
            logger.debug(f"Failed to remove resource from cache: {e}")
    
    # Non-cached operations that need real-time data
    def get_resource(
        self, resource_id: str, resource_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get resource - not cached to ensure real-time state"""
        return super().get_resource(resource_id, resource_type)
    
    def get_resource_state(self, metadata) -> Optional[Dict[str, Any]]:
        """Get resource state with persistent cache checking"""
        from ...core.cache.simple_postgres_cache import get_simple_cache
        
        # Generate fingerprint for cache lookup
        cache = get_simple_cache()
        
        # Get resource type from annotations (set by VirtualMachine.__init__)
        resource_type = metadata.annotations.get('resource_type', 'VirtualMachine')
        
        # Extract region from zone if available in annotations
        region = self.config.region or ""
        zone = metadata.annotations.get('zone')
        
        if zone and '-' in zone:
            # Convert zone like "europe-west1-b" to region "europe-west1"
            region_parts = zone.split('-')
            if len(region_parts) >= 2:
                region = '-'.join(region_parts[:-1])
        
        # Use environment from metadata
        environment = metadata.environment or getattr(metadata, 'environment', 'development')
        
        logger.info(f"🔍 Cache lookup for {metadata.name}: provider=gcp, type={resource_type}, region={region}, env={environment}")
        
        # Get the actual project ID (after initialization it should be set)
        project_id = self.config.project or ""
        
        # Check persistent cache first
        cached_state = cache.get_resource_by_fingerprint(
            provider="gcp",
            resource_type=resource_type,
            resource_name=metadata.name,
            project=project_id,
            environment=environment,
            region=region
        )
        
        if cached_state:
            logger.info(f"✅ Cache HIT: Found {metadata.name} in persistent cache")
            return cached_state
        
        # Cache miss - check cloud provider
        logger.info(f"❌ Cache MISS: Checking cloud for {metadata.name}")
        state = super().get_resource_state(metadata)
        
        # Cache the result if found (this refreshes expired entries)
        if state:
            cache.cache_resource_state(
                provider="gcp",
                resource_type=resource_type,
                resource_id=state.get('id', metadata.id),
                resource_name=metadata.name,
                state_data=state,
                project=project_id,
                environment=environment,
                region=region,
                ttl_seconds=7200  # 2 hours TTL for better caching
            )
            logger.info(f"💾 Cached resource state for {metadata.name} (refreshed cache)")
        
        return state
    
    def tag_resource(
        self, resource_id: str, resource_type: str, tags: Dict[str, str]
    ) -> None:
        """Tag resource and invalidate cache"""
        result = super().tag_resource(resource_id, resource_type, tags)
        # Invalidate cache after tagging
        # Create event loop for async operations
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                self._invalidate_resource_cache(resource_type)
            )
        finally:
            loop.close()
        return result
    
    # Cache cost estimation
    @cache_provider_api_sync("gcp", "estimate_cost")
    def estimate_cost(
        self, resource_type: str, config: Dict[str, Any]
    ) -> Dict[str, float]:
        """Estimate cost with caching"""
        return super().estimate_cost(resource_type, config)
    
    # Cache validation results
    @cache_provider_api_sync("gcp", "validate_config")
    def validate_config(
        self, resource_type: str, config: Dict[str, Any]
    ) -> List[str]:
        """Validate config with caching"""
        return super().validate_config(resource_type, config)
    
    def clear_cache(self) -> None:
        """Clear all cache for this provider"""
        # Create event loop for async operations
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._invalidate_cache())
        finally:
            loop.close()
        logger.info("Cleared all GCP provider cache")
    
    def clear_resource_cache(self, resource_type: str) -> None:
        """Clear cache for a specific resource type"""
        # Create event loop for async operations
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._invalidate_resource_cache(resource_type))
        finally:
            loop.close()
        logger.info(f"Cleared GCP cache for {resource_type}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for this provider"""
        from ...core.cache import get_cache_manager
        
        cache_manager = get_cache_manager()
        if hasattr(cache_manager, 'get_statistics_sync'):
            return cache_manager.get_statistics_sync()
        else:
            return cache_manager.get_statistics()


# Factory function for creating cached provider
def create_cached_gcp_provider(config: ProviderConfig) -> CachedGCPComputeProvider:
    """Create a cached GCP provider instance"""
    return CachedGCPComputeProvider(config)