"""
Main Apply Command - orchestrates the apply process
"""

import asyncio
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List
from argparse import Namespace

from ..base import BaseCommand
from ...utils.errors import CommandError
from ....core.nexus.engine import NexusEngine
from ....core.nexus.lifecycle import LifecycleManager
from ....core.nexus.reconciler import StateReconciler
from ....core.services.dependency_resolver import DependencyResolver

from .loader import InfrastructureLoader
from .planner import ChangePlanner
from .executor import ChangeExecutor
from .display import ChangeDisplayer

if TYPE_CHECKING:
    from ...utils.output import Console
    from ...utils.config import CLIConfig


class ApplyCommand(BaseCommand):
    """Apply infrastructure changes"""

    def __init__(self):
        self.loader = InfrastructureLoader()
        self.planner = ChangePlanner()
        self.executor = ChangeExecutor()
        self.display = ChangeDisplayer()

    @property
    def name(self) -> str:
        return "apply"

    @property
    def description(self) -> str:
        return "Apply infrastructure changes"

    def register(self, subparsers) -> None:
        """Register command arguments"""
        parser = subparsers.add_parser(
            self.name,
            help=self.description,
            description="Apply infrastructure changes from a Python file",
        )

        parser.add_argument("file", type=Path, help="Infrastructure file to apply")

        parser.add_argument(
            "--auto-approve", action="store_true", help="Skip confirmation prompts"
        )

        parser.add_argument(
            "--parallelism",
            type=int,
            default=10,
            help="Number of parallel operations (default: 10)",
        )

        parser.add_argument(
            "--refresh", action="store_true", help="Refresh state before applying"
        )

        parser.add_argument(
            "--target",
            action="append",
            help="Target specific resources (can be used multiple times)",
        )

        self.add_common_arguments(parser)

    def execute(self, args: Namespace, config: "CLIConfig", console: "Console") -> int:
        """Execute the apply command"""
        infrastructure_file = args.file

        if not infrastructure_file.exists():
            console.error(f"Infrastructure file not found: {infrastructure_file}")
            return 1

        console.info(f"Applying infrastructure from: {infrastructure_file}")

        try:
            # Load infrastructure
            resources = self.loader.load_infrastructure(infrastructure_file, console)

            if not resources:
                console.info("No resources found to apply")
                return 0

            # Initialize engines
            engine = NexusEngine()
            lifecycle_manager = LifecycleManager()
            reconciler = StateReconciler()

            # Filter resources by target if specified
            if args.target:
                resources = self.loader.filter_resources(resources, args.target, console)

            # Plan changes
            console.info("Analyzing infrastructure changes...")
            with console.status("Planning changes..."):
                changes = self.planner.plan_changes(resources, reconciler, console)

            # Check if there are actually any changes
            total_changes = sum(len(resources) for resources in changes.values())
            if total_changes == 0:
                console.success("No changes needed. Infrastructure is up to date.")
                return 0

            # Display changes
            self.display.display_changes(changes, console)

            # Confirm changes
            if not args.auto_approve and not config.auto_approve:
                if not console.confirm("Apply these changes?"):
                    console.info("Apply cancelled")
                    return 0

            # Apply changes with dependency resolution
            return self.executor.apply_changes_with_dependencies(
                changes, engine, lifecycle_manager, console, args
            )

        except Exception as e:
            raise CommandError(f"Failed to apply infrastructure: {e}")