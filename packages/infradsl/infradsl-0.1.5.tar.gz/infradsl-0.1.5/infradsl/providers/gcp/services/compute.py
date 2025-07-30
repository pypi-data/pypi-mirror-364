"""
GCP Compute Engine Service
"""

import time
import logging
from typing import Any, Dict, List, Optional

from .base import BaseGCPService
from ....core.interfaces.provider import ResourceQuery, ResourceMetadata
from ....core.exceptions import ProviderException

logger = logging.getLogger(__name__)


class ComputeService(BaseGCPService):
    """GCP Compute Engine service implementation"""
    
    def create_instance(self, config: Dict[str, Any], metadata: ResourceMetadata) -> Dict[str, Any]:
        """Create a GCP Compute Engine instance"""
        try:
            if not self._compute_client:
                raise ProviderException("GCP client not initialized")

            # Import Google Cloud libraries
            from google.cloud import compute_v1

            # Extract instance configuration
            instance_name = config.get("name")
            if not instance_name:
                raise ProviderException("Instance name is required")
            
            machine_type = config.get("machine_type", config.get("size", "e2-small"))
            zone = config.get("zone", f"{self.config.region}-a")
            image_family = config.get("image_family", config.get("image", "ubuntu-2204-lts"))
            image_project = config.get("image_project", "ubuntu-os-cloud")
            disk_size_gb = int(config.get("disk_size_gb", 20))

            # Handle SSH keys
            ssh_keys = config.get("ssh_keys", [])
            ssh_key_content = config.get("_ssh_key_content", {})
            metadata_items = []

            # Process SSH keys
            ssh_key_strings = []
            for key_name in ssh_keys:
                if key_name in ssh_key_content:
                    key_content = ssh_key_content[key_name]
                    username = config.get("admin_user", "ubuntu")
                    ssh_key_strings.append(f"{username}:{key_content}")

            if ssh_key_strings:
                ssh_item = compute_v1.Items(
                    key="ssh-keys", value="\n".join(ssh_key_strings)
                )
                metadata_items.append(ssh_item)

            # Add user data if provided
            if config.get("user_data"):
                user_data_item = compute_v1.Items(
                    key="user-data", value=config["user_data"]
                )
                metadata_items.append(user_data_item)

            # Convert InfraDSL tags to GCP labels
            tags = config.get("tags", [])
            if isinstance(tags, dict):
                labels = self._convert_tags_dict_to_labels(tags)
            else:
                labels = self._convert_tags_to_labels(tags)

            # Create instance configuration
            instance = compute_v1.Instance()
            instance.name = instance_name
            instance.machine_type = f"zones/{zone}/machineTypes/{machine_type}"

            # Boot disk
            boot_disk = compute_v1.AttachedDisk()
            boot_disk.auto_delete = True
            boot_disk.boot = True
            boot_disk.type_ = "PERSISTENT"

            initialize_params = compute_v1.AttachedDiskInitializeParams(
                source_image=f"projects/{image_project}/global/images/family/{image_family}",
                disk_size_gb=disk_size_gb,
                disk_type=f"zones/{zone}/diskTypes/pd-standard",
            )
            boot_disk.initialize_params = initialize_params
            instance.disks = [boot_disk]

            # Network interface (default)
            network_interface = compute_v1.NetworkInterface()
            network_interface.name = "default"

            # Add external IP if requested
            if config.get("public_ip", True):
                access_config = compute_v1.AccessConfig()
                access_config.name = "External NAT"
                access_config.type_ = "ONE_TO_ONE_NAT"
                network_interface.access_configs = [access_config]

            instance.network_interfaces = [network_interface]

            # Add labels
            if labels:
                instance.labels = labels

            # Add metadata
            if metadata_items:
                instance.metadata = compute_v1.Metadata(items=metadata_items)

            # Create the instance
            operation = self._compute_client.insert(
                project=self._project_id, zone=zone, instance_resource=instance
            )

            # Wait for operation to complete
            self._wait_for_operation(operation, zone)

            # Get the created instance
            created_instance = self._compute_client.get(
                project=self._project_id, zone=zone, instance=instance_name
            )

            # Convert to standardized format
            return self._instance_to_dict(created_instance, zone)

        except Exception as e:
            raise ProviderException(f"Failed to create instance {config.get('name')}: {e}")

    def update_instance(self, resource_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a GCP Compute Engine instance"""
        logger.info(f"Updating GCP instance {resource_id} with updates: {updates}")
        try:
            # Parse instance ID - handle both full GCP path and simple formats
            if "/" in resource_id:
                parts = resource_id.split("/")
                if len(parts) == 6 and parts[0] == "projects" and parts[2] == "zones" and parts[4] == "instances":
                    # Full format: projects/PROJECT/zones/ZONE/instances/NAME
                    zone = parts[3]  # zone name
                    instance_name = parts[5]  # instance name
                elif len(parts) == 2:
                    # Simple format: zone/instance_name
                    zone, instance_name = parts
                else:
                    # Fallback: assume last part is instance name, use default zone
                    zone = f"{self.config.region}-a"
                    instance_name = parts[-1]
            else:
                zone = f"{self.config.region}-a"
                instance_name = resource_id

            # Handle machine type changes (requires stop/start)
            if "size" in updates:
                # Handle both direct value and diff format
                size_value = updates["size"]
                if isinstance(size_value, dict) and "desired" in size_value:
                    # Diff format: {"current": "e2-medium", "desired": "e2-small"}
                    size_value = size_value["desired"]
                self._resize_instance(instance_name, zone, size_value)

            # Handle label updates
            if "tags" in updates:
                # Handle both direct value and diff format
                tags_value = updates["tags"]
                if isinstance(tags_value, dict) and "desired" in tags_value:
                    # Diff format: {"current": [...], "desired": [...]}
                    tags_value = {"desired": tags_value["desired"]}
                elif isinstance(tags_value, list):
                    # Direct list format - convert to expected format
                    tags_value = {"desired": tags_value}
                self._update_instance_labels(instance_name, zone, tags_value)

            # Get updated instance
            if not self._compute_client:
                raise ProviderException("GCP client not initialized")
            
            updated_instance = self._compute_client.get(
                project=self._project_id, zone=zone, instance=instance_name
            )

            return self._instance_to_dict(updated_instance, zone)

        except Exception as e:
            raise ProviderException(f"Failed to update instance {resource_id}: {e}")

    def delete_instance(self, resource_id: str) -> None:
        """Delete a GCP Compute Engine instance"""
        try:
            # Parse instance ID - handle both full GCP path and simple formats
            if "/" in resource_id:
                parts = resource_id.split("/")
                if len(parts) == 6 and parts[0] == "projects" and parts[2] == "zones" and parts[4] == "instances":
                    # Full format: projects/PROJECT/zones/ZONE/instances/NAME
                    zone = parts[3]  # zone name
                    instance_name = parts[5]  # instance name
                elif len(parts) == 2:
                    # Simple format: zone/instance_name
                    zone, instance_name = parts
                else:
                    # Fallback: assume last part is instance name, use default zone
                    zone = f"{self.config.region}-a"
                    instance_name = parts[-1]
            else:
                zone = f"{self.config.region}-a"
                instance_name = resource_id

            if not self._compute_client:
                raise ProviderException("GCP client not initialized")
            
            operation = self._compute_client.delete(
                project=self._project_id, zone=zone, instance=instance_name
            )

            # Wait for deletion to complete
            self._wait_for_operation(operation, zone)

        except Exception as e:
            raise ProviderException(f"Failed to delete instance {resource_id}: {e}")

    def get_instance(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get a GCP Compute Engine instance by ID"""
        try:
            # Parse instance ID - handle both full GCP path and simple formats
            if "/" in resource_id:
                parts = resource_id.split("/")
                if len(parts) == 6 and parts[0] == "projects" and parts[2] == "zones" and parts[4] == "instances":
                    # Full format: projects/PROJECT/zones/ZONE/instances/NAME
                    zone = parts[3]  # zone name
                    instance_name = parts[5]  # instance name
                elif len(parts) == 2:
                    # Simple format: zone/instance_name
                    zone, instance_name = parts
                else:
                    # Fallback: assume last part is instance name, use default zone
                    zone = f"{self.config.region}-a"
                    instance_name = parts[-1]
            else:
                zone = f"{self.config.region}-a"
                instance_name = resource_id

            if not self._compute_client:
                return None
            
            instance = self._compute_client.get(
                project=self._project_id, zone=zone, instance=instance_name
            )

            return self._instance_to_dict(instance, zone)

        except Exception:
            return None

    def list_instances(self, query: Optional[ResourceQuery] = None) -> List[Dict[str, Any]]:
        """List GCP Compute Engine instances"""
        try:
            from google.cloud import compute_v1

            instances = []

            # If no compute client is available, return empty list for preview mode
            if not self._compute_client:
                return []

            zones_client = compute_v1.ZonesClient()

            # List instances from all zones in the region
            zones = zones_client.list(project=self._project_id)
            for zone in zones:
                region = getattr(self.config.region, 'value', self.config.region) or "us-central1"
                if zone.name.startswith(region):
                    try:
                        zone_instances = self._compute_client.list(
                            project=self._project_id, zone=zone.name
                        )

                        for instance in zone_instances:
                            instance_dict = self._instance_to_dict(instance, zone.name)

                            # Apply query filters if provided
                            if query and not self._matches_query(instance_dict, query):
                                continue

                            instances.append(instance_dict)

                    except Exception as e:
                        logger.debug(f"Error listing instances in zone {zone.name}: {e}")
                        continue

            return instances

        except Exception as e:
            raise ProviderException(f"Failed to list instances: {e}")

    def tag_instance(self, resource_id: str, tags: Dict[str, str]) -> None:
        """Apply labels to a GCP Compute Engine instance"""
        try:
            # Parse instance ID
            if "/" in resource_id:
                zone, instance_name = resource_id.split("/", 1)
            else:
                zone = f"{self.config.region}-a"
                instance_name = resource_id

            # Convert tags to GCP labels format
            labels = self._convert_tags_dict_to_labels(tags)

            # Get current instance to get label fingerprint
            if not self._compute_client:
                raise ProviderException("GCP client not initialized")
            
            instance = self._compute_client.get(
                project=self._project_id, zone=zone, instance=instance_name
            )

            # Update labels
            from google.cloud import compute_v1

            request = compute_v1.InstancesSetLabelsRequest(
                labels=labels,
                label_fingerprint=instance.label_fingerprint,
            )
            self._compute_client.set_labels(
                project=self._project_id,
                zone=zone,
                instance=instance_name,
                instances_set_labels_request_resource=request,
            )

        except Exception as e:
            raise ProviderException(f"Failed to tag instance {resource_id}: {e}")

    def get_regions(self) -> List[str]:
        """Get list of available GCP regions"""
        try:
            from google.cloud import compute_v1

            regions_client = compute_v1.RegionsClient()
            regions = regions_client.list(project=self._project_id)

            return [region.name for region in regions]

        except Exception:
            # Return common regions as fallback
            return [
                "us-central1",
                "us-east1",
                "us-west1",
                "us-west2",
                "europe-west1",
                "europe-west2",
                "asia-east1",
                "asia-southeast1",
            ]

    def _wait_for_operation(self, operation, zone: str, timeout: int = 300) -> None:
        """Wait for a GCP operation to complete"""
        from google.cloud import compute_v1

        zone_operations_client = compute_v1.ZoneOperationsClient()

        start_time = time.time()
        while time.time() - start_time < timeout:
            result = zone_operations_client.get(
                project=self._project_id, zone=zone, operation=operation.name
            )

            if result.status == compute_v1.Operation.Status.DONE:
                if result.error:
                    raise ProviderException(f"Operation failed: {result.error}")
                return

            time.sleep(2)

        raise ProviderException(f"Operation timed out after {timeout} seconds")

    def _instance_to_dict(self, instance, zone: str) -> Dict[str, Any]:
        """Convert GCP instance to standardized dictionary"""
        # Extract IP addresses
        public_ip = None
        private_ip = None

        for interface in instance.network_interfaces:
            if interface.network_i_p:
                private_ip = interface.network_i_p
            for access_config in interface.access_configs:
                if access_config.nat_i_p:
                    public_ip = access_config.nat_i_p

        # Convert labels to InfraDSL tag format
        tags = []
        if instance.labels:
            for key, value in instance.labels.items():
                if key.startswith("infradsl_"):
                    original_key = key.replace("_", ".")
                    tags.append(f"{original_key}:{value}")
                else:
                    tags.append(f"{key}:{value}")

        return {
            "id": f"{zone}/{instance.name}",
            "name": instance.name,
            "status": instance.status,
            "machine_type": instance.machine_type.split("/")[-1] if instance.machine_type else None,
            "zone": zone,
            "region": zone.rsplit("-", 1)[0],
            "ip_address": public_ip,
            "private_ip_address": private_ip,
            "tags": tags,
            "labels": dict(instance.labels) if instance.labels else {},
            "created_at": instance.creation_timestamp,
            "size": instance.machine_type.split("/")[-1] if instance.machine_type else None,
            "image": self._extract_image_family(instance),
            "backups": False,
            "ipv6": False,
            "monitoring": True,
            "type": "instance",
            "provider": "gcp",
            "state": "active" if instance.status == "RUNNING" else "pending",
        }

    def _convert_tags_to_labels(self, tags: List[str]) -> Dict[str, str]:
        """Convert InfraDSL tags to GCP labels"""
        labels = {}

        for tag in tags:
            if ":" in tag:
                key, value = tag.split(":", 1)
                gcp_key = key.replace(".", "_").lower()
                gcp_value = value.lower().replace(" ", "_")
                labels[gcp_key] = gcp_value
            else:
                gcp_key = tag.replace(".", "_").lower()
                labels[gcp_key] = "true"

        return labels

    def _convert_tags_dict_to_labels(self, tags: Dict[str, str]) -> Dict[str, str]:
        """Convert InfraDSL tags dict to GCP labels"""
        labels = {}

        for key, value in tags.items():
            gcp_key = key.replace(".", "_").lower()
            gcp_value = str(value).lower().replace(" ", "_")
            labels[gcp_key] = gcp_value

        return labels

    def _extract_image_family(self, instance) -> Optional[str]:
        """Extract image family from GCP instance boot disk"""
        try:
            from google.cloud import compute_v1

            for disk in instance.disks:
                if disk.boot:
                    if disk.source:
                        try:
                            parts = disk.source.split("/")
                            if len(parts) >= 2:
                                disk_name = parts[-1]
                                zone = parts[-3] if len(parts) >= 3 else None

                                if zone and self._project_id:
                                    disks_client = compute_v1.DisksClient()
                                    disk_resource = disks_client.get(
                                        project=self._project_id,
                                        zone=zone,
                                        disk=disk_name,
                                    )

                                    if hasattr(disk_resource, "source_image") and disk_resource.source_image:
                                        source_image = disk_resource.source_image
                                        parts = source_image.split("/")
                                        if "images" in parts:
                                            image_idx = parts.index("images")
                                            if image_idx + 1 < len(parts):
                                                image_name = parts[image_idx + 1]
                                                # Try to extract family from image name
                                                if "ubuntu-2204" in image_name:
                                                    return "ubuntu-2204-lts"
                                                elif "ubuntu-2004" in image_name:
                                                    return "ubuntu-2004-lts"
                                                elif "debian-12" in image_name:
                                                    return "debian-12"
                                                elif "centos" in image_name:
                                                    return "centos-7"
                                                else:
                                                    return image_name.split("-v")[0] if "-v" in image_name else image_name
                        except Exception as e:
                            logger.debug(f"Error extracting image from disk resource: {e}")

                    # Fallback: check initialize_params
                    if hasattr(disk, "initialize_params") and disk.initialize_params:
                        if hasattr(disk.initialize_params, "source_image") and disk.initialize_params.source_image:
                            source_image = disk.initialize_params.source_image
                            parts = source_image.split("/")
                            if "family" in parts:
                                family_idx = parts.index("family")
                                if family_idx + 1 < len(parts):
                                    return parts[family_idx + 1]
                    break
        except Exception as e:
            logger.debug(f"Error in _extract_image_family: {e}")
        return None

    def _matches_query(self, instance: Dict[str, Any], query: ResourceQuery) -> bool:
        """Check if instance matches query filters"""
        filters = query.filters

        if "name" in filters and instance.get("name") != filters["name"]:
            return False

        if "id" in filters and instance.get("id") != filters["id"]:
            return False

        return True

    def _resize_instance(self, instance_name: str, zone: str, new_machine_type: str) -> None:
        """Resize a GCP Compute Engine instance"""
        logger.info(f"Resizing instance {instance_name} in zone {zone} to {new_machine_type}")
        if not self._compute_client:
            raise ProviderException("GCP client not initialized")

        try:
            # Stop the instance
            logger.info(f"Stopping instance {instance_name}...")
            stop_operation = self._compute_client.stop(
                project=self._project_id, zone=zone, instance=instance_name
            )
            logger.info(f"Stop operation initiated: {stop_operation.name if hasattr(stop_operation, 'name') else 'OK'}")

            # Wait for it to stop
            self._wait_for_instance_status(instance_name, zone, "TERMINATED")
            logger.info(f"Instance {instance_name} stopped successfully")

            # Change machine type
            from google.cloud import compute_v1

            logger.info(f"Changing machine type to {new_machine_type}...")
            request = compute_v1.InstancesSetMachineTypeRequest(
                machine_type=f"zones/{zone}/machineTypes/{new_machine_type}"
            )
            resize_operation = self._compute_client.set_machine_type(
                project=self._project_id,
                zone=zone,
                instance=instance_name,
                instances_set_machine_type_request_resource=request,
            )
            logger.info(f"Resize operation completed: {resize_operation.name if hasattr(resize_operation, 'name') else 'OK'}")

            # Start the instance
            logger.info(f"Starting instance {instance_name}...")
            start_operation = self._compute_client.start(
                project=self._project_id, zone=zone, instance=instance_name
            )
            logger.info(f"Start operation initiated: {start_operation.name if hasattr(start_operation, 'name') else 'OK'}")

            # Wait for it to start with a shorter timeout to avoid command timeout
            try:
                self._wait_for_instance_status(instance_name, zone, "RUNNING", timeout=60)
                logger.info(f"Instance {instance_name} started successfully")
            except ProviderException as e:
                logger.warning(f"Instance may still be starting: {e}")
                logger.info("The instance start operation was initiated but may take more time to complete")
                
        except Exception as e:
            logger.error(f"Error during resize operation: {e}")
            # Try to ensure the instance is started even if there was an error
            logger.info(f"Attempting to start instance {instance_name} after error...")
            try:
                self._compute_client.start(
                    project=self._project_id, zone=zone, instance=instance_name
                )
                logger.info("Start operation initiated after error")
            except Exception as start_error:
                logger.error(f"Failed to start instance after resize error: {start_error}")
            raise

    def _update_instance_labels(self, instance_name: str, zone: str, tags_update: Dict[str, Any]) -> None:
        """Update instance labels"""
        if "desired" in tags_update:
            desired_tags = tags_update["desired"]
            labels = self._convert_tags_dict_to_labels(desired_tags)

            # Get current instance to get label fingerprint
            if not self._compute_client:
                raise ProviderException("GCP client not initialized")
            
            instance = self._compute_client.get(
                project=self._project_id, zone=zone, instance=instance_name
            )

            # Set labels
            from google.cloud import compute_v1

            request = compute_v1.InstancesSetLabelsRequest(
                labels=labels,
                label_fingerprint=instance.label_fingerprint,
            )
            self._compute_client.set_labels(
                project=self._project_id,
                zone=zone,
                instance=instance_name,
                instances_set_labels_request_resource=request,
            )

    def _wait_for_instance_status(self, instance_name: str, zone: str, target_status: str, timeout: int = 120) -> None:
        """Wait for instance to reach target status"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self._compute_client:
                raise ProviderException("GCP client not initialized")
            
            instance = self._compute_client.get(
                project=self._project_id, zone=zone, instance=instance_name
            )

            if instance.status == target_status:
                return

            time.sleep(5)

        raise ProviderException(
            f"Instance {instance_name} did not reach {target_status} within {timeout} seconds"
        )

    def estimate_cost(self, config: Dict[str, Any]) -> Dict[str, float]:
        """Estimate cost for GCP Compute Engine instance"""
        machine_type = config.get("size", "e2-micro")

        # Basic cost estimates (USD per hour)
        pricing = {
            "e2-micro": 0.008,
            "e2-small": 0.016,
            "e2-medium": 0.033,
            "e2-standard-2": 0.067,
            "e2-standard-4": 0.134,
            "e2-standard-8": 0.268,
        }

        hourly_cost = pricing.get(machine_type, 0.05)
        monthly_cost = hourly_cost * 24 * 30

        return {"hourly": hourly_cost, "monthly": monthly_cost}

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate GCP Compute resource configuration"""
        errors = []

        if not config.get("name"):
            errors.append("Instance name is required")

        machine_type = config.get("size")
        if machine_type and not machine_type.startswith(("e2-", "n1-", "n2-", "c2-", "m1-")):
            errors.append(f"Invalid machine type: {machine_type}")

        return errors

    def preview_create(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Preview GCP instance creation"""
        return {
            "instance_name": config.get("name"),
            "machine_type": config.get("machine_type", config.get("size", "e2-small")),
            "zone": config.get("zone", f"{self.config.region}-a"),
            "image_family": config.get("image_family", config.get("image", "ubuntu-2204-lts")),
            "disk_size_gb": config.get("disk_size_gb", 20),
            "public_ip": config.get("public_ip", True),
            "ssh_keys": len(config.get("ssh_keys", [])),
        }

    def preview_update(self, resource_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Preview GCP instance update"""
        warnings = []
        if "size" in updates:
            warnings = [
                "Changing machine type requires the instance to be stopped",
                "This will cause downtime during the resize operation",
            ]

        return {
            "instance_id": resource_id,
            "changes": list(updates.keys()),
            "requires_restart": "size" in updates,
            "warnings": warnings,
        }

    def get_delete_warnings(self) -> List[str]:
        """Get warnings for GCP instance deletion"""
        return [
            "Instance and all attached disks will be permanently deleted",
            "This action cannot be undone",
            "All data on the instance will be lost",
        ]