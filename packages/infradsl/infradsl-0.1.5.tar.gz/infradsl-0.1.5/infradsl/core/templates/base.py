from typing import Dict, Any, List, Optional, Self, Type, Union, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from datetime import datetime
import json
import inspect


@dataclass
class TemplateMetadata:
    """Template metadata and information"""
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    tags: List[str] = field(default_factory=list)
    category: str = "general"
    
    # Dependencies and compatibility
    requires: List[str] = field(default_factory=list)  # Required templates
    providers: List[str] = field(default_factory=list)  # Supported providers
    min_infradsl_version: str = "1.0.0"
    
    # Usage and examples
    examples: List[Dict[str, Any]] = field(default_factory=list)
    documentation_url: str = ""
    repository_url: str = ""
    
    # Registry information
    registry_url: str = ""
    download_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Template configuration schema
    parameters_schema: Dict[str, Any] = field(default_factory=dict)
    outputs_schema: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "version": self.version, 
            "description": self.description,
            "author": self.author,
            "tags": self.tags,
            "category": self.category,
            "requires": self.requires,
            "providers": self.providers,
            "min_infradsl_version": self.min_infradsl_version,
            "examples": self.examples,
            "documentation_url": self.documentation_url,
            "repository_url": self.repository_url,
            "registry_url": self.registry_url,
            "download_count": self.download_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "parameters_schema": self.parameters_schema,
            "outputs_schema": self.outputs_schema,
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemplateMetadata":
        """Create from dictionary"""
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)


@dataclass
class TemplateContext:
    """Template execution context and state"""
    name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    overrides: Dict[str, Any] = field(default_factory=dict)
    extensions: List[str] = field(default_factory=list)
    environment: str = "development"
    provider_configs: Dict[str, Any] = field(default_factory=dict)
    
    # Runtime state
    resources: List[Any] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    
    def merge_parameters(self, params: Dict[str, Any]) -> None:
        """Merge parameters with existing ones"""
        self.parameters.update(params)
        
    def add_override(self, key: str, value: Any) -> None:
        """Add configuration override"""
        self.overrides[key] = value
        
    def add_extension(self, template_name: str) -> None:
        """Add template extension"""
        if template_name not in self.extensions:
            self.extensions.append(template_name)


class BaseTemplate(ABC):
    """
    Base class for all InfraDSL templates.
    
    Templates are reusable infrastructure patterns that can be:
    - Discovered dynamically from registries
    - Extended with additional functionality
    - Customized with parameters and overrides
    - Composed into larger patterns
    """
    
    def __init__(self, name: str, **kwargs):
        self.metadata: TemplateMetadata = self._create_metadata()
        self.context = TemplateContext(name=name, parameters=kwargs)
        self._initialized = False
        self._built_resources: List[Any] = []
        
    @abstractmethod
    def _create_metadata(self) -> TemplateMetadata:
        """Create template metadata (implemented by concrete templates)"""
        pass
        
    @abstractmethod
    def build(self, context: TemplateContext) -> List[Any]:
        """Build the template resources (implemented by concrete templates)"""
        pass
        
    def initialize(self) -> Self:
        """Initialize the template (called before build)"""
        if not self._initialized:
            self._validate_parameters()
            self._setup_defaults()
            self._initialized = True
        return self
        
    def _validate_parameters(self) -> None:
        """Validate template parameters against schema"""
        schema = self.metadata.parameters_schema
        if not schema:
            return
            
        # Basic validation - could be enhanced with jsonschema
        required = schema.get("required", [])
        for param in required:
            if param not in self.context.parameters:
                raise ValueError(f"Required parameter '{param}' missing for template {self.metadata.name}")
                
    def _setup_defaults(self) -> None:
        """Setup default parameter values"""
        schema = self.metadata.parameters_schema
        if not schema:
            return
            
        properties = schema.get("properties", {})
        for param_name, param_config in properties.items():
            if param_name not in self.context.parameters and "default" in param_config:
                self.context.parameters[param_name] = param_config["default"]
                
    # Fluent interface methods
    
    def with_parameters(self, **params) -> Self:
        """Add parameters (chainable)"""
        self.context.merge_parameters(params)
        return self
        
    def override(self, **overrides) -> Self:
        """Add configuration overrides (chainable)"""
        for key, value in overrides.items():
            self.context.add_override(key, value)
        return self
        
    def extend(self, template_name: str) -> Self:
        """Extend with another template (chainable)"""
        self.context.add_extension(template_name)
        return self
        
    def environment(self, env: str) -> Self:
        """Set environment (chainable)"""
        self.context.environment = env
        return self
        
    def production(self) -> Self:
        """Configure for production environment (chainable)"""
        return self.environment("production")
        
    def staging(self) -> Self:
        """Configure for staging environment (chainable)"""  
        return self.environment("staging")
        
    def development(self) -> Self:
        """Configure for development environment (chainable)"""
        return self.environment("development")
        
    # Template execution
    
    def render(self) -> List[Any]:
        """Render the template to resources"""
        if not self._initialized:
            self.initialize()
            
        # Apply extensions first
        for extension_name in self.context.extensions:
            self._apply_extension(extension_name)
            
        # Build base template
        resources = self.build(self.context)
        
        # Apply overrides
        self._apply_overrides(resources)
        
        # Store built resources
        self._built_resources.extend(resources)
        self.context.resources.extend(resources)
        
        return resources
        
    def _apply_extension(self, extension_name: str) -> None:
        """Apply template extension"""
        # This would load and apply the extension template
        # Implementation would involve the registry system
        pass
        
    def _apply_overrides(self, resources: List[Any]) -> None:
        """Apply configuration overrides to resources"""
        for resource in resources:
            for key, value in self.context.overrides.items():
                if hasattr(resource, 'spec') and hasattr(resource.spec, key):
                    setattr(resource.spec, key, value)
                    
    # Utility methods
    
    def get_parameter(self, name: str, default: Any = None) -> Any:
        """Get parameter value"""
        return self.context.parameters.get(name, default)
        
    def set_output(self, name: str, value: Any) -> None:
        """Set template output"""
        self.context.outputs[name] = value
        
    def get_outputs(self) -> Dict[str, Any]:
        """Get template outputs"""
        return self.context.outputs.copy()
        
    def get_resources(self) -> List[Any]:
        """Get built resources"""
        return self._built_resources.copy()
        
    # Metadata and introspection
    
    def get_metadata(self) -> TemplateMetadata:
        """Get template metadata"""
        return self.metadata
        
    def describe(self) -> Dict[str, Any]:
        """Get template description and usage information"""
        return {
            "metadata": self.metadata.to_dict(),
            "parameters": self.context.parameters,
            "overrides": self.context.overrides,
            "extensions": self.context.extensions,
            "environment": self.context.environment,
            "resource_count": len(self._built_resources),
            "outputs": self.context.outputs,
        }
        
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.context.name}', version='{self.metadata.version}')>"


class TemplateFactory:
    """Factory for creating template instances"""
    
    @staticmethod
    def create_template(template_class: Type[BaseTemplate], name: str, **kwargs) -> BaseTemplate:
        """Create template instance"""
        return template_class(name, **kwargs)
        
    @staticmethod
    def create_from_dict(template_data: Dict[str, Any]) -> BaseTemplate:
        """Create template from dictionary configuration"""
        # This would be used for dynamic template loading
        # Implementation depends on the template data format
        pass