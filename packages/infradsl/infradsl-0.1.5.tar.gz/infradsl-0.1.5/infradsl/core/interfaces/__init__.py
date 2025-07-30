"""
Core interfaces for InfraDSL
"""

from .provider import (
    ProviderInterface,
    ProviderType,
    ProviderConfig,
    ResourceQuery,
)

__all__ = [
    "ProviderInterface",
    "ProviderType",
    "ProviderConfig",
    "ResourceQuery",
]