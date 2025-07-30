"""
Context-Aware Resource Discovery

This module provides intelligent resource discovery capabilities that optimize
API calls by using context to determine which resources to scan and how to query them.
"""

from .context_aware_discovery import (
    ContextAwareDiscoveryEngine,
    DiscoveryContext,
    DiscoveryScope,
    ContextHint,
    create_context_aware_discovery_engine,
)
from .integration import (
    DiscoveryIntegration,
    get_discovery_integration,
    discover_for_deployment,
    discover_for_monitoring,
    discover_for_cost_optimization,
    discover_minimal,
)

__all__ = [
    "ContextAwareDiscoveryEngine",
    "DiscoveryContext", 
    "DiscoveryScope",
    "ContextHint",
    "create_context_aware_discovery_engine",
    "DiscoveryIntegration",
    "get_discovery_integration",
    "discover_for_deployment",
    "discover_for_monitoring",
    "discover_for_cost_optimization",
    "discover_minimal",
]