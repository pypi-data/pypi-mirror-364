"""
Auto-Remediation CLI Commands - Management commands for auto-remediation

This module provides CLI commands for managing auto-remediation requests,
approval workflows, and safety checks.
"""

import asyncio
import json
from argparse import Namespace
from typing import Optional, TYPE_CHECKING

from tabulate import tabulate

from infradsl.core.monitoring import (
    AutoRemediationEngine,
    AutoRemediationIntegration,
    RemediationStatus,
    SafetyLevel,
    setup_auto_remediation_integration,
    get_auto_remediation_integration,
)
from .base import BaseCommand

if TYPE_CHECKING:
    from ..utils.output import Console
    from ..utils.config import CLIConfig


class RemediateCommand(BaseCommand):
    """Auto-remediation management commands"""

    @property
    def name(self) -> str:
        return "remediate"

    @property
    def description(self) -> str:
        return "Manage auto-remediation requests and workflows"

    def register(self, subparsers) -> None:
        """Register remediate subcommands"""
        parser = subparsers.add_parser(
            self.name,
            help=self.description,
            description="Manage auto-remediation requests, approval workflows, and safety checks",
        )

        # Add common arguments
        self.add_common_arguments(parser)

        # Create subparsers for remediate commands
        remediate_subparsers = parser.add_subparsers(
            dest="remediate_command", help="Remediate commands", metavar="COMMAND"
        )

        # Start command
        start_parser = remediate_subparsers.add_parser(
            "start", help="Start the auto-remediation integration"
        )
        start_parser.add_argument(
            "--enable-auto-remediation",
            action="store_true",
            default=True,
            help="Enable auto-remediation",
        )
        start_parser.add_argument(
            "--disable-auto-remediation",
            action="store_true",
            help="Disable auto-remediation",
        )
        start_parser.add_argument(
            "--enable-auto-approval",
            action="store_true",
            help="Enable auto-approval",
        )
        start_parser.add_argument(
            "--disable-auto-approval",
            action="store_true",
            help="Disable auto-approval",
        )
        start_parser.add_argument(
            "--max-concurrent",
            type=int,
            default=3,
            help="Maximum concurrent remediation operations",
        )
        start_parser.add_argument(
            "--slack-webhook", help="Slack webhook URL for notifications"
        )
        start_parser.add_argument(
            "--daemon-mode", action="store_true", help="Run as daemon (non-interactive)"
        )

        # Requests command
        requests_parser = remediate_subparsers.add_parser(
            "requests", help="List remediation requests"
        )
        requests_parser.add_argument(
            "--format", choices=["table", "json"], default="table", help="Output format"
        )

        # Approve command
        approve_parser = remediate_subparsers.add_parser(
            "approve", help="Approve a remediation request"
        )
        approve_parser.add_argument("request_id", help="Request ID to approve")
        approve_parser.add_argument(
            "--approved-by", default="cli-user", help="Approver name"
        )

        # Reject command
        reject_parser = remediate_subparsers.add_parser(
            "reject", help="Reject a remediation request"
        )
        reject_parser.add_argument("request_id", help="Request ID to reject")
        reject_parser.add_argument("reason", help="Rejection reason")
        reject_parser.add_argument(
            "--rejected-by", default="cli-user", help="Rejector name"
        )

        # Rollback command
        rollback_parser = remediate_subparsers.add_parser(
            "rollback", help="Rollback a completed remediation"
        )
        rollback_parser.add_argument("request_id", help="Request ID to rollback")
        rollback_parser.add_argument("reason", help="Rollback reason")
        rollback_parser.add_argument(
            "--rolled-back-by", default="cli-user", help="Rollback initiator name"
        )

        # Show command
        show_parser = remediate_subparsers.add_parser(
            "show", help="Show detailed information about a remediation request"
        )
        show_parser.add_argument("request_id", help="Request ID to show")
        show_parser.add_argument(
            "--format", choices=["table", "json"], default="table", help="Output format"
        )

        # Stats command
        stats_parser = remediate_subparsers.add_parser(
            "stats", help="Show auto-remediation statistics"
        )
        stats_parser.add_argument(
            "--format", choices=["table", "json"], default="table", help="Output format"
        )

        # Toggle auto-remediation command
        toggle_remediation_parser = remediate_subparsers.add_parser(
            "toggle-auto-remediation", help="Toggle auto-remediation on/off"
        )
        toggle_remediation_parser.add_argument(
            "--enable", action="store_true", help="Enable auto-remediation"
        )
        toggle_remediation_parser.add_argument(
            "--disable", action="store_true", help="Disable auto-remediation"
        )

        # Toggle auto-approval command
        toggle_approval_parser = remediate_subparsers.add_parser(
            "toggle-auto-approval", help="Toggle auto-approval on/off"
        )
        toggle_approval_parser.add_argument(
            "--enable", action="store_true", help="Enable auto-approval"
        )
        toggle_approval_parser.add_argument(
            "--disable", action="store_true", help="Disable auto-approval"
        )

    def execute(self, args: Namespace, config: "CLIConfig", console: "Console") -> int:
        """Execute remediate command"""
        if not hasattr(args, "remediate_command") or not args.remediate_command:
            console.error(
                "Remediate command required. Use --help for available commands."
            )
            return 1

        handlers = {
            "start": self._start_integration,
            "requests": self._list_requests,
            "approve": self._approve_request,
            "reject": self._reject_request,
            "rollback": self._rollback_request,
            "show": self._show_request,
            "stats": self._show_stats,
            "toggle-auto-remediation": self._toggle_auto_remediation,
            "toggle-auto-approval": self._toggle_auto_approval,
        }

        handler = handlers.get(args.remediate_command)
        if not handler:
            console.error(f"Unknown remediate command: {args.remediate_command}")
            return 1

        try:
            return handler(args, config, console)
        except Exception as e:
            console.error(f"Command failed: {e}")
            if console.verbosity >= 2:
                import traceback
                console.error(traceback.format_exc())
            return 1

    def _start_integration(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Start the auto-remediation integration"""

        async def start_remediation():
            console.info("🚀 Starting auto-remediation integration...")

            # Determine enable flags
            enable_auto_remediation = True
            if args.disable_auto_remediation:
                enable_auto_remediation = False
            elif args.enable_auto_remediation:
                enable_auto_remediation = True

            enable_auto_approval = False
            if args.enable_auto_approval:
                enable_auto_approval = True
            elif args.disable_auto_approval:
                enable_auto_approval = False

            # Setup notification configuration
            notification_config = {}
            if args.slack_webhook:
                notification_config["slack_webhook"] = args.slack_webhook

            # Setup auto-remediation integration
            integration = await setup_auto_remediation_integration(
                enable_auto_remediation=enable_auto_remediation,
                enable_auto_approval=enable_auto_approval,
                notification_config=notification_config,
            )

            console.success("✅ Auto-remediation integration started successfully")
            console.info(f"🔧 Auto-remediation enabled: {enable_auto_remediation}")
            console.info(f"⚡ Auto-approval enabled: {enable_auto_approval}")
            console.info(f"🔄 Max concurrent operations: {args.max_concurrent}")

            # Show status
            status = integration.get_status()
            console.info(f"🎯 Daemon state: {status['drift_daemon_status']['state']}")

            if args.daemon_mode:
                # Run as daemon
                console.info("🔒 Running in daemon mode (Ctrl+C to stop)")
                try:
                    while True:
                        await asyncio.sleep(10)
                except KeyboardInterrupt:
                    console.info("\n🛑 Shutting down integration...")
                    await integration.stop()
                    console.success("✅ Integration stopped")
            else:
                # Interactive mode
                console.info("\n📋 Interactive mode - Commands:")
                console.info("  status - Show current status")
                console.info("  requests - List pending requests")
                console.info("  approve <id> - Approve a request")
                console.info("  reject <id> <reason> - Reject a request")
                console.info("  check - Force drift check")
                console.info("  stop - Stop integration")
                console.info("  quit - Exit")

                while True:
                    try:
                        cmd = input("\nremediate> ").strip()

                        if not cmd:
                            continue

                        parts = cmd.split()
                        command = parts[0].lower()

                        if command == "status":
                            status = integration.get_status()
                            console.info(
                                f"🎯 Auto-remediation: {status['auto_remediation_enabled']}"
                            )
                            console.info(
                                f"⚡ Auto-approval: {status['auto_approval_enabled']}"
                            )
                            console.info(
                                f"🔄 Daemon state: {status['drift_daemon_status']['state']}"
                            )

                            remediation_stats = status["remediation_engine_stats"]
                            console.info(
                                f"📊 Total requests: {remediation_stats['total_requests']}"
                            )
                            console.info(f"✅ Completed: {remediation_stats['completed']}")
                            console.info(f"❌ Failed: {remediation_stats['failed']}")
                            console.info(
                                f"🔄 Pending: {remediation_stats['by_status']['pending']}"
                            )

                        elif command == "requests":
                            pending = integration.get_pending_requests()
                            if not pending:
                                console.info("📋 No pending requests")
                            else:
                                console.info(f"📋 Pending requests ({len(pending)}):")
                                for req in pending:
                                    console.info(
                                        f"  {req['id']}: {req['resource_name']} ({req['safety_level']}) - {req['proposed_action']}"
                                    )

                        elif command == "approve" and len(parts) >= 2:
                            request_id = parts[1]
                            success = await integration.approve_request(
                                request_id, "cli-user"
                            )
                            if success:
                                console.success(f"✅ Request {request_id} approved")
                            else:
                                console.error(f"❌ Failed to approve request {request_id}")

                        elif command == "reject" and len(parts) >= 3:
                            request_id = parts[1]
                            reason = " ".join(parts[2:])
                            success = await integration.reject_request(
                                request_id, "cli-user", reason
                            )
                            if success:
                                console.success(f"✅ Request {request_id} rejected")
                            else:
                                console.error(f"❌ Failed to reject request {request_id}")

                        elif command == "check":
                            console.info("🔍 Forcing drift check...")
                            results = await integration.force_check()
                            drift_count = sum(1 for r in results if r.drift_detected)
                            console.success(
                                f"✅ Check completed: {len(results)} resources checked, {drift_count} drift detected"
                            )

                        elif command == "stop":
                            console.info("🛑 Stopping integration...")
                            await integration.stop()
                            console.success("✅ Integration stopped")
                            break

                        elif command in ["quit", "exit"]:
                            console.info("🛑 Stopping integration...")
                            await integration.stop()
                            console.success("✅ Goodbye!")
                            break

                        else:
                            console.error("❌ Unknown command or missing arguments")
                            console.info(
                                "Available commands: status, requests, approve <id>, reject <id> <reason>, check, stop, quit"
                            )

                    except KeyboardInterrupt:
                        console.info("\n🛑 Stopping integration...")
                        await integration.stop()
                        console.success("✅ Goodbye!")
                        break
                    except EOFError:
                        console.info("\n🛑 Stopping integration...")
                        await integration.stop()
                        break

        try:
            asyncio.run(start_remediation())
            return 0
        except Exception as e:
            console.error(f"Error starting integration: {e}")
            return 1

    def _list_requests(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """List remediation requests"""

        async def list_requests():
            try:
                # Create temporary engine to check for requests
                engine = AutoRemediationEngine()

                # Get all requests
                all_requests = list(engine.remediation_requests.values())

                if args.format == "json":
                    requests_data = [
                        {
                            "id": req.id,
                            "resource_name": req.drift_result.resource_name,
                            "resource_type": req.drift_result.resource_type,
                            "status": req.status.value,
                            "safety_level": req.safety_level.value,
                            "proposed_action": req.proposed_action.value,
                            "created_at": req.created_at.isoformat(),
                            "requested_by": req.requested_by,
                            "approved_by": req.approved_by,
                            "rejected_by": req.rejected_by,
                        }
                        for req in all_requests
                    ]
                    console.print(json.dumps(requests_data, indent=2))
                else:
                    if not all_requests:
                        console.info("📋 No remediation requests found")
                    else:
                        console.info(f"📋 Remediation Requests ({len(all_requests)}):")

                        # Group by status
                        by_status = {}
                        for req in all_requests:
                            status = req.status.value
                            if status not in by_status:
                                by_status[status] = []
                            by_status[status].append(req)

                        for status, requests in by_status.items():
                            console.info(f"\n{status.upper()} ({len(requests)}):")

                            requests_table = [
                                [
                                    req.id,
                                    req.drift_result.resource_name,
                                    req.drift_result.resource_type,
                                    req.safety_level.value,
                                    req.proposed_action.value,
                                    req.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                                    req.requested_by,
                                    req.approved_by or req.rejected_by or "-",
                                ]
                                for req in requests
                            ]

                            console.print(
                                tabulate(
                                    requests_table,
                                    headers=[
                                        "ID",
                                        "Resource",
                                        "Type",
                                        "Safety",
                                        "Action",
                                        "Created",
                                        "Requestor",
                                        "Reviewer",
                                    ],
                                    tablefmt="grid",
                                )
                            )

            except Exception as e:
                console.error(f"❌ Error listing requests: {e}")
                return 1

            return 0

        try:
            return asyncio.run(list_requests())
        except Exception as e:
            console.error(f"Error listing requests: {e}")
            return 1

    def _approve_request(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Approve a remediation request"""

        async def approve_request():
            try:
                engine = AutoRemediationEngine()
                success = await engine.approve_remediation(args.request_id, args.approved_by)

                if success:
                    console.success(f"✅ Request {args.request_id} approved by {args.approved_by}")
                    return 0
                else:
                    console.error(f"❌ Failed to approve request {args.request_id}")
                    return 1

            except Exception as e:
                console.error(f"❌ Error approving request: {e}")
                return 1

        try:
            return asyncio.run(approve_request())
        except Exception as e:
            console.error(f"Error approving request: {e}")
            return 1

    def _reject_request(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Reject a remediation request"""

        async def reject_request():
            try:
                engine = AutoRemediationEngine()
                success = await engine.reject_remediation(
                    args.request_id, args.rejected_by, args.reason
                )

                if success:
                    console.success(f"✅ Request {args.request_id} rejected by {args.rejected_by}")
                    console.info(f"📝 Reason: {args.reason}")
                    return 0
                else:
                    console.error(f"❌ Failed to reject request {args.request_id}")
                    return 1

            except Exception as e:
                console.error(f"❌ Error rejecting request: {e}")
                return 1

        try:
            return asyncio.run(reject_request())
        except Exception as e:
            console.error(f"Error rejecting request: {e}")
            return 1

    def _rollback_request(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Rollback a completed remediation"""

        async def rollback_request():
            try:
                engine = AutoRemediationEngine()
                success = await engine.rollback_remediation(
                    args.request_id, args.rolled_back_by, args.reason
                )

                if success:
                    console.success(f"✅ Request {args.request_id} rolled back by {args.rolled_back_by}")
                    console.info(f"📝 Reason: {args.reason}")
                    return 0
                else:
                    console.error(f"❌ Failed to rollback request {args.request_id}")
                    return 1

            except Exception as e:
                console.error(f"❌ Error rolling back request: {e}")
                return 1

        try:
            return asyncio.run(rollback_request())
        except Exception as e:
            console.error(f"Error rolling back request: {e}")
            return 1

    def _show_request(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Show detailed information about a remediation request"""

        async def show_request():
            try:
                engine = AutoRemediationEngine()
                request_status = engine.get_request_status(args.request_id)

                if not request_status:
                    console.error(f"❌ Request {args.request_id} not found")
                    return 1

                if args.format == "json":
                    console.print(json.dumps(request_status, indent=2))
                else:
                    console.info(f"📋 Remediation Request: {args.request_id}")
                    console.info("=" * 50)

                    # Basic info
                    basic_info = [
                        ["ID", request_status["id"]],
                        ["Status", request_status["status"]],
                        ["Safety Level", request_status["safety_level"]],
                        ["Proposed Action", request_status["proposed_action"]],
                        ["Created At", request_status["created_at"]],
                        ["Requested By", request_status["requested_by"]],
                        ["Approved By", request_status["approved_by"] or "-"],
                        ["Rejected By", request_status["rejected_by"] or "-"],
                        [
                            "Rejection Reason",
                            request_status["rejection_reason"] or "-",
                        ],
                    ]

                    console.info("\n📊 Basic Information:")
                    console.print(
                        tabulate(basic_info, headers=["Field", "Value"], tablefmt="grid")
                    )

                    # Safety checks
                    if request_status["safety_checks"]:
                        console.info("\n🛡️  Safety Checks:")
                        safety_table = [
                            [
                                check["check_name"],
                                check["description"],
                                check["severity"],
                                "✅" if check["passed"] else "❌",
                                check.get("error", "-"),
                            ]
                            for check in request_status["safety_checks"]
                        ]
                        console.print(
                            tabulate(
                                safety_table,
                                headers=[
                                    "Check",
                                    "Description",
                                    "Severity",
                                    "Passed",
                                    "Error",
                                ],
                                tablefmt="grid",
                            )
                        )

                    # Audit trail
                    if request_status["audit_trail"]:
                        console.info("\n📜 Audit Trail:")
                        audit_table = [
                            [
                                entry["timestamp"],
                                entry["event"],
                                str(entry["details"]),
                            ]
                            for entry in request_status["audit_trail"]
                        ]
                        console.print(
                            tabulate(
                                audit_table,
                                headers=["Timestamp", "Event", "Details"],
                                tablefmt="grid",
                            )
                        )

                return 0

            except Exception as e:
                console.error(f"❌ Error showing request: {e}")
                return 1

        try:
            return asyncio.run(show_request())
        except Exception as e:
            console.error(f"Error showing request: {e}")
            return 1

    def _show_stats(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Show auto-remediation statistics"""

        async def show_stats():
            try:
                engine = AutoRemediationEngine()
                stats = engine.get_statistics()

                if args.format == "json":
                    console.print(json.dumps(stats, indent=2))
                else:
                    console.info("📊 Auto-Remediation Statistics")
                    console.info("=" * 50)

                    # Overview
                    overview = [
                        ["Total Requests", stats["total_requests"]],
                        ["Auto Approved", stats["auto_approved"]],
                        ["Manual Approved", stats["manual_approved"]],
                        ["Rejected", stats["rejected"]],
                        ["Completed", stats["completed"]],
                        ["Failed", stats["failed"]],
                        ["Rolled Back", stats["rolled_back"]],
                        ["Escalated", stats["escalated"]],
                    ]

                    console.info("\n📈 Overview:")
                    console.print(
                        tabulate(overview, headers=["Metric", "Count"], tablefmt="grid")
                    )

                    # By Status
                    status_table = [
                        ["Pending", stats["by_status"]["pending"]],
                        ["Approved", stats["by_status"]["approved"]],
                        ["Rejected", stats["by_status"]["rejected"]],
                        ["Completed", stats["by_status"]["completed"]],
                        ["Failed", stats["by_status"]["failed"]],
                    ]

                    console.info("\n📊 By Status:")
                    console.print(
                        tabulate(
                            status_table,
                            headers=["Status", "Count"],
                            tablefmt="grid",
                        )
                    )

                    # Configuration
                    config_table = [
                        ["Active Remediations", stats["active_remediations"]],
                        ["Safety Checks", stats["safety_checks_configured"]],
                        [
                            "Approval Workflows",
                            stats["approval_workflows_configured"],
                        ],
                    ]

                    console.info("\n⚙️  Configuration:")
                    console.print(
                        tabulate(
                            config_table,
                            headers=["Setting", "Value"],
                            tablefmt="grid",
                        )
                    )

                return 0

            except Exception as e:
                console.error(f"❌ Error showing statistics: {e}")
                return 1

        try:
            return asyncio.run(show_stats())
        except Exception as e:
            console.error(f"Error showing statistics: {e}")
            return 1

    def _toggle_auto_remediation(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Toggle auto-remediation on/off"""
        try:
            integration = get_auto_remediation_integration()

            if args.enable:
                integration.enable_auto_remediation()
                console.success("✅ Auto-remediation enabled")
            elif args.disable:
                integration.disable_auto_remediation()
                console.success("❌ Auto-remediation disabled")
            else:
                console.error("❌ Must specify --enable or --disable")
                return 1

            return 0

        except Exception as e:
            console.error(f"❌ Error toggling auto-remediation: {e}")
            return 1

    def _toggle_auto_approval(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Toggle auto-approval on/off"""
        try:
            integration = get_auto_remediation_integration()

            if args.enable:
                integration.enable_auto_approval()
                console.success("✅ Auto-approval enabled")
            elif args.disable:
                integration.disable_auto_approval()
                console.success("❌ Auto-approval disabled")
            else:
                console.error("❌ Must specify --enable or --disable")
                return 1

            return 0

        except Exception as e:
            console.error(f"❌ Error toggling auto-approval: {e}")
            return 1