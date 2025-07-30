"""
InfraDSL Monitoring Module

This module provides real-time continuous drift monitoring capabilities
for infrastructure resources with multi-channel notifications.
"""

from .daemon import DriftMonitoringDaemon, MonitoringPolicy, DriftResult
from .notifications import (
    NotificationManager, 
    NotificationEvent, 
    NotificationPriority,
    NotificationChannel,
    NotificationRule,
    NotificationTemplate
)
from .integration import MonitoringIntegration, get_monitoring_integration, setup_monitoring_with_notifications
from .config import (
    MonitoringConfig, 
    MonitoringConfigManager, 
    get_config_manager,
    SlackConfig,
    EmailConfig,
    WebhookConfig
)
from .auto_remediation import (
    AutoRemediationEngine,
    RemediationRequest,
    SafetyCheck,
    ApprovalWorkflow,
    RemediationStatus,
    SafetyLevel
)
from .auto_remediation_integration import (
    AutoRemediationIntegration,
    get_auto_remediation_integration,
    setup_auto_remediation_integration
)

__all__ = [
    # Daemon components
    "DriftMonitoringDaemon",
    "MonitoringPolicy", 
    "DriftResult",
    
    # Notification components
    "NotificationManager",
    "NotificationEvent",
    "NotificationPriority",
    "NotificationChannel", 
    "NotificationRule",
    "NotificationTemplate",
    
    # Integration
    "MonitoringIntegration",
    "get_monitoring_integration",
    "setup_monitoring_with_notifications",
    
    # Configuration
    "MonitoringConfig",
    "MonitoringConfigManager",
    "get_config_manager",
    "SlackConfig",
    "EmailConfig",
    "WebhookConfig",
    
    # Auto-remediation
    "AutoRemediationEngine",
    "RemediationRequest",
    "SafetyCheck",
    "ApprovalWorkflow",
    "RemediationStatus",
    "SafetyLevel",
    "AutoRemediationIntegration",
    "get_auto_remediation_integration",
    "setup_auto_remediation_integration",
]