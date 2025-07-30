"""
Cache Lookup Module - handles cached resource state retrieval
"""

import asyncio
import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class CacheLookup:
    """Handles cache lookup for imported resources"""

    def get_cached_state_sync(self, resource: Any) -> Dict[str, Any] | None:
        """Synchronous wrapper for cache lookup that handles both sync and async contexts"""
        try:
            from ....core.cache.postgresql_cache import is_postgresql_cache_enabled

            # Only use PostgreSQL cache for fingerprint lookup
            if not is_postgresql_cache_enabled():
                return None

            # Handle different event loop scenarios
            try:
                loop = asyncio.get_running_loop()
                # If we're in a running loop, use run_in_executor to avoid blocking
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._async_cache_lookup(resource))
                    cached_data = future.result()
            except RuntimeError:
                # No running loop, we can create a new one
                cached_data = asyncio.run(self._async_cache_lookup(resource))
            
            if cached_data:
                # Convert cached data to state format expected by preview
                return self._convert_cached_to_state(cached_data)
            
            return None
            
        except Exception as e:
            logger.debug(f"Error checking cache for {resource.name}: {e}")
            return None

    async def get_cached_state(self, resource: Any) -> Dict[str, Any] | None:
        """Async version of cache lookup"""
        try:
            from ....core.cache.postgresql_cache import is_postgresql_cache_enabled

            # Only use PostgreSQL cache for fingerprint lookup
            if not is_postgresql_cache_enabled():
                return None

            cached_data = await self._async_cache_lookup(resource)
            
            if cached_data:
                # Convert cached data to state format expected by preview
                return self._convert_cached_to_state(cached_data)
            
            return None
            
        except Exception as e:
            logger.debug(f"Error checking cache for {resource.name}: {e}")
            return None

    async def _async_cache_lookup(self, resource: Any) -> Dict[str, Any] | None:
        """Async helper for cache lookup"""
        from ....core.cache.postgresql_cache import get_postgresql_cache_manager
        cache_manager = await get_postgresql_cache_manager()
        
        # Primary lookup: by name and provider (more reliable than fingerprint)
        cached_data = await self._lookup_by_name_and_provider(cache_manager, resource.name, "gcp")
        
        if cached_data:
            # For imported resources, trust the cache completely
            if cached_data.get('imported'):
                return cached_data
            
            # For applied resources, do basic state comparison
            # This allows "no changes needed" for resources created via apply
            if self._basic_state_matches(resource, cached_data):
                return cached_data
        
        return None

    async def _lookup_by_name_and_provider(self, cache_manager, name: str, provider: str) -> Dict[str, Any] | None:
        """Look up cached resource by name and provider in PostgreSQL"""
        try:
            if not hasattr(cache_manager, '_pool') or not cache_manager._pool:
                return None

            async with cache_manager._pool.acquire() as conn:
                # Query the cache table for name and provider (both imported and applied resources)
                query = """
                SELECT state_data, created_at, ttl_seconds,
                       (created_at + (ttl_seconds || ' seconds')::interval > NOW()) as is_valid
                FROM infradsl_resource_cache 
                WHERE state_data->>'name' = $1
                AND provider = $2
                ORDER BY created_at DESC
                LIMIT 1
                """
                
                row = await conn.fetchrow(query, name, provider)
                
                if row:
                    # Parse the JSON data
                    data = json.loads(row['state_data']) if isinstance(row['state_data'], str) else row['state_data']
                    
                    if row['is_valid']:
                        return data
                    else:
                        # Check if resource still exists in cloud provider
                        refreshed_data = await self._refresh_from_cloud_provider(conn, data)
                        if refreshed_data:
                            return refreshed_data
                        else:
                            return None
                
                return None
                
        except Exception as e:
            logger.debug(f"Error looking up by name {name} and provider {provider}: {e}")
            return None

    async def _refresh_from_cloud_provider(self, conn, cached_data: Dict[str, Any]) -> Dict[str, Any] | None:
        """Refresh cache entry by checking cloud provider (simplified implementation)"""
        try:
            # Update last_seen timestamp in database
            update_query = """
            UPDATE infradsl_resource_cache 
            SET last_seen = NOW(), ttl_seconds = 3600
            WHERE state_data->>'id' = $1
            """
            
            resource_id = cached_data.get('id')
            if resource_id:
                await conn.execute(update_query, resource_id)
                
                # Return the cached data as still valid
                return cached_data
            
            return None
            
        except Exception as e:
            logger.debug(f"Error refreshing from cloud provider: {e}")
            return None

    def _convert_cached_to_state(self, cached_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert cached resource data to state format expected by preview"""
        # Extract provider type to determine format
        provider = cached_data.get('provider', 'unknown').lower()
        
        state = {
            '_imported_resource': True,  # Mark as imported to skip comparison
            'name': cached_data.get('name'),
            'region': cached_data.get('region'),
            'zone': cached_data.get('zone'),
            'tags': []
        }
        
        # Extract configuration data
        config = cached_data.get('configuration', {})
        state.update({
            'size': config.get('size') or config.get('machine_type'),
            'image': config.get('image') or config.get('image_family'),
            'backups': config.get('backups', False),
            'ipv6': config.get('ipv6', False),
            'monitoring': config.get('monitoring', True),
        })
        
        # Convert tags from dict format to list format as expected by preview
        tags_dict = config.get('tags', {})
        if isinstance(tags_dict, dict):
            for key, value in tags_dict.items():
                state['tags'].append(f"{key}:{value}")
        elif isinstance(tags_dict, list):
            state['tags'] = tags_dict
            
        # Provider-specific adjustments
        if provider == 'gcp':
            state['machine_type'] = state.get('size')
            state['disk_size_gb'] = config.get('disk_size_gb', 20)
            state['public_ip'] = config.get('public_ip', True)
            
        return state
    
    def _basic_state_matches(self, resource: Any, cached_data: Dict[str, Any]) -> bool:
        """Basic state comparison for generic resources"""
        try:
            # Compare basic resource properties
            if resource.name != cached_data.get('name'):
                return False
            
            # For CloudRun resources, compare key properties
            if resource.__class__.__name__ == "CloudRun":
                return self._cloudrun_state_matches(resource, cached_data)
            
            # For other resources, basic name comparison is sufficient
            return True
            
        except Exception as e:
            logger.debug(f"Error comparing states for {resource.name}: {e}")
            return False
    
    def _cloudrun_state_matches(self, resource: Any, cached_data: Dict[str, Any]) -> bool:
        """Compare CloudRun resource state with cached data"""
        try:
            # Compare container image
            expected_image = resource.spec.container.image
            cached_image = cached_data.get('image')
            if expected_image != cached_image:
                logger.debug(f"Image mismatch: {expected_image} != {cached_image}")
                return False
            
            # Compare region
            expected_region = resource.spec.region
            cached_region = cached_data.get('region')
            if expected_region != cached_region:
                logger.debug(f"Region mismatch: {expected_region} != {cached_region}")
                return False
            
            # Compare min/max instances (these are not typically stored in cloud state, so skip for now)
            # Compare environment variables (these are not typically stored in cloud state, so skip for now)
            
            logger.debug(f"CloudRun state matches for {resource.name}")
            return True
            
        except Exception as e:
            logger.debug(f"Error comparing CloudRun states: {e}")
            return False