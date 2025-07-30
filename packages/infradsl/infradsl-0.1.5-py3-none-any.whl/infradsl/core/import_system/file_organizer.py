"""
Intelligent File Organization System for Resource Import

This module provides multiple strategies for organizing imported resources
into logical, maintainable file structures with proper dependency relationships.
"""

from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import logging
from collections import defaultdict

from .dependency_graph import ResourceNode, DependencyGraph

logger = logging.getLogger(__name__)


class OrganizationStrategy(Enum):
    """File organization strategies"""
    SERVICE = "service"              # Group by service type (compute, network, database)
    ENVIRONMENT = "environment"      # Group by environment (prod, staging, dev)
    LAYER = "layer"                 # Group by dependency layer (base, security, compute, data)
    HYBRID = "hybrid"               # Combination of strategies
    CUSTOM = "custom"               # User-defined organization


@dataclass
class FileGroup:
    """Represents a group of resources that belong in the same file"""
    path: str                                    # Relative file path
    name: str                                    # Display name
    resources: List[ResourceNode] = field(default_factory=list)
    imports: Set[str] = field(default_factory=set)  # Required imports
    description: str = ""                        # File description
    priority: int = 0                           # Creation order priority
    
    def add_resource(self, resource: ResourceNode) -> None:
        """Add a resource to this file group"""
        self.resources.append(resource)
    
    def add_import(self, import_path: str) -> None:
        """Add a required import to this file group"""
        self.imports.add(import_path)


class FileOrganizer:
    """
    Intelligent file organization system for imported resources.
    
    Takes a dependency graph and organizes resources into logical
    file structures based on the selected organization strategy.
    """
    
    def __init__(self, strategy: OrganizationStrategy = OrganizationStrategy.SERVICE):
        self.strategy = strategy
        self.file_groups: Dict[str, FileGroup] = {}
        self._resource_type_mappings = self._build_resource_type_mappings()
        self._environment_priorities = {"production": 1, "staging": 2, "development": 3}
    
    def _build_resource_type_mappings(self) -> Dict[str, str]:
        """Build mappings from resource types to service categories"""
        return {
            # AWS Compute
            "aws_instance": "compute",
            "aws_launch_template": "compute", 
            "aws_autoscaling_group": "compute",
            "aws_ecs_cluster": "compute",
            "aws_ecs_service": "compute",
            "aws_ecs_task_definition": "compute",
            "aws_eks_cluster": "compute",
            "aws_lambda_function": "compute",
            
            # AWS Network
            "aws_vpc": "network",
            "aws_subnet": "network",
            "aws_internet_gateway": "network",
            "aws_nat_gateway": "network",
            "aws_route_table": "network",
            "aws_route": "network",
            "aws_security_group": "network",
            "aws_network_acl": "network",
            "aws_lb": "network",
            "aws_alb": "network",
            "aws_nlb": "network",
            "aws_api_gateway": "network",
            
            # AWS Database
            "aws_db_instance": "database",
            "aws_db_cluster": "database",
            "aws_db_subnet_group": "database",
            "aws_db_parameter_group": "database",
            "aws_elasticache_cluster": "database",
            "aws_elasticache_subnet_group": "database",
            "aws_dynamodb_table": "database",
            
            # AWS Storage
            "aws_s3_bucket": "storage",
            "aws_s3_bucket_policy": "storage",
            "aws_ebs_volume": "storage",
            "aws_efs_file_system": "storage",
            "aws_efs_mount_target": "storage",
            
            # AWS Security/IAM
            "aws_iam_role": "security",
            "aws_iam_policy": "security", 
            "aws_iam_role_policy_attachment": "security",
            "aws_iam_instance_profile": "security",
            "aws_iam_user": "security",
            "aws_iam_group": "security",
            "aws_kms_key": "security",
            "aws_kms_alias": "security",
            "aws_key_pair": "security",
            
            # AWS Monitoring
            "aws_cloudwatch_log_group": "monitoring",
            "aws_cloudwatch_metric_alarm": "monitoring",
            "aws_sns_topic": "monitoring",
            "aws_sqs_queue": "monitoring",
            
            # GCP Compute
            "google_compute_instance": "compute",
            "google_compute_instance_template": "compute",
            "google_compute_instance_group": "compute",
            "google_compute_autoscaler": "compute",
            "google_container_cluster": "compute",
            "google_container_node_pool": "compute",
            "google_cloud_run_service": "compute",
            "google_cloudfunctions_function": "compute",
            
            # GCP Network
            "google_compute_network": "network",
            "google_compute_subnetwork": "network",
            "google_compute_router": "network",
            "google_compute_router_nat": "network",
            "google_compute_firewall": "network",
            "google_compute_global_forwarding_rule": "network",
            "google_compute_forwarding_rule": "network",
            "google_compute_target_pool": "network",
            "google_compute_backend_service": "network",
            
            # GCP Database  
            "google_sql_database_instance": "database",
            "google_sql_database": "database",
            "google_sql_user": "database",
            "google_redis_instance": "database",
            "google_bigtable_instance": "database",
            "google_firestore_database": "database",
            
            # GCP Storage
            "google_storage_bucket": "storage",
            "google_storage_bucket_object": "storage",
            "google_compute_disk": "storage",
            
            # GCP Security/IAM
            "google_service_account": "security",
            "google_service_account_key": "security",
            "google_project_iam_binding": "security",
            "google_project_iam_member": "security",
            "google_kms_key_ring": "security",
            "google_kms_crypto_key": "security",
        }
    
    def organize(self, dependency_graph: DependencyGraph,
                output_directory: str = "infrastructure") -> Dict[str, FileGroup]:
        """
        Organize resources into file groups based on the selected strategy.
        
        Args:
            dependency_graph: Analyzed dependency graph
            output_directory: Base output directory
        
        Returns:
            Dictionary mapping file paths to FileGroup objects
        """
        logger.info(f"Organizing resources using {self.strategy.value} strategy")
        
        if self.strategy == OrganizationStrategy.SERVICE:
            return self._organize_by_service(dependency_graph, output_directory)
        elif self.strategy == OrganizationStrategy.ENVIRONMENT:
            return self._organize_by_environment(dependency_graph, output_directory)
        elif self.strategy == OrganizationStrategy.LAYER:
            return self._organize_by_layer(dependency_graph, output_directory)
        elif self.strategy == OrganizationStrategy.HYBRID:
            return self._organize_hybrid(dependency_graph, output_directory)
        else:
            raise ValueError(f"Unsupported organization strategy: {self.strategy}")
    
    def _organize_by_service(self, graph: DependencyGraph,
                           base_dir: str) -> Dict[str, FileGroup]:
        """Organize resources by service type (compute, network, database, etc.)"""
        file_groups = {}
        service_resources = defaultdict(list)
        
        # Group resources by service type
        for resource in graph.nodes.values():
            service = self._get_service_type(resource)
            service_resources[service].append(resource)
        
        # Create file groups for each service
        for service, resources in service_resources.items():
            # Further subdivide large services
            if service in ["compute", "network"] and len(resources) > 15:
                subgroups = self._subdivide_service_resources(service, resources)
                for subgroup_name, subgroup_resources in subgroups.items():
                    path = f"{base_dir}/{service}/{subgroup_name}.py"
                    file_group = FileGroup(
                        path=path,
                        name=f"{service.title()} - {subgroup_name.title()}",
                        description=f"{subgroup_name.title()} resources for {service}"
                    )
                    for resource in subgroup_resources:
                        file_group.add_resource(resource)
                    file_groups[path] = file_group
            else:
                # Create single file for service
                filename = self._get_service_filename(service, resources)
                path = f"{base_dir}/{service}/{filename}.py"
                file_group = FileGroup(
                    path=path,
                    name=service.title(),
                    description=f"{service.title()} infrastructure resources"
                )
                for resource in resources:
                    file_group.add_resource(resource)
                file_groups[path] = file_group
        
        # Create import manifest
        manifest_path = f"{base_dir}/_imports.py"
        file_groups[manifest_path] = self._create_import_manifest(file_groups)
        
        return file_groups
    
    def _organize_by_environment(self, graph: DependencyGraph,
                               base_dir: str) -> Dict[str, FileGroup]:
        """Organize resources by environment (production, staging, development)"""
        file_groups = {}
        env_resources = defaultdict(lambda: defaultdict(list))
        
        # Group resources by environment and service
        for resource in graph.nodes.values():
            environment = self._get_environment(resource)
            service = self._get_service_type(resource)
            env_resources[environment][service].append(resource)
        
        # Create file groups for each environment/service combination
        for environment, services in env_resources.items():
            for service, resources in services.items():
                filename = service if len(services) > 1 else "infrastructure"
                path = f"{base_dir}/{environment}/{filename}.py"
                
                file_group = FileGroup(
                    path=path,
                    name=f"{environment.title()} - {service.title()}",
                    description=f"{service.title()} resources for {environment} environment",
                    priority=self._environment_priorities.get(environment, 99)
                )
                
                for resource in resources:
                    file_group.add_resource(resource)
                
                file_groups[path] = file_group
        
        return file_groups
    
    def _organize_by_layer(self, graph: DependencyGraph,
                         base_dir: str) -> Dict[str, FileGroup]:
        """Organize resources by dependency layer (base, security, compute, data, edge)"""
        file_groups = {}
        layer_groups = graph.get_layer_groups()
        
        layer_names = ["base", "security", "compute", "data", "edge"]
        
        for i, layer_resources in enumerate(layer_groups):
            # Determine layer name based on resource types
            layer_name = self._determine_layer_name(layer_resources, i)
            
            # Group resources by service within layer
            service_groups = defaultdict(list)
            for resource in layer_resources:
                service = self._get_service_type(resource)
                service_groups[service].append(resource)
            
            # Create files for each service in the layer
            for service, resources in service_groups.items():
                if len(service_groups) == 1:
                    # Single service in layer
                    path = f"{base_dir}/{layer_name}.py"
                    name = layer_name.title()
                else:
                    # Multiple services in layer
                    path = f"{base_dir}/{layer_name}_{service}.py"
                    name = f"{layer_name.title()} - {service.title()}"
                
                file_group = FileGroup(
                    path=path,
                    name=name,
                    description=f"{layer_name.title()} layer {service} resources",
                    priority=i
                )
                
                for resource in resources:
                    file_group.add_resource(resource)
                
                file_groups[path] = file_group
        
        return file_groups
    
    def _organize_hybrid(self, graph: DependencyGraph,
                       base_dir: str) -> Dict[str, FileGroup]:
        """Hybrid organization: base layer + environment-based organization"""
        file_groups = {}
        
        # Separate foundational resources from application resources
        foundational_types = {
            "aws_vpc", "aws_internet_gateway", "aws_nat_gateway",
            "google_compute_network", "google_compute_router"
        }
        
        foundational_resources = []
        app_resources = defaultdict(lambda: defaultdict(list))
        
        for resource in graph.nodes.values():
            if resource.type in foundational_types:
                foundational_resources.append(resource)
            else:
                environment = self._get_environment(resource)
                service = self._get_service_type(resource)
                app_resources[environment][service].append(resource)
        
        # Create shared foundation layer
        if foundational_resources:
            path = f"{base_dir}/shared/foundation.py"
            file_group = FileGroup(
                path=path,
                name="Shared Foundation",
                description="Foundational network and infrastructure resources",
                priority=0
            )
            for resource in foundational_resources:
                file_group.add_resource(resource)
            file_groups[path] = file_group
        
        # Create environment-specific files
        for environment, services in app_resources.items():
            for service, resources in services.items():
                path = f"{base_dir}/{environment}/{service}.py"
                file_group = FileGroup(
                    path=path,
                    name=f"{environment.title()} - {service.title()}",
                    description=f"{service.title()} resources for {environment} environment",
                    priority=self._environment_priorities.get(environment, 99)
                )
                for resource in resources:
                    file_group.add_resource(resource)
                file_groups[path] = file_group
        
        return file_groups
    
    def _get_service_type(self, resource: ResourceNode) -> str:
        """Determine the service type for a resource"""
        return self._resource_type_mappings.get(resource.type, "misc")
    
    def _get_environment(self, resource: ResourceNode) -> str:
        """Determine the environment for a resource"""
        # Try Environment tag first
        if env_tag := resource.tags.get("Environment"):
            return env_tag.lower()
        
        # Try to infer from resource name
        name = resource.name.lower()
        if "prod" in name:
            return "production"
        elif "stag" in name:
            return "staging"
        elif "dev" in name or "test" in name:
            return "development"
        
        # Try to infer from metadata
        if resource.metadata.get("environment"):
            return resource.metadata["environment"].lower()
        
        return "unknown"
    
    def _subdivide_service_resources(self, service: str,
                                   resources: List[ResourceNode]) -> Dict[str, List[ResourceNode]]:
        """Subdivide large service groups into smaller, logical groups"""
        if service == "compute":
            return self._subdivide_compute_resources(resources)
        elif service == "network":
            return self._subdivide_network_resources(resources)
        else:
            # Default subdivision by resource type
            subgroups = defaultdict(list)
            for resource in resources:
                resource_name = resource.type.split("_")[-1]  # e.g., "instance" from "aws_instance"
                subgroups[resource_name].append(resource)
            return dict(subgroups)
    
    def _subdivide_compute_resources(self, resources: List[ResourceNode]) -> Dict[str, List[ResourceNode]]:
        """Subdivide compute resources by purpose/tier"""
        subgroups = defaultdict(list)
        
        for resource in resources:
            # Try to categorize by name/tags
            name = resource.name.lower()
            tags = {k.lower(): v.lower() for k, v in resource.tags.items()}
            
            if any(term in name for term in ["web", "frontend", "nginx", "apache"]):
                subgroups["web_servers"].append(resource)
            elif any(term in name for term in ["app", "application", "backend", "api"]):
                subgroups["app_servers"].append(resource)
            elif any(term in name for term in ["db", "database", "mysql", "postgres"]):
                subgroups["database_servers"].append(resource)
            elif any(term in name for term in ["bastion", "jump", "ssh"]):
                subgroups["bastion_hosts"].append(resource)
            elif any(term in name for term in ["worker", "queue", "job"]):
                subgroups["worker_nodes"].append(resource)
            elif tags.get("tier") in ["web", "app", "database", "cache"]:
                subgroups[f"{tags['tier']}_servers"].append(resource)
            elif resource.type in ["aws_lambda_function", "google_cloudfunctions_function"]:
                subgroups["serverless"].append(resource)
            elif resource.type in ["aws_ecs_cluster", "aws_eks_cluster", "google_container_cluster"]:
                subgroups["containers"].append(resource)
            else:
                subgroups["instances"].append(resource)
        
        return dict(subgroups)
    
    def _subdivide_network_resources(self, resources: List[ResourceNode]) -> Dict[str, List[ResourceNode]]:
        """Subdivide network resources by function"""
        subgroups = defaultdict(list)
        
        for resource in resources:
            if resource.type in ["aws_vpc", "google_compute_network"]:
                subgroups["vpc"].append(resource)
            elif resource.type in ["aws_subnet", "google_compute_subnetwork"]:
                subgroups["subnets"].append(resource)
            elif "security_group" in resource.type or "firewall" in resource.type:
                subgroups["security_groups"].append(resource)
            elif "gateway" in resource.type or "nat" in resource.type:
                subgroups["gateways"].append(resource)
            elif "route" in resource.type:
                subgroups["routing"].append(resource)
            elif "lb" in resource.type or "balancer" in resource.type:
                subgroups["load_balancers"].append(resource)
            else:
                subgroups["network"].append(resource)
        
        return dict(subgroups)
    
    def _get_service_filename(self, service: str, resources: List[ResourceNode]) -> str:
        """Generate an appropriate filename for a service group"""
        if len(resources) == 1:
            return resources[0].variable_name
        
        # Use service name with resource count
        return f"{service}"
    
    def _determine_layer_name(self, resources: List[ResourceNode], layer_index: int) -> str:
        """Determine appropriate layer name based on resource types"""
        resource_types = {r.type for r in resources}
        
        # Foundation layer (VPCs, networks)
        if any("vpc" in rt or "network" in rt for rt in resource_types):
            return "foundation"
        
        # Security layer (security groups, IAM)
        if any("security" in rt or "iam" in rt for rt in resource_types):
            return "security"
        
        # Compute layer (instances, containers)
        if any("instance" in rt or "compute" in rt for rt in resource_types):
            return "compute"
        
        # Data layer (databases, storage)
        if any("db" in rt or "storage" in rt or "bucket" in rt for rt in resource_types):
            return "data"
        
        # Default naming
        return f"layer_{layer_index + 1}"
    
    def _create_import_manifest(self, file_groups: Dict[str, FileGroup]) -> FileGroup:
        """Create an import manifest file that imports all resource files"""
        manifest = FileGroup(
            path="_imports.py",
            name="Import Manifest",
            description="Imports all infrastructure resources for dependency resolution"
        )
        
        # Add imports for all other files
        for path, file_group in file_groups.items():
            if path != "_imports.py" and file_group.resources:
                # Convert file path to import statement
                import_path = path.replace("/", ".").replace(".py", "")
                manifest.add_import(import_path)
        
        return manifest
    
    def calculate_import_dependencies(self, file_groups: Dict[str, FileGroup],
                                    dependency_graph: DependencyGraph) -> None:
        """Calculate and set import dependencies between file groups"""
        # Create mapping from resource ID to file path
        resource_to_file = {}
        for path, file_group in file_groups.items():
            for resource in file_group.resources:
                resource_to_file[resource.id] = path
        
        # Calculate imports for each file group
        for path, file_group in file_groups.items():
            required_imports = set()
            
            for resource in file_group.resources:
                # Get dependencies for this resource
                dependencies, _ = zip(*dependency_graph.get_dependencies(resource.id)) if dependency_graph.get_dependencies(resource.id) else ([], [])
                
                for dep_resource in dependencies:
                    dep_file_path = resource_to_file.get(dep_resource.id)
                    if dep_file_path and dep_file_path != path:
                        # Convert file path to relative import
                        import_path = self._calculate_relative_import(path, dep_file_path)
                        required_imports.add(import_path)
            
            file_group.imports.update(required_imports)
    
    def _calculate_relative_import(self, from_path: str, to_path: str) -> str:
        """Calculate relative import path between two files"""
        from_parts = Path(from_path).parent.parts
        to_parts = Path(to_path).parts
        
        # Calculate relative path
        common_path = []
        for i, (from_part, to_part) in enumerate(zip(from_parts, to_parts)):
            if from_part == to_part:
                common_path.append(from_part)
            else:
                break
        
        # Calculate how many levels to go up
        levels_up = len(from_parts) - len(common_path)
        
        # Build relative import
        if levels_up == 0:
            # Same directory
            return f".{Path(to_path).stem}"
        elif levels_up == 1:
            # One level up
            remaining_path = "/".join(to_parts[len(common_path):])
            module_path = Path(remaining_path).with_suffix("").as_posix().replace("/", ".")
            return f"..{module_path}"
        else:
            # Multiple levels up
            dots = "." * (levels_up + 1)
            remaining_path = "/".join(to_parts[len(common_path):])
            module_path = Path(remaining_path).with_suffix("").as_posix().replace("/", ".")
            return f"{dots}{module_path}"
    
    def get_creation_order(self, file_groups: Dict[str, FileGroup]) -> List[str]:
        """Get the order in which files should be created based on dependencies"""
        # Sort by priority first, then by path for deterministic ordering
        sorted_groups = sorted(
            file_groups.items(),
            key=lambda x: (x[1].priority, x[0])
        )
        
        return [path for path, _ in sorted_groups]
    
    def get_statistics(self, file_groups: Dict[str, FileGroup]) -> Dict[str, Any]:
        """Get organization statistics"""
        total_resources = sum(len(fg.resources) for fg in file_groups.values())
        
        files_by_size = defaultdict(int)
        for file_group in file_groups.values():
            size_bucket = len(file_group.resources) // 5 * 5  # Round to nearest 5
            files_by_size[f"{size_bucket}-{size_bucket+4}"] += 1
        
        return {
            "total_files": len(file_groups),
            "total_resources": total_resources,
            "average_resources_per_file": total_resources / len(file_groups) if file_groups else 0,
            "files_by_size": dict(files_by_size),
            "organization_strategy": self.strategy.value,
            "largest_file": max(
                (fg.path for fg in file_groups.values() if fg.resources),
                key=lambda path: len(file_groups[path].resources),
                default="none"
            )
        }