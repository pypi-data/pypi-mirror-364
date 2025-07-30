"""
Integration utilities for context-aware discovery

This module provides utilities to integrate context-aware discovery
with the existing provider system and cache layer.
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta

from .context_aware_discovery import (
    ContextAwareDiscoveryEngine,
    DiscoveryContext,
    DiscoveryScope,
    ContextHint,
)
from ..nexus.provider_registry import get_registry
from ..cache import get_cache_manager, CacheType


logger = logging.getLogger(__name__)


class DiscoveryIntegration:
    """Integration layer for context-aware discovery"""

    def __init__(self):
        self.engine = ContextAwareDiscoveryEngine()
        self.provider_registry = get_registry()
        self.cache_manager = get_cache_manager()
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the discovery integration"""
        if self._initialized:
            return

        # Register all available providers
        providers = self.provider_registry.list_providers()
        for provider in providers:
            # Note: This would need actual provider instances, not metadata
            # For now, we'll skip provider registration and let the engine handle it
            pass

        self._initialized = True
        logger.info(
            f"Discovery integration initialized with {len(providers)} providers"
        )

    async def discover_for_deployment(
        self, project: str, environment: str, region: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Discover resources optimized for deployment scenarios

        Args:
            project: Target project name
            environment: Target environment
            region: Optional region filter

        Returns:
            List of deployment-relevant resources
        """
        self.initialize()

        context = DiscoveryContext(
            project=project,
            environment=environment,
            region=region,
            hints={ContextHint.DEPLOYMENT},
            scope=DiscoveryScope.SELECTIVE,
            use_cache=True,
            parallel_discovery=True,
        )

        return await self.engine.discover_resources(context)

    async def discover_for_monitoring(
        self,
        project: Optional[str] = None,
        environment: Optional[str] = None,
        max_age_minutes: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Discover resources optimized for monitoring scenarios

        Args:
            project: Optional project filter
            environment: Optional environment filter
            max_age_minutes: Maximum age of cached results in minutes

        Returns:
            List of monitoring-relevant resources
        """
        self.initialize()

        context = DiscoveryContext(
            project=project,
            environment=environment,
            hints={ContextHint.MONITORING, ContextHint.DEPLOYMENT},
            scope=DiscoveryScope.SELECTIVE,
            max_age=timedelta(minutes=max_age_minutes),
            use_cache=True,
            parallel_discovery=True,
        )

        return await self.engine.discover_resources(context)

    async def discover_for_cost_optimization(
        self, project: Optional[str] = None, region: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Discover resources optimized for cost analysis

        Args:
            project: Optional project filter
            region: Optional region filter

        Returns:
            List of cost-relevant resources
        """
        self.initialize()

        context = DiscoveryContext(
            project=project,
            region=region,
            hints={ContextHint.COST_OPTIMIZATION},
            scope=DiscoveryScope.COMPREHENSIVE,
            use_cache=True,
            parallel_discovery=True,
        )

        return await self.engine.discover_resources(context)

    async def discover_specific_resources(
        self,
        resource_types: List[str],
        project: Optional[str] = None,
        environment: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Discover specific resource types with filters

        Args:
            resource_types: List of resource types to discover
            project: Optional project filter
            environment: Optional environment filter
            tags: Optional tag filters

        Returns:
            List of matching resources
        """
        self.initialize()

        context = DiscoveryContext(
            project=project,
            environment=environment,
            resource_types=set(resource_types),
            tags=tags,
            scope=DiscoveryScope.SELECTIVE,
            use_cache=True,
            parallel_discovery=True,
        )

        return await self.engine.discover_resources(context)

    async def discover_minimal(
        self, project: str, environment: str, hint: Optional[ContextHint] = None
    ) -> List[Dict[str, Any]]:
        """
        Minimal discovery for quick resource overview

        Args:
            project: Target project name
            environment: Target environment
            hint: Optional context hint to guide discovery

        Returns:
            List of essential resources
        """
        self.initialize()

        hints = {hint} if hint else {ContextHint.DEPLOYMENT}

        context = DiscoveryContext(
            project=project,
            environment=environment,
            hints=hints,
            scope=DiscoveryScope.MINIMAL,
            use_cache=True,
            parallel_discovery=True,
        )

        return await self.engine.discover_resources(context)

    async def discover_comprehensive(
        self, providers: Optional[List[str]] = None, region: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Comprehensive discovery across all resources

        Args:
            providers: Optional list of providers to scan
            region: Optional region filter

        Returns:
            List of all discovered resources
        """
        self.initialize()

        context = DiscoveryContext(
            region=region,
            scope=DiscoveryScope.COMPREHENSIVE,
            use_cache=True,
            parallel_discovery=True,
        )

        return await self.engine.discover_resources(context, providers)

    async def clear_discovery_cache(
        self, project: Optional[str] = None, environment: Optional[str] = None
    ) -> None:
        """
        Clear discovery cache for specific contexts

        Args:
            project: Optional project filter
            environment: Optional environment filter
        """
        if project or environment:
            # Clear specific cache entries
            # This is a simplified implementation
            await self.cache_manager.invalidate_type(CacheType.RESOURCE_DISCOVERY)
        else:
            # Clear all discovery cache
            await self.cache_manager.invalidate_type(CacheType.RESOURCE_DISCOVERY)

        logger.info("Discovery cache cleared")

    def get_discovery_statistics(self) -> Dict[str, Any]:
        """
        Get discovery statistics

        Returns:
            Dictionary of discovery statistics
        """
        cache_stats = self.cache_manager.get_statistics()

        # Filter for discovery-related statistics
        discovery_stats = {
            "cache_enabled": self.cache_manager.config.enable_cache,
            "discovery_entries": cache_stats.get("entries_by_type", {}).get(
                CacheType.RESOURCE_DISCOVERY.value, 0
            ),
            "total_cache_entries": cache_stats.get("total_entries", 0),
            "cache_hit_rate": cache_stats.get("hit_rate", "0%"),
            "providers_registered": len(self.provider_registry.list_providers()),
            "discovery_initialized": self._initialized,
        }

        return discovery_stats


# Global discovery integration instance
_discovery_integration = None


def get_discovery_integration() -> DiscoveryIntegration:
    """Get the global discovery integration instance"""
    global _discovery_integration
    if _discovery_integration is None:
        _discovery_integration = DiscoveryIntegration()
    return _discovery_integration


# Convenience functions for common discovery scenarios
async def discover_for_deployment(
    project: str, environment: str, region: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Convenience function for deployment discovery"""
    integration = get_discovery_integration()
    return await integration.discover_for_deployment(project, environment, region)


async def discover_for_monitoring(
    project: Optional[str] = None,
    environment: Optional[str] = None,
    max_age_minutes: int = 30,
) -> List[Dict[str, Any]]:
    """Convenience function for monitoring discovery"""
    integration = get_discovery_integration()
    return await integration.discover_for_monitoring(
        project, environment, max_age_minutes
    )


async def discover_for_cost_optimization(
    project: Optional[str] = None, region: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Convenience function for cost optimization discovery"""
    integration = get_discovery_integration()
    return await integration.discover_for_cost_optimization(project, region)


async def discover_minimal(
    project: str, environment: str, hint: Optional[ContextHint] = None
) -> List[Dict[str, Any]]:
    """Convenience function for minimal discovery"""
    integration = get_discovery_integration()
    return await integration.discover_minimal(project, environment, hint)
