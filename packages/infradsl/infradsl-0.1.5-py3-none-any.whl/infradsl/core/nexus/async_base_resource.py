"""
Async Base Resource - Async-compatible base class for all InfraDSL resources
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, List, Self, Union, Sequence
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from .base_resource import (
    ResourceState,
    DriftAction,
    ResourceMetadata,
    ResourceSpec,
    ResourceStatus,
)
from ..interfaces.async_provider import AsyncProviderInterface
from ..interfaces.provider import ProviderInterface


class AsyncBaseResource(ABC):
    """
    Async-compatible base class for all InfraDSL resources.
    Implements the fluent interface pattern and async lifecycle methods.
    """

    def __init__(self, name: str):
        self.metadata = ResourceMetadata(name=name)
        self.spec = self._create_spec()
        self.status = ResourceStatus()
        self._provider: Optional[
            Union[AsyncProviderInterface, ProviderInterface, str]
        ] = None
        self._drift_policy = DriftAction.NOTIFY
        self._hooks: List[Any] = []
        self._dependencies: List["AsyncBaseResource"] = []  # Resources this depends on
        self._dependents: List["AsyncBaseResource"] = (
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

    def depends_on(self, *resources: "AsyncBaseResource") -> Self:
        """Add explicit dependency on other resources"""
        for resource in resources:
            if resource not in self._dependencies:
                self._dependencies.append(resource)
                resource._dependents.append(self)
        return self

    def with_provider(
        self, provider: Union[AsyncProviderInterface, ProviderInterface, str]
    ) -> Self:
        """Attach a provider to this resource"""
        if isinstance(provider, str):
            # String provider name - resolve to actual provider instance
            try:
                from .provider_registry import get_registry
                from ..interfaces.provider import ProviderType, ProviderConfig

                # Get the provider registry
                registry = get_registry()

                # Convert string to ProviderType
                provider_type = ProviderType(provider.lower())

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

    def add_implicit_dependency(self, resource: "AsyncBaseResource") -> None:
        """Add implicit dependency (used internally by resource methods)"""
        if resource not in self._dependencies:
            self._dependencies.append(resource)
            resource._dependents.append(self)

    def get_dependencies(self) -> List["AsyncBaseResource"]:
        """Get all resources this resource depends on"""
        return self._dependencies.copy()

    def get_dependents(self) -> List["AsyncBaseResource"]:
        """Get all resources that depend on this resource"""
        return self._dependents.copy()

    async def _execute_with_provider(self, method_name: str, *args, **kwargs) -> Any:
        """Execute method with provider, handling both sync and async providers"""
        if not self._provider:
            raise ValueError("No provider attached to resource")

        if isinstance(self._provider, str):
            raise ValueError(
                f"Provider '{self._provider}' is not resolved to an actual provider instance"
            )

        method = getattr(self._provider, method_name)

        if isinstance(self._provider, AsyncProviderInterface):
            # Async provider - call directly
            return await method(*args, **kwargs)
        else:
            # Sync provider - wrap in executor
            import concurrent.futures

            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                return await loop.run_in_executor(executor, method, *args, **kwargs)

    async def preview(self) -> Dict[str, Any]:
        """Preview what would be created/changed"""
        self._validate_spec()

        # Get current state from provider
        current_state = await self._get_current_state()

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

    async def create(self) -> Self:
        """Create the resource"""
        self._validate_spec()

        # Check if already exists
        current = await self._get_current_state()
        if current:
            # Resource exists, reconcile instead
            return await self._reconcile(current)

        # Create new resource
        self.status.state = ResourceState.CREATING
        await self._execute_hooks("pre_create")

        try:
            provider_result = await self._provider_create()
            self.status.cloud_id = provider_result.get("id")
            self.status.provider_data = provider_result
            self.status.state = ResourceState.ACTIVE
            self.metadata.created_at = datetime.utcnow()

            await self._execute_hooks("post_create")

        except Exception as e:
            self.status.state = ResourceState.FAILED
            self.status.message = str(e)
            raise

        return self

    async def destroy(self) -> None:
        """Destroy the resource"""
        if self.status.state == ResourceState.DELETED:
            return

        self.status.state = ResourceState.DELETING
        await self._execute_hooks("pre_destroy")

        try:
            await self._provider_destroy()
            self.status.state = ResourceState.DELETED
            await self._execute_hooks("post_destroy")

        except Exception as e:
            self.status.state = ResourceState.FAILED
            self.status.message = str(e)
            raise

    async def check_drift(self) -> Dict[str, Any]:
        """Check for drift between desired and actual state"""
        current = await self._get_current_state()
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

    async def _reconcile(self, current_state: Dict[str, Any]) -> Self:
        """Reconcile actual state with desired state"""
        desired = self._to_provider_config()
        diff = self._calculate_diff(current_state, desired)

        if not diff:
            # No changes needed
            return self

        # Apply updates
        self.status.state = ResourceState.UPDATING
        await self._execute_hooks("pre_update")

        try:
            provider_result = await self._provider_update(diff)
            self.status.provider_data.update(provider_result)
            self.status.state = ResourceState.ACTIVE
            self.metadata.updated_at = datetime.utcnow()

            await self._execute_hooks("post_update")

        except Exception as e:
            self.status.state = ResourceState.FAILED
            self.status.message = str(e)
            raise

        return self

    async def _get_current_state(self) -> Optional[Dict[str, Any]]:
        """Get current state from cloud provider"""
        if not self._provider:
            # No provider attached - return None to indicate resource doesn't exist
            return None

        if isinstance(self._provider, str):
            # Provider is still a string (not resolved) - return None to indicate resource doesn't exist
            return None

        try:
            return await self._execute_with_provider(
                "get_resource_state", self.metadata
            )
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

    async def _execute_hooks(self, event: str) -> None:
        """Execute registered hooks for an event"""
        for hook in self._hooks:
            if hasattr(hook, event):
                hook_method = getattr(hook, event)
                if asyncio.iscoroutinefunction(hook_method):
                    await hook_method(self)
                else:
                    hook_method(self)

    @abstractmethod
    async def _provider_create(self) -> Dict[str, Any]:
        """Provider-specific create implementation"""
        pass

    @abstractmethod
    async def _provider_update(self, diff: Dict[str, Any]) -> Dict[str, Any]:
        """Provider-specific update implementation"""
        pass

    @abstractmethod
    async def _provider_destroy(self) -> None:
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
            "drift_policy": self._drift_policy.value if self._drift_policy else None,
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

    # Batch operations support
    @classmethod
    async def batch_create(
        cls, resources: List["AsyncBaseResource"]
    ) -> Sequence[Union["AsyncBaseResource", BaseException]]:
        """Create multiple resources in parallel"""
        tasks = [resource.create() for resource in resources]
        return await asyncio.gather(*tasks, return_exceptions=True)

    @classmethod
    async def batch_destroy(
        cls, resources: List["AsyncBaseResource"]
    ) -> Sequence[Union[None, BaseException]]:
        """Destroy multiple resources in parallel"""
        tasks = [resource.destroy() for resource in resources]
        return await asyncio.gather(*tasks, return_exceptions=True)

    @classmethod
    async def batch_check_drift(
        cls, resources: List["AsyncBaseResource"]
    ) -> Sequence[Union[Dict[str, Any], BaseException]]:
        """Check drift for multiple resources in parallel"""
        tasks = [resource.check_drift() for resource in resources]
        return await asyncio.gather(*tasks, return_exceptions=True)

    @classmethod
    async def batch_preview(
        cls, resources: List["AsyncBaseResource"]
    ) -> Sequence[Union[Dict[str, Any], BaseException]]:
        """Preview multiple resources in parallel"""
        tasks = [resource.preview() for resource in resources]
        return await asyncio.gather(*tasks, return_exceptions=True)

    # Dependency resolution
    async def resolve_dependencies(self) -> List["AsyncBaseResource"]:
        """Resolve and return dependencies in creation order"""
        visited = set()
        result = []

        async def visit(resource):
            if resource.metadata.id in visited:
                return
            visited.add(resource.metadata.id)

            # Visit dependencies first
            for dep in resource.get_dependencies():
                await visit(dep)

            result.append(resource)

        await visit(self)
        return result

    async def create_with_dependencies(self) -> Self:
        """Create resource along with all its dependencies"""
        dependencies = await self.resolve_dependencies()

        # Create dependencies in order
        for dep in dependencies:
            if dep.status.state != ResourceState.ACTIVE:
                await dep.create()

        return self

    async def destroy_with_dependents(self) -> None:
        """Destroy resource along with all its dependents"""
        # Destroy dependents first
        for dependent in self.get_dependents():
            if dependent.status.state != ResourceState.DELETED:
                await dependent.destroy()

        # Then destroy self
        await self.destroy()
