"""
Code Generator for Resource Import

This module generates clean, maintainable InfraDSL Python code from
imported cloud resources with proper dependency references and formatting.
"""

from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging
from textwrap import indent
import json
import re
from collections import defaultdict

from .dependency_graph import ResourceNode, DependencyGraph, DependencyEdge
from .file_organizer import FileGroup, FileOrganizer

logger = logging.getLogger(__name__)


@dataclass
class ImportStatement:
    """Represents a Python import statement"""
    module: str              # Module to import from
    items: List[str]         # Items to import
    alias: Optional[str] = None  # Optional alias
    is_relative: bool = False    # Whether it's a relative import
    
    def __str__(self) -> str:
        if self.items:
            items_str = ", ".join(self.items)
            if len(self.items) == 1 and not self.alias:
                return f"from {self.module} import {items_str}"
            else:
                return f"from {self.module} import {items_str}"
        else:
            if self.alias:
                return f"import {self.module} as {self.alias}"
            else:
                return f"import {self.module}"


class CodeGenerator:
    """
    Generates clean InfraDSL Python code from imported resources.
    
    Creates properly formatted Python files with:
    - Clean imports with dependency references
    - Chainable method calls matching InfraDSL patterns
    - Proper variable naming and code organization
    - Type hints and documentation
    """
    
    def __init__(self):
        self.indent_size = 4
        self.max_line_length = 100
        self._resource_factories = self._build_resource_factories()
    
    def _build_resource_factories(self) -> Dict[str, str]:
        """Build mapping from resource types to InfraDSL factory methods"""
        return {
            # AWS Resources
            "aws_instance": "AWS.EC2",
            "aws_vpc": "AWS.VPC", 
            "aws_subnet": "AWS.Subnet",
            "aws_security_group": "AWS.SecurityGroup",
            "aws_internet_gateway": "AWS.InternetGateway",
            "aws_nat_gateway": "AWS.NATGateway",
            "aws_route_table": "AWS.RouteTable",
            "aws_lb": "AWS.LoadBalancer",
            "aws_alb": "AWS.ALB",
            "aws_nlb": "AWS.NLB",
            "aws_db_instance": "AWS.RDS",
            "aws_db_subnet_group": "AWS.DBSubnetGroup",
            "aws_s3_bucket": "AWS.S3",
            "aws_iam_role": "AWS.IAMRole",
            "aws_iam_policy": "AWS.IAMPolicy",
            "aws_key_pair": "AWS.KeyPair",
            "aws_lambda_function": "AWS.Lambda",
            "aws_ecs_cluster": "AWS.ECSCluster",
            "aws_ecs_service": "AWS.ECSService",
            
            # GCP Resources
            "google_compute_instance": "GCP.ComputeEngine",
            "google_compute_network": "VPCNetwork",
            "google_compute_subnetwork": "VPCNetwork", 
            "google_compute_firewall": "GCP.Firewall",
            "google_compute_router": "GCP.Router",
            "google_compute_forwarding_rule": "GCP.LoadBalancer",
            "google_sql_database_instance": "GCP.CloudSQL",
            "google_storage_bucket": "GCP.CloudStorage",
            "google_service_account": "GCP.ServiceAccount",
            "google_container_cluster": "GCP.GKE",
            "google_cloud_run_service": "CloudRun",
            
            # DigitalOcean Resources
            "digitalocean_droplet": "DigitalOcean.Droplet",
            "digitalocean_vpc": "DigitalOcean.VPC",
            "digitalocean_database_cluster": "DigitalOcean.Database",
            "digitalocean_loadbalancer": "DigitalOcean.LoadBalancer",
            "digitalocean_spaces_bucket": "DigitalOcean.Space",
        }
    
    def generate_file(self, file_group: FileGroup, 
                     dependency_graph: DependencyGraph,
                     all_file_groups: Dict[str, FileGroup]) -> str:
        """
        Generate Python code for a file group.
        
        Args:
            file_group: The file group to generate code for
            dependency_graph: Complete dependency graph
            all_file_groups: All file groups for reference resolution
        
        Returns:
            Generated Python code as a string
        """
        logger.debug(f"Generating code for {file_group.path}")
        
        lines = []
        
        # File header
        lines.extend(self._generate_file_header(file_group))
        lines.append("")
        
        # Imports
        import_lines = self._generate_imports(file_group, all_file_groups)
        if import_lines:
            lines.extend(import_lines)
            lines.append("")
        
        # Resource definitions
        resource_count = 0
        for resource in file_group.resources:
            # Skip GCP subnets - they're handled within VPC
            if resource.type == "google_compute_subnetwork":
                continue
                
            if resource_count > 0:
                lines.append("")  # Blank line between resources
            
            resource_lines = self._generate_resource_code(
                resource, dependency_graph, all_file_groups
            )
            lines.extend(resource_lines)
            resource_count += 1
        
        # Export list (optional)
        if len(file_group.resources) > 1:
            lines.append("")
            lines.extend(self._generate_exports(file_group.resources))
        
        return "\n".join(lines)
    
    def _generate_file_header(self, file_group: FileGroup) -> List[str]:
        """Generate file header with docstring"""
        lines = [
            '"""',
            f"{file_group.name}",
            "",
            f"{file_group.description}",
            "",
            "This file was automatically generated by InfraDSL import.",
            "You can modify this file, but be careful with dependencies.",
            '"""'
        ]
        return lines
    
    def _generate_imports(self, file_group: FileGroup,
                         all_file_groups: Dict[str, FileGroup]) -> List[str]:
        """Generate import statements for the file"""
        lines = []
        
        # Standard imports
        standard_imports = self._get_standard_imports(file_group)
        if standard_imports:
            lines.extend(standard_imports)
            lines.append("")
        
        # InfraDSL imports
        infradsl_imports = self._get_infradsl_imports(file_group)
        if infradsl_imports:
            lines.extend(infradsl_imports)
            lines.append("")
        
        # Dependency imports
        dependency_imports = self._get_dependency_imports(file_group, all_file_groups)
        if dependency_imports:
            lines.extend(dependency_imports)
        
        return lines
    
    def _get_standard_imports(self, file_group: FileGroup) -> List[str]:
        """Get standard library imports needed"""
        imports = []
        
        # Check if we need any standard library imports
        for resource in file_group.resources:
            # Check if resource uses complex configurations that need json, base64, etc.
            if any(attr in resource.attributes for attr in ["user_data", "policy", "configuration"]):
                if "import json" not in imports:
                    imports.append("import json")
                if "import base64" not in imports:
                    imports.append("import base64")
        
        return imports
    
    def _get_infradsl_imports(self, file_group: FileGroup) -> List[str]:
        """Get InfraDSL imports needed"""
        providers = set()
        specific_imports = set()
        
        for resource in file_group.resources:
            if resource.type.startswith("aws_"):
                providers.add("AWS")
            elif resource.type.startswith("google_"):
                if resource.type == "google_cloud_run_service":
                    specific_imports.add("from infradsl.resources.compute.cloud_run import CloudRun")
                elif resource.type in ["google_compute_network", "google_compute_subnetwork"]:
                    specific_imports.add("from infradsl.resources.network.vpc import VPCNetwork")
                else:
                    providers.add("GCP")
            elif resource.type.startswith("digitalocean_"):
                providers.add("DigitalOcean")
        
        imports = []
        if providers:
            provider_list = ", ".join(sorted(providers))
            imports.append(f"from infradsl import {provider_list}")
        
        imports.extend(sorted(specific_imports))
        return imports
    
    def _get_dependency_imports(self, file_group: FileGroup,
                              all_file_groups: Dict[str, FileGroup]) -> List[str]:
        """Get imports for dependency resources"""
        imports = []
        
        # Build resource-to-file mapping
        resource_to_file = {}
        resource_to_variable = {}
        for path, fg in all_file_groups.items():
            for resource in fg.resources:
                resource_to_file[resource.id] = path
                resource_to_variable[resource.id] = resource.variable_name
        
        # Collect imports needed for each resource in this file
        needed_imports = defaultdict(set)
        
        for resource in file_group.resources:
            # Find resources this one depends on
            for dep_resource_id in self._get_resource_dependencies(resource):
                if dep_resource_id in resource_to_file:
                    dep_file_path = resource_to_file[dep_resource_id]
                    dep_variable = resource_to_variable[dep_resource_id]
                    
                    # Don't import from the same file
                    if dep_file_path != file_group.path:
                        import_path = self._calculate_import_path(file_group.path, dep_file_path)
                        needed_imports[import_path].add(dep_variable)
        
        # Generate import statements
        for import_path, variables in needed_imports.items():
            var_list = ", ".join(sorted(variables))
            imports.append(f"from {import_path} import {var_list}")
        
        return imports
    
    def _generate_resource_code(self, resource: ResourceNode,
                              dependency_graph: DependencyGraph,
                              all_file_groups: Dict[str, FileGroup]) -> List[str]:
        """Generate code for a single resource"""
        lines = []
        
        # Resource comment
        lines.append(f"# {resource.name} ({resource.type})")
        
        # Variable assignment with factory method
        factory_method = self._resource_factories.get(resource.type, "Unknown")
        
        # Generate chainable method calls
        method_calls = self._generate_method_calls(resource, dependency_graph, all_file_groups)
        
        if method_calls:
            # Format with parentheses for multi-line chaining
            lines.append(f'{resource.variable_name} = (')
            lines.append(f'    {factory_method}("{resource.name}")')
            for method_call in method_calls:
                lines.append(f'    {method_call}')
            lines.append(')')
        else:
            # Single line if no method calls
            lines.append(f'{resource.variable_name} = {factory_method}("{resource.name}")')
        
        return lines
    
    def _generate_method_calls(self, resource: ResourceNode,
                             dependency_graph: DependencyGraph,
                             all_file_groups: Dict[str, FileGroup]) -> List[str]:
        """Generate chainable method calls for a resource"""
        calls = []
        attrs = resource.attributes
        
        # Build resource-to-variable mapping for references
        resource_to_variable = {}
        for fg in all_file_groups.values():
            for res in fg.resources:
                resource_to_variable[res.id] = res.variable_name
        
        # Generate calls based on resource type
        if resource.type == "aws_instance":
            calls.extend(self._generate_ec2_method_calls(resource, attrs, resource_to_variable))
        elif resource.type == "aws_vpc":
            calls.extend(self._generate_vpc_method_calls(resource, attrs))
        elif resource.type == "aws_subnet":
            calls.extend(self._generate_subnet_method_calls(resource, attrs, resource_to_variable))
        elif resource.type == "aws_security_group":
            calls.extend(self._generate_security_group_calls(resource, attrs, resource_to_variable))
        elif resource.type == "aws_db_instance":
            calls.extend(self._generate_rds_method_calls(resource, attrs, resource_to_variable))
        elif resource.type.startswith("google_compute_instance"):
            calls.extend(self._generate_gcp_instance_calls(resource, attrs, resource_to_variable))
        elif resource.type == "google_cloud_run_service":
            calls.extend(self._generate_cloudrun_method_calls(resource, attrs, resource_to_variable))
        elif resource.type == "google_compute_network":
            calls.extend(self._generate_gcp_vpc_method_calls(resource, attrs))
        elif resource.type == "google_compute_subnetwork":
            # Skip subnets - they should be added to VPC via .subnet() method
            return []
        else:
            # Generic method calls
            calls.extend(self._generate_generic_method_calls(resource, attrs, resource_to_variable))
        
        # Add common tags/labels
        calls.extend(self._generate_tag_calls(resource))
        
        # Add environment-specific calls
        calls.extend(self._generate_environment_calls(resource))
        
        return calls
    
    def _generate_ec2_method_calls(self, resource: ResourceNode, 
                                 attrs: Dict[str, Any],
                                 resource_map: Dict[str, str]) -> List[str]:
        """Generate method calls for AWS EC2 instances"""
        calls = []
        
        # AMI
        if ami_id := attrs.get("ami"):
            calls.append(f'.ami("{ami_id}")')
        
        # Instance type
        if instance_type := attrs.get("instance_type"):
            calls.append(f'.instance_type("{instance_type}")')
        
        # Key pair
        if key_name := attrs.get("key_name"):
            calls.append(f'.key_pair("{key_name}")')
        
        # Subnet (with reference if available)
        if subnet_id := attrs.get("subnet_id"):
            if subnet_id in resource_map:
                calls.append(f'.subnet({resource_map[subnet_id]})')
            else:
                calls.append(f'.subnet("{subnet_id}")')
        
        # Security groups (with references if available)
        if security_groups := attrs.get("security_group_ids", []):
            for sg_id in security_groups:
                if sg_id in resource_map:
                    calls.append(f'.security_group({resource_map[sg_id]})')
                else:
                    calls.append(f'.security_group("{sg_id}")')
        
        # Public IP
        if attrs.get("associate_public_ip_address"):
            calls.append('.public_ip()')
        
        # Private IP
        if private_ip := attrs.get("private_ip_address"):
            calls.append(f'.private_ip("{private_ip}")')
        
        # Root volume
        if root_device := attrs.get("root_block_device"):
            if isinstance(root_device, list) and root_device:
                root = root_device[0]
                size = root.get("volume_size", 20)
                volume_type = root.get("volume_type", "gp3")
                encrypted = root.get("encrypted", True)
                calls.append(f'.root_volume({size}, "{volume_type}", {encrypted})')
        
        # EBS volumes
        if ebs_devices := attrs.get("ebs_block_device", []):
            for i, ebs in enumerate(ebs_devices):
                device = ebs.get("device_name", f"/dev/sdf{i}")
                size = ebs.get("volume_size", 10)
                volume_type = ebs.get("volume_type", "gp3")
                calls.append(f'.ebs_volume("data_{i}", {size}, "{volume_type}")')
        
        # IAM role
        if iam_profile := attrs.get("iam_instance_profile"):
            if isinstance(iam_profile, dict):
                role_name = iam_profile.get("name", "")
            else:
                role_name = str(iam_profile)
            if role_name:
                calls.append(f'.iam_role("{role_name}")')
        
        # Monitoring
        if attrs.get("monitoring"):
            calls.append('.monitoring()')
        
        # User data
        if user_data := attrs.get("user_data"):
            # If user data is small, include inline; otherwise suggest file
            if len(user_data) < 200:
                clean_data = user_data.replace('\n', '\\n').replace('"', '\\"')
                calls.append(f'.user_data("{clean_data}")')
            else:
                calls.append('.user_data_file("startup.sh")  # TODO: Create startup.sh file')
        
        return calls
    
    def _generate_vpc_method_calls(self, resource: ResourceNode,
                                 attrs: Dict[str, Any]) -> List[str]:
        """Generate method calls for AWS VPC"""
        calls = []
        
        # CIDR block
        if cidr := attrs.get("cidr_block"):
            calls.append(f'.cidr("{cidr}")')
        
        # DNS support
        if attrs.get("enable_dns_support", True):
            calls.append('.enable_dns()')
        
        # DNS hostnames
        if attrs.get("enable_dns_hostnames"):
            calls.append('.enable_dns_hostnames()')
        
        return calls
    
    def _generate_subnet_method_calls(self, resource: ResourceNode,
                                    attrs: Dict[str, Any],
                                    resource_map: Dict[str, str]) -> List[str]:
        """Generate method calls for AWS Subnet"""
        calls = []
        
        # VPC reference
        if vpc_id := attrs.get("vpc_id"):
            if vpc_id in resource_map:
                calls.append(f'.vpc({resource_map[vpc_id]})')
            else:
                calls.append(f'.vpc_id("{vpc_id}")')
        
        # CIDR block
        if cidr := attrs.get("cidr_block"):
            calls.append(f'.cidr("{cidr}")')
        
        # Availability zone
        if az := attrs.get("availability_zone"):
            calls.append(f'.availability_zone("{az}")')
        
        # Public subnet
        if attrs.get("map_public_ip_on_launch"):
            calls.append('.public()')
        else:
            calls.append('.private()')
        
        return calls
    
    def _generate_security_group_calls(self, resource: ResourceNode,
                                     attrs: Dict[str, Any],
                                     resource_map: Dict[str, str]) -> List[str]:
        """Generate method calls for AWS Security Group"""
        calls = []
        
        # VPC reference  
        if vpc_id := attrs.get("vpc_id"):
            if vpc_id in resource_map:
                calls.append(f'.vpc({resource_map[vpc_id]})')
        
        # Description
        if description := attrs.get("description"):
            calls.append(f'.description("{description}")')
        
        # Ingress rules
        if ingress_rules := attrs.get("ingress", []):
            for rule in ingress_rules:
                calls.extend(self._generate_security_rule_calls("ingress", rule, resource_map))
        
        # Egress rules
        if egress_rules := attrs.get("egress", []):
            for rule in egress_rules:
                calls.extend(self._generate_security_rule_calls("egress", rule, resource_map))
        
        return calls
    
    def _generate_security_rule_calls(self, rule_type: str, rule: Dict[str, Any],
                                    resource_map: Dict[str, str]) -> List[str]:
        """Generate security group rule method calls"""
        calls = []
        
        protocol = rule.get("protocol", "tcp")
        from_port = rule.get("from_port", 0)
        to_port = rule.get("to_port", 0)
        
        # CIDR blocks
        if cidr_blocks := rule.get("cidr_blocks", []):
            for cidr in cidr_blocks:
                if from_port == to_port:
                    calls.append(f'.{rule_type}_rule("{protocol}", {from_port}, "{cidr}")')
                else:
                    calls.append(f'.{rule_type}_rule("{protocol}", {from_port}, {to_port}, "{cidr}")')
        
        # Security group references
        if sg_refs := rule.get("security_groups", []):
            for sg_ref in sg_refs:
                sg_var = resource_map.get(sg_ref, f'"{sg_ref}"')
                calls.append(f'.{rule_type}_rule("{protocol}", {from_port}, {to_port}, {sg_var})')
        
        return calls
    
    def _generate_rds_method_calls(self, resource: ResourceNode,
                                 attrs: Dict[str, Any],
                                 resource_map: Dict[str, str]) -> List[str]:
        """Generate method calls for AWS RDS instances"""
        calls = []
        
        # Engine
        if engine := attrs.get("engine"):
            calls.append(f'.engine("{engine}")')
        
        # Engine version
        if version := attrs.get("engine_version"):
            calls.append(f'.engine_version("{version}")')
        
        # Instance class
        if instance_class := attrs.get("instance_class"):
            calls.append(f'.instance_class("{instance_class}")')
        
        # Storage
        if storage := attrs.get("allocated_storage"):
            calls.append(f'.storage({storage})')
        
        # Storage encrypted
        if attrs.get("storage_encrypted"):
            calls.append('.encrypted()')
        
        # Multi-AZ
        if attrs.get("multi_az"):
            calls.append('.multi_az()')
        
        # Database name
        if db_name := attrs.get("db_name"):
            calls.append(f'.database_name("{db_name}")')
        
        # Master username
        if username := attrs.get("username"):
            calls.append(f'.master_username("{username}")')
        
        # Subnet group
        if subnet_group := attrs.get("db_subnet_group_name"):
            if subnet_group in resource_map:
                calls.append(f'.subnet_group({resource_map[subnet_group]})')
            else:
                calls.append(f'.subnet_group("{subnet_group}")')
        
        # Security groups
        if security_groups := attrs.get("vpc_security_group_ids", []):
            for sg_id in security_groups:
                if sg_id in resource_map:
                    calls.append(f'.security_group({resource_map[sg_id]})')
                else:
                    calls.append(f'.security_group("{sg_id}")')
        
        return calls
    
    def _generate_gcp_instance_calls(self, resource: ResourceNode,
                                   attrs: Dict[str, Any],
                                   resource_map: Dict[str, str]) -> List[str]:
        """Generate method calls for GCP Compute instances"""
        calls = []
        
        # Machine type
        if machine_type := attrs.get("machine_type"):
            # Extract just the machine type from full URL
            if "/" in machine_type:
                machine_type = machine_type.split("/")[-1]
            calls.append(f'.machine_type("{machine_type}")')
        
        # Zone
        if zone := attrs.get("zone"):
            if "/" in zone:
                zone = zone.split("/")[-1]
            calls.append(f'.zone("{zone}")')
        
        # Boot disk
        if boot_disk := attrs.get("boot_disk"):
            if isinstance(boot_disk, list) and boot_disk:
                disk = boot_disk[0]
                if initialize_params := disk.get("initialize_params"):
                    if isinstance(initialize_params, list) and initialize_params:
                        params = initialize_params[0]
                        if image := params.get("image"):
                            calls.append(f'.image("{image}")')
                        if size := params.get("size"):
                            calls.append(f'.boot_disk_size({size})')
        
        # Network interfaces
        if network_interfaces := attrs.get("network_interface"):
            for interface in network_interfaces:
                if subnetwork := interface.get("subnetwork"):
                    if subnetwork in resource_map:
                        calls.append(f'.subnet({resource_map[subnetwork]})')
                    else:
                        calls.append(f'.subnetwork("{subnetwork}")')
                
                # External IP
                if access_configs := interface.get("access_config"):
                    if access_configs:  # Has external IP
                        calls.append('.external_ip()')
        
        return calls
    
    def _generate_cloudrun_method_calls(self, resource: ResourceNode,
                                      attrs: Dict[str, Any],
                                      resource_map: Dict[str, str]) -> List[str]:
        """Generate method calls for GCP Cloud Run services"""
        calls = []
        
        # Location/region
        if location := attrs.get("location"):
            calls.append(f'.region("{location}")')
        
        # Mark as imported resource with cloud_id
        if resource.id:
            calls.append(f'.imported("{resource.id}")')
        
        # Container configuration
        if container := attrs.get("container"):
            if image := container.get("image"):
                calls.append(f'.image("{image}")')
            
            if ports := container.get("ports"):
                if ports and len(ports) > 0:
                    port = ports[0]
                    if port != 8080:  # Only specify if not default
                        calls.append(f'.port({port})')
            
            if cpu := container.get("cpu"):
                # CPU value might be a string like "1000m" or integer
                if isinstance(cpu, str):
                    calls.append(f'.cpu("{cpu}")')
                else:
                    calls.append(f'.cpu({cpu})')
            
            if memory := container.get("memory"):
                calls.append(f'.memory("{memory}")')
        
        # Ingress settings
        if ingress := attrs.get("ingress"):
            if ingress == "INGRESS_TRAFFIC_INTERNAL_ONLY":
                calls.append('.internal_only()')
            elif ingress == "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER":
                calls.append('.internal_load_balancer()')
        
        # Service account
        if service_account := attrs.get("service_account_email"):
            if service_account:
                calls.append(f'.service_account("{service_account}")')
        
        # Traffic allocation (if not 100% to latest)
        if traffic := attrs.get("traffic"):
            if traffic and len(traffic) > 1:  # Multiple traffic splits
                for t in traffic:
                    if revision := t.get("revision"):
                        percent = t.get("percent", 0)
                        calls.append(f'.traffic("{revision}", {percent})')
        
        # Allow unauthenticated (if specified)
        if "allow_unauthenticated" in attrs:
            if attrs["allow_unauthenticated"]:
                calls.append('.public()')
            else:
                calls.append('.authenticated()')
        
        # Min/max instances
        if min_instances := attrs.get("min_instances"):
            if min_instances != 0:
                calls.append(f'.min_instances({min_instances})')
        
        if max_instances := attrs.get("max_instances"):
            if max_instances != 100:  # Only add if not default
                calls.append(f'.max_instances({max_instances})')
        
        return calls
    
    def _generate_gcp_vpc_method_calls(self, resource: ResourceNode,
                                      attrs: Dict[str, Any]) -> List[str]:
        """Generate method calls for GCP VPC networks"""
        calls = []
        
        # Routing mode
        if routing_mode := attrs.get("routing_mode"):
            if routing_mode == "GLOBAL":
                calls.append('.global_routing()')
            elif routing_mode == "REGIONAL":
                calls.append('.regional_routing()')
        
        # Auto create subnets
        if auto_create := attrs.get("auto_create_subnetworks"):
            if not auto_create:
                calls.append('.custom_subnets()')
        
        # MTU
        if mtu := attrs.get("mtu"):
            if mtu != 1460:  # Only add if not default
                calls.append(f'.mtu({mtu})')
        
        return calls
    
    def _generate_generic_method_calls(self, resource: ResourceNode,
                                     attrs: Dict[str, Any],
                                     resource_map: Dict[str, str]) -> List[str]:
        """Generate generic method calls for unknown resource types"""
        calls = []
        
        # Common attributes that translate to method calls
        attr_mappings = {
            "name": lambda v: f'.name("{v}")',
            "description": lambda v: f'.description("{v}")',
            "region": lambda v: f'.region("{v}")',
            "zone": lambda v: f'.zone("{v}")',
            "size": lambda v: f'.size("{v}")',
            "type": lambda v: f'.type("{v}")',
        }
        
        for attr, value in attrs.items():
            if attr in attr_mappings and value:
                calls.append(attr_mappings[attr](value))
        
        return calls
    
    def _generate_tag_calls(self, resource: ResourceNode) -> List[str]:
        """Generate tag/label method calls"""
        calls = []
        
        if resource.tags:
            # Use .label() for GCP resources, .tag() for others
            tag_method = "label" if resource.type.startswith("google_") else "tag"
            
            # Group common tags
            common_tags = ["Name", "Environment", "Project", "Team", "Owner"]
            
            for tag_key, tag_value in resource.tags.items():
                if tag_key in common_tags:
                    method_name = tag_key.lower()
                    if method_name == "name":
                        continue  # Skip Name tag as it's usually the resource name
                    calls.append(f'.{method_name}("{tag_value}")')
                else:
                    calls.append(f'.{tag_method}("{tag_key}", "{tag_value}")')
        
        return calls
    
    def _generate_environment_calls(self, resource: ResourceNode) -> List[str]:
        """Generate environment-specific method calls"""
        calls = []
        
        # Determine environment
        env = "unknown"
        if env_tag := resource.tags.get("Environment"):
            env = env_tag.lower()
        elif "prod" in resource.name.lower():
            env = "production"
        elif "stag" in resource.name.lower():
            env = "staging"
        elif "dev" in resource.name.lower():
            env = "development"
        
        # Add environment-specific calls
        if env == "production":
            calls.append('.production()')
        elif env == "staging":
            calls.append('.staging()')
        elif env == "development":
            calls.append('.development()')
        
        return calls
    
    def _generate_exports(self, resources: List[ResourceNode]) -> List[str]:
        """Generate __all__ export list"""
        lines = []
        
        # Filter out subnets for GCP
        variable_names = [
            resource.variable_name 
            for resource in resources 
            if resource.type != "google_compute_subnetwork"
        ]
        
        if variable_names:
            lines.append("# Export all resources")
            lines.append("__all__ = [")
            
            for name in sorted(variable_names):
                lines.append(f'    "{name}",')
            
            lines.append("]")
        
        return lines
    
    def _get_resource_dependencies(self, resource: ResourceNode) -> List[str]:
        """Get list of resource IDs that this resource depends on"""
        dependencies = []
        attrs = resource.attributes
        
        # Common dependency patterns
        if subnet_id := attrs.get("subnet_id"):
            dependencies.append(subnet_id)
        
        if vpc_id := attrs.get("vpc_id"):
            dependencies.append(vpc_id)
        
        if security_groups := attrs.get("security_group_ids", []):
            dependencies.extend(security_groups)
        
        if vpc_security_groups := attrs.get("vpc_security_group_ids", []):
            dependencies.extend(vpc_security_groups)
        
        # Add more dependency patterns as needed
        
        return dependencies
    
    def _calculate_import_path(self, from_path: str, to_path: str) -> str:
        """Calculate relative import path between files"""
        from_parts = Path(from_path).parent.parts
        to_parts = Path(to_path).with_suffix("").parts
        
        # Find common path
        common_length = 0
        for i, (from_part, to_part) in enumerate(zip(from_parts, to_parts)):
            if from_part == to_part:
                common_length = i + 1
            else:
                break
        
        # Calculate relative path
        up_levels = len(from_parts) - common_length
        remaining_path = to_parts[common_length:]
        
        if up_levels == 0:
            # Same directory
            return f".{remaining_path[-1]}"
        else:
            # Go up and then down
            dots = "." * (up_levels + 1)  
            if remaining_path:
                return f"{dots}{'.'.join(remaining_path)}"
            else:
                return dots[:-1]  # Remove one dot
    
    def format_code(self, code: str) -> str:
        """Format generated code for better readability"""
        lines = code.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Remove trailing whitespace
            line = line.rstrip()
            
            # Format long method chains
            if len(line) > self.max_line_length and '.' in line and '(' in line:
                # Split long method chains
                formatted_lines.extend(self._split_long_line(line))
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _split_long_line(self, line: str) -> List[str]:
        """Split a long line into multiple lines"""
        # This is a simplified implementation
        # In a real scenario, you'd want more sophisticated formatting
        if '\\' in line:
            return [line]  # Already split
        
        # Find a good place to split (before a method call)
        parts = line.split('.')
        if len(parts) <= 2:
            return [line]
        
        # Reconstruct with line breaks
        result = []
        current_line = parts[0]
        
        for part in parts[1:]:
            potential_line = f"{current_line}.{part}"
            if len(potential_line) > self.max_line_length:
                result.append(f"{current_line} \\")
                current_line = f"    .{part}"
            else:
                current_line = potential_line
        
        result.append(current_line)
        return result