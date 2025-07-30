"""
Configuration management commands
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List
from argparse import Namespace

from .base import BaseCommand
from ..utils.errors import CommandError, ConfigurationError
from ..utils.config import CLIConfig

if TYPE_CHECKING:
    from ..utils.output import Console


class ConfigCommand(BaseCommand):
    """Manage InfraDSL configuration"""

    @property
    def name(self) -> str:
        return "config"

    @property
    def description(self) -> str:
        return "Manage InfraDSL configuration"

    def register(self, subparsers) -> None:
        """Register command arguments"""
        parser = subparsers.add_parser(
            self.name,
            help=self.description,
            description="Manage InfraDSL configuration",
        )

        subcommands = parser.add_subparsers(
            dest="config_action", help="Configuration actions"
        )

        # Show command
        show_parser = subcommands.add_parser("show", help="Show current configuration")
        show_parser.add_argument("--key", help="Show specific configuration key")

        # Set command
        set_parser = subcommands.add_parser("set", help="Set configuration value")
        set_parser.add_argument("key", help="Configuration key to set")
        set_parser.add_argument("value", help="Value to set")

        # Unset command
        unset_parser = subcommands.add_parser("unset", help="Unset configuration value")
        unset_parser.add_argument("key", help="Configuration key to unset")

        # Init command
        init_parser = subcommands.add_parser("init", help="Initialize configuration")
        init_parser.add_argument(
            "--force",
            action="store_true",
            help="Force initialization even if config exists",
        )

        # Validate command
        validate_parser = subcommands.add_parser(
            "validate", help="Validate configuration"
        )
        validate_parser.add_argument(
            "--file", type=Path, help="Configuration file to validate"
        )

        self.add_common_arguments(parser)

    def execute(self, args: Namespace, config: "CLIConfig", console: "Console") -> int:
        """Execute the config command"""
        if not args.config_action:
            console.error(
                "No config action specified. Use 'show', 'set', 'unset', 'init', or 'validate'"
            )
            return 1

        try:
            if args.config_action == "show":
                return self._show_config(args, config, console)
            elif args.config_action == "set":
                return self._set_config(args, config, console)
            elif args.config_action == "unset":
                return self._unset_config(args, config, console)
            elif args.config_action == "init":
                return self._init_config(args, config, console)
            elif args.config_action == "validate":
                return self._validate_config(args, config, console)
            else:
                console.error(f"Unknown config action: {args.config_action}")
                return 1

        except Exception as e:
            raise CommandError(f"Failed to execute config command: {e}")

    def _show_config(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Show current configuration"""
        if args.key:
            # Show specific key
            value = self._get_config_value(config, args.key)
            if value is not None:
                console.output({args.key: value})
                return 0
            else:
                console.error(f"Configuration key not found: {args.key}")
                return 1
        else:
            # Show all configuration
            config_dict = self._config_to_dict(config)
            console.output(config_dict, "Current Configuration")
            return 0

    def _set_config(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Set configuration value"""
        key = args.key
        value = args.value

        try:
            # Parse value if it's a known type
            parsed_value = self._parse_config_value(value)

            # Set the value
            self._set_config_value(config, key, parsed_value)

            # Save configuration
            config.save()

            console.success(f"Set {key} = {parsed_value}")
            return 0

        except Exception as e:
            console.error(f"Failed to set configuration: {e}")
            return 1

    def _unset_config(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Unset configuration value"""
        key = args.key

        try:
            # Check if key exists
            if not self._has_config_key(config, key):
                console.error(f"Configuration key not found: {key}")
                return 1

            # Unset the value
            self._unset_config_value(config, key)

            # Save configuration
            config.save()

            console.success(f"Unset {key}")
            return 0

        except Exception as e:
            console.error(f"Failed to unset configuration: {e}")
            return 1

    def _init_config(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Initialize configuration"""
        config_path = Path.cwd() / "infradsl.yaml"

        if config_path.exists() and not args.force:
            console.error(f"Configuration file already exists: {config_path}")
            console.info("Use --force to overwrite")
            return 1

        try:
            # Create default configuration
            default_config = CLIConfig()

            # Interactive setup
            console.info("Initializing InfraDSL configuration...")

            # Get project name
            project = console.input("Project name", default_config.project)
            if project:
                default_config.project = project

            # Get environment
            environment = console.input(
                "Environment", default_config.environment or "dev"
            )
            if environment:
                default_config.environment = environment

            # Get default region
            region = console.input(
                "Default region", default_config.default_region or "us-west-2"
            )
            if region:
                default_config.default_region = region

            # Save configuration
            default_config.save(config_path)

            console.success(f"Configuration initialized: {config_path}")
            return 0

        except Exception as e:
            console.error(f"Failed to initialize configuration: {e}")
            return 1

    def _validate_config(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Validate configuration"""
        config_file = args.file

        if config_file:
            # Validate specific file
            if not config_file.exists():
                console.error(f"Configuration file not found: {config_file}")
                return 1

            try:
                test_config = CLIConfig.load(config_file)
                console.success(f"Configuration file is valid: {config_file}")
                return 0
            except Exception as e:
                console.error(f"Configuration file is invalid: {e}")
                return 1
        else:
            # Validate current configuration
            try:
                errors = self._validate_config_object(config)
                if errors:
                    console.error("Configuration validation failed:")
                    for error in errors:
                        console.error(f"  - {error}")
                    return 1
                else:
                    console.success("Configuration is valid")
                    return 0
            except Exception as e:
                console.error(f"Configuration validation failed: {e}")
                return 1

    def _config_to_dict(self, config: "CLIConfig") -> Dict[str, Any]:
        """Convert config object to dictionary"""
        return {
            "project": config.project,
            "environment": config.environment,
            "default_region": config.default_region,
            "default_output_format": config.default_output_format,
            "auto_approve": config.auto_approve,
            "timeout": config.timeout,
            "provider_configs": config.provider_configs or {},
        }

    def _get_config_value(self, config: "CLIConfig", key: str) -> Any:
        """Get configuration value by key"""
        if key == "project":
            return config.project
        elif key == "environment":
            return config.environment
        elif key == "default_region":
            return config.default_region
        elif key == "default_output_format":
            return config.default_output_format
        elif key == "auto_approve":
            return config.auto_approve
        elif key == "timeout":
            return config.timeout
        elif key.startswith("provider_configs."):
            provider = key.split(".", 1)[1]
            return config.get_provider_config(provider)
        else:
            return None

    def _set_config_value(self, config: "CLIConfig", key: str, value: Any) -> None:
        """Set configuration value by key"""
        if key == "project":
            config.project = value
        elif key == "environment":
            config.environment = value
        elif key == "default_region":
            config.default_region = value
        elif key == "default_output_format":
            config.default_output_format = value
        elif key == "auto_approve":
            config.auto_approve = bool(value)
        elif key == "timeout":
            config.timeout = int(value)
        elif key.startswith("provider_configs."):
            provider = key.split(".", 1)[1]
            if isinstance(value, dict):
                config.set_provider_config(provider, value)
            else:
                raise ConfigurationError(f"Provider config must be a dictionary: {key}")
        else:
            raise ConfigurationError(f"Unknown configuration key: {key}")

    def _unset_config_value(self, config: "CLIConfig", key: str) -> None:
        """Unset configuration value by key"""
        if key == "project":
            config.project = None
        elif key == "environment":
            config.environment = None
        elif key == "default_region":
            config.default_region = None
        elif key == "default_output_format":
            config.default_output_format = "table"
        elif key == "auto_approve":
            config.auto_approve = False
        elif key == "timeout":
            config.timeout = 300
        elif key.startswith("provider_configs."):
            provider = key.split(".", 1)[1]
            if config.provider_configs and provider in config.provider_configs:
                del config.provider_configs[provider]
        else:
            raise ConfigurationError(f"Unknown configuration key: {key}")

    def _has_config_key(self, config: "CLIConfig", key: str) -> bool:
        """Check if configuration key exists"""
        return self._get_config_value(config, key) is not None

    def _parse_config_value(self, value: str) -> Any:
        """Parse configuration value from string"""
        # Try to parse as boolean
        if value.lower() in ("true", "false"):
            return value.lower() == "true"

        # Try to parse as integer
        try:
            return int(value)
        except ValueError:
            pass

        # Try to parse as float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value

    def _validate_config_object(self, config: "CLIConfig") -> List[str]:
        """Validate configuration object"""
        errors = []

        # Validate output format
        if config.default_output_format not in ("table", "json", "yaml"):
            errors.append(f"Invalid output format: {config.default_output_format}")

        # Validate timeout
        if config.timeout <= 0:
            errors.append(f"Timeout must be positive: {config.timeout}")

        # Validate provider configs
        if config.provider_configs:
            for provider, provider_config in config.provider_configs.items():
                if not isinstance(provider_config, dict):
                    errors.append(f"Provider config must be a dictionary: {provider}")

        return errors
