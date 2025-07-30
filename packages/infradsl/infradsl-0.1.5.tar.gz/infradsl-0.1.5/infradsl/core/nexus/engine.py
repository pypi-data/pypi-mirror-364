from typing import Dict, List, Optional, Type, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

from .base_resource import BaseResource, DriftAction
from ..interfaces.provider import (
    ProviderInterface,
    ProviderType,
    ProviderConfig,
)
from ..exceptions import NexusException

logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """Execution modes for operations"""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    BATCHED = "batched"


@dataclass
class NexusConfig:
    """Configuration for the Nexus Engine"""

    providers: Dict[str, ProviderConfig] = field(default_factory=dict)
    default_provider: Optional[str] = None
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    max_parallel_operations: int = 10
    enable_drift_detection: bool = True
    enable_cost_analysis: bool = True
    enable_security_scanning: bool = True
    telemetry_enabled: bool = True
    hooks: List[Any] = field(default_factory=list)


class ResourceRegistry:
    """Registry for tracking all resources managed by Nexus"""

    def __init__(self):
        self._resources: Dict[str, BaseResource] = {}
        self._by_type: Dict[str, List[str]] = {}
        self._by_project: Dict[str, List[str]] = {}
        self._by_environment: Dict[str, List[str]] = {}

    def register(self, resource: BaseResource) -> None:
        """Register a resource"""
        resource_id = resource.metadata.id
        self._resources[resource_id] = resource

        # Index by type
        resource_type = resource.__class__.__name__
        if resource_type not in self._by_type:
            self._by_type[resource_type] = []
        self._by_type[resource_type].append(resource_id)

        # Index by project
        if resource.metadata.project:
            if resource.metadata.project not in self._by_project:
                self._by_project[resource.metadata.project] = []
            self._by_project[resource.metadata.project].append(resource_id)

        # Index by environment
        if resource.metadata.environment:
            if resource.metadata.environment not in self._by_environment:
                self._by_environment[resource.metadata.environment] = []
            self._by_environment[resource.metadata.environment].append(
                resource_id
            )

    def get(self, resource_id: str) -> Optional[BaseResource]:
        """Get a resource by ID"""
        return self._resources.get(resource_id)

    def list_by_type(self, resource_type: str) -> List[BaseResource]:
        """List resources by type"""
        ids = self._by_type.get(resource_type, [])
        return [self._resources[rid] for rid in ids]

    def list_by_project(self, project: str) -> List[BaseResource]:
        """List resources by project"""
        ids = self._by_project.get(project, [])
        return [self._resources[rid] for rid in ids]

    def list_by_environment(self, environment: str) -> List[BaseResource]:
        """List resources by environment"""
        ids = self._by_environment.get(environment, [])
        return [self._resources[rid] for rid in ids]

    def list_all(self) -> List[BaseResource]:
        """List all resources"""
        return list(self._resources.values())


class NexusEngine:
    """
    The Nexus Engine - the heart of InfraDSL.

    Responsible for:
    - Managing providers and resources
    - Orchestrating operations (create, update, destroy)
    - Handling drift detection and remediation
    - Coordinating intelligence features
    - Managing execution modes and parallelism
    """

    def __init__(self, config: Optional[NexusConfig] = None):
        self.config = config or NexusConfig()
        self._providers: Dict[str, ProviderInterface] = {}
        self._registry = ResourceRegistry()
        self._executor = ThreadPoolExecutor(
            max_workers=self.config.max_parallel_operations
        )
        self._event_handlers: Dict[str, List[Callable[..., Any]]] = {}
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialize configured providers"""
        for name, provider_config in self.config.providers.items():
            provider_class = self._get_provider_class(provider_config.type)
            if provider_class:
                self._providers[name] = provider_class(provider_config)
                logger.info(
                    f"Initialized provider: {name} ({provider_config.type.value})"
                )

    def _get_provider_class(
        self, provider_type: ProviderType
    ) -> Optional[Type[ProviderInterface]]:
        """Get provider class by type"""
        # This will be populated by provider implementations
        # For now, return None
        return None

    def get_provider(self, name: Optional[str] = None) -> ProviderInterface:
        """Get a provider by name or the default provider"""
        if name:
            if name not in self._providers:
                raise NexusException(f"Provider '{name}' not found")
            return self._providers[name]

        if self.config.default_provider:
            return self._providers[self.config.default_provider]

        if len(self._providers) == 1:
            return list(self._providers.values())[0]

        raise NexusException(
            "No provider specified and no default provider configured"
        )

    def register_resource(
        self, resource: BaseResource, provider_name: Optional[str] = None
    ) -> BaseResource:
        """Register a resource with the engine"""
        # --- Automatic provider attachment ---
        if resource._provider is None:
            # Try to infer provider from resource's factory (e.g., DigitalOcean.Droplet)
            factory = getattr(resource, "_factory", None)
            provider_config = None
            if factory and hasattr(factory, "_default_config"):
                provider_config = getattr(factory, "_default_config")
            # Fallback: try to get from class (for future extensibility)
            elif hasattr(resource, "_default_config"):
                provider_config = getattr(resource, "_default_config")

            if provider_config:
                # Use the provider registry to create the provider
                try:
                    from infradsl.core.nexus.provider_registry import (
                        get_registry,
                    )

                    registry = get_registry()
                    provider = registry.create_provider(
                        provider_config.type, provider_config
                    )
                    resource._provider = provider
                except Exception as e:
                    logger.error(f"Failed to auto-attach provider: {e}")
                    # Fallback to engine logic below

        # Fallback: use engine's provider logic if still not attached
        if resource._provider is None:
            provider = self.get_provider(provider_name)
            resource._provider = provider

        # Register in registry
        self._registry.register(resource)

        # Apply global hooks
        for hook in self.config.hooks:
            resource._hooks.append(hook)

        self._emit_event("resource_registered", resource)

        return resource

    async def create_resources(
        self, resources: List[BaseResource]
    ) -> List[BaseResource]:
        """Create multiple resources"""
        if self.config.execution_mode == ExecutionMode.SEQUENTIAL:
            return await self._create_sequential(resources)
        elif self.config.execution_mode == ExecutionMode.PARALLEL:
            return await self._create_parallel(resources)
        else:  # BATCHED
            return await self._create_batched(resources)

    async def _create_sequential(
        self, resources: List[BaseResource]
    ) -> List[BaseResource]:
        """Create resources sequentially"""
        results = []
        for resource in resources:
            try:
                self._emit_event("resource_creating", resource)
                result = await asyncio.to_thread(resource.create)
                self._emit_event("resource_created", result)
                results.append(result)
            except Exception as e:
                self._emit_event("resource_failed", resource, error=e)
                raise
        return results

    async def _create_parallel(
        self, resources: List[BaseResource]
    ) -> List[BaseResource]:
        """Create resources in parallel"""
        tasks = []
        for resource in resources:
            self._emit_event("resource_creating", resource)
            task = asyncio.to_thread(resource.create)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check for failures
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self._emit_event("resource_failed", resources[i], error=result)
                raise result
            else:
                self._emit_event("resource_created", result)
                final_results.append(result)

        return final_results

    async def _create_batched(
        self, resources: List[BaseResource]
    ) -> List[BaseResource]:
        """Create resources in batches"""
        batch_size = self.config.max_parallel_operations
        results = []

        for i in range(0, len(resources), batch_size):
            batch = resources[i : i + batch_size]
            batch_results = await self._create_parallel(batch)
            results.extend(batch_results)

        return results

    async def destroy_resources(self, resources: List[BaseResource]) -> None:
        """Destroy multiple resources"""
        # Destroy in reverse order to handle dependencies
        reversed_resources = list(reversed(resources))

        for resource in reversed_resources:
            try:
                self._emit_event("resource_destroying", resource)
                await asyncio.to_thread(resource.destroy)
                self._emit_event("resource_destroyed", resource)
            except Exception as e:
                self._emit_event("resource_failed", resource, error=e)
                raise

    async def check_drift(
        self, project: Optional[str] = None, environment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check drift for resources"""
        if not self.config.enable_drift_detection:
            return {"enabled": False}

        # Get resources to check
        if project:
            resources = self._registry.list_by_project(project)
        elif environment:
            resources = self._registry.list_by_environment(environment)
        else:
            resources = self._registry.list_all()

        drift_report: Dict[str, Any] = {
            "total_resources": len(resources),
            "drifted_resources": [],
            "missing_resources": [],
            "ok_resources": [],
        }

        for resource in resources:
            try:
                drift_status = await asyncio.to_thread(resource.check_drift)

                if drift_status["drifted"]:
                    if drift_status.get("reason") == "Resource does not exist":
                        drift_report["missing_resources"].append(
                            {
                                "resource": resource.metadata.name,
                                "type": resource.__class__.__name__,
                                "id": resource.metadata.id,
                            }
                        )
                    else:
                        drift_report["drifted_resources"].append(
                            {
                                "resource": resource.metadata.name,
                                "type": resource.__class__.__name__,
                                "id": resource.metadata.id,
                                "diff": drift_status.get("diff"),
                            }
                        )

                    # Handle drift based on policy
                    await self._handle_drift(resource, drift_status)
                else:
                    drift_report["ok_resources"].append(resource.metadata.id)

            except Exception as e:
                logger.error(
                    f"Error checking drift for {resource.metadata.name}: {e}"
                )

        self._emit_event("drift_check_completed", drift_report)
        return drift_report

    async def _handle_drift(
        self, resource: BaseResource, drift_status: Dict[str, Any]
    ) -> None:
        """Handle drift based on resource policy"""
        policy = resource._drift_policy

        if policy == DriftAction.NOTIFY:
            self._emit_event("drift_detected", resource, drift_status)

        elif policy == DriftAction.REVERT:
            self._emit_event("drift_reconciling", resource)
            try:
                if drift_status.get("action_required") == "create":
                    await asyncio.to_thread(resource.create)
                else:
                    # Resource exists but drifted - reconcile will handle it
                    current_state = resource._get_current_state()
                    if current_state is not None:
                        await asyncio.to_thread(
                            resource._reconcile, current_state
                        )
                    else:
                        # Fallback to create if current state is None
                        await asyncio.to_thread(resource.create)
                self._emit_event("drift_reconciled", resource)
            except Exception as e:
                self._emit_event("drift_reconcile_failed", resource, error=e)

        elif policy == DriftAction.DESTROY:
            self._emit_event("drift_destroying", resource)
            await asyncio.to_thread(resource.destroy)
            self._emit_event("drift_destroyed", resource)

    def on_event(self, event: str, handler: Callable[..., Any]) -> None:
        """Register an event handler"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)

    def _emit_event(self, event: str, *args, **kwargs) -> None:
        """Emit an event to all handlers"""
        if event in self._event_handlers:
            for handler in self._event_handlers[event]:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in event handler for {event}: {e}")

    def get_registry(self) -> ResourceRegistry:
        """Get the resource registry"""
        return self._registry

    def create_resource(self, resource: BaseResource) -> bool:
        """Create a single resource"""
        try:
            self._emit_event("resource_creating", resource)
            result = resource.create()
            self._emit_event("resource_created", resource)
            return True
        except Exception as e:
            self._emit_event("resource_failed", resource, error=e)
            logger.error(
                f"Failed to create resource {resource.metadata.name}: {e}"
            )
            return False

    def update_resource(self, resource: BaseResource) -> bool:
        """Update a single resource"""
        try:
            self._emit_event("resource_updating", resource)
            # Get current state and reconcile
            current_state = resource._get_current_state()
            if current_state is not None:
                resource._reconcile(current_state)
            else:
                # If no current state, create the resource
                resource.create()
            self._emit_event("resource_updated", resource)
            return True
        except Exception as e:
            self._emit_event("resource_failed", resource, error=e)
            logger.error(
                f"Failed to update resource {resource.metadata.name}: {e}"
            )
            return False

    def delete_resource(self, resource: BaseResource) -> bool:
        """Delete a single resource"""
        try:
            self._emit_event("resource_destroying", resource)
            resource.destroy()
            self._emit_event("resource_destroyed", resource)
            return True
        except Exception as e:
            self._emit_event("resource_failed", resource, error=e)
            logger.error(
                f"Failed to delete resource {resource.metadata.name}: {e}"
            )
            return False

    def destroy(self, resource: BaseResource) -> bool:
        """Alias for delete_resource for backward compatibility"""
        return self.delete_resource(resource)

    def get_resource_state(
        self, resource_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get current state of a resource from provider"""
        try:
            # Find resource in registry
            resource = None
            for res in self._registry.list_all():
                if res.metadata.name == resource_name:
                    resource = res
                    break

            if resource is None:
                return None

            # Get current state from provider
            current_state = resource._get_current_state()
            return current_state
        except Exception as e:
            logger.error(
                f"Failed to get resource state for {resource_name}: {e}"
            )
            return None

    def get_resource_by_id(
        self, resource_type: str, resource_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get resource details by provider-specific ID"""
        try:
            # This would integrate with actual provider APIs
            # For now, return mock data
            return {
                "id": resource_id,
                "type": resource_type,
                "name": f"imported-{resource_type}-{resource_id[:8]}",
                "provider": "aws",  # Mock provider
                "status": "running",
                "created_at": "2024-01-01T00:00:00Z",
                "configuration": {
                    "instance_type": "t2.micro",
                    "region": "us-west-2",
                },
            }
        except Exception as e:
            logger.error(f"Failed to get resource by ID {resource_id}: {e}")
            return None

    def shutdown(self) -> None:
        """Shutdown the engine"""
        self._executor.shutdown(wait=True)
