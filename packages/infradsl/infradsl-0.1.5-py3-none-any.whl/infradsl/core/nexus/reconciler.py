from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from datetime import datetime

from .base_resource import BaseResource, ResourceState, DriftAction
from ..exceptions import StateException


logger = logging.getLogger(__name__)


class ReconciliationStrategy(Enum):
    """Strategies for reconciling state differences"""

    REPLACE = "replace"  # Replace entire resource
    UPDATE = "update"  # Update only changed fields
    PATCH = "patch"  # Apply minimal patches
    CUSTOM = "custom"  # Use custom reconciliation logic


class FieldChange:
    """Represents a change to a single field"""

    def __init__(self, path: str, old_value: Any, new_value: Any):
        self.path = path
        self.old_value = old_value
        self.new_value = new_value
        self.applied = False
        self.error: Optional[str] = None

    def __repr__(self):
        return (
            f"FieldChange(path={self.path}, old={self.old_value}, new={self.new_value})"
        )


@dataclass
class ReconciliationPlan:
    """Plan for reconciling state differences"""

    resource_id: str
    resource_type: str
    strategy: ReconciliationStrategy
    changes: List[FieldChange] = field(default_factory=list)
    estimated_impact: Dict[str, Any] = field(default_factory=dict)
    validation_errors: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def is_valid(self) -> bool:
        """Check if the plan is valid and can be executed"""
        return len(self.validation_errors) == 0

    def add_change(self, path: str, old_value: Any, new_value: Any) -> None:
        """Add a field change to the plan"""
        self.changes.append(FieldChange(path, old_value, new_value))

    def get_change_summary(self) -> Dict[str, int]:
        """Get summary of changes by type"""
        summary = {
            "total": len(self.changes),
            "additions": 0,
            "modifications": 0,
            "deletions": 0,
        }

        for change in self.changes:
            if change.old_value is None:
                summary["additions"] += 1
            elif change.new_value is None:
                summary["deletions"] += 1
            else:
                summary["modifications"] += 1

        return summary


class StateReconciler:
    """
    Core reconciliation engine that handles state differences.
    Responsible for:
    - Detecting differences between desired and actual state
    - Creating reconciliation plans
    - Executing state changes
    - Handling conflicts and rollbacks
    """

    def __init__(self):
        self._strategies: Dict[str, ReconciliationStrategy] = {}
        self._custom_handlers: Dict[str, Callable[..., Any]] = {}
        self._field_validators: Dict[str, List[Callable[..., Any]]] = {}
        self._impact_analyzers: List[Callable[..., Any]] = []

    def register_strategy(
        self, resource_type: str, strategy: ReconciliationStrategy
    ) -> None:
        """Register a reconciliation strategy for a resource type"""
        self._strategies[resource_type] = strategy

    def register_custom_handler(
        self, resource_type: str, handler: Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]
    ) -> None:
        """Register a custom reconciliation handler"""
        self._custom_handlers[resource_type] = handler

    def register_field_validator(
        self, field_path: str, validator: Callable[[Any, Any], Optional[str]]
    ) -> None:
        """Register a validator for specific field changes"""
        if field_path not in self._field_validators:
            self._field_validators[field_path] = []
        self._field_validators[field_path].append(validator)

    def register_impact_analyzer(
        self, analyzer: Callable[[ReconciliationPlan], Dict[str, Any]]
    ) -> None:
        """Register an impact analyzer"""
        self._impact_analyzers.append(analyzer)

    def create_plan(
        self,
        resource: BaseResource,
        current_state: Dict[str, Any],
        desired_state: Dict[str, Any],
    ) -> ReconciliationPlan:
        """Create a reconciliation plan for a resource"""
        resource_type = resource.__class__.__name__
        strategy = self._strategies.get(resource_type, ReconciliationStrategy.UPDATE)

        plan = ReconciliationPlan(
            resource_id=resource.metadata.id,
            resource_type=resource_type,
            strategy=strategy,
        )

        # Find all differences
        self._find_differences(current_state, desired_state, "", plan)

        # Validate changes
        self._validate_changes(plan)

        # Analyze impact
        self._analyze_impact(plan)

        return plan

    def _find_differences(
        self, current: Any, desired: Any, path: str, plan: ReconciliationPlan
    ) -> None:
        """Recursively find differences between current and desired state"""
        if type(current) != type(desired):
            # Type changed
            plan.add_change(path, current, desired)
            return

        if isinstance(desired, dict):
            # Handle dictionaries
            all_keys = set(current.keys()) | set(desired.keys())

            for key in all_keys:
                new_path = f"{path}.{key}" if path else key

                if key not in current:
                    # Key added
                    plan.add_change(new_path, None, desired[key])
                elif key not in desired:
                    # Key removed
                    plan.add_change(new_path, current[key], None)
                else:
                    # Recurse into nested structures
                    self._find_differences(current[key], desired[key], new_path, plan)

        elif isinstance(desired, list):
            # Handle lists
            if len(current) != len(desired) or current != desired:
                # For now, treat list changes as full replacements
                # More sophisticated list diffing could be added
                plan.add_change(path, current, desired)

        elif current != desired:
            # Primitive value changed
            plan.add_change(path, current, desired)

    def _validate_changes(self, plan: ReconciliationPlan) -> None:
        """Validate all changes in the plan"""
        for change in plan.changes:
            # Check field-specific validators
            validators = self._get_validators_for_path(change.path)

            for validator in validators:
                error = validator(change.old_value, change.new_value)
                if error:
                    plan.validation_errors.append(f"{change.path}: {error}")

            # Check general validation rules
            if self._is_immutable_field(change.path):
                plan.validation_errors.append(
                    f"{change.path}: Field is immutable and cannot be changed"
                )

    def _get_validators_for_path(self, path: str) -> List[Callable[..., Any]]:
        """Get all validators that apply to a field path"""
        validators = []

        # Exact match
        if path in self._field_validators:
            validators.extend(self._field_validators[path])

        # Wildcard matches (e.g., "*.port" matches "container.port")
        for pattern, pattern_validators in self._field_validators.items():
            if self._path_matches_pattern(path, pattern):
                validators.extend(pattern_validators)

        return validators

    def _path_matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if a path matches a pattern with wildcards"""
        if "*" not in pattern:
            return path == pattern

        # Simple wildcard matching
        pattern_parts = pattern.split(".")
        path_parts = path.split(".")

        if len(pattern_parts) != len(path_parts):
            return False

        for i, (pattern_part, path_part) in enumerate(zip(pattern_parts, path_parts)):
            if pattern_part != "*" and pattern_part != path_part:
                return False

        return True

    def _is_immutable_field(self, path: str) -> bool:
        """Check if a field is immutable"""
        # Common immutable fields
        immutable_patterns = ["id", "*.id", "metadata.created_at", "*.created_at"]

        for pattern in immutable_patterns:
            if self._path_matches_pattern(path, pattern):
                return True

        return False

    def _analyze_impact(self, plan: ReconciliationPlan) -> None:
        """Analyze the impact of changes"""
        plan.estimated_impact = {
            "downtime": False,
            "data_loss": False,
            "performance_impact": "low",
            "cost_impact": 0.0,
        }

        # Run registered analyzers
        for analyzer in self._impact_analyzers:
            impact = analyzer(plan)
            plan.estimated_impact.update(impact)

        # Basic impact analysis
        for change in plan.changes:
            # Check for potentially disruptive changes
            if self._is_disruptive_change(change):
                plan.estimated_impact["downtime"] = True

            if self._may_cause_data_loss(change):
                plan.estimated_impact["data_loss"] = True

    def _is_disruptive_change(self, change: FieldChange) -> bool:
        """Check if a change is potentially disruptive"""
        disruptive_patterns = ["*.size", "*.instance_type", "*.region", "network.*"]

        for pattern in disruptive_patterns:
            if self._path_matches_pattern(change.path, pattern):
                return True

        return False

    def _may_cause_data_loss(self, change: FieldChange) -> bool:
        """Check if a change may cause data loss"""
        # Deletion of storage-related fields
        if change.new_value is None and any(
            keyword in change.path.lower()
            for keyword in ["storage", "volume", "disk", "database"]
        ):
            return True

        return False

    async def execute_plan(
        self, plan: ReconciliationPlan, resource: BaseResource, dry_run: bool = False
    ) -> Dict[str, Any]:
        """Execute a reconciliation plan"""
        if not plan.is_valid():
            raise StateException(
                f"Cannot execute invalid plan: {plan.validation_errors}"
            )

        result: Dict[str, Any] = {
            "plan_id": plan.resource_id,
            "changes_applied": 0,
            "changes_failed": 0,
            "errors": [],
            "duration_ms": 0,
        }

        if dry_run:
            result["dry_run"] = True
            result["changes_to_apply"] = len(plan.changes)
            return result

        start_time = datetime.utcnow()

        try:
            if plan.strategy == ReconciliationStrategy.CUSTOM:
                # Use custom handler
                handler = self._custom_handlers.get(plan.resource_type)
                if not handler:
                    raise StateException(
                        f"No custom handler registered for {plan.resource_type}"
                    )

                await handler(resource, plan)
                result["changes_applied"] = len(plan.changes)

            else:
                # Apply changes
                for change in plan.changes:
                    try:
                        await self._apply_change(resource, change)
                        change.applied = True
                        result["changes_applied"] += 1
                    except Exception as e:
                        change.error = str(e)
                        result["changes_failed"] += 1
                        result["errors"].append(f"Failed to apply {change.path}: {e}")

                        # Decide whether to continue or rollback
                        if result["changes_failed"] > 3:
                            raise StateException(
                                "Too many failures, aborting reconciliation"
                            )

        finally:
            end_time = datetime.utcnow()
            result["duration_ms"] = int((end_time - start_time).total_seconds() * 1000)

        return result

    async def _apply_change(self, resource: BaseResource, change: FieldChange) -> None:
        """Apply a single change to a resource"""
        # This would call the provider to apply the change
        # For now, it's a placeholder
        logger.info(f"Applying change: {change}")

        # In a real implementation, this would:
        # 1. Call the provider's update method for the specific field
        # 2. Wait for the change to be applied
        # 3. Verify the change was successful
        pass

    def get_strategy(self, resource_type: str) -> ReconciliationStrategy:
        """Get the reconciliation strategy for a resource type"""
        return self._strategies.get(resource_type, ReconciliationStrategy.UPDATE)
