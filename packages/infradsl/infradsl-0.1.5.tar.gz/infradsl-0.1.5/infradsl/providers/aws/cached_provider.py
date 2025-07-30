"""
Cached AWS Provider

This module integrates the intelligent caching layer with the AWS provider
for improved performance and reduced API calls.
"""

from typing import Any, Dict, List, Optional
import logging

from .provider import AWSProvider
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


class CachedAWSProvider(AWSProvider, CachedProviderMixin):
    """
    AWS provider with intelligent caching capabilities
    """
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        logger.info("AWS provider initialized with caching enabled")
    
    # Cache API responses for common operations
    @cache_provider_api_sync("aws", "get_regions")
    def get_regions(self) -> List[str]:
        """Get available regions with caching"""
        return super().get_regions()
    
    @cache_provider_api_sync("aws", "get_resource_types")
    def get_resource_types(self) -> List[str]:
        """Get resource types with caching"""
        return super().get_resource_types()
    
    # Cache resource discovery operations
    @cache_resource_discovery_sync("aws")
    def discover_resources(
        self, resource_type: str, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """Discover resources with caching"""
        return super().discover_resources(resource_type, query)
    
    @cache_resource_discovery_sync("aws")
    def list_resources(
        self, resource_type: str, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """List resources with caching"""
        return super().list_resources(resource_type, query)
    
    # Cache plan operations
    @cache_plan_operation_sync("aws", "create")
    def plan_create(
        self,
        resource_type: str,
        config: Dict[str, Any],
        metadata: ResourceMetadata,
    ) -> Dict[str, Any]:
        """Plan resource creation with caching"""
        return super().plan_create(resource_type, config, metadata)
    
    @cache_plan_operation_sync("aws", "update")
    def plan_update(
        self,
        resource_id: str,
        resource_type: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Plan resource update with caching"""
        return super().plan_update(resource_id, resource_type, updates)
    
    @cache_plan_operation_sync("aws", "delete")
    def plan_delete(
        self,
        resource_id: str,
        resource_type: str,
    ) -> Dict[str, Any]:
        """Plan resource deletion with caching"""
        return super().plan_delete(resource_id, resource_type)
    
    # Invalidate cache on resource changes
    @invalidate_on_change_sync("aws", "ec2_instance")
    @invalidate_on_change_sync("aws", "s3_bucket")
    @invalidate_on_change_sync("aws", "cloudfront_distribution")
    @invalidate_on_change_sync("aws", "route53_zone")
    @invalidate_on_change_sync("aws", "domain_registration")
    @invalidate_on_change_sync("aws", "certificate_manager")
    @invalidate_on_change_sync("aws", "vpc")
    @invalidate_on_change_sync("aws", "security_group")
    @invalidate_on_change_sync("aws", "nat_gateway")
    @invalidate_on_change_sync("aws", "vpc_peering_connection")
    @invalidate_on_change_sync("aws", "load_balancer")
    @invalidate_on_change_sync("aws", "rds_instance")
    @invalidate_on_change_sync("aws", "lambda_function")
    @invalidate_on_change_sync("aws", "ecs_cluster")
    @invalidate_on_change_sync("aws", "eks_cluster")
    def create_resource(
        self,
        resource_type: str,
        config: Dict[str, Any],
        metadata: ResourceMetadata,
    ) -> Dict[str, Any]:
        """Create resource and invalidate cache"""
        result = super().create_resource(resource_type, config, metadata)
        
        # Cache the created resource state
        if result:
            from ...core.cache.simple_postgres_cache import get_simple_cache
            cache = get_simple_cache()
            
            # Get resource type from annotations
            resource_type_name = metadata.annotations.get('resource_type', resource_type)
            
            # Extract region from result or config
            region = result.get('Location', {}).get('LocationConstraint', '')
            if not region:
                region = self.config.region or ""
            
            # Use environment from metadata
            environment = metadata.environment or getattr(metadata, 'environment', 'development')
            
            cache.cache_resource_state(
                provider="aws",
                resource_type=resource_type_name,
                resource_id=result.get('id', metadata.id),
                resource_name=metadata.name,
                state_data=result,
                project=self.config.project or "",
                environment=environment,
                region=region,
                ttl_seconds=7200  # 2 hours TTL
            )
            logger.info(f"💾 Cached newly created resource: {metadata.name}")
        
        return result
    
    @invalidate_on_change_sync("aws", "ec2_instance")
    @invalidate_on_change_sync("aws", "s3_bucket")
    @invalidate_on_change_sync("aws", "cloudfront_distribution")
    @invalidate_on_change_sync("aws", "route53_zone")
    @invalidate_on_change_sync("aws", "domain_registration")
    @invalidate_on_change_sync("aws", "certificate_manager")
    @invalidate_on_change_sync("aws", "vpc")
    @invalidate_on_change_sync("aws", "security_group")
    @invalidate_on_change_sync("aws", "nat_gateway")
    @invalidate_on_change_sync("aws", "vpc_peering_connection")
    @invalidate_on_change_sync("aws", "load_balancer")
    @invalidate_on_change_sync("aws", "rds_instance")
    @invalidate_on_change_sync("aws", "lambda_function")
    @invalidate_on_change_sync("aws", "ecs_cluster")
    @invalidate_on_change_sync("aws", "eks_cluster")
    def update_resource(
        self, resource_id: str, resource_type: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update resource and invalidate cache"""
        result = super().update_resource(resource_id, resource_type, updates)
        
        # Refresh cache with updated state
        if result:
            from ...core.cache.simple_postgres_cache import get_simple_cache
            cache = get_simple_cache()
            cache.invalidate_resource("aws", resource_type, resource_id)
            logger.info(f"♻️ Refreshed cache for updated resource: {resource_id}")
        
        return result
    
    @invalidate_on_change_sync("aws", "ec2_instance")
    @invalidate_on_change_sync("aws", "s3_bucket")
    @invalidate_on_change_sync("aws", "cloudfront_distribution")
    @invalidate_on_change_sync("aws", "route53_zone")
    @invalidate_on_change_sync("aws", "domain_registration")
    @invalidate_on_change_sync("aws", "certificate_manager")
    @invalidate_on_change_sync("aws", "vpc")
    @invalidate_on_change_sync("aws", "security_group")
    @invalidate_on_change_sync("aws", "nat_gateway")
    @invalidate_on_change_sync("aws", "vpc_peering_connection")
    @invalidate_on_change_sync("aws", "load_balancer")
    @invalidate_on_change_sync("aws", "rds_instance")
    @invalidate_on_change_sync("aws", "lambda_function")
    @invalidate_on_change_sync("aws", "ecs_cluster")
    @invalidate_on_change_sync("aws", "eks_cluster")
    def delete_resource(self, resource_id: str, resource_type: str) -> None:
        """Delete resource and invalidate cache"""
        # First delete the resource
        super().delete_resource(resource_id, resource_type)
        
        # Remove from PostgreSQL cache
        try:
            from ...core.cache.simple_postgres_cache import get_simple_cache
            cache = get_simple_cache()
            cache.invalidate_resource("aws", resource_type, resource_id)
            logger.info(f"🗑️ Removed {resource_type} {resource_id} from cache after deletion")
        except Exception as e:
            logger.debug(f"Failed to remove resource from cache: {e}")
    
    # Non-cached operations that need real-time data
    def get_resource(
        self, resource_id: str, resource_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get resource - not cached to ensure real-time state"""
        return super().get_resource(resource_id, resource_type)
    
    # Get resource state for discovery - this should check cache first
    def get_resource_state(self, metadata: ResourceMetadata) -> Optional[Dict[str, Any]]:
        """Get resource state with intelligent caching"""
        # Create event loop for async operations
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Check cache first using deterministic fingerprint
            from ...core.cache import get_cache_manager, CacheType
            cache_manager = get_cache_manager()
            
            # Generate cache key from resource metadata
            cache_key_components = {
                "provider": "aws",
                "resource_type": metadata.type,
                "resource_name": metadata.name,
                "project": metadata.project,
                "environment": metadata.environment,
                "region": self.config.region,
            }
            
            # Try to get from cache
            cached_state = loop.run_until_complete(
                cache_manager.get(CacheType.RESOURCE_DISCOVERY, **cache_key_components)
            )
            
            if cached_state is not None:
                logger.debug(f"Cache hit for resource state: {metadata.name}")
                return cached_state
            
            # Cache miss - get from provider
            logger.debug(f"Cache miss for resource state: {metadata.name}")
            state = super().get_resource_state(metadata)
            
            # Cache the result if found
            if state:
                loop.run_until_complete(
                    cache_manager.set(
                        CacheType.RESOURCE_DISCOVERY, 
                        state,
                        **cache_key_components
                    )
                )
            
            return state
            
        finally:
            loop.close()
    
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
    @cache_provider_api_sync("aws", "estimate_cost")
    def estimate_cost(
        self, resource_type: str, config: Dict[str, Any]
    ) -> Dict[str, float]:
        """Estimate cost with caching"""
        return super().estimate_cost(resource_type, config)
    
    # Cache validation results
    @cache_provider_api_sync("aws", "validate_config")
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
        logger.info("Cleared all AWS provider cache")
    
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
        logger.info(f"Cleared AWS cache for {resource_type}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for this provider"""
        from ...core.cache import get_cache_manager
        
        cache_manager = get_cache_manager()
        if hasattr(cache_manager, 'get_statistics_sync'):
            return cache_manager.get_statistics_sync()
        else:
            return cache_manager.get_statistics()


# Factory function for creating cached provider
def create_cached_aws_provider(config: ProviderConfig) -> CachedAWSProvider:
    """Create a cached AWS provider instance"""
    return CachedAWSProvider(config)