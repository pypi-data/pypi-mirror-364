"""
InfraDSL - Infrastructure as Code, Redefined

A next-generation Infrastructure-as-Code framework that treats infrastructure
as a living, self-aware system.
"""

from .core import *
from .providers import AWS, GoogleCloud, DigitalOcean

# Add GCP alias for convenience
GCP = GoogleCloud
from .resources.compute.virtual_machine import InstanceSize
from .resources import VirtualMachine
from .regions import Region, GCPRegion, Zone, AWSRegion, DORegion

# Template Registry System - Import lazily to avoid circular imports
try:
    from .registry.build_push import BuildPushRegistry, publish_template
    from .registry.template_builder import TemplatePackageBuilder, create_template_package
    from .registry.validator import TemplateValidator, validate_template_package
except ImportError:
    # Fallback if circular imports occur
    BuildPushRegistry = None
    TemplatePackageBuilder = None  
    TemplateValidator = None
    publish_template = None
    create_template_package = None
    validate_template_package = None

__version__ = "0.1.0"
__all__ = [
    # Core exports
    "BaseResource",
    "ResourceState",
    "DriftAction",
    "NexusEngine",
    "NexusConfig",
    "ExecutionMode",
    # Provider exports
    "AWS",
    "GoogleCloud",
    "GCP",
    "DigitalOcean",
    # Resource exports
    "InstanceSize",
    "VirtualMachine",
    # Region/Zone exports
    "Region",
    "GCPRegion", 
    "Zone",
    "AWSRegion",
    "DORegion",
    # Template Registry System
    "BuildPushRegistry",
    "TemplatePackageBuilder", 
    "TemplateValidator",
    "publish_template",
    "create_template_package",
    "validate_template_package",
]
