"""
Context-aware resource discovery CLI command
"""

import asyncio
import json
from argparse import Namespace
from typing import TYPE_CHECKING, Set
from datetime import datetime, timedelta

from .base import BaseCommand
from ..utils.errors import CommandError
from ...core.discovery.context_aware_discovery import (
    ContextAwareDiscoveryEngine,
    DiscoveryContext,
    DiscoveryScope,
    ContextHint,
)
from ...core.nexus.provider_registry import get_registry

if TYPE_CHECKING:
    from ..utils.output import Console
    from ..utils.config import CLIConfig


class DiscoverCommand(BaseCommand):
    """Context-aware resource discovery command"""

    @property
    def name(self) -> str:
        return "discover"

    @property
    def description(self) -> str:
        return "Discover cloud resources using context-aware selective discovery"

    def register(self, subparsers) -> None:
        """Register discover command"""
        parser = subparsers.add_parser(
            self.name,
            help=self.description,
            description="Discover cloud resources with intelligent context-aware scanning",
        )

        # Context filters
        parser.add_argument("--project", help="Filter resources by project")
        parser.add_argument(
            "--environment", "--env", help="Filter resources by environment"
        )
        parser.add_argument("--region", help="Filter resources by region")

        # Resource filters
        parser.add_argument(
            "--type",
            "--resource-type",
            action="append",
            help="Filter by resource type (can be specified multiple times)",
        )
        parser.add_argument(
            "--tag",
            action="append",
            help="Filter by tag in format key=value (can be specified multiple times)",
        )

        # Discovery scope
        parser.add_argument(
            "--scope",
            choices=[s.value for s in DiscoveryScope],
            default=DiscoveryScope.SELECTIVE.value,
            help="Discovery scope level",
        )

        # Context hints
        parser.add_argument(
            "--hint",
            action="append",
            choices=[h.value for h in ContextHint],
            help="Context hint to optimize discovery (can be specified multiple times)",
        )

        # Providers
        parser.add_argument(
            "--provider",
            action="append",
            help="Specific provider to scan (can be specified multiple times)",
        )

        # Performance options
        parser.add_argument(
            "--no-cache", action="store_true", help="Disable cache usage"
        )
        parser.add_argument(
            "--sequential",
            action="store_true",
            help="Use sequential discovery instead of parallel",
        )
        parser.add_argument(
            "--max-age",
            type=int,
            metavar="MINUTES",
            help="Maximum age of cached results in minutes",
        )
        parser.add_argument(
            "--max-concurrent",
            type=int,
            default=10,
            metavar="N",
            help="Maximum concurrent requests",
        )

        # Output options
        parser.add_argument(
            "--format",
            choices=["table", "json", "yaml"],
            default="table",
            help="Output format",
        )
        parser.add_argument("--output", "-o", help="Output file path")
        parser.add_argument(
            "--stats", action="store_true", help="Show discovery statistics"
        )

    def execute(self, args: Namespace, config: "CLIConfig", console: "Console") -> int:
        """Execute discover command"""
        try:
            # Create discovery context
            context = self._create_discovery_context(args)

            # Run discovery
            return asyncio.run(self._run_discovery(args, context, console))

        except Exception as e:
            console.error(f"Discovery failed: {str(e)}")
            return 1

    def _create_discovery_context(self, args: Namespace) -> DiscoveryContext:
        """Create discovery context from command arguments"""

        # Parse resource types
        resource_types = None
        if args.type:
            resource_types = set(args.type)

        # Parse tags
        tags = None
        if args.tag:
            tags = {}
            for tag_str in args.tag:
                if "=" in tag_str:
                    key, value = tag_str.split("=", 1)
                    tags[key] = value
                else:
                    tags[tag_str] = tag_str

        # Parse hints
        hints = None
        if args.hint:
            hints = set(ContextHint(h) for h in args.hint)

        # Parse max age
        max_age = None
        if args.max_age:
            max_age = timedelta(minutes=args.max_age)

        return DiscoveryContext(
            project=args.project,
            environment=args.environment,
            region=args.region,
            resource_types=resource_types,
            tags=tags,
            hints=hints,
            scope=DiscoveryScope(args.scope),
            max_age=max_age,
            use_cache=not args.no_cache,
            parallel_discovery=not args.sequential,
            max_concurrent_requests=args.max_concurrent,
        )

    async def _run_discovery(
        self, args: Namespace, context: DiscoveryContext, console: "Console"
    ) -> int:
        """Run the discovery process"""

        # Create discovery engine
        engine = ContextAwareDiscoveryEngine()

        # Register providers
        provider_registry = get_registry()
        available_providers = provider_registry.list_providers()

        # Filter to requested providers if specified
        if args.provider:
            available_providers = [
                provider
                for provider in available_providers
                if provider.name in args.provider
            ]

        if not available_providers:
            console.error("No providers available for discovery")
            return 1

        # Register providers with discovery engine
        # Note: This would need actual provider instances, not metadata
        # For now, we'll skip provider registration and let the engine handle it
        pass

        # Show discovery plan
        if args.stats:
            console.info(
                f"🔍 Starting discovery with {len(available_providers)} providers"
            )
            console.info(f"Scope: {context.scope.value}")
            if context.hints:
                hints_str = ", ".join(h.value for h in context.hints)
                console.info(f"Hints: {hints_str}")
            if context.resource_types:
                types_str = ", ".join(context.resource_types)
                console.info(f"Resource types: {types_str}")

        # Execute discovery
        start_time = datetime.utcnow()
        provider_names = [provider.name for provider in available_providers]
        resources = await engine.discover_resources(context, providers=provider_names)
        end_time = datetime.utcnow()

        # Show statistics
        if args.stats:
            duration = (end_time - start_time).total_seconds()
            console.info(f"✅ Discovery completed in {duration:.2f}s")
            console.info(f"Found {len(resources)} resources")

            # Group by provider
            by_provider = {}
            for resource in resources:
                provider = resource.get("provider", "unknown")
                by_provider.setdefault(provider, 0)
                by_provider[provider] += 1

            if by_provider:
                console.info("Resources by provider:")
                for provider, count in sorted(by_provider.items()):
                    console.info(f"  {provider}: {count}")

        # Output results
        if args.output:
            self._write_output(resources, args.format, args.output)
            console.info(f"Results written to {args.output}")
        else:
            self._display_results(resources, args.format, console)

        return 0

    def _display_results(
        self, resources: list, format_type: str, console: "Console"
    ) -> None:
        """Display discovery results"""

        if format_type == "json":
            console.print(json.dumps(resources, indent=2))
        elif format_type == "yaml":
            import yaml

            console.print(yaml.dump(resources, default_flow_style=False))
        else:
            # Table format
            if not resources:
                console.print("No resources found")
                return

            # Create table data
            headers = ["Name", "Type", "Provider", "State", "Region", "Project"]
            rows = []

            for resource in resources:
                row = [
                    resource.get("name", ""),
                    resource.get("type", ""),
                    resource.get("provider", ""),
                    resource.get("state", ""),
                    resource.get("region", ""),
                    resource.get("project", ""),
                ]
                rows.append(row)

            # Print table using console output method
            console.output(rows)

    def _write_output(
        self, resources: list, format_type: str, output_path: str
    ) -> None:
        """Write results to output file"""

        if format_type == "json":
            with open(output_path, "w") as f:
                json.dump(resources, f, indent=2)
        elif format_type == "yaml":
            import yaml

            with open(output_path, "w") as f:
                yaml.dump(resources, f, default_flow_style=False)
        else:
            # CSV format for table
            import csv

            with open(output_path, "w", newline="") as f:
                if resources:
                    writer = csv.DictWriter(f, fieldnames=resources[0].keys())
                    writer.writeheader()
                    writer.writerows(resources)
