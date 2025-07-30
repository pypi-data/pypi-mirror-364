"""
Factory for creating state storage backends

Provides a centralized way to create storage instances with
support for different backend types and configurations.
"""

from typing import Dict, Type, Any
from ..interfaces.state_storage import StateStorage
from .memory import MemoryStorage
from .file import FileStorage


# Registry of available storage backends
STORAGE_REGISTRY: Dict[str, Type[StateStorage]] = {
    "memory": MemoryStorage,
    "file": FileStorage,
    # Future backends can be added here:
    # "database": DatabaseStorage,
    # "redis": RedisStorage,
}


def create_storage(backend_type: str, **kwargs: Any) -> StateStorage:
    """
    Create a state storage backend instance.
    
    Args:
        backend_type: Type of storage backend ("memory", "file", "database")
        **kwargs: Additional arguments passed to storage constructor
        
    Returns:
        Initialized storage backend instance
        
    Raises:
        ValueError: If backend_type is not supported
    """
    backend_class = STORAGE_REGISTRY.get(backend_type.lower())
    if not backend_class:
        available_backends = ", ".join(STORAGE_REGISTRY.keys())
        raise ValueError(
            f"Unsupported storage backend: {backend_type}. "
            f"Available backends: {available_backends}"
        )
    
    return backend_class(**kwargs)


def get_available_backends() -> list[str]:
    """
    Get list of available storage backend types.
    
    Returns:
        List of supported backend type names
    """
    return list(STORAGE_REGISTRY.keys())


def register_storage_backend(name: str, backend_class: Type[StateStorage]) -> None:
    """
    Register a new storage backend type.
    
    Args:
        name: Name for the backend type
        backend_class: Storage class implementing StateStorage interface
        
    Raises:
        ValueError: If backend_class doesn't implement StateStorage
    """
    if not issubclass(backend_class, StateStorage):
        raise ValueError(
            f"Backend class {backend_class} must implement StateStorage interface"
        )
    
    STORAGE_REGISTRY[name.lower()] = backend_class