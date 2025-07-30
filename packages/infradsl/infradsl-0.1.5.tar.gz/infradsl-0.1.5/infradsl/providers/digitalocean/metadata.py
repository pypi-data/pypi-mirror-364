"""
DigitalOcean Provider Metadata
"""

from ...core.interfaces.provider import ProviderType

# Provider metadata for registration
METADATA = {
    "name": "DigitalOcean",
    "provider_type": ProviderType.DIGITAL_OCEAN,
    "version": "1.0.0",
    "author": "InfraDSL Team",
    "description": "DigitalOcean cloud provider with support for Droplets, networking, and storage",
    "resource_types": ["droplet"],
    "regions": ["nyc1", "nyc3", "ams3", "sgp1", "lon1", "fra1", "tor1", "sfo3"],
    "required_config": ["token"],
    "optional_config": ["region"],
}
