"""
InfraDSL Template Registry System

The Template Registry provides a dynamic, extensible way to create, share, and reuse
infrastructure patterns. Templates can be discovered, imported, extended, and customized
at runtime.

Example Usage:
    # Simple template usage
    vm = Template.GenericVM("my-web-server")
    
    # Extended template with overrides
    stack = (Template.WebApp("my-app")
             .extend("DatabaseCluster")  
             .override(instance_count=3)
             .with_monitoring()
             .production())
    
    # Custom template creation
    custom = (Template.create("MyPattern")
              .base("GenericVM")
              .add("LoadBalancer")
              .add("Database")
              .publish("my-registry"))
"""

from .registry import TemplateRegistry
from .base import BaseTemplate, TemplateMetadata
from .loader import TemplateLoader
from .builder import TemplateBuilder
from .template import Template

__all__ = [
    "Template",
    "TemplateRegistry", 
    "BaseTemplate",
    "TemplateMetadata",
    "TemplateLoader",
    "TemplateBuilder",
]