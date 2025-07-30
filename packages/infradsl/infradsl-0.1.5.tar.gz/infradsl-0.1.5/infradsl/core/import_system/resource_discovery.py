"""
Parallel Resource Discovery and Tagging System

This module provides high-performance parallel resource discovery across
multiple cloud providers with automatic tagging and cache population.
"""

import asyncio
import logging
from typing import Dict, List, Set, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from pathlib import Path
import os
import json

from .dependency_graph import ResourceNode, DependencyGraph
# For now, we'll create a simplified discovery system
# TODO: Integrate with proper state discovery interfaces later

logger = logging.getLogger(__name__)


@dataclass
class DiscoveryProgress:
    """Progress tracking for resource discovery operations"""
    total_providers: int = 0
    providers_completed: int = 0
    total_resources: int = 0
    resources_discovered: int = 0
    resources_tagged: int = 0
    resources_cached: int = 0
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    current_provider: str = ""
    errors: List[str] = field(default_factory=list)
    
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        return (datetime.now(timezone.utc) - self.start_time).total_seconds()
    
    @property
    def resources_per_second(self) -> float:
        """Calculate discovery rate"""
        elapsed = self.elapsed_time
        return self.resources_discovered / elapsed if elapsed > 0 else 0.0


@dataclass
class ProviderDiscoveryResult:
    """Result from discovering resources in a single provider"""
    provider: str
    region: str
    resources: List[ResourceNode]
    errors: List[str] = field(default_factory=list)
    discovery_time: float = 0.0
    tagged_count: int = 0
    cached_count: int = 0


class ResourceDiscoveryEngine:
    """
    High-performance parallel resource discovery engine.
    
    Discovers resources across multiple cloud providers, tags them
    for InfraDSL management, and populates the cache for instant recognition.
    """
    
    def __init__(self, max_workers: int = 10, batch_size: int = 50):
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.progress = DiscoveryProgress()
        self._discovery_interfaces = self._build_discovery_interfaces()
        self._management_tags = {
            "infradsl.managed": "true",
            "infradsl.import.version": "1.0",
            "infradsl.import.engine": "parallel-discovery"
        }
    
    def _build_discovery_interfaces(self) -> Dict[str, Any]:
        """Build provider discovery interfaces"""
        # For now, return empty dict - we'll implement discovery logic directly
        # TODO: Integrate with actual provider discovery implementations
        return {}
    
    async def discover_all_resources(self, 
                                   providers: List[str],
                                   regions: Optional[Dict[str, List[str]]] = None,
                                   filters: Optional[Dict[str, Any]] = None,
                                   auto_tag: bool = True) -> DependencyGraph:
        """
        Discover all resources across specified providers and regions.
        
        Args:
            providers: List of provider names (aws, gcp, digitalocean)
            regions: Provider-specific regions {provider: [regions]}
            filters: Resource filters (tags, types, etc.)
            auto_tag: Whether to automatically tag resources as managed
        
        Returns:
            DependencyGraph with all discovered resources
        """
        logger.info(f"Starting parallel resource discovery across {len(providers)} providers")
        
        # Initialize progress tracking
        self.progress = DiscoveryProgress()
        self.progress.total_providers = len(providers)
        
        # Set default regions if not provided
        if regions is None:
            regions = self._get_default_regions(providers)
        
        # Create dependency graph
        dependency_graph = DependencyGraph()
        
        # Discover resources in parallel
        discovery_tasks = []
        for provider in providers:
            provider_regions = regions.get(provider, ["default"])
            for region in provider_regions:
                task = self._discover_provider_resources(
                    provider, region, filters, auto_tag
                )
                discovery_tasks.append(task)
        
        # Wait for all discovery tasks to complete
        results = await asyncio.gather(*discovery_tasks, return_exceptions=True)
        
        # Process results and build dependency graph
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Provider discovery failed: {result}")
                self.progress.errors.append(str(result))
                continue
            
            if isinstance(result, ProviderDiscoveryResult):
                # Add resources to dependency graph
                for resource in result.resources:
                    dependency_graph.add_resource(
                        resource_id=resource.id,
                        name=resource.name,
                        resource_type=resource.type,
                        provider=resource.provider,
                        region=resource.region,
                        attributes=resource.attributes,
                        metadata=resource.metadata,
                        tags=resource.tags
                    )
                
                self.progress.resources_discovered += len(result.resources)
                self.progress.resources_tagged += result.tagged_count
                self.progress.resources_cached += result.cached_count
                
        self.progress.providers_completed = len(providers)
        
        # Analyze dependencies
        dependency_graph.analyze_dependencies()
        
        logger.info(
            f"Discovery complete: {self.progress.resources_discovered} resources "
            f"in {self.progress.elapsed_time:.2f}s "
            f"({self.progress.resources_per_second:.1f} resources/sec)"
        )
        
        return dependency_graph
    
    async def _discover_provider_resources(self, 
                                         provider: str,
                                         region: str,
                                         filters: Optional[Dict[str, Any]],
                                         auto_tag: bool) -> ProviderDiscoveryResult:
        """Discover resources for a single provider/region"""
        start_time = time.time()
        self.progress.current_provider = f"{provider}/{region}"
        
        logger.debug(f"Discovering resources in {provider}/{region}")
        
        result = ProviderDiscoveryResult(
            provider=provider,
            region=region,
            resources=[]
        )
        
        try:
            # For demo purposes, use mock discovery directly
            # TODO: Get actual discovery interface
            discovery = None  # We're not using it in mock mode
            
            # Discover resources (using mock data for now)
            resources = await self._discover_resources_async(
                discovery, region, filters, provider
            )
            
            # Convert to ResourceNode objects
            resource_nodes = []
            for resource_data in resources:
                node = self._create_resource_node(resource_data, provider, region)
                resource_nodes.append(node)
            
            result.resources = resource_nodes
            
            # Tag resources if requested
            if auto_tag and resource_nodes:
                tagged_count = await self._tag_resources_batch(resource_nodes)
                result.tagged_count = tagged_count
            
            # Cache resources
            if resource_nodes:
                cached_count = await self._cache_resources_batch(resource_nodes)
                result.cached_count = cached_count
            
        except Exception as e:
            logger.error(f"Error discovering {provider}/{region}: {e}")
            result.errors.append(str(e))
        
        result.discovery_time = time.time() - start_time
        return result
    
    async def _discover_resources_async(self,
                                      discovery: Any,
                                      region: str,
                                      filters: Optional[Dict[str, Any]],
                                      provider: str = "aws") -> List[Dict[str, Any]]:
        """Discover resources using async operations"""
        # GCP uses real API discovery, others use mock data for demo
        # TODO: Implement actual provider discovery for AWS and DigitalOcean
        await asyncio.sleep(0.1)  # Small delay for non-GCP providers
        
        if provider == "aws":
            return self._generate_aws_mock_resources(region)
        elif provider == "gcp":
            # Run GCP discovery in thread pool since it's synchronous
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._discover_real_gcp_resources, region)
        elif provider == "digitalocean":
            return self._generate_digitalocean_mock_resources(region)
        else:
            return []
    
    def _generate_aws_mock_resources(self, region: str) -> List[Dict[str, Any]]:
        """Generate mock AWS resources"""
        return [
            {
                "id": f"i-{region.replace('-', '')}001",
                "name": f"web-server-{region}",
                "type": "aws_instance",
                "attributes": {
                    "instance_type": "t3.medium",
                    "ami": "ami-12345678",
                    "subnet_id": f"subnet-{region.replace('-', '')}001"
                },
                "tags": {"Environment": "production", "Tier": "web"},
                "metadata": {"region": region, "availability_zone": f"{region}a"}
            },
            {
                "id": f"subnet-{region.replace('-', '')}001", 
                "name": f"public-subnet-{region}",
                "type": "aws_subnet",
                "attributes": {
                    "cidr_block": "10.0.1.0/24",
                    "vpc_id": f"vpc-{region.replace('-', '')}001"
                },
                "tags": {"Environment": "production", "Type": "public"},
                "metadata": {"region": region}
            },
            {
                "id": f"vpc-{region.replace('-', '')}001",
                "name": f"main-vpc-{region}",
                "type": "aws_vpc", 
                "attributes": {
                    "cidr_block": "10.0.0.0/16"
                },
                "tags": {"Environment": "production"},
                "metadata": {"region": region}
            }
        ]
    
    def _discover_real_gcp_resources(self, region: str) -> List[Dict[str, Any]]:
        """Discover real GCP resources using Google Cloud APIs"""
        try:
            from google.cloud import compute_v1
            import os
            import json
            
            # Get project ID from environment or service account
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
            
            if not project_id:
                # Try to get from service account file
                service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                if service_account_path and os.path.exists(service_account_path):
                    with open(service_account_path) as f:
                        creds = json.load(f)
                    project_id = creds.get("project_id")
            
            if not project_id:
                logger.warning("No GCP project ID found. Set GOOGLE_CLOUD_PROJECT or GOOGLE_APPLICATION_CREDENTIALS")
                return []
            
            logger.info(f"Discovering GCP resources in project {project_id}, region {region}")
            resources = []
            
            # Initialize clients
            instances_client = compute_v1.InstancesClient()
            networks_client = compute_v1.NetworksClient()
            subnetworks_client = compute_v1.SubnetworksClient()
            
            # Try to initialize Cloud Run client
            try:
                from google.cloud import run_v2
                cloudrun_client = run_v2.ServicesClient()
                logger.debug("Cloud Run client initialized successfully")
            except ImportError:
                logger.warning("google-cloud-run not installed. Cloud Run services will not be discovered. Install with: pip install google-cloud-run")
                cloudrun_client = None
            except Exception as e:
                logger.warning(f"Failed to initialize Cloud Run client: {e}")
                cloudrun_client = None
            
            # Get zones for the region
            zones_client = compute_v1.ZonesClient()
            zones_list = zones_client.list(project=project_id)
            region_zones = [zone.name for zone in zones_list if zone.name.startswith(f"{region}-")]
            
            logger.debug(f"Found zones for region {region}: {region_zones}")
            
            # Discover Compute Engine instances
            for zone in region_zones:
                try:
                    instances = instances_client.list(project=project_id, zone=zone)
                    for instance in instances:
                        # Convert GCP instance to our resource format
                        instance_resource = self._convert_gcp_instance(instance, project_id, zone, region)
                        resources.append(instance_resource)
                        logger.debug(f"Found instance: {instance.name} in {zone}")
                except Exception as e:
                    logger.warning(f"Failed to list instances in zone {zone}: {e}")
            
            # Discover VPC networks
            try:
                networks = networks_client.list(project=project_id)
                for network in networks:
                    network_resource = self._convert_gcp_network(network, project_id, region)
                    resources.append(network_resource)
                    logger.debug(f"Found network: {network.name}")
            except Exception as e:
                logger.warning(f"Failed to list networks: {e}")
            
            # Discover subnets
            try:
                subnets = subnetworks_client.list(project=project_id, region=region)
                for subnet in subnets:
                    subnet_resource = self._convert_gcp_subnet(subnet, project_id, region)
                    resources.append(subnet_resource)
                    logger.debug(f"Found subnet: {subnet.name} in {region}")
            except Exception as e:
                logger.warning(f"Failed to list subnets in region {region}: {e}")
            
            # Discover Cloud Run services
            if cloudrun_client:
                try:
                    # Cloud Run uses parent format: projects/{project}/locations/{location}
                    parent = f"projects/{project_id}/locations/{region}"
                    cloudrun_services = cloudrun_client.list_services(parent=parent)
                    for service in cloudrun_services:
                        service_resource = self._convert_gcp_cloudrun_service(service, project_id, region)
                        resources.append(service_resource)
                        logger.debug(f"Found Cloud Run service: {service.name.split('/')[-1]} in {region}")
                except Exception as e:
                    logger.warning(f"Failed to list Cloud Run services in region {region}: {e}")
            
            logger.info(f"Discovered {len(resources)} GCP resources in {region}")
            return resources
            
        except ImportError:
            logger.error("google-cloud-compute not installed. Install with: pip install google-cloud-compute")
            return []
        except Exception as e:
            logger.error(f"Failed to discover GCP resources: {e}")
            return []
    
    def _convert_gcp_instance(self, instance, project_id: str, zone: str, region: str) -> Dict[str, Any]:
        """Convert GCP instance to our resource format"""
        # Extract machine type (get just the type name, not full URL)
        machine_type = instance.machine_type.split('/')[-1] if instance.machine_type else "unknown"
        
        # Extract boot disk info
        boot_disk_info = {}
        if instance.disks:
            for disk in instance.disks:
                if disk.boot:
                    boot_disk_info = {
                        "size": disk.disk_size_gb if hasattr(disk, 'disk_size_gb') else 20,
                        "image": disk.source.split('/')[-1] if disk.source else "unknown"
                    }
                    break
        
        # Extract network interfaces
        network_interfaces = []
        for interface in instance.network_interfaces:
            interface_data = {
                "network": interface.network.split('/')[-1] if interface.network else "",
                "subnetwork": interface.subnetwork.split('/')[-1] if interface.subnetwork else "",
                "internal_ip": interface.network_i_p if hasattr(interface, 'network_i_p') else "",
                "has_external_ip": len(interface.access_configs) > 0 if interface.access_configs else False
            }
            network_interfaces.append(interface_data)
        
        # Extract labels (GCP's version of tags)
        labels = dict(instance.labels) if instance.labels else {}
        
        return {
            "id": f"projects/{project_id}/zones/{zone}/instances/{instance.name}",
            "name": instance.name,
            "type": "google_compute_instance",
            "attributes": {
                "machine_type": machine_type,
                "zone": zone,
                "status": instance.status,
                "boot_disk": boot_disk_info,
                "network_interfaces": network_interfaces,
                "creation_timestamp": instance.creation_timestamp,
                "self_link": instance.self_link
            },
            "tags": labels,
            "metadata": {
                "region": region,
                "zone": zone,
                "project_id": project_id
            }
        }
    
    def _convert_gcp_network(self, network, project_id: str, region: str) -> Dict[str, Any]:
        """Convert GCP network to our resource format"""
        return {
            "id": f"projects/{project_id}/global/networks/{network.name}",
            "name": network.name,
            "type": "google_compute_network",
            "attributes": {
                "routing_mode": network.routing_config.routing_mode if network.routing_config else "REGIONAL",
                "auto_create_subnetworks": network.auto_create_subnetworks,
                "mtu": network.mtu if hasattr(network, 'mtu') else 1460,
                "creation_timestamp": network.creation_timestamp,
                "self_link": network.self_link
            },
            "tags": {},
            "metadata": {
                "region": region,
                "project_id": project_id
            }
        }
    
    def _convert_gcp_subnet(self, subnet, project_id: str, region: str) -> Dict[str, Any]:
        """Convert GCP subnet to our resource format"""
        return {
            "id": f"projects/{project_id}/regions/{region}/subnetworks/{subnet.name}",
            "name": subnet.name,
            "type": "google_compute_subnetwork",
            "attributes": {
                "ip_cidr_range": subnet.ip_cidr_range,
                "network": subnet.network.split('/')[-1] if subnet.network else "",
                "region": region,
                "private_ip_google_access": subnet.private_ip_google_access,
                "creation_timestamp": subnet.creation_timestamp,
                "self_link": subnet.self_link
            },
            "tags": {},
            "metadata": {
                "region": region,
                "project_id": project_id
            }
        }
    
    def _convert_gcp_cloudrun_service(self, service, project_id: str, region: str) -> Dict[str, Any]:
        """Convert GCP Cloud Run service to our resource format"""
        # Extract service name from full resource name
        # Format: projects/{project}/locations/{location}/services/{service}
        service_name = service.name.split('/')[-1]
        
        # Extract traffic allocation
        traffic_info = []
        if hasattr(service, 'spec') and hasattr(service.spec, 'traffic'):
            for traffic in service.spec.traffic:
                traffic_info.append({
                    "percent": traffic.percent,
                    "revision": traffic.revision if hasattr(traffic, 'revision') else None,
                    "tag": traffic.tag if hasattr(traffic, 'tag') else None
                })
        
        # Extract container configuration (Cloud Run v2 API structure)
        container_info = {}
        if hasattr(service, 'template') and hasattr(service.template, 'containers'):
            # Cloud Run v2 API structure
            containers = service.template.containers
            if containers and len(containers) > 0:
                container = containers[0]  # Get first container
                container_info = {
                    "image": container.image if hasattr(container, 'image') else "",
                    "ports": [port.container_port for port in container.ports] if hasattr(container, 'ports') and container.ports else [8080],
                    "cpu": None,
                    "memory": None
                }
                
                # Extract resources (CPU and memory)
                if hasattr(container, 'resources'):
                    if hasattr(container.resources, 'limits'):
                        limits = container.resources.limits
                        container_info["cpu"] = limits.get("cpu", None)
                        container_info["memory"] = limits.get("memory", None)
        
        # Extract labels (Cloud Run's version of tags)
        labels = {}
        if hasattr(service, 'metadata') and hasattr(service.metadata, 'labels'):
            labels = dict(service.metadata.labels)
        
        # Extract conditions for status
        conditions = []
        if hasattr(service, 'status') and hasattr(service.status, 'conditions'):
            for condition in service.status.conditions:
                conditions.append({
                    "type": condition.type,
                    "status": condition.status,
                    "reason": getattr(condition, 'reason', ''),
                    "message": getattr(condition, 'message', '')
                })
        
        return {
            "id": service.name,
            "name": service_name,
            "type": "google_cloud_run_service",
            "attributes": {
                "location": region,
                "container": container_info,
                "traffic": traffic_info,
                "ingress": getattr(service, 'ingress', 'INGRESS_TRAFFIC_ALL') if hasattr(service, 'ingress') else 'INGRESS_TRAFFIC_ALL',
                "service_account_email": getattr(service.template, 'service_account', '') if hasattr(service, 'template') and hasattr(service.template, 'service_account') else '',
                "conditions": conditions,
                "creation_timestamp": service.metadata.creation_timestamp if hasattr(service, 'metadata') else None,
                "generation": service.metadata.generation if hasattr(service, 'metadata') else None
            },
            "tags": labels,
            "metadata": {
                "region": region,
                "project_id": project_id,
                "resource_type": "cloud_run_service"
            }
        }
    
    def _generate_digitalocean_mock_resources(self, region: str) -> List[Dict[str, Any]]:
        """Generate mock DigitalOcean resources"""
        return [
            {
                "id": f"droplet-{region}-001",
                "name": f"web-server-{region}",
                "type": "digitalocean_droplet",
                "attributes": {
                    "size": "s-2vcpu-2gb",
                    "image": "ubuntu-20-04-x64",
                    "region": region,
                    "vpc_uuid": f"vpc-{region}-001"
                },
                "tags": {"environment": "production", "tier": "web"},
                "metadata": {"region": region}
            },
            {
                "id": f"vpc-{region}-001",
                "name": f"main-vpc-{region}",
                "type": "digitalocean_vpc",
                "attributes": {
                    "ip_range": "10.0.0.0/16",
                    "region": region
                },
                "tags": {"environment": "production"},
                "metadata": {"region": region}
            },
            {
                "id": f"db-{region}-001",
                "name": f"postgres-{region}",
                "type": "digitalocean_database_cluster",
                "attributes": {
                    "engine": "pg",
                    "version": "13",
                    "size": "db-s-1vcpu-1gb",
                    "region": region,
                    "num_nodes": 1
                },
                "tags": {"environment": "production", "type": "database"},
                "metadata": {"region": region}
            }
        ]
    
    def _create_resource_node(self, 
                            resource_data: Dict[str, Any],
                            provider: str,
                            region: str) -> ResourceNode:
        """Convert resource data to ResourceNode"""
        return ResourceNode(
            id=resource_data.get("id", f"unknown-{int(time.time())}"),
            name=resource_data.get("name", "unnamed"),
            type=resource_data.get("type", "unknown"),
            provider=provider,
            region=region,
            metadata=resource_data.get("metadata", {}),
            attributes=resource_data.get("attributes", {}),
            tags=resource_data.get("tags", {})
        )
    
    async def _tag_resources_batch(self, resources: List[ResourceNode]) -> int:
        """Tag resources in parallel batches"""
        logger.debug(f"Tagging {len(resources)} resources")
        
        # Add import timestamp
        timestamp = datetime.now(timezone.utc).isoformat()
        tags_to_add = {
            **self._management_tags,
            "infradsl.import.timestamp": timestamp
        }
        
        # Process in batches to avoid overwhelming APIs
        tagged_count = 0
        batches = self._create_batches(resources, self.batch_size)
        
        tag_tasks = []
        for batch in batches:
            task = self._tag_resource_batch(batch, tags_to_add)
            tag_tasks.append(task)
        
        # Wait for all tagging to complete
        batch_results = await asyncio.gather(*tag_tasks, return_exceptions=True)
        
        for result in batch_results:
            if isinstance(result, Exception):
                logger.warning(f"Batch tagging failed: {result}")
            else:
                tagged_count += result
        
        return tagged_count
    
    async def _tag_resource_batch(self, 
                                batch: List[ResourceNode],
                                tags: Dict[str, str]) -> int:
        """Tag a batch of resources"""
        loop = asyncio.get_event_loop()
        tagged_count = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            tag_futures = []
            
            for resource in batch:
                future = executor.submit(self._tag_single_resource, resource, tags)
                tag_futures.append(future)
            
            # Wait for all tags to complete
            for future in as_completed(tag_futures):
                try:
                    result = await loop.run_in_executor(None, lambda: future.result())
                    if result:
                        tagged_count += 1
                except Exception as e:
                    logger.warning(f"Failed to tag resource: {e}")
        
        return tagged_count
    
    def _tag_single_resource(self, resource: ResourceNode, tags: Dict[str, str]) -> bool:
        """Tag a single resource (sync operation)"""
        try:
            # This would call the actual provider API to add tags
            # For now, simulate the operation
            logger.debug(f"Tagging resource {resource.id} with {len(tags)} tags")
            
            # Update resource tags locally
            resource.tags.update(tags)
            
            # TODO: Implement actual provider-specific tagging
            # provider = self._get_provider_client(resource.provider)
            # provider.tag_resource(resource.id, tags)
            
            return True
            
        except Exception as e:
            logger.warning(f"Failed to tag resource {resource.id}: {e}")
            return False
    
    async def _cache_resources_batch(self, resources: List[ResourceNode]) -> int:
        """Cache resources in parallel batches"""
        logger.debug(f"Caching {len(resources)} resources")
        
        # TODO: Implement actual cache integration
        # This would integrate with the PostgreSQL cache system
        cached_count = 0
        
        batches = self._create_batches(resources, self.batch_size)
        
        cache_tasks = []
        for batch in batches:
            task = self._cache_resource_batch(batch)
            cache_tasks.append(task)
        
        batch_results = await asyncio.gather(*cache_tasks, return_exceptions=True)
        
        for result in batch_results:
            if isinstance(result, Exception):
                logger.warning(f"Batch caching failed: {result}")
            else:
                cached_count += result
        
        return cached_count
    
    async def _cache_resource_batch(self, batch: List[ResourceNode]) -> int:
        """Cache a batch of resources"""
        try:
            from ..cache.simple_postgres_cache import get_simple_cache
            cache = get_simple_cache()
            
            cached_count = 0
            for resource in batch:
                try:
                    # Convert ResourceNode to state data for caching
                    state_data = {
                        "id": resource.id,
                        "name": resource.name,
                        "type": resource.type,
                        "provider": resource.provider,
                        "region": resource.region,
                        "attributes": resource.attributes,
                        "tags": resource.tags,
                        "metadata": resource.metadata,
                        "variable_name": resource.variable_name,
                        "discovered_at": datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Cache the resource state
                    cache.cache_resource_state(
                        provider=resource.provider,
                        resource_type=resource.type,
                        resource_id=resource.id,
                        resource_name=resource.name,
                        state_data=state_data,
                        project=resource.metadata.get("project_id", ""),
                        environment=resource.tags.get("Environment", resource.tags.get("env", "production")),
                        region=resource.region,
                        ttl_seconds=86400  # 24 hours TTL for discovered resources
                    )
                    cached_count += 1
                    logger.debug(f"Cached resource {resource.id} in PostgreSQL")
                    
                except Exception as e:
                    logger.warning(f"Failed to cache resource {resource.id}: {e}")
            
            return cached_count
            
        except ImportError:
            logger.warning("PostgreSQL cache not available. Resources will not be cached.")
            return 0
        except Exception as e:
            logger.error(f"Error caching resource batch: {e}")
            return 0
    
    def _create_batches(self, items: List[Any], batch_size: int) -> List[List[Any]]:
        """Split items into batches"""
        batches = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batches.append(batch)
        return batches
    
    def _get_default_regions(self, providers: List[str]) -> Dict[str, List[str]]:
        """Get default regions for providers"""
        default_regions = {
            "aws": ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
            "gcp": ["us-central1", "us-east1", "europe-west1", "asia-southeast1"], 
            "digitalocean": ["nyc1", "sfo3", "lon1", "sgp1"]
        }
        
        return {
            provider: default_regions.get(provider, ["default"])
            for provider in providers
        }
    
    def get_progress(self) -> DiscoveryProgress:
        """Get current discovery progress"""
        return self.progress
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get discovery statistics"""
        return {
            "total_resources_discovered": self.progress.resources_discovered,
            "total_resources_tagged": self.progress.resources_tagged,
            "total_resources_cached": self.progress.resources_cached,
            "discovery_time": self.progress.elapsed_time,
            "discovery_rate": self.progress.resources_per_second,
            "providers_completed": self.progress.providers_completed,
            "total_providers": self.progress.total_providers,
            "error_count": len(self.progress.errors),
            "success_rate": (
                (self.progress.providers_completed / self.progress.total_providers)
                if self.progress.total_providers > 0 else 0.0
            ) * 100
        }


async def discover_and_import(providers: List[str],
                            regions: Optional[Dict[str, List[str]]] = None,
                            filters: Optional[Dict[str, Any]] = None,
                            auto_tag: bool = True,
                            max_workers: int = 10) -> DependencyGraph:
    """
    Convenience function for resource discovery and import.
    
    Args:
        providers: List of cloud providers to discover
        regions: Provider-specific regions to search
        filters: Resource filters (tags, types, etc.)
        auto_tag: Whether to tag resources as InfraDSL managed
        max_workers: Maximum parallel workers
    
    Returns:
        DependencyGraph with all discovered resources
    """
    engine = ResourceDiscoveryEngine(max_workers=max_workers)
    
    dependency_graph = await engine.discover_all_resources(
        providers=providers,
        regions=regions,
        filters=filters,
        auto_tag=auto_tag
    )
    
    # Log summary
    stats = engine.get_statistics()
    logger.info(
        f"Import Summary: "
        f"{stats['total_resources_discovered']} resources discovered, "
        f"{stats['total_resources_tagged']} tagged, "
        f"{stats['total_resources_cached']} cached "
        f"in {stats['discovery_time']:.2f}s "
        f"({stats['discovery_rate']:.1f} resources/sec)"
    )
    
    return dependency_graph


class ProgressReporter:
    """Real-time progress reporting for resource discovery"""
    
    def __init__(self, engine: ResourceDiscoveryEngine):
        self.engine = engine
        self._reporting = False
    
    async def start_reporting(self, interval: float = 1.0):
        """Start real-time progress reporting"""
        self._reporting = True
        
        while self._reporting:
            progress = self.engine.get_progress()
            self._print_progress(progress)
            await asyncio.sleep(interval)
    
    def stop_reporting(self):
        """Stop progress reporting"""
        self._reporting = False
    
    def _print_progress(self, progress: DiscoveryProgress):
        """Print formatted progress information"""
        elapsed = progress.elapsed_time
        rate = progress.resources_per_second
        
        print(f"\r🔍 Discovery Progress: "
              f"{progress.resources_discovered} resources "
              f"({progress.providers_completed}/{progress.total_providers} providers) "
              f"| {rate:.1f} res/sec "
              f"| {elapsed:.1f}s elapsed", end="", flush=True)


# Export key classes and functions
__all__ = [
    "ResourceDiscoveryEngine",
    "DiscoveryProgress", 
    "ProviderDiscoveryResult",
    "ProgressReporter",
    "discover_and_import"
]