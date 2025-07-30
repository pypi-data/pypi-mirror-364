"""
Change Planner - analyzes current vs desired state and plans changes
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, List

from ....core.nexus.reconciler import StateReconciler
from ....core.services.state_detection import create_state_detector
from .state_analyzer import StateAnalyzer

if TYPE_CHECKING:
    from ...utils.output import Console

logger = logging.getLogger(__name__)


class ChangePlanner:
    """Plans infrastructure changes by comparing current and desired state"""

    def __init__(self):
        self.state_analyzer = StateAnalyzer()

    def plan_changes(
        self, resources: List[Any], reconciler: StateReconciler, console: "Console"
    ) -> Dict[str, List[Any]]:
        """Plan infrastructure changes"""
        changes = {"create": [], "update": [], "delete": [], "replace": []}

        for resource in resources:
            # Get current state from provider
            current_state = self._get_current_state(resource)
            desired_state = self.state_analyzer.get_desired_state(resource)

            # Determine required action
            if current_state is None:
                changes["create"].append(resource)
            elif self.state_analyzer.needs_replacement(current_state, desired_state):
                changes["replace"].append(resource)
            elif self.state_analyzer.should_recreate_for_disk_changes(
                resource, current_state, desired_state
            ):
                changes["replace"].append(resource)
            elif self.state_analyzer.needs_update(current_state, desired_state):
                changes["update"].append(resource)
            # If no changes needed, resource is not included

        console.debug(
            f"Planned changes: {len(changes['create'])} create, {len(changes['update'])} update, {len(changes['replace'])} replace"
        )
        return changes

    def _get_current_state(self, resource: Any) -> Dict[str, Any] | None:
        """Get current state of resource from provider using universal state detection"""
        try:
            # First check cache for imported resources
            cache_state = self._get_cached_state(resource)
            if cache_state is not None:
                logger.debug(f"Found cached state for resource {resource.name}")
                return cache_state

            # Check if resource has a provider attached
            if hasattr(resource, "_provider") and resource._provider:
                # Debug: check provider type
                logger.debug(f"Resource {resource.name} has provider: {type(resource._provider)} - {resource._provider}")
                
                # Skip provider detection if provider is just a string - resource is likely imported
                if isinstance(resource._provider, str):
                    logger.debug(f"Provider is string, skipping provider detection for {resource.name}")
                    return None
                    
                # Use universal state detector
                state_detector = create_state_detector(resource._provider)
                return state_detector.get_current_state(resource)

            return None
        except Exception as e:
            # Log the error but don't fail - assume resource doesn't exist
            logger.debug(f"Error checking current state for {resource.name}: {e}")
            return None

    def _get_cached_state(self, resource: Any) -> Dict[str, Any] | None:
        """Check cache for imported resource state using fingerprint lookup"""
        try:
            # First try the sync SimplePostgreSQLCache for fingerprint lookup
            fingerprint_state = self._get_fingerprint_cached_state(resource)
            if fingerprint_state:
                return fingerprint_state
                
            from ....core.cache.postgresql_cache import is_postgresql_cache_enabled, get_postgresql_cache_manager
            import asyncio

            # Fallback to async PostgreSQL cache 
            if not is_postgresql_cache_enabled():
                return None

            async def lookup_with_cleanup():
                cache_manager = await get_postgresql_cache_manager()
                
                # Primary lookup: by name and provider for all resources (not just imported)
                cached_data = await self._lookup_by_name_and_provider(cache_manager, resource.name, "gcp")
                
                if cached_data:
                    # For imported resources, trust the cache completely
                    if cached_data.get('imported'):
                        return cached_data
                    
                    # For regular resources, use state comparison
                    if self._state_matches(resource, cached_data):
                        return cached_data
                
                return None
            
            # Run the lookup with proper async handling
            cached_data = asyncio.run(lookup_with_cleanup())
            
            if cached_data:
                # Convert cached data to state format expected by apply
                return self._convert_cached_to_state(cached_data)
            
            return None
            
        except Exception as e:
            logger.debug(f"Error checking cache for {resource.name}: {e}")
            return None

    def _get_fingerprint_cached_state(self, resource: Any) -> Dict[str, Any] | None:
        """Check SimplePostgreSQLCache for imported resource state using fingerprint lookup"""
        try:
            logger.debug(f"Checking fingerprint cache for resource: {resource.name}")
            
            # Use the provider's get_resource_state method which implements fingerprint lookup
            if hasattr(resource, "_provider") and resource._provider:
                logger.debug(f"Resource {resource.name} has provider: {type(resource._provider)}")
                
                # Check if the provider has get_resource_state method (GCP provider does)
                if hasattr(resource._provider, "get_resource_state"):
                    logger.debug(f"Calling get_resource_state for {resource.name}")
                    cached_resource = resource._provider.get_resource_state(resource.metadata)
                    if cached_resource:
                        logger.debug(f"Found resource via fingerprint lookup: {resource.name}")
                        # Convert to expected state format with imported flag
                        state = self._convert_fingerprint_cache_to_state(cached_resource)
                        state['_imported_resource'] = True  # Mark as imported
                        return state
                    else:
                        logger.debug(f"No cached resource found via fingerprint for {resource.name}")
                else:
                    logger.debug(f"Provider for {resource.name} doesn't have get_resource_state method")
            else:
                logger.debug(f"Resource {resource.name} has no provider or provider is None")
            
            return None
            
        except Exception as e:
            logger.debug(f"Error checking fingerprint cache for {resource.name}: {e}")
            return None

    def _convert_fingerprint_cache_to_state(self, cached_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert fingerprint cache data to state format expected by planner"""
        state = {
            '_imported_resource': True,  # Mark as imported to avoid replacement
            'name': cached_data.get('name'),
            'region': cached_data.get('region'),
            'tags': cached_data.get('tags', {}),
            'id': cached_data.get('id'),
            'provider': cached_data.get('provider'),
            'type': cached_data.get('type'),
        }
        
        # Copy all attributes for full state comparison
        if 'attributes' in cached_data:
            state.update(cached_data['attributes'])
            
        return state

    async def _lookup_by_name_and_provider(self, cache_manager, name: str, provider: str) -> Dict[str, Any] | None:
        """Look up cached resource by name and provider in PostgreSQL"""
        try:
            if not hasattr(cache_manager, '_pool') or not cache_manager._pool:
                return None

            # Check if connection pool is still valid
            if cache_manager._pool.is_closing():
                logger.debug(f"PostgreSQL connection pool is closing, skipping cache lookup for {name}")
                return None

            async with cache_manager._pool.acquire() as conn:
                # Query the cache table for name and provider (including expired entries)
                query = """
                SELECT state_data, created_at, ttl_seconds, fingerprint,
                       (created_at + (ttl_seconds || ' seconds')::interval > NOW()) as is_valid
                FROM infradsl_resource_cache 
                WHERE state_data->>'name' = $1
                AND state_data->>'provider' = $2
                ORDER BY created_at DESC
                LIMIT 1
                """
                
                row = await conn.fetchrow(query, name, provider)
                
                if row:
                    # Parse the JSON data
                    import json
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
            import asyncpg
            if isinstance(e, asyncpg.ConnectionDoesNotExistError):
                logger.debug(f"PostgreSQL connection closed during cache lookup for {name}, skipping cache")
            elif isinstance(e, (asyncpg.PostgresError, ConnectionError)):
                logger.debug(f"PostgreSQL error during cache lookup for {name}: {e}")
            else:
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
        """Convert cached resource data to state format expected by apply"""
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
        
        # Convert tags from dict format to list format as expected by apply
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

    def _state_matches(self, resource: Any, cached_data: Dict[str, Any]) -> bool:
        """Check if resource state matches cached data"""
        try:
            # For CloudDNS resources, compare DNS-specific fields
            if resource.__class__.__name__ == "CloudDNS":
                return self._dns_state_matches(resource, cached_data)
            elif resource.__class__.__name__ == "VirtualMachine":
                return self._vm_state_matches(resource, cached_data)
            else:
                # For other resources, use basic comparison
                return self._basic_state_matches(resource, cached_data)
            
        except Exception as e:
            logger.debug(f"Error comparing states for {resource.name}: {e}")
            return False

    def _dns_state_matches(self, resource: Any, cached_data: Dict[str, Any]) -> bool:
        """Compare CloudDNS resource state with cached data"""
        try:
            # Check basic DNS properties
            if resource.spec.dns_name != cached_data.get('dns_name'):
                logger.debug(f"DNS name mismatch: {resource.spec.dns_name} != {cached_data.get('dns_name')}")
                return False
                
            if resource.spec.operation_mode.value != cached_data.get('operation_mode'):
                logger.debug(f"Operation mode mismatch: {resource.spec.operation_mode.value} != {cached_data.get('operation_mode')}")
                return False
                
            # Check existing zone name (stored as zone_id in cache)
            cached_zone = cached_data.get('zone_id') or cached_data.get('existing_zone_name') 
            if resource.spec.existing_zone_name != cached_zone:
                logger.debug(f"Existing zone mismatch: {resource.spec.existing_zone_name} != {cached_zone}")
                return False
            
            # For manage_records mode, we don't need to compare records here
            # The stateless engine should recognize this as existing and up-to-date
            logger.debug(f"DNS state matches for {resource.name}")
            return True
            
        except Exception as e:
            logger.debug(f"Error comparing DNS states: {e}")
            return False

    def _vm_state_matches(self, resource: Any, cached_data: Dict[str, Any]) -> bool:
        """Compare VirtualMachine resource state with cached data"""
        # This would implement VM-specific comparison logic
        return False

    def _basic_state_matches(self, resource: Any, cached_data: Dict[str, Any]) -> bool:
        """Basic state comparison for generic resources"""
        return resource.name == cached_data.get('name')

    def _resource_to_state(self, resource: Any) -> Dict[str, Any]:
        """Convert resource object to state dictionary for fingerprint generation"""
        # This should mirror the provider's state format
        state = {
            "name": resource.name,
            "type": resource.__class__.__name__,
        }
        
        # Add resource-specific fields based on type
        if resource.__class__.__name__ == "CloudDNS":
            state.update({
                "dns_name": resource.spec.dns_name,
                "operation_mode": resource.spec.operation_mode.value if resource.spec.operation_mode else None,
                "existing_zone_name": resource.spec.existing_zone_name,
                "dnssec_enabled": resource.spec.dnssec_enabled,
                "records": [
                    {
                        "name": record.name,
                        "type": record.type.value,
                        "ttl": record.ttl,
                        "rrdatas": record.rrdatas
                    }
                    for record in resource.spec.records
                ]
            })
        elif resource.__class__.__name__ == "VirtualMachine":
            # Add VM-specific fields
            state.update({
                "size": resource.spec.size,
                "image": resource.spec.image,
                "region": resource.metadata.annotations.get("region"),
                "zone": resource.metadata.annotations.get("zone"),
                "backups": getattr(resource.spec, "backups_enabled", False),
                "monitoring": getattr(resource.spec, "monitoring", True),
            })
        
        return state