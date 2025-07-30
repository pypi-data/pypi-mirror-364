"""
Self-Healing Reconciliation Engine

This module provides the self-healing engine and reconciliation policies
for automatically maintaining infrastructure in its desired state.
"""

from .policies import (
    ReconciliationPolicy,
    ReconciliationAction,
    DriftSeverity,
    ReconciliationTrigger,
    DriftEvent,
    ReconciliationResult,
    NotifyOnlyPolicy,
    RevertOnDriftPolicy,
    DestroyOnDriftPolicy,
    IgnoreDriftPolicy,
    CompositePolicy,
    create_default_policies,
    create_conservative_policies,
    create_aggressive_policies,
)
from .engine import (
    SelfHealingEngine,
    EngineConfig,
    EngineStatus,
    get_self_healing_engine,
)
from .notifications import (
    NotificationChannel,
    NotificationManager,
    ConsoleNotificationChannel,
    WebhookNotificationChannel,
    SlackNotificationChannel,
    EmailNotificationChannel,
    get_notification_manager,
    setup_default_notifications,
    setup_slack_notifications,
    setup_webhook_notifications,
)

__all__ = [
    # Policies
    "ReconciliationPolicy",
    "ReconciliationAction",
    "DriftSeverity",
    "ReconciliationTrigger",
    "DriftEvent",
    "ReconciliationResult",
    "NotifyOnlyPolicy",
    "RevertOnDriftPolicy",
    "DestroyOnDriftPolicy",
    "IgnoreDriftPolicy",
    "CompositePolicy",
    "create_default_policies",
    "create_conservative_policies",
    "create_aggressive_policies",
    # Engine
    "SelfHealingEngine",
    "EngineConfig",
    "EngineStatus",
    "get_self_healing_engine",
    # Notifications
    "NotificationChannel",
    "NotificationManager",
    "ConsoleNotificationChannel",
    "WebhookNotificationChannel",
    "SlackNotificationChannel",
    "EmailNotificationChannel",
    "get_notification_manager",
    "setup_default_notifications",
    "setup_slack_notifications",
    "setup_webhook_notifications",
]