"""
In-memory state storage implementation

Provides fast, temporary storage for resource state during CLI operations.
Data is lost when the process exits - suitable for stateless operations.
"""

from typing import Dict, Any, Optional
from ..interfaces.state_storage import StateStorage


class MemoryStorage(StateStorage):
    """
    In-memory storage backend for resource state.
    
    Fast and lightweight, but data is not persisted across
    process restarts. Ideal for stateless CLI operations.
    """
    
    def __init__(self):
        """Initialize empty in-memory storage."""
        self._storage: Dict[str, Dict[str, Any]] = {}
    
    def get(self, resource_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve state for a specific resource.
        
        Args:
            resource_name: Name of the resource
            
        Returns:
            Resource state dictionary or None if not found
        """
        return self._storage.get(resource_name)
    
    def set(self, resource_name: str, state: Dict[str, Any]) -> None:
        """
        Store state for a specific resource.
        
        Args:
            resource_name: Name of the resource
            state: Resource state dictionary
        """
        self._storage[resource_name] = state.copy()
    
    def delete(self, resource_name: str) -> bool:
        """
        Delete state for a specific resource.
        
        Args:
            resource_name: Name of the resource
            
        Returns:
            True if resource was deleted, False if not found
        """
        if resource_name in self._storage:
            del self._storage[resource_name]
            return True
        return False
    
    def list_all(self) -> Dict[str, Dict[str, Any]]:
        """
        List all stored resource states.
        
        Returns:
            Dictionary mapping resource names to their states
        """
        return {name: state.copy() for name, state in self._storage.items()}
    
    def clear(self) -> None:
        """Clear all stored states."""
        self._storage.clear()
    
    def exists(self, resource_name: str) -> bool:
        """
        Check if state exists for a resource.
        
        Args:
            resource_name: Name of the resource
            
        Returns:
            True if state exists, False otherwise
        """
        return resource_name in self._storage
    
    def size(self) -> int:
        """
        Get the number of stored resources.
        
        Returns:
            Number of resources in storage
        """
        return len(self._storage)