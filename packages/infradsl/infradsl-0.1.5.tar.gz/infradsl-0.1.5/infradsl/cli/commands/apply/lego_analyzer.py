"""
LEGO Principle Analyzer - additive infrastructure without recreate cycles
"""

from typing import Any, Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class LEGOAnalyzer:
    """Analyzes changes using the LEGO principle - additive components without recreation"""

    def analyze_lego_changes(self, current_resource: Any, desired_resource: Any) -> Dict[str, List[str]]:
        """
        Analyze changes using LEGO principle - separate additive vs modification changes.
        
        Returns:
            changes = {
                "vm_modifications": [],      # Changes to the VM itself (might require recreation)
                "additive_components": [],   # New components to add (pure LEGO)
                "component_updates": [],     # Updates to existing components (in-place)
                "component_removals": [],    # Components to remove
                "in_place_updates": []       # Properties that can be updated in-place
            }
        """
        changes = {
            "vm_modifications": [],
            "additive_components": [],
            "component_updates": [],
            "component_removals": [],
            "in_place_updates": []
        }

        if not current_resource or not desired_resource:
            return changes

        # Core VM properties that might require recreation
        core_properties = ["size", "image", "zone", "machine_type"]
        
        # Properties that can be updated in-place without recreation
        in_place_properties = ["disk_size_gb", "tags", "labels", "monitoring", "backups", "metadata"]
        
        # LEGO components that are purely additive
        lego_components = [
            "load_balancer", "database", "monitoring_stack", "backup_schedule",
            "ssl_cert", "firewall_rules", "dns_config", "cdn", "vpn_access"
        ]

        # Analyze core VM properties
        current_state = self._get_resource_state(current_resource)
        desired_state = self._get_resource_state(desired_resource)

        for prop in core_properties:
            current_val = current_state.get(prop)
            desired_val = desired_state.get(prop)
            
            if current_val != desired_val and desired_val is not None:
                changes["vm_modifications"].append(prop)

        # Analyze in-place updatable properties
        for prop in in_place_properties:
            current_val = current_state.get(prop)
            desired_val = desired_state.get(prop)
            
            if current_val != desired_val and desired_val is not None:
                changes["in_place_updates"].append(prop)

        # Analyze LEGO components
        for component in lego_components:
            current_has = self._has_component(current_resource, component)
            desired_has = self._has_component(desired_resource, component)
            
            if not current_has and desired_has:
                # New component being added - pure LEGO operation
                changes["additive_components"].append(component)
            elif current_has and desired_has:
                # Component exists in both, check if configuration changed
                if self._component_changed(current_resource, desired_resource, component):
                    changes["component_updates"].append(component)
            elif current_has and not desired_has:
                # Component being removed
                changes["component_removals"].append(component)

        return changes

    def should_use_lego_approach(self, changes: Dict[str, List[str]]) -> bool:
        """Determine if we can use pure LEGO approach vs need recreation"""
        # If only additive components and in-place updates, use LEGO
        destructive_changes = changes.get("vm_modifications", [])
        
        # Special case: disk size increases can be done in-place on most providers
        non_destructive_modifications = []
        for mod in destructive_changes:
            if mod == "disk_size_gb":
                # Disk size increase is in-place on GCP/AWS/DO
                changes["in_place_updates"].append(mod)
            else:
                non_destructive_modifications.append(mod)
        
        changes["vm_modifications"] = non_destructive_modifications
        
        # Pure LEGO if no destructive VM modifications
        return len(changes["vm_modifications"]) == 0

    def get_execution_plan(self, changes: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Generate execution plan optimized for LEGO principle"""
        plan = []

        # 1. In-place updates first (zero downtime)
        for update in changes.get("in_place_updates", []):
            plan.append({
                "action": "update_in_place",
                "target": update,
                "risk": "none",
                "downtime": "0s",
                "description": f"Update {update} without VM restart"
            })

        # 2. Add new LEGO components (pure additions)
        for component in changes.get("additive_components", []):
            plan.append({
                "action": "add_component", 
                "target": component,
                "risk": "none",
                "downtime": "0s",
                "description": f"Add {component} component (LEGO principle)"
            })

        # 3. Update existing components (component-level changes)
        for component in changes.get("component_updates", []):
            plan.append({
                "action": "update_component",
                "target": component,
                "risk": "low",
                "downtime": "0s",
                "description": f"Update {component} configuration"
            })

        # 4. Remove components (clean removal)
        for component in changes.get("component_removals", []):
            plan.append({
                "action": "remove_component",
                "target": component,
                "risk": "low", 
                "downtime": "0s",
                "description": f"Remove {component} component"
            })

        # 5. VM modifications (last resort, with user confirmation)
        for modification in changes.get("vm_modifications", []):
            plan.append({
                "action": "modify_vm",
                "target": modification,
                "risk": "high",
                "downtime": "2-5min",
                "description": f"Modify VM {modification} (requires recreation)",
                "requires_confirmation": True
            })

        return plan

    def _get_resource_state(self, resource: Any) -> Dict[str, Any]:
        """Extract state from resource for comparison"""
        if hasattr(resource, "to_dict"):
            return resource.to_dict()
        
        # Extract common properties
        state = {}
        
        # Core VM properties
        if hasattr(resource, "spec"):
            spec = resource.spec
            state.update({
                "size": getattr(spec, "instance_size", None),
                "machine_type": getattr(spec, "machine_type", None),
                "image": getattr(spec, "image_type", None),
                "zone": getattr(spec, "provider_config", {}).get("zone"),
                "disk_size_gb": getattr(spec, "disk_size_gb", None),
            })

        # Metadata and labels
        if hasattr(resource, "metadata"):
            metadata = resource.metadata
            state.update({
                "tags": getattr(metadata, "tags", {}),
                "labels": getattr(metadata, "labels", {}),
                "environment": getattr(metadata, "environment", None),
            })

        return state

    def _has_component(self, resource: Any, component_name: str) -> bool:
        """Check if resource has a specific LEGO component"""
        # Check for component-specific attributes
        component_attributes = {
            "load_balancer": ["_load_balancer_config", "_lb_config", "load_balancer"],
            "database": ["_database_config", "_db_config", "database"],
            "monitoring_stack": ["_monitoring_config", "monitoring"],
            "backup_schedule": ["_backup_config", "backup"],
            "ssl_cert": ["_ssl_config", "ssl"],
            "firewall_rules": ["_firewall_config", "firewall"],
            "dns_config": ["_dns_config", "dns"],
            "cdn": ["_cdn_config", "cdn"],
            "vpn_access": ["_vpn_config", "vpn"]
        }

        if component_name in component_attributes:
            for attr in component_attributes[component_name]:
                if hasattr(resource, attr):
                    value = getattr(resource, attr)
                    # Component exists if attribute is not None/empty
                    return value is not None and value != {}
        
        return False

    def _component_changed(self, current_resource: Any, desired_resource: Any, component_name: str) -> bool:
        """Check if a LEGO component's configuration changed"""
        component_attributes = {
            "load_balancer": ["_load_balancer_config", "_lb_config"],
            "database": ["_database_config", "_db_config"],
            "monitoring_stack": ["_monitoring_config"],
            "backup_schedule": ["_backup_config"],
            "ssl_cert": ["_ssl_config"],
            "firewall_rules": ["_firewall_config"],
            "dns_config": ["_dns_config"],
            "cdn": ["_cdn_config"],
            "vpn_access": ["_vpn_config"]
        }

        if component_name in component_attributes:
            for attr in component_attributes[component_name]:
                current_val = getattr(current_resource, attr, None)
                desired_val = getattr(desired_resource, attr, None)
                
                # Compare configurations
                if current_val != desired_val:
                    return True
        
        return False

    def explain_lego_benefits(self, changes: Dict[str, List[str]]) -> str:
        """Generate user-friendly explanation of LEGO benefits"""
        if self.should_use_lego_approach(changes):
            additive_count = len(changes.get("additive_components", []))
            update_count = len(changes.get("in_place_updates", []))
            
            explanation = "🧱 LEGO Principle: This change uses additive components!\n\n"
            explanation += "Benefits:\n"
            explanation += "  ✅ Your VM will NOT be recreated or restarted\n"
            explanation += "  ✅ Zero downtime\n"
            explanation += "  ✅ No data loss risk\n"
            explanation += "  ✅ Changes are easily reversible\n\n"
            
            if additive_count > 0:
                explanation += f"  🔧 Adding {additive_count} new component(s)\n"
            if update_count > 0:
                explanation += f"  📝 Updating {update_count} property(s) in-place\n"
                
            return explanation
        else:
            vm_modifications = changes.get("vm_modifications", [])
            explanation = "⚠️  Some changes require VM modification:\n\n"
            
            for mod in vm_modifications:
                explanation += f"  🔄 {mod} change requires VM recreation\n"
            
            explanation += "\nTo minimize recreation in future:\n"
            explanation += "  💡 Use .disk() for storage additions\n"
            explanation += "  💡 Use .load_balancer() for load balancing\n"
            explanation += "  💡 Use .database() for data storage\n"
            
            return explanation