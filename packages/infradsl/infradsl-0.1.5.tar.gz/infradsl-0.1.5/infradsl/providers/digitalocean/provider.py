"""
DigitalOcean Provider Implementation
"""

import os
import logging
from typing import Any, Dict, List, Optional
import digitalocean as do_client

from ...core.interfaces.provider import (
    ProviderInterface,
    ProviderType,
    ProviderConfig,
    ResourceMetadata,
    ResourceQuery,
)
from ...core.exceptions import ProviderException
from .services import DropletService, DatabaseService

logger = logging.getLogger(__name__)


class DigitalOceanProvider(ProviderInterface):
    """
    DigitalOcean provider implementation using the official SDK.

    Supports:
    - Droplets (VMs)
    - Managed Databases (PostgreSQL, MySQL, Redis, MongoDB)
    - SSH Keys
    - Regions
    - Sizes (instance types)
    - Images
    """

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.config = config
        self._client = None
        self._validate_config()
        self._initialize()

        # Initialize services
        self.droplet_service = DropletService(self._client, self.config.credentials)
        self.database_service = DatabaseService(self._client, self.config.credentials)

    def _validate_config(self) -> None:
        """Validate DigitalOcean configuration"""
        if not self.config.credentials:
            # Try to get from environment
            token = os.getenv("DIGITALOCEAN_TOKEN")
            if not token:
                raise ProviderException(
                    "DigitalOcean token not found. Set DIGITALOCEAN_TOKEN environment variable "
                    "or provide credentials in config."
                )
            self.config.credentials = {"token": token}

        if not self.config.credentials or "token" not in self.config.credentials:
            raise ProviderException("DigitalOcean API token is required")

    def _initialize(self) -> None:
        """Initialize DigitalOcean client"""
        try:
            if not self.config.credentials:
                raise ProviderException("No credentials configured")
            token = self.config.credentials["token"]
            self._client = do_client.Manager(token=token)

            # Test connection
            self._client.get_account()
        except Exception as e:
            raise ProviderException(f"Failed to initialize DigitalOcean client: {e}")

    def create_resource(
        self, resource_type: str, config: Dict[str, Any], metadata: ResourceMetadata
    ) -> Dict[str, Any]:
        """Create a DigitalOcean resource"""
        if resource_type == "droplet":
            return self.droplet_service.create_droplet(config, metadata)
        elif resource_type == "managed_database":
            return self.database_service.create_database(config, metadata)
        else:
            raise ProviderException(f"Unsupported resource type: {resource_type}")

    def update_resource(
        self, resource_id: str, resource_type: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a DigitalOcean resource"""
        if resource_type == "droplet":
            return self.droplet_service.update_droplet(resource_id, updates)
        elif resource_type == "managed_database":
            return self.database_service.update_database(resource_id, updates)
        else:
            raise ProviderException(f"Unsupported resource type: {resource_type}")

    def delete_resource(self, resource_id: str, resource_type: str) -> None:
        """Delete a DigitalOcean resource"""
        if resource_type == "droplet":
            self.droplet_service.delete_droplet(resource_id)
        elif resource_type == "managed_database":
            self.database_service.delete_database(resource_id)
        else:
            raise ProviderException(f"Unsupported resource type: {resource_type}")

    def get_resource(
        self, resource_id: str, resource_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get a DigitalOcean resource by ID"""
        if resource_type == "droplet":
            return self.droplet_service.get_droplet(resource_id)
        elif resource_type == "managed_database":
            return self.database_service.get_database(resource_id)
        else:
            return None

    def list_resources(
        self, resource_type: str, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """List DigitalOcean resources"""
        resources = []

        if resource_type == "droplet" or resource_type == "*":
            resources.extend(self.droplet_service.list_droplets(query))

        if resource_type == "managed_database" or resource_type == "*":
            # Extract tags from query if provided
            tags = query.filters.get("tags") if query and query.filters else None
            resources.extend(self.database_service.list_databases(tags))

        return resources

    def tag_resource(
        self, resource_id: str, resource_type: str, tags: Dict[str, str]
    ) -> None:
        """Apply tags to a DigitalOcean resource"""
        if resource_type == "droplet":
            self.droplet_service.tag_service.tag_droplet(resource_id, tags)
        elif resource_type == "managed_database":
            # Database tagging is handled during update
            self.database_service.update_database(resource_id, {"tags": tags})
        else:
            raise ProviderException(f"Unsupported resource type: {resource_type}")

    async def update_resource_tags(self, resource_id: str, tags: Dict[str, str]) -> None:
        """
        Update resource tags for Pillar 1: Enhanced "Codify My Cloud" Import Tool.
        
        This method is specifically for instant tagging during import to mark
        resources as InfraDSL-managed without requiring 'infra apply'.
        """
        try:
            # Determine resource type by looking up the resource
            resource_type = await self._determine_resource_type(resource_id)
            
            if resource_type == "droplet":
                # Use DigitalOcean tagging API for droplets
                try:
                    # Convert tags to DigitalOcean tag format (list of strings)
                    do_tags = [f"{k}:{v}" for k, v in tags.items()]
                    
                    # Get the droplet to ensure it exists
                    droplet = self._client.get_droplet(resource_id)
                    if not droplet:
                        raise ProviderException(f"Droplet {resource_id} not found")
                    
                    # Apply tags to the droplet
                    for tag_string in do_tags:
                        # Create tag if it doesn't exist
                        tag_name = tag_string.replace(":", "-").replace(".", "-")
                        try:
                            self._client.create_tag(tag_name)
                        except Exception:
                            # Tag might already exist, that's fine
                            pass
                        
                        # Apply tag to droplet
                        self._client.tag_resource(tag_name, [droplet])
                    
                    logger.info(f"Successfully tagged droplet {resource_id} with {len(tags)} tags")
                    
                except Exception as e:
                    logger.error(f"Failed to tag droplet {resource_id}: {e}")
                    raise ProviderException(f"Failed to tag droplet: {e}")
                    
            elif resource_type == "managed_database":
                # Update database with tags
                try:
                    # For databases, tags are stored as metadata
                    update_data = {"tags": list(tags.keys())}  # DO databases use tag list
                    await self.database_service.update_database(resource_id, update_data)
                    logger.info(f"Successfully tagged database {resource_id} with {len(tags)} tags")
                    
                except Exception as e:
                    logger.error(f"Failed to tag database {resource_id}: {e}")
                    raise ProviderException(f"Failed to tag database: {e}")
                    
            else:
                logger.warning(f"Unknown resource type for {resource_id}, skipping tagging")
                
        except Exception as e:
            logger.error(f"Failed to update tags for resource {resource_id}: {e}")
            raise ProviderException(f"Tag update failed: {e}")

    async def _determine_resource_type(self, resource_id: str) -> str:
        """Determine the resource type for a given resource ID"""
        try:
            # Try droplet first (most common)
            try:
                droplet = self._client.get_droplet(resource_id)
                if droplet:
                    return "droplet"
            except Exception:
                pass
            
            # Try database
            try:
                database = self.database_service.get_database(resource_id)
                if database:
                    return "managed_database"
            except Exception:
                pass
            
            # Default to droplet if we can't determine
            logger.warning(f"Could not determine resource type for {resource_id}, defaulting to droplet")
            return "droplet"
            
        except Exception as e:
            logger.error(f"Error determining resource type for {resource_id}: {e}")
            return "droplet"

    def estimate_cost(
        self, resource_type: str, config: Dict[str, Any]
    ) -> Dict[str, float]:
        """Estimate cost for a DigitalOcean resource"""
        if resource_type == "droplet":
            return self.droplet_service.estimate_droplet_cost(config)
        elif resource_type == "managed_database":
            return self._estimate_database_cost(config)
        else:
            return {"hourly": 0.0, "monthly": 0.0}

    def validate_config(self, resource_type: str, config: Dict[str, Any]) -> List[str]:
        """Validate DigitalOcean resource configuration"""
        errors = []

        if resource_type == "droplet":
            if "name" not in config:
                errors.append("Droplet name is required")
            if "region" in config:
                regions = self.get_regions()
                if config["region"] not in regions:
                    errors.append(f"Invalid region: {config['region']}")
            if "size" in config:
                sizes = self.droplet_service.get_droplet_sizes()
                if config["size"] not in sizes:
                    errors.append(f"Invalid size: {config['size']}")

        elif resource_type == "managed_database":
            if "name" not in config:
                errors.append("Database name is required")
            if "engine" not in config:
                errors.append("Database engine is required")
            elif config["engine"] not in ["pg", "mysql", "redis", "mongodb"]:
                errors.append(f"Invalid database engine: {config['engine']}")
            if "region" in config:
                regions = self.get_regions()
                if config["region"] not in regions:
                    errors.append(f"Invalid region: {config['region']}")

        return errors

    def _estimate_database_cost(self, config: Dict[str, Any]) -> Dict[str, float]:
        """Estimate cost for a managed database"""
        # DigitalOcean database pricing (approximate)
        size_costs = {
            "db-s-1vcpu-1gb": {"hourly": 0.022, "monthly": 15.0},  # Basic
            "db-s-1vcpu-2gb": {"hourly": 0.037, "monthly": 25.0},  # Standard
            "db-s-2vcpu-4gb": {"hourly": 0.084, "monthly": 60.0},  # Performance
            "db-s-4vcpu-8gb": {"hourly": 0.169, "monthly": 120.0},  # Professional
            "db-s-6vcpu-16gb": {"hourly": 0.337, "monthly": 240.0},  # Premium
            "db-s-8vcpu-32gb": {"hourly": 0.675, "monthly": 480.0},  # High Performance
        }

        size = config.get("size", "db-s-1vcpu-2gb")
        costs = size_costs.get(size, {"hourly": 0.037, "monthly": 25.0})

        # Additional nodes increase cost
        num_nodes = config.get("num_nodes", 1)
        standby_nodes = config.get("standby_nodes", 0)
        total_nodes = num_nodes + standby_nodes

        return {
            "hourly": costs["hourly"] * total_nodes,
            "monthly": costs["monthly"] * total_nodes,
        }

    def get_resource_types(self) -> List[str]:
        """Get supported DigitalOcean resource types"""
        return ["droplet", "managed_database"]

    def get_regions(self) -> List[str]:
        """Get available DigitalOcean regions"""
        try:
            if not self._client:
                raise ProviderException("Client not initialized")

            regions = self._client.get_all_regions()
            return [region["slug"] for region in regions]
        except Exception:
            # Return common regions as fallback
            return ["nyc1", "nyc3", "ams3", "sgp1", "lon1", "fra1", "tor1", "sfo3"]

    def plan_create(
        self,
        resource_type: str,
        config: Dict[str, Any],
        metadata: ResourceMetadata,
    ) -> Dict[str, Any]:
        """Preview the creation of a DigitalOcean resource"""
        if resource_type == "droplet":
            return self.droplet_service.plan_create_droplet(config, metadata)
        elif resource_type == "managed_database":
            return self.database_service.plan_create_database(config, metadata)
        else:
            return {
                "resource_type": resource_type,
                "action": "create",
                "status": "unsupported",
                "message": f"Unsupported resource type: {resource_type}",
                "config": config,
            }

    def plan_update(
        self,
        resource_id: str,
        resource_type: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Preview the update of a DigitalOcean resource"""
        if resource_type == "droplet":
            return self.droplet_service.plan_update_droplet(resource_id, updates)
        elif resource_type == "managed_database":
            return self.database_service.plan_update_database(resource_id, updates)
        else:
            return {
                "resource_type": resource_type,
                "resource_id": resource_id,
                "action": "update",
                "status": "unsupported",
                "message": f"Unsupported resource type: {resource_type}",
                "updates": updates,
            }

    def plan_delete(
        self,
        resource_id: str,
        resource_type: str,
    ) -> Dict[str, Any]:
        """Preview the deletion of a DigitalOcean resource"""
        if resource_type == "droplet":
            return self.droplet_service.plan_delete_droplet(resource_id)
        elif resource_type == "managed_database":
            return self.database_service.plan_delete_database(resource_id)
        else:
            return {
                "resource_type": resource_type,
                "resource_id": resource_id,
                "action": "delete",
                "status": "unsupported",
                "message": f"Unsupported resource type: {resource_type}",
            }

    def discover_resources(
        self, resource_type: str, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """Discover DigitalOcean resources using broader discovery mechanisms"""
        # For now, this can be similar to list_resources but with enhanced discovery
        # In the future, this could include importing existing resources, scanning for unmanaged resources, etc.
        resources = []

        if resource_type == "droplet" or resource_type == "*":
            discovered_droplets = self.droplet_service.discover_droplets(query)
            resources.extend(discovered_droplets)

        if resource_type == "managed_database" or resource_type == "*":
            discovered_databases = self.database_service.discover_databases(query)
            resources.extend(discovered_databases)

        return resources
