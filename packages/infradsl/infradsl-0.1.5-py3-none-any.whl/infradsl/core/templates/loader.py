from typing import Dict, Any, List, Optional, Type, Union, Callable
import importlib
from pathlib import Path
import logging

from .base import BaseTemplate, TemplateMetadata  
from .registry import get_global_registry, TemplateRegistry


class TemplateLoader:
    """
    Dynamic template loader that provides the Template.* interface.
    
    This class handles the magic method resolution for template discovery:
    - Template.GenericVM("name") -> Loads GenericVM template
    - Template.WebApp("name") -> Loads WebApp template  
    - Template.Database("name") -> Loads Database template
    
    Templates are loaded on-demand from registries and cached for performance.
    """
    
    def __init__(self, registry: TemplateRegistry = None):
        self.registry = registry or get_global_registry()
        self.logger = logging.getLogger(__name__)
        self._template_cache: Dict[str, Type[BaseTemplate]] = {}
        
    def __getattr__(self, template_name: str) -> Callable:
        """
        Magic method that handles Template.TemplateName("instance_name") calls.
        
        This enables the dynamic template loading syntax:
        - Template.GenericVM("my-vm")
        - Template.WebApp("my-app") 
        - Template.DatabaseCluster("my-db")
        """
        if template_name.startswith('_'):
            # Avoid infinite recursion on internal attributes
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{template_name}'")
            
        def template_factory(instance_name: str, **kwargs) -> BaseTemplate:
            """Factory function that creates template instances"""
            return self.load_template(template_name, instance_name, **kwargs)
            
        return template_factory
        
    def load_template(self, template_name: str, instance_name: str, **kwargs) -> BaseTemplate:
        """
        Load and instantiate a template by name.
        
        Args:
            template_name: Name of the template to load (e.g., "GenericVM")
            instance_name: Name for the template instance
            **kwargs: Parameters to pass to the template
            
        Returns:
            BaseTemplate instance
            
        Raises:
            TemplateNotFoundError: If template is not found in any registry
            TemplateLoadError: If template fails to load or instantiate
        """
        try:
            # Check cache first
            if template_name in self._template_cache:
                template_class = self._template_cache[template_name]
            else:
                # Load from registry
                template_class = self.registry.get_template(template_name)
                if not template_class:
                    raise TemplateNotFoundError(f"Template '{template_name}' not found in any registry")
                    
                # Cache for future use
                self._template_cache[template_name] = template_class
                
            # Create instance
            template_instance = template_class(instance_name, **kwargs)
            
            # Initialize and validate
            template_instance.initialize()
            validation_errors = self.registry.validate_template(template_instance)
            if validation_errors:
                error_msg = f"Template validation failed: {'; '.join(validation_errors)}"
                raise TemplateValidationError(error_msg)
                
            return template_instance
            
        except Exception as e:
            self.logger.error(f"Failed to load template '{template_name}': {e}")
            if isinstance(e, (TemplateNotFoundError, TemplateValidationError)):
                raise
            else:
                raise TemplateLoadError(f"Failed to load template '{template_name}': {e}") from e
                
    def list_available_templates(self) -> List[TemplateMetadata]:
        """List all available templates from registries"""
        return self.registry.list_templates()
        
    def search_templates(self, query: str) -> List[TemplateMetadata]:
        """Search for templates by name, description, or tags"""
        return self.registry.search_templates(query)
        
    def get_template_info(self, template_name: str) -> Optional[TemplateMetadata]:
        """Get detailed information about a template"""
        return self.registry.get_template_metadata(template_name)
        
    def refresh_cache(self):
        """Refresh template cache and rediscover templates"""
        self._template_cache.clear()
        self.registry.discover_templates(force_refresh=True)
        
    def create_template_builder(self, base_template: str = None) -> "TemplateBuilder":
        """Create a new template builder for custom templates"""
        from .builder import TemplateBuilder
        return TemplateBuilder(base_template, registry=self.registry)


class TemplateNotFoundError(Exception):
    """Raised when a requested template is not found in any registry"""
    pass


class TemplateLoadError(Exception):
    """Raised when a template fails to load"""
    pass


class TemplateValidationError(Exception):
    """Raised when a template fails validation"""
    pass


class TemplateProxy:
    """
    Proxy class that provides the main Template interface.
    
    This is the class that users import and interact with:
    from infradsl.templates import Template
    
    vm = Template.GenericVM("my-vm")
    """
    
    def __init__(self):
        self._loader = TemplateLoader()
        
    def __getattr__(self, name: str) -> Callable:
        """Delegate to the loader for dynamic template resolution"""
        return getattr(self._loader, name)
        
    def create(self, name: str) -> "TemplateBuilder":
        """Create a new custom template"""
        from .builder import TemplateBuilder
        return TemplateBuilder(name=name, registry=self._loader.registry)
        
    def list(self, category: str = None, tags: List[str] = None) -> List[TemplateMetadata]:
        """List available templates with optional filtering"""
        return self._loader.registry.list_templates(category=category, tags=tags)
        
    def search(self, query: str) -> List[TemplateMetadata]:
        """Search for templates"""
        return self._loader.search_templates(query)
        
    def info(self, template_name: str) -> Optional[TemplateMetadata]:
        """Get template information"""
        return self._loader.get_template_info(template_name)
        
    def refresh(self):
        """Refresh template registries"""
        self._loader.refresh_cache()
        
    def add_registry(self, path_or_url: str, registry_type: str = "auto"):
        """Add a new template registry"""
        if registry_type == "auto":
            # Auto-detect registry type
            if path_or_url.startswith(('http://', 'https://')):
                registry_type = "remote"
            elif path_or_url.startswith('git@') or path_or_url.endswith('.git'):
                registry_type = "git"
            else:
                registry_type = "local"
                
        if registry_type == "local":
            self._loader.registry.add_local_registry(path_or_url)
        elif registry_type == "remote":
            self._loader.registry.add_remote_registry(path_or_url)
        elif registry_type == "git":
            self._loader.registry.add_git_registry(path_or_url)
        else:
            raise ValueError(f"Unsupported registry type: {registry_type}")
            
    def configure(self, **settings):
        """Configure template system settings"""
        # TODO: Implement global template configuration
        pass