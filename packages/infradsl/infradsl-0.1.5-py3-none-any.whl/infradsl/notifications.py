"""
InfraDSL Notifications - Easy-to-use notification setup

Rails-like one-liner notification configuration for InfraDSL resources.
Simply import and configure your webhooks!

Usage:
    from infradsl.notifications import notify_discord, notify_slack, notify_all
    
    # Discord only
    notify_discord("https://discord.com/api/webhooks/YOUR/WEBHOOK")
    
    # Multiple platforms
    notify_all(
        discord="https://discord.com/api/webhooks/YOUR/WEBHOOK",
        slack="https://hooks.slack.com/services/YOUR/WEBHOOK"
    )
"""

from .core.hooks import configure_notifications, hooks


def notify_discord(webhook_url: str):
    """
    Configure Discord notifications for all resource lifecycle events.
    
    Args:
        webhook_url: Discord webhook URL
        
    Example:
        notify_discord("https://discord.com/api/webhooks/123/abc")
    """
    configure_notifications(discord_webhook=webhook_url)
    print(f"✅ Discord notifications configured!")
    print(f"   Webhook: {webhook_url[:50]}...")
    print(f"   Events: create, update, destroy, drift, errors")


def notify_slack(webhook_url: str, channel: str = None):
    """
    Configure Slack notifications for all resource lifecycle events.
    
    Args:
        webhook_url: Slack webhook URL
        channel: Default channel (optional)
        
    Example:
        notify_slack("https://hooks.slack.com/services/T00/B00/XXX", "#infrastructure")
    """
    # Note: We'll need to update the configure_notifications to support channel
    configure_notifications(slack_webhook=webhook_url)
    print(f"✅ Slack notifications configured!")
    print(f"   Webhook: {webhook_url[:50]}...")
    if channel:
        print(f"   Channel: {channel}")
    print(f"   Events: create, update, destroy, drift, errors")


def notify_teams(webhook_url: str):
    """
    Configure Microsoft Teams notifications for all resource lifecycle events.
    
    Args:
        webhook_url: Teams webhook URL
        
    Example:
        notify_teams("https://outlook.office.com/webhook/YOUR/TEAMS/WEBHOOK")
    """
    configure_notifications(teams_webhook=webhook_url)
    print(f"✅ Teams notifications configured!")
    print(f"   Webhook: {webhook_url[:50]}...")
    print(f"   Events: create, update, destroy, drift, errors")


def notify_webhook(webhook_url: str, headers: dict = None):
    """
    Configure generic webhook notifications for all resource lifecycle events.
    
    Args:
        webhook_url: Generic webhook URL
        headers: Optional custom headers
        
    Example:
        notify_webhook("https://your-api.com/hooks", {"Authorization": "Bearer token"})
    """
    configure_notifications(webhook_url=webhook_url)
    print(f"✅ Generic webhook notifications configured!")
    print(f"   Webhook: {webhook_url[:50]}...")
    if headers:
        print(f"   Headers: {list(headers.keys())}")
    print(f"   Events: create, update, destroy, drift, errors")


def notify_all(discord: str = None, slack: str = None, teams: str = None, webhook: str = None):
    """
    Configure multiple notification channels at once.
    
    Args:
        discord: Discord webhook URL
        slack: Slack webhook URL  
        teams: Teams webhook URL
        webhook: Generic webhook URL
        
    Example:
        notify_all(
            discord="https://discord.com/api/webhooks/123/abc",
            slack="https://hooks.slack.com/services/T00/B00/XXX"
        )
    """
    configure_notifications(
        discord_webhook=discord,
        slack_webhook=slack,
        teams_webhook=teams,
        webhook_url=webhook
    )
    
    channels = []
    if discord:
        channels.append("Discord")
    if slack:
        channels.append("Slack") 
    if teams:
        channels.append("Teams")
    if webhook:
        channels.append("Webhook")
    
    print(f"✅ Multi-channel notifications configured!")
    print(f"   Channels: {', '.join(channels)}")
    print(f"   Events: create, update, destroy, drift, errors")


# Convenience aliases for shorter imports
discord = notify_discord
slack = notify_slack  
teams = notify_teams
webhook = notify_webhook
all_channels = notify_all


# Auto-register default lifecycle hooks when imported
@hooks.after_create
async def _default_create_notification(context):
    """Default creation notification"""
    pass  # Notification is handled automatically by the hooks system

@hooks.after_update  
async def _default_update_notification(context):
    """Default update notification"""
    pass  # Notification is handled automatically by the hooks system

@hooks.after_destroy
async def _default_destroy_notification(context):
    """Default destroy notification"""
    pass  # Notification is handled automatically by the hooks system

@hooks.on_drift
async def _default_drift_notification(context):
    """Default drift notification"""
    pass  # Notification is handled automatically by the hooks system

@hooks.on_error
async def _default_error_notification(context):
    """Default error notification"""
    pass  # Notification is handled automatically by the hooks system


# Export the main notification functions
__all__ = [
    "notify_discord",
    "notify_slack", 
    "notify_teams",
    "notify_webhook",
    "notify_all",
    "discord",
    "slack",
    "teams", 
    "webhook",
    "all_channels"
]