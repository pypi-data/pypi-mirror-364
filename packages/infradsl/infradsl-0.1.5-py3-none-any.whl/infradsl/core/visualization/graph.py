"""
Dependency Graph Builder for Infrastructure Topology

This module implements the core graph building logic for visualizing
infrastructure dependencies and relationships.
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone

try:
    import networkx as nx

    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None

from infradsl.core.nexus.base_resource import BaseResource

try:
    from infradsl.core.monitoring import DriftResult
except ImportError:
    # Create a dummy DriftResult if monitoring module is not available
    class DriftResult:
        def __init__(self):
            self.drift_detected = False


class NodeType(Enum):
    """Types of nodes in the dependency graph"""

    COMPUTE = "compute"
    NETWORK = "network"
    STORAGE = "storage"
    DATABASE = "database"
    SECURITY = "security"
    MONITORING = "monitoring"
    CICD = "cicd"
    DNS = "dns"
    LOADBALANCER = "loadbalancer"
    CONTAINER = "container"
    KUBERNETES = "kubernetes"
    FUNCTION = "function"
    UNKNOWN = "unknown"


class GraphDirection(Enum):
    """Direction for graph traversal and layout"""

    TOP_DOWN = "TB"
    BOTTOM_UP = "BT"
    LEFT_RIGHT = "LR"
    RIGHT_LEFT = "RL"


@dataclass
class ResourceNode:
    """Represents a resource node in the dependency graph"""

    id: str
    name: str
    type: NodeType
    provider: str
    resource: Optional[BaseResource] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    drift_status: Optional[DriftResult] = None
    position: Optional[Tuple[float, float]] = None

    @property
    def display_name(self) -> str:
        """Get display name for the node"""
        return self.metadata.get("display_name", self.name)

    @property
    def is_drifted(self) -> bool:
        """Check if resource has drift"""
        return self.drift_status is not None and self.drift_status.drift_detected

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "provider": self.provider,
            "display_name": self.display_name,
            "is_drifted": self.is_drifted,
            "metadata": self.metadata,
            "position": self.position,
        }


@dataclass
class DependencyEdge:
    """Represents a dependency relationship between resources"""

    source_id: str
    target_id: str
    dependency_type: str = "depends_on"
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_critical(self) -> bool:
        """Check if this is a critical dependency"""
        return self.metadata.get("critical", True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert edge to dictionary representation"""
        return {
            "source": self.source_id,
            "target": self.target_id,
            "type": self.dependency_type,
            "critical": self.is_critical,
            "metadata": self.metadata,
        }


@dataclass
class DependencyGraph:
    """Container for the complete dependency graph"""

    nodes: Dict[str, ResourceNode] = field(default_factory=dict)
    edges: List[DependencyEdge] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_node(self, node: ResourceNode) -> None:
        """Add a node to the graph"""
        self.nodes[node.id] = node

    def add_edge(self, edge: DependencyEdge) -> None:
        """Add an edge to the graph"""
        self.edges.append(edge)

    def get_node(self, node_id: str) -> Optional[ResourceNode]:
        """Get a node by ID"""
        return self.nodes.get(node_id)

    def get_edges_from(self, node_id: str) -> List[DependencyEdge]:
        """Get all edges originating from a node"""
        return [e for e in self.edges if e.source_id == node_id]

    def get_edges_to(self, node_id: str) -> List[DependencyEdge]:
        """Get all edges pointing to a node"""
        return [e for e in self.edges if e.target_id == node_id]

    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary representation"""
        return {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges],
            "metadata": self.metadata,
        }


class DependencyGraphBuilder:
    """
    Builds dependency graphs from infrastructure resources

    This class analyzes resource relationships and constructs a
    graph representation suitable for visualization.
    """

    def __init__(self):
        """Initialize the graph builder"""
        self._type_mapping = {
            # AWS mappings
            "aws_instance": NodeType.COMPUTE,
            "aws_vpc": NodeType.NETWORK,
            "aws_subnet": NodeType.NETWORK,
            "aws_security_group": NodeType.SECURITY,
            "aws_s3_bucket": NodeType.STORAGE,
            "aws_rds_instance": NodeType.DATABASE,
            "aws_lambda_function": NodeType.FUNCTION,
            "aws_lb": NodeType.LOADBALANCER,
            "aws_route53_zone": NodeType.DNS,
            # GCP mappings
            "google_compute_instance": NodeType.COMPUTE,
            "google_compute_network": NodeType.NETWORK,
            "google_compute_subnetwork": NodeType.NETWORK,
            "google_compute_firewall": NodeType.SECURITY,
            "google_storage_bucket": NodeType.STORAGE,
            "google_sql_database_instance": NodeType.DATABASE,
            "google_cloudfunctions_function": NodeType.FUNCTION,
            "google_compute_backend_service": NodeType.LOADBALANCER,
            "google_dns_managed_zone": NodeType.DNS,
            "google_cloud_run_service": NodeType.CONTAINER,
            # DigitalOcean mappings
            "digitalocean_droplet": NodeType.COMPUTE,
            "digitalocean_vpc": NodeType.NETWORK,
            "digitalocean_firewall": NodeType.SECURITY,
            "digitalocean_spaces_bucket": NodeType.STORAGE,
            "digitalocean_database_cluster": NodeType.DATABASE,
            "digitalocean_loadbalancer": NodeType.LOADBALANCER,
            "digitalocean_domain": NodeType.DNS,
            # Kubernetes mappings
            "kubernetes_deployment": NodeType.KUBERNETES,
            "kubernetes_service": NodeType.KUBERNETES,
            "kubernetes_ingress": NodeType.KUBERNETES,
            "kubernetes_config_map": NodeType.KUBERNETES,
            "kubernetes_secret": NodeType.KUBERNETES,
        }

    def build_graph(
        self,
        resources: List[BaseResource],
        drift_results: Optional[Dict[str, DriftResult]] = None,
    ) -> DependencyGraph:
        """
        Build a dependency graph from a list of resources

        Args:
            resources: List of infrastructure resources
            drift_results: Optional drift detection results

        Returns:
            Complete dependency graph
        """
        graph = DependencyGraph()
        drift_results = drift_results or {}

        # First pass: Create nodes
        for resource in resources:
            node = self._create_node(resource, drift_results.get(resource.id))
            graph.add_node(node)

        # Second pass: Create edges
        for resource in resources:
            edges = self._analyze_dependencies(resource, resources)
            for edge in edges:
                graph.add_edge(edge)

        # Third pass: Detect circular dependencies
        circular_deps = self._detect_circular_dependencies(graph)
        if circular_deps:
            graph.metadata["circular_dependencies"] = circular_deps

        # Fourth pass: Optimize layout
        self._optimize_layout(graph)

        # Add metadata
        graph.metadata.update(
            {
                "total_nodes": len(graph.nodes),
                "total_edges": len(graph.edges),
                "drift_count": sum(1 for n in graph.nodes.values() if n.is_drifted),
                "providers": list(set(n.provider for n in graph.nodes.values())),
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
        )

        return graph

    def _create_node(
        self,
        resource: BaseResource,
        drift_result: Optional[DriftResult] = None,
    ) -> ResourceNode:
        """Create a node from a resource"""
        resource_type = self._get_resource_type(resource)
        node_type = self._type_mapping.get(resource_type, NodeType.UNKNOWN)

        metadata = {
            "resource_type": resource_type,
            "state": (
                resource.status.state.value
                if hasattr(resource, "status") and hasattr(resource.status, "state")
                else "unknown"
            ),
            "created_at": (
                resource.metadata.created_at
                if hasattr(resource, "metadata")
                and hasattr(resource.metadata, "created_at")
                else None
            ),
            "tags": resource.tags if hasattr(resource, "tags") else {},
        }

        # Add provider-specific metadata
        if hasattr(resource, "provider_config"):
            metadata["region"] = getattr(resource.provider_config, "region", None)
            metadata["zone"] = getattr(resource.provider_config, "zone", None)

        return ResourceNode(
            id=resource.id,
            name=resource.name,
            type=node_type,
            provider=self._get_provider_name(resource),
            resource=resource,
            metadata=metadata,
            drift_status=drift_result,
        )

    def _analyze_dependencies(
        self,
        resource: BaseResource,
        all_resources: List[BaseResource],
    ) -> List[DependencyEdge]:
        """Analyze and extract dependencies for a resource"""
        edges = []
        resource_map = {r.id: r for r in all_resources}

        # Check explicit dependencies
        if hasattr(resource, "depends_on"):
            for dep_id in resource.depends_on:
                if dep_id in resource_map:
                    edges.append(
                        DependencyEdge(
                            source_id=resource.id,
                            target_id=dep_id,
                            dependency_type="explicit",
                            metadata={"declared": True},
                        )
                    )

        # Check implicit dependencies (resource references)
        implicit_deps = self._find_implicit_dependencies(resource, all_resources)
        for dep_id, dep_type in implicit_deps:
            edges.append(
                DependencyEdge(
                    source_id=resource.id,
                    target_id=dep_id,
                    dependency_type=dep_type,
                    metadata={"implicit": True},
                )
            )

        return edges

    def _find_implicit_dependencies(
        self,
        resource: BaseResource,
        all_resources: List[BaseResource],
    ) -> List[Tuple[str, str]]:
        """Find implicit dependencies through resource references"""
        dependencies = []

        # Convert resource to dict for analysis
        resource_dict = resource.dict() if hasattr(resource, "dict") else {}

        # Look for resource references in configuration
        for key, value in self._flatten_dict(resource_dict):
            if isinstance(value, str):
                # Check if value references another resource
                for other in all_resources:
                    if other.id != resource.id and (
                        other.id in value
                        or other.name in value
                        or (hasattr(other, "arn") and other.arn in value)
                    ):
                        dep_type = self._infer_dependency_type(key)
                        dependencies.append((other.id, dep_type))

        return dependencies

    def _detect_circular_dependencies(self, graph: DependencyGraph) -> List[List[str]]:
        """Detect circular dependencies in the graph"""
        # Check if NetworkX is available
        if not NETWORKX_AVAILABLE:
            return []  # Skip cycle detection if NetworkX is not available

        # Build NetworkX graph for cycle detection
        nx_graph = nx.DiGraph()

        for node_id in graph.nodes:
            nx_graph.add_node(node_id)

        for edge in graph.edges:
            nx_graph.add_edge(edge.source_id, edge.target_id)

        # Find all simple cycles
        try:
            cycles = list(nx.simple_cycles(nx_graph))
            return cycles
        except Exception:
            # This catches both nx.NetworkXNoCycle and any other exceptions
            return []

    def _optimize_layout(self, graph: DependencyGraph) -> None:
        """Optimize graph layout for visualization"""
        if not graph.nodes:
            return

        # Check if NetworkX is available
        if not NETWORKX_AVAILABLE:
            self._simple_layout(graph)
            return

        try:
            # Build NetworkX graph for layout calculation
            nx_graph = nx.DiGraph()

            for node_id, node in graph.nodes.items():
                nx_graph.add_node(node_id, node=node)

            for edge in graph.edges:
                nx_graph.add_edge(edge.source_id, edge.target_id)

            # Calculate hierarchical layout
            try:
                # Try hierarchical layout first
                pos = nx.nx_agraph.graphviz_layout(nx_graph, prog="dot")
            except (ImportError, Exception):
                # Fall back to spring layout if graphviz is not available
                try:
                    pos = nx.spring_layout(nx_graph, k=2, iterations=50)
                except ImportError:
                    # If NetworkX layout functions fail due to missing numpy, use simple layout
                    pos = self._simple_layout(graph)

            # Update node positions
            for node_id, (x, y) in pos.items():
                if node_id in graph.nodes:
                    graph.nodes[node_id].position = (x, y)

        except Exception as e:
            # If any layout fails, fall back to simple positioning
            self._simple_layout(graph)

    def _simple_layout(self, graph: DependencyGraph) -> Dict[str, Tuple[float, float]]:
        """Simple circular layout fallback that doesn't require external dependencies"""
        import math

        nodes = list(graph.nodes.keys())
        if not nodes:
            return {}

        # Arrange nodes in a circle
        center_x, center_y = 400, 300
        radius = min(200, max(50, len(nodes) * 15))

        positions = {}
        for i, node_id in enumerate(nodes):
            angle = 2 * math.pi * i / len(nodes)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            positions[node_id] = (x, y)

            # Update node position directly
            if node_id in graph.nodes:
                graph.nodes[node_id].position = (x, y)

        return positions

    def _get_resource_type(self, resource: BaseResource) -> str:
        """Extract resource type from resource object"""
        if hasattr(resource, "resource_type"):
            return resource.resource_type

        # Infer from class name
        class_name = resource.__class__.__name__
        return class_name.lower()

    def _get_provider_name(self, resource: BaseResource) -> str:
        """Extract provider name from resource"""
        if hasattr(resource, "provider"):
            return resource.provider

        # Infer from module name
        module_name = resource.__class__.__module__
        if "aws" in module_name:
            return "aws"
        elif "google" in module_name or "gcp" in module_name:
            return "gcp"
        elif "digitalocean" in module_name:
            return "digitalocean"
        elif "kubernetes" in module_name or "k8s" in module_name:
            return "kubernetes"

        return "unknown"

    def _flatten_dict(
        self, d: Dict[str, Any], parent_key: str = ""
    ) -> List[Tuple[str, Any]]:
        """Flatten nested dictionary for dependency analysis"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key))
            else:
                items.append((new_key, v))
        return items

    def _infer_dependency_type(self, key: str) -> str:
        """Infer dependency type from configuration key"""
        key_lower = key.lower()

        if "subnet" in key_lower:
            return "network"
        elif "security_group" in key_lower or "firewall" in key_lower:
            return "security"
        elif "role" in key_lower or "policy" in key_lower:
            return "iam"
        elif "vpc" in key_lower or "network" in key_lower:
            return "network"
        elif "bucket" in key_lower or "storage" in key_lower:
            return "storage"
        elif "database" in key_lower or "db" in key_lower:
            return "database"

        return "reference"
