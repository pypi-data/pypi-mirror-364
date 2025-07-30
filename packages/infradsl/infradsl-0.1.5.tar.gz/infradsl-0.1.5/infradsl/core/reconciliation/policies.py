"""
Reconciliation Policies for Self-Healing Engine

This module defines the reconciliation policies that determine how the self-healing
engine responds to detected drift and failures.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime, timedelta, timezone

from ..interfaces.provider import ProviderInterface
from ..nexus.base_resource import ResourceMetadata


logger = logging.getLogger(__name__)


class ReconciliationAction(Enum):
    """Actions that can be taken during reconciliation"""

    NOTIFY = "notify"  # Send notification only
    REVERT = "revert"  # Revert to desired state
    DESTROY = "destroy"  # Destroy drifted resource
    IGNORE = "ignore"  # Ignore the drift
    RECREATE = "recreate"  # Destroy and recreate resource
    UPDATE = "update"  # Update resource configuration


class DriftSeverity(Enum):
    """Severity levels for drift detection"""

    LOW = "low"  # Minor configuration drift
    MEDIUM = "medium"  # Significant configuration drift
    HIGH = "high"  # Critical drift or security issue
    CRITICAL = "critical"  # System-threatening drift


class ReconciliationTrigger(Enum):
    """Triggers for reconciliation actions"""

    DRIFT_DETECTED = "drift_detected"
    RESOURCE_FAILURE = "resource_failure"
    HEALTH_CHECK_FAILED = "health_check_failed"
    SECURITY_VIOLATION = "security_violation"
    COST_THRESHOLD_EXCEEDED = "cost_threshold_exceeded"
    SCHEDULED_CHECK = "scheduled_check"


@dataclass
class DriftEvent:
    """Information about a detected drift event"""

    resource_id: str
    resource_type: str
    resource_name: str
    provider: str
    project: str
    environment: str

    # Drift details
    drift_type: str
    severity: DriftSeverity
    trigger: ReconciliationTrigger
    detected_at: datetime

    # State information
    desired_state: Dict[str, Any]
    current_state: Dict[str, Any]
    diff: Dict[str, Any]

    # Context
    metadata: ResourceMetadata
    tags: Dict[str, str]

    # Previous events
    previous_events: Optional[List["DriftEvent"]] = None
    failure_count: int = 0


@dataclass
class ReconciliationResult:
    """Result of a reconciliation action"""

    action: ReconciliationAction
    success: bool
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    duration: float

    # Resource state after action
    final_state: Optional[Dict[str, Any]] = None

    # Notifications sent
    notifications_sent: Optional[List[str]] = None


class ReconciliationPolicy(ABC):
    """Base class for reconciliation policies"""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.enabled = True
        self.last_triggered: Optional[datetime] = None
        self.trigger_count = 0

    @abstractmethod
    def should_trigger(self, event: DriftEvent) -> bool:
        """Determine if this policy should trigger for the given event"""
        pass

    @abstractmethod
    def get_action(self, event: DriftEvent) -> ReconciliationAction:
        """Get the action to take for the given event"""
        pass

    @abstractmethod
    async def execute(
        self,
        event: DriftEvent,
        provider: ProviderInterface,
        notifier: Optional[Callable] = None,
    ) -> ReconciliationResult:
        """Execute the reconciliation action"""
        pass

    def can_trigger(self, event: DriftEvent) -> bool:
        """Check if policy can trigger (rate limiting, etc.)"""
        return self.enabled and self.should_trigger(event)


class NotifyOnlyPolicy(ReconciliationPolicy):
    """Policy that only sends notifications without taking action"""

    def __init__(
        self,
        name: str = "notify_only",
        severity_threshold: DriftSeverity = DriftSeverity.LOW,
        rate_limit_minutes: int = 60,
    ):
        super().__init__(name, "Send notifications for drift events")
        self.severity_threshold = severity_threshold
        self.rate_limit = timedelta(minutes=rate_limit_minutes)

    def should_trigger(self, event: DriftEvent) -> bool:
        # Check severity threshold
        severity_levels = {
            DriftSeverity.LOW: 0,
            DriftSeverity.MEDIUM: 1,
            DriftSeverity.HIGH: 2,
            DriftSeverity.CRITICAL: 3,
        }

        return (
            severity_levels[event.severity] >= severity_levels[self.severity_threshold]
        )

    def get_action(self, event: DriftEvent) -> ReconciliationAction:
        return ReconciliationAction.NOTIFY

    async def execute(
        self,
        event: DriftEvent,
        provider: ProviderInterface,
        notifier: Optional[Callable] = None,
    ) -> ReconciliationResult:
        start_time = datetime.now(timezone.utc)

        # Rate limiting
        if (
            self.last_triggered
            and datetime.now(timezone.utc) - self.last_triggered < self.rate_limit
        ):
            return ReconciliationResult(
                action=ReconciliationAction.NOTIFY,
                success=False,
                message="Rate limited",
                details={"rate_limit": self.rate_limit.total_seconds()},
                timestamp=start_time,
                duration=0,
                notifications_sent=[],
            )

        # Send notification
        notifications_sent = []
        if notifier:
            try:
                notification_message = self._format_notification(event)
                await notifier(notification_message)
                notifications_sent.append("default")
            except Exception as e:
                logger.error(f"Failed to send notification: {e}")

        self.last_triggered = start_time
        self.trigger_count += 1

        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()

        return ReconciliationResult(
            action=ReconciliationAction.NOTIFY,
            success=len(notifications_sent) > 0,
            message=f"Notification sent for {event.drift_type} drift",
            details={
                "drift_type": event.drift_type,
                "severity": event.severity.value,
                "resource": event.resource_name,
            },
            timestamp=start_time,
            duration=duration,
            notifications_sent=notifications_sent,
        )

    def _format_notification(self, event: DriftEvent) -> str:
        """Format notification message"""
        return f"""
🚨 Infrastructure Drift Detected

Resource: {event.resource_name} ({event.resource_type})
Project: {event.project}
Environment: {event.environment}
Provider: {event.provider}

Drift Type: {event.drift_type}
Severity: {event.severity.value}
Detected: {event.detected_at.isoformat()}

Changes:
{self._format_diff(event.diff)}

Resource ID: {event.resource_id}
""".strip()

    def _format_diff(self, diff: Dict[str, Any]) -> str:
        """Format diff for notification"""
        lines = []
        for key, value in diff.items():
            if isinstance(value, dict):
                old_val = value.get("old", "")
                new_val = value.get("new", "")
                lines.append(f"  {key}: {old_val} → {new_val}")
            else:
                lines.append(f"  {key}: {value}")
        return "\n".join(lines)


class RevertOnDriftPolicy(ReconciliationPolicy):
    """Policy that reverts resources to their desired state"""

    def __init__(
        self,
        name: str = "revert_on_drift",
        severity_threshold: DriftSeverity = DriftSeverity.MEDIUM,
        max_attempts: int = 3,
        backoff_minutes: int = 5,
    ):
        super().__init__(name, "Revert resources to desired state on drift")
        self.severity_threshold = severity_threshold
        self.max_attempts = max_attempts
        self.backoff_time = timedelta(minutes=backoff_minutes)

    def should_trigger(self, event: DriftEvent) -> bool:
        # Check severity threshold
        severity_levels = {
            DriftSeverity.LOW: 0,
            DriftSeverity.MEDIUM: 1,
            DriftSeverity.HIGH: 2,
            DriftSeverity.CRITICAL: 3,
        }

        if severity_levels[event.severity] < severity_levels[self.severity_threshold]:
            return False

        # Check failure count
        return event.failure_count < self.max_attempts

    def get_action(self, event: DriftEvent) -> ReconciliationAction:
        return ReconciliationAction.REVERT

    async def execute(
        self,
        event: DriftEvent,
        provider: ProviderInterface,
        notifier: Optional[Callable] = None,
    ) -> ReconciliationResult:
        start_time = datetime.now(timezone.utc)

        try:
            # Revert the resource to desired state
            logger.info(f"Reverting resource {event.resource_name} to desired state")

            # Extract changes needed to revert
            revert_changes = self._extract_revert_changes(event)

            # Apply the revert
            result = provider.update_resource(
                event.resource_id, event.resource_type, revert_changes
            )

            # Verify the revert was successful
            final_state = provider.get_resource(
                event.resource_id, event.resource_type
            )

            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()

            # Send notification about revert
            if notifier:
                try:
                    message = f"✅ Successfully reverted {event.resource_name} to desired state"
                    await notifier(message)
                except Exception as e:
                    logger.error(f"Failed to send revert notification: {e}")

            return ReconciliationResult(
                action=ReconciliationAction.REVERT,
                success=True,
                message=f"Successfully reverted {event.resource_name}",
                details={
                    "reverted_fields": list(revert_changes.keys()),
                    "revert_changes": revert_changes,
                },
                timestamp=start_time,
                duration=duration,
                final_state=final_state,
                notifications_sent=["revert_success"],
            )

        except Exception as e:
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()

            logger.error(f"Failed to revert resource {event.resource_name}: {e}")

            # Send failure notification
            if notifier:
                try:
                    message = f"❌ Failed to revert {event.resource_name}: {str(e)}"
                    await notifier(message)
                except Exception as ne:
                    logger.error(f"Failed to send failure notification: {ne}")

            return ReconciliationResult(
                action=ReconciliationAction.REVERT,
                success=False,
                message=f"Failed to revert {event.resource_name}: {str(e)}",
                details={
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                timestamp=start_time,
                duration=duration,
                notifications_sent=["revert_failure"],
            )

    def _extract_revert_changes(self, event: DriftEvent) -> Dict[str, Any]:
        """Extract the changes needed to revert to desired state"""
        revert_changes = {}

        for field, change in event.diff.items():
            if isinstance(change, dict) and "desired" in change:
                # This is a field that has drifted
                revert_changes[field] = change["desired"]

        return revert_changes


class DestroyOnDriftPolicy(ReconciliationPolicy):
    """Policy that destroys resources on critical drift"""

    def __init__(
        self,
        name: str = "destroy_on_drift",
        severity_threshold: DriftSeverity = DriftSeverity.HIGH,
        require_confirmation: bool = True,
        protected_resources: Optional[List[str]] = None,
    ):
        super().__init__(name, "Destroy resources on critical drift")
        self.severity_threshold = severity_threshold
        self.require_confirmation = require_confirmation
        self.protected_resources = protected_resources or []

    def should_trigger(self, event: DriftEvent) -> bool:
        # Check severity threshold
        severity_levels = {
            DriftSeverity.LOW: 0,
            DriftSeverity.MEDIUM: 1,
            DriftSeverity.HIGH: 2,
            DriftSeverity.CRITICAL: 3,
        }

        if severity_levels[event.severity] < severity_levels[self.severity_threshold]:
            return False

        # Check if resource is protected
        if event.resource_id in self.protected_resources:
            return False

        # Don't destroy databases or other critical resources
        if event.resource_type in ["database", "managed_database"]:
            return False

        return True

    def get_action(self, event: DriftEvent) -> ReconciliationAction:
        return ReconciliationAction.DESTROY

    async def execute(
        self,
        event: DriftEvent,
        provider: ProviderInterface,
        notifier: Optional[Callable] = None,
    ) -> ReconciliationResult:
        start_time = datetime.now(timezone.utc)

        # Send pre-destruction notification
        if notifier:
            try:
                message = f"🚨 CRITICAL: About to destroy {event.resource_name} due to {event.drift_type} drift"
                await notifier(message)
            except Exception as e:
                logger.error(f"Failed to send pre-destruction notification: {e}")

        try:
            # Destroy the resource
            logger.warning(
                f"Destroying resource {event.resource_name} due to critical drift"
            )

            provider.delete_resource(event.resource_id, event.resource_type)

            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()

            # Send destruction confirmation
            if notifier:
                try:
                    message = f"💥 DESTROYED: {event.resource_name} has been destroyed due to critical drift"
                    await notifier(message)
                except Exception as e:
                    logger.error(f"Failed to send destruction notification: {e}")

            return ReconciliationResult(
                action=ReconciliationAction.DESTROY,
                success=True,
                message=f"Successfully destroyed {event.resource_name}",
                details={
                    "reason": event.drift_type,
                    "severity": event.severity.value,
                },
                timestamp=start_time,
                duration=duration,
                notifications_sent=["destroy_success"],
            )

        except Exception as e:
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()

            logger.error(f"Failed to destroy resource {event.resource_name}: {e}")

            # Send failure notification
            if notifier:
                try:
                    message = f"❌ FAILED to destroy {event.resource_name}: {str(e)}"
                    await notifier(message)
                except Exception as ne:
                    logger.error(f"Failed to send failure notification: {ne}")

            return ReconciliationResult(
                action=ReconciliationAction.DESTROY,
                success=False,
                message=f"Failed to destroy {event.resource_name}: {str(e)}",
                details={
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                timestamp=start_time,
                duration=duration,
                notifications_sent=["destroy_failure"],
            )


class IgnoreDriftPolicy(ReconciliationPolicy):
    """Policy that ignores certain types of drift"""

    def __init__(
        self,
        name: str = "ignore_drift",
        ignored_fields: Optional[List[str]] = None,
        ignored_drift_types: Optional[List[str]] = None,
    ):
        super().__init__(name, "Ignore specific types of drift")
        self.ignored_fields = ignored_fields or [
            "last_seen",
            "uptime",
            "status_updated_at",
            "metrics",
        ]
        self.ignored_drift_types = ignored_drift_types or [
            "power_state",
            "temporary_status",
            "metrics_update",
        ]

    def should_trigger(self, event: DriftEvent) -> bool:
        # Check if drift type should be ignored
        if event.drift_type in self.ignored_drift_types:
            return True

        # Check if all drift is in ignored fields
        diff_fields = set(event.diff.keys())
        ignored_fields_set = set(self.ignored_fields)

        # If all changed fields are in ignored list, trigger ignore
        return diff_fields.issubset(ignored_fields_set)

    def get_action(self, event: DriftEvent) -> ReconciliationAction:
        return ReconciliationAction.IGNORE

    async def execute(
        self,
        event: DriftEvent,
        provider: ProviderInterface,
        notifier: Optional[Callable] = None,
    ) -> ReconciliationResult:
        start_time = datetime.now(timezone.utc)

        logger.info(f"Ignoring drift for {event.resource_name}: {event.drift_type}")

        # Optionally send notification about ignored drift
        if notifier and event.severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]:
            try:
                message = f"ℹ️ Ignoring {event.severity.value} drift for {event.resource_name}: {event.drift_type}"
                await notifier(message)
            except Exception as e:
                logger.error(f"Failed to send ignore notification: {e}")

        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()

        return ReconciliationResult(
            action=ReconciliationAction.IGNORE,
            success=True,
            message=f"Ignored drift for {event.resource_name}",
            details={
                "drift_type": event.drift_type,
                "ignored_fields": list(
                    set(event.diff.keys()) & set(self.ignored_fields)
                ),
            },
            timestamp=start_time,
            duration=duration,
            notifications_sent=(
                ["ignore"]
                if event.severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]
                else []
            ),
        )


class CompositePolicy(ReconciliationPolicy):
    """Policy that combines multiple policies with priority ordering"""

    def __init__(
        self,
        name: str = "composite_policy",
        policies: Optional[List[ReconciliationPolicy]] = None,
    ):
        super().__init__(name, "Composite policy with multiple rules")
        self.policies = policies or []

    def add_policy(self, policy: ReconciliationPolicy) -> None:
        """Add a policy to the composite"""
        self.policies.append(policy)

    def should_trigger(self, event: DriftEvent) -> bool:
        # Composite should trigger if any child policy should trigger
        return any(policy.can_trigger(event) for policy in self.policies)

    def get_action(self, event: DriftEvent) -> ReconciliationAction:
        # Return action from first policy that should trigger
        for policy in self.policies:
            if policy.can_trigger(event):
                return policy.get_action(event)
        return ReconciliationAction.IGNORE

    async def execute(
        self,
        event: DriftEvent,
        provider: ProviderInterface,
        notifier: Optional[Callable] = None,
    ) -> ReconciliationResult:
        # Execute first policy that should trigger
        for policy in self.policies:
            if policy.can_trigger(event):
                return await policy.execute(event, provider, notifier)

        # If no policy triggers, return ignore result
        return ReconciliationResult(
            action=ReconciliationAction.IGNORE,
            success=True,
            message="No policies triggered",
            details={"policies_evaluated": len(self.policies)},
            timestamp=datetime.now(timezone.utc),
            duration=0,
            notifications_sent=[],
        )


# Default policy configurations
def create_default_policies() -> List[ReconciliationPolicy]:
    """Create default reconciliation policies"""
    return [
        # Ignore minor drift
        IgnoreDriftPolicy(
            name="ignore_minor_drift",
            ignored_fields=["last_seen", "uptime", "status_updated_at", "metrics"],
            ignored_drift_types=["power_state", "temporary_status", "metrics_update"],
        ),
        # Notify on medium drift
        NotifyOnlyPolicy(
            name="notify_medium_drift",
            severity_threshold=DriftSeverity.MEDIUM,
            rate_limit_minutes=30,
        ),
        # Revert on high drift
        RevertOnDriftPolicy(
            name="revert_high_drift",
            severity_threshold=DriftSeverity.HIGH,
            max_attempts=3,
            backoff_minutes=5,
        ),
        # Destroy on critical security violations
        DestroyOnDriftPolicy(
            name="destroy_critical_security",
            severity_threshold=DriftSeverity.CRITICAL,
            require_confirmation=False,
            protected_resources=[],
        ),
    ]


def create_conservative_policies() -> List[ReconciliationPolicy]:
    """Create conservative reconciliation policies (notify only)"""
    return [
        NotifyOnlyPolicy(
            name="notify_all_drift",
            severity_threshold=DriftSeverity.LOW,
            rate_limit_minutes=15,
        ),
        IgnoreDriftPolicy(
            name="ignore_minor_drift",
            ignored_fields=["last_seen", "uptime", "status_updated_at", "metrics"],
            ignored_drift_types=["power_state", "temporary_status", "metrics_update"],
        ),
    ]


def create_aggressive_policies() -> List[ReconciliationPolicy]:
    """Create aggressive reconciliation policies (auto-remediate)"""
    return [
        # Ignore very minor drift
        IgnoreDriftPolicy(
            name="ignore_minor_drift",
            ignored_fields=["last_seen", "uptime", "status_updated_at", "metrics"],
            ignored_drift_types=["power_state", "temporary_status", "metrics_update"],
        ),
        # Revert on medium drift
        RevertOnDriftPolicy(
            name="revert_medium_drift",
            severity_threshold=DriftSeverity.MEDIUM,
            max_attempts=5,
            backoff_minutes=2,
        ),
        # Destroy on high drift
        DestroyOnDriftPolicy(
            name="destroy_high_drift",
            severity_threshold=DriftSeverity.HIGH,
            require_confirmation=False,
            protected_resources=[],
        ),
    ]
