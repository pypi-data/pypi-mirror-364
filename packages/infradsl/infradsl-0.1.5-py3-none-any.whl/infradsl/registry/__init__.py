"""
InfraDSL Template Registry Helpers

This module provides utilities for template authors to easily publish
their templates to the registry.

Usage in template files:
    from infradsl import BuildPushRegistry
    
    # At the end of your template file
    if __name__ == "__main__":
        BuildPushRegistry(
            name="MyAwesomeTemplate",
            version="1.0.0",
            description="An awesome infrastructure template",
            author="Your Name",
            category="compute",
            tags=["vm", "scalable", "production"],
            providers=["aws", "gcp"],
            visibility="public"
        )
"""

from .build_push import BuildPushRegistry
from .template_builder import TemplatePackageBuilder
from .validator import TemplateValidator

__all__ = [
    "BuildPushRegistry", 
    "TemplatePackageBuilder",
    "TemplateValidator"
]