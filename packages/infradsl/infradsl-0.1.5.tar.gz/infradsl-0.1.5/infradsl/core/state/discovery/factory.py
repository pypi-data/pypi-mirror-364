"""
Factory for creating state discoverers

Provides a centralized way to create provider-specific discoverers
with support for different cloud platforms.
"""

from typing import Dict, Type
from ..interfaces.state_discoverer import StateDiscoverer
from ...interfaces.provider import ProviderInterface


# Registry will be populated as we import discoverer classes
DISCOVERER_REGISTRY: Dict[str, Type[StateDiscoverer]] = {}


def create_discoverer(provider_name: str, provider: ProviderInterface) -> StateDiscoverer:
    """
    Create a state discoverer for the given provider.
    
    Args:
        provider_name: Name of the provider (e.g., "gcp", "digitalocean", "aws")
        provider: The provider implementation
        
    Returns:
        Initialized state discoverer instance
        
    Raises:
        ValueError: If no discoverer is available for the provider
    """
    # Lazy import to avoid circular dependencies
    if not DISCOVERER_REGISTRY:
        _populate_registry()
    
    discoverer_class = DISCOVERER_REGISTRY.get(provider_name.lower())
    if not discoverer_class:
        available_providers = ", ".join(DISCOVERER_REGISTRY.keys())
        raise ValueError(
            f"No state discoverer available for provider: {provider_name}. "
            f"Available providers: {available_providers}"
        )
    
    return discoverer_class(provider)


def _populate_registry() -> None:
    """Populate the discoverer registry with available implementations."""
    try:
        from .digitalocean import DigitalOceanStateDiscoverer
        DISCOVERER_REGISTRY["digitalocean"] = DigitalOceanStateDiscoverer
    except ImportError:
        pass
    
    try:
        from .gcp import GCPStateDiscoverer
        DISCOVERER_REGISTRY["gcp"] = GCPStateDiscoverer
    except ImportError:
        pass
    
    try:
        from .aws import AWSStateDiscoverer
        DISCOVERER_REGISTRY["aws"] = AWSStateDiscoverer
    except ImportError:
        pass


def get_available_discoverers() -> list[str]:
    """
    Get list of available discoverer provider names.
    
    Returns:
        List of supported provider names
    """
    if not DISCOVERER_REGISTRY:
        _populate_registry()
    return list(DISCOVERER_REGISTRY.keys())


def register_discoverer(provider_name: str, discoverer_class: Type[StateDiscoverer]) -> None:
    """
    Register a new discoverer implementation.
    
    Args:
        provider_name: Name of the provider
        discoverer_class: Discoverer class implementing StateDiscoverer interface
        
    Raises:
        ValueError: If discoverer_class doesn't implement StateDiscoverer
    """
    if not issubclass(discoverer_class, StateDiscoverer):
        raise ValueError(
            f"Discoverer class {discoverer_class} must implement StateDiscoverer interface"
        )
    
    DISCOVERER_REGISTRY[provider_name.lower()] = discoverer_class