from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import graphlib
import asyncio
import logging

from .base_resource import BaseResource, ResourceState
from ..exceptions import ResourceException


logger = logging.getLogger(__name__)


class DependencyType(Enum):
    """Types of resource dependencies"""

    HARD = "hard"  # Must exist before creation
    SOFT = "soft"  # Reference only, no ordering required
    RUNTIME = "runtime"  # Discovered at runtime


@dataclass
class ResourceDependency:
    """Represents a dependency between resources"""

    source_id: str
    target_id: str
    dependency_type: DependencyType = DependencyType.HARD
    attributes: Dict[str, Any] = field(default_factory=dict)


class ResourceGraph:
    """
    Manages resource dependencies as a directed acyclic graph (DAG).
    Used for determining creation/destruction order.
    """

    def __init__(self):
        self._dependencies: Dict[str, Set[str]] = {}
        self._reverse_dependencies: Dict[str, Set[str]] = {}
        self._dependency_metadata: Dict[Tuple[str, str], ResourceDependency] = {}

    def add_dependency(self, dependency: ResourceDependency) -> None:
        """Add a dependency relationship"""
        source, target = dependency.source_id, dependency.target_id

        # Initialize sets if needed
        if source not in self._dependencies:
            self._dependencies[source] = set()
        if target not in self._reverse_dependencies:
            self._reverse_dependencies[target] = set()

        # Add the dependency
        self._dependencies[source].add(target)
        self._reverse_dependencies[target].add(source)
        self._dependency_metadata[(source, target)] = dependency

    def remove_dependency(self, source_id: str, target_id: str) -> None:
        """Remove a dependency relationship"""
        if source_id in self._dependencies:
            self._dependencies[source_id].discard(target_id)
        if target_id in self._reverse_dependencies:
            self._reverse_dependencies[target_id].discard(source_id)
        self._dependency_metadata.pop((source_id, target_id), None)

    def get_dependencies(self, resource_id: str) -> Set[str]:
        """Get all resources this resource depends on"""
        return self._dependencies.get(resource_id, set())

    def get_dependents(self, resource_id: str) -> Set[str]:
        """Get all resources that depend on this resource"""
        return self._reverse_dependencies.get(resource_id, set())

    def get_creation_order(self, resource_ids: List[str]) -> List[List[str]]:
        """
        Get the order to create resources, respecting dependencies.
        Returns a list of batches that can be created in parallel.
        """
        # Build subgraph for requested resources
        subgraph = {}
        for rid in resource_ids:
            deps = self._dependencies.get(rid, set())
            # Only include dependencies that are in our resource list
            subgraph[rid] = deps.intersection(resource_ids)

        try:
            # Use topological sort to get order
            sorter = graphlib.TopologicalSorter(subgraph)
            sorter.prepare()

            # Get batches of resources that can be created in parallel
            batches = []
            while sorter.is_active():
                batch = list(sorter.get_ready())
                if batch:
                    batches.append(batch)
                    for node in batch:
                        sorter.done(node)

            return batches

        except graphlib.CycleError as e:
            raise ResourceException(f"Circular dependency detected: {e}")

    def get_destruction_order(self, resource_ids: List[str]) -> List[List[str]]:
        """
        Get the order to destroy resources (reverse of creation order).
        """
        creation_order = self.get_creation_order(resource_ids)
        # Reverse the order of batches
        return list(reversed(creation_order))

    def validate_no_cycles(self) -> bool:
        """Validate that the graph has no cycles"""
        try:
            sorter = graphlib.TopologicalSorter(self._dependencies)
            list(sorter.static_order())
            return True
        except graphlib.CycleError:
            return False


class LifecycleManager:
    """
    Manages the lifecycle of resources including:
    - Dependency resolution
    - Ordered creation/destruction
    - State transitions
    - Rollback on failures
    """

    def __init__(self):
        self._graph = ResourceGraph()
        self._resources: Dict[str, BaseResource] = {}
        self._state_history: Dict[str, List[ResourceState]] = {}

    def register_resource(self, resource: BaseResource) -> None:
        """Register a resource with the lifecycle manager"""
        self._resources[resource.metadata.id] = resource
        self._state_history[resource.metadata.id] = [resource.status.state]

    def add_dependency(
        self,
        source: BaseResource,
        target: BaseResource,
        dependency_type: DependencyType = DependencyType.HARD,
    ) -> None:
        """Add a dependency between resources"""
        dep = ResourceDependency(
            source_id=source.metadata.id,
            target_id=target.metadata.id,
            dependency_type=dependency_type,
        )
        self._graph.add_dependency(dep)

    def remove_dependency(self, source: BaseResource, target: BaseResource) -> None:
        """Remove a dependency between resources"""
        self._graph.remove_dependency(source.metadata.id, target.metadata.id)

    async def create_resources(
        self, resources: List[BaseResource], parallel: bool = True
    ) -> List[BaseResource]:
        """
        Create resources in dependency order.

        Args:
            resources: Resources to create
            parallel: Whether to create independent resources in parallel

        Returns:
            Successfully created resources
        """
        resource_ids = [r.metadata.id for r in resources]
        batches = self._graph.get_creation_order(resource_ids)

        created_resources = []
        failed_resources = []

        for batch in batches:
            batch_resources = [self._resources[rid] for rid in batch]

            # Check if dependencies are satisfied
            for resource in batch_resources:
                if not self._check_dependencies_satisfied(resource):
                    raise ResourceException(
                        f"Dependencies not satisfied for {resource.metadata.name}"
                    )

            # Create resources in this batch
            if parallel and len(batch_resources) > 1:
                results = await self._create_parallel(batch_resources)
            else:
                results = await self._create_sequential(batch_resources)

            # Track results
            for resource, success in results:
                if success:
                    created_resources.append(resource)
                else:
                    failed_resources.append(resource)
                    # If any resource fails, stop and rollback
                    if failed_resources:
                        await self._rollback_creation(created_resources)
                        raise ResourceException(
                            f"Failed to create resources: {[r.metadata.name for r in failed_resources]}"
                        )

        return created_resources

    async def destroy_resources(
        self, resources: List[BaseResource], parallel: bool = True
    ) -> None:
        """
        Destroy resources in reverse dependency order.
        """
        resource_ids = [r.metadata.id for r in resources]
        batches = self._graph.get_destruction_order(resource_ids)

        for batch in batches:
            batch_resources = [self._resources[rid] for rid in batch]

            # Check if any dependents still exist
            for resource in batch_resources:
                if self._has_active_dependents(resource):
                    raise ResourceException(
                        f"Cannot destroy {resource.metadata.name}: has active dependents"
                    )

            # Destroy resources in this batch
            if parallel and len(batch_resources) > 1:
                await self._destroy_parallel(batch_resources)
            else:
                await self._destroy_sequential(batch_resources)

    def _check_dependencies_satisfied(self, resource: BaseResource) -> bool:
        """Check if all dependencies of a resource are satisfied"""
        dependencies = self._graph.get_dependencies(resource.metadata.id)

        for dep_id in dependencies:
            dep_resource = self._resources.get(dep_id)
            if not dep_resource or dep_resource.status.state != ResourceState.ACTIVE:
                return False

        return True

    def _has_active_dependents(self, resource: BaseResource) -> bool:
        """Check if a resource has any active dependents"""
        dependents = self._graph.get_dependents(resource.metadata.id)

        for dep_id in dependents:
            dep_resource = self._resources.get(dep_id)
            if dep_resource and dep_resource.status.state in [
                ResourceState.ACTIVE,
                ResourceState.CREATING,
                ResourceState.UPDATING,
            ]:
                return True

        return False

    async def _create_sequential(
        self, resources: List[BaseResource]
    ) -> List[Tuple[BaseResource, bool]]:
        """Create resources sequentially"""
        results = []

        for resource in resources:
            try:
                self._transition_state(resource, ResourceState.CREATING)
                await asyncio.to_thread(resource.create)
                results.append((resource, True))
            except Exception as e:
                logger.error(f"Failed to create {resource.metadata.name}: {e}")
                self._transition_state(resource, ResourceState.FAILED)
                results.append((resource, False))

        return results

    async def _create_parallel(
        self, resources: List[BaseResource]
    ) -> List[Tuple[BaseResource, bool]]:
        """Create resources in parallel"""
        tasks = []

        for resource in resources:
            self._transition_state(resource, ResourceState.CREATING)
            task = asyncio.to_thread(resource.create)
            tasks.append((resource, task))

        results = []
        for resource, task in tasks:
            try:
                await task
                results.append((resource, True))
            except Exception as e:
                logger.error(f"Failed to create {resource.metadata.name}: {e}")
                self._transition_state(resource, ResourceState.FAILED)
                results.append((resource, False))

        return results

    async def _destroy_sequential(self, resources: List[BaseResource]) -> None:
        """Destroy resources sequentially"""
        for resource in resources:
            try:
                self._transition_state(resource, ResourceState.DELETING)
                await asyncio.to_thread(resource.destroy)
            except Exception as e:
                logger.error(f"Failed to destroy {resource.metadata.name}: {e}")
                self._transition_state(resource, ResourceState.FAILED)
                raise

    async def _destroy_parallel(self, resources: List[BaseResource]) -> None:
        """Destroy resources in parallel"""
        tasks = []

        for resource in resources:
            self._transition_state(resource, ResourceState.DELETING)
            task = asyncio.to_thread(resource.destroy)
            tasks.append((resource, task))

        for resource, task in tasks:
            try:
                await task
            except Exception as e:
                logger.error(f"Failed to destroy {resource.metadata.name}: {e}")
                self._transition_state(resource, ResourceState.FAILED)
                raise

    async def _rollback_creation(self, created_resources: List[BaseResource]) -> None:
        """Rollback by destroying already created resources"""
        logger.warning(f"Rolling back creation of {len(created_resources)} resources")

        try:
            await self.destroy_resources(created_resources, parallel=True)
        except Exception as e:
            logger.error(f"Error during rollback: {e}")

    def _transition_state(
        self, resource: BaseResource, new_state: ResourceState
    ) -> None:
        """Transition a resource to a new state and track history"""
        old_state = resource.status.state
        resource.status.state = new_state

        # Track state history
        if resource.metadata.id in self._state_history:
            self._state_history[resource.metadata.id].append(new_state)

        logger.debug(
            f"Resource {resource.metadata.name} transitioned from {old_state} to {new_state}"
        )

    def get_state_history(self, resource: BaseResource) -> List[ResourceState]:
        """Get the state transition history for a resource"""
        return self._state_history.get(resource.metadata.id, [])

    def get_dependency_graph(self) -> ResourceGraph:
        """Get the dependency graph"""
        return self._graph
