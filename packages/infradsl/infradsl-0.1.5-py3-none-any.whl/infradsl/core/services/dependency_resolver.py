"""
Dependency Resolution System for InfraDSL

This module provides intelligent dependency resolution for resource creation,
ensuring resources are created in the correct order based on their dependencies.
"""

from typing import List, Dict, Set, Optional, Any
from collections import defaultdict, deque
from ..nexus.base_resource import BaseResource


class DependencyResolver:
    """
    Resolves dependencies between resources and provides creation order.

    This resolver uses topological sorting to determine the correct order
    for resource creation and can detect circular dependencies.
    """

    def __init__(self):
        self._resources: Dict[str, BaseResource] = {}
        self._dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self._reverse_graph: Dict[str, Set[str]] = defaultdict(set)

    def add_resource(self, resource: BaseResource) -> None:
        """Add a resource to the dependency graph"""
        resource_id = resource.metadata.id
        self._resources[resource_id] = resource

        # Build dependency graph
        for dependency in resource.get_dependencies():
            dep_id = dependency.metadata.id
            self._dependency_graph[resource_id].add(dep_id)
            self._reverse_graph[dep_id].add(resource_id)

    def add_resources(self, resources: List[BaseResource]) -> None:
        """Add multiple resources to the dependency graph"""
        for resource in resources:
            self.add_resource(resource)

    def resolve_creation_order(self) -> List[BaseResource]:
        """
        Resolve the creation order using topological sorting.

        Returns:
            List of resources in the order they should be created

        Raises:
            ValueError: If circular dependencies are detected
        """
        # Check for circular dependencies first
        cycles = self._detect_cycles()
        if cycles:
            raise ValueError(f"Circular dependencies detected: {cycles}")

        # Perform topological sort
        in_degree = defaultdict(int)

        # Calculate in-degree for all resources
        for resource_id in self._resources:
            in_degree[resource_id] = len(self._dependency_graph[resource_id])

        # Queue of resources with no dependencies
        queue = deque(
            [
                resource_id
                for resource_id in self._resources
                if in_degree[resource_id] == 0
            ]
        )

        result = []

        while queue:
            current_id = queue.popleft()
            result.append(self._resources[current_id])

            # Reduce in-degree for all dependents
            for dependent_id in self._reverse_graph[current_id]:
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    queue.append(dependent_id)

        # Check if all resources were processed
        if len(result) != len(self._resources):
            remaining = [
                rid
                for rid in self._resources
                if rid not in [r.metadata.id for r in result]
            ]
            raise ValueError(
                f"Failed to resolve dependencies for resources: {remaining}"
            )

        return result

    def resolve_destruction_order(self) -> List[BaseResource]:
        """
        Resolve the destruction order (reverse of creation order).

        Returns:
            List of resources in the order they should be destroyed
        """
        creation_order = self.resolve_creation_order()
        return list(reversed(creation_order))

    def get_resource_dependencies(self, resource: BaseResource) -> List[BaseResource]:
        """Get all resources that a given resource depends on"""
        resource_id = resource.metadata.id
        if resource_id not in self._resources:
            return []

        dependencies = []
        for dep_id in self._dependency_graph[resource_id]:
            if dep_id in self._resources:
                dependencies.append(self._resources[dep_id])

        return dependencies

    def get_resource_dependents(self, resource: BaseResource) -> List[BaseResource]:
        """Get all resources that depend on a given resource"""
        resource_id = resource.metadata.id
        if resource_id not in self._resources:
            return []

        dependents = []
        for dep_id in self._reverse_graph[resource_id]:
            if dep_id in self._resources:
                dependents.append(self._resources[dep_id])

        return dependents

    def _detect_cycles(self) -> List[List[str]]:
        """
        Detect circular dependencies using DFS.

        Returns:
            List of cycles, where each cycle is a list of resource IDs
        """
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(resource_id: str, path: List[str]) -> None:
            if resource_id in rec_stack:
                # Found a cycle
                cycle_start = path.index(resource_id)
                cycle = path[cycle_start:] + [resource_id]
                cycles.append(cycle)
                return

            if resource_id in visited:
                return

            visited.add(resource_id)
            rec_stack.add(resource_id)

            for dep_id in self._dependency_graph[resource_id]:
                if dep_id in self._resources:
                    dfs(dep_id, path + [resource_id])

            rec_stack.remove(resource_id)

        for resource_id in self._resources:
            if resource_id not in visited:
                dfs(resource_id, [])

        return cycles

    def get_dependency_graph(self) -> Dict[str, Dict[str, Any]]:
        """
        Get a visualization-friendly representation of the dependency graph.

        Returns:
            Dictionary with resource info and dependencies
        """
        graph = {}

        for resource_id, resource in self._resources.items():
            dependencies = [
                {
                    "id": dep_id,
                    "name": self._resources[dep_id].metadata.name,
                    "type": self._resources[dep_id].__class__.__name__,
                }
                for dep_id in self._dependency_graph[resource_id]
                if dep_id in self._resources
            ]

            dependents = [
                {
                    "id": dep_id,
                    "name": self._resources[dep_id].metadata.name,
                    "type": self._resources[dep_id].__class__.__name__,
                }
                for dep_id in self._reverse_graph[resource_id]
                if dep_id in self._resources
            ]

            graph[resource_id] = {
                "name": resource.metadata.name,
                "type": resource.__class__.__name__,
                "dependencies": dependencies,
                "dependents": dependents,
            }

        return graph

    def clear(self) -> None:
        """Clear all resources and dependencies"""
        self._resources.clear()
        self._dependency_graph.clear()
        self._reverse_graph.clear()


def create_resources_with_dependencies(
    resources: List[BaseResource],
) -> List[BaseResource]:
    """
    Create resources in the correct order based on their dependencies.

    Args:
        resources: List of resources to create

    Returns:
        List of created resources in the order they were created

    Raises:
        ValueError: If circular dependencies are detected
    """
    resolver = DependencyResolver()
    resolver.add_resources(resources)

    # Get creation order
    creation_order = resolver.resolve_creation_order()

    # Create resources in order
    created_resources = []
    for resource in creation_order:
        try:
            resource.create()
            created_resources.append(resource)
        except Exception as e:
            # If creation fails, we should probably clean up already created resources
            # but for now just re-raise
            raise e

    return created_resources


def destroy_resources_with_dependencies(resources: List[BaseResource]) -> None:
    """
    Destroy resources in the correct order based on their dependencies.

    Args:
        resources: List of resources to destroy
    """
    resolver = DependencyResolver()
    resolver.add_resources(resources)

    # Get destruction order (reverse of creation order)
    destruction_order = resolver.resolve_destruction_order()

    # Destroy resources in order
    for resource in destruction_order:
        try:
            resource.destroy()
        except Exception as e:
            # Log error but continue destroying other resources
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to destroy resource {resource.metadata.name}: {e}")
