"""
GCP Provider Metadata
"""

from ...core.interfaces.provider import ProviderType

METADATA = {
    "name": "Google Cloud Platform Compute Engine",
    "provider_type": ProviderType.GCP,
    "version": "1.0.0",
    "author": "InfraDSL Team",
    "description": "Google Cloud Platform Compute Engine provider for VM management",
    "resource_types": ["instance"],
    "regions": [
        "us-central1",
        "us-east1",
        "us-west1",
        "us-west2",
        "europe-west1",
        "europe-west2",
        "asia-east1",
        "asia-southeast1",
    ],
    "required_config": ["project"],
    "optional_config": ["region", "credentials"],
    "documentation_url": "https://cloud.google.com/compute/docs",
}