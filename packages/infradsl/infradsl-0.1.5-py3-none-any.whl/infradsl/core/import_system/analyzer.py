"""
Resource Analysis Engine for Import System

This module analyzes cloud resources to understand their configurations,
detect patterns, and build dependency relationships.
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple
import re
from datetime import datetime

from .models import (
    CloudResource, 
    DependencyGraph, 
    ImportConfig, 
    ResourceType
)

logger = logging.getLogger(__name__)


class ResourceAnalyzer:
    """
    Analyzes cloud resources for import operations.
    
    This analyzer:
    1. Builds dependency graphs between resources
    2. Detects common infrastructure patterns
    3. Optimizes resource configurations for code generation
    """
    
    def __init__(self):
        """Initialize the resource analyzer"""
        self.dependency_rules = self._initialize_dependency_rules()
        self.pattern_detectors = self._initialize_pattern_detectors()
    
    async def build_dependency_graph(
        self, 
        resources: List[CloudResource], 
        config: ImportConfig
    ) -> DependencyGraph:
        """
        Build a dependency graph from discovered resources.
        
        Args:
            resources: List of cloud resources
            config: Import configuration
            
        Returns:
            DependencyGraph with resources and dependencies
        """
        logger.info(f"Building dependency graph for {len(resources)} resources")
        
        graph = DependencyGraph()
        
        # Add all resources to the graph
        for resource in resources:
            graph.add_resource(resource)
        
        # Analyze dependencies between resources
        await self._analyze_resource_dependencies(graph, config)
        
        # Set import priorities based on dependencies
        self._set_import_priorities(graph)
        
        logger.info(f"Built dependency graph with {len(graph.edges)} dependencies")
        return graph
    
    async def _analyze_resource_dependencies(
        self, 
        graph: DependencyGraph, 
        config: ImportConfig
    ) -> None:
        """Analyze and add dependencies between resources"""
        resources = list(graph.resources.values())
        
        for i, resource_a in enumerate(resources):
            for j, resource_b in enumerate(resources):
                if i != j:  # Don't compare resource with itself
                    dependency = await self._check_dependency(resource_a, resource_b, config)
                    if dependency:
                        graph.add_dependency(resource_a.id, resource_b.id)
                        logger.debug(f"Found dependency: {resource_a.name} -> {resource_b.name}")
    
    async def _check_dependency(
        self, 
        resource_a: CloudResource, 
        resource_b: CloudResource, 
        config: ImportConfig
    ) -> bool:
        """
        Check if resource_a depends on resource_b.
        
        Args:
            resource_a: Potential dependent resource
            resource_b: Potential dependency resource
            config: Import configuration
            
        Returns:
            True if resource_a depends on resource_b
        """
        # Apply dependency rules
        for rule in self.dependency_rules:
            if await rule(resource_a, resource_b, config):
                return True
        
        return False
    
    def _initialize_dependency_rules(self) -> List[Any]:
        """Initialize dependency detection rules"""
        return [
            self._check_network_dependency,
            self._check_storage_dependency,
            self._check_security_dependency,
            self._check_reference_dependency,
            self._check_naming_dependency,
        ]
    
    async def _check_network_dependency(
        self, 
        resource_a: CloudResource, 
        resource_b: CloudResource, 
        config: ImportConfig
    ) -> bool:
        """Check for network-based dependencies"""
        # VMs depend on networks/subnets
        if (resource_a.type == ResourceType.VIRTUAL_MACHINE and 
            resource_b.type == ResourceType.NETWORK):
            
            # Check if VM references the network
            vm_config = resource_a.configuration
            network_id = resource_b.id
            network_name = resource_b.name
            
            # Check various network reference patterns
            network_refs = [
                vm_config.get("network"),
                vm_config.get("subnet"),
                vm_config.get("vpc_id"),
                vm_config.get("network_id"),
            ]
            
            for ref in network_refs:
                if ref and (str(ref) == network_id or str(ref) == network_name):
                    return True
        
        return False
    
    async def _check_storage_dependency(
        self, 
        resource_a: CloudResource, 
        resource_b: CloudResource, 
        config: ImportConfig
    ) -> bool:
        """Check for storage-based dependencies"""
        # VMs depend on storage volumes
        if (resource_a.type == ResourceType.VIRTUAL_MACHINE and 
            resource_b.type == ResourceType.STORAGE):
            
            vm_config = resource_a.configuration
            storage_id = resource_b.id
            storage_name = resource_b.name
            
            # Check for volume attachments
            volumes = vm_config.get("volumes", [])
            if isinstance(volumes, list):
                for volume in volumes:
                    if isinstance(volume, dict):
                        vol_id = volume.get("id") or volume.get("volume_id")
                        if vol_id and (str(vol_id) == storage_id or str(vol_id) == storage_name):
                            return True
            
            # Check for disk references
            disks = vm_config.get("disks", [])
            if isinstance(disks, list):
                for disk in disks:
                    if isinstance(disk, dict):
                        disk_id = disk.get("source") or disk.get("disk_id")
                        if disk_id and (str(disk_id) == storage_id or str(disk_id) == storage_name):
                            return True
        
        return False
    
    async def _check_security_dependency(
        self, 
        resource_a: CloudResource, 
        resource_b: CloudResource, 
        config: ImportConfig
    ) -> bool:
        """Check for security-based dependencies"""
        # VMs depend on security groups
        if (resource_a.type == ResourceType.VIRTUAL_MACHINE and 
            resource_b.type == ResourceType.SECURITY_GROUP):
            
            vm_config = resource_a.configuration
            sg_id = resource_b.id
            sg_name = resource_b.name
            
            # Check security group references
            security_groups = vm_config.get("security_groups", [])
            if isinstance(security_groups, list):
                for sg in security_groups:
                    if str(sg) == sg_id or str(sg) == sg_name:
                        return True
        
        return False
    
    async def _check_reference_dependency(
        self, 
        resource_a: CloudResource, 
        resource_b: CloudResource, 
        config: ImportConfig
    ) -> bool:
        """Check for explicit ID/ARN references"""
        # Look for explicit references in configuration
        config_str = str(resource_a.configuration)
        
        # Check for resource B's ID in resource A's configuration
        if resource_b.id in config_str:
            return True
        
        # Check for ARN-style references (AWS)
        if config.provider == "aws":
            # Look for ARN patterns
            arn_pattern = f"arn:aws:[^:]+:[^:]*:[^:]*:{resource_b.id}"
            if re.search(arn_pattern, config_str):
                return True
        
        return False
    
    async def _check_naming_dependency(
        self, 
        resource_a: CloudResource, 
        resource_b: CloudResource, 
        config: ImportConfig
    ) -> bool:
        """Check for naming-based dependencies"""
        # Look for resource B's name in resource A's configuration
        config_str = str(resource_a.configuration).lower()
        resource_b_name = resource_b.name.lower()
        
        # Skip very short names to avoid false positives
        if len(resource_b_name) < 4:
            return False
        
        # Check if resource B's name appears in resource A's config
        if resource_b_name in config_str:
            # Additional validation to reduce false positives
            # Check if it's a meaningful reference (not just substring)
            words = re.findall(r'\b' + re.escape(resource_b_name) + r'\b', config_str)
            return len(words) > 0
        
        return False
    
    def _set_import_priorities(self, graph: DependencyGraph) -> None:
        """Set import priorities based on dependency depth"""
        # Calculate dependency depth for each resource
        depths = {}
        
        def calculate_depth(resource_id: str, visited: Set[str]) -> int:
            if resource_id in visited:
                return 0  # Circular dependency, break the cycle
            
            if resource_id in depths:
                return depths[resource_id]
            
            visited.add(resource_id)
            max_depth = 0
            
            # Find all resources this one depends on
            for from_id, to_id in graph.edges:
                if from_id == resource_id:
                    dep_depth = calculate_depth(to_id, visited.copy())
                    max_depth = max(max_depth, dep_depth + 1)
            
            depths[resource_id] = max_depth
            return max_depth
        
        # Calculate depths for all resources
        for resource_id in graph.resources:
            calculate_depth(resource_id, set())
        
        # Set priorities (higher depth = higher priority = created first)
        for resource_id, depth in depths.items():
            graph.resources[resource_id].import_priority = depth
    
    def _initialize_pattern_detectors(self) -> List[Any]:
        """Initialize infrastructure pattern detectors"""
        return [
            self._detect_web_tier_pattern,
            self._detect_database_tier_pattern,
            self._detect_load_balancer_pattern,
            self._detect_auto_scaling_pattern,
        ]
    
    async def detect_patterns(
        self, 
        resources: List[CloudResource]
    ) -> List[Dict[str, Any]]:
        """
        Detect common infrastructure patterns.
        
        Args:
            resources: List of cloud resources
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        for detector in self.pattern_detectors:
            detected = await detector(resources)
            if detected:
                patterns.extend(detected)
        
        return patterns
    
    async def _detect_web_tier_pattern(
        self, 
        resources: List[CloudResource]
    ) -> List[Dict[str, Any]]:
        """Detect web tier patterns (web servers, app servers)"""
        patterns = []
        
        web_servers = [
            r for r in resources 
            if r.type == ResourceType.VIRTUAL_MACHINE and
            any(keyword in r.name.lower() for keyword in ['web', 'app', 'frontend', 'nginx', 'apache'])
        ]
        
        if len(web_servers) >= 2:
            patterns.append({
                "type": "web_tier",
                "description": f"Web tier with {len(web_servers)} servers",
                "resources": [ws.id for ws in web_servers],
                "confidence": 0.8
            })
        
        return patterns
    
    async def _detect_database_tier_pattern(
        self, 
        resources: List[CloudResource]
    ) -> List[Dict[str, Any]]:
        """Detect database tier patterns"""
        patterns = []
        
        databases = [r for r in resources if r.type == ResourceType.DATABASE]
        
        if databases:
            patterns.append({
                "type": "database_tier",
                "description": f"Database tier with {len(databases)} databases",
                "resources": [db.id for db in databases],
                "confidence": 0.9
            })
        
        return patterns
    
    async def _detect_load_balancer_pattern(
        self, 
        resources: List[CloudResource]
    ) -> List[Dict[str, Any]]:
        """Detect load balancer patterns"""
        patterns = []
        
        load_balancers = [r for r in resources if r.type == ResourceType.LOAD_BALANCER]
        
        if load_balancers:
            patterns.append({
                "type": "load_balancer",
                "description": f"Load balancing with {len(load_balancers)} load balancers",
                "resources": [lb.id for lb in load_balancers],
                "confidence": 0.9
            })
        
        return patterns
    
    async def _detect_auto_scaling_pattern(
        self, 
        resources: List[CloudResource]
    ) -> List[Dict[str, Any]]:
        """Detect auto-scaling patterns"""
        patterns = []
        
        # Look for multiple similar VMs (potential auto-scaling group)
        vm_groups = {}
        for resource in resources:
            if resource.type == ResourceType.VIRTUAL_MACHINE:
                # Group by similar names (remove numbers/suffixes)
                base_name = re.sub(r'[-_]\d+$', '', resource.name)
                if base_name not in vm_groups:
                    vm_groups[base_name] = []
                vm_groups[base_name].append(resource)
        
        for base_name, vms in vm_groups.items():
            if len(vms) >= 3:  # 3 or more similar VMs
                patterns.append({
                    "type": "auto_scaling_group",
                    "description": f"Auto-scaling group '{base_name}' with {len(vms)} instances",
                    "resources": [vm.id for vm in vms],
                    "confidence": 0.7
                })
        
        return patterns
    
    def optimize_resource_configuration(
        self, 
        resource: CloudResource
    ) -> CloudResource:
        """
        Optimize resource configuration for code generation.
        
        Args:
            resource: Cloud resource to optimize
            
        Returns:
            Optimized cloud resource
        """
        # Create a copy to avoid modifying the original
        optimized = CloudResource(
            id=resource.id,
            name=resource.name,
            type=resource.type,
            provider=resource.provider,
            region=resource.region,
            zone=resource.zone,
            project=resource.project,
            configuration=resource.configuration.copy(),
            metadata=resource.metadata.copy(),
            tags=resource.tags.copy(),
            dependencies=resource.dependencies.copy(),
            dependents=resource.dependents.copy(),
            discovered_at=resource.discovered_at,
            import_priority=resource.import_priority
        )
        
        # Remove provider-specific internal fields
        internal_fields = [
            'id', 'self_link', 'creation_timestamp', 'fingerprint',
            'kind', 'status', 'zone_url', 'region_url', 'project_id'
        ]
        
        for field in internal_fields:
            optimized.configuration.pop(field, None)
        
        # Normalize common field names
        field_mappings = {
            'machine_type': 'size',
            'instance_type': 'size',
            'disk_size_gb': 'disk_size',
            'boot_disk_size_gb': 'disk_size',
        }
        
        for old_field, new_field in field_mappings.items():
            if old_field in optimized.configuration:
                optimized.configuration[new_field] = optimized.configuration.pop(old_field)
        
        # Clean up empty or null values
        optimized.configuration = {
            k: v for k, v in optimized.configuration.items() 
            if v is not None and v != '' and v != []
        }
        
        return optimized