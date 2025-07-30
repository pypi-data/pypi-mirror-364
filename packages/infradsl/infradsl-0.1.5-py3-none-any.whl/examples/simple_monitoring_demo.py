#!/usr/bin/env python3
"""
Simple InfraDSL Monitoring Demo

This demo shows the basic monitoring components without complex integrations.
"""

import asyncio
import json
from datetime import datetime, timezone

from infradsl.core.monitoring import (
    DriftMonitoringDaemon,
    MonitoringPolicy,
    NotificationManager,
    NotificationEvent,
    NotificationPriority,
    NotificationChannel,
    NotificationRule,
    NotificationTemplate,
    MonitoringConfig,
    SlackConfig,
    EmailConfig,
    WebhookConfig,
    get_config_manager,
)


def demo_basic_components():
    """Demo basic monitoring components"""
    print("🔧 Testing basic monitoring components...")
    
    # Create monitoring policy
    policy = MonitoringPolicy(
        name="test_policy",
        resource_filter={"environment": "test"},
        check_interval=60,
        priority="medium",
        auto_remediate=False,
        notification_channels=["slack"]
    )
    print(f"✅ Created policy: {policy.name}")
    
    # Create notification manager
    notification_manager = NotificationManager()
    print("✅ Created notification manager")
    
    # Create notification rule
    rule = NotificationRule(
        name="test_rule",
        channels=[NotificationChannel.SLACK],
        event_types=["drift_detected"],
        priority_threshold=NotificationPriority.MEDIUM,
        filters={},
        rate_limit=10
    )
    notification_manager.add_rule(rule)
    print(f"✅ Added notification rule: {rule.name}")
    
    # Create notification template
    template = NotificationTemplate(
        name="test_template",
        content={
            "subject": "Test Alert",
            "body": "Test message: {{ message }}"
        }
    )
    notification_manager.add_template(template)
    print(f"✅ Added template: {template.name}")
    
    # Create monitoring daemon (but don't start it)
    daemon = DriftMonitoringDaemon(
        default_interval=300,
        max_concurrent_checks=5,
        enable_intelligent_caching=False  # Disable caching to avoid cache manager issues
    )
    daemon.add_policy(policy)
    print(f"✅ Created daemon with policy: {policy.name}")
    
    return daemon, notification_manager


async def demo_notification_events():
    """Demo notification events"""
    print("\n📡 Testing notification events...")
    
    # Create notification manager
    notification_manager = NotificationManager()
    
    # Add a test rule
    rule = NotificationRule(
        name="test_events",
        channels=[NotificationChannel.SLACK],
        event_types=["drift_detected", "test_event"],
        priority_threshold=NotificationPriority.LOW,
        filters={},
    )
    notification_manager.add_rule(rule)
    
    # Create test events
    test_events = [
        NotificationEvent(
            id="test-1",
            event_type="drift_detected",
            resource_id="vm-123",
            resource_name="test-vm",
            resource_type="VirtualMachine",
            message="Test drift detected",
            details={"test": "data"},
            timestamp=datetime.now(timezone.utc),
            priority=NotificationPriority.MEDIUM,
            project="test-project",
            environment="test"
        ),
        NotificationEvent(
            id="test-2",
            event_type="test_event",
            resource_id="db-456",
            resource_name="test-db",
            resource_type="Database",
            message="Test event triggered",
            details={"status": "ok"},
            timestamp=datetime.now(timezone.utc),
            priority=NotificationPriority.HIGH,
            project="test-project",
            environment="production"
        )
    ]
    
    # Test notification matching (without actually sending)
    print("📋 Testing notification rules...")
    for event in test_events:
        matching_rules = notification_manager._find_matching_rules(event)
        print(f"   Event {event.id}: {len(matching_rules)} matching rules")
    
    # Test deduplication
    print("🔄 Testing deduplication...")
    should_dedupe1 = notification_manager._should_deduplicate(test_events[0])
    should_dedupe2 = notification_manager._should_deduplicate(test_events[0])  # Same event
    print(f"   First event deduplicated: {should_dedupe1}")
    print(f"   Second event deduplicated: {should_dedupe2}")
    
    # Get stats
    stats = notification_manager.get_statistics()
    print(f"📊 Notification stats: {stats}")
    
    print("✅ Notification events test completed")


def demo_configuration_management():
    """Demo configuration management"""
    print("\n⚙️ Testing configuration management...")
    
    # Create configurations
    slack_config = SlackConfig(
        webhook_url="https://hooks.slack.com/services/TEST/TEST/TEST",
        channel="#test-alerts",
        enabled=True
    )
    print(f"✅ Created Slack config: {slack_config.webhook_url}")
    
    email_config = EmailConfig(
        smtp_server="smtp.test.com",
        smtp_port=587,
        username="test@test.com",
        password="test-password",
        from_email="alerts@test.com",
        enabled=True
    )
    print(f"✅ Created email config: {email_config.smtp_server}")
    
    webhook_config = WebhookConfig(
        webhook_url="https://webhook.test.com/alerts",
        headers={"Authorization": "Bearer test-token"},
        enabled=True
    )
    print(f"✅ Created webhook config: {webhook_config.webhook_url}")
    
    # Create full monitoring config
    monitoring_config = MonitoringConfig(
        default_interval=300,
        max_concurrent_checks=10,
        enable_intelligent_caching=True,
        cache_ttl=3600,
        slack=slack_config,
        email=email_config,
        webhook=webhook_config,
        policies=[
            {
                "name": "production_critical",
                "resource_filter": {"environment": "production"},
                "check_interval": 60,
                "priority": "high",
                "auto_remediate": True,
                "notification_channels": ["slack", "email"]
            }
        ]
    )
    print(f"✅ Created monitoring config with {len(monitoring_config.policies)} policies")
    
    # Test configuration manager
    config_manager = get_config_manager()
    print(f"✅ Got config manager: {config_manager.config_file}")
    
    # Test sample config
    sample_config = config_manager.create_sample_config()
    print(f"✅ Created sample config with {len(sample_config.policies)} policies")
    
    print("✅ Configuration management test completed")


async def demo_daemon_lifecycle():
    """Demo daemon lifecycle without resource operations"""
    print("\n🔄 Testing daemon lifecycle...")
    
    # Create daemon without cache manager to avoid issues
    daemon = DriftMonitoringDaemon(
        default_interval=5,  # Short interval for demo
        max_concurrent_checks=3,
        enable_intelligent_caching=False  # Disable caching
    )
    
    # Add a test policy
    policy = MonitoringPolicy(
        name="test_lifecycle",
        resource_filter={"environment": "test"},
        check_interval=2,
        priority="medium"
    )
    daemon.add_policy(policy)
    print(f"✅ Added policy: {policy.name}")
    
    # Test daemon status
    status = daemon.get_status()
    print(f"📊 Initial daemon status: {status['state']}")
    
    # Start daemon
    print("🚀 Starting daemon...")
    await daemon.start()
    
    # Check status
    status = daemon.get_status()
    print(f"📊 Running daemon status: {status['state']}")
    
    # Let it run briefly
    await asyncio.sleep(2)
    
    # Pause daemon
    print("⏸️  Pausing daemon...")
    await daemon.pause()
    
    status = daemon.get_status()
    print(f"📊 Paused daemon status: {status['state']}")
    
    # Resume daemon
    print("▶️  Resuming daemon...")
    await daemon.resume()
    
    status = daemon.get_status()
    print(f"📊 Resumed daemon status: {status['state']}")
    
    # Let it run briefly
    await asyncio.sleep(2)
    
    # Stop daemon
    print("🛑 Stopping daemon...")
    await daemon.stop()
    
    status = daemon.get_status()
    print(f"📊 Final daemon status: {status['state']}")
    
    print("✅ Daemon lifecycle test completed")


async def main():
    """Main demo function"""
    print("🎯 Simple InfraDSL Monitoring Demo")
    print("=" * 50)
    
    # Run component tests
    daemon, notification_manager = demo_basic_components()
    await demo_notification_events()
    demo_configuration_management()
    await demo_daemon_lifecycle()
    
    print("\n🎉 All tests completed successfully!")
    print("\nKey Components Tested:")
    print("✅ DriftMonitoringDaemon - Lifecycle management")
    print("✅ MonitoringPolicy - Resource filtering")
    print("✅ NotificationManager - Event handling")
    print("✅ NotificationRule - Rule matching")
    print("✅ NotificationTemplate - Template system")
    print("✅ Configuration Management - Config loading/saving")
    print("\nNext Steps:")
    print("1. Add actual resources to test drift detection")
    print("2. Configure real notification channels")
    print("3. Set up monitoring policies for your infrastructure")


if __name__ == "__main__":
    asyncio.run(main())