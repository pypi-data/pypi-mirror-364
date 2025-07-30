#!/usr/bin/env python3
"""
InfraDSL Monitoring and Notifications Demo

This demo shows how to set up comprehensive monitoring with notifications
for Slack, email, and webhooks.
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, List

from infradsl.core.monitoring import (
    setup_monitoring_with_notifications,
    MonitoringPolicy,
    NotificationRule,
    NotificationChannel,
    NotificationPriority,
    NotificationTemplate,
    get_config_manager,
    MonitoringConfig,
    SlackConfig,
    EmailConfig,
    WebhookConfig,
)


async def demo_basic_setup():
    """Demo basic monitoring setup with notifications"""
    print("🚀 Setting up basic monitoring with notifications...")
    
    # Setup monitoring with Slack notifications
    integration = await setup_monitoring_with_notifications(
        slack_webhook="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
        monitoring_policies=[
            MonitoringPolicy(
                name="production_critical",
                resource_filter={"environment": "production", "labels": {"tier": "critical"}},
                check_interval=60,  # 1 minute
                priority="high",
                auto_remediate=True,
                notification_channels=["slack"]
            ),
            MonitoringPolicy(
                name="development_resources",
                resource_filter={"environment": "development"},
                check_interval=900,  # 15 minutes
                priority="low",
                auto_remediate=False,
                notification_channels=["slack"]
            )
        ]
    )
    
    print(f"✅ Monitoring integration started: {integration.get_status()}")
    
    # Let it run for a bit (in real usage, this would run continuously)
    await asyncio.sleep(5)
    
    await integration.stop()
    print("✅ Basic setup demo completed")


async def demo_advanced_setup():
    """Demo advanced monitoring setup with multiple notification channels"""
    print("\n🔧 Setting up advanced monitoring with multiple channels...")
    
    # Create advanced configuration
    integration = await setup_monitoring_with_notifications(
        slack_webhook="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
        email_config={
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "your-email@gmail.com",
            "password": "your-app-password",
            "from_email": "infradsl@yourcompany.com"
        },
        webhook_url="https://your-webhook-endpoint.com/infradsl",
        monitoring_policies=[
            MonitoringPolicy(
                name="security_critical",
                resource_filter={
                    "labels": {"security": "critical"}
                },
                check_interval=30,  # 30 seconds
                priority="critical",
                auto_remediate=True,
                notification_channels=["slack", "email", "webhook"]
            ),
            MonitoringPolicy(
                name="cost_optimization",
                resource_filter={
                    "labels": {"cost-optimize": "true"}
                },
                check_interval=3600,  # 1 hour
                priority="medium",
                auto_remediate=False,
                notification_channels=["slack"]
            )
        ]
    )
    
    # Add custom notification rules
    custom_rules = [
        NotificationRule(
            name="escalation_rule",
            channels=[NotificationChannel.SLACK, NotificationChannel.EMAIL],
            event_types=["drift_detected"],
            priority_threshold=NotificationPriority.HIGH,
            filters={"environment": "production"},
            rate_limit=5  # Max 5 notifications per hour
        ),
        NotificationRule(
            name="summary_rule",
            channels=[NotificationChannel.WEBHOOK],
            event_types=["drift_check_summary"],
            priority_threshold=NotificationPriority.MEDIUM,
            filters={},
            rate_limit=2  # Max 2 summaries per hour
        )
    ]
    
    for rule in custom_rules:
        integration.notification_manager.add_rule(rule)
    
    print(f"✅ Advanced monitoring setup completed: {integration.get_status()}")
    
    await asyncio.sleep(3)
    await integration.stop()
    print("✅ Advanced setup demo completed")


async def demo_custom_templates():
    """Demo custom notification templates"""
    print("\n🎨 Setting up custom notification templates...")
    
    integration = await setup_monitoring_with_notifications(
        slack_webhook="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    )
    
    # Create custom Slack template
    custom_slack_template = NotificationTemplate(
        name="custom_slack_template",
        content={
            "subject": "Custom Infrastructure Alert",
            "body": """🔴 *DRIFT ALERT* 🔴
            
📦 *Resource:* {{ resource_name }}
🏷️ *Type:* {{ resource_type }}
⚠️ *Priority:* {{ priority|upper }}
🕒 *Time:* {{ timestamp }}
🌍 *Environment:* {{ event.environment or 'Unknown' }}
📍 *Project:* {{ event.project or 'Unknown' }}

💬 *Message:*
{{ message }}

{% if event.details %}
📊 *Details:*
```
{{ event.details|tojson(indent=2) }}
```
{% endif %}

🔗 *Resource ID:* `{{ resource_id }}`
""",
        },
    )
    
    # Create custom email template
    custom_email_template = NotificationTemplate(
        name="custom_email_template",
        content={
            "subject": "🚨 Infrastructure Drift Alert - {{ resource_name }}",
            "body": """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .alert { background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; margin: 10px 0; border-radius: 4px; }
        .info { background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; margin: 10px 0; border-radius: 4px; }
        .details { background-color: #f8f9fa; padding: 10px; border-radius: 4px; font-family: monospace; }
    </style>
</head>
<body>
    <div class="alert">
        <h2>🚨 Infrastructure Drift Detected</h2>
        <p><strong>Resource:</strong> {{ resource_name }} ({{ resource_type }})</p>
        <p><strong>Priority:</strong> {{ priority|upper }}</p>
        <p><strong>Environment:</strong> {{ event.environment or 'Unknown' }}</p>
        <p><strong>Project:</strong> {{ event.project or 'Unknown' }}</p>
        <p><strong>Timestamp:</strong> {{ timestamp }}</p>
    </div>
    
    <div class="info">
        <h3>Message</h3>
        <p>{{ message }}</p>
    </div>
    
    {% if event.details %}
    <div class="details">
        <h3>Technical Details</h3>
        <pre>{{ event.details|tojson(indent=2) }}</pre>
    </div>
    {% endif %}
    
    <p><small>This alert was generated by InfraDSL Infrastructure Monitoring at {{ timestamp }}</small></p>
</body>
</html>""",
        },
    )
    
    # Add custom templates
    integration.notification_manager.add_template(custom_slack_template)
    integration.notification_manager.add_template(custom_email_template)
    
    # Create rules that use custom templates
    custom_rule = NotificationRule(
        name="custom_template_rule",
        channels=[NotificationChannel.SLACK],
        event_types=["drift_detected"],
        priority_threshold=NotificationPriority.MEDIUM,
        filters={},
        template_name="custom_slack_template",
        rate_limit=10
    )
    
    integration.notification_manager.add_rule(custom_rule)
    
    print("✅ Custom templates configured")
    print(f"📊 Templates available: {list(integration.notification_manager.templates.keys())}")
    
    await asyncio.sleep(2)
    await integration.stop()
    print("✅ Custom templates demo completed")


def demo_configuration_file():
    """Demo configuration file management"""
    print("\n⚙️ Demonstrating configuration file management...")
    
    # Get configuration manager
    config_manager = get_config_manager()
    
    # Create sample configuration
    sample_config = config_manager.create_sample_config()
    print(f"📄 Sample configuration created")
    
    # Save configuration
    config_manager.save_config(sample_config)
    print(f"💾 Configuration saved to: {config_manager.config_file}")
    
    # Load configuration
    loaded_config = config_manager.load_config()
    print(f"📥 Configuration loaded successfully")
    
    # Display configuration summary
    print("\n📋 Configuration Summary:")
    print(f"  Default interval: {loaded_config.default_interval}s")
    print(f"  Max concurrent checks: {loaded_config.max_concurrent_checks}")
    print(f"  Slack configured: {loaded_config.slack is not None}")
    print(f"  Email configured: {loaded_config.email is not None}")
    print(f"  Webhook configured: {loaded_config.webhook is not None}")
    print(f"  Monitoring policies: {len(loaded_config.policies)}")
    print(f"  Notification rules: {len(loaded_config.notification_rules)}")
    
    print("✅ Configuration demo completed")


async def demo_monitoring_simulation():
    """Demo monitoring simulation with fake drift events"""
    print("\n🎭 Simulating drift events for testing...")
    
    integration = await setup_monitoring_with_notifications(
        slack_webhook="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    )
    
    # Simulate some drift events
    from infradsl.core.monitoring.notifications import NotificationEvent
    
    # Create test events
    test_events = [
        NotificationEvent(
            id="test-1",
            event_type="drift_detected",
            resource_id="vm-12345",
            resource_name="web-server-prod",
            resource_type="VirtualMachine",
            message="Security group configuration has drifted",
            details={
                "security_groups": {
                    "expected": ["sg-prod-web"],
                    "actual": ["sg-prod-web", "sg-default"]
                }
            },
            timestamp=datetime.now(timezone.utc),
            priority=NotificationPriority.HIGH,
            project="my-project",
            environment="production",
            tags=["security", "critical"]
        ),
        NotificationEvent(
            id="test-2",
            event_type="drift_detected",
            resource_id="db-67890",
            resource_name="database-prod",
            resource_type="Database",
            message="Instance type has been changed",
            details={
                "instance_type": {
                    "expected": "db.t3.medium",
                    "actual": "db.t3.small"
                }
            },
            timestamp=datetime.now(timezone.utc),
            priority=NotificationPriority.MEDIUM,
            project="my-project",
            environment="production",
            tags=["performance"]
        )
    ]
    
    # Send test notifications
    for event in test_events:
        print(f"📤 Sending test notification: {event.message}")
        results = await integration.notification_manager.send_notification(event)
        print(f"   Results: {results}")
    
    # Display statistics
    stats = integration.notification_manager.get_statistics()
    print(f"\n📊 Notification Statistics:")
    print(f"  Total notifications: {stats['total_notifications']}")
    print(f"  Notifications (24h): {stats['notifications_24h']}")
    print(f"  Active rules: {stats['active_rules']}")
    print(f"  Configured channels: {stats['configured_channels']}")
    
    await integration.stop()
    print("✅ Simulation demo completed")


async def main():
    """Main demo function"""
    print("🎯 InfraDSL Monitoring and Notifications Demo")
    print("=" * 50)
    
    # Run demos
    await demo_basic_setup()
    await demo_advanced_setup()
    await demo_custom_templates()
    demo_configuration_file()
    await demo_monitoring_simulation()
    
    print("\n🎉 All demos completed successfully!")
    print("\nNext Steps:")
    print("1. Configure your actual Slack webhook URL")
    print("2. Set up email SMTP configuration")
    print("3. Configure webhook endpoint")
    print("4. Customize monitoring policies for your infrastructure")
    print("5. Run 'infra monitor start' to begin monitoring")


if __name__ == "__main__":
    asyncio.run(main())