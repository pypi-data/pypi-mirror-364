"""
InfraDSL Built-in Templates

This package contains the built-in template collection that ships with InfraDSL.
These templates provide common infrastructure patterns and can be used as
building blocks for more complex architectures.
"""

# Export the main Template interface
from ..core.templates.template import (
    Template,
    list_templates,
    search_templates, 
    template_info,
    refresh_templates,
    add_template_registry,
    create_vm_template,
    create_web_app_template,
    create_database_template,
    template_manager
)

__all__ = [
    "Template",
    "list_templates",
    "search_templates", 
    "template_info",
    "refresh_templates",
    "add_template_registry",
    "create_vm_template",
    "create_web_app_template", 
    "create_database_template",
    "template_manager"
]