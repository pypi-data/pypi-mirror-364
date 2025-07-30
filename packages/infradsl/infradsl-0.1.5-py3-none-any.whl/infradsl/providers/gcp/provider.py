"""
Google Cloud Platform Compute Engine Provider Implementation
"""

import os
from typing import Any, Dict, List, Optional

from ...core.interfaces.provider import (
    ProviderInterface,
    ProviderType,
    ProviderConfig,
    ResourceMetadata,
    ResourceQuery,
)
from ...core.exceptions import ProviderException

from .services.compute import ComputeService
from .services.dns import DNSService
from .services.cloud_run import CloudRunService

import logging
logger = logging.getLogger(__name__)


class GCPComputeProvider(ProviderInterface):
    """
    Google Cloud Platform Compute Engine provider implementation.

    Supports:
    - Compute Engine instances (VMs)
    - Instance templates
    - Machine types and images
    - Labels (GCP's version of tags)
    - Regions and zones
    """

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.config = config
        self._compute_client = None
        self._project_id = None
        self._validate_config()
        self._initialize()

        # Initialize services
        self.compute = ComputeService(self)
        self.dns = DNSService(self)
        self.cloud_run = CloudRunService(self)

    def _validate_config(self) -> None:
        """Validate GCP configuration"""
        # Project ID is required
        if not self.config.project:
            # Try to get from environment
            project = os.getenv("GOOGLE_CLOUD_PROJECT")
            if project:
                self.config.project = project
            else:
                raise ProviderException(
                    "GCP project ID is required. Set project in config or GOOGLE_CLOUD_PROJECT environment variable."
                )

        # Always allow preview operations without full credential validation
        try:
            # Check for Google Cloud libraries first
            import google.auth
            import google.cloud.compute_v1
        except ImportError:
            raise ProviderException(
                "Google Cloud SDK not installed. Run: pip install google-cloud-compute google-auth"
            )

    def _initialize(self) -> None:
        """Initialize GCP Compute Engine client"""
        try:
            # Import Google Cloud libraries
            from google.cloud import compute_v1
            from google.auth import default

            # Try to initialize credentials
            credentials = None
            if (
                self.config.credentials
                and "service_account_path" in self.config.credentials
            ):
                try:
                    from google.oauth2.service_account import Credentials
                    import json

                    service_account_path = self.config.credentials[
                        "service_account_path"
                    ]
                    with open(service_account_path) as f:
                        credentials_info = json.load(f)
                    credentials = Credentials.from_service_account_info(
                        credentials_info
                    )
                except Exception as e:
                    print(f"[DEBUG] Could not load service account credentials: {e}")
                    credentials = None

            if credentials is None:
                try:
                    # Use default credentials (ADC)
                    credentials, project = default()
                    if not self.config.project:
                        self.config.project = project
                except Exception:
                    credentials = None

            # Initialize compute client
            if credentials:
                self._compute_client = compute_v1.InstancesClient(
                    credentials=credentials
                )
            else:
                self._compute_client = None

            self._project_id = self.config.project

        except Exception as e:
            raise ProviderException(f"Failed to initialize GCP Compute client: {e}")

    def create_resource(
        self, resource_type: str, config: Dict[str, Any], metadata: ResourceMetadata
    ) -> Dict[str, Any]:
        """Create a GCP resource"""
        if resource_type == "instance":
            return self.compute.create_instance(config, metadata)
        elif resource_type == "dns_managed_zone":
            return self.dns.create_managed_zone(config, metadata)
        elif resource_type == "cloud_run_service":
            return self.cloud_run.create_service(config, metadata)
        else:
            raise ProviderException(f"Unsupported resource type: {resource_type}")

    def update_resource(
        self, resource_id: str, resource_type: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a GCP resource"""
        if resource_type == "instance":
            return self.compute.update_instance(resource_id, updates)
        elif resource_type == "dns_managed_zone":
            return self.dns.update_managed_zone(resource_id, updates)
        elif resource_type == "cloud_run_service":
            return self.cloud_run.update_service(resource_id, updates)
        else:
            raise ProviderException(f"Unsupported resource type: {resource_type}")

    def delete_resource(self, resource_id: str, resource_type: str) -> None:
        """Delete a GCP resource"""
        if resource_type == "instance":
            self.compute.delete_instance(resource_id)
        elif resource_type == "dns_managed_zone":
            self.dns.delete_managed_zone(resource_id)
        elif resource_type == "cloud_run_service":
            self.cloud_run.delete_service(resource_id)
        else:
            raise ProviderException(f"Unsupported resource type: {resource_type}")

    def get_resource(
        self, resource_id: str, resource_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get a single GCP resource by ID"""
        if resource_type == "instance":
            return self.compute.get_instance(resource_id)
        elif resource_type == "dns_managed_zone":
            return self.dns.get_managed_zone(resource_id)
        else:
            raise ProviderException(f"Unsupported resource type: {resource_type}")

    def list_resources(
        self, resource_type: str, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """List GCP resources"""
        if resource_type == "instance":
            return self.compute.list_instances(query)
        elif resource_type == "dns_managed_zone":
            return self.dns.list_managed_zones(query)
        elif resource_type == "cloud_run_service":
            location = query.filters.get("location") if query and query.filters else None
            return self.cloud_run.list_services(location)
        else:
            raise ProviderException(f"Unsupported resource type: {resource_type}")

    def tag_resource(
        self, resource_id: str, resource_type: str, tags: Dict[str, str]
    ) -> None:
        """Apply labels to a GCP Compute resource"""
        if resource_type == "instance":
            self.compute.tag_instance(resource_id, tags)
        else:
            raise ProviderException(f"Unsupported resource type: {resource_type}")

    async def update_resource_tags(self, resource_id: str, tags: Dict[str, str]) -> None:
        """
        Update resource labels for Pillar 1: Enhanced "Codify My Cloud" Import Tool.
        
        This method is specifically for instant labeling during import to mark
        resources as InfraDSL-managed without requiring 'infra apply'.
        
        Note: GCP uses "labels" instead of "tags", but we maintain the same interface.
        """
        try:
            # Determine resource type by looking up the resource
            resource_type = await self._determine_resource_type(resource_id)
            
            if resource_type == "instance":
                # Use GCP Compute Engine labeling API
                try:
                    from google.cloud import compute_v1
                    import asyncio
                    
                    if not self._compute_client:
                        raise ProviderException("GCP Compute client not initialized")
                    
                    # Parse zone and instance name from resource ID
                    if "/" in resource_id:
                        if "projects/" in resource_id:
                            # Full URL format: projects/PROJECT/zones/ZONE/instances/NAME
                            parts = resource_id.split("/")
                            zone = parts[3] if len(parts) >= 4 else self.config.region
                            instance_name = parts[5] if len(parts) >= 6 else resource_id
                        else:
                            # Simple format: ZONE/INSTANCE_NAME (our discovery format)
                            parts = resource_id.split("/")
                            if len(parts) == 2:
                                zone, instance_name = parts
                            else:
                                # Fallback
                                instance_name = resource_id
                                zone = self.config.region
                    else:
                        # Simple instance name
                        instance_name = resource_id
                        zone = self.config.region
                    
                    logger.debug(f"Labeling GCP instance: project={self._project_id}, zone={zone}, instance={instance_name}")
                    
                    # Get current instance to preserve existing labels with timeout
                    try:
                        # Add timeout for the get operation
                        instance = self._compute_client.get(
                            request={
                                "project": self._project_id,
                                "zone": zone,
                                "instance": instance_name
                            },
                            timeout=30  # 30 second timeout
                        )
                        logger.debug(f"Retrieved instance {instance_name}, current labels: {instance.labels}")
                    except Exception as e:
                        logger.error(f"Failed to get instance {instance_name}: {e}")
                        raise ProviderException(f"Failed to get instance: {e}")
                    
                    # Merge new labels with existing ones
                    current_labels = dict(instance.labels) if instance.labels else {}
                    
                    # Convert InfraDSL tags to GCP-compatible labels
                    # GCP labels must be lowercase and can only contain lowercase letters, numbers, hyphens, and underscores
                    gcp_labels = {}
                    for key, value in tags.items():
                        # Convert to GCP-compatible format
                        gcp_key = key.lower().replace(".", "_").replace(":", "_").replace("-", "_")
                        gcp_value = str(value).lower().replace(".", "_").replace(":", "_").replace("-", "_")
                        # Remove any invalid characters and limit length
                        gcp_key = ''.join(c for c in gcp_key if c.isalnum() or c == '_')[:63]
                        gcp_value = ''.join(c for c in gcp_value if c.isalnum() or c == '_')[:63]
                        if gcp_key and gcp_value:  # Only add if both key and value are valid
                            gcp_labels[gcp_key] = gcp_value
                    
                    logger.debug(f"Converted labels: {gcp_labels}")
                    
                    # Merge labels
                    updated_labels = {**current_labels, **gcp_labels}
                    logger.debug(f"Final labels to set: {updated_labels}")
                    
                    # Update instance labels with timeout
                    try:
                        operation = self._compute_client.set_labels(
                            request={
                                "project": self._project_id,
                                "zone": zone,
                                "instance": instance_name,
                                "instances_set_labels_request_resource": {
                                    "labels": updated_labels,
                                    "label_fingerprint": instance.label_fingerprint
                                }
                            },
                            timeout=30  # 30 second timeout
                        )
                        
                        # Don't wait for operation to complete for performance
                        # The labeling will complete asynchronously
                        operation_name = getattr(operation, 'name', 'unknown')
                        logger.debug(f"Started label operation for instance {instance_name}: {operation_name}")
                        logger.info(f"Successfully started labeling operation for GCP instance {instance_name} with {len(gcp_labels)} labels")
                        
                    except Exception as e:
                        logger.error(f"Failed to set labels on instance {instance_name}: {e}")
                        # Check if it's a specific GCP error
                        if "timeout" in str(e).lower():
                            logger.warning(f"Labeling operation timed out for {instance_name}, but may complete asynchronously")
                        else:
                            raise ProviderException(f"Failed to set labels: {e}")
                    
                except Exception as e:
                    logger.error(f"Failed to label GCP instance {resource_id}: {e}")
                    import traceback
                    logger.debug(f"Full error traceback: {traceback.format_exc()}")
                    raise ProviderException(f"Failed to label GCP instance: {e}")
                    
            elif resource_type == "disk":
                # Handle GCP persistent disks
                try:
                    from google.cloud import compute_v1
                    
                    if not self._compute_client:
                        raise ProviderException("GCP Compute client not initialized")
                    
                    # Parse zone and disk name from resource ID
                    if "/" in resource_id:
                        if "projects/" in resource_id:
                            # Full URL format: projects/PROJECT/zones/ZONE/disks/NAME
                            parts = resource_id.split("/")
                            zone = parts[3] if len(parts) >= 4 else self.config.region
                            disk_name = parts[5] if len(parts) >= 6 else resource_id
                        else:
                            # Simple format: ZONE/DISK_NAME (our discovery format)
                            parts = resource_id.split("/")
                            if len(parts) == 2:
                                zone, disk_name = parts
                            else:
                                # Fallback
                                disk_name = resource_id
                                zone = self.config.region
                    else:
                        disk_name = resource_id
                        zone = self.config.region
                    
                    # Get disk client
                    disk_client = compute_v1.DisksClient(credentials=self._compute_client._transport._credentials)
                    
                    # Get current disk to preserve existing labels
                    disk = disk_client.get(
                        project=self._project_id,
                        zone=zone,
                        disk=disk_name
                    )
                    
                    # Convert and merge labels
                    current_labels = disk.labels or {}
                    gcp_labels = {}
                    for key, value in tags.items():
                        gcp_key = key.lower().replace(".", "_").replace(":", "_")
                        gcp_value = value.lower().replace(".", "_").replace(":", "_")
                        gcp_labels[gcp_key] = gcp_value
                    
                    updated_labels = {**current_labels, **gcp_labels}
                    
                    # Update disk labels
                    operation = disk_client.set_labels(
                        project=self._project_id,
                        zone=zone,
                        disk=disk_name,
                        zone_set_labels_request_resource=compute_v1.ZoneSetLabelsRequest(
                            labels=updated_labels,
                            label_fingerprint=disk.label_fingerprint
                        )
                    )
                    
                    logger.info(f"Successfully labeled GCP disk {disk_name} with {len(tags)} labels")
                    
                except Exception as e:
                    logger.error(f"Failed to label GCP disk {resource_id}: {e}")
                    raise ProviderException(f"Failed to label GCP disk: {e}")
                    
            else:
                logger.warning(f"Unknown resource type '{resource_type}' for {resource_id}, skipping labeling")
                
        except Exception as e:
            logger.error(f"Failed to update labels for resource {resource_id}: {e}")
            raise ProviderException(f"Label update failed: {e}")

    async def _determine_resource_type(self, resource_id: str) -> str:
        """Determine the GCP resource type for a given resource ID"""
        try:
            # GCP resource IDs can be names or full URLs
            if "/" in resource_id:
                # Full URL format: projects/PROJECT/zones/ZONE/instances/NAME
                parts = resource_id.split("/")
                if len(parts) >= 5:
                    resource_type_part = parts[4]  # "instances", "disks", etc.
                    if resource_type_part == "instances":
                        return "instance"
                    elif resource_type_part == "disks":
                        return "disk"
                    elif resource_type_part == "networks":
                        return "network"
                    elif resource_type_part == "firewalls":
                        return "firewall"
            
            # For simple names, try to determine by making API calls
            return await self._determine_resource_type_by_lookup(resource_id)
                
        except Exception as e:
            logger.error(f"Error determining resource type for {resource_id}: {e}")
            return "instance"  # Default fallback

    async def _determine_resource_type_by_lookup(self, resource_id: str) -> str:
        """Determine resource type by making API calls"""
        try:
            if not self._compute_client:
                logger.warning("GCP Compute client not available for resource type lookup")
                return "instance"
            
            # Try instance first (most common)
            try:
                zone = self.config.region
                instance = self._compute_client.get(
                    project=self._project_id,
                    zone=zone,
                    instance=resource_id
                )
                if instance:
                    return "instance"
            except Exception:
                pass
            
            # Try disk
            try:
                from google.cloud import compute_v1
                disk_client = compute_v1.DisksClient(credentials=self._compute_client._transport._credentials)
                zone = self.config.region
                disk = disk_client.get(
                    project=self._project_id,
                    zone=zone,
                    disk=resource_id
                )
                if disk:
                    return "disk"
            except Exception:
                pass
            
            # Default to instance
            logger.warning(f"Could not determine resource type for {resource_id}, defaulting to instance")
            return "instance"
            
        except Exception as e:
            logger.error(f"Error in resource type lookup for {resource_id}: {e}")
            return "instance"

    def estimate_cost(
        self, resource_type: str, config: Dict[str, Any]
    ) -> Dict[str, float]:
        """Estimate cost for GCP resources"""
        if resource_type == "instance":
            return self.compute.estimate_cost(config)
        elif resource_type == "dns_managed_zone":
            return self.dns.estimate_cost(config)
        else:
            return {"hourly": 0.0, "monthly": 0.0}

    def validate_config(self, resource_type: str, config: Dict[str, Any]) -> List[str]:
        """Validate GCP resource configuration"""
        if resource_type == "instance":
            return self.compute.validate_config(config)
        elif resource_type == "dns_managed_zone":
            return self.dns.validate_config(config)
        else:
            return []

    def get_resource_types(self) -> List[str]:
        """Get list of supported resource types"""
        return ["instance", "dns_managed_zone", "dns_records", "cloud_run_service"]

    def get_regions(self) -> List[str]:
        """Get list of available GCP regions"""
        return self.compute.get_regions()

    def discover_resources(
        self, resource_type: str, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """Discover resources in GCP using broader discovery mechanisms"""
        return self.list_resources(resource_type, query)

    def get_resource_state(self, metadata: ResourceMetadata) -> Optional[Dict[str, Any]]:
        """
        Get resource state using InfraDSL metadata for GCP resources.
        Uses fingerprint-based lookup for unique resource identification.
        """
        # Determine resource type from metadata annotations
        resource_type_annotation = metadata.annotations.get('resource_type', '')
        
        if resource_type_annotation == 'VirtualMachine':
            # Map to GCP instance resource type
            gcp_resource_type = "google_compute_instance"
        elif resource_type_annotation == 'CloudDNS':
            # Map to GCP DNS managed zone resource type
            gcp_resource_type = "google_dns_managed_zone"
        elif resource_type_annotation == 'CloudRun':
            # Map to GCP Cloud Run service resource type
            gcp_resource_type = "google_cloud_run_service"
        else:
            # For other types, use annotation as-is or default
            gcp_resource_type = resource_type_annotation.lower()
        
        try:
            # Use fingerprint-based lookup from cache for unique identification
            from ...core.cache.simple_postgres_cache import get_simple_cache
            cache = get_simple_cache()
            
            # Get project and environment from metadata (matching cache logic)
            project_id = metadata.project or self._project_id or ""
            environment = metadata.environment or "production"  # Default to production like cache logic
            
            # For Cloud Run, use the region from metadata if available
            region = ""
            if resource_type_annotation == 'CloudRun':
                # Try to get region from metadata or use default
                region = metadata.annotations.get('region', 'us-central1')
                # Look for cloud_id in annotations which might contain it from .imported() call
                if 'cloud_id' in metadata.annotations:
                    cloud_id = metadata.annotations['cloud_id']
                    if 'projects/' in cloud_id:
                        parts = cloud_id.split('/')
                        if len(parts) >= 2:
                            extracted_project = parts[1]
                            if extracted_project:
                                project_id = extracted_project
                                logger.debug(f"Extracted project {project_id} from cloud_id: {cloud_id}")
                    if 'locations/' in cloud_id:
                        parts = cloud_id.split('/')
                        for i, part in enumerate(parts):
                            if part == 'locations' and i + 1 < len(parts):
                                extracted_region = parts[i + 1]
                                if extracted_region:
                                    region = extracted_region
                                    logger.debug(f"Extracted region {region} from cloud_id: {cloud_id}")
            
            # Look up resource by fingerprint
            logger.debug(f"Looking up resource by fingerprint: provider='gcp', type={gcp_resource_type!r}, name={metadata.name!r}, project={project_id!r}, environment={environment!r}, region={region!r}")
            
            cached_resource = cache.get_resource_by_fingerprint(
                provider="gcp",
                resource_type=gcp_resource_type,
                resource_name=metadata.name,
                project=project_id,
                environment=environment,
                region=region
            )
            
            if cached_resource:
                logger.debug(f"Found cached {gcp_resource_type} resource by fingerprint: {metadata.name}")
                return cached_resource
            
            logger.debug(f"No cached {gcp_resource_type} resource found by fingerprint for {metadata.name}")
            return None
            
        except Exception as e:
            logger.debug(f"Error looking up resource state by fingerprint for {metadata.name}: {e}")
            # Fallback to legacy name-based lookup if fingerprint lookup fails
            return self._fallback_name_based_lookup(metadata, gcp_resource_type)
    
    def _fallback_name_based_lookup(self, metadata: ResourceMetadata, gcp_resource_type: str) -> Optional[Dict[str, Any]]:
        """Fallback to name-based lookup if fingerprint lookup fails"""
        try:
            # Map GCP resource types to provider resource types for legacy lookup
            provider_resource_type = gcp_resource_type
            if gcp_resource_type == "google_compute_instance":
                provider_resource_type = "instance"
            elif gcp_resource_type == "google_dns_managed_zone":
                provider_resource_type = "dns_managed_zone"
            elif gcp_resource_type == "google_cloud_run_service":
                provider_resource_type = "cloud_run_service"
            
            # Check if this resource type is supported
            if provider_resource_type not in self.get_resource_types():
                logger.debug(f"Unsupported resource type for state lookup: {provider_resource_type}")
                return None
            
            # Use tags to find the resource, specifically filtering by name
            query = ResourceQuery().by_labels(**metadata.to_tags())
            resources = self.list_resources(provider_resource_type, query)
            
            if not resources:
                logger.debug(f"No {provider_resource_type} resources found matching metadata for {metadata.name}")
                return None
            
            # Filter by exact resource name to prevent cross-resource contamination
            matching_resources = []
            for resource in resources:
                # Check if the resource has the correct infradsl.name tag
                resource_tags = resource.get('tags', {})
                infradsl_name = resource_tags.get('infradsl.name') or resource_tags.get('infradsl_name')
                
                # Also check the actual GCP resource name as fallback
                gcp_resource_name = resource.get('name', '')
                
                if infradsl_name == metadata.name or gcp_resource_name == metadata.name:
                    matching_resources.append(resource)
                    logger.debug(f"Found matching {provider_resource_type} resource: {resource.get('name')} (infradsl.name: {infradsl_name})")
            
            if not matching_resources:
                logger.debug(f"No {provider_resource_type} resources found with exact name match for {metadata.name}")
                return None
            
            if len(matching_resources) > 1:
                logger.warning(f"Multiple {provider_resource_type} resources found for {metadata.name}, using first match")
            
            # Return the correctly matched resource
            resource = matching_resources[0]
            logger.debug(f"Returning {provider_resource_type} resource: {resource.get('name')} (id: {resource.get('id')})")
            return resource
            
        except Exception as e:
            logger.debug(f"Error in fallback name-based lookup for {metadata.name}: {e}")
            return None

    def plan_create(
        self, resource_type: str, config: Dict[str, Any], metadata: ResourceMetadata
    ) -> Dict[str, Any]:
        """Preview the creation of a GCP resource"""
        try:
            plan = {
                "action": "create",
                "resource_type": resource_type,
                "name": config.get("name", "unnamed"),
                "provider": "gcp",
                "config": config,
                "metadata": {
                    "id": metadata.id,
                    "name": metadata.name,
                    "project": metadata.project,
                    "environment": metadata.environment,
                },
                "estimated_cost": self.estimate_cost(resource_type, config),
            }

            if resource_type == "instance":
                plan["preview"] = self.compute.preview_create(config)
            elif resource_type == "dns_managed_zone":
                plan["preview"] = self.dns.preview_create(config)

            return plan
        except Exception as e:
            return {
                "action": "create",
                "resource_type": resource_type,
                "error": str(e),
            }

    def plan_update(
        self, resource_id: str, resource_type: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Preview the update of a GCP resource"""
        try:
            current_resource = self.get_resource(resource_id, resource_type)

            plan = {
                "action": "update",
                "resource_type": resource_type,
                "resource_id": resource_id,
                "provider": "gcp",
                "changes": updates,
                "current_state": current_resource,
            }

            if resource_type == "instance":
                plan["preview"] = self.compute.preview_update(resource_id, updates)

            return plan
        except Exception as e:
            return {
                "action": "update",
                "resource_type": resource_type,
                "resource_id": resource_id,
                "error": str(e),
            }

    def plan_delete(self, resource_id: str, resource_type: str) -> Dict[str, Any]:
        """Preview the deletion of a GCP resource"""
        try:
            current_resource = self.get_resource(resource_id, resource_type)

            plan = {
                "action": "delete",
                "resource_type": resource_type,
                "resource_id": resource_id,
                "provider": "gcp",
                "current_state": current_resource,
            }

            if resource_type == "instance":
                plan["warnings"] = self.compute.get_delete_warnings()

            return plan
        except Exception as e:
            return {
                "action": "delete",
                "resource_type": resource_type,
                "resource_id": resource_id,
                "error": str(e),
            }
    @property
    def project_id(self) -> str:
        """Get the GCP project ID"""
        return self.config.project
