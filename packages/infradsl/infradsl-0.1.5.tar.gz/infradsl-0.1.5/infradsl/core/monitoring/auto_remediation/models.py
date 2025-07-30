"""
Auto-Remediation Models - Data classes and enums for the auto-remediation system
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable

from ..daemon import DriftResult
from infradsl.core.nexus.base_resource import BaseResource
from infradsl.core.reconciliation.policies import (
    ReconciliationAction,
    ReconciliationResult,
)


class RemediationAction(Enum):
    """Types of remediation actions"""

    APPROVE = "approve"
    REJECT = "reject"
    ROLLBACK = "rollback"
    IGNORE = "ignore"
    ESCALATE = "escalate"


class RemediationStatus(Enum):
    """Status of a remediation operation"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    ESCALATED = "escalated"


class SafetyLevel(Enum):
    """Safety levels for remediation actions"""

    LOW = "low"  # No safety checks required
    MEDIUM = "medium"  # Basic safety checks
    HIGH = "high"  # Comprehensive safety checks
    CRITICAL = "critical"  # Manual approval required


@dataclass
class SafetyCheck:
    """Safety check definition"""

    name: str
    description: str
    check_function: Callable[[BaseResource, Dict[str, Any]], bool]
    severity: SafetyLevel = SafetyLevel.MEDIUM
    enabled: bool = True


@dataclass
class ApprovalWorkflow:
    """Approval workflow configuration"""

    name: str
    description: str
    required_approvers: List[str]
    timeout_minutes: int = 60
    auto_approve_conditions: List[Callable[[DriftResult], bool]] = field(
        default_factory=list
    )
    escalation_conditions: List[Callable[[DriftResult], bool]] = field(
        default_factory=list
    )


@dataclass
class RemediationRequest:
    """Remediation request with approval workflow"""

    id: str
    drift_result: DriftResult
    proposed_action: ReconciliationAction
    safety_level: SafetyLevel
    created_at: datetime
    requested_by: str
    approvers: List[str]
    status: RemediationStatus = RemediationStatus.PENDING
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejected_by: Optional[str] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    execution_started_at: Optional[datetime] = None
    execution_completed_at: Optional[datetime] = None
    execution_result: Optional[ReconciliationResult] = None
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)
    safety_checks: List[Dict[str, Any]] = field(default_factory=list)
    rollback_plan: Optional[Dict[str, Any]] = None
    remediation_data: Dict[str, Any] = field(default_factory=dict)
