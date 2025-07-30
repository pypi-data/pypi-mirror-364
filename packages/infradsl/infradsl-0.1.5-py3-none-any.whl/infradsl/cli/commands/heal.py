"""
Self-healing engine CLI command
"""

import asyncio
import json
from argparse import Namespace
from typing import TYPE_CHECKING

from .base import BaseCommand
from ..utils.errors import CommandError
from ...core.reconciliation import (
    get_self_healing_engine,
    EngineConfig,
    EngineStatus,
    DriftSeverity,
    ReconciliationAction,
    create_default_policies,
    create_conservative_policies,
    create_aggressive_policies,
)
from ...core.nexus.provider_registry import get_registry

if TYPE_CHECKING:
    from ..utils.output import Console
    from ..utils.config import CLIConfig


class HealCommand(BaseCommand):
    """Self-healing engine management command"""

    @property
    def name(self) -> str:
        return "heal"

    @property
    def description(self) -> str:
        return "Manage the self-healing engine for automatic infrastructure reconciliation"

    def register(self, subparsers) -> None:
        """Register heal command and subcommands"""
        parser = subparsers.add_parser(
            self.name,
            help=self.description,
            description="Manage the self-healing engine for automatic infrastructure reconciliation",
        )

        heal_subparsers = parser.add_subparsers(dest="heal_action", help="Self-healing actions")

        # Start engine
        start_parser = heal_subparsers.add_parser(
            "start",
            help="Start the self-healing engine"
        )
        start_parser.add_argument(
            "--policy-set",
            choices=["default", "conservative", "aggressive"],
            default="default",
            help="Policy set to use"
        )
        start_parser.add_argument(
            "--check-interval",
            type=int,
            default=300,
            metavar="SECONDS",
            help="Check interval in seconds"
        )
        start_parser.add_argument(
            "--no-auto-remediation",
            action="store_true",
            help="Disable automatic remediation (notifications only)"
        )

        # Stop engine
        heal_subparsers.add_parser(
            "stop",
            help="Stop the self-healing engine"
        )

        # Pause engine
        heal_subparsers.add_parser(
            "pause",
            help="Pause the self-healing engine"
        )

        # Resume engine
        heal_subparsers.add_parser(
            "resume",
            help="Resume the self-healing engine"
        )

        # Status
        status_parser = heal_subparsers.add_parser(
            "status",
            help="Show engine status and statistics"
        )
        status_parser.add_argument(
            "--json",
            action="store_true",
            help="Output in JSON format"
        )

        # Force check
        check_parser = heal_subparsers.add_parser(
            "check",
            help="Force an immediate drift check"
        )
        check_parser.add_argument(
            "--project",
            help="Check specific project only"
        )
        check_parser.add_argument(
            "--environment", "--env",
            help="Check specific environment only"
        )
        check_parser.add_argument(
            "--resource-type",
            help="Check specific resource type only"
        )

        # Show events
        events_parser = heal_subparsers.add_parser(
            "events",
            help="Show recent drift events"
        )
        events_parser.add_argument(
            "--limit",
            type=int,
            default=20,
            help="Maximum number of events to show"
        )
        events_parser.add_argument(
            "--json",
            action="store_true",
            help="Output in JSON format"
        )

        # Show results
        results_parser = heal_subparsers.add_parser(
            "results",
            help="Show recent reconciliation results"
        )
        results_parser.add_argument(
            "--limit",
            type=int,
            default=20,
            help="Maximum number of results to show"
        )
        results_parser.add_argument(
            "--json",
            action="store_true",
            help="Output in JSON format"
        )

        # Policies
        policies_parser = heal_subparsers.add_parser(
            "policies",
            help="Show configured reconciliation policies"
        )
        policies_parser.add_argument(
            "--json",
            action="store_true",
            help="Output in JSON format"
        )

    def execute(self, args: Namespace, config: "CLIConfig", console: "Console") -> int:
        """Execute heal command"""
        try:
            if not hasattr(args, 'heal_action') or args.heal_action is None:
                console.error("No heal action specified. Use --help for available actions.")
                return 1

            if args.heal_action == "start":
                return asyncio.run(self._start_engine(args, console))
            elif args.heal_action == "stop":
                return asyncio.run(self._stop_engine(console))
            elif args.heal_action == "pause":
                return asyncio.run(self._pause_engine(console))
            elif args.heal_action == "resume":
                return asyncio.run(self._resume_engine(console))
            elif args.heal_action == "status":
                return self._show_status(args, console)
            elif args.heal_action == "check":
                return asyncio.run(self._force_check(args, console))
            elif args.heal_action == "events":
                return self._show_events(args, console)
            elif args.heal_action == "results":
                return self._show_results(args, console)
            elif args.heal_action == "policies":
                return self._show_policies(args, console)
            else:
                console.error(f"Unknown heal action: {args.heal_action}")
                return 1

        except Exception as e:
            console.error(f"Heal command failed: {str(e)}")
            return 1

    async def _start_engine(self, args: Namespace, console: "Console") -> int:
        """Start the self-healing engine"""
        engine = get_self_healing_engine()
        
        # Check if already running
        if engine.status == EngineStatus.RUNNING:
            console.print("✅ Self-healing engine is already running")
            return 0
        
        # Configure engine
        config = EngineConfig(
            check_interval_seconds=args.check_interval,
            auto_remediation_enabled=not args.no_auto_remediation,
        )
        engine.config = config
        
        # Set up policies
        if args.policy_set == "conservative":
            policies = create_conservative_policies()
        elif args.policy_set == "aggressive":
            policies = create_aggressive_policies()
        else:
            policies = create_default_policies()
        
        # Clear existing policies and add new ones
        engine.policies.clear()
        for policy in policies:
            engine.add_policy(policy)
        
        # Register providers
        registry = get_registry()
        provider_metadata = registry.list_providers()
        
        # Note: This would need actual provider instances
        # For now, we'll skip provider registration
        console.info(f"Found {len(provider_metadata)} providers")
        
        # Start engine
        console.info("🚀 Starting self-healing engine...")
        await engine.start()
        
        console.print("✅ Self-healing engine started successfully")
        console.print(f"Policy set: {args.policy_set}")
        console.print(f"Check interval: {args.check_interval} seconds")
        console.print(f"Auto-remediation: {'disabled' if args.no_auto_remediation else 'enabled'}")
        console.print(f"Policies loaded: {len(engine.policies)}")
        
        return 0

    async def _stop_engine(self, console: "Console") -> int:
        """Stop the self-healing engine"""
        engine = get_self_healing_engine()
        
        if engine.status == EngineStatus.STOPPED:
            console.print("ℹ️  Self-healing engine is already stopped")
            return 0
        
        console.info("🛑 Stopping self-healing engine...")
        await engine.stop()
        
        console.print("✅ Self-healing engine stopped")
        return 0

    async def _pause_engine(self, console: "Console") -> int:
        """Pause the self-healing engine"""
        engine = get_self_healing_engine()
        
        if engine.status != EngineStatus.RUNNING:
            console.error("Engine is not running")
            return 1
        
        await engine.pause()
        console.print("⏸️  Self-healing engine paused")
        return 0

    async def _resume_engine(self, console: "Console") -> int:
        """Resume the self-healing engine"""
        engine = get_self_healing_engine()
        
        if engine.status != EngineStatus.PAUSED:
            console.error("Engine is not paused")
            return 1
        
        await engine.resume()
        console.print("▶️  Self-healing engine resumed")
        return 0

    def _show_status(self, args: Namespace, console: "Console") -> int:
        """Show engine status"""
        engine = get_self_healing_engine()
        status = engine.get_status()
        
        if args.json:
            console.print(json.dumps(status, indent=2))
            return 0
        
        # Format status display
        console.print("🏥 Self-Healing Engine Status\n")
        
        # Basic status
        status_emoji = {
            "running": "🟢",
            "paused": "🟡",
            "stopped": "🔴",
            "error": "❌",
            "starting": "🔄",
            "stopping": "🔄",
        }
        
        console.print(f"Status: {status_emoji.get(status['status'], '❓')} {status['status'].upper()}")
        
        if status['uptime_seconds']:
            uptime_hours = status['uptime_seconds'] / 3600
            console.print(f"Uptime: {uptime_hours:.1f} hours")
        
        # Statistics
        stats = status['stats']
        console.print(f"\nStatistics:")
        console.print(f"  Checks performed: {stats['checks_performed']}")
        console.print(f"  Drift events detected: {stats['drift_events_detected']}")
        console.print(f"  Reconciliations attempted: {stats['reconciliations_attempted']}")
        console.print(f"  Reconciliations successful: {stats['reconciliations_successful']}")
        console.print(f"  Notifications sent: {stats['notifications_sent']}")
        
        if stats['last_check_time']:
            console.print(f"  Last check: {stats['last_check_time']}")
        
        # Policies
        console.print(f"\nPolicies: {len(status['policies'])}")
        for policy in status['policies']:
            enabled_str = "✅" if policy['enabled'] else "❌"
            console.print(f"  {enabled_str} {policy['name']}: {policy['description']}")
            if policy['trigger_count'] > 0:
                console.print(f"    Triggers: {policy['trigger_count']}")
        
        # Recent activity
        console.print(f"\nRecent Activity:")
        console.print(f"  Events: {status['recent_events']}")
        console.print(f"  Results: {status['recent_results']}")
        
        return 0

    async def _force_check(self, args: Namespace, console: "Console") -> int:
        """Force an immediate drift check"""
        engine = get_self_healing_engine()
        
        console.info("🔍 Starting forced drift check...")
        
        events = await engine.force_check(
            project=args.project,
            environment=args.environment,
            resource_type=args.resource_type
        )
        
        console.print(f"✅ Force check completed: {len(events)} drift events detected")
        
        if events:
            console.print("\nDrift Events:")
            for event in events[:10]:  # Show first 10 events
                severity_emoji = {
                    "low": "🟢",
                    "medium": "🟡",
                    "high": "🟠",
                    "critical": "🔴"
                }
                
                emoji = severity_emoji.get(event.severity.value, "❓")
                console.print(f"  {emoji} {event.resource_name} ({event.drift_type})")
        
        return 0

    def _show_events(self, args: Namespace, console: "Console") -> int:
        """Show recent drift events"""
        engine = get_self_healing_engine()
        events = engine.get_recent_events(limit=args.limit)
        
        if args.json:
            console.print(json.dumps(events, indent=2))
            return 0
        
        console.print(f"📊 Recent Drift Events ({len(events)})\n")
        
        if not events:
            console.print("No recent drift events")
            return 0
        
        # Table format
        headers = ["Time", "Resource", "Type", "Severity", "Drift"]
        rows = []
        
        for event in events:
            severity_emoji = {
                "low": "🟢",
                "medium": "🟡",
                "high": "🟠",
                "critical": "🔴"
            }
            
            emoji = severity_emoji.get(event['severity'], "❓")
            rows.append([
                event['detected_at'][:19],  # Truncate timestamp
                event['resource_name'],
                event['resource_type'],
                f"{emoji} {event['severity']}",
                event['drift_type']
            ])
        
        console.print_table(headers, rows)
        return 0

    def _show_results(self, args: Namespace, console: "Console") -> int:
        """Show recent reconciliation results"""
        engine = get_self_healing_engine()
        results = engine.get_recent_results(limit=args.limit)
        
        if args.json:
            console.print(json.dumps(results, indent=2))
            return 0
        
        console.print(f"📋 Recent Reconciliation Results ({len(results)})\n")
        
        if not results:
            console.print("No recent reconciliation results")
            return 0
        
        # Table format
        headers = ["Time", "Action", "Status", "Duration", "Message"]
        rows = []
        
        for result in results:
            status_emoji = "✅" if result['success'] else "❌"
            
            rows.append([
                result['timestamp'][:19],  # Truncate timestamp
                result['action'],
                f"{status_emoji} {'success' if result['success'] else 'failed'}",
                f"{result['duration']:.2f}s",
                result['message'][:50] + "..." if len(result['message']) > 50 else result['message']
            ])
        
        console.print_table(headers, rows)
        return 0

    def _show_policies(self, args: Namespace, console: "Console") -> int:
        """Show configured reconciliation policies"""
        engine = get_self_healing_engine()
        status = engine.get_status()
        
        if args.json:
            console.print(json.dumps(status['policies'], indent=2))
            return 0
        
        console.print("📋 Reconciliation Policies\n")
        
        if not status['policies']:
            console.print("No policies configured")
            return 0
        
        for policy in status['policies']:
            enabled_str = "✅ ENABLED" if policy['enabled'] else "❌ DISABLED"
            console.print(f"{enabled_str} {policy['name']}")
            console.print(f"  Description: {policy['description']}")
            console.print(f"  Triggers: {policy['trigger_count']}")
            
            if policy['last_triggered']:
                console.print(f"  Last triggered: {policy['last_triggered']}")
            
            console.print("")
        
        return 0