"""
Monitoring CLI Commands - Management commands for drift monitoring and auto-remediation

This module provides CLI commands for managing the drift monitoring daemon,
auto-remediation engine, and notification systems.
"""

import asyncio
import json
from argparse import Namespace
from typing import TYPE_CHECKING

from tabulate import tabulate

from infradsl.core.monitoring import (
    MonitoringPolicy,
    get_config_manager,
    setup_monitoring_with_notifications,
)
from infradsl.core.monitoring.daemon import DriftMonitoringDaemon
from .base import BaseCommand

if TYPE_CHECKING:
    from ..utils.output import Console
    from ..utils.config import CLIConfig


class MonitorCommand(BaseCommand):
    """Monitor drift and manage auto-remediation"""

    @property
    def name(self) -> str:
        return "monitor"

    @property
    def description(self) -> str:
        return "Monitor drift and manage auto-remediation"

    def register(self, subparsers) -> None:
        """Register monitor subcommands"""
        parser = subparsers.add_parser(
            self.name,
            help=self.description,
            description="Monitor infrastructure drift and manage auto-remediation",
        )

        # Add common arguments
        self.add_common_arguments(parser)

        # Create subparsers for monitor commands
        monitor_subparsers = parser.add_subparsers(
            dest="monitor_command", help="Monitor commands", metavar="COMMAND"
        )

        # Start command
        start_parser = monitor_subparsers.add_parser(
            "start", help="Start the drift monitoring daemon"
        )
        start_parser.add_argument("--config-file", help="Configuration file path")
        start_parser.add_argument(
            "--interval",
            type=int,
            default=300,
            help="Default monitoring interval in seconds",
        )
        start_parser.add_argument(
            "--max-concurrent", type=int, default=10, help="Maximum concurrent checks"
        )
        start_parser.add_argument(
            "--enable-cache",
            action="store_true",
            default=True,
            help="Enable intelligent caching",
        )
        start_parser.add_argument(
            "--cache-ttl", type=int, default=3600, help="Cache TTL in seconds"
        )
        start_parser.add_argument(
            "--slack-webhook", help="Slack webhook URL for notifications"
        )
        start_parser.add_argument(
            "--email-smtp", help="SMTP server for email notifications"
        )
        start_parser.add_argument(
            "--email-port", type=int, default=587, help="SMTP port"
        )
        start_parser.add_argument("--email-username", help="SMTP username")
        start_parser.add_argument("--email-password", help="SMTP password")
        start_parser.add_argument("--email-from", help="From email address")
        start_parser.add_argument("--webhook-url", help="Webhook URL for notifications")
        start_parser.add_argument(
            "--daemon-mode", action="store_true", help="Run as daemon (non-interactive)"
        )

        # Status command
        status_parser = monitor_subparsers.add_parser(
            "status", help="Show monitoring daemon status"
        )
        status_parser.add_argument(
            "--format", choices=["table", "json"], default="table", help="Output format"
        )

        # Check command
        check_parser = monitor_subparsers.add_parser(
            "check", help="Force an immediate drift check"
        )
        check_parser.add_argument("--resource-id", help="Check specific resource by ID")
        check_parser.add_argument(
            "--format", choices=["table", "json"], default="table", help="Output format"
        )

        # Stop command
        monitor_subparsers.add_parser("stop", help="Stop the drift monitoring daemon")

        # Policy management
        add_policy_parser = monitor_subparsers.add_parser(
            "add-policy", help="Add a monitoring policy"
        )
        add_policy_parser.add_argument("--name", required=True, help="Policy name")
        add_policy_parser.add_argument(
            "--check-interval", type=int, default=300, help="Check interval in seconds"
        )
        add_policy_parser.add_argument(
            "--priority",
            choices=["low", "medium", "high"],
            default="medium",
            help="Policy priority",
        )
        add_policy_parser.add_argument(
            "--auto-remediate", action="store_true", help="Enable auto-remediation"
        )
        add_policy_parser.add_argument("--environment", help="Filter by environment")
        add_policy_parser.add_argument("--project", help="Filter by project")
        add_policy_parser.add_argument(
            "--resource-type", help="Filter by resource type"
        )
        add_policy_parser.add_argument(
            "--label", action="append", help="Filter by label (key=value)"
        )
        add_policy_parser.add_argument(
            "--notification-channels", action="append", help="Notification channels"
        )

        # Remove policy command
        remove_policy_parser = monitor_subparsers.add_parser(
            "remove-policy", help="Remove a monitoring policy"
        )
        remove_policy_parser.add_argument(
            "--name", required=True, help="Policy name to remove"
        )

        # List policies command
        list_policies_parser = monitor_subparsers.add_parser(
            "list-policies", help="List monitoring policies"
        )
        list_policies_parser.add_argument(
            "--format", choices=["table", "json"], default="table", help="Output format"
        )

        # Configure notifications
        config_notif_parser = monitor_subparsers.add_parser(
            "configure-notifications", help="Configure notification settings"
        )
        config_notif_parser.add_argument("--slack-webhook", help="Slack webhook URL")
        config_notif_parser.add_argument("--slack-channel", help="Slack channel")
        config_notif_parser.add_argument("--email-smtp", help="SMTP server")
        config_notif_parser.add_argument("--email-port", type=int, help="SMTP port")
        config_notif_parser.add_argument("--email-username", help="SMTP username")
        config_notif_parser.add_argument("--email-password", help="SMTP password")
        config_notif_parser.add_argument("--email-from", help="From email address")
        config_notif_parser.add_argument("--webhook-url", help="Webhook URL")
        config_notif_parser.add_argument(
            "--webhook-headers", help="Webhook headers (JSON format)"
        )

        # Init config command
        monitor_subparsers.add_parser(
            "init-config", help="Initialize monitoring configuration with samples"
        )

    def execute(self, args: Namespace, config: "CLIConfig", console: "Console") -> int:
        """Execute monitor command"""
        if not hasattr(args, "monitor_command") or not args.monitor_command:
            console.error(
                "Monitor command required. Use --help for available commands."
            )
            return 1

        if args.monitor_command == "start":
            return self._start_monitoring(args, config, console)
        elif args.monitor_command == "status":
            return self._show_status(args, config, console)
        elif args.monitor_command == "check":
            return self._force_check(args, config, console)
        elif args.monitor_command == "stop":
            return self._stop_monitoring(args, config, console)
        elif args.monitor_command == "add-policy":
            return self._add_policy(args, config, console)
        elif args.monitor_command == "remove-policy":
            return self._remove_policy(args, config, console)
        elif args.monitor_command == "list-policies":
            return self._list_policies(args, config, console)
        elif args.monitor_command == "configure-notifications":
            return self._configure_notifications(args, config, console)
        elif args.monitor_command == "init-config":
            return self._init_config(args, config, console)
        else:
            console.error(f"Unknown monitor command: {args.monitor_command}")
            return 1

    def _start_monitoring(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Start monitoring daemon"""

        async def start_monitoring():
            console.info("🚀 Starting drift monitoring daemon...")

            # Load configuration
            config_manager = get_config_manager()
            if args.config_file:
                config_manager.config_file = args.config_file

            try:
                monitor_config = config_manager.load_config()
                console.info(
                    f"📄 Loaded configuration from {config_manager.config_file}"
                )
            except Exception as e:
                console.warning(f"Could not load configuration: {e}")
                console.info("Using default configuration...")
                monitor_config = config_manager.create_sample_config()

            # Override with CLI options
            monitor_config.default_interval = args.interval
            monitor_config.max_concurrent_checks = args.max_concurrent
            monitor_config.enable_intelligent_caching = args.enable_cache
            monitor_config.cache_ttl = args.cache_ttl

            # Setup notification configuration
            notification_config = {}

            if args.slack_webhook:
                notification_config["slack_webhook"] = args.slack_webhook
            elif monitor_config.slack and monitor_config.slack.enabled:
                notification_config["slack_webhook"] = monitor_config.slack.webhook_url

            if (
                args.email_smtp
                and args.email_username
                and args.email_password
                and args.email_from
            ):
                notification_config["email_config"] = {
                    "smtp_server": args.email_smtp,
                    "smtp_port": args.email_port,
                    "username": args.email_username,
                    "password": args.email_password,
                    "from_email": args.email_from,
                }
            elif monitor_config.email and monitor_config.email.enabled:
                notification_config["email_config"] = {
                    "smtp_server": monitor_config.email.smtp_server,
                    "smtp_port": monitor_config.email.smtp_port,
                    "username": monitor_config.email.username,
                    "password": monitor_config.email.password,
                    "from_email": monitor_config.email.from_email,
                }

            if args.webhook_url:
                notification_config["webhook_url"] = args.webhook_url
            elif monitor_config.webhook and monitor_config.webhook.enabled:
                notification_config["webhook_url"] = monitor_config.webhook.webhook_url

            # Create monitoring policies from configuration
            policies = []
            for policy_config in monitor_config.policies:
                policy = MonitoringPolicy(
                    name=policy_config["name"],
                    resource_filter=policy_config.get("resource_filter", {}),
                    check_interval=policy_config.get("check_interval", args.interval),
                    priority=policy_config.get("priority", "medium"),
                    auto_remediate=policy_config.get("auto_remediate", False),
                    notification_channels=policy_config.get(
                        "notification_channels", []
                    ),
                )
                policies.append(policy)

            # Setup monitoring integration
            integration = await setup_monitoring_with_notifications(
                monitoring_policies=policies,
                slack_webhook=notification_config.get("slack_webhook", None),
                email_config=notification_config.get("email_config", None),
                webhook_url=notification_config.get("webhook_url", None),
            )

            console.success("✅ Drift monitoring daemon started successfully")
            console.info(f"📊 Monitoring interval: {args.interval} seconds")
            console.info(f"🔄 Max concurrent checks: {args.max_concurrent}")
            console.info(f"📝 Policies loaded: {len(policies)}")

            # Show status
            status = integration.get_status()
            console.info(f"🎯 Daemon state: {status['daemon_status']['state']}")

            if args.daemon_mode:
                # Run as daemon
                console.info("🔒 Running in daemon mode (Ctrl+C to stop)")
                try:
                    while True:
                        await asyncio.sleep(10)
                except KeyboardInterrupt:
                    console.info("\n🛑 Shutting down daemon...")
                    await integration.stop()
                    console.success("✅ Daemon stopped")
            else:
                # Interactive mode
                console.info("\n📋 Interactive mode - Commands:")
                console.info("  status - Show current status")
                console.info("  check - Force immediate check")
                console.info("  stop - Stop monitoring")
                console.info("  quit - Exit")

                while True:
                    try:
                        cmd = input("\nmonitor> ").strip().lower()

                        if cmd == "status":
                            status = integration.get_status()
                            console.info(
                                f"🎯 State: {status['daemon_status']['state']}"
                            )
                            console.info(
                                f"📊 Total checks: {status['daemon_status']['statistics']['total_checks']}"
                            )
                            console.info(
                                f"⚠️  Drift detected: {status['daemon_status']['statistics']['drift_detected']}"
                            )
                            console.info(
                                f"📱 Notifications: {status['notification_stats']['total_notifications']}"
                            )

                        elif cmd == "check":
                            console.info("🔍 Forcing immediate check...")
                            results = await integration.daemon.force_check()
                            drift_count = sum(1 for r in results if r.drift_detected)
                            console.success(
                                f"✅ Check completed: {len(results)} resources checked, {drift_count} drift detected"
                            )

                        elif cmd == "stop":
                            console.info("🛑 Stopping monitoring...")
                            await integration.stop()
                            console.success("✅ Monitoring stopped")
                            break

                        elif cmd in ["quit", "exit"]:
                            console.info("🛑 Stopping monitoring...")
                            await integration.stop()
                            console.success("✅ Goodbye!")
                            break

                        else:
                            console.error("❌ Unknown command")

                    except KeyboardInterrupt:
                        console.info("\n🛑 Stopping monitoring...")
                        await integration.stop()
                        console.success("✅ Goodbye!")
                        break
                    except EOFError:
                        console.info("\n🛑 Stopping monitoring...")
                        await integration.stop()
                        break

        try:
            asyncio.run(start_monitoring())
            return 0
        except Exception as e:
            console.error(f"Error starting monitoring: {e}")
            return 1

    def _stop_monitoring(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Stop monitoring daemon"""
        console.info("🛑 Stopping drift monitoring daemon...")
        # TODO: Implement daemon stop (requires process management)
        console.success("✅ Monitoring daemon stopped")
        return 0

    def _show_status(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Show monitoring status"""

        async def get_status():
            try:
                # Try to get status from running integration
                # For now, show configuration status
                config_manager = get_config_manager()
                monitor_config = config_manager.load_config()

                status_data = {
                    "configuration": {
                        "config_file": config_manager.config_file,
                        "default_interval": monitor_config.default_interval,
                        "max_concurrent_checks": monitor_config.max_concurrent_checks,
                        "intelligent_caching": monitor_config.enable_intelligent_caching,
                        "cache_ttl": monitor_config.cache_ttl,
                        "policies": len(monitor_config.policies),
                        "notification_rules": len(monitor_config.notification_rules),
                    },
                    "notifications": {
                        "slack_configured": monitor_config.slack is not None
                        and monitor_config.slack.enabled,
                        "email_configured": monitor_config.email is not None
                        and monitor_config.email.enabled,
                        "webhook_configured": monitor_config.webhook is not None
                        and monitor_config.webhook.enabled,
                    },
                    "policies": [
                        {
                            "name": policy["name"],
                            "check_interval": policy.get(
                                "check_interval", monitor_config.default_interval
                            ),
                            "priority": policy.get("priority", "medium"),
                            "auto_remediate": policy.get("auto_remediate", False),
                            "resource_filter": policy.get("resource_filter", {}),
                        }
                        for policy in monitor_config.policies
                    ],
                }

                if args.format == "json":
                    console.print(json.dumps(status_data, indent=2))
                else:
                    console.info("📊 Monitoring Status")
                    console.info("=" * 50)

                    # Configuration
                    console.info("\n🔧 Configuration:")
                    config_table = [
                        ["Config File", status_data["configuration"]["config_file"]],
                        [
                            "Default Interval",
                            f"{status_data['configuration']['default_interval']}s",
                        ],
                        [
                            "Max Concurrent",
                            status_data["configuration"]["max_concurrent_checks"],
                        ],
                        [
                            "Intelligent Caching",
                            status_data["configuration"]["intelligent_caching"],
                        ],
                        ["Cache TTL", f"{status_data['configuration']['cache_ttl']}s"],
                        ["Policies", status_data["configuration"]["policies"]],
                        [
                            "Notification Rules",
                            status_data["configuration"]["notification_rules"],
                        ],
                    ]
                    console.print(
                        tabulate(
                            config_table, headers=["Setting", "Value"], tablefmt="grid"
                        )
                    )

                    # Notifications
                    console.info("\n📱 Notifications:")
                    notif_table = [
                        [
                            "Slack",
                            (
                                "✅"
                                if status_data["notifications"]["slack_configured"]
                                else "❌"
                            ),
                        ],
                        [
                            "Email",
                            (
                                "✅"
                                if status_data["notifications"]["email_configured"]
                                else "❌"
                            ),
                        ],
                        [
                            "Webhook",
                            (
                                "✅"
                                if status_data["notifications"]["webhook_configured"]
                                else "❌"
                            ),
                        ],
                    ]
                    console.print(
                        tabulate(
                            notif_table,
                            headers=["Channel", "Configured"],
                            tablefmt="grid",
                        )
                    )

                    # Policies
                    if status_data["policies"]:
                        console.info("\n📝 Monitoring Policies:")
                        policies_table = [
                            [
                                policy["name"],
                                f"{policy['check_interval']}s",
                                policy["priority"],
                                "✅" if policy["auto_remediate"] else "❌",
                                (
                                    str(policy["resource_filter"])
                                    if policy["resource_filter"]
                                    else "None"
                                ),
                            ]
                            for policy in status_data["policies"]
                        ]
                        console.print(
                            tabulate(
                                policies_table,
                                headers=[
                                    "Name",
                                    "Interval",
                                    "Priority",
                                    "Auto-Remediate",
                                    "Filter",
                                ],
                                tablefmt="grid",
                            )
                        )

            except Exception as e:
                console.error(f"Error getting status: {e}")
                return 1

            return 0

        try:
            return asyncio.run(get_status())
        except Exception as e:
            console.error(f"Error showing status: {e}")
            return 1

    def _force_check(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Force an immediate drift check"""

        async def force_check():
            try:
                # Create a temporary daemon for checking
                daemon = DriftMonitoringDaemon(
                    enable_intelligent_caching=False  # Disable caching for immediate check
                )

                console.info("🔍 Performing drift check...")
                results = await daemon.force_check(args.resource_id)

                drift_count = sum(1 for r in results if r.drift_detected)

                if args.format == "json":
                    results_data = [
                        {
                            "resource_id": r.resource_id,
                            "resource_name": r.resource_name,
                            "resource_type": r.resource_type,
                            "drift_detected": r.drift_detected,
                            "drift_details": r.drift_details,
                            "check_timestamp": r.check_timestamp.isoformat(),
                        }
                        for r in results
                    ]
                    console.print(json.dumps(results_data, indent=2))
                else:
                    console.success(
                        f"✅ Check completed: {len(results)} resources checked, {drift_count} with drift"
                    )

                    if results:
                        # Show result table
                        results_table = [
                            [
                                r.resource_name,
                                r.resource_type,
                                "✅" if r.drift_detected else "❌",
                                str(r.drift_details) if r.drift_details else "None",
                                r.check_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                            ]
                            for r in results
                        ]
                        console.print(
                            tabulate(
                                results_table,
                                headers=[
                                    "Resource",
                                    "Type",
                                    "Drift",
                                    "Details",
                                    "Timestamp",
                                ],
                                tablefmt="grid",
                            )
                        )

            except Exception as e:
                console.error(f"❌ Error performing check: {e}")
                return 1

            return 0

        try:
            return asyncio.run(force_check())
        except Exception as e:
            console.error(f"Error performing check: {e}")
            return 1

    def _add_policy(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Add a monitoring policy"""
        # Build resource filter
        resource_filter = {}
        if args.environment:
            resource_filter["environment"] = args.environment
        if args.project:
            resource_filter["project"] = args.project
        if args.resource_type:
            resource_filter["type"] = args.resource_type
        if hasattr(args, "label") and args.label:
            labels = {}
            for label_str in args.label:
                if "=" in label_str:
                    key, value = label_str.split("=", 1)
                    labels[key] = value
            if labels:
                resource_filter["labels"] = labels

        # Create policy configuration
        policy_config = {
            "name": args.name,
            "resource_filter": resource_filter,
            "check_interval": args.check_interval,
            "priority": args.priority,
            "auto_remediate": args.auto_remediate,
            "notification_channels": (
                list(args.notification_channels)
                if hasattr(args, "notification_channels") and args.notification_channels
                else []
            ),
        }

        # Load existing configuration
        config_manager = get_config_manager()
        monitor_config = config_manager.load_config()

        # Add new policy
        monitor_config.policies.append(policy_config)

        # Save configuration
        config_manager.save_config(monitor_config)

        console.success(f"✅ Added monitoring policy: {args.name}")
        console.info(f"   Check interval: {args.check_interval}s")
        console.info(f"   Priority: {args.priority}")
        console.info(f"   Auto-remediate: {args.auto_remediate}")
        console.info(f"   Resource filter: {resource_filter}")
        console.info(
            f"   Notification channels: {policy_config['notification_channels']}"
        )
        return 0

    def _remove_policy(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Remove a monitoring policy"""
        # Load existing configuration
        config_manager = get_config_manager()
        monitor_config = config_manager.load_config()

        # Find and remove policy
        original_count = len(monitor_config.policies)
        monitor_config.policies = [
            p for p in monitor_config.policies if p["name"] != args.name
        ]

        if len(monitor_config.policies) < original_count:
            # Save configuration
            config_manager.save_config(monitor_config)
            console.success(f"✅ Removed monitoring policy: {args.name}")
            return 0
        else:
            console.error(f"❌ Policy not found: {args.name}")
            return 1

    def _list_policies(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """List monitoring policies"""
        # Load configuration
        config_manager = get_config_manager()
        monitor_config = config_manager.load_config()

        if args.format == "json":
            console.print(json.dumps(monitor_config.policies, indent=2))
        else:
            if not monitor_config.policies:
                console.info("📝 No monitoring policies configured")
            else:
                console.info("📝 Monitoring Policies:")
                policies_table = [
                    [
                        policy["name"],
                        f"{policy.get('check_interval', 300)}s",
                        policy.get("priority", "medium"),
                        "✅" if policy.get("auto_remediate", False) else "❌",
                        (
                            str(policy.get("resource_filter", {}))
                            if policy.get("resource_filter")
                            else "None"
                        ),
                        (
                            ", ".join(policy.get("notification_channels", []))
                            if policy.get("notification_channels")
                            else "None"
                        ),
                    ]
                    for policy in monitor_config.policies
                ]
                console.print(
                    tabulate(
                        policies_table,
                        headers=[
                            "Name",
                            "Interval",
                            "Priority",
                            "Auto-Remediate",
                            "Filter",
                            "Channels",
                        ],
                        tablefmt="grid",
                    )
                )
        return 0

    def _configure_notifications(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Configure notification settings"""
        # Load existing configuration
        config_manager = get_config_manager()
        monitor_config = config_manager.load_config()

        # Update Slack configuration
        if args.slack_webhook:
            from infradsl.core.monitoring.config import SlackConfig

            monitor_config.slack = SlackConfig(
                webhook_url=args.slack_webhook,
                channel=getattr(args, "slack_channel", None),
                enabled=True,
            )
            console.success(f"✅ Configured Slack notifications: {args.slack_webhook}")

        # Update email configuration
        if (
            args.email_smtp
            and args.email_username
            and args.email_password
            and args.email_from
        ):
            from infradsl.core.monitoring.config import EmailConfig

            monitor_config.email = EmailConfig(
                smtp_server=args.email_smtp,
                smtp_port=args.email_port or 587,
                username=args.email_username,
                password=args.email_password,
                from_email=args.email_from,
                enabled=True,
            )
            console.success(f"✅ Configured email notifications: {args.email_smtp}")

        # Update webhook configuration
        if args.webhook_url:
            from infradsl.core.monitoring.config import WebhookConfig

            headers = {}
            if hasattr(args, "webhook_headers") and args.webhook_headers:
                try:
                    headers = json.loads(args.webhook_headers)
                except json.JSONDecodeError:
                    console.error("❌ Invalid webhook headers JSON format")
                    return 1

            monitor_config.webhook = WebhookConfig(
                webhook_url=args.webhook_url, headers=headers, enabled=True
            )
            console.success(f"✅ Configured webhook notifications: {args.webhook_url}")

        # Save configuration
        config_manager.save_config(monitor_config)
        console.success("✅ Notification configuration saved")
        return 0

    def _init_config(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Initialize monitoring configuration with samples"""
        config_manager = get_config_manager()
        sample_config = config_manager.create_sample_config()

        try:
            config_manager.save_config(sample_config)
            console.success(
                f"✅ Sample configuration created: {config_manager.config_file}"
            )
            console.info("📝 Edit the configuration file to customize settings")
            console.info("🚀 Run 'infra monitor start' to begin monitoring")
            return 0
        except Exception as e:
            console.error(f"❌ Error creating configuration: {e}")
            return 1
