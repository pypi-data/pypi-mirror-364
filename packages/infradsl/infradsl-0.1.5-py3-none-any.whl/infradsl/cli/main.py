#!/usr/bin/env python3
"""
InfraDSL CLI - Main entry point
"""

import sys
import argparse
from typing import List, Optional
from pathlib import Path
import traceback

from .commands import (
    InitCommand,
    ApplyCommand,
    DestroyCommand,
    PreviewCommand,
    DriftCommand,
    StateCommand,
    ConfigCommand,
    HealthCommand,
    InsightsCommand,
    CacheCommand,
    DiscoverCommand,
    HealCommand,
    GenerateCommand,
    ImportCommand,
    ServeCommand,
    VisualizeCommand,
    MonitorCommand,
    RemediateCommand,
    ProviderCommand,
    RegistryCommand,
    AuthCommand,
    CreateTemplateCommand,
)
from .utils.output import Console, OutputFormat
from .utils.config import CLIConfig
from .utils.errors import InfraDSLCLIError
# Get version without importing parent module to avoid circular imports
__version__ = "0.1.5"


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser"""
    parser = argparse.ArgumentParser(
        prog="infra",
        description="InfraDSL - Infrastructure as Code, Redefined",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  infra init myproject              Initialize a new project
  infra apply infrastructure.py     Apply infrastructure changes
  infra preview infrastructure.py   Preview changes without applying
  infra destroy infrastructure.py   Destroy infrastructure
  infra drift check                 Check for infrastructure drift
  infra state list                  List managed resources
  infra health                      Check resource health
  infra insights                    Show cost and security insights
  infra cache stats                 Show cache statistics
  infra discover aws                Discover AWS resources
  infra heal start                  Start self-healing engine
  infra generate provider aws       Generate AWS provider code
  infra serve                       Start HTTP/gRPC service

For more information, visit: https://docs.infradsl.dev/reference/cli/
        """,
    )

    # Global options
    parser.add_argument(
        "--version", action="version", version=f"InfraDSL {__version__}"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Increase verbosity (use -vv for debug)",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress non-error output"
    )
    parser.add_argument(
        "--format",
        choices=["table", "json", "yaml"],
        default="table",
        help="Output format (default: table)",
    )
    parser.add_argument(
        "--no-color", action="store_true", help="Disable colored output"
    )
    parser.add_argument("--config", type=Path, help="Path to configuration file")
    parser.add_argument("--project", help="Project name (overrides config)")
    parser.add_argument("--environment", help="Environment name (overrides config)")

    # Subcommands
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", metavar="COMMAND"
    )

    # Initialize commands
    commands = [
        InitCommand(),
        ApplyCommand(),
        DestroyCommand(),
        PreviewCommand(),
        DriftCommand(),
        StateCommand(),
        ConfigCommand(),
        HealthCommand(),
        InsightsCommand(),
        CacheCommand(),
        DiscoverCommand(),
        HealCommand(),
        GenerateCommand(),
        ImportCommand(),
        ServeCommand(),
        VisualizeCommand(),
        MonitorCommand(),
        RemediateCommand(),
        ProviderCommand(),
        RegistryCommand(),
        AuthCommand(),
        CreateTemplateCommand(),
    ]

    # Register each command
    for cmd in commands:
        cmd.register(subparsers)

    return parser


def setup_console(args: argparse.Namespace) -> Console:
    """Setup console output based on arguments"""

    # Determine output format
    if args.format == "json":
        output_format = OutputFormat.JSON
    elif args.format == "yaml":
        output_format = OutputFormat.YAML
    else:
        output_format = OutputFormat.TABLE

    # Determine verbosity
    if args.quiet:
        verbosity = 0
    else:
        # Default to verbosity 1 for better user experience
        verbosity = max(1, args.verbose)

    return Console(format=output_format, no_color=args.no_color, verbosity=verbosity)


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point"""

    if argv is None:
        argv = sys.argv[1:]

    parser = create_parser()

    # Handle no arguments
    if not argv:
        parser.print_help()
        return 0

    try:
        args = parser.parse_args(argv)

        # Setup console
        console = setup_console(args)

        # Load CLI configuration
        config = CLIConfig.load(args.config)

        # Override config with command line arguments
        if args.project:
            config.project = args.project
        if args.environment:
            config.environment = args.environment

        # No command specified
        if not args.command:
            parser.print_help()
            return 0

        # Find and execute command
        commands = {
            "init": InitCommand(),
            "apply": ApplyCommand(),
            "destroy": DestroyCommand(),
            "preview": PreviewCommand(),
            "drift": DriftCommand(),
            "state": StateCommand(),
            "config": ConfigCommand(),
            "health": HealthCommand(),
            "insights": InsightsCommand(),
            "cache": CacheCommand(),
            "discover": DiscoverCommand(),
            "heal": HealCommand(),
            "generate": GenerateCommand(),
            "import": ImportCommand(),
            "serve": ServeCommand(),
            "visualize": VisualizeCommand(),
            "monitor": MonitorCommand(),
            "remediate": RemediateCommand(),
            "provider": ProviderCommand(),
            "registry": RegistryCommand(),
            "auth": AuthCommand(),
            "create": CreateTemplateCommand(),
        }

        if args.command not in commands:
            console.error(f"Unknown command: {args.command}")
            return 1

        command = commands[args.command]

        # Execute command
        return command.execute(args, config, console)

    except KeyboardInterrupt:
        console.error("\\nOperation cancelled by user")
        return 130  # Standard exit code for Ctrl+C

    except InfraDSLCLIError as e:
        console.error(f"Error: {e}")
        if console.verbosity >= 2:
            console.error(traceback.format_exc())
        return 1

    except Exception as e:
        console.error(f"Unexpected error: {e}")
        if console.verbosity >= 1:
            console.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
