"""
Rails-like Lifecycle Hooks for InfraDSL Resources

This module provides Rails-style lifecycle hooks (before_create, after_create, etc.)
that can automatically trigger notifications and other actions.
"""

import asyncio
import uuid
import os
import json
import tempfile
from datetime import datetime, timezone
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from enum import Enum

from ..monitoring.notifications import (
    NotificationManager, 
    NotificationEvent, 
    NotificationPriority,
    DiscordNotifier
)


class LifecycleEvent(Enum):
    """Resource lifecycle events"""
    BEFORE_CREATE = "before_create"
    AFTER_CREATE = "after_create" 
    BEFORE_UPDATE = "before_update"
    AFTER_UPDATE = "after_update"
    BEFORE_DESTROY = "before_destroy"
    AFTER_DESTROY = "after_destroy"
    ON_DRIFT = "on_drift"
    ON_ERROR = "on_error"


@dataclass
class HookContext:
    """Context passed to lifecycle hooks"""
    resource: Any
    event: LifecycleEvent
    metadata: Dict[str, Any]
    changes: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None
    
    @property
    def resource_name(self) -> str:
        """Get resource name"""
        return getattr(self.resource, 'name', str(self.resource))
    
    @property
    def resource_type(self) -> str:
        """Get resource type"""
        return self.resource.__class__.__name__
    
    @property
    def resource_id(self) -> str:
        """Get resource ID"""
        if hasattr(self.resource, 'metadata') and hasattr(self.resource.metadata, 'id'):
            return self.resource.metadata.id
        return f"{self.resource_type.lower()}-{self.resource_name}"


class LifecycleHooks:
    """Rails-like lifecycle hooks system"""
    
    def __init__(self):
        self.hooks: Dict[LifecycleEvent, List[Callable]] = {
            event: [] for event in LifecycleEvent
        }
        self.notification_manager: Optional[NotificationManager] = None
        self._config_file = None
    
    def before_create(self, func: Callable):
        """Register before_create hook"""
        self.hooks[LifecycleEvent.BEFORE_CREATE].append(func)
        return func
    
    def after_create(self, func: Callable):
        """Register after_create hook"""
        self.hooks[LifecycleEvent.AFTER_CREATE].append(func)
        return func
    
    def before_update(self, func: Callable):
        """Register before_update hook"""
        self.hooks[LifecycleEvent.BEFORE_UPDATE].append(func)
        return func
    
    def after_update(self, func: Callable):
        """Register after_update hook"""
        self.hooks[LifecycleEvent.AFTER_UPDATE].append(func)
        return func
    
    def before_destroy(self, func: Callable):
        """Register before_destroy hook"""
        self.hooks[LifecycleEvent.BEFORE_DESTROY].append(func)
        return func
    
    def after_destroy(self, func: Callable):
        """Register after_destroy hook"""
        self.hooks[LifecycleEvent.AFTER_DESTROY].append(func)
        return func
    
    def on_drift(self, func: Callable):
        """Register drift detection hook"""
        self.hooks[LifecycleEvent.ON_DRIFT].append(func)
        return func
    
    def on_error(self, func: Callable):
        """Register error handler hook"""
        self.hooks[LifecycleEvent.ON_ERROR].append(func)
        return func
    
    def setup_notifications(self, discord_webhook: str = None, slack_webhook: str = None, 
                          teams_webhook: str = None, webhook_url: str = None):
        """Setup notification manager with webhooks"""
        self.notification_manager = NotificationManager()
        
        if discord_webhook:
            self.notification_manager.configure_discord(discord_webhook)
            # Add default rule for all lifecycle events
            from ..monitoring.notifications import NotificationRule, NotificationChannel, NotificationPriority
            rule = NotificationRule(
                name="discord_lifecycle_events",
                event_types=["after_create", "after_update", "after_destroy", "on_drift", "on_error"],
                channels=[NotificationChannel.DISCORD],
                priority_threshold=NotificationPriority.LOW,  # Send all priority levels
                filters={},  # No filters, send all events
                enabled=True
            )
            self.notification_manager.add_rule(rule)
            print(f"[DEBUG] Added Discord notification rule for lifecycle events")
            
        if slack_webhook:
            self.notification_manager.configure_slack(slack_webhook)
            # Add default rule for all lifecycle events  
            from ..monitoring.notifications import NotificationRule, NotificationChannel, NotificationPriority
            rule = NotificationRule(
                name="slack_lifecycle_events",
                event_types=["after_create", "after_update", "after_destroy", "on_drift", "on_error"],
                channels=[NotificationChannel.SLACK],
                priority_threshold=NotificationPriority.LOW,
                filters={},
                enabled=True
            )
            self.notification_manager.add_rule(rule)
            
        if teams_webhook:
            self.notification_manager.configure_teams(teams_webhook)
            # Add default rule for all lifecycle events
            from ..monitoring.notifications import NotificationRule, NotificationChannel, NotificationPriority
            rule = NotificationRule(
                name="teams_lifecycle_events", 
                event_types=["after_create", "after_update", "after_destroy", "on_drift", "on_error"],
                channels=[NotificationChannel.TEAMS],
                priority_threshold=NotificationPriority.LOW,
                filters={},
                enabled=True
            )
            self.notification_manager.add_rule(rule)
            
        if webhook_url:
            self.notification_manager.configure_webhook(webhook_url)
        
        # Persist configuration for apply process
        self._save_notification_config({
            'discord_webhook': discord_webhook,
            'slack_webhook': slack_webhook,
            'teams_webhook': teams_webhook,
            'webhook_url': webhook_url
        })
    
    async def trigger(self, event: LifecycleEvent, resource: Any, **kwargs):
        """Trigger lifecycle hooks for an event"""
        context = HookContext(
            resource=resource,
            event=event,
            metadata=kwargs.get('metadata', {}),
            changes=kwargs.get('changes'),
            error=kwargs.get('error')
        )
        
        # Run registered hooks
        for hook in self.hooks[event]:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook(context)
                else:
                    hook(context)
            except Exception as e:
                print(f"Error in hook {hook.__name__}: {e}")
        
        # Send notifications if configured (try to load from saved config if not available)
        if not self.notification_manager:
            print(f"[DEBUG] No notification manager, trying to load config...")
            self._load_notification_config()
        
        if self.notification_manager:
            print(f"[DEBUG] Notification manager found, sending notification...")
            await self._send_notification(context)
        else:
            print(f"[DEBUG] No notification manager available after config load")
    
    async def _send_notification(self, context: HookContext):
        """Send notification for lifecycle event"""
        print(f"[DEBUG] _send_notification called for event: {context.event.value}")
        
        # Skip notifications for before events to avoid spam
        if context.event.value.startswith('before_'):
            print(f"[DEBUG] Skipping notification for before_ event: {context.event.value}")
            return
        
        priority = self._get_priority_for_event(context.event)
        message = self._format_message(context)
        
        notification_event = NotificationEvent(
            id=str(uuid.uuid4()),
            event_type=context.event.value,
            resource_id=context.resource_id,
            resource_name=context.resource_name,
            resource_type=context.resource_type,
            message=message,
            details=self._get_notification_details(context),
            timestamp=datetime.now(timezone.utc),
            priority=priority,
            project=getattr(context.resource.metadata, 'project', None),
            environment=getattr(context.resource.metadata, 'environment', 'unknown'),
            tags=getattr(context.resource, 'tags', [])
        )
        
        try:
            print(f"[DEBUG] Attempting to send notification: {message}")
            await self.notification_manager.send_notification(notification_event)
            print(f"[DEBUG] Notification sent successfully!")
        except Exception as e:
            print(f"[DEBUG] Failed to send notification: {e}")
            import traceback
            print(f"[DEBUG] Full traceback:")
            traceback.print_exc()
    
    def _get_priority_for_event(self, event: LifecycleEvent) -> NotificationPriority:
        """Get notification priority based on event type"""
        priority_map = {
            LifecycleEvent.AFTER_CREATE: NotificationPriority.MEDIUM,
            LifecycleEvent.AFTER_UPDATE: NotificationPriority.MEDIUM,
            LifecycleEvent.AFTER_DESTROY: NotificationPriority.HIGH,
            LifecycleEvent.ON_DRIFT: NotificationPriority.HIGH,
            LifecycleEvent.ON_ERROR: NotificationPriority.CRITICAL,
        }
        return priority_map.get(event, NotificationPriority.LOW)
    
    def _format_message(self, context: HookContext) -> str:
        """Format notification message"""
        action_map = {
            LifecycleEvent.AFTER_CREATE: "created",
            LifecycleEvent.AFTER_UPDATE: "updated", 
            LifecycleEvent.AFTER_DESTROY: "destroyed",
            LifecycleEvent.ON_DRIFT: "drift detected",
            LifecycleEvent.ON_ERROR: "error occurred",
        }
        
        action = action_map.get(context.event, context.event.value)
        
        if context.error:
            return f"Error during {action} of {context.resource_type} '{context.resource_name}': {context.error}"
        else:
            return f"{context.resource_type} '{context.resource_name}' {action} successfully"
    
    def _get_notification_details(self, context: HookContext) -> Dict[str, Any]:
        """Get detailed information for notification"""
        details = {
            "event_type": context.event.value,
            "resource_type": context.resource_type,
            "resource_name": context.resource_name,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if context.changes:
            details["changes"] = context.changes
        
        if context.error:
            details["error"] = str(context.error)
            details["error_type"] = context.error.__class__.__name__
        
        # Add resource-specific details
        if hasattr(context.resource, 'spec'):
            resource_config = {
                "size": getattr(context.resource.spec, 'instance_size', None),
                "image": f"{getattr(context.resource.spec, 'image_type', None)} {getattr(context.resource.spec, 'image_version', '')}"
            }
            
            # Safely get zone from provider config if it exists
            if hasattr(context.resource.spec, 'provider_config') and context.resource.spec.provider_config:
                resource_config["zone"] = context.resource.spec.provider_config.get('zone')
            elif hasattr(context.resource, 'metadata') and hasattr(context.resource.metadata, 'annotations'):
                # Fallback: get zone from metadata annotations
                resource_config["zone"] = context.resource.metadata.annotations.get('zone')
            
            details["resource_config"] = resource_config
        
        return details
    
    def _save_notification_config(self, config: Dict[str, Any]):
        """Save notification configuration to temporary file"""
        try:
            # Use a consistent temporary file path
            temp_dir = tempfile.gettempdir()
            self._config_file = os.path.join(temp_dir, 'infradsl_notifications.json')
            
            # Filter out None values
            filtered_config = {k: v for k, v in config.items() if v is not None}
            
            if filtered_config:
                with open(self._config_file, 'w') as f:
                    json.dump(filtered_config, f)
                print(f"[DEBUG] Saved notification config to {self._config_file}")
            else:
                # Remove config file if no webhooks configured
                if os.path.exists(self._config_file):
                    os.remove(self._config_file)
        except Exception as e:
            print(f"[DEBUG] Failed to save notification config: {e}")
    
    def _load_notification_config(self):
        """Load notification configuration from temporary file"""
        try:
            temp_dir = tempfile.gettempdir()
            config_file = os.path.join(temp_dir, 'infradsl_notifications.json')
            
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                print(f"[DEBUG] Loading notification config from {config_file}")
                
                # Setup notification manager with loaded config
                self.notification_manager = NotificationManager()
                
                if config.get('discord_webhook'):
                    self.notification_manager.configure_discord(config['discord_webhook'])
                    # Add default rule for all lifecycle events
                    from ..monitoring.notifications import NotificationRule, NotificationChannel, NotificationPriority
                    rule = NotificationRule(
                        name="discord_lifecycle_events",
                        event_types=["after_create", "after_update", "after_destroy", "on_drift", "on_error"],
                        channels=[NotificationChannel.DISCORD],
                        priority_threshold=NotificationPriority.LOW,
                        filters={},
                        enabled=True
                    )
                    self.notification_manager.add_rule(rule)
                    print(f"[DEBUG] Configured Discord webhook and added notification rule")
                    
                if config.get('slack_webhook'):
                    self.notification_manager.configure_slack(config['slack_webhook'])
                    # Add default rule for all lifecycle events  
                    from ..monitoring.notifications import NotificationRule, NotificationChannel, NotificationPriority
                    rule = NotificationRule(
                        name="slack_lifecycle_events",
                        event_types=["after_create", "after_update", "after_destroy", "on_drift", "on_error"],
                        channels=[NotificationChannel.SLACK],
                        priority_threshold=NotificationPriority.LOW,
                        filters={},
                        enabled=True
                    )
                    self.notification_manager.add_rule(rule)
                    print(f"[DEBUG] Configured Slack webhook and added notification rule")
                    
                if config.get('teams_webhook'):
                    self.notification_manager.configure_teams(config['teams_webhook'])
                    # Add default rule for all lifecycle events
                    from ..monitoring.notifications import NotificationRule, NotificationChannel, NotificationPriority
                    rule = NotificationRule(
                        name="teams_lifecycle_events", 
                        event_types=["after_create", "after_update", "after_destroy", "on_drift", "on_error"],
                        channels=[NotificationChannel.TEAMS],
                        priority_threshold=NotificationPriority.LOW,
                        filters={},
                        enabled=True
                    )
                    self.notification_manager.add_rule(rule)
                    print(f"[DEBUG] Configured Teams webhook and added notification rule")
                    
                if config.get('webhook_url'):
                    self.notification_manager.configure_webhook(config['webhook_url'])
                    print(f"[DEBUG] Configured generic webhook")
            else:
                print(f"[DEBUG] No notification config file found at {config_file}")
        except Exception as e:
            print(f"[DEBUG] Failed to load notification config: {e}")


# Global hooks instance - Rails-like singleton
hooks = LifecycleHooks()


# Convenience decorators for easy usage
def before_create(func):
    """Decorator for before_create hooks"""
    return hooks.before_create(func)


def after_create(func):
    """Decorator for after_create hooks"""
    return hooks.after_create(func)


def before_update(func):
    """Decorator for before_update hooks"""
    return hooks.before_update(func)


def after_update(func):
    """Decorator for after_update hooks"""
    return hooks.after_update(func)


def before_destroy(func):
    """Decorator for before_destroy hooks"""
    return hooks.before_destroy(func)


def after_destroy(func):
    """Decorator for after_destroy hooks"""
    return hooks.after_destroy(func)


def on_drift(func):
    """Decorator for drift detection hooks"""
    return hooks.on_drift(func)


def on_error(func):
    """Decorator for error handling hooks"""
    return hooks.on_error(func)


def configure_notifications(discord_webhook: str = None, slack_webhook: str = None,
                          teams_webhook: str = None, webhook_url: str = None):
    """Configure notification webhooks - Rails-like configuration"""
    hooks.setup_notifications(
        discord_webhook=discord_webhook,
        slack_webhook=slack_webhook, 
        teams_webhook=teams_webhook,
        webhook_url=webhook_url
    )


async def trigger_lifecycle_event(event: LifecycleEvent, resource: Any, **kwargs):
    """Trigger a lifecycle event - used by InfraDSL core"""
    await hooks.trigger(event, resource, **kwargs)