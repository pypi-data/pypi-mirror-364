"""
DEPRECATED: This file has been modularized into the auto_remediation package.

This file is kept for backward compatibility. New code should import from:
- infradsl.core.monitoring.auto_remediation.engine.AutoRemediationEngine
- infradsl.core.monitoring.auto_remediation.models.*

This file will be removed in a future version.
"""

# Import everything from the new modular structure for backward compatibility
from .auto_remediation import *

import warnings

warnings.warn(
    "auto_remediation.py is deprecated. Use auto_remediation package instead.",
    DeprecationWarning,
    stacklevel=2
)