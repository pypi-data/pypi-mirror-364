"""
DigitalOcean Provider - Backward compatibility module

This module provides backward compatibility by re-exporting the
refactored components from the digitalocean package.
"""

# Import from the new modular structure
from .digitalocean import DigitalOceanProvider, METADATA
from .digitalocean.factory import DigitalOcean

# Re-export for backward compatibility
__all__ = ["DigitalOceanProvider", "DigitalOcean", "METADATA"]
