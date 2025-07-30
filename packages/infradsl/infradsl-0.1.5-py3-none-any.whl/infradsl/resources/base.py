"""
Base resource class for all InfraDSL resources
"""

from typing import Any, Dict, Optional
from abc import ABC, abstractmethod


class BaseResource(ABC):
    """
    Base class for all InfraDSL resources

    Provides common functionality for resource management including:
    - Resource naming and identification
    - Provider integration
    - Lifecycle management (create, update, destroy)
    - State serialization
    """

    def __init__(self, name: str):
        self.name = name
        self._resource_type = "BaseResource"
        self._provider = None
        self._state = None
        self._config = {}
        self.tags = []

    def tag(self, key: str, value: Optional[str] = None) -> "BaseResource":
        """Add a tag to the resource"""
        if value is None:
            # Simple tag without value
            if key not in self.tags:
                self.tags.append(key)
        else:
            # Key-value tag
            tag_str = f"{key}:{value}"
            if tag_str not in self.tags:
                self.tags.append(tag_str)
        return self

    def tags_dict(self, tags: Dict[str, str]) -> "BaseResource":
        """Add multiple tags from a dictionary"""
        for key, value in tags.items():
            self.tag(key, value)
        return self

    @abstractmethod
    def create(self) -> "BaseResource":
        """Create the resource"""
        pass

    @abstractmethod
    def update(self) -> "BaseResource":
        """Update the resource"""
        pass

    @abstractmethod
    def destroy(self) -> None:
        """Destroy the resource"""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert the resource to a dictionary representation"""
        pass

    def __str__(self) -> str:
        return f"{self._resource_type}({self.name})"

    def __repr__(self) -> str:
        return f"{self._resource_type}(name='{self.name}', provider={self._provider})"
