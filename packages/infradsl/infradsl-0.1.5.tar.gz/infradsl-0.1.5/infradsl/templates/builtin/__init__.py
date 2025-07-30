"""
Built-in InfraDSL Templates

This package contains the default template library that ships with InfraDSL.
These templates demonstrate best practices and provide ready-to-use patterns
for common infrastructure scenarios.

Available Templates:
- GenericVM: Basic virtual machine template
- WebApp: Web application with load balancer
- Database: Database cluster template
- ContainerApp: Containerized application template
- StaticSite: Static website with CDN
- ServerlessAPI: Serverless API template
"""

# Import built-in templates for auto-discovery
from .generic_vm import GenericVMTemplate
from .web_app import WebAppTemplate  
from .database import DatabaseTemplate

__all__ = [
    "GenericVMTemplate",
    "WebAppTemplate",
    "DatabaseTemplate",
]