from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, List, Self, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import hashlib


def generate_deterministic_id(name: str, resource_type: str = "") -> str:
    """Generate a deterministic UUID based on resource name and type"""
    # Create a deterministic hash from name and type
    content = f"{resource_type}:{name}"
    hash_digest = hashlib.sha256(content.encode()).hexdigest()
    
    # Convert hash to UUID format (first 32 chars of hash)
    uuid_str = f"{hash_digest[:8]}-{hash_digest[8:12]}-{hash_digest[12:16]}-{hash_digest[16:20]}-{hash_digest[20:32]}"
    return uuid_str


class ResourceState(Enum):
    """Resource lifecycle states"""

    PENDING = "pending"
    CREATING = "creating"
    ACTIVE = "active"
    UPDATING = "updating"
    DELETING = "deleting"
    DELETED = "deleted"
    FAILED = "failed"
    DRIFTED = "drifted"


class DriftAction(Enum):
    """Actions to take when drift is detected"""

    NOTIFY = "notify"  # Default: Report drift
    REVERT = "revert"  # Automatically trigger an apply to correct the drift
    DESTROY = "destroy"  # Destroy the resource if it has drifted
    IGNORE = "ignore"  # Ignore drift


@dataclass
class ResourceMetadata:
    """Metadata for tracking resources"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    project: Optional[str] = None
    environment: Optional[str] = None
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, Any] = field(default_factory=dict)

    def to_tags(self) -> Dict[str, str]:
        """Convert metadata to cloud provider tags"""
        tags = {
            "infradsl.managed": "true",
            "infradsl.id": self.id,
            "infradsl.name": self.name,
        }
        if self.project:
            tags["infradsl.project"] = self.project
        if self.environment:
            tags["infradsl.environment"] = self.environment
        tags.update(self.labels)
        return tags

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
            "created_by": self.created_by,
            "project": self.project,
            "environment": self.environment,
            "labels": self.labels,
            "annotations": self.annotations,
        }


@dataclass
class ResourceSpec:
    """Base specification for resources"""

    pass


@dataclass
class ResourceStatus:
    """Current status of a resource"""

    state: ResourceState = ResourceState.PENDING
    message: Optional[str] = None
    cloud_id: Optional[str] = None
    provider_data: Dict[str, Any] = field(default_factory=dict)
    last_sync: Optional[datetime] = None
    drift_detected: bool = False
    drift_details: Optional[Dict[str, Any]] = None


class BaseResource(ABC):
    """
    Base class for all InfraDSL resources.
    Implements the fluent interface pattern and core lifecycle methods.
    """

    def __init__(self, name: str):
        self.metadata = ResourceMetadata(name=name)
        # Set deterministic ID based on resource name and type
        self.metadata.id = generate_deterministic_id(name, self.__class__.__name__)
        self.spec = self._create_spec()
        self.status = ResourceStatus()
        self._provider: Optional[Union[Any, str]] = None
        self._drift_policy = DriftAction.NOTIFY
        self._hooks: List[Any] = []
        self._dependencies: List["BaseResource"] = (
            []
        )  # Resources this depends on
        self._dependents: List["BaseResource"] = (
            []
        )  # Resources that depend on this

    @abstractmethod
    def _create_spec(self) -> ResourceSpec:
        """Create the resource-specific specification"""
        pass

    @abstractmethod
    def _validate_spec(self) -> None:
        """Validate the resource specification"""
        pass

    @abstractmethod
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        pass

    def project(self, project: str) -> Self:
        """Set the project for this resource"""
        self.metadata.project = project
        return self

    def with_project(self, project: str) -> Self:
        """Set the project for this resource"""
        self.metadata.project = project
        return self

    def environment(self, env: str) -> Self:
        """Set the environment for this resource"""
        self.metadata.environment = env
        return self

    def with_environment(self, env: str) -> Self:
        """Set the environment for this resource"""
        self.metadata.environment = env
        return self

    def labels(
        self, labels_dict: Optional[Dict[str, str]] = None, **labels: str
    ) -> Self:
        """Add labels to the resource"""
        if labels_dict:
            self.metadata.labels.update(labels_dict)
        if labels:
            self.metadata.labels.update(labels)
        return self

    def annotate(self, **annotations: Any) -> Self:
        """Add annotations to the resource"""
        self.metadata.annotations.update(annotations)
        return self

    def drift_policy(self, policy: DriftAction) -> Self:
        """Set the drift remediation policy"""
        self._drift_policy = policy
        return self

    def depends_on(self, *resources: "BaseResource") -> Self:
        """Add explicit dependency on other resources"""
        for resource in resources:
            if resource not in self._dependencies:
                self._dependencies.append(resource)
                resource._dependents.append(self)
        return self

    def with_provider(self, provider: Any) -> Self:
        """Attach a provider to this resource"""
        if isinstance(provider, str):
            # String provider name - resolve to actual provider instance
            try:
                from .provider_registry import get_registry
                from ..interfaces.provider import ProviderType

                # Get the provider registry
                registry = get_registry()

                # Convert string to ProviderType
                provider_type = ProviderType(provider.lower())

                # Create a basic provider config - this will be enhanced later
                from ..interfaces.provider import ProviderConfig

                # Create minimal config - real config should come from environment or CLI
                provider_config = ProviderConfig(
                    type=provider_type,
                    region=getattr(self, "_default_region", None)
                    or "us-east-1",  # Default fallback
                )

                # Create the provider instance
                self._provider = registry.create_provider(
                    provider_type, provider_config
                )
            except Exception as e:
                # If we can't resolve the provider, store the string for now
                # This allows the nexus engine to resolve it later
                self._provider = provider
        else:
            # Provider object - use as-is
            self._provider = provider
        return self

    def add_implicit_dependency(self, resource: "BaseResource") -> None:
        """Add implicit dependency (used internally by resource methods)"""
        if resource not in self._dependencies:
            self._dependencies.append(resource)
            resource._dependents.append(self)

    def get_dependencies(self) -> List["BaseResource"]:
        """Get all resources this resource depends on"""
        return self._dependencies.copy()

    def get_dependents(self) -> List["BaseResource"]:
        """Get all resources that depend on this resource"""
        return self._dependents.copy()

    def preview(self) -> Dict[str, Any]:
        """Preview what would be created/changed"""
        self._validate_spec()

        # Get current state from provider
        current_state = self._get_current_state()

        # Calculate desired state
        desired_state = self._to_provider_config()

        # Generate diff
        diff = self._calculate_diff(current_state, desired_state)

        return {
            "action": "create" if current_state is None else "update",
            "resource_type": self.__class__.__name__,
            "name": self.metadata.name,
            "current": current_state,
            "desired": desired_state,
            "diff": diff,
        }

    def create(self) -> Self:
        """Create the resource"""
        self._validate_spec()

        # Check if already exists
        current = self._get_current_state()
        if current:
            # Resource exists, populate cloud_id from current state and reconcile instead
            self._populate_cloud_id_from_state(current)
            return self._reconcile(current)

        # Create new resource
        self.status.state = ResourceState.CREATING
        self._execute_hooks("pre_create")

        try:
            provider_result = self._provider_create()
            self.status.cloud_id = provider_result.get("id")
            self.status.provider_data = provider_result
            self.status.state = ResourceState.ACTIVE
            self.metadata.created_at = datetime.utcnow()

            self._execute_hooks("post_create")

        except Exception as e:
            self.status.state = ResourceState.FAILED
            self.status.message = str(e)
            raise

        return self

    def destroy(self) -> None:
        """Destroy the resource"""
        if self.status.state == ResourceState.DELETED:
            return

        self.status.state = ResourceState.DELETING
        self._execute_hooks("pre_destroy")

        try:
            self._provider_destroy()
            self.status.state = ResourceState.DELETED
            self._execute_hooks("post_destroy")

        except Exception as e:
            self.status.state = ResourceState.FAILED
            self.status.message = str(e)
            raise

    def check_drift(self) -> Dict[str, Any]:
        """Check for drift between desired and actual state"""
        current = self._get_current_state()
        if not current:
            return {
                "drifted": True,
                "reason": "Resource does not exist",
                "action_required": "create",
            }

        desired = self._to_provider_config()
        diff = self._calculate_diff(current, desired)

        if diff:
            self.status.drift_detected = True
            self.status.drift_details = diff
            return {"drifted": True, "diff": diff, "action_required": "update"}

        self.status.drift_detected = False
        self.status.drift_details = None
        return {"drifted": False}

    def _populate_cloud_id_from_state(self, state: Dict[str, Any]) -> None:
        """Extract and set cloud_id from state data"""
        # For CloudDNS resources, the actual cloud ID is in zone_id, not id
        if self.__class__.__name__ == "CloudDNS":
            cloud_id = state.get("zone_id") or state.get("id")
        else:
            # For other resources, use the standard id field
            cloud_id = state.get("id")
            
        if cloud_id:
            self.status.cloud_id = cloud_id

    def _reconcile(self, current_state: Dict[str, Any]) -> Self:
        """Reconcile actual state with desired state"""
        desired = self._to_provider_config()
        diff = self._calculate_diff(current_state, desired)

        if not diff:
            # No changes needed
            return self

        # Apply updates
        self.status.state = ResourceState.UPDATING
        self._execute_hooks("pre_update")

        try:
            provider_result = self._provider_update(diff)
            self.status.provider_data.update(provider_result)
            self.status.state = ResourceState.ACTIVE
            self.metadata.updated_at = datetime.utcnow()

            self._execute_hooks("post_update")

        except Exception as e:
            self.status.state = ResourceState.FAILED
            self.status.message = str(e)
            raise

        return self

    def _get_current_state(self) -> Optional[Dict[str, Any]]:
        """Get current state from cloud provider"""
        if not self._provider:
            # No provider attached - return None to indicate resource doesn't exist
            return None

        if isinstance(self._provider, str):
            # Provider is still a string (not resolved) - return None to indicate resource doesn't exist
            return None

        try:
            return self._provider.get_resource_state(self.metadata)
        except Exception:
            # If provider fails, assume resource doesn't exist
            return None

    def _calculate_diff(
        self, current: Optional[Dict[str, Any]], desired: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate differences between current and desired state"""
        if not current:
            return desired

        diff = {}
        for key, desired_value in desired.items():
            if key not in current or current[key] != desired_value:
                diff[key] = {
                    "current": current.get(key),
                    "desired": desired_value,
                }

        return diff

    def _execute_hooks(self, event: str) -> None:
        """Execute registered hooks for an event"""
        for hook in self._hooks:
            if hasattr(hook, event):
                getattr(hook, event)(self)

    @abstractmethod
    def _provider_create(self) -> Dict[str, Any]:
        """Provider-specific create implementation"""
        pass

    @abstractmethod
    def _provider_update(self, diff: Dict[str, Any]) -> Dict[str, Any]:
        """Provider-specific update implementation"""
        pass

    @abstractmethod
    def _provider_destroy(self) -> None:
        """Provider-specific destroy implementation"""
        pass

    # CLI-compatible methods

    def to_dict(self) -> Dict[str, Any]:
        """Convert resource to dictionary for CLI display"""
        return {
            "name": self.metadata.name,
            "type": self.__class__.__name__,
            "id": self.metadata.id,
            "project": self.metadata.project,
            "environment": self.metadata.environment,
            "state": self.status.state.value,
            "created_at": (
                self.metadata.created_at.isoformat()
                if self.metadata.created_at
                else None
            ),
            "updated_at": (
                self.metadata.updated_at.isoformat()
                if self.metadata.updated_at
                else None
            ),
            "labels": self.metadata.labels,
            "annotations": self.metadata.annotations,
            "spec": self._format_spec_for_display(),
            "drift_policy": (
                self._drift_policy.value if self._drift_policy else None
            ),
        }

    def _format_spec_for_display(self) -> Dict[str, Any]:
        """Format spec for human-readable display"""
        spec_dict = {}

        # Convert spec to dict, handling enums and complex types
        for field_name, field_value in self.spec.__dict__.items():
            if field_value is None:
                continue

            if hasattr(field_value, "value"):  # Enum
                spec_dict[field_name] = field_value.value
            elif isinstance(field_value, list):
                # Handle lists, especially for things like additional_disks
                if field_value and isinstance(field_value[0], dict):
                    # Format complex list items
                    formatted_list = []
                    for item in field_value:
                        formatted_item = {}
                        for k, v in item.items():
                            if v is not None:
                                formatted_item[k] = v
                        if formatted_item:
                            formatted_list.append(formatted_item)
                    if formatted_list:
                        spec_dict[field_name] = formatted_list
                elif field_value:
                    spec_dict[field_name] = field_value
            elif isinstance(field_value, dict):
                # Only include non-empty dicts
                if field_value:
                    spec_dict[field_name] = field_value
            else:
                spec_dict[field_name] = field_value

        return spec_dict

    @property
    def _resource_type(self) -> str:
        """Get resource type name for CLI display"""
        return self.__class__.__name__

    @property
    def name(self) -> str:
        """Get resource name for CLI display"""
        return self.metadata.name
