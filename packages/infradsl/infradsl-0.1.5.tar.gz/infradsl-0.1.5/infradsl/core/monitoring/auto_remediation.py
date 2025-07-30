"""
Auto-Remediation Engine - Backward compatibility import

This file provides backward compatibility imports from the modularized auto_remediation package.
For new code, import directly from the auto_remediation package modules.
"""

# Import everything from the new modular structure for backward compatibility
from .auto_remediation.models import (
    RemediationAction,
    RemediationStatus,
    SafetyLevel,
    SafetyCheck,
    ApprovalWorkflow,
    RemediationRequest,
)

from .auto_remediation.engine import AutoRemediationEngine

# Keep the old interface working
__all__ = [
    "RemediationAction",
    "RemediationStatus",
    "SafetyLevel",
    "SafetyCheck",
    "ApprovalWorkflow",
    "RemediationRequest",
    "AutoRemediationEngine",
]
