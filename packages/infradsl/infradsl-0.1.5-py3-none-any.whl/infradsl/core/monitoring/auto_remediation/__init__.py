"""
Auto-Remediation Engine - Automated infrastructure drift remediation

This package provides automated actions for detected drift with safety checks and rollback
capabilities, now modularized for better maintainability.
"""

from .models import (
    RemediationAction,
    RemediationStatus,
    SafetyLevel,
    SafetyCheck,
    ApprovalWorkflow,
    RemediationRequest,
)
from .engine import AutoRemediationEngine

__all__ = [
    # Enums and data models
    "RemediationAction",
    "RemediationStatus",
    "SafetyLevel",
    "SafetyCheck",
    "ApprovalWorkflow",
    "RemediationRequest",
    # Main engine
    "AutoRemediationEngine",
]
