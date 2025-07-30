"""
Storage backend interface for state persistence

Defines the contract for different state storage implementations,
allowing pluggable backends for memory, file, database, etc.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime


class StateStorage(ABC):
    """
    Abstract base class for state storage backends.
    
    Provides a consistent interface for storing and retrieving
    resource state across different storage mechanisms.
    """
    
    @abstractmethod
    def get(self, resource_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve state for a specific resource.
        
        Args:
            resource_name: Name of the resource
            
        Returns:
            Resource state dictionary or None if not found
        """
        pass
    
    @abstractmethod
    def set(self, resource_name: str, state: Dict[str, Any]) -> None:
        """
        Store state for a specific resource.
        
        Args:
            resource_name: Name of the resource
            state: Resource state dictionary
        """
        pass
    
    @abstractmethod
    def delete(self, resource_name: str) -> bool:
        """
        Delete state for a specific resource.
        
        Args:
            resource_name: Name of the resource
            
        Returns:
            True if resource was deleted, False if not found
        """
        pass
    
    @abstractmethod
    def list_all(self) -> Dict[str, Dict[str, Any]]:
        """
        List all stored resource states.
        
        Returns:
            Dictionary mapping resource names to their states
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """
        Clear all stored states.
        """
        pass
    
    @abstractmethod
    def exists(self, resource_name: str) -> bool:
        """
        Check if state exists for a resource.
        
        Args:
            resource_name: Name of the resource
            
        Returns:
            True if state exists, False otherwise
        """
        pass
    
    def update_metadata(self, resource_name: str, metadata: Dict[str, Any]) -> None:
        """
        Update metadata for an existing resource state.
        
        Args:
            resource_name: Name of the resource
            metadata: Metadata dictionary to merge
        """
        current_state = self.get(resource_name)
        if current_state:
            current_state.setdefault("metadata", {}).update(metadata)
            current_state["updated_at"] = datetime.utcnow().isoformat()
            self.set(resource_name, current_state)
    
    def get_by_provider(self, provider_name: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all resources for a specific provider.
        
        Args:
            provider_name: Name of the provider (e.g., "gcp", "digitalocean")
            
        Returns:
            Dictionary of resources from the specified provider
        """
        all_resources = self.list_all()
        return {
            name: state 
            for name, state in all_resources.items()
            if state.get("provider") == provider_name
        }
    
    def get_by_project(self, project_name: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all resources for a specific project.
        
        Args:
            project_name: Name of the project
            
        Returns:
            Dictionary of resources from the specified project
        """
        all_resources = self.list_all()
        return {
            name: state 
            for name, state in all_resources.items()
            if state.get("project") == project_name
        }
    
    def get_by_environment(self, environment: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all resources for a specific environment.
        
        Args:
            environment: Environment name (e.g., "production", "development")
            
        Returns:
            Dictionary of resources from the specified environment
        """
        all_resources = self.list_all()
        return {
            name: state 
            for name, state in all_resources.items()
            if state.get("environment") == environment
        }