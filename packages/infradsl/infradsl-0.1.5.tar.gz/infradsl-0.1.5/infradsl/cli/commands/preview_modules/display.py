"""
Display Module - handles formatting and display of preview results
"""

from typing import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ...utils.output import Console


class PreviewDisplay:
    """Handles display and formatting of preview results"""

    def display_preview_summary(self, changes: Dict[str, List[Any]], console: "Console") -> None:
        """Display a summary of planned changes"""
        total_changes = sum(len(resources) for resources in changes.values())
        
        if total_changes == 0:
            console.success("No changes needed. Infrastructure is up to date.")
            return

        console.info("Planned infrastructure changes:")
        console.info("")

        # Display each type of change
        for change_type, resources in changes.items():
            if resources:
                self._display_change_group(change_type, resources, console)

        console.info("")
        console.info(f"Plan: {self._format_plan_summary(changes)}")

    def _display_change_group(self, change_type: str, resources: List[Any], console: "Console") -> None:
        """Display a group of changes of the same type"""
        if change_type == "create":
            console.info("Resources to be created:")
            icon = "+"
            color = "green"
        elif change_type == "update":
            console.info("Resources to be updated:")
            icon = "~"
            color = "yellow"
        elif change_type == "replace":
            console.info("Resources to be replaced:")
            icon = "-/+"
            color = "red"
        elif change_type == "delete":
            console.info("Resources to be deleted:")
            icon = "-"
            color = "red"
        else:
            console.info(f"Resources to be {change_type}:")
            icon = "?"
            color = "white"

        for resource in resources:
            resource_name = getattr(resource, 'name', str(resource))
            resource_type = getattr(resource, '_resource_type', 'unknown')
            console.info(f"  {icon} {resource_name} ({resource_type})")

        console.info("")

    def _format_plan_summary(self, changes: Dict[str, List[Any]]) -> str:
        """Format the plan summary line"""
        parts = []
        
        if changes.get("create"):
            count = len(changes["create"])
            parts.append(f"{count} to add")
            
        if changes.get("update"):
            count = len(changes["update"])
            parts.append(f"{count} to change")
            
        if changes.get("replace"):
            count = len(changes["replace"])
            parts.append(f"{count} to replace")
            
        if changes.get("delete"):
            count = len(changes["delete"])
            parts.append(f"{count} to destroy")

        return ", ".join(parts) if parts else "no changes"

    def display_resource_details(self, resource: Any, change_type: str, current_state: Dict[str, Any], 
                                desired_state: Dict[str, Any], console: "Console") -> None:
        """Display detailed information about a resource change"""
        resource_name = getattr(resource, 'name', str(resource))
        resource_type = getattr(resource, '_resource_type', 'unknown')
        
        console.info(f"\n{change_type.title()}: {resource_name} ({resource_type})")
        console.info("=" * 50)
        
        if change_type == "create":
            self._display_creation_details(desired_state, console)
        elif change_type == "update":
            self._display_update_details(current_state, desired_state, console)
        elif change_type == "replace":
            self._display_replacement_details(current_state, desired_state, console)

    def _display_creation_details(self, desired_state: Dict[str, Any], console: "Console") -> None:
        """Display details for resource creation"""
        console.info("Configuration:")
        for key, value in desired_state.items():
            if not key.startswith('_'):
                console.info(f"  {key}: {value}")

    def _display_update_details(self, current_state: Dict[str, Any], desired_state: Dict[str, Any], 
                               console: "Console") -> None:
        """Display details for resource updates"""
        console.info("Changes:")
        
        # Find differences
        all_keys = set(current_state.keys()) | set(desired_state.keys())
        for key in sorted(all_keys):
            if key.startswith('_'):
                continue
                
            current_val = current_state.get(key, "<not set>")
            desired_val = desired_state.get(key, "<not set>")
            
            if current_val != desired_val:
                console.info(f"  {key}:")
                console.info(f"    - {current_val}")
                console.info(f"    + {desired_val}")

    def _display_replacement_details(self, current_state: Dict[str, Any], desired_state: Dict[str, Any], 
                                   console: "Console") -> None:
        """Display details for resource replacement"""
        console.info("This resource will be destroyed and recreated due to immutable changes:")
        self._display_update_details(current_state, desired_state, console)