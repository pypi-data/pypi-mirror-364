"""
AWS Provider Metadata
"""

from ...core.interfaces.provider import ProviderType

METADATA = {
    "name": "AWS",
    "provider_type": ProviderType.AWS,
    "version": "1.0.0",
    "author": "InfraDSL",
    "description": "AWS provider for CloudFront, S3, Route53, and EC2",
    "resource_types": ["CloudFront", "S3", "Route53", "EC2"],
    "regions": ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
    "required_config": [],
    "optional_config": [
        "profile",
        "access_key_id",
        "secret_access_key",
        "session_token",
    ],
}