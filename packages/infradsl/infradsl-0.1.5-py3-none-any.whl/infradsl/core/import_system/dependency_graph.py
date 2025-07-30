"""
Dependency Graph Analyzer for Resource Import

This module analyzes dependencies between cloud resources to ensure
correct import order and generate clean reference-based code.
"""

from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class DependencyType(Enum):
    """Types of dependencies between resources"""
    REQUIRED = "required"      # Hard dependency - resource cannot exist without it
    REFERENCE = "reference"    # Soft dependency - references another resource
    NETWORK = "network"        # Network-level dependency (VPC, subnet, etc.)
    SECURITY = "security"      # Security-related dependency (IAM, security groups)
    STORAGE = "storage"        # Storage dependency (volumes, buckets)


@dataclass
class ResourceNode:
    """Represents a resource in the dependency graph"""
    id: str                           # Cloud resource ID
    name: str                         # Display name
    type: str                         # Resource type (aws_instance, etc.)
    provider: str                     # Cloud provider
    region: str                       # Cloud region
    metadata: Dict[str, Any]          # Additional resource metadata
    attributes: Dict[str, Any]        # Resource configuration
    tags: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Generate a Python-friendly variable name"""
        self.variable_name = self._generate_variable_name()
    
    def _generate_variable_name(self) -> str:
        """Generate a Python variable name from resource name/tags"""
        # Try Name tag first
        if name_tag := self.tags.get("Name"):
            return self._pythonize_name(name_tag)
        
        # Try to generate from resource type + identifiers
        type_part = self.type.replace("aws_", "").replace("gcp_", "")
        
        # Add distinguishing attributes
        parts = [type_part]
        
        if self.metadata.get("availability_zone"):
            az = self.metadata["availability_zone"].split("-")[-1]  # e.g., "1a"
            parts.append(az)
        
        if self.metadata.get("environment"):
            parts.insert(0, self.metadata["environment"])
            
        return "_".join(parts)
    
    def _pythonize_name(self, name: str) -> str:
        """Convert a name to a valid Python variable name"""
        # Replace invalid characters with underscores
        import re
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        
        # Ensure it starts with a letter or underscore
        if name and name[0].isdigit():
            name = f"resource_{name}"
        
        # Convert to lowercase
        return name.lower()


@dataclass
class DependencyEdge:
    """Represents a dependency relationship between resources"""
    from_resource: str              # ID of the dependent resource
    to_resource: str                # ID of the dependency
    dependency_type: DependencyType # Type of dependency
    attribute: str                  # Which attribute creates the dependency
    description: str = ""           # Human-readable description
    required: bool = True           # Whether this is a hard requirement


class CircularDependencyError(Exception):
    """Raised when circular dependencies are detected"""
    def __init__(self, cycle: List[str]):
        self.cycle = cycle
        super().__init__(f"Circular dependency detected: {' -> '.join(cycle)}")


class DependencyGraph:
    """
    Dependency graph analyzer for cloud resources.
    
    Builds and analyzes dependency relationships between resources
    to enable correct import ordering and code generation.
    """
    
    def __init__(self):
        self.nodes: Dict[str, ResourceNode] = {}
        self.edges: List[DependencyEdge] = []
        self._adjacency_list: Dict[str, Set[str]] = defaultdict(set)
        self._reverse_adjacency: Dict[str, Set[str]] = defaultdict(set)
        self._analyzed = False
    
    def add_resource(self, resource_id: str, name: str, resource_type: str,
                    provider: str, region: str, attributes: Dict[str, Any],
                    metadata: Optional[Dict[str, Any]] = None,
                    tags: Optional[Dict[str, str]] = None) -> ResourceNode:
        """Add a resource to the dependency graph"""
        node = ResourceNode(
            id=resource_id,
            name=name,
            type=resource_type,
            provider=provider,
            region=region,
            metadata=metadata or {},
            attributes=attributes,
            tags=tags or {}
        )
        
        self.nodes[resource_id] = node
        self._analyzed = False
        
        logger.debug(f"Added resource {resource_id} ({resource_type}) to dependency graph")
        return node
    
    def add_dependency(self, from_resource: str, to_resource: str,
                      dependency_type: DependencyType, attribute: str,
                      description: str = "", required: bool = True) -> None:
        """Add a dependency relationship between resources"""
        if from_resource not in self.nodes:
            raise ValueError(f"Resource {from_resource} not found in graph")
        if to_resource not in self.nodes:
            raise ValueError(f"Resource {to_resource} not found in graph")
        
        edge = DependencyEdge(
            from_resource=from_resource,
            to_resource=to_resource,
            dependency_type=dependency_type,
            attribute=attribute,
            description=description,
            required=required
        )
        
        self.edges.append(edge)
        self._adjacency_list[from_resource].add(to_resource)
        self._reverse_adjacency[to_resource].add(from_resource)
        self._analyzed = False
        
        logger.debug(f"Added dependency: {from_resource} -> {to_resource} ({dependency_type.value})")
    
    def analyze_dependencies(self) -> None:
        """Analyze all resources and automatically detect dependencies"""
        logger.info(f"Analyzing dependencies for {len(self.nodes)} resources")
        
        for resource_id, node in self.nodes.items():
            self._analyze_resource_dependencies(node)
        
        self._analyzed = True
        logger.info(f"Dependency analysis complete. Found {len(self.edges)} dependencies")
    
    def _analyze_resource_dependencies(self, node: ResourceNode) -> None:
        """Analyze dependencies for a specific resource"""
        resource_type = node.type
        attributes = node.attributes
        
        # AWS EC2 Instance dependencies
        if resource_type == "aws_instance":
            self._analyze_ec2_dependencies(node)
        
        # AWS RDS Instance dependencies
        elif resource_type == "aws_db_instance":
            self._analyze_rds_dependencies(node)
        
        # AWS Subnet dependencies
        elif resource_type == "aws_subnet":
            self._analyze_subnet_dependencies(node)
        
        # AWS Security Group dependencies
        elif resource_type == "aws_security_group":
            self._analyze_security_group_dependencies(node)
        
        # AWS Load Balancer dependencies
        elif resource_type in ["aws_lb", "aws_alb", "aws_nlb"]:
            self._analyze_load_balancer_dependencies(node)
        
        # GCP Compute Instance dependencies
        elif resource_type == "google_compute_instance":
            self._analyze_gcp_instance_dependencies(node)
        
        # Add more resource types as needed
        else:
            logger.debug(f"No dependency analysis available for resource type: {resource_type}")
    
    def _analyze_ec2_dependencies(self, node: ResourceNode) -> None:
        """Analyze AWS EC2 instance dependencies"""
        attrs = node.attributes
        
        # VPC dependency (via subnet)
        if subnet_id := attrs.get("subnet_id"):
            if subnet_id in self.nodes:
                self.add_dependency(
                    node.id, subnet_id,
                    DependencyType.NETWORK, "subnet_id",
                    "EC2 instance requires subnet"
                )
        
        # Security Group dependencies
        if security_groups := attrs.get("security_group_ids", []):
            for sg_id in security_groups:
                if sg_id in self.nodes:
                    self.add_dependency(
                        node.id, sg_id,
                        DependencyType.SECURITY, "security_group_ids",
                        "EC2 instance requires security group"
                    )
        
        # IAM Role dependency
        if iam_profile := attrs.get("iam_instance_profile"):
            # Extract role name from instance profile
            if isinstance(iam_profile, dict):
                role_name = iam_profile.get("name")
            else:
                role_name = iam_profile
            
            if role_name and role_name in self.nodes:
                self.add_dependency(
                    node.id, role_name,
                    DependencyType.SECURITY, "iam_instance_profile",
                    "EC2 instance requires IAM role"
                )
        
        # Key Pair dependency
        if key_name := attrs.get("key_name"):
            if key_name in self.nodes:
                self.add_dependency(
                    node.id, key_name,
                    DependencyType.SECURITY, "key_name",
                    "EC2 instance requires key pair",
                    required=False  # Soft dependency
                )
    
    def _analyze_rds_dependencies(self, node: ResourceNode) -> None:
        """Analyze AWS RDS instance dependencies"""
        attrs = node.attributes
        
        # DB Subnet Group dependency
        if subnet_group := attrs.get("db_subnet_group_name"):
            if subnet_group in self.nodes:
                self.add_dependency(
                    node.id, subnet_group,
                    DependencyType.NETWORK, "db_subnet_group_name",
                    "RDS instance requires subnet group"
                )
        
        # Security Group dependencies
        if security_groups := attrs.get("vpc_security_group_ids", []):
            for sg_id in security_groups:
                if sg_id in self.nodes:
                    self.add_dependency(
                        node.id, sg_id,
                        DependencyType.SECURITY, "vpc_security_group_ids",
                        "RDS instance requires security group"
                    )
    
    def _analyze_subnet_dependencies(self, node: ResourceNode) -> None:
        """Analyze AWS subnet dependencies"""
        attrs = node.attributes
        
        # VPC dependency
        if vpc_id := attrs.get("vpc_id"):
            if vpc_id in self.nodes:
                self.add_dependency(
                    node.id, vpc_id,
                    DependencyType.NETWORK, "vpc_id",
                    "Subnet requires VPC"
                )
        
        # Route Table dependency
        if route_table_id := attrs.get("route_table_id"):
            if route_table_id in self.nodes:
                self.add_dependency(
                    node.id, route_table_id,
                    DependencyType.NETWORK, "route_table_id",
                    "Subnet requires route table",
                    required=False
                )
    
    def _analyze_security_group_dependencies(self, node: ResourceNode) -> None:
        """Analyze AWS security group dependencies"""
        attrs = node.attributes
        
        # VPC dependency
        if vpc_id := attrs.get("vpc_id"):
            if vpc_id in self.nodes:
                self.add_dependency(
                    node.id, vpc_id,
                    DependencyType.NETWORK, "vpc_id",
                    "Security group requires VPC"
                )
        
        # Security group rule dependencies (references to other SGs)
        for rule_type in ["ingress", "egress"]:
            if rules := attrs.get(rule_type, []):
                for rule in rules:
                    if sg_refs := rule.get("security_groups", []):
                        for sg_ref in sg_refs:
                            if sg_ref in self.nodes and sg_ref != node.id:
                                self.add_dependency(
                                    node.id, sg_ref,
                                    DependencyType.SECURITY, f"{rule_type}_rule",
                                    f"Security group references other security group",
                                    required=False
                                )
    
    def _analyze_load_balancer_dependencies(self, node: ResourceNode) -> None:
        """Analyze AWS Load Balancer dependencies"""
        attrs = node.attributes
        
        # Subnet dependencies
        if subnets := attrs.get("subnets", []):
            for subnet_id in subnets:
                if subnet_id in self.nodes:
                    self.add_dependency(
                        node.id, subnet_id,
                        DependencyType.NETWORK, "subnets",
                        "Load balancer requires subnet"
                    )
        
        # Security Group dependencies
        if security_groups := attrs.get("security_groups", []):
            for sg_id in security_groups:
                if sg_id in self.nodes:
                    self.add_dependency(
                        node.id, sg_id,
                        DependencyType.SECURITY, "security_groups",
                        "Load balancer requires security group"
                    )
    
    def _analyze_gcp_instance_dependencies(self, node: ResourceNode) -> None:
        """Analyze GCP Compute instance dependencies"""
        attrs = node.attributes
        
        # Network interface dependencies
        if network_interfaces := attrs.get("network_interface", []):
            for interface in network_interfaces:
                # Subnet dependency
                if subnetwork := interface.get("subnetwork"):
                    if subnetwork in self.nodes:
                        self.add_dependency(
                            node.id, subnetwork,
                            DependencyType.NETWORK, "network_interface.subnetwork",
                            "GCP instance requires subnet"
                        )
        
        # Service account dependency
        if service_account := attrs.get("service_account"):
            if isinstance(service_account, list) and service_account:
                sa_email = service_account[0].get("email")
                if sa_email and sa_email in self.nodes:
                    self.add_dependency(
                        node.id, sa_email,
                        DependencyType.SECURITY, "service_account",
                        "GCP instance requires service account",
                        required=False
                    )
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in the graph"""
        if not self._analyzed:
            self.analyze_dependencies()
        
        visited = set()
        recursion_stack = set()
        cycles = []
        
        def dfs(node: str, path: List[str]) -> None:
            if node in recursion_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            recursion_stack.add(node)
            path.append(node)
            
            for neighbor in self._adjacency_list[node]:
                dfs(neighbor, path.copy())
            
            recursion_stack.remove(node)
        
        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id, [])
        
        return cycles
    
    def topological_sort(self) -> List[ResourceNode]:
        """
        Return resources in dependency order using Kahn's algorithm.
        
        Resources with no dependencies come first, followed by resources
        that depend on them, etc.
        """
        if not self._analyzed:
            self.analyze_dependencies()
        
        # Check for circular dependencies first
        cycles = self.detect_circular_dependencies()
        if cycles:
            logger.error(f"Circular dependencies detected: {cycles}")
            raise CircularDependencyError(cycles[0])  # Raise first cycle found
        
        # Kahn's algorithm implementation
        in_degree = defaultdict(int)
        
        # Calculate in-degrees
        for node_id in self.nodes:
            in_degree[node_id] = 0
        
        for edge in self.edges:
            if edge.required:  # Only count required dependencies
                in_degree[edge.from_resource] += 1
        
        # Initialize queue with nodes that have no dependencies
        queue = deque([node_id for node_id, degree in in_degree.items() if degree == 0])
        result = []
        
        while queue:
            current = queue.popleft()
            result.append(self.nodes[current])
            
            # Reduce in-degree for all dependents
            for dependent in self._reverse_adjacency[current]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        # Verify all nodes were processed
        if len(result) != len(self.nodes):
            unprocessed = set(self.nodes.keys()) - {node.id for node in result}
            logger.error(f"Failed to process all nodes. Unprocessed: {unprocessed}")
            raise CircularDependencyError(list(unprocessed))
        
        logger.info(f"Topological sort complete. Ordered {len(result)} resources")
        return result
    
    def get_dependencies(self, resource_id: str) -> List[Tuple[ResourceNode, DependencyEdge]]:
        """Get all dependencies for a specific resource"""
        dependencies = []
        
        for edge in self.edges:
            if edge.from_resource == resource_id:
                dependency_node = self.nodes[edge.to_resource]
                dependencies.append((dependency_node, edge))
        
        return dependencies
    
    def get_dependents(self, resource_id: str) -> List[Tuple[ResourceNode, DependencyEdge]]:
        """Get all resources that depend on this resource"""
        dependents = []
        
        for edge in self.edges:
            if edge.to_resource == resource_id:
                dependent_node = self.nodes[edge.from_resource]
                dependents.append((dependent_node, edge))
        
        return dependents
    
    def get_layer_groups(self) -> List[List[ResourceNode]]:
        """
        Group resources into dependency layers.
        
        Layer 0: Resources with no dependencies
        Layer 1: Resources that only depend on Layer 0
        Layer 2: Resources that depend on Layer 0 or 1
        etc.
        """
        if not self._analyzed:
            self.analyze_dependencies()
        
        layers = []
        remaining = set(self.nodes.keys())
        processed = set()
        
        while remaining:
            current_layer = []
            
            # Find nodes that have all dependencies satisfied
            for node_id in remaining.copy():
                dependencies = [edge.to_resource for edge in self.edges 
                              if edge.from_resource == node_id and edge.required]
                
                if all(dep in processed for dep in dependencies):
                    current_layer.append(self.nodes[node_id])
                    remaining.remove(node_id)
                    processed.add(node_id)
            
            if not current_layer and remaining:
                # No progress made - likely circular dependency
                raise CircularDependencyError(list(remaining))
            
            layers.append(current_layer)
        
        return layers
    
    def export_dot(self) -> str:
        """Export the dependency graph in DOT format for visualization"""
        if not self._analyzed:
            self.analyze_dependencies()
        
        lines = ["digraph DependencyGraph {", "  rankdir=TB;", "  node [shape=box];", ""]
        
        # Add nodes
        for node in self.nodes.values():
            label = f"{node.variable_name}\\n({node.type})"
            lines.append(f'  "{node.id}" [label="{label}"];')
        
        lines.append("")
        
        # Add edges
        for edge in self.edges:
            style = "solid" if edge.required else "dashed"
            color = {
                DependencyType.NETWORK: "blue",
                DependencyType.SECURITY: "red", 
                DependencyType.STORAGE: "green",
                DependencyType.REQUIRED: "black",
                DependencyType.REFERENCE: "gray"
            }.get(edge.dependency_type, "black")
            
            lines.append(f'  "{edge.to_resource}" -> "{edge.from_resource}" [style={style}, color={color}];')
        
        lines.append("}")
        return "\n".join(lines)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get dependency graph statistics"""
        if not self._analyzed:
            self.analyze_dependencies()
        
        dependency_counts = defaultdict(int)
        for edge in self.edges:
            dependency_counts[edge.dependency_type] += 1
        
        return {
            "total_resources": len(self.nodes),
            "total_dependencies": len(self.edges),
            "dependency_types": dict(dependency_counts),
            "average_dependencies_per_resource": len(self.edges) / len(self.nodes) if self.nodes else 0,
            "resources_with_no_dependencies": len([
                node for node in self.nodes.values()
                if not any(edge.from_resource == node.id for edge in self.edges)
            ]),
            "circular_dependencies": len(self.detect_circular_dependencies())
        }