"""
Context-Aware Selective Discovery Engine

This module implements intelligent resource discovery that optimizes API calls
by using context to determine which resources to scan and how to query them.
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime, timedelta

from ..interfaces.provider import ProviderInterface, ResourceQuery
from ..cache import get_cache_manager, CacheType
from ..state.interfaces.state_discoverer import StateDiscoverer
from ..state.discovery.factory import create_discoverer


logger = logging.getLogger(__name__)


class DiscoveryScope(Enum):
    """Discovery scope levels"""

    MINIMAL = "minimal"  # Only essential resources
    SELECTIVE = "selective"  # Context-based resource selection
    COMPREHENSIVE = "comprehensive"  # Full resource discovery


class ContextHint(Enum):
    """Context hints for optimizing discovery"""

    DEPLOYMENT = "deployment"  # Focus on compute resources
    MONITORING = "monitoring"  # Focus on observability resources
    NETWORKING = "networking"  # Focus on network resources
    STORAGE = "storage"  # Focus on storage resources
    DATABASE = "database"  # Focus on database resources
    SECURITY = "security"  # Focus on security resources
    COST_OPTIMIZATION = "cost"  # Focus on cost-related resources


@dataclass
class DiscoveryContext:
    """Context information for selective discovery"""

    # Basic context
    project: Optional[str] = None
    environment: Optional[str] = None
    region: Optional[str] = None

    # Resource filters
    resource_types: Optional[Set[str]] = None
    tags: Optional[Dict[str, str]] = None

    # Discovery hints
    hints: Optional[Set[ContextHint]] = None
    scope: DiscoveryScope = DiscoveryScope.SELECTIVE

    # Time-based context
    last_discovery: Optional[datetime] = None
    max_age: Optional[timedelta] = None

    # Performance optimizations
    use_cache: bool = True
    parallel_discovery: bool = True
    max_concurrent_requests: int = 10


class ContextAwareDiscoveryEngine:
    """
    Intelligent discovery engine that uses context to optimize resource scanning
    """

    def __init__(self):
        self.cache_manager = get_cache_manager()
        self.providers: Dict[str, ProviderInterface] = {}
        self.discoverers: Dict[str, StateDiscoverer] = {}

        # Resource type priorities for different contexts
        self.context_priorities = {
            ContextHint.DEPLOYMENT: {
                "droplet": 1,
                "instance": 1,
                "kubernetes_cluster": 1,
                "load_balancer": 2,
                "database": 3,
            },
            ContextHint.MONITORING: {
                "monitoring_service": 1,
                "alert_policy": 1,
                "log_sink": 2,
                "dashboard": 2,
            },
            ContextHint.NETWORKING: {
                "vpc": 1,
                "subnet": 1,
                "firewall": 1,
                "load_balancer": 2,
                "dns_zone": 2,
            },
            ContextHint.STORAGE: {
                "volume": 1,
                "bucket": 1,
                "snapshot": 2,
                "backup": 2,
            },
            ContextHint.DATABASE: {
                "database": 1,
                "managed_database": 1,
                "database_cluster": 1,
                "database_replica": 2,
            },
            ContextHint.SECURITY: {
                "firewall": 1,
                "security_group": 1,
                "iam_role": 1,
                "key_pair": 2,
                "certificate": 2,
            },
            ContextHint.COST_OPTIMIZATION: {
                "droplet": 1,
                "instance": 1,
                "database": 1,
                "volume": 2,
                "snapshot": 3,
            },
        }

    def register_provider(self, name: str, provider: ProviderInterface) -> None:
        """Register a provider for discovery"""
        self.providers[name] = provider
        try:
            self.discoverers[name] = create_discoverer(name, provider)
        except ValueError as e:
            logger.warning(f"No discoverer available for provider {name}: {e}")

    async def discover_resources(
        self, context: DiscoveryContext, providers: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Discover resources using context-aware selective discovery

        Args:
            context: Discovery context with filters and hints
            providers: Optional list of provider names to scan

        Returns:
            List of discovered resources
        """
        if providers is None:
            providers = list(self.providers.keys())

        # Check cache first if enabled
        if context.use_cache:
            cached_results = await self._check_cache(context, providers)
            if cached_results:
                logger.info(f"Retrieved {len(cached_results)} resources from cache")
                return cached_results

        # Determine optimal discovery strategy
        discovery_plan = self._create_discovery_plan(context, providers)

        # Execute discovery
        all_resources = []
        if context.parallel_discovery:
            all_resources = await self._parallel_discovery(discovery_plan, context)
        else:
            all_resources = await self._sequential_discovery(discovery_plan, context)

        # Apply post-discovery filters
        filtered_resources = self._apply_context_filters(all_resources, context)

        # Cache results if enabled
        if context.use_cache:
            await self._cache_results(context, providers, filtered_resources)

        logger.info(
            f"Discovered {len(filtered_resources)} resources using context-aware discovery"
        )
        return filtered_resources

    def _create_discovery_plan(
        self, context: DiscoveryContext, providers: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Create optimized discovery plan based on context"""
        plan = {}

        for provider_name in providers:
            if provider_name not in self.providers:
                continue

            provider = self.providers[provider_name]

            # Determine resource types to scan
            resource_types = self._determine_resource_types(context, provider)

            # Create queries for each resource type
            queries = {}
            for resource_type in resource_types:
                query = self._create_resource_query(context, resource_type)
                queries[resource_type] = query

            plan[provider_name] = {
                "resource_types": resource_types,
                "queries": queries,
                "priority": self._calculate_provider_priority(context, provider_name),
            }

        return plan

    def _determine_resource_types(
        self, context: DiscoveryContext, provider: ProviderInterface
    ) -> List[str]:
        """Determine which resource types to scan based on context"""

        # Get all available resource types for provider
        available_types = provider.get_resource_types()

        # If specific resource types are requested, filter to those
        if context.resource_types:
            available_types = [
                rt for rt in available_types if rt in context.resource_types
            ]

        # Apply context hints to prioritize resource types
        if context.hints and context.scope != DiscoveryScope.COMPREHENSIVE:
            prioritized_types = self._prioritize_resource_types(
                available_types, context.hints
            )

            if context.scope == DiscoveryScope.MINIMAL:
                # Only return top priority resources
                return prioritized_types[:3]
            elif context.scope == DiscoveryScope.SELECTIVE:
                # Return prioritized list (but include all types)
                return prioritized_types

        return available_types

    def _prioritize_resource_types(
        self, resource_types: List[str], hints: Set[ContextHint]
    ) -> List[str]:
        """Prioritize resource types based on context hints"""

        # Calculate priority scores for each resource type
        type_scores = {}
        for resource_type in resource_types:
            score = 0
            for hint in hints:
                if hint in self.context_priorities:
                    score += self.context_priorities[hint].get(resource_type, 0)
            type_scores[resource_type] = score

        # Sort by priority score (descending)
        return sorted(resource_types, key=lambda t: type_scores.get(t, 0), reverse=True)

    def _create_resource_query(
        self, context: DiscoveryContext, resource_type: str
    ) -> ResourceQuery:
        """Create optimized resource query based on context"""
        query = ResourceQuery()

        # Apply context filters
        if context.project:
            query.by_project(context.project)

        if context.environment:
            query.by_environment(context.environment)

        if context.tags:
            query.by_labels(**context.tags)

        query.by_type(resource_type)

        return query

    def _calculate_provider_priority(
        self, context: DiscoveryContext, provider_name: str
    ) -> int:
        """Calculate priority for provider based on context"""
        # For now, simple priority based on provider type
        priorities = {
            "digitalocean": 1,
            "aws": 2,
            "gcp": 3,
            "azure": 4,
        }
        return priorities.get(provider_name, 999)

    async def _parallel_discovery(
        self, discovery_plan: Dict[str, Dict[str, Any]], context: DiscoveryContext
    ) -> List[Dict[str, Any]]:
        """Execute discovery in parallel across providers"""
        import asyncio

        tasks = []
        for provider_name, plan in discovery_plan.items():
            if provider_name in self.discoverers:
                task = asyncio.create_task(
                    self._discover_provider_resources(provider_name, plan, context)
                )
                tasks.append(task)

        # Execute with concurrency limit
        semaphore = asyncio.Semaphore(context.max_concurrent_requests)

        async def bounded_discovery(task):
            async with semaphore:
                return await task

        bounded_tasks = [bounded_discovery(task) for task in tasks]
        results = await asyncio.gather(*bounded_tasks, return_exceptions=True)

        # Flatten results and filter out exceptions
        all_resources = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Discovery task failed: {result}")
            elif isinstance(result, list):
                all_resources.extend(result)
            else:
                logger.warning(f"Unexpected result type: {type(result)}")

        return all_resources

    async def _sequential_discovery(
        self, discovery_plan: Dict[str, Dict[str, Any]], context: DiscoveryContext
    ) -> List[Dict[str, Any]]:
        """Execute discovery sequentially"""
        all_resources = []

        # Sort providers by priority
        sorted_providers = sorted(
            discovery_plan.items(), key=lambda x: x[1]["priority"]
        )

        for provider_name, plan in sorted_providers:
            if provider_name in self.discoverers:
                try:
                    resources = await self._discover_provider_resources(
                        provider_name, plan, context
                    )
                    all_resources.extend(resources)
                except Exception as e:
                    logger.error(f"Discovery failed for provider {provider_name}: {e}")

        return all_resources

    async def _discover_provider_resources(
        self, provider_name: str, plan: Dict[str, Any], context: DiscoveryContext
    ) -> List[Dict[str, Any]]:
        """Discover resources for a specific provider"""
        provider = self.providers[provider_name]
        discoverer = self.discoverers[provider_name]

        resources = []

        # Use discoverer if available, otherwise fall back to provider
        if discoverer:
            # Get all managed resources and filter by context
            all_resources = discoverer.discover_resources()

            # Filter by resource types in plan
            resource_types = set(plan["resource_types"])
            for resource in all_resources:
                if self._matches_resource_type(resource, resource_types):
                    resources.append(resource)
        else:
            # Fall back to provider list_resources
            for resource_type in plan["resource_types"]:
                query = plan["queries"][resource_type]
                try:
                    type_resources = provider.list_resources(resource_type, query)
                    resources.extend(type_resources)
                except Exception as e:
                    logger.debug(
                        f"Failed to discover {resource_type} from {provider_name}: {e}"
                    )

        return resources

    def _matches_resource_type(
        self, resource: Dict[str, Any], resource_types: Set[str]
    ) -> bool:
        """Check if resource matches any of the target resource types"""
        resource_type = resource.get("type", "").lower()

        # Map common resource types
        type_mappings = {
            "virtualmachine": "droplet",
            "manageddatabase": "managed_database",
            "database": "database",
        }

        mapped_type = type_mappings.get(resource_type, resource_type)
        return mapped_type in resource_types

    def _apply_context_filters(
        self, resources: List[Dict[str, Any]], context: DiscoveryContext
    ) -> List[Dict[str, Any]]:
        """Apply additional context-based filters to resources"""
        filtered = []

        for resource in resources:
            # Apply region filter
            if context.region:
                if resource.get("region") != context.region:
                    continue

            # Apply time-based filters
            if context.max_age and context.last_discovery:
                discovered_at = resource.get("discovered_at")
                if discovered_at:
                    try:
                        discovery_time = datetime.fromisoformat(
                            discovered_at.replace("Z", "+00:00")
                        )
                        if discovery_time < context.last_discovery - context.max_age:
                            continue
                    except ValueError:
                        # Invalid datetime format, skip filter
                        pass

            # Apply tag filters
            if context.tags:
                resource_tags = resource.get("tags", {})
                if isinstance(resource_tags, list):
                    # Convert list of tags to dict
                    tag_dict = {}
                    for tag in resource_tags:
                        if ":" in tag:
                            key, value = tag.split(":", 1)
                            tag_dict[key] = value
                    resource_tags = tag_dict

                # Check if all required tags are present
                matches = True
                for key, value in context.tags.items():
                    if key not in resource_tags or resource_tags[key] != value:
                        matches = False
                        break

                if not matches:
                    continue

            filtered.append(resource)

        return filtered

    async def _check_cache(
        self, context: DiscoveryContext, providers: List[str]
    ) -> Optional[List[Dict[str, Any]]]:
        """Check cache for existing discovery results"""
        cache_key = self._generate_cache_key(context, providers)
        cached_data = await self.cache_manager.get(
            CacheType.RESOURCE_DISCOVERY, cache_key
        )

        if cached_data:
            # Check if cached data is still valid
            if self._is_cache_valid(cached_data, context):
                return cached_data.get("resources", [])

        return None

    async def _cache_results(
        self,
        context: DiscoveryContext,
        providers: List[str],
        resources: List[Dict[str, Any]],
    ) -> None:
        """Cache discovery results"""
        cache_key = self._generate_cache_key(context, providers)
        cache_data = {
            "resources": resources,
            "timestamp": datetime.utcnow().isoformat(),
            "context": {
                "project": context.project,
                "environment": context.environment,
                "region": context.region,
                "scope": context.scope.value,
                "hints": [h.value for h in context.hints] if context.hints else None,
            },
        }

        await self.cache_manager.set(
            CacheType.RESOURCE_DISCOVERY, cache_data, cache_key
        )

    def _generate_cache_key(
        self, context: DiscoveryContext, providers: List[str]
    ) -> str:
        """Generate cache key for discovery context"""
        key_parts = [
            f"discovery",
            f"providers:{','.join(sorted(providers))}",
            f"project:{context.project or 'all'}",
            f"env:{context.environment or 'all'}",
            f"region:{context.region or 'all'}",
            f"scope:{context.scope.value}",
        ]

        if context.hints:
            hint_str = ",".join(sorted(h.value for h in context.hints))
            key_parts.append(f"hints:{hint_str}")

        if context.resource_types:
            types_str = ",".join(sorted(context.resource_types))
            key_parts.append(f"types:{types_str}")

        return ":".join(key_parts)

    def _is_cache_valid(
        self, cached_data: Dict[str, Any], context: DiscoveryContext
    ) -> bool:
        """Check if cached data is still valid for the given context"""
        if not cached_data.get("timestamp"):
            return False

        try:
            cached_time = datetime.fromisoformat(cached_data["timestamp"])

            # Check if cache is too old
            if context.max_age:
                if datetime.utcnow() - cached_time > context.max_age:
                    return False

            # Check if context has changed significantly
            cached_context = cached_data.get("context", {})
            if cached_context.get("project") != context.project:
                return False
            if cached_context.get("environment") != context.environment:
                return False
            if cached_context.get("region") != context.region:
                return False

            return True
        except (ValueError, TypeError):
            return False


# Factory function for creating discovery engine
def create_context_aware_discovery_engine() -> ContextAwareDiscoveryEngine:
    """Create a new context-aware discovery engine instance"""
    return ContextAwareDiscoveryEngine()
