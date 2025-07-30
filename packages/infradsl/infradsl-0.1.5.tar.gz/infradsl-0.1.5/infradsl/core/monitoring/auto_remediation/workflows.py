"""
Auto-Remediation Approval Workflows - Workflow management for remediation approvals
"""

import logging
from typing import Dict

from .models import ApprovalWorkflow, SafetyLevel, RemediationRequest
from ..daemon import DriftResult

logger = logging.getLogger(__name__)


class WorkflowManager:
    """Manager for approval workflows"""
    
    def __init__(self):
        self.approval_workflows: Dict[str, ApprovalWorkflow] = {}
        self._setup_default_approval_workflows()
    
    def add_approval_workflow(self, workflow: ApprovalWorkflow):
        """Add an approval workflow"""
        self.approval_workflows[workflow.name] = workflow
        logger.info(f"Added approval workflow: {workflow.name}")
    
    def get_approval_workflows(self) -> Dict[str, ApprovalWorkflow]:
        """Get all approval workflows"""
        return self.approval_workflows
    
    async def check_auto_approval(self, request: RemediationRequest) -> bool:
        """Check if request can be auto-approved"""
        # Find appropriate workflow
        workflow = self.approval_workflows.get(request.safety_level.value)
        if not workflow:
            return False

        # Check auto-approval conditions
        for condition in workflow.auto_approve_conditions:
            try:
                if not condition(request.drift_result):
                    return False
            except Exception as e:
                logger.error(f"Auto-approval condition failed: {e}")
                return False

        return True
    
    def get_required_approvers(self, safety_level: SafetyLevel) -> list[str]:
        """Get required approvers for a safety level"""
        if safety_level == SafetyLevel.LOW:
            return []
        elif safety_level == SafetyLevel.MEDIUM:
            return ["ops-team"]
        elif safety_level == SafetyLevel.HIGH:
            return ["ops-team", "security-team"]
        elif safety_level == SafetyLevel.CRITICAL:
            return ["ops-manager", "security-manager"]
        else:
            return ["ops-team"]
    
    def _setup_default_approval_workflows(self):
        """Setup default approval workflows"""

        # Low risk workflow
        def auto_approve_low_risk(drift_result: DriftResult) -> bool:
            """Auto-approve low-risk changes"""
            # Only auto-approve if not in production and not critical
            return (
                getattr(drift_result, "environment", "") != "production"
                and "critical" not in str(drift_result.drift_details).lower()
            )

        low_risk_workflow = ApprovalWorkflow(
            name="low_risk",
            description="Auto-approval for low-risk changes",
            required_approvers=[],
            timeout_minutes=5,
            auto_approve_conditions=[auto_approve_low_risk],
        )
        self.add_approval_workflow(low_risk_workflow)

        # Medium risk workflow
        medium_risk_workflow = ApprovalWorkflow(
            name="medium_risk",
            description="Single approval for medium-risk changes",
            required_approvers=["ops-team"],
            timeout_minutes=30,
        )
        self.add_approval_workflow(medium_risk_workflow)

        # High risk workflow
        def escalate_high_risk(drift_result: DriftResult) -> bool:
            """Escalate high-risk changes"""
            return (
                getattr(drift_result, "environment", "") == "production"
                or "security" in str(drift_result.drift_details).lower()
            )

        high_risk_workflow = ApprovalWorkflow(
            name="high_risk",
            description="Dual approval for high-risk changes",
            required_approvers=["ops-team", "security-team"],
            timeout_minutes=60,
            escalation_conditions=[escalate_high_risk],
        )
        self.add_approval_workflow(high_risk_workflow)

        # Critical workflow
        critical_workflow = ApprovalWorkflow(
            name="critical",
            description="Management approval for critical changes",
            required_approvers=["ops-manager", "security-manager"],
            timeout_minutes=120,
        )
        self.add_approval_workflow(critical_workflow)