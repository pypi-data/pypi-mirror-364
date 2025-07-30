"""
HTTP Server - Backward compatibility import

This file provides backward compatibility imports from the modularized http_server package.
For new code, import directly from the http_server package modules.
"""

# Import everything from the new modular structure for backward compatibility
from .http_server.server import NexusAPIServer
from .http_server.models import (
    ResourceCreateRequest,
    ResourceUpdateRequest,
    ResourceResponse,
    OperationResponse,
    ErrorResponse,
)

# Keep the old interface working
__all__ = [
    "NexusAPIServer",
    "ResourceCreateRequest",
    "ResourceUpdateRequest",
    "ResourceResponse",
    "OperationResponse",
    "ErrorResponse",
]
