"""
Monitoring Integration - Connects drift monitoring daemon with notification system

This module provides integration between the DriftMonitoringDaemon and
NotificationManager to enable automatic notifications for drift events.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from .daemon import DriftMonitoringDaemon, DriftResult, MonitoringPolicy
from .notifications import (
    NotificationManager,
    NotificationEvent,
    NotificationPriority,
    NotificationChannel,
    NotificationRule,
    NotificationTemplate,
)

logger = logging.getLogger(__name__)


class MonitoringIntegration:
    """
    Integration class that connects drift monitoring with notifications
    """
    
    def __init__(
        self,
        daemon: Optional[DriftMonitoringDaemon] = None,
        notification_manager: Optional[NotificationManager] = None,
    ):
        self.daemon = daemon or DriftMonitoringDaemon()
        self.notification_manager = notification_manager or NotificationManager()
        self.configured = False
        
        # Setup default handlers
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default event handlers"""
        # Connect drift detected events to notifications
        self.daemon.add_drift_detected_handler(self._handle_drift_detected)
        
        # Connect check completed events for summary notifications
        self.daemon.add_check_completed_handler(self._handle_check_completed)
    
    async def _handle_drift_detected(self, drift_result: DriftResult):
        """Handle drift detected event"""
        try:
            # Create notification event
            notification_event = NotificationEvent(
                id=f"drift-{drift_result.resource_id}-{datetime.now(timezone.utc).timestamp()}",
                event_type="drift_detected",
                resource_id=drift_result.resource_id,
                resource_name=drift_result.resource_name,
                resource_type=drift_result.resource_type,
                message=f"Drift detected in {drift_result.resource_name}",
                details=drift_result.drift_details,
                timestamp=drift_result.check_timestamp,
                priority=self._determine_priority(drift_result),
                project=getattr(drift_result, 'project', None),
                environment=getattr(drift_result, 'environment', None),
                tags=getattr(drift_result, 'tags', None),
            )
            
            # Send notification
            await self.notification_manager.send_notification(notification_event)
            
        except Exception as e:
            logger.error(f"Error handling drift detected event: {e}")
    
    async def _handle_check_completed(self, drift_results: List[DriftResult]):
        """Handle check completed event"""
        try:
            # Only send summary if there are multiple results or critical drift
            drift_count = sum(1 for r in drift_results if r.drift_detected)
            
            if drift_count == 0:
                return  # No drift, no notification needed
            
            # Create summary notification
            notification_event = NotificationEvent(
                id=f"check-summary-{datetime.now(timezone.utc).timestamp()}",
                event_type="drift_check_summary",
                resource_id="multiple",
                resource_name="Infrastructure Check",
                resource_type="summary",
                message=f"Drift check completed: {drift_count} resources with drift detected",
                details={
                    "total_checked": len(drift_results),
                    "drift_detected": drift_count,
                    "resources_with_drift": [
                        r.resource_name for r in drift_results if r.drift_detected
                    ]
                },
                timestamp=datetime.now(timezone.utc),
                priority=NotificationPriority.MEDIUM if drift_count < 5 else NotificationPriority.HIGH,
            )
            
            # Send notification
            await self.notification_manager.send_notification(notification_event)
            
        except Exception as e:
            logger.error(f"Error handling check completed event: {e}")
    
    def _determine_priority(self, drift_result: DriftResult) -> NotificationPriority:
        """Determine notification priority based on drift result"""
        if not drift_result.drift_detected:
            return NotificationPriority.LOW
        
        # Check for critical drift indicators
        details = drift_result.drift_details
        
        # Security-related drift is critical
        security_indicators = [
            "security_groups", "firewall_rules", "network_access",
            "encryption", "backup_enabled", "monitoring_enabled"
        ]
        
        if any(indicator in str(details).lower() for indicator in security_indicators):
            return NotificationPriority.CRITICAL
        
        # Resource state changes are high priority
        if "error" in details or "failed" in str(details).lower():
            return NotificationPriority.HIGH
        
        # Configuration drift is medium priority
        return NotificationPriority.MEDIUM
    
    def configure_slack_notifications(
        self,
        webhook_url: str,
        channel: Optional[str] = None,
        rules: Optional[List[NotificationRule]] = None,
    ):
        """Configure Slack notifications"""
        # Configure Slack notifier
        self.notification_manager.configure_slack(webhook_url, channel)
        
        # Add default rules if none provided
        if not rules:
            rules = [
                NotificationRule(
                    name="slack_critical_drift",
                    channels=[NotificationChannel.SLACK],
                    event_types=["drift_detected"],
                    priority_threshold=NotificationPriority.CRITICAL,
                    filters={},
                ),
                NotificationRule(
                    name="slack_high_drift",
                    channels=[NotificationChannel.SLACK],
                    event_types=["drift_detected"],
                    priority_threshold=NotificationPriority.HIGH,
                    filters={},
                    rate_limit=10,  # Max 10 notifications per hour
                ),
                NotificationRule(
                    name="slack_summary",
                    channels=[NotificationChannel.SLACK],
                    event_types=["drift_check_summary"],
                    priority_threshold=NotificationPriority.MEDIUM,
                    filters={},
                    rate_limit=4,  # Max 4 summaries per hour
                ),
            ]
        
        # Add rules to notification manager
        for rule in rules:
            self.notification_manager.add_rule(rule)
        
        logger.info("Configured Slack notifications")
    
    def configure_email_notifications(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_email: str,
        rules: Optional[List[NotificationRule]] = None,
        use_tls: bool = True,
    ):
        """Configure email notifications"""
        # Configure email notifier
        self.notification_manager.configure_email(
            smtp_server, smtp_port, username, password, from_email, use_tls
        )
        
        # Add default rules if none provided
        if not rules:
            rules = [
                NotificationRule(
                    name="email_critical_drift",
                    channels=[NotificationChannel.EMAIL],
                    event_types=["drift_detected"],
                    priority_threshold=NotificationPriority.CRITICAL,
                    filters={},
                ),
                NotificationRule(
                    name="email_daily_summary",
                    channels=[NotificationChannel.EMAIL],
                    event_types=["drift_check_summary"],
                    priority_threshold=NotificationPriority.MEDIUM,
                    filters={},
                    rate_limit=1,  # Max 1 email per hour
                ),
            ]
        
        # Add rules to notification manager
        for rule in rules:
            self.notification_manager.add_rule(rule)
        
        logger.info("Configured email notifications")
    
    def configure_webhook_notifications(
        self,
        webhook_url: str,
        headers: Optional[Dict[str, str]] = None,
        rules: Optional[List[NotificationRule]] = None,
    ):
        """Configure webhook notifications"""
        # Configure webhook notifier
        self.notification_manager.configure_webhook(webhook_url, headers)
        
        # Add default rules if none provided
        if not rules:
            rules = [
                NotificationRule(
                    name="webhook_all_drift",
                    channels=[NotificationChannel.WEBHOOK],
                    event_types=["drift_detected", "drift_check_summary"],
                    priority_threshold=NotificationPriority.LOW,
                    filters={},
                ),
            ]
        
        # Add rules to notification manager
        for rule in rules:
            self.notification_manager.add_rule(rule)
        
        logger.info("Configured webhook notifications")
    
    def add_notification_templates(self):
        """Add default notification templates"""
        # Slack template
        slack_template = NotificationTemplate(
            name="slack_drift_template",
            content={
                "subject": "Infrastructure Drift Alert",
                "body": """🚨 *Drift Detected*
                
*Resource:* {{ resource_name }} ({{ resource_type }})
*Priority:* {{ priority|upper }}
*Timestamp:* {{ timestamp }}
*Message:* {{ message }}

{% if event.details %}
*Details:*
{% for key, value in event.details.items() %}
• {{ key }}: {{ value }}
{% endfor %}
{% endif %}
""",
            },
        )
        
        # Email template
        email_template = NotificationTemplate(
            name="email_drift_template",
            content={
                "subject": "[InfraDSL] Drift Alert - {{ resource_name }}",
                "body": """Infrastructure Drift Alert

Resource: {{ resource_name }} ({{ resource_type }})
Priority: {{ priority|upper }}
Timestamp: {{ timestamp }}
Project: {{ event.project or 'N/A' }}
Environment: {{ event.environment or 'N/A' }}

Message:
{{ message }}

{% if event.details %}
Details:
{% for key, value in event.details.items() %}
- {{ key }}: {{ value }}
{% endfor %}
{% endif %}

This alert was generated by InfraDSL Infrastructure Monitoring.
""",
            },
        )
        
        # Webhook template
        webhook_template = NotificationTemplate(
            name="webhook_drift_template",
            content={
                "body": """{
    "alert_type": "infrastructure_drift",
    "resource": {
        "id": "{{ resource_id }}",
        "name": "{{ resource_name }}",
        "type": "{{ resource_type }}"
    },
    "priority": "{{ priority }}",
    "timestamp": "{{ timestamp }}",
    "message": "{{ message }}",
    "details": {{ event.details|tojson }},
    "project": "{{ event.project }}",
    "environment": "{{ event.environment }}",
    "tags": {{ event.tags|tojson }}
}""",
            },
        )
        
        # Add templates to notification manager
        self.notification_manager.add_template(slack_template)
        self.notification_manager.add_template(email_template)
        self.notification_manager.add_template(webhook_template)
        
        logger.info("Added default notification templates")
    
    async def start(self):
        """Start the monitoring integration"""
        # Add default templates
        self.add_notification_templates()
        
        # Start the daemon
        await self.daemon.start()
        
        self.configured = True
        logger.info("Monitoring integration started")
    
    async def stop(self):
        """Stop the monitoring integration"""
        await self.daemon.stop()
        self.configured = False
        logger.info("Monitoring integration stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            "configured": self.configured,
            "daemon_status": self.daemon.get_status(),
            "notification_stats": self.notification_manager.get_statistics(),
        }


# Global monitoring integration instance
_monitoring_integration = None


def get_monitoring_integration() -> MonitoringIntegration:
    """Get the global monitoring integration instance"""
    global _monitoring_integration
    if _monitoring_integration is None:
        _monitoring_integration = MonitoringIntegration()
    return _monitoring_integration


async def setup_monitoring_with_notifications(
    slack_webhook: Optional[str] = None,
    email_config: Optional[Dict[str, Any]] = None,
    webhook_url: Optional[str] = None,
    monitoring_policies: Optional[List[MonitoringPolicy]] = None,
) -> MonitoringIntegration:
    """
    Convenience function to setup monitoring with notifications
    
    Args:
        slack_webhook: Slack webhook URL
        email_config: Email configuration dict
        webhook_url: Webhook URL
        monitoring_policies: Custom monitoring policies
    
    Returns:
        Configured MonitoringIntegration instance
    """
    integration = get_monitoring_integration()
    
    # Configure notifications
    if slack_webhook:
        integration.configure_slack_notifications(slack_webhook)
    
    if email_config:
        integration.configure_email_notifications(**email_config)
    
    if webhook_url:
        integration.configure_webhook_notifications(webhook_url)
    
    # Add custom policies
    if monitoring_policies:
        for policy in monitoring_policies:
            integration.daemon.add_policy(policy)
    
    # Start the integration
    await integration.start()
    
    return integration