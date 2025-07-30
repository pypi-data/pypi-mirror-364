"""
InfraDSL Core - The foundational components of the InfraDSL framework
"""

from .nexus import *
from .interfaces import *
from .exceptions import *

__version__ = "0.1.0"
__all__ = [
    # Re-export from nexus
    "BaseResource",
    "ResourceState",
    "DriftAction",
    "ResourceMetadata",
    "ResourceSpec",
    "ResourceStatus",
    "NexusEngine",
    "NexusConfig",
    "ExecutionMode",
    "ResourceRegistry",
    "LifecycleManager",
    "ResourceGraph",
    "ResourceDependency",
    "DependencyType",
    "StateReconciler",
    "ReconciliationStrategy",
    "ReconciliationPlan",
    "FieldChange",
    "ProviderRegistry",
    "ProviderMetadata",
    "ProviderCapability",
    "get_registry",
    "register_provider",
    "get_provider",
    # Re-export from interfaces
    "ProviderInterface",
    "ProviderType",
    "ProviderConfig",
    "ResourceQuery",
    # Re-export from exceptions
    "NexusException",
    "ResourceException",
    "ProviderException",
    "ValidationException",
    "DriftException",
    "StateException",
]
