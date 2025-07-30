"""
Preview infrastructure changes
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List
from argparse import Namespace

from .base import BaseCommand
from ..utils.errors import CommandError
from ...core.nexus.reconciler import StateReconciler
from ...core.services.state_detection import create_state_detector

# Import modular components
from .preview_modules import (
    CacheLookup,
    StateComparison,
    ResourceLoader,
    PreviewDisplay,
    ProviderConfig,
)
from .apply.planner import ChangePlanner

if TYPE_CHECKING:
    from ..utils.output import Console
    from ..utils.config import CLIConfig


class PreviewCommand(BaseCommand):
    """Preview infrastructure changes without applying them"""

    def __init__(self):
        # Initialize modular components
        self.cache_lookup = CacheLookup()
        self.state_comparison = StateComparison()
        self.resource_loader = ResourceLoader()
        self.display = PreviewDisplay()
        self.provider_config = ProviderConfig()
        # Use the fixed ChangePlanner for accurate planning
        self.change_planner = ChangePlanner()

    @property
    def name(self) -> str:
        return "preview"

    @property
    def description(self) -> str:
        return "Preview infrastructure changes without applying them"

    def register(self, subparsers) -> None:
        """Register command arguments"""
        parser = subparsers.add_parser(
            self.name,
            help=self.description,
            description="Preview infrastructure changes without applying them",
        )

        parser.add_argument("file", type=Path, help="Infrastructure file to preview")

        parser.add_argument(
            "--summary-only",
            action="store_true",
            help="Show only summary, skip detailed resource configurations",
        )

        parser.add_argument(
            "--target",
            action="append",
            help="Target specific resources (can be used multiple times)",
        )

        parser.add_argument(
            "--refresh", action="store_true", help="Refresh state before previewing"
        )

        self.add_common_arguments(parser)

    def execute(self, args: Namespace, config: "CLIConfig", console: "Console") -> int:
        """Execute the preview command"""
        infrastructure_file = args.file

        if not infrastructure_file.exists():
            console.error(f"Infrastructure file not found: {infrastructure_file}")
            return 1

        console.info(
            f"📋 Previewing infrastructure from: [cyan]{infrastructure_file}[/cyan]"
        )

        try:
            # Load and parse infrastructure file using modular component
            resources = self.resource_loader.load_infrastructure(
                infrastructure_file, console
            )

            if not resources:
                console.info("No resources found to preview")
                return 0

            # Initialize reconciler
            reconciler = StateReconciler()

            # Filter resources by target if specified using modular component
            if args.target:
                resources = self.resource_loader.filter_resources(
                    resources, args.target, console
                )
                console.info(
                    f"🎯 Targeting {len(resources)} resources: {', '.join(args.target)}"
                )

            # Preview changes
            console.info("🔍 Analyzing infrastructure changes...")

            with console.status("Planning changes..."):
                changes = self.change_planner.plan_changes(resources, reconciler, console)

            # Check if there are actually any changes
            total_changes = sum(len(resources) for resources in changes.values())
            if total_changes == 0:
                console.success("No changes needed. Infrastructure is up to date.")
                return 0

            # Display changes using modular component
            self.display.display_preview_summary(changes, console)

            # Display resource details by default (unless summary-only is requested)
            if not args.summary_only:
                self._display_resource_details(resources, console)

            # Display summary
            self._display_summary(changes, console)

            return 0

        except Exception as e:
            raise CommandError(f"Failed to preview infrastructure: {e}")

    # Note: _load_infrastructure and _filter_resources methods moved to ResourceLoader module

    def _plan_changes(
            self, resources: List[Any], reconciler: StateReconciler, console: "Console"
    ) -> Dict[str, List[Any]]:
        """Plan infrastructure changes"""
        changes = {"create": [], "update": [], "delete": [], "replace": []}

        for resource in resources:
            # Get current state from provider
            current_state = self._get_current_state(resource)
            desired_state = self.provider_config.extract_provider_config(resource)

            # Determine required action using modular components
            if current_state is None:
                changes["create"].append(resource)
            elif self.state_comparison.needs_replacement(current_state, desired_state):
                changes["replace"].append(resource)
            elif self.state_comparison.needs_update(current_state, desired_state):
                changes["update"].append(resource)
            # If no changes needed, resource is not included

        console.debug(
            f"Planned changes: {len(changes['create'])} create, {len(changes['update'])} update, {len(changes['replace'])} replace"
        )
        return changes

    def _get_current_state(self, resource: Any) -> Dict[str, Any] | None:
        """Get current state of resource from provider using universal state detection"""
        try:
            # First check cache for imported resources using modular component
            cache_state = self.cache_lookup.get_cached_state_sync(resource)
            if cache_state is not None:
                import logging

                logger = logging.getLogger(__name__)
                logger.debug(f"Found cached state for resource {resource.name}")
                return cache_state

            # Check if a resource has a provider attached
            if hasattr(resource, "_provider") and resource._provider:
                # Use universal state detector
                state_detector = create_state_detector(resource._provider)
                return state_detector.get_current_state(resource)

            return None
        except Exception as e:
            # Log the error but don't fail - assume resource doesn't exist
            import logging

            logger = logging.getLogger(__name__)
            logger.debug(f"Error checking current state for {resource.name}: {e}")
            return None

    # Note: _get_cached_state moved to CacheLookup module

    # Note: Cache lookup methods moved to CacheLookup module

    # Note: Cache helper methods moved to CacheLookup module

    # Note: _get_desired_state moved to the ProviderConfig module (called via extract_provider_config)

    # Note: Provider config methods moved to ProviderConfig module

    # Note: State comparison methods moved to StateComparison module

    def _display_changes(
            self, changes: Dict[str, List[Any]], console: "Console", detailed: bool = False
    ) -> None:
        """Display planned changes"""
        total_changes = sum(len(resources) for resources in changes.values())

        if total_changes == 0:
            return

        console.info("")
        console.info(f"📋 Planned Infrastructure Changes ({total_changes} total)")
        console.info("─" * 60)

        # Display creates
        if changes["create"]:
            console.success(f"  ✅ {len(changes['create'])} resource(s) to create:")
            for resource in changes["create"]:
                console.info(f"     ➕ {resource.name}")
                console.info(f"        Type: {resource._resource_type}")
                if detailed:
                    # Show configuration for new resources
                    desired_state = self.provider_config.extract_provider_config(
                        resource
                    )
                    self._display_resource_details_inline(
                        desired_state, console, indent="        "
                    )
            console.info("")

        # Display updates
        if changes["update"]:
            console.info(f"  🔄 {len(changes['update'])} resource(s) to update:")
            for resource in changes["update"]:
                console.info(f"     📝 {resource.name}")
                console.info(f"        Type: {resource._resource_type}")
                # Always show what's changing in updates
                current_state = self._get_current_state(resource)
                desired_state = self._get_desired_state(resource)
                if current_state is not None:
                    self._display_diff(
                        current_state, desired_state, console, indent="        "
                    )
            console.info("")

        # Display replacements
        if changes["replace"]:
            console.warning(f"  🔄 {len(changes['replace'])} resource(s) to replace:")
            for resource in changes["replace"]:
                console.info(f"     🔄 {resource.name}")
                console.info(f"        Type: {resource._resource_type}")
                console.warning(f"        ⚠️  Will be destroyed and recreated")
                if detailed:
                    # Show what's changing for replacements
                    current_state = self._get_current_state(resource)
                    desired_state = self.provider_config.extract_provider_config(
                        resource
                    )
                    if current_state is not None:
                        self._display_diff(
                            current_state, desired_state, console, indent="        "
                        )
            console.info("")

        # Display deletes
        if changes["delete"]:
            console.warning(f"  🗑️  {len(changes['delete'])} resource(s) to delete:")
            for resource in changes["delete"]:
                console.info(f"     ❌ {resource.name}")
                console.info(f"        Type: {resource._resource_type}")
                console.warning(f"        ⚠️  Will be permanently deleted")
            console.info("")

    def _display_resource_config(
            self, resource: Any, console: "Console", indent: str = ""
    ) -> None:
        """Display resource configuration"""
        config = resource.to_dict()

        for key, value in config.items():
            if key.startswith("_"):
                continue

            if key == "spec" and isinstance(value, dict):
                console.info(f"{indent}{key}:")
                self._display_spec_details(value, console, indent + "  ")
            else:
                console.info(f"{indent}{key}: {value}")

    def _display_spec_details(
            self, spec: Dict[str, Any], console: "Console", indent: str = ""
    ) -> None:
        """Display spec details in a formatted way"""
        for key, value in spec.items():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                # Handle complex list items like additional_disks
                console.info(f"{indent}{key}:")
                for i, item in enumerate(value):
                    console.info(f"{indent}  - {i + 1}:")
                    for k, v in item.items():
                        console.info(f"{indent}    {k}: {v}")
            elif isinstance(value, list):
                console.info(f"{indent}{key}: {', '.join(str(v) for v in value)}")
            else:
                console.info(f"{indent}{key}: {value}")

    def _display_resource_details(
            self, resources: List[Any], console: "Console"
    ) -> None:
        """Display detailed resource configurations"""
        console.info("")
        console.info("📄 Resource Configuration Details")
        console.info("═" * 60)

        for i, resource in enumerate(resources, 1):
            console.info("")
            console.info(f"┌─ Resource {i}/{len(resources)}: {resource.name}")
            console.info(f"│  Type: {resource._resource_type}")

            # Handle provider display for both string and object providers
            provider_display = "Unknown"
            if hasattr(resource, "_provider") and resource._provider:
                if isinstance(resource._provider, str):
                    provider_display = resource._provider.upper()
                elif hasattr(resource._provider, "config"):
                    provider_display = (
                        resource._provider.config.type.value
                        if hasattr(resource._provider.config.type, "value")
                        else str(resource._provider.config.type)
                    )

            console.info(f"│  Provider: {provider_display}")
            console.info("├─ Configuration:")
            self._display_resource_config_enhanced(resource, console, "│    ")
            console.info("└─" + "─" * 55)

    def _display_resource_config_enhanced(
            self, resource: Any, console: "Console", indent: str = ""
    ) -> None:
        """Display enhanced resource configuration"""
        config = resource.to_dict()

        # Filter out internal fields and organize by importance
        important_fields = [
            "name",
            "type",
            "custom_domains",
            "existing_bucket",
            "existing_zone",
        ]
        technical_fields = [
            "config",
            "reference_distribution_id",
            "auto_ssl_certificate",
        ]

        # Show important fields first
        for field in important_fields:
            if field in config and config[field] is not None:
                self._display_config_field(field, config[field], console, indent)

        # Show technical configuration
        if any(field in config for field in technical_fields):
            console.info(f"{indent}Technical Configuration:")
            for field in technical_fields:
                if field in config and config[field] is not None:
                    self._display_config_field(
                        field, config[field], console, indent + "  "
                    )

        # Show other fields
        shown_fields = set(important_fields + technical_fields + ["_provider"])
        remaining_fields = {
            k: v
            for k, v in config.items()
            if k not in shown_fields and not k.startswith("_") and v is not None
        }

        if remaining_fields:
            console.info(f"{indent}Additional Configuration:")
            for field, value in remaining_fields.items():
                self._display_config_field(field, value, console, indent + "  ")

    def _display_config_field(
            self, field: str, value: Any, console: "Console", indent: str = ""
    ) -> None:
        """Display a single configuration field with proper formatting"""
        if isinstance(value, dict):
            if not value:
                console.info(f"{indent}{field}: (empty)")
                return
            # Show important fields from config dict
            if field == "config":
                # Extract key information from config
                key_info = []
                if "custom_domains" in value and value["custom_domains"]:
                    key_info.append(f"domains: {', '.join(value['custom_domains'])}")
                if "existing_bucket" in value and value["existing_bucket"]:
                    key_info.append(f"bucket: {value['existing_bucket']}")
                if "existing_zone" in value and value["existing_zone"]:
                    key_info.append(f"zone: {value['existing_zone']}")
                if (
                        "reference_distribution_id" in value
                        and value["reference_distribution_id"]
                ):
                    key_info.append(
                        f"copying from: {value['reference_distribution_id']}"
                    )
                if "auto_ssl_certificate" in value and value["auto_ssl_certificate"]:
                    key_info.append("auto SSL: enabled")

                if key_info:
                    console.info(f"{indent}{field}: {' | '.join(key_info)}")
                else:
                    console.info(f"{indent}{field}: (standard configuration)")
            else:
                console.info(f"{indent}{field}:")
                for k, v in value.items():
                    if v is not None:
                        console.info(f"{indent}  {k}: {v}")
        elif isinstance(value, list):
            if not value:
                console.info(f"{indent}{field}: []")
            elif len(value) <= 3:
                console.info(f"{indent}{field}: {value}")
            else:
                console.info(f"{indent}{field}: [{len(value)} items]")
        else:
            console.info(f"{indent}{field}: {value}")

    def _display_summary(
            self, changes: Dict[str, List[Any]], console: "Console"
    ) -> None:
        """Display summary of changes"""
        create_count = len(changes["create"])
        update_count = len(changes["update"])
        replace_count = len(changes["replace"])
        delete_count = len(changes["delete"])

        console.info("")
        console.info("📊 Infrastructure Change Summary")
        console.info("╭─" + "─" * 58 + "─╮")
        console.info("│                                                            │")

        if create_count > 0:
            console.success(
                f"│  ✅ Create: {create_count} resource(s)                               │"
            )
        if update_count > 0:
            console.info(
                f"│  📝 Update: {update_count} resource(s)                               │"
            )
        if replace_count > 0:
            console.warning(
                f"│  🔄 Replace: {replace_count} resource(s)                             │"
            )
        if delete_count > 0:
            console.warning(
                f"│  🗑️  Delete: {delete_count} resource(s)                              │"
            )

        console.info("│                                                            │")

        # Estimate cost and time
        estimated_time = self._estimate_time(changes)
        minutes = estimated_time // 60
        seconds = estimated_time % 60
        time_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
        console.info(f"│  ⏱️  Estimated execution time: {time_str:<25}  │")

        console.info("│                                                            │")
        console.info("╰─" + "─" * 58 + "─╯")

        # Show warnings
        if replace_count > 0 or delete_count > 0:
            console.info("")
            console.warning("⚠️  Important Warnings:")
            if replace_count > 0:
                console.warning(
                    f"   • {replace_count} resource(s) will be destroyed and recreated"
                )
            if delete_count > 0:
                console.warning(
                    f"   • {delete_count} resource(s) will be permanently deleted"
                )

        console.info("")
        console.info("💡 Next steps:")
        console.info("   • Review the changes above carefully")
        console.info("   • Run 'infra apply' to execute these changes")
        console.info("   • Use 'infra apply --dry-run' to validate without executing")
        console.info("")

    def _estimate_time(self, changes: Dict[str, List[Any]]) -> int:
        """Estimate time to apply changes"""
        # Simple estimation based on resource counts
        create_time = len(changes["create"]) * 30  # 30s per create
        update_time = len(changes["update"]) * 15  # 15s per update
        replace_time = len(changes["replace"]) * 45  # 45s per replace (delete + create)
        delete_time = len(changes["delete"]) * 10  # 10s per delete

        return create_time + update_time + replace_time + delete_time

    def _display_resource_details_inline(
            self, state: Dict[str, Any], console: "Console", indent: str = ""
    ) -> None:
        """Display resource configuration details"""
        # Show key configuration fields
        key_fields = [
            "region",
            "size",
            "image",
            "backups",
            "ipv6",
            "monitoring",
            "tags",
        ]
        for field in key_fields:
            if field in state and state[field] is not None:
                if field == "tags" and isinstance(state[field], list):
                    if state[field]:
                        console.info(f"{indent}{field}:")
                        for tag in sorted(state[field]):
                            console.info(f"{indent}  - {tag}")
                    else:
                        console.info(f"{indent}{field}: []")
                else:
                    console.info(f"{indent}{field}: {state[field]}")

    def _display_diff(
            self,
            current: Dict[str, Any],
            desired: Dict[str, Any],
            console: "Console",
            indent: str = "",
    ) -> None:
        """Display detailed diff between current and desired state"""
        # Compare key fields
        key_fields = [
            "region",
            "size",
            "image",
            "backups",
            "ipv6",
            "monitoring",
            "tags",
            "additional_disks",
        ]

        for field in key_fields:
            current_val = current.get(field)
            desired_val = desired.get(field)

            if current_val != desired_val:
                if field == "tags":
                    self._display_tags_diff(
                        current_val or [], desired_val or [], console, indent
                    )
                elif field == "additional_disks":
                    self._display_disks_diff(
                        current_val or [], desired_val or [], console, indent
                    )
                else:
                    console.info(f"{indent}{field}: {current_val} -> {desired_val}")

    def _display_tags_diff(
            self,
            current_tags: List[str],
            desired_tags: List[str],
            console: "Console",
            indent: str = "",
    ) -> None:
        """Display detailed tags diff"""
        current_set = set(current_tags)
        desired_set = set(desired_tags)

        # Tags to remove
        to_remove = current_set - desired_set
        # Tags to add
        to_add = desired_set - current_set

        if to_remove or to_add:
            console.info(f"{indent}tags:")

            if to_remove:
                for tag in sorted(to_remove):
                    console.info(f"{indent}  - {tag}")

            if to_add:
                for tag in sorted(to_add):
                    console.info(f"{indent}  + {tag}")

            # Show unchanged tags if verbose
            if console.verbosity >= 2:
                unchanged = current_set & desired_set
                if unchanged:
                    console.info(f"{indent}  (unchanged: {sorted(unchanged)})")

    def _display_disks_diff(
            self,
            current_disks: List[Dict[str, Any]],
            desired_disks: List[Dict[str, Any]],
            console: "Console",
            indent: str = "",
    ) -> None:
        """Display detailed additional disks diff"""

        # Convert to readable strings for comparison
        def disk_to_string(disk):
            size = disk.get("size_gb", "unknown")
            disk_type = disk.get("type", "ssd")
            mount = disk.get("mount_point")
            return f"{size}GB {disk_type}" + (f" at {mount}" if mount else "")

        current_disk_strings = {disk_to_string(disk) for disk in current_disks}
        desired_disk_strings = {disk_to_string(disk) for disk in desired_disks}

        # Disks to remove
        to_remove = current_disk_strings - desired_disk_strings
        # Disks to add
        to_add = desired_disk_strings - current_disk_strings

        if to_remove or to_add:
            console.info(f"{indent}additional_disks:")

            if to_remove:
                for disk in sorted(to_remove):
                    console.info(f"{indent}  - {disk}")

            if to_add:
                for disk in sorted(to_add):
                    console.info(f"{indent}  + {disk}")
