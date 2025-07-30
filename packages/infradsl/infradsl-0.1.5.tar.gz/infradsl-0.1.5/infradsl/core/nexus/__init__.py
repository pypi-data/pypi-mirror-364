"""
Nexus Engine - The heart of InfraDSL
"""

from .base_resource import (
    BaseResource,
    ResourceState,
    DriftAction,
    ResourceMetadata,
    ResourceSpec,
    ResourceStatus,
)
from .engine import (
    NexusEngine,
    NexusConfig,
    ExecutionMode,
    ResourceRegistry,
)
from .lifecycle import (
    LifecycleManager,
    ResourceGraph,
    ResourceDependency,
    DependencyType,
)
from .reconciler import (
    StateReconciler,
    ReconciliationStrategy,
    ReconciliationPlan,
    FieldChange,
)
from .provider_registry import (
    ProviderRegistry,
    ProviderMetadata,
    ProviderCapability,
    get_registry,
    register_provider,
    get_provider,
)

__all__ = [
    # Base resource classes
    "BaseResource",
    "ResourceState",
    "DriftAction",
    "ResourceMetadata",
    "ResourceSpec",
    "ResourceStatus",
    
    # Engine
    "NexusEngine",
    "NexusConfig",
    "ExecutionMode",
    "ResourceRegistry",
    
    # Lifecycle management
    "LifecycleManager",
    "ResourceGraph",
    "ResourceDependency",
    "DependencyType",
    
    # State reconciliation
    "StateReconciler",
    "ReconciliationStrategy",
    "ReconciliationPlan",
    "FieldChange",
    
    # Provider registry
    "ProviderRegistry",
    "ProviderMetadata",
    "ProviderCapability",
    "get_registry",
    "register_provider",
    "get_provider",
]