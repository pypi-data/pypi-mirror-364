"""
Change Displayer - handles formatting and displaying changes to the user
"""

from typing import TYPE_CHECKING, Any, Dict, List

from .state_analyzer import StateAnalyzer

if TYPE_CHECKING:
    from ...utils.output import Console


class ChangeDisplayer:
    """Displays planned changes in a user-friendly format"""

    def __init__(self):
        self.state_analyzer = StateAnalyzer()

    def display_changes(self, changes: Dict[str, List[Any]], console: "Console") -> None:
        """Display planned changes with LEGO principle information"""
        total_changes = sum(len(resources) for resources in changes.values())

        if total_changes == 0:
            return

        console.info(f"\nPlanned changes ({total_changes} total):")
        
        # Check if any resources can benefit from LEGO principle
        lego_resources = []
        recreation_resources = []
        
        for change_type, resources in changes.items():
            for resource in resources:
                if change_type in ["create", "update"]:
                    # Analyze if this change uses LEGO principle
                    current_state = self._get_current_state(resource)
                    if current_state:
                        lego_analysis = self.state_analyzer.analyze_changes_with_lego(current_state, resource)
                        if lego_analysis.get("use_lego", False):
                            lego_resources.append((resource, lego_analysis))
                        else:
                            recreation_resources.append(resource)
        
        # Display LEGO principle info if applicable
        if lego_resources:
            console.info("\n🧱 LEGO Principle Benefits:")
            console.info("   ✅ The following changes use additive components")
            console.info("   ✅ No VM recreation required")
            console.info("   ✅ Zero downtime operations")
            
            for resource, analysis in lego_resources:
                additive_count = len(analysis["changes"].get("additive_components", []))
                if additive_count > 0:
                    console.info(f"   🔧 {resource.name}: Adding {additive_count} component(s)")
        
        if recreation_resources:
            console.info("\n⚠️  The following changes may require VM modification:")
            for resource in recreation_resources:
                console.info(f"   🔄 {resource.name}: Core property changes")

        # Display creates
        if changes["create"]:
            console.info(f"\n  {len(changes['create'])} to create:")
            for resource in changes["create"]:
                console.info(f"    + {resource.name} ({resource._resource_type})")
                # Show configuration for new resources
                desired_state = self.state_analyzer.get_desired_state(resource)
                self._display_resource_details(desired_state, console, indent="      ")

        # Display updates
        if changes["update"]:
            console.info(f"\n  {len(changes['update'])} to update:")
            for resource in changes["update"]:
                console.info(f"    ~ {resource.name} ({resource._resource_type})")
                # Show detailed diff for updates
                current_state = self._get_current_state(resource)
                desired_state = self.state_analyzer.get_desired_state(resource)
                if current_state is not None:
                    self._display_diff(
                        current_state, desired_state, console, indent="      "
                    )

        # Display replacements
        if changes["replace"]:
            console.info(f"\n  {len(changes['replace'])} to replace:")
            for resource in changes["replace"]:
                console.info(f"    -+ {resource.name} ({resource._resource_type})")
                # Show what's changing for replacements
                current_state = self._get_current_state(resource)
                desired_state = self.state_analyzer.get_desired_state(resource)
                if current_state is not None:
                    self._display_diff(
                        current_state, desired_state, console, indent="      "
                    )

        # Display deletes
        if changes["delete"]:
            console.info(f"\n  {len(changes['delete'])} to delete:")
            for resource in changes["delete"]:
                console.info(f"    - {resource.name} ({resource._resource_type})")

    def _display_resource_details(
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
        ]

        for field in key_fields:
            current_val = current.get(field)
            desired_val = desired.get(field)

            if current_val != desired_val:
                if field == "tags":
                    self._display_tags_diff(
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

    def _get_current_state(self, resource: Any) -> Dict[str, Any] | None:
        """Get current state of resource from provider - simplified for display"""
        # This would normally use the planner's method, but for display we can simplify
        try:
            if hasattr(resource, "_provider") and resource._provider:
                from ....core.services.state_detection import create_state_detector
                state_detector = create_state_detector(resource._provider)
                return state_detector.get_current_state(resource)
            return None
        except Exception:
            return None