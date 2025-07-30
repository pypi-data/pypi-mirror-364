"""
State management commands
"""

from typing import TYPE_CHECKING, Any, Dict, List
from argparse import Namespace
from pathlib import Path
import json
from datetime import datetime

from .base import BaseCommand
from ..utils.errors import CommandError
from ...core.nexus.engine import NexusEngine
from ...core.nexus.resource_tracker import ResourceTracker
from ...core.nexus.provider_registry import get_registry

if TYPE_CHECKING:
    from ..utils.output import Console
    from ..utils.config import CLIConfig


class StateCommand(BaseCommand):
    """Manage infrastructure state"""

    @property
    def name(self) -> str:
        return "state"

    @property
    def description(self) -> str:
        return "Manage infrastructure state"

    def register(self, subparsers) -> None:
        """Register command arguments"""
        parser = subparsers.add_parser(
            self.name, help=self.description, description="Manage infrastructure state"
        )

        subcommands = parser.add_subparsers(dest="state_action", help="State actions")

        # List command
        list_parser = subcommands.add_parser("list", help="List managed resources")
        list_parser.add_argument("--type", help="Filter by resource type")
        list_parser.add_argument("--project", help="Filter by project")
        list_parser.add_argument("--environment", help="Filter by environment")
        list_parser.add_argument("--provider", help="Filter by provider")
        list_parser.add_argument(
            "--discover",
            action="store_true",
            help="Discover resources from cloud providers",
        )

        # Show command
        show_parser = subcommands.add_parser("show", help="Show resource details")
        show_parser.add_argument("resource_name", help="Name of resource to show")

        # Refresh command
        refresh_parser = subcommands.add_parser(
            "refresh", help="Refresh state from providers"
        )
        refresh_parser.add_argument(
            "--all", action="store_true", help="Refresh all resources"
        )
        refresh_parser.add_argument(
            "resource_name", nargs="?", help="Name of specific resource to refresh"
        )

        # Import command
        import_parser = subcommands.add_parser(
            "import", help="Import existing resources"
        )
        import_parser.add_argument("resource_type", help="Type of resource to import")
        import_parser.add_argument(
            "resource_name", help="Name for the imported resource"
        )
        import_parser.add_argument("resource_id", help="Provider-specific resource ID")

        # Remove command
        remove_parser = subcommands.add_parser(
            "remove", help="Remove resource from state"
        )
        remove_parser.add_argument("resource_name", help="Name of resource to remove")
        remove_parser.add_argument(
            "--force", action="store_true", help="Force removal without confirmation"
        )

        self.add_common_arguments(parser)

    def execute(self, args: Namespace, config: "CLIConfig", console: "Console") -> int:
        """Execute the state command"""
        if not args.state_action:
            console.error(
                "No state action specified. Use 'list', 'show', 'refresh', 'import', or 'remove'"
            )
            return 1

        try:
            if args.state_action == "list":
                return self._list_resources(args, config, console)
            elif args.state_action == "show":
                return self._show_resource(args, config, console)
            elif args.state_action == "refresh":
                return self._refresh_state(args, config, console)
            elif args.state_action == "import":
                return self._import_resource(args, config, console)
            elif args.state_action == "remove":
                return self._remove_resource(args, config, console)
            else:
                console.error(f"Unknown state action: {args.state_action}")
                return 1

        except Exception as e:
            raise CommandError(f"Failed to execute state command: {e}")

    def _get_state_file_path(self) -> Path:
        """Get path to state file"""
        # Try to find a project-specific state directory
        state_dir = Path.cwd() / ".infradsl"
        if not state_dir.exists():
            # Check for global state directory
            state_dir = Path.home() / ".infradsl"

        state_dir.mkdir(exist_ok=True)
        return state_dir / "state.json"

    def _load_state(self) -> Dict[str, Any]:
        """Load state from file"""
        state_file = self._get_state_file_path()
        if not state_file.exists():
            return {"resources": {}, "last_updated": None}

        try:
            with open(state_file, "r") as f:
                return json.load(f)
        except Exception:
            # If state file is corrupted, return empty state
            return {"resources": {}, "last_updated": None}

    def _save_state(self, state: Dict[str, Any]) -> None:
        """Save state to file"""
        state_file = self._get_state_file_path()
        state["last_updated"] = datetime.utcnow().isoformat()

        try:
            with open(state_file, "w") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            # Log but don't fail if we can't save state
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to save state: {e}")

    def _discover_resources_from_providers(self, console: "Console") -> Dict[str, Any]:
        """Discover managed resources using context-aware discovery with caching"""
        import os
        import asyncio

        console.info("Starting context-aware resource discovery with caching...")

        try:
            from dotenv import load_dotenv

            load_dotenv()
            console.debug("Loaded environment variables")
        except Exception as e:
            console.debug(f"Failed to load dotenv: {e}")

        try:
            console.debug("Importing discovery engine...")
            from ...core.discovery.context_aware_discovery import (
                create_context_aware_discovery_engine,
                DiscoveryContext,
                DiscoveryScope,
                ContextHint,
            )
            from ...core.interfaces.provider import ProviderConfig, ProviderType

            console.info("Discovery engine imported successfully")
        except Exception as e:
            console.info(f"Failed to import discovery engine: {e}")
            return {}

        # Initialize the context-aware discovery engine
        console.info("Initializing context-aware discovery engine...")
        try:
            # Create a cache-enabled discovery engine with sync-friendly initialization
            from ...core.state.engine import StateEngine

            # Use file-based storage for caching instead of async in-memory
            engine = StateEngine(storage_backend="file")
            console.info("Discovery engine initialized successfully")
        except Exception as e:
            console.info(f"Failed to initialize discovery engine: {e}")
            return {}

        # Register providers with the discovery engine
        providers_registered = 0

        # Try to register DigitalOcean provider
        console.debug("Checking for DigitalOcean provider...")
        try:
            from ...providers.digitalocean import DigitalOceanProvider

            console.debug("Attempting to register DigitalOcean provider")
            token = os.getenv("DIGITALOCEAN_TOKEN")
            if token:
                console.debug("Found DIGITALOCEAN_TOKEN, creating config...")
                config = ProviderConfig(
                    type=ProviderType.DIGITAL_OCEAN,
                    credentials={"token": token},
                    region="nyc1",
                )
                console.debug("Creating DigitalOcean provider instance...")
                provider = DigitalOceanProvider(config=config)
                console.debug(
                    "Registering DigitalOcean provider with discovery engine..."
                )
                engine.register_provider("digitalocean", provider)
                providers_registered += 1
                console.debug("Registered DigitalOcean provider")
            else:
                console.debug("No DIGITALOCEAN_TOKEN found, skipping DigitalOcean")
        except Exception as e:
            console.debug(f"Could not register DigitalOcean provider: {e}")

        # Try to register GCP provider
        console.debug("Checking for GCP provider...")
        try:
            from ...providers.gcp import GCPComputeProvider

            console.debug("Attempting to register GCP provider")

            # Try to auto-discover GCP project from environment
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
            region = os.getenv(
                "GOOGLE_CLOUD_REGION", "us-central1"
            )  # Default to us-central1

            # Try to get project from service account file
            if not project_id:
                try:
                    import json

                    service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                    if service_account_path and os.path.exists(service_account_path):
                        console.debug(
                            f"Reading service account file: {service_account_path}"
                        )
                        with open(service_account_path) as f:
                            creds = json.load(f)
                        project_id = creds.get("project_id")
                        console.debug(
                            f"Found project ID from service account: {project_id}"
                        )
                except Exception as e:
                    console.debug(f"Could not read service account file: {e}")

            if project_id:
                console.debug(
                    f"Creating GCP config with project: {project_id}, region: {region}"
                )
                config = ProviderConfig(
                    type=ProviderType.GCP, project=project_id, region=region
                )
                console.debug("Creating GCP provider instance...")
                provider = GCPComputeProvider(config=config)
                console.debug("Registering GCP provider with discovery engine...")
                engine.register_provider("gcp", provider)
                providers_registered += 1
                console.debug("Registered GCP provider")
            else:
                console.debug("No GCP project ID found, skipping GCP")

        except Exception as e:
            console.debug(f"Could not register GCP provider: {e}")

        # Try to register AWS provider
        console.debug("Checking for AWS provider...")
        try:
            from ...providers.aws_provider import AWSProvider

            console.debug("Attempting to register AWS provider")

            # AWS credentials come from environment, IAM role, or AWS profile
            console.debug("Creating AWS config...")
            config = ProviderConfig(
                type=ProviderType.AWS, region=os.getenv("AWS_REGION", "us-east-1")
            )
            console.debug("Creating AWS provider instance...")
            provider = AWSProvider(config)
            console.debug("Registering AWS provider with discovery engine...")
            engine.register_provider("aws", provider)
            providers_registered += 1
            console.debug("Registered AWS provider")

        except Exception as e:
            console.debug(f"Could not register AWS provider: {e}")

        if providers_registered == 0:
            console.info("No providers registered, returning empty result")
            return {}

        console.info(f"Successfully registered {providers_registered} providers")

        # Use the state engine for discovery with caching
        console.info("Starting file-cached resource discovery...")
        try:
            console.info("About to call engine.discover_all_resources...")

            # Use the state engine's discovery which now has file-based caching
            discovered_resources = engine.discover_all_resources(
                update_storage=True, timeout=15  # Enable storage for caching
            )

            console.info(f"Total discovered resources: {len(discovered_resources)}")
            console.info("Resource discovery completed successfully")
            return discovered_resources
        except Exception as e:
            console.debug(f"Error during resource discovery: {e}")
            import traceback

            console.debug(f"Exception details: {traceback.format_exc()}")
            return {}

    def _list_resources(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """List managed resources"""
        console.info("Listing managed resources...")

        # ALWAYS query cloud providers first (stateless principle)
        console.info("About to start cloud provider discovery...")
        try:
            resources = self._discover_resources_from_providers(console)
            console.info(f"Discovery completed, found {len(resources)} resources")
        except Exception as e:
            console.info(f"Discovery failed: {e}")
            import traceback

            console.info(f"Traceback: {traceback.format_exc()}")
            resources = {}

        if not resources:
            console.info("No managed resources found")
            return 0

        # Convert to list format
        resource_list = list(resources.values())

        # Apply filters
        if args.type:
            resource_list = [r for r in resource_list if r.get("type") == args.type]

        if args.project:
            resource_list = [
                r for r in resource_list if r.get("project") == args.project
            ]

        if args.environment:
            resource_list = [
                r for r in resource_list if r.get("environment") == args.environment
            ]

        if args.provider:
            resource_list = [
                r for r in resource_list if r.get("provider") == args.provider
            ]

        if not resource_list:
            console.info("No resources found matching criteria")
            return 0

        # Display resources
        self._display_resource_list(resource_list, console)

        return 0

    def _show_resource(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Show detailed resource information"""
        resource_name = args.resource_name

        console.info(f"Showing resource: {resource_name}")

        # Load state and find resource
        state = self._load_state()
        resources = state.get("resources", {})

        if resource_name not in resources:
            # Try to discover the resource
            with console.status(f"Looking for resource {resource_name}..."):
                discovered = self._discover_resources_from_providers(console)

            if resource_name in discovered:
                resource = discovered[resource_name]
                # Save to state
                resources[resource_name] = resource
                state["resources"] = resources
                self._save_state(state)
            else:
                console.error(f"Resource not found: {resource_name}")
                console.info(
                    "Use 'infra state list --discover' to scan for managed resources"
                )
                return 1
        else:
            resource = resources[resource_name]

        # Display resource details
        self._display_resource_details(resource, console)

        return 0

    def _refresh_state(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Refresh state from providers"""
        if args.all:
            console.info("Refreshing all resources...")
        else:
            console.info(f"Refreshing resource: {args.resource_name}")

        # Initialize tracker and engine
        tracker = ResourceTracker()
        engine = NexusEngine()

        if args.all:
            # Refresh all resources
            resources = tracker.list_resources()
            refreshed_count = 0
            failed_count = 0

            for resource_info in resources:
                try:
                    with console.status(f"Refreshing {resource_info['name']}..."):
                        success = self._refresh_resource(resource_info, engine, tracker)

                    if success:
                        console.success(f"Refreshed {resource_info['name']}")
                        refreshed_count += 1
                    else:
                        console.error(f"Failed to refresh {resource_info['name']}")
                        failed_count += 1

                except Exception as e:
                    console.error(f"Error refreshing {resource_info['name']}: {e}")
                    failed_count += 1

            console.info(
                f"Refresh completed: {refreshed_count} refreshed, {failed_count} failed"
            )
            return 1 if failed_count > 0 else 0

        else:
            # Refresh specific resource
            resource_name = args.resource_name
            resource = tracker.get_resource(resource_name)

            if not resource:
                console.error(f"Resource not found: {resource_name}")
                return 1

            with console.status(f"Refreshing {resource_name}..."):
                success = self._refresh_resource(resource, engine, tracker)

            if success:
                console.success(f"Refreshed {resource_name}")
                return 0
            else:
                console.error(f"Failed to refresh {resource_name}")
                return 1

    def _import_resource(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Import existing resource into state"""
        resource_type = args.resource_type
        resource_name = args.resource_name
        resource_id = args.resource_id

        console.info(
            f"Importing {resource_type} resource: {resource_name} (ID: {resource_id})"
        )

        # Initialize tracker and engine
        tracker = ResourceTracker()
        engine = NexusEngine()

        try:
            with console.status(f"Importing {resource_name}..."):
                success = self._import_resource_from_provider(
                    resource_type, resource_name, resource_id, engine, tracker
                )

            if success:
                console.success(f"Imported {resource_name}")
                return 0
            else:
                console.error(f"Failed to import {resource_name}")
                return 1

        except Exception as e:
            console.error(f"Error importing {resource_name}: {e}")
            return 1

    def _remove_resource(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Remove resource from state"""
        resource_name = args.resource_name

        console.info(f"Removing resource from state: {resource_name}")

        # Initialize tracker
        tracker = ResourceTracker()

        # Check if resource exists
        resource = tracker.get_resource(resource_name)

        if not resource:
            console.error(f"Resource not found: {resource_name}")
            return 1

        # Confirm removal
        if not args.force:
            console.warning(f"This will remove {resource_name} from state management")
            console.warning("The actual resource will NOT be destroyed")
            if not console.confirm("Continue?"):
                console.info("Removal cancelled")
                return 0

        try:
            success = tracker.remove_resource(resource_name)

            if success:
                console.success(f"Removed {resource_name} from state")
                return 0
            else:
                console.error(f"Failed to remove {resource_name} from state")
                return 1

        except Exception as e:
            console.error(f"Error removing {resource_name}: {e}")
            return 1

    def _display_resource_list(
        self, resources: List[Dict[str, Any]], console: "Console"
    ) -> None:
        """Display a list of resources in table format"""
        if not resources:
            return

        console.info(f"\nFound {len(resources)} managed resources:")
        console.info("")

        # Table headers
        headers = ["NAME", "TYPE", "PROVIDER", "STATE", "PROJECT", "ENVIRONMENT"]
        console.info("  ".join(f"{h:<15}" for h in headers))
        console.info("  ".join("-" * 15 for _ in headers))

        # Table rows
        for resource in sorted(resources, key=lambda x: x.get("name", "") or ""):
            row = [
                (resource.get("name") or "")[:15],
                (resource.get("type") or "")[:15],
                (resource.get("provider") or "")[:15],
                (resource.get("state") or "")[:15],
                (resource.get("project") or "")[:15],
                (resource.get("environment") or "")[:15],
            ]
            console.info("  ".join(f"{col:<15}" for col in row))

        console.info("")

    def _display_resource_details(
        self, resource: Dict[str, Any], console: "Console"
    ) -> None:
        """Display detailed resource information"""
        console.info("")
        console.info("=" * 60)
        console.info(f"Resource: {resource.get('name', 'Unknown')}")
        console.info("=" * 60)

        # Basic information
        console.info(f"  Type: {resource.get('type', 'Unknown')}")
        console.info(f"  ID: {resource.get('id', 'Unknown')}")
        console.info(f"  Provider: {resource.get('provider', 'Unknown')}")
        console.info(f"  Provider ID: {resource.get('provider_id', 'Unknown')}")
        console.info(f"  State: {resource.get('state', 'Unknown')}")

        # Project/Environment
        if resource.get("project"):
            console.info(f"  Project: {resource['project']}")
        if resource.get("environment"):
            console.info(f"  Environment: {resource['environment']}")

        # Network information
        if resource.get("ip_address"):
            console.info(f"  Public IP: {resource['ip_address']}")
        if resource.get("private_ip_address"):
            console.info(f"  Private IP: {resource['private_ip_address']}")
        if resource.get("region"):
            console.info(f"  Region: {resource['region']}")

        # Size/Configuration
        if resource.get("size"):
            console.info(f"  Size: {resource['size']}")
        if resource.get("image"):
            console.info(f"  Image: {resource['image']}")

        # Timestamps
        if resource.get("created_at"):
            console.info(f"  Created: {resource['created_at']}")
        if resource.get("discovered_at"):
            console.info(f"  Discovered: {resource['discovered_at']}")

        # Configuration
        config = resource.get("configuration", {})
        if config:
            console.info("  Configuration:")
            for key, value in config.items():
                console.info(f"    {key}: {value}")

        # Tags
        tags = resource.get("tags", [])
        if tags:
            console.info("  Tags:")
            for tag in sorted(tags):
                console.info(f"    - {tag}")

        console.info("=" * 60)
        console.info("")

    def _refresh_resource(
        self,
        resource_info: Dict[str, Any],
        engine: NexusEngine,
        tracker: ResourceTracker,
    ) -> bool:
        """Refresh a single resource"""
        try:
            # Get current state from provider
            current_state = engine.get_resource_state(resource_info["name"])

            if current_state:
                # Update tracked resource
                tracker.update_resource(resource_info["name"], current_state)
                return True
            else:
                # Resource not found in provider
                tracker.mark_resource_missing(resource_info["name"])
                return False

        except Exception:
            return False

    def _import_resource_from_provider(
        self,
        resource_type: str,
        resource_name: str,
        resource_id: str,
        engine: NexusEngine,
        tracker: ResourceTracker,
    ) -> bool:
        """Import a resource from provider"""
        try:
            # Get resource details from provider
            resource_details = engine.get_resource_by_id(resource_type, resource_id)

            if resource_details:
                # Add to tracker
                tracker.add_resource(resource_name, resource_type, resource_details)
                return True
            else:
                return False

        except Exception:
            return False
