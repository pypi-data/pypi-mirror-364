"""
Notification system for the self-healing engine

This module provides notification channels for sending alerts about
drift events and reconciliation actions.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .policies import DriftEvent, ReconciliationResult

logger = logging.getLogger(__name__)


class NotificationChannel(ABC):
    """Base class for notification channels"""

    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled

    @abstractmethod
    async def send(
        self, message: str, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send a notification message"""
        pass

    def is_enabled(self) -> bool:
        """Check if a channel is enabled"""
        return self.enabled


class ConsoleNotificationChannel(NotificationChannel):
    """Console notification channel for development/testing"""

    def __init__(self, name: str = "console"):
        super().__init__(name)

    async def send(
        self, message: str, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send notification to console"""
        try:
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            formatted_message = f"[{timestamp}] INFRADSL ALERT: {message}"

            # Use logger for console output
            logger.info(formatted_message)

            # Also print to stdout for immediate visibility
            print(formatted_message)

            return True
        except Exception as e:
            logger.error(f"Console notification failed: {e}")
            return False


class WebhookNotificationChannel(NotificationChannel):
    """Webhook notification channel for external services"""

    def __init__(
        self,
        name: str,
        webhook_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
    ):
        super().__init__(name)
        self.webhook_url = webhook_url
        self.headers = headers or {"Content-Type": "application/json"}
        self.timeout = timeout

    async def send(
        self, message: str, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send notification via webhook"""
        try:
            import aiohttp

            payload = {
                "timestamp": datetime.utcnow().isoformat(),
                "service": "infradsl",
                "alert_type": "self_healing",
                "message": message,
                "metadata": metadata or {},
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as response:
                    if response.status >= 400:
                        logger.error(f"Webhook returned status {response.status}")
                        return False

                    return True

        except Exception as e:
            logger.error(f"Webhook notification failed: {e}")
            return False


class SlackNotificationChannel(NotificationChannel):
    """Slack notification channel"""

    def __init__(
        self,
        name: str,
        webhook_url: str,
        channel: Optional[str] = None,
        username: str = "InfraDSL",
        emoji: str = ":robot_face:",
    ):
        super().__init__(name)
        self.webhook_url = webhook_url
        self.channel = channel
        self.username = username
        self.emoji = emoji

    async def send(
        self, message: str, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send notification to Slack"""
        try:
            import aiohttp

            # Format message for Slack
            formatted_message = self._format_slack_message(message, metadata)

            payload = {
                "text": formatted_message,
                "username": self.username,
                "icon_emoji": self.emoji,
            }

            if self.channel:
                payload["channel"] = self.channel

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status >= 400:
                        logger.error(f"Slack webhook returned status {response.status}")
                        return False

                    return True

        except Exception as e:
            logger.error(f"Slack notification failed: {e}")
            return False

    def _format_slack_message(
        self, message: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format message for Slack"""
        # Add Markdown formatting
        formatted = f"*InfraDSL Self-Healing Alert*\n\n{message}"

        if metadata:
            formatted += "\n\n*Details:*"
            for key, value in metadata.items():
                formatted += f"\n• {key}: {value}"

        return formatted


class EmailNotificationChannel(NotificationChannel):
    """Email notification channel"""

    def __init__(
        self,
        name: str,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_email: str,
        to_emails: List[str],
        use_tls: bool = True,
    ):
        super().__init__(name)
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails
        self.use_tls = use_tls

    async def send(
        self, message: str, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send notification via email"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            # Create a message
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = ", ".join(self.to_emails)
            msg["Subject"] = "InfraDSL Self-Healing Alert"

            # Format email body
            body = self._format_email_body(message, metadata)
            msg.attach(MIMEText(body, "plain"))

            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)

            if self.use_tls:
                server.starttls()

            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()

            return True

        except Exception as e:
            logger.error(f"Email notification failed: {e}")
            return False

    def _format_email_body(
        self, message: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format email body"""
        body = f"""
InfraDSL Self-Healing Alert

{message}

Timestamp: {datetime.utcnow().isoformat()}
"""

        if metadata:
            body += "\n\nDetails:\n"
            for key, value in metadata.items():
                body += f"  {key}: {value}\n"

        return body


class NotificationManager:
    """Manages multiple notification channels"""

    def __init__(self):
        self.channels: Dict[str, NotificationChannel] = {}
        self.stats = {
            "notifications_sent": 0,
            "notifications_failed": 0,
            "channels_active": 0,
        }

    def add_channel(self, channel: NotificationChannel) -> None:
        """Add a notification channel"""
        self.channels[channel.name] = channel
        self.stats["channels_active"] = len(
            [c for c in self.channels.values() if c.is_enabled()]
        )
        logger.info(f"Added notification channel: {channel.name}")

    def remove_channel(self, channel_name: str) -> bool:
        """Remove a notification channel"""
        if channel_name in self.channels:
            del self.channels[channel_name]
            self.stats["channels_active"] = len(
                [c for c in self.channels.values() if c.is_enabled()]
            )
            logger.info(f"Removed notification channel: {channel_name}")
            return True
        return False

    def enable_channel(self, channel_name: str) -> bool:
        """Enable a notification channel"""
        if channel_name in self.channels:
            self.channels[channel_name].enabled = True
            self.stats["channels_active"] = len(
                [c for c in self.channels.values() if c.is_enabled()]
            )
            return True
        return False

    def disable_channel(self, channel_name: str) -> bool:
        """Disable a notification channel"""
        if channel_name in self.channels:
            self.channels[channel_name].enabled = False
            self.stats["channels_active"] = len(
                [c for c in self.channels.values() if c.is_enabled()]
            )
            return True
        return False

    async def send_notification(
        self, message: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bool]:
        """Send notification to all enabled channels"""
        results = {}

        # Get enabled channels
        enabled_channels = [c for c in self.channels.values() if c.is_enabled()]

        if not enabled_channels:
            logger.warning("No enabled notification channels")
            return results

        # Send it to all channels concurrently
        tasks = []
        for channel in enabled_channels:
            task = asyncio.create_task(
                self._send_to_channel(channel, message, metadata)
            )
            tasks.append((channel.name, task))

        # Wait for all tasks to complete
        for channel_name, task in tasks:
            try:
                success = await task
                results[channel_name] = success

                if success:
                    self.stats["notifications_sent"] += 1
                else:
                    self.stats["notifications_failed"] += 1

            except Exception as e:
                logger.error(f"Notification task failed for {channel_name}: {e}")
                results[channel_name] = False
                self.stats["notifications_failed"] += 1

        return results

    async def _send_to_channel(
        self,
        channel: NotificationChannel,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Send notification to a single channel"""
        try:
            return await channel.send(message, metadata)
        except Exception as e:
            logger.error(f"Failed to send notification to {channel.name}: {e}")
            return False

    async def send_drift_event_notification(self, event: DriftEvent) -> Dict[str, bool]:
        """Send notification for a drift event"""
        message = f"""
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

        metadata = {
            "resource_name": event.resource_name,
            "resource_type": event.resource_type,
            "project": event.project,
            "environment": event.environment,
            "provider": event.provider,
            "drift_type": event.drift_type,
            "severity": event.severity.value,
            "resource_id": event.resource_id,
        }

        return await self.send_notification(message, metadata)

    async def send_reconciliation_result_notification(
        self, result: ReconciliationResult
    ) -> Dict[str, bool]:
        """Send notification for a reconciliation result"""

        status_emoji = "✅" if result.success else "❌"
        action_emoji = {
            "notify": "📢",
            "revert": "↩️",
            "destroy": "💥",
            "ignore": "🙈",
            "recreate": "🔄",
            "update": "📝",
        }

        emoji = action_emoji.get(result.action.value, "🔧")

        message = f"""
{status_emoji} Reconciliation {result.action.value.title()}

Status: {'SUCCESS' if result.success else 'FAILED'}
Action: {emoji} {result.action.value.upper()}
Duration: {result.duration:.2f}s
Timestamp: {result.timestamp.isoformat()}

Message: {result.message}
""".strip()

        if result.details:
            message += f"\n\nDetails: {json.dumps(result.details, indent=2)}"

        metadata = {
            "action": result.action.value,
            "success": result.success,
            "duration": result.duration,
            "timestamp": result.timestamp.isoformat(),
            "message": result.message,
        }

        return await self.send_notification(message, metadata)

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

    def get_stats(self) -> Dict[str, Any]:
        """Get notification statistics"""
        return {
            **self.stats,
            "channels_configured": len(self.channels),
            "channels_enabled": len(
                [c for c in self.channels.values() if c.is_enabled()]
            ),
            "channels": [
                {
                    "name": channel.name,
                    "enabled": channel.enabled,
                    "type": type(channel).__name__,
                }
                for channel in self.channels.values()
            ],
        }


# Global notification manager instance
_notification_manager = None


def get_notification_manager() -> NotificationManager:
    """Get the global notification manager instance"""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager


def setup_default_notifications() -> NotificationManager:
    """Set up default notification channels"""
    manager = get_notification_manager()

    # Add console channel for development
    console_channel = ConsoleNotificationChannel()
    manager.add_channel(console_channel)

    logger.info("Default notification channels configured")
    return manager


def setup_slack_notifications(
    webhook_url: str, channel: Optional[str] = None
) -> NotificationManager:
    """Set up Slack notifications"""
    manager = get_notification_manager()

    slack_channel = SlackNotificationChannel(
        name="slack", webhook_url=webhook_url, channel=channel
    )
    manager.add_channel(slack_channel)

    logger.info("Slack notification channel configured")
    return manager


def setup_webhook_notifications(
    webhook_url: str, headers: Optional[Dict[str, str]] = None
) -> NotificationManager:
    """Set up webhook notifications"""
    manager = get_notification_manager()

    webhook_channel = WebhookNotificationChannel(
        name="webhook", webhook_url=webhook_url, headers=headers
    )
    manager.add_channel(webhook_channel)

    logger.info("Webhook notification channel configured")
    return manager
