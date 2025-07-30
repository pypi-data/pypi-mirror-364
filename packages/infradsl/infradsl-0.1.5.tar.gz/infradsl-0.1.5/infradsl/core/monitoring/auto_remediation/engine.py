"""
Auto-Remediation Engine - Main engine class that coordinates all auto-remediation functionality
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from .models import (
    RemediationRequest,
    RemediationStatus,
    SafetyLevel,
    RemediationAction,
)
from .safety import SafetyCheckManager
from .workflows import WorkflowManager
from .execution import RemediationExecutor
from ..daemon import DriftResult
from ..notifications import (
    NotificationManager,
    NotificationEvent,
    NotificationPriority,
)
from infradsl.core.nexus import NexusEngine
from infradsl.core.reconciliation.policies import (
    ReconciliationPolicy,
    ReconciliationAction,
)

logger = logging.getLogger(__name__)


class AutoRemediationEngine:
    """
    Auto-remediation engine with safety checks, approval workflows,
    and rollback capabilities.
    """

    def __init__(
        self,
        nexus_engine: Optional[NexusEngine] = None,
        notification_manager: Optional[NotificationManager] = None,
        enable_auto_approval: bool = False,
        max_concurrent_remediations: int = 3,
        audit_log_retention_days: int = 30,
    ):
        """
        Initialize the auto-remediation engine

        Args:
            nexus_engine: NexusEngine instance for resource operations
            notification_manager: NotificationManager for alerts
            enable_auto_approval: Enable automatic approval for low-risk actions
            max_concurrent_remediations: Maximum concurrent remediation operations
            audit_log_retention_days: Days to retain audit logs
        """
        self.nexus_engine = nexus_engine or NexusEngine()
        self.notification_manager = (
            notification_manager or NotificationManager()
        )
        self.enable_auto_approval = enable_auto_approval
        self.max_concurrent_remediations = max_concurrent_remediations
        self.audit_log_retention_days = audit_log_retention_days

        # Component managers
        self.safety_manager = SafetyCheckManager()
        self.workflow_manager = WorkflowManager()
        self.executor = RemediationExecutor(self.nexus_engine)

        # State management
        self.remediation_requests: Dict[str, RemediationRequest] = {}
        self.active_remediations: Dict[str, asyncio.Task] = {}
        self.reconciliation_policies: List[ReconciliationPolicy] = []

        # Rate limiting
        self.remediation_semaphore = asyncio.Semaphore(
            max_concurrent_remediations
        )

        # Statistics
        self.stats = {
            "total_requests": 0,
            "auto_approved": 0,
            "manual_approved": 0,
            "rejected": 0,
            "completed": 0,
            "failed": 0,
            "rolled_back": 0,
            "escalated": 0,
        }

    # Delegation methods for component managers
    def add_safety_check(self, safety_check):
        """Add a safety check"""
        self.safety_manager.add_safety_check(safety_check)

    def add_approval_workflow(self, workflow):
        """Add an approval workflow"""
        self.workflow_manager.add_approval_workflow(workflow)

    def add_reconciliation_policy(self, policy: ReconciliationPolicy):
        """Add a reconciliation policy"""
        self.reconciliation_policies.append(policy)
        logger.info(f"Added reconciliation policy: {policy.name}")

    @property
    def safety_checks(self):
        """Get safety checks from manager"""
        return self.safety_manager.get_safety_checks()

    @property
    def approval_workflows(self):
        """Get approval workflows from manager"""
        return self.workflow_manager.get_approval_workflows()

    async def assess_and_request_remediation(
        self,
        drift_result: DriftResult,
        proposed_action: ReconciliationAction,
        requested_by: str = "system",
        force_manual_approval: bool = False,
    ) -> str:
        """
        Assess and request remediation for a drift result

        Args:
            drift_result: Drift result to remediate
            proposed_action: Proposed action to take
            requested_by: User/system requesting remediation
            force_manual_approval: Force manual approval even for low-risk actions

        Returns:
            Request ID string
        """
        request = await self.request_remediation(
            drift_result, requested_by, force_manual_approval
        )
        return request.id

    async def request_remediation(
        self,
        drift_result: DriftResult,
        requested_by: str = "system",
        force_manual_approval: bool = False,
    ) -> RemediationRequest:
        """
        Request remediation for a drift result

        Args:
            drift_result: Drift result to remediate
            requested_by: User/system requesting remediation
            force_manual_approval: Force manual approval even for low-risk actions

        Returns:
            RemediationRequest object
        """
        # Generate request ID
        request_id = f"rem-{uuid.uuid4().hex[:8]}"

        # Determine proposed action
        proposed_action = self._determine_remediation_action(drift_result)

        # Determine safety level
        safety_level = self._assess_safety_level(drift_result)

        # Run safety checks
        safety_check_results = await self._run_safety_checks(drift_result)

        # Create remediation request
        request = RemediationRequest(
            id=request_id,
            drift_result=drift_result,
            proposed_action=proposed_action,
            safety_level=safety_level,
            created_at=datetime.now(timezone.utc),
            requested_by=requested_by,
            approvers=self.workflow_manager.get_required_approvers(
                safety_level
            ),
            safety_checks=safety_check_results,
            rollback_plan=self.executor.create_rollback_plan(drift_result),
            remediation_data={
                "original_state": drift_result.drift_details.get(
                    "expected_state", {}
                ).copy(),
                "detected_at": drift_result.check_timestamp.isoformat(),
                "drift_changes": drift_result.drift_details.get("changes", {}),
            },
        )

        # Add audit trail entry
        self._add_audit_entry(
            request,
            "request_created",
            {
                "requested_by": requested_by,
                "safety_level": safety_level.value,
                "proposed_action": proposed_action.value,
            },
        )

        # Store request
        self.remediation_requests[request_id] = request
        self.stats["total_requests"] += 1

        # Send notification
        await self._send_remediation_notification(
            request, "remediation_requested"
        )

        # Check for auto-approval
        if not force_manual_approval and self.enable_auto_approval:
            if await self.workflow_manager.check_auto_approval(request):
                await self.approve_remediation(
                    request_id, "auto-approval-system"
                )

        logger.info(f"Remediation requested: {request_id}")
        return request

    async def approve_remediation(
        self,
        request_id: str,
        approved_by: str,
        execute_immediately: bool = True,
    ) -> bool:
        """
        Approve a remediation request

        Args:
            request_id: Request ID to approve
            approved_by: User approving the request
            execute_immediately: Execute remediation immediately after approval

        Returns:
            True if approved successfully
        """
        if request_id not in self.remediation_requests:
            logger.error(f"Remediation request {request_id} not found")
            return False

        request = self.remediation_requests[request_id]

        # Check if already processed
        if request.status not in [
            RemediationStatus.PENDING,
            RemediationStatus.ESCALATED,
        ]:
            logger.warning(
                f"Request {request_id} already processed: {request.status}"
            )
            return False

        # Update request
        request.status = RemediationStatus.APPROVED
        request.approved_by = approved_by
        request.approved_at = datetime.now(timezone.utc)

        # Add audit trail
        self._add_audit_entry(
            request,
            "approved",
            {
                "approved_by": approved_by,
                "approved_at": request.approved_at.isoformat(),
            },
        )

        # Update statistics
        if approved_by == "auto-approval-system":
            self.stats["auto_approved"] += 1
        else:
            self.stats["manual_approved"] += 1

        # Send notification
        await self._send_remediation_notification(
            request, "remediation_approved"
        )

        # Execute if requested
        if execute_immediately:
            await self._execute_remediation(request)

        logger.info(f"Remediation approved: {request_id} by {approved_by}")
        return True

    async def reject_remediation(
        self,
        request_id: str,
        rejected_by: str,
        reason: str,
    ) -> bool:
        """
        Reject a remediation request

        Args:
            request_id: Request ID to reject
            rejected_by: User rejecting the request
            reason: Reason for rejection

        Returns:
            True if rejected successfully
        """
        if request_id not in self.remediation_requests:
            logger.error(f"Remediation request {request_id} not found")
            return False

        request = self.remediation_requests[request_id]

        # Check if already processed
        if request.status not in [
            RemediationStatus.PENDING,
            RemediationStatus.ESCALATED,
        ]:
            logger.warning(
                f"Request {request_id} already processed: {request.status}"
            )
            return False

        # Update request
        request.status = RemediationStatus.REJECTED
        request.rejected_by = rejected_by
        request.rejected_at = datetime.now(timezone.utc)
        request.rejection_reason = reason

        # Add audit trail
        self._add_audit_entry(
            request,
            "rejected",
            {
                "rejected_by": rejected_by,
                "rejected_at": request.rejected_at.isoformat(),
                "reason": reason,
            },
        )

        # Update statistics
        self.stats["rejected"] += 1

        # Send notification
        await self._send_remediation_notification(
            request, "remediation_rejected"
        )

        logger.info(f"Remediation rejected: {request_id} by {rejected_by}")
        return True

    async def rollback_remediation(
        self,
        request_id: str,
        rolled_back_by: str,
        reason: str,
    ) -> bool:
        """
        Rollback a completed remediation

        Args:
            request_id: Request ID to rollback
            rolled_back_by: User initiating rollback
            reason: Reason for rollback

        Returns:
            True if rollback successful
        """
        if request_id not in self.remediation_requests:
            logger.error(f"Remediation request {request_id} not found")
            return False

        request = self.remediation_requests[request_id]

        # Check if can be rolled back
        if request.status != RemediationStatus.COMPLETED:
            logger.warning(
                f"Request {request_id} cannot be rolled back: {request.status}"
            )
            return False

        if not request.rollback_plan:
            logger.error(f"No rollback plan available for {request_id}")
            return False

        try:
            # Execute rollback
            await self._execute_rollback(request, rolled_back_by, reason)

            # Update status
            request.status = RemediationStatus.ROLLED_BACK

            # Add audit trail
            self._add_audit_entry(
                request,
                "rolled_back",
                {
                    "rolled_back_by": rolled_back_by,
                    "reason": reason,
                    "rolled_back_at": datetime.now(timezone.utc).isoformat(),
                },
            )

            # Update statistics
            self.stats["rolled_back"] += 1

            # Send notification
            await self._send_remediation_notification(
                request, "remediation_rolled_back"
            )

            logger.info(
                f"Remediation rolled back: {request_id} by {rolled_back_by}"
            )
            return True

        except Exception as e:
            logger.error(f"Rollback failed for {request_id}: {e}")
            return False

    def _determine_remediation_action(
        self, drift_result: DriftResult
    ) -> ReconciliationAction:
        """Determine the appropriate remediation action"""
        if not drift_result.drift_detected:
            return ReconciliationAction.IGNORE

        # Check for critical security issues
        if any(
            keyword in str(drift_result.drift_details).lower()
            for keyword in ["security", "firewall", "access", "encryption"]
        ):
            return ReconciliationAction.REVERT

        # Check for resource state issues
        if "error" in drift_result.drift_details or "failed" in str(
            drift_result.drift_details
        ):
            return ReconciliationAction.RECREATE

        # Default to update for configuration drift
        return ReconciliationAction.UPDATE

    def _assess_safety_level(self, drift_result: DriftResult) -> SafetyLevel:
        """Assess the safety level required for remediation"""

        # Check for critical conditions
        if (
            hasattr(drift_result, "environment")
            and getattr(drift_result, "environment") == "production"
        ):
            return SafetyLevel.CRITICAL

        # Check for high-risk conditions
        if any(
            keyword in str(drift_result.drift_details).lower()
            for keyword in ["security", "firewall", "network", "encryption"]
        ):
            return SafetyLevel.HIGH

        # Check for medium-risk conditions
        if any(
            keyword in str(drift_result.drift_details).lower()
            for keyword in ["config", "settings", "parameter"]
        ):
            return SafetyLevel.MEDIUM

        return SafetyLevel.LOW

    async def _run_safety_checks(
        self, drift_result: DriftResult
    ) -> List[Dict[str, Any]]:
        """Run safety checks on a drift result"""
        safety_check_results = []

        # Get resource
        resource = self.nexus_engine._registry.get(drift_result.resource_id)
        if not resource:
            logger.warning(
                f"Resource {drift_result.resource_id} not found for safety checks"
            )
            return safety_check_results

        # Run each safety check
        for check_name, safety_check in self.safety_checks.items():
            if not safety_check.enabled:
                continue

            try:
                # Create context
                context = {
                    "drift_result": drift_result,
                    "timestamp": datetime.now(timezone.utc),
                }

                # Run check
                passed = safety_check.check_function(resource, context)

                result = {
                    "check_name": check_name,
                    "description": safety_check.description,
                    "severity": safety_check.severity.value,
                    "passed": passed,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

                safety_check_results.append(result)

            except Exception as e:
                logger.error(f"Safety check {check_name} failed: {e}")
                safety_check_results.append(
                    {
                        "check_name": check_name,
                        "description": safety_check.description,
                        "severity": safety_check.severity.value,
                        "passed": False,
                        "error": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

        return safety_check_results

    def _add_audit_entry(
        self, request: RemediationRequest, event: str, details: Dict[str, Any]
    ):
        """Add an audit trail entry"""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "details": details,
        }
        request.audit_trail.append(entry)

    async def _send_remediation_notification(
        self, request: RemediationRequest, event_type: str
    ):
        """Send notification for remediation event"""
        try:
            # Create notification event
            notification_event = NotificationEvent(
                id=f"rem-{request.id}-{event_type}",
                event_type=event_type,
                resource_id=request.drift_result.resource_id,
                resource_name=request.drift_result.resource_name,
                resource_type=request.drift_result.resource_type,
                message=f"Remediation {event_type.replace('_', ' ')}: {request.drift_result.resource_name}",
                details={
                    "request_id": request.id,
                    "safety_level": request.safety_level.value,
                    "proposed_action": request.proposed_action.value,
                    "status": request.status.value,
                    "requested_by": request.requested_by,
                },
                timestamp=datetime.now(timezone.utc),
                priority=self._get_notification_priority(request.safety_level),
            )

            # Send notification
            await self.notification_manager.send_notification(
                notification_event
            )

        except Exception as e:
            logger.error(f"Failed to send remediation notification: {e}")

    def _get_notification_priority(
        self, safety_level: SafetyLevel
    ) -> NotificationPriority:
        """Get notification priority for safety level"""
        if safety_level == SafetyLevel.CRITICAL:
            return NotificationPriority.CRITICAL
        elif safety_level == SafetyLevel.HIGH:
            return NotificationPriority.HIGH
        elif safety_level == SafetyLevel.MEDIUM:
            return NotificationPriority.MEDIUM
        else:
            return NotificationPriority.LOW

    async def _execute_remediation(self, request: RemediationRequest):
        """Execute a remediation request"""
        async with self.remediation_semaphore:
            try:
                # Update status
                request.status = RemediationStatus.IN_PROGRESS
                request.execution_started_at = datetime.now(timezone.utc)

                # Add audit trail
                self._add_audit_entry(
                    request,
                    "execution_started",
                    {
                        "started_at": request.execution_started_at.isoformat(),
                    },
                )

                # Send notification
                await self._send_remediation_notification(
                    request, "remediation_started"
                )

                # Execute actual remediation using the executor
                try:
                    await self.executor.execute_remediation_action(request)
                except Exception as e:
                    # If remediation fails, update status and raise
                    request.status = RemediationStatus.FAILED
                    request.execution_completed_at = datetime.now(timezone.utc)
                    self._add_audit_entry(
                        request,
                        "execution_failed",
                        {
                            "error": str(e),
                            "failed_at": request.execution_completed_at.isoformat(),
                        },
                    )
                    raise

                # Update status
                request.status = RemediationStatus.COMPLETED
                request.execution_completed_at = datetime.now(timezone.utc)

                # Add audit trail
                self._add_audit_entry(
                    request,
                    "execution_completed",
                    {
                        "completed_at": request.execution_completed_at.isoformat(),
                    },
                )

                # Update statistics
                self.stats["completed"] += 1

                # Send notification
                await self._send_remediation_notification(
                    request, "remediation_completed"
                )

                logger.info(f"Remediation completed: {request.id}")

            except Exception as e:
                # Handle failure
                request.status = RemediationStatus.FAILED

                # Add audit trail
                self._add_audit_entry(
                    request,
                    "execution_failed",
                    {
                        "error": str(e),
                        "failed_at": datetime.now(timezone.utc).isoformat(),
                    },
                )

                # Update statistics
                self.stats["failed"] += 1

                # Send notification
                await self._send_remediation_notification(
                    request, "remediation_failed"
                )

                logger.error(f"Remediation failed: {request.id} - {e}")

    async def _execute_rollback(
        self, request: RemediationRequest, rolled_back_by: str, reason: str
    ):
        """Execute rollback for a remediation"""
        logger.info(
            f"Executing rollback for {request.id} by {rolled_back_by}: {reason}"
        )

        try:
            # If we have the original state, restore it
            if "original_state" in request.remediation_data:
                await self.executor.restore_original_state(request)
            else:
                logger.warning(
                    f"No original state found for rollback of {request.id}"
                )

            # Add audit entry for rollback
            self._add_audit_entry(
                request,
                "rollback_completed",
                {
                    "rolled_back_by": rolled_back_by,
                    "reason": reason,
                    "rolled_back_at": datetime.now(timezone.utc).isoformat(),
                },
            )

            # Send notification
            await self._send_remediation_notification(
                request, "remediation_rolled_back"
            )

        except Exception as e:
            logger.error(f"Rollback failed for {request.id}: {e}")
            self._add_audit_entry(
                request,
                "rollback_failed",
                {
                    "rolled_back_by": rolled_back_by,
                    "reason": reason,
                    "error": str(e),
                    "failed_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            raise

    def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a remediation request"""
        if request_id not in self.remediation_requests:
            return None

        request = self.remediation_requests[request_id]
        return {
            "id": request.id,
            "status": request.status.value,
            "safety_level": request.safety_level.value,
            "proposed_action": request.proposed_action.value,
            "created_at": request.created_at.isoformat(),
            "requested_by": request.requested_by,
            "approved_by": request.approved_by,
            "rejected_by": request.rejected_by,
            "rejection_reason": request.rejection_reason,
            "audit_trail": request.audit_trail,
            "safety_checks": request.safety_checks,
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get remediation statistics"""
        return {
            "total_requests": self.stats["total_requests"],
            "by_status": {
                "pending": len(
                    [
                        r
                        for r in self.remediation_requests.values()
                        if r.status == RemediationStatus.PENDING
                    ]
                ),
                "approved": len(
                    [
                        r
                        for r in self.remediation_requests.values()
                        if r.status == RemediationStatus.APPROVED
                    ]
                ),
                "rejected": len(
                    [
                        r
                        for r in self.remediation_requests.values()
                        if r.status == RemediationStatus.REJECTED
                    ]
                ),
                "completed": len(
                    [
                        r
                        for r in self.remediation_requests.values()
                        if r.status == RemediationStatus.COMPLETED
                    ]
                ),
                "failed": len(
                    [
                        r
                        for r in self.remediation_requests.values()
                        if r.status == RemediationStatus.FAILED
                    ]
                ),
            },
            "auto_approved": self.stats["auto_approved"],
            "manual_approved": self.stats["manual_approved"],
            "rejected": self.stats["rejected"],
            "completed": self.stats["completed"],
            "failed": self.stats["failed"],
            "rolled_back": self.stats["rolled_back"],
            "escalated": self.stats["escalated"],
            "active_remediations": len(self.active_remediations),
            "safety_checks_configured": len(self.safety_checks),
            "approval_workflows_configured": len(self.approval_workflows),
        }

    def list_pending_requests(self) -> List[Dict[str, Any]]:
        """List pending remediation requests"""
        pending_requests = [
            r
            for r in self.remediation_requests.values()
            if r.status == RemediationStatus.PENDING
        ]

        return [
            {
                "id": req.id,
                "resource_name": req.drift_result.resource_name,
                "resource_type": req.drift_result.resource_type,
                "safety_level": req.safety_level.value,
                "proposed_action": req.proposed_action.value,
                "created_at": req.created_at.isoformat(),
                "requested_by": req.requested_by,
                "required_approvers": req.approvers,
            }
            for req in pending_requests
        ]
