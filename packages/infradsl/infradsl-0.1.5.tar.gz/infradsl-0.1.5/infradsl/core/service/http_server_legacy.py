"""
DEPRECATED: This file has been modularized into the http_server package.

This file is kept for backward compatibility. New code should import from:
- infradsl.core.service.http_server.server.NexusAPIServer
- infradsl.core.service.http_server.models.*

This file will be removed in a future version.
"""

# Import everything from the new modular structure for backward compatibility
from .http_server import *

import warnings

warnings.warn(
    "http_server.py is deprecated. Use http_server package instead.",
    DeprecationWarning,
    stacklevel=2
)