"""
DigitalOcean Droplet Service
"""

import digitalocean as do_client
from typing import Dict, Any, Optional, List
from ....core.exceptions import ProviderException
from ....core.interfaces.provider import ResourceMetadata, ResourceQuery
from .ssh_key import SSHKeyService
from .tag import TagService
from .volume import VolumeService


class DropletService:
    """Handles droplet operations for DigitalOcean"""

    def __init__(self, client, credentials: Optional[Dict[str, Any]] = None):
        self._client = client
        self._credentials = credentials
        self.ssh_key_service = SSHKeyService(client, credentials)
        self.tag_service = TagService(credentials)
        self.volume_service = VolumeService(client, credentials)

    def create_droplet(
        self, config: Dict[str, Any], metadata: ResourceMetadata
    ) -> Dict[str, Any]:
        """Create a DigitalOcean Droplet"""
        try:
            if not self._credentials:
                raise ProviderException("No credentials configured")

            # Handle SSH key uploads if needed
            ssh_keys = config.get("ssh_keys", [])
            ssh_key_content = config.get("_ssh_key_content", {})

            processed_ssh_keys = self.ssh_key_service.process_ssh_keys(
                ssh_keys, ssh_key_content
            )

            # Extract droplet configuration
            # Convert tags - replace dots with underscores for DigitalOcean compatibility
            tags_dict = config.get("tags", {})
            tag_list = self.tag_service.convert_tags_to_digitalocean(tags_dict)

            droplet_config = {
                "name": config["name"],
                "region": config.get("region", "nyc1"),
                "size": config.get("size", "s-1vcpu-1gb"),
                "image": config.get("image", "ubuntu-22-04-x64"),
                "ssh_keys": processed_ssh_keys,
                "backups": config.get("backups", False),
                "ipv6": config.get("ipv6", True),
                "monitoring": config.get("monitoring", True),
                "tags": tag_list,
                "user_data": config.get("user_data"),
            }

            # Create droplet
            droplet = do_client.Droplet(
                token=self._credentials["token"], **droplet_config
            )
            droplet.create()

            # Wait for creation to complete
            droplet.load()

            return {
                "id": str(droplet.id),
                "name": droplet.name,
                "status": droplet.status,
                "ip_address": droplet.ip_address,
                "private_ip_address": droplet.private_ip_address,
                "region": getattr(droplet, "region", {}).get("slug", "unknown"),
                "size": getattr(droplet, "size", {}).get("slug", "unknown"),
                "image": getattr(droplet, "image", {}).get("slug", "unknown"),
                "created_at": droplet.created_at,
            }

        except Exception as e:
            raise ProviderException(f"Failed to create droplet: {e}")

    def update_droplet(
        self, droplet_id: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a DigitalOcean Droplet"""
        try:
            if not self._credentials:
                raise ProviderException("No credentials configured")

            droplet = do_client.Droplet(token=self._credentials["token"], id=droplet_id)
            droplet.load()

            # Apply updates
            if "name" in updates:
                # Handle name update - extract desired value from diff format
                name_update = updates["name"]
                if isinstance(name_update, dict) and "desired" in name_update:
                    droplet.rename(name_update["desired"])
                else:
                    droplet.rename(name_update)

            if "size" in updates:
                # Handle droplet resizing - requires stop -> resize -> start sequence
                size_update = updates["size"]
                desired_size = size_update
                if isinstance(size_update, dict) and "desired" in size_update:
                    desired_size = size_update["desired"]
                elif isinstance(size_update, str):
                    desired_size = size_update

                print(f"[DEBUG] Resizing droplet {droplet_id} to size: {desired_size}")

                # Check if droplet is running - if so, we need to stop it first
                was_running = droplet.status == "active"

                if was_running:
                    print(f"[DEBUG] Stopping droplet {droplet_id} for resize...")
                    droplet.shutdown()
                    # Wait for droplet to be powered off
                    self._wait_for_droplet_status(droplet, "off", timeout=120)

                print(f"[DEBUG] Performing resize to {desired_size}...")
                # Perform the resize operation (correct DigitalOcean SDK syntax)
                droplet.resize(
                    desired_size, disk=False
                )  # disk=False for CPU/RAM only resize

                # Wait for resize to complete
                self._wait_for_droplet_status(droplet, "off", timeout=300)

                if was_running:
                    print(f"[DEBUG] Starting droplet {droplet_id} after resize...")
                    droplet.power_on()
                    # Wait for droplet to be active again
                    self._wait_for_droplet_status(droplet, "active", timeout=120)

            if "additional_disks" in updates:
                # Handle additional disks (volumes) - requires stop -> create -> attach -> start sequence
                disks_update = updates["additional_disks"]
                if isinstance(disks_update, dict) and "desired" in disks_update:
                    desired_disks = disks_update["desired"]
                    current_disks = disks_update.get("current", [])

                    print(f"[DEBUG] Managing additional disks for droplet {droplet_id}")
                    print(f"[DEBUG] Current disks: {current_disks}")
                    print(f"[DEBUG] Desired disks: {desired_disks}")

                    # Check if droplet is running - if so, we need to stop it first
                    was_running = droplet.status == "active"

                    if was_running:
                        print(
                            f"[DEBUG] Stopping droplet {droplet_id} for disk operations..."
                        )
                        droplet.shutdown()
                        # Wait for droplet to be powered off
                        self._wait_for_droplet_status(droplet, "off", timeout=120)

                    # Create and attach new volumes
                    self.volume_service.manage_droplet_volumes(
                        droplet_id, current_disks, desired_disks
                    )

                    if was_running:
                        print(
                            f"[DEBUG] Starting droplet {droplet_id} after disk operations..."
                        )
                        droplet.power_on()
                        # Wait for droplet to be active again
                        self._wait_for_droplet_status(droplet, "active", timeout=120)

            if "tags" in updates:
                # Handle tag updates - extract desired tags from diff format
                tags_update = updates["tags"]
                print(f"[DEBUG] Raw tags_update: {tags_update}")
                if isinstance(tags_update, dict) and "desired" in tags_update:
                    desired_tags = tags_update["desired"]
                    print(f"[DEBUG] Desired tags list: {desired_tags}")

                    # Check if desired_tags is a dictionary or list
                    if isinstance(desired_tags, dict):
                        # Include ALL tags (management + user-defined) for consistency
                        tags_dict = {}
                        for key, value in desired_tags.items():
                            tags_dict[key] = value
                            print(f"[DEBUG] Including tag: {key}={value}")
                    else:
                        # Handle list format (legacy)
                        tags_dict = {}
                        for tag in desired_tags:
                            if ":" in tag:
                                key, value = tag.split(":", 1)
                                tags_dict[key] = value
                                print(
                                    f"[DEBUG] Split tag '{tag}' -> key='{key}', value='{value}'"
                                )
                            else:
                                tags_dict[tag] = tag
                                print(
                                    f"[DEBUG] No-split tag '{tag}' -> key='{tag}', value='{tag}'"
                                )

                    print(f"[DEBUG] Final tags_dict: {tags_dict}")
                    self.tag_service.tag_droplet(droplet_id, tags_dict)
                else:
                    self.tag_service.tag_droplet(droplet_id, tags_update)

            return {
                "id": str(droplet.id),
                "name": droplet.name,
                "status": droplet.status,
                "tags": droplet.tags,
            }

        except Exception as e:
            raise ProviderException(f"Failed to update droplet: {e}")

    def delete_droplet(self, droplet_id: str) -> None:
        """Delete a DigitalOcean Droplet"""
        try:
            if not self._credentials:
                raise ProviderException("No credentials configured")

            droplet = do_client.Droplet(token=self._credentials["token"], id=droplet_id)
            droplet.destroy()
        except Exception as e:
            raise ProviderException(f"Failed to delete droplet: {e}")

    def get_droplet(self, droplet_id: str) -> Optional[Dict[str, Any]]:
        """Get a DigitalOcean Droplet by ID"""
        try:
            if not self._credentials:
                raise ProviderException("No credentials configured")

            droplet = do_client.Droplet(token=self._credentials["token"], id=droplet_id)
            droplet.load()

            return {
                "id": str(droplet.id),
                "name": droplet.name,
                "status": droplet.status,
                "ip_address": droplet.ip_address,
                "private_ip_address": droplet.private_ip_address,
                "region": getattr(droplet, "region", {}).get("slug", "unknown"),
                "size": getattr(droplet, "size", {}).get("slug", "unknown"),
                "image": getattr(droplet, "image", {}).get("slug", "unknown"),
                "created_at": droplet.created_at,
                "tags": droplet.tags,
            }

        except Exception:
            return None

    def list_droplets(
        self, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """List DigitalOcean Droplets"""
        try:
            if not self._client:
                raise ProviderException("Client not initialized")

            droplets = self._client.get_all_droplets()

            # Apply filters if query provided
            if query and query.filters:
                filtered_droplets = []
                for droplet in droplets:
                    if self._matches_query(droplet, query):
                        filtered_droplets.append(droplet)
                droplets = filtered_droplets

            result_list = []
            for droplet in droplets:
                # Convert tags back - replace underscores with dots for infradsl tags
                converted_tags = self.tag_service.convert_tags_from_digitalocean(
                    droplet.tags
                )

                # Get attached volumes for LEGO principle support
                additional_disks = self.volume_service.get_droplet_volumes(droplet.id)

                result_list.append(
                    {
                        "id": str(droplet.id),
                        "name": droplet.name,
                        "status": droplet.status,
                        "ip_address": droplet.ip_address,
                        "private_ip_address": droplet.private_ip_address,
                        "region": getattr(droplet, "region", {}).get("slug", "unknown"),
                        "size": getattr(droplet, "size", {}).get("slug", "unknown"),
                        "image": getattr(droplet, "image", {}).get("slug", "unknown"),
                        "created_at": droplet.created_at,
                        "tags": converted_tags,
                        # Add missing fields for proper stateless comparison
                        "backups": getattr(droplet, "backups", False),
                        "ipv6": getattr(
                            droplet, "ipv6", True
                        ),  # Most droplets have IPv6 enabled by default
                        "monitoring": True,  # DigitalOcean droplets have monitoring enabled by default
                        "user_data": None,  # User data is not retrievable via API after creation
                        "additional_disks": additional_disks,  # Include attached volumes
                    }
                )

            return result_list

        except Exception as e:
            raise ProviderException(f"Failed to list droplets: {e}")

    def _matches_query(self, droplet: Any, query: ResourceQuery) -> bool:
        """Check if droplet matches query filters"""
        if "name" in query.filters and droplet.name != query.filters["name"]:
            return False
        if "tags" in query.filters:
            # Check if droplet has required tags
            required_tags = query.filters["tags"]
            droplet_tags = set(droplet.tags)
            for key, value in required_tags.items():
                if f"{key}:{value}" not in droplet_tags:
                    return False
        return True

    def _wait_for_droplet_status(
        self, droplet, target_status: str, timeout: int = 120
    ) -> None:
        """Wait for droplet to reach target status"""
        import time

        start_time = time.time()
        while time.time() - start_time < timeout:
            droplet.load()  # Refresh droplet state
            current_status = droplet.status
            print(
                f"[DEBUG] Waiting for droplet status: {current_status} -> {target_status}"
            )

            if current_status == target_status:
                print(f"[DEBUG] Droplet reached target status: {target_status}")
                return

            time.sleep(5)  # Wait 5 seconds before checking again

        raise ProviderException(
            f"Timeout waiting for droplet to reach status '{target_status}' (current: {droplet.status})"
        )

    def estimate_droplet_cost(self, config: Dict[str, Any]) -> Dict[str, float]:
        """Estimate cost for a DigitalOcean Droplet"""
        # DigitalOcean pricing (simplified)
        size_pricing = {
            "s-1vcpu-512mb-10gb": {"hourly": 0.00595, "monthly": 4.0},
            "s-1vcpu-1gb": {"hourly": 0.00893, "monthly": 6.0},
            "s-1vcpu-2gb": {"hourly": 0.01786, "monthly": 12.0},
            "s-2vcpu-4gb": {"hourly": 0.03571, "monthly": 24.0},
            "s-4vcpu-8gb": {"hourly": 0.07143, "monthly": 48.0},
            "s-8vcpu-16gb": {"hourly": 0.14286, "monthly": 96.0},
        }

        size = config.get("size", "s-1vcpu-1gb")
        pricing = size_pricing.get(size, size_pricing["s-1vcpu-1gb"])

        return {
            "hourly": pricing["hourly"],
            "monthly": pricing["monthly"],
        }

    def get_droplet_sizes(self) -> List[str]:
        """Get available DigitalOcean droplet sizes"""
        try:
            if not self._client:
                raise ProviderException("Client not initialized")

            sizes = self._client.get_all_sizes()
            return [size["slug"] for size in sizes]
        except Exception:
            # Return common sizes as fallback
            return [
                "s-1vcpu-512mb-10gb",
                "s-1vcpu-1gb",
                "s-1vcpu-2gb",
                "s-2vcpu-4gb",
                "s-4vcpu-8gb",
                "s-8vcpu-16gb",
            ]

    def plan_create_droplet(
        self, config: Dict[str, Any], metadata: ResourceMetadata
    ) -> Dict[str, Any]:
        """Preview the creation of a DigitalOcean droplet"""
        # Validate configuration first
        errors = self._validate_droplet_config(config)
        if errors:
            return {
                "resource_type": "droplet",
                "action": "create",
                "status": "error",
                "errors": errors,
                "config": config,
            }

        # Estimate cost
        cost = self.estimate_droplet_cost(config)

        # Build the preview plan
        return {
            "resource_type": "droplet",
            "action": "create",
            "status": "ready",
            "config": config,
            "metadata": metadata.to_dict(),
            "estimated_cost": cost,
            "changes": {
                "create": {
                    "name": config["name"],
                    "region": config.get("region", "nyc1"),
                    "size": config.get("size", "s-1vcpu-1gb"),
                    "image": config.get("image", "ubuntu-22-04-x64"),
                    "ssh_keys": config.get("ssh_keys", []),
                    "backups": config.get("backups", False),
                    "tags": config.get("tags", {}),
                }
            },
        }

    def plan_update_droplet(
        self, droplet_id: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Preview the update of a DigitalOcean droplet"""
        # Get current droplet state
        current_droplet = self.get_droplet(droplet_id)
        if not current_droplet:
            return {
                "resource_type": "droplet",
                "resource_id": droplet_id,
                "action": "update",
                "status": "error",
                "message": f"Droplet {droplet_id} not found",
            }

        # Analyze what changes would be made
        changes = {}
        if "name" in updates and updates["name"] != current_droplet.get("name"):
            changes["name"] = {
                "old": current_droplet.get("name"),
                "new": updates["name"],
            }

        if "tags" in updates:
            current_tags = current_droplet.get("tags", {})
            new_tags = updates["tags"]
            if current_tags != new_tags:
                changes["tags"] = {
                    "old": current_tags,
                    "new": new_tags,
                }

        # Note: DigitalOcean doesn't support changing size, region, or image after creation
        unsupported_changes = []
        for field in ["size", "region", "image"]:
            if field in updates:
                unsupported_changes.append(
                    f"Cannot change {field} after droplet creation"
                )

        return {
            "resource_type": "droplet",
            "resource_id": droplet_id,
            "action": "update",
            "status": "ready" if not unsupported_changes else "warning",
            "changes": changes,
            "warnings": unsupported_changes,
            "current_state": current_droplet,
            "updates": updates,
        }

    def plan_delete_droplet(self, droplet_id: str) -> Dict[str, Any]:
        """Preview the deletion of a DigitalOcean droplet"""
        # Get current droplet state
        current_droplet = self.get_droplet(droplet_id)
        if not current_droplet:
            return {
                "resource_type": "droplet",
                "resource_id": droplet_id,
                "action": "delete",
                "status": "error",
                "message": f"Droplet {droplet_id} not found",
            }

        # Check for attached volumes or other dependencies
        warnings = []
        if current_droplet.get("volume_ids"):
            warnings.append("Droplet has attached volumes that will be detached")

        return {
            "resource_type": "droplet",
            "resource_id": droplet_id,
            "action": "delete",
            "status": "ready",
            "current_state": current_droplet,
            "warnings": warnings,
            "impact": {
                "data_loss": "All data on the droplet will be permanently lost",
                "ip_address": "IP address will be released",
                "backups": (
                    "Existing backups will be retained"
                    if current_droplet.get("backups")
                    else "No backups to retain"
                ),
            },
        }

    def discover_droplets(
        self, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """Discover DigitalOcean droplets with enhanced metadata"""
        # For now, this is similar to list_droplets but could be enhanced with:
        # - Unmanaged resource detection
        # - Cost analysis
        # - Security scanning
        # - Compliance checking
        droplets = self.list_droplets(query)

        # Enhance each droplet with discovery metadata
        enhanced_droplets = []
        for droplet in droplets:
            enhanced_droplet = droplet.copy()
            enhanced_droplet["discovery_metadata"] = {
                "discovered_at": self._get_current_timestamp(),
                "managed_by_infradsl": self._is_managed_by_infradsl(droplet),
                "cost_analysis": self._analyze_droplet_cost(droplet),
            }
            enhanced_droplets.append(enhanced_droplet)

        return enhanced_droplets

    def _validate_droplet_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate droplet configuration"""
        errors = []

        if "name" not in config:
            errors.append("Droplet name is required")

        if "region" in config:
            # This would need to check against actual regions
            pass

        if "size" in config:
            # This would need to check against actual sizes
            pass

        return errors

    def _get_current_timestamp(self) -> str:
        """Get current timestamp for discovery metadata"""
        from datetime import datetime

        return datetime.utcnow().isoformat()

    def _is_managed_by_infradsl(self, droplet: Dict[str, Any]) -> bool:
        """Check if droplet is managed by InfraDSL"""
        tags = droplet.get("tags", {})
        return "infradsl.managed" in tags or "infradsl:managed" in tags

    def _analyze_droplet_cost(self, droplet: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cost for a droplet"""
        size = droplet.get("size", "s-1vcpu-1gb")
        config = {"size": size}
        return self.estimate_droplet_cost(config)
