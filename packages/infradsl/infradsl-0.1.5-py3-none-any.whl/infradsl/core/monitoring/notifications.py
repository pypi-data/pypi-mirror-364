"""
Notification System - Multi-channel notification management

This module implements the NotificationManager class that provides
Slack, email, and webhook notification capabilities with templating
and rate limiting.
"""

import asyncio
import logging
import smtplib
import ssl
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import json
import aiohttp
import jinja2
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class NotificationChannel(Enum):
    """Notification channel types"""
    SLACK = "slack"
    EMAIL = "email"
    WEBHOOK = "webhook"
    TEAMS = "teams"
    DISCORD = "discord"


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class NotificationEvent:
    """Notification event data"""
    id: str
    event_type: str
    resource_id: str
    resource_name: str
    resource_type: str
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    priority: NotificationPriority
    project: Optional[str] = None
    environment: Optional[str] = None
    tags: Optional[List[str]] = None


@dataclass
class NotificationRule:
    """Notification rule configuration"""
    name: str
    channels: List[NotificationChannel]
    event_types: List[str]
    priority_threshold: NotificationPriority
    filters: Dict[str, Any]
    template_name: Optional[str] = None
    rate_limit: Optional[int] = None  # Max notifications per hour
    enabled: bool = True


class NotificationTemplate:
    """Notification template with Jinja2 support"""
    
    def __init__(self, name: str, content: Dict[str, str]):
        self.name = name
        self.content = content  # {"subject": "...", "body": "..."}
        self.jinja_env = jinja2.Environment(
            loader=jinja2.DictLoader(content),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
    
    def render(self, template_type: str, context: Dict[str, Any]) -> str:
        """Render template with context"""
        if template_type not in self.content:
            raise ValueError(f"Template type {template_type} not found in {self.name}")
        
        template = self.jinja_env.get_template(template_type)
        return template.render(**context)


class RateLimiter:
    """Rate limiter for notifications"""
    
    def __init__(self, max_notifications: int, window_seconds: int = 3600):
        self.max_notifications = max_notifications
        self.window_seconds = window_seconds
        self.notifications: List[datetime] = []
    
    def can_send(self) -> bool:
        """Check if we can send a notification"""
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(seconds=self.window_seconds)
        
        # Remove old notifications
        self.notifications = [n for n in self.notifications if n > cutoff]
        
        return len(self.notifications) < self.max_notifications
    
    def record_notification(self):
        """Record a notification"""
        self.notifications.append(datetime.now(timezone.utc))


class SlackNotifier:
    """Slack notification handler"""
    
    def __init__(self, webhook_url: str, default_channel: Optional[str] = None):
        self.webhook_url = webhook_url
        self.default_channel = default_channel
    
    async def send_notification(self, event: NotificationEvent, template: Optional[NotificationTemplate] = None) -> bool:
        """Send Slack notification"""
        try:
            # Build message
            if template:
                context = {
                    "event": asdict(event),
                    "resource_id": event.resource_id,
                    "resource_name": event.resource_name,
                    "resource_type": event.resource_type,
                    "message": event.message,
                    "priority": event.priority.value,
                    "timestamp": event.timestamp.isoformat(),
                }
                message = template.render("body", context)
            else:
                message = self._format_default_message(event)
            
            # Build Slack payload
            payload = {
                "text": message,
                "username": "InfraDSL Monitor",
                "icon_emoji": ":warning:" if event.priority in [NotificationPriority.HIGH, NotificationPriority.CRITICAL] else ":information_source:",
                "attachments": [
                    {
                        "color": self._get_color_for_priority(event.priority),
                        "fields": [
                            {
                                "title": "Resource",
                                "value": f"{event.resource_name} ({event.resource_type})",
                                "short": True
                            },
                            {
                                "title": "Priority",
                                "value": event.priority.value.upper(),
                                "short": True
                            },
                            {
                                "title": "Timestamp",
                                "value": event.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
                                "short": True
                            }
                        ]
                    }
                ]
            }
            
            if self.default_channel:
                payload["channel"] = self.default_channel
            
            # Send to Slack
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Slack notification sent for event {event.id}")
                        return True
                    else:
                        logger.error(f"Failed to send Slack notification: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
            return False
    
    def _format_default_message(self, event: NotificationEvent) -> str:
        """Format default message"""
        priority_emoji = {
            NotificationPriority.LOW: ":information_source:",
            NotificationPriority.MEDIUM: ":warning:",
            NotificationPriority.HIGH: ":exclamation:",
            NotificationPriority.CRITICAL: ":rotating_light:"
        }
        
        emoji = priority_emoji.get(event.priority, ":information_source:")
        return f"{emoji} *{event.event_type}* - {event.message}"
    
    def _get_color_for_priority(self, priority: NotificationPriority) -> str:
        """Get color for priority level"""
        colors = {
            NotificationPriority.LOW: "good",
            NotificationPriority.MEDIUM: "warning",
            NotificationPriority.HIGH: "danger",
            NotificationPriority.CRITICAL: "danger"
        }
        return colors.get(priority, "good")


class DiscordNotifier:
    """Discord notification handler"""
    
    def __init__(self, webhook_url: str, username: Optional[str] = None):
        self.webhook_url = webhook_url
        self.username = username or "InfraDSL Monitor"
    
    async def send_notification(self, event: NotificationEvent, template: Optional[NotificationTemplate] = None) -> bool:
        """Send Discord notification"""
        print(f"[DEBUG] DiscordNotifier.send_notification called for event: {event.event_type}")
        try:
            # Build message
            if template:
                context = {
                    "event": asdict(event),
                    "resource_id": event.resource_id,
                    "resource_name": event.resource_name,
                    "resource_type": event.resource_type,
                    "message": event.message,
                    "priority": event.priority.value,
                    "timestamp": event.timestamp.isoformat(),
                }
                content = template.render("body", context)
            else:
                content = self._format_default_message(event)
            
            # Build Discord embed payload
            title = self._get_event_title(event)
            embed = {
                "title": title,
                "description": event.message,
                "color": self._get_color_for_event(event),
                "fields": [
                    {
                        "name": "Resource",
                        "value": f"`{event.resource_name}` ({event.resource_type})",
                        "inline": True
                    },
                    {
                        "name": "Priority", 
                        "value": event.priority.value.upper(),
                        "inline": True
                    },
                    {
                        "name": "Resource ID",
                        "value": f"`{event.resource_id}`",
                        "inline": True
                    }
                ],
                "timestamp": event.timestamp.isoformat(),
                "footer": {
                    "text": "InfraDSL Infrastructure Monitor"
                }
            }
            
            # Add project/environment info if available
            if event.project:
                embed["fields"].append({
                    "name": "Project",
                    "value": event.project,
                    "inline": True
                })
            
            if event.environment:
                embed["fields"].append({
                    "name": "Environment", 
                    "value": event.environment,
                    "inline": True
                })
            
            payload = {
                "username": self.username,
                "content": content if not template else None,
                "embeds": [embed]
            }
            
            # Send to Discord
            print(f"[DEBUG] Sending Discord webhook to: {self.webhook_url[:50]}...")
            print(f"[DEBUG] Payload: {payload}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    response_text = await response.text()
                    print(f"[DEBUG] Discord response status: {response.status}")
                    print(f"[DEBUG] Discord response body: {response_text}")
                    
                    if response.status == 204:  # Discord returns 204 for successful webhook
                        logger.info(f"Discord notification sent for event {event.id}")
                        print(f"[DEBUG] Discord webhook sent successfully!")
                        return True
                    else:
                        logger.error(f"Failed to send Discord notification: {response.status}")
                        print(f"[DEBUG] Discord webhook failed with status {response.status}: {response_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending Discord notification: {e}")
            print(f"[DEBUG] Discord notification exception: {e}")
            import traceback
            print(f"[DEBUG] Full traceback:")
            traceback.print_exc()
            return False
    
    def _format_default_message(self, event: NotificationEvent) -> str:
        """Format default message - not used when embeds are present"""
        return None  # We use embeds instead of plain content
    
    def _get_event_title(self, event: NotificationEvent) -> str:
        """Get formatted title for event type"""
        title_map = {
            "after_create": "✅ Infrastructure Created",
            "after_update": "🔄 Infrastructure Updated",
            "after_destroy": "🗑️ Infrastructure Destroyed",
            "on_drift": "⚠️ Configuration Drift Detected",
            "on_error": "❌ Infrastructure Error"
        }
        return title_map.get(event.event_type, f"📋 {event.event_type}")
    
    def _get_color_for_event(self, event: NotificationEvent) -> int:
        """Get color based on event type (Discord uses integer colors)"""
        colors = {
            "after_create": 0x00FF00,      # Green for creation
            "after_update": 0x3498DB,      # Blue for updates
            "after_destroy": 0x95A5A6,     # Gray for destruction
            "on_drift": 0xFFFF00,          # Yellow for drift
            "on_error": 0xFF0000           # Red for errors
        }
        return colors.get(event.event_type, 0x00FF00)


class TeamsNotifier:
    """Microsoft Teams notification handler"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def send_notification(self, event: NotificationEvent, template: Optional[NotificationTemplate] = None) -> bool:
        """Send Teams notification"""
        try:
            # Build message
            if template:
                context = {
                    "event": asdict(event),
                    "resource_id": event.resource_id,
                    "resource_name": event.resource_name,
                    "resource_type": event.resource_type,
                    "message": event.message,
                    "priority": event.priority.value,
                    "timestamp": event.timestamp.isoformat(),
                }
                summary = template.render("body", context)
            else:
                summary = self._format_default_message(event)
            
            # Build Teams Adaptive Card payload
            payload = {
                "@type": "MessageCard",
                "@context": "https://schema.org/extensions",
                "summary": summary,
                "themeColor": self._get_color_for_priority(event.priority),
                "sections": [
                    {
                        "activityTitle": f"{event.event_type} - {event.resource_name}",
                        "activitySubtitle": event.message,
                        "facts": [
                            {
                                "name": "Resource",
                                "value": f"{event.resource_name} ({event.resource_type})"
                            },
                            {
                                "name": "Priority",
                                "value": event.priority.value.upper()
                            },
                            {
                                "name": "Resource ID",
                                "value": event.resource_id
                            },
                            {
                                "name": "Timestamp",
                                "value": event.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
                            }
                        ]
                    }
                ]
            }
            
            # Add project/environment info if available
            if event.project:
                payload["sections"][0]["facts"].append({
                    "name": "Project",
                    "value": event.project
                })
            
            if event.environment:
                payload["sections"][0]["facts"].append({
                    "name": "Environment", 
                    "value": event.environment
                })
            
            # Send to Teams
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Teams notification sent for event {event.id}")
                        return True
                    else:
                        logger.error(f"Failed to send Teams notification: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending Teams notification: {e}")
            return False
    
    def _format_default_message(self, event: NotificationEvent) -> str:
        """Format default message"""
        return f"{event.event_type} - {event.message}"
    
    def _get_color_for_priority(self, priority: NotificationPriority) -> str:
        """Get color for priority level (Teams uses hex colors)"""
        colors = {
            NotificationPriority.LOW: "00FF00",      # Green
            NotificationPriority.MEDIUM: "FFD700",   # Gold
            NotificationPriority.HIGH: "FF6600",     # Orange
            NotificationPriority.CRITICAL: "FF0000"  # Red
        }
        return colors.get(priority, "00FF00")


class EmailNotifier:
    """Email notification handler"""
    
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_email: str,
        use_tls: bool = True
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.use_tls = use_tls
    
    async def send_notification(
        self,
        event: NotificationEvent,
        to_emails: List[str],
        template: Optional[NotificationTemplate] = None
    ) -> bool:
        """Send email notification"""
        try:
            # Build email content
            if template:
                context = {
                    "event": asdict(event),
                    "resource_id": event.resource_id,
                    "resource_name": event.resource_name,
                    "resource_type": event.resource_type,
                    "message": event.message,
                    "priority": event.priority.value,
                    "timestamp": event.timestamp.isoformat(),
                }
                subject = template.render("subject", context)
                body = template.render("body", context)
            else:
                subject = f"[InfraDSL] {event.event_type} - {event.resource_name}"
                body = self._format_default_email_body(event)
            
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = ", ".join(to_emails)
            msg["Subject"] = subject
            
            msg.attach(MIMEText(body, "plain"))
            
            # Send email
            await self._send_email(msg, to_emails)
            
            logger.info(f"Email notification sent for event {event.id} to {len(to_emails)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return False
    
    async def _send_email(self, msg: MIMEMultipart, to_emails: List[str]):
        """Send email using SMTP"""
        # Run in executor to avoid blocking
        await asyncio.get_event_loop().run_in_executor(
            None, self._send_email_sync, msg, to_emails
        )
    
    def _send_email_sync(self, msg: MIMEMultipart, to_emails: List[str]):
        """Send email synchronously"""
        context = ssl.create_default_context()
        
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            if self.use_tls:
                server.starttls(context=context)
            
            server.login(self.username, self.password)
            server.sendmail(self.from_email, to_emails, msg.as_string())
    
    def _format_default_email_body(self, event: NotificationEvent) -> str:
        """Format default email body"""
        return f"""
InfraDSL Infrastructure Monitoring Alert

Event Type: {event.event_type}
Resource: {event.resource_name} ({event.resource_type})
Resource ID: {event.resource_id}
Priority: {event.priority.value.upper()}
Timestamp: {event.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

Message:
{event.message}

Details:
{json.dumps(event.details, indent=2)}

Project: {event.project or 'N/A'}
Environment: {event.environment or 'N/A'}
Tags: {', '.join(event.tags or [])}

---
This alert was generated by InfraDSL Infrastructure Monitoring
"""


class WebhookNotifier:
    """Webhook notification handler"""
    
    def __init__(self, webhook_url: str, headers: Optional[Dict[str, str]] = None):
        self.webhook_url = webhook_url
        self.headers = headers or {"Content-Type": "application/json"}
    
    async def send_notification(self, event: NotificationEvent, template: Optional[NotificationTemplate] = None) -> bool:
        """Send webhook notification"""
        try:
            # Build payload
            if template:
                context = {
                    "event": asdict(event),
                    "resource_id": event.resource_id,
                    "resource_name": event.resource_name,
                    "resource_type": event.resource_type,
                    "message": event.message,
                    "priority": event.priority.value,
                    "timestamp": event.timestamp.isoformat(),
                }
                payload_str = template.render("body", context)
                payload = json.loads(payload_str)
            else:
                payload = {
                    "event_id": event.id,
                    "event_type": event.event_type,
                    "resource_id": event.resource_id,
                    "resource_name": event.resource_name,
                    "resource_type": event.resource_type,
                    "message": event.message,
                    "priority": event.priority.value,
                    "timestamp": event.timestamp.isoformat(),
                    "details": event.details,
                    "project": event.project,
                    "environment": event.environment,
                    "tags": event.tags,
                }
            
            # Send webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers=self.headers
                ) as response:
                    if response.status in [200, 201, 202]:
                        logger.info(f"Webhook notification sent for event {event.id}")
                        return True
                    else:
                        logger.error(f"Failed to send webhook notification: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending webhook notification: {e}")
            return False


class NotificationManager:
    """
    Notification manager with multi-channel support, templating,
    and rate limiting.
    """
    
    def __init__(self):
        self.rules: List[NotificationRule] = []
        self.templates: Dict[str, NotificationTemplate] = {}
        self.rate_limiters: Dict[str, RateLimiter] = {}
        self.notifiers: Dict[NotificationChannel, Any] = {}
        self.notification_history: List[NotificationEvent] = []
        self.deduplication_cache: Dict[str, datetime] = {}
        self.deduplication_window = timedelta(minutes=5)
    
    def add_rule(self, rule: NotificationRule):
        """Add a notification rule"""
        self.rules.append(rule)
        
        # Create rate limiter if specified
        if rule.rate_limit:
            self.rate_limiters[rule.name] = RateLimiter(rule.rate_limit)
        
        logger.info(f"Added notification rule: {rule.name}")
    
    def remove_rule(self, rule_name: str):
        """Remove a notification rule"""
        self.rules = [r for r in self.rules if r.name != rule_name]
        
        # Remove rate limiter
        if rule_name in self.rate_limiters:
            del self.rate_limiters[rule_name]
        
        logger.info(f"Removed notification rule: {rule_name}")
    
    def add_template(self, template: NotificationTemplate):
        """Add a notification template"""
        self.templates[template.name] = template
        logger.info(f"Added notification template: {template.name}")
    
    def configure_slack(self, webhook_url: str, default_channel: Optional[str] = None):
        """Configure Slack notifier"""
        self.notifiers[NotificationChannel.SLACK] = SlackNotifier(webhook_url, default_channel)
        logger.info("Configured Slack notifier")
    
    def configure_email(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_email: str,
        use_tls: bool = True
    ):
        """Configure email notifier"""
        self.notifiers[NotificationChannel.EMAIL] = EmailNotifier(
            smtp_server, smtp_port, username, password, from_email, use_tls
        )
        logger.info("Configured email notifier")
    
    def configure_webhook(self, webhook_url: str, headers: Optional[Dict[str, str]] = None):
        """Configure webhook notifier"""
        self.notifiers[NotificationChannel.WEBHOOK] = WebhookNotifier(webhook_url, headers)
        logger.info("Configured webhook notifier")
    
    def configure_discord(self, webhook_url: str, username: Optional[str] = None):
        """Configure Discord notifier"""
        self.notifiers[NotificationChannel.DISCORD] = DiscordNotifier(webhook_url, username)
        logger.info("Configured Discord notifier")
    
    def configure_teams(self, webhook_url: str):
        """Configure Microsoft Teams notifier"""
        self.notifiers[NotificationChannel.TEAMS] = TeamsNotifier(webhook_url)
        logger.info("Configured Teams notifier")
    
    async def send_notification(
        self,
        event: NotificationEvent,
        recipients: Optional[Dict[NotificationChannel, List[str]]] = None
    ) -> Dict[NotificationChannel, bool]:
        """Send notification based on rules"""
        results = {}
        
        # Check for deduplication
        if self._should_deduplicate(event):
            logger.info(f"Notification deduplicated for event {event.id}")
            return results
        
        # Find matching rules
        matching_rules = self._find_matching_rules(event)
        
        # Send notifications for each matching rule
        for rule in matching_rules:
            if not rule.enabled:
                continue
            
            # Check rate limit
            if rule.name in self.rate_limiters:
                rate_limiter = self.rate_limiters[rule.name]
                if not rate_limiter.can_send():
                    logger.warning(f"Rate limit exceeded for rule {rule.name}")
                    continue
                rate_limiter.record_notification()
            
            # Get template
            template = None
            if rule.template_name and rule.template_name in self.templates:
                template = self.templates[rule.template_name]
            
            # Send to each channel
            for channel in rule.channels:
                if channel not in self.notifiers:
                    logger.warning(f"Notifier not configured for channel {channel.value}")
                    continue
                
                notifier = self.notifiers[channel]
                
                try:
                    if channel == NotificationChannel.SLACK:
                        success = await notifier.send_notification(event, template)
                    elif channel == NotificationChannel.DISCORD:
                        print(f"[DEBUG] Sending Discord notification via notifier")
                        success = await notifier.send_notification(event, template)
                    elif channel == NotificationChannel.TEAMS:
                        success = await notifier.send_notification(event, template)
                    elif channel == NotificationChannel.EMAIL:
                        # Get email recipients
                        emails = recipients.get(channel, []) if recipients else []
                        if not emails:
                            logger.warning(f"No email recipients specified for event {event.id}")
                            continue
                        success = await notifier.send_notification(event, emails, template)
                    elif channel == NotificationChannel.WEBHOOK:
                        success = await notifier.send_notification(event, template)
                    else:
                        logger.warning(f"Unsupported notification channel: {channel.value}")
                        continue
                    
                    results[channel] = success
                    
                except Exception as e:
                    logger.error(f"Error sending notification via {channel.value}: {e}")
                    results[channel] = False
        
        # Add to history
        self.notification_history.append(event)
        
        # Keep only recent history
        if len(self.notification_history) > 1000:
            self.notification_history = self.notification_history[-1000:]
        
        return results
    
    def _should_deduplicate(self, event: NotificationEvent) -> bool:
        """Check if event should be deduplicated"""
        # Create deduplication key
        dedup_key = f"{event.event_type}:{event.resource_id}:{event.priority.value}"
        
        now = datetime.now(timezone.utc)
        
        # Clean old entries
        cutoff = now - self.deduplication_window
        self.deduplication_cache = {
            key: timestamp for key, timestamp in self.deduplication_cache.items()
            if timestamp > cutoff
        }
        
        # Check if we've seen this event recently
        if dedup_key in self.deduplication_cache:
            return True
        
        # Record this event
        self.deduplication_cache[dedup_key] = now
        return False
    
    def _find_matching_rules(self, event: NotificationEvent) -> List[NotificationRule]:
        """Find rules that match an event"""
        matching_rules = []
        
        for rule in self.rules:
            if self._rule_matches_event(rule, event):
                matching_rules.append(rule)
        
        return matching_rules
    
    def _rule_matches_event(self, rule: NotificationRule, event: NotificationEvent) -> bool:
        """Check if a rule matches an event"""
        # Check event type
        if event.event_type not in rule.event_types:
            return False
        
        # Check priority threshold
        priority_levels = {
            NotificationPriority.LOW: 0,
            NotificationPriority.MEDIUM: 1,
            NotificationPriority.HIGH: 2,
            NotificationPriority.CRITICAL: 3,
        }
        
        if priority_levels[event.priority] < priority_levels[rule.priority_threshold]:
            return False
        
        # Check filters
        for filter_key, filter_value in rule.filters.items():
            if filter_key == "project" and event.project != filter_value:
                return False
            elif filter_key == "environment" and event.environment != filter_value:
                return False
            elif filter_key == "resource_type" and event.resource_type != filter_value:
                return False
            elif filter_key == "tags" and not set(filter_value).issubset(set(event.tags or [])):
                return False
        
        return True
    
    def get_notification_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get notification history"""
        recent_history = self.notification_history[-limit:] if limit > 0 else self.notification_history
        
        return [asdict(event) for event in recent_history]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get notification statistics"""
        now = datetime.now(timezone.utc)
        last_24h = now - timedelta(hours=24)
        
        recent_notifications = [
            event for event in self.notification_history
            if event.timestamp > last_24h
        ]
        
        by_priority = {}
        by_channel = {}
        
        for event in recent_notifications:
            priority = event.priority.value
            by_priority[priority] = by_priority.get(priority, 0) + 1
        
        return {
            "total_notifications": len(self.notification_history),
            "notifications_24h": len(recent_notifications),
            "by_priority_24h": by_priority,
            "active_rules": len([r for r in self.rules if r.enabled]),
            "total_rules": len(self.rules),
            "configured_channels": list(self.notifiers.keys()),
            "templates": list(self.templates.keys()),
        }