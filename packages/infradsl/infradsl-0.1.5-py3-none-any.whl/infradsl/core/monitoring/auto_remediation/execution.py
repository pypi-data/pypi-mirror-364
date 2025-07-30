"""
Auto-Remediation Execution - Remediation execution and rollback logic
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any

from .models import RemediationRequest, RemediationStatus
from infradsl.core.nexus import NexusEngine
from infradsl.core.nexus.reconciler import StateReconciler

logger = logging.getLogger(__name__)


class RemediationExecutor:
    """Handles execution of remediation actions and rollbacks"""
    
    def __init__(self, nexus_engine: NexusEngine):
        self.nexus_engine = nexus_engine
    
    async def execute_remediation_action(self, request: RemediationRequest) -> None:
        """Execute the actual remediation action"""
        from infradsl.core.nexus.reconciler import StateReconciler

        logger.info(f"Executing remediation action for {request.id}")

        try:
            # Get the reconciler and resource
            reconciler = StateReconciler()

            # Get the resource from the nexus engine registry
            resource = self.nexus_engine.get_resource_by_id(
                request.drift_result.resource_id
            )

            if not resource:
                raise Exception(
                    f"Resource {request.drift_result.resource_id} not found"
                )

            # Get current and desired states
            current_state = request.drift_result.drift_details.get(
                "actual_state", {}
            )
            desired_state = request.drift_result.drift_details.get(
                "expected_state", {}
            )

            # Create reconciliation plan
            plan = reconciler.create_plan(
                resource, current_state, desired_state
            )

            # Validate the plan
            if not plan.is_valid():
                raise Exception(
                    f"Invalid reconciliation plan: {plan.validation_errors}"
                )

            # Execute the reconciliation plan
            result = await reconciler.execute_plan(
                plan, resource, dry_run=False
            )

            # Store the execution result
            request.remediation_data["execution_result"] = result

            # Check if remediation was successful
            if result.get("changes_failed", 0) > 0:
                raise Exception(
                    f"Remediation partially failed: {result.get('errors', [])}"
                )

            logger.info(f"Remediation action completed for {request.id}")

        except Exception as e:
            logger.error(
                f"Failed to execute remediation action for {request.id}: {e}"
            )
            raise

    async def restore_original_state(self, request: RemediationRequest) -> None:
        """Restore the original state of a resource (rollback)"""
        from infradsl.core.nexus.reconciler import StateReconciler

        logger.info(f"Restoring original state for {request.id}")

        try:
            # Get the reconciler and resource
            reconciler = StateReconciler()

            # Get the resource from the nexus engine registry
            resource = self.nexus_engine.get_resource_by_id(
                request.drift_result.resource_id
            )

            if not resource:
                raise Exception(
                    f"Resource {request.drift_result.resource_id} not found"
                )

            # Get current state and original state
            current_state = self.nexus_engine.get_resource_state(
                request.drift_result.resource_id
            )
            original_state = request.remediation_data["original_state"]

            # Create rollback reconciliation plan
            plan = reconciler.create_plan(
                resource, current_state, original_state
            )

            # Validate the rollback plan
            if not plan.is_valid():
                raise Exception(
                    f"Invalid rollback plan: {plan.validation_errors}"
                )

            # Execute the rollback plan
            result = await reconciler.execute_plan(
                plan, resource, dry_run=False
            )

            # Check if rollback was successful
            if result.get("changes_failed", 0) > 0:
                raise Exception(
                    f"Rollback partially failed: {result.get('errors', [])}"
                )

            logger.info(f"Original state restored for {request.id}")

        except Exception as e:
            logger.error(
                f"Failed to restore original state for {request.id}: {e}"
            )
            raise
    
    def create_rollback_plan(self, drift_result) -> Dict[str, Any]:
        """Create a rollback plan for a drift result"""
        return {
            "resource_id": drift_result.resource_id,
            "original_state": drift_result.drift_details,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "actions": [
                {
                    "action": "restore_configuration",
                    "parameters": drift_result.drift_details,
                }
            ],
        }