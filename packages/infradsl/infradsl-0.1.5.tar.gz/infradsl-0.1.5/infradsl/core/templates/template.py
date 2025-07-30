"""
Main Template interface for InfraDSL Template Registry.

This module provides the primary Template class that users interact with:

    from infradsl.templates import Template
    
    # Load and instantiate templates
    vm = Template.GenericVM("my-server")
    app = Template.WebApp("my-app").with_ssl().production()
    
    # Create custom templates  
    custom = (Template.create("MyStack")
              .base("GenericVM") 
              .add_component("Database")
              .publish())

The Template class uses dynamic attribute resolution to load templates
from registries on-demand, providing a seamless development experience.
"""

from typing import Dict, Any, List, Optional, Type, Union, Callable

from .loader import TemplateProxy


# Create global Template instance
Template = TemplateProxy()

# Export for easier importing
__all__ = ["Template"]


# Template shortcuts and utilities

def list_templates(category: str = None, tags: List[str] = None):
    """List available templates with optional filtering"""
    return Template.list(category=category, tags=tags)

def search_templates(query: str):
    """Search for templates by name, description, or tags"""
    return Template.search(query)

def template_info(name: str):
    """Get detailed information about a template"""
    return Template.info(name)

def refresh_templates():
    """Refresh template cache and registries"""
    Template.refresh()

def add_template_registry(path_or_url: str, registry_type: str = "auto"):
    """Add a new template registry"""
    Template.add_registry(path_or_url, registry_type)


# Template creation shortcuts

def create_vm_template(name: str):
    """Create a new VM template builder"""
    from .builder import create_vm_template
    return create_vm_template(name)

def create_web_app_template(name: str):
    """Create a new web application template builder"""
    from .builder import create_web_app_template
    return create_web_app_template(name)

def create_database_template(name: str):
    """Create a new database template builder"""
    from .builder import create_database_template
    return create_database_template(name)


# Template registry management

class TemplateManager:
    """Template management utilities"""
    
    @staticmethod
    def install_template(source: str, name: str = None):
        """Install a template from various sources"""
        # TODO: Implement template installation from:
        # - Git repositories
        # - Archive files (tar.gz, zip)
        # - Remote URLs
        # - Package managers (pip, npm equivalent for templates)
        pass
        
    @staticmethod
    def uninstall_template(name: str):
        """Uninstall a template"""
        # TODO: Implement template removal
        pass
        
    @staticmethod
    def update_template(name: str, version: str = "latest"):
        """Update a template to a specific version"""
        # TODO: Implement template updates
        pass
        
    @staticmethod
    def list_installed():
        """List locally installed templates"""
        return Template.list()
        
    @staticmethod
    def validate_template(name: str):
        """Validate a template configuration"""
        # TODO: Implement template validation
        pass


# Export manager for convenience
template_manager = TemplateManager()