"""
Google Cloud Platform Compute Engine Provider Implementation
"""

import os
import time
from typing import Any, Dict, List, Optional
from ..core.interfaces.provider import (
    ProviderInterface,
    ProviderType,
    ProviderConfig,
    ResourceMetadata,
    ResourceQuery,
)
from ..core.exceptions import ProviderException


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
        # Real operations will fail later with specific credential errors
        try:
            # Check for Google Cloud libraries first
            import google.auth
            import google.cloud.compute_v1
        except ImportError:
            raise ProviderException(
                "Google Cloud SDK not installed. Run: pip install google-cloud-compute google-auth"
            )

        # Try to set up credentials if available
        if not self.config.credentials:
            # Try to get from environment variables
            service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if service_account_path:
                if os.path.exists(service_account_path):
                    self.config.credentials = {
                        "service_account_path": service_account_path
                    }
                else:
                    print(
                        f"[WARNING] Service account file not found at: {service_account_path}"
                    )
            # Don't fail here - let the actual operations handle credential errors

    def _initialize(self) -> None:
        """Initialize GCP Compute Engine client"""
        try:
            # Import Google Cloud libraries (they should be available after validation)
            from google.cloud import compute_v1
            from google.auth import default

            # Try to initialize credentials
            credentials = None
            if (
                self.config.credentials
                and "service_account_path" in self.config.credentials
            ):
                try:
                    from google.auth.service_account import Credentials  # type: ignore
                    import json

                    service_account_path = self.config.credentials[
                        "service_account_path"
                    ]
                    print(
                        f"[DEBUG] Loading service account from: {service_account_path}"
                    )

                    with open(service_account_path) as f:
                        credentials_info = json.load(f)
                    credentials = Credentials.from_service_account_info(
                        credentials_info
                    )
                    # Service account credentials loaded successfully
                except ImportError:
                    # google.auth.service_account not available, fall back to default auth
                    # Using default authentication
                    credentials = None  # Will be handled by default auth below
                except Exception as e:
                    # For preview operations, we can continue without credentials
                    # Could not load service account credentials
                    credentials = None

            if credentials is None:
                try:
                    # Use default credentials (ADC)
                    credentials, project = default()
                    if not self.config.project:
                        self.config.project = project
                except Exception:
                    # For preview operations, we can continue without credentials
                    print(
                        "[DEBUG] No credentials available - operations requiring cloud access will fail"
                    )
                    credentials = None

            # Initialize compute client (even without credentials for preview operations)
            if credentials:
                self._compute_client = compute_v1.InstancesClient(
                    credentials=credentials
                )
                # Test connection only if we have credentials
                try:
                    zones_client = compute_v1.ZonesClient(credentials=credentials)
                    # Just create the request, don't actually execute it
                    request = compute_v1.ListZonesRequest(project=self.config.project)
                    # This is enough to validate the client setup
                except Exception as e:
                    print(f"[DEBUG] Could not test GCP connection: {e}")
            else:
                # No credentials available - client will be None
                self._compute_client = None

            self._project_id = self.config.project

        except Exception as e:
            raise ProviderException(f"Failed to initialize GCP Compute client: {e}")

    def create_resource(
        self, resource_type: str, config: Dict[str, Any], metadata: ResourceMetadata
    ) -> Dict[str, Any]:
        """Create a GCP Compute resource"""
        if resource_type == "instance":
            return self._create_instance(config, metadata)
        else:
            raise ProviderException(f"Unsupported resource type: {resource_type}")

    def _create_instance(
        self, config: Dict[str, Any], metadata: ResourceMetadata
    ) -> Dict[str, Any]:
        """Create a GCP Compute Engine instance"""
        try:
            if not self._compute_client:
                raise ProviderException("GCP client not initialized")

            # Import Google Cloud libraries
            from google.cloud import compute_v1  # type: ignore

            # Extract instance configuration
            instance_name = config.get("name")
            if not instance_name:
                raise ProviderException("Instance name is required")
            assert isinstance(instance_name, str)  # Type narrowing
            machine_type = config.get(
                "machine_type", config.get("size", "e2-small")
            )  # Use machine_type or fallback to size
            zone = config.get("zone", f"{self.config.region}-a")  # Default zone
            image_family = config.get(
                "image_family", config.get("image", "ubuntu-2204-lts")
            )
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
                    # GCP format: "username:ssh-rsa KEY user@host"
                    # Extract username from key or use default
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

            # Define the instance
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
            raise ProviderException(
                f"Failed to create instance {config.get('name')}: {e}"
            )

    def update_resource(
        self, resource_id: str, resource_type: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a GCP Compute resource"""
        if resource_type == "instance":
            return self._update_instance(resource_id, updates)
        else:
            raise ProviderException(f"Unsupported resource type: {resource_type}")

    def _update_instance(
        self, instance_id: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a GCP Compute Engine instance"""
        try:
            # Parse instance ID (format: "projects/PROJECT/zones/ZONE/instances/NAME")
            parts = instance_id.split("/")
            if len(parts) != 6 or parts[0] != "projects":
                # Try simpler format: zone/instance_name
                if "/" in instance_id:
                    zone, instance_name = instance_id.split("/", 1)
                else:
                    # Assume default zone and instance_id is just the name
                    zone = f"{self.config.region}-a"
                    instance_name = instance_id
            else:
                zone = parts[3]
                instance_name = parts[5]

            print(f"[DEBUG] Updating instance {instance_name} in zone {zone}")

            # Handle machine type changes (requires stop/start)
            if "size" in updates:
                self._resize_instance(instance_name, zone, updates["size"])

            # Handle label updates
            if "tags" in updates:
                self._update_instance_labels(instance_name, zone, updates["tags"])

            # Get updated instance
            if not self._compute_client:
                raise ProviderException("GCP client not initialized")
            assert self._compute_client is not None  # Type narrowing
            updated_instance = self._compute_client.get(
                project=self._project_id, zone=zone, instance=instance_name
            )

            return self._instance_to_dict(updated_instance, zone)

        except Exception as e:
            raise ProviderException(f"Failed to update instance {instance_id}: {e}")

    def delete_resource(self, resource_id: str, resource_type: str) -> None:
        """Delete a GCP Compute resource"""
        if resource_type == "instance":
            self._delete_instance(resource_id)
        else:
            raise ProviderException(f"Unsupported resource type: {resource_type}")

    def _delete_instance(self, instance_id: str) -> None:
        """Delete a GCP Compute Engine instance"""
        try:
            # Parse instance ID
            if "/" in instance_id:
                zone, instance_name = instance_id.split("/", 1)
            else:
                zone = f"{self.config.region}-a"
                instance_name = instance_id

            if not self._compute_client:
                raise ProviderException("GCP client not initialized")
            assert self._compute_client is not None  # Type narrowing
            operation = self._compute_client.delete(
                project=self._project_id, zone=zone, instance=instance_name
            )

            # Wait for deletion to complete
            self._wait_for_operation(operation, zone)

        except Exception as e:
            raise ProviderException(f"Failed to delete instance {instance_id}: {e}")

    def get_resource(
        self, resource_id: str, resource_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get a single GCP Compute resource by ID"""
        if resource_type == "instance":
            return self._get_instance(resource_id)
        else:
            raise ProviderException(f"Unsupported resource type: {resource_type}")

    def _get_instance(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get a GCP Compute Engine instance by ID"""
        try:
            # Parse instance ID
            if "/" in instance_id:
                zone, instance_name = instance_id.split("/", 1)
            else:
                zone = f"{self.config.region}-a"
                instance_name = instance_id

            if not self._compute_client:
                return None
            assert self._compute_client is not None  # Type narrowing
            instance = self._compute_client.get(
                project=self._project_id, zone=zone, instance=instance_name
            )

            return self._instance_to_dict(instance, zone)

        except Exception:
            return None

    def list_resources(
        self, resource_type: str, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """List GCP Compute resources"""
        if resource_type == "instance":
            return self._list_instances(query)
        else:
            raise ProviderException(f"Unsupported resource type: {resource_type}")

    def _list_instances(
        self, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """List GCP Compute Engine instances"""
        try:
            from google.cloud import compute_v1

            instances = []

            # If no compute client is available, try using gcloud CLI as fallback
            if not self._compute_client:
                return self._list_instances_via_gcloud()

            zones_client = compute_v1.ZonesClient()

            # List instances from all zones in the region
            zones = zones_client.list(project=self._project_id)
            for zone in zones:
                region = getattr(self.config.region, 'value', self.config.region) or "us-central1"  # Default region
                if zone.name.startswith(region):
                    try:
                        if not self._compute_client:
                            continue
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
                        print(
                            f"[DEBUG] Error listing instances in zone {zone.name}: {e}"
                        )
                        continue

            return instances

        except Exception as e:
            raise ProviderException(f"Failed to list instances: {e}")

    def tag_resource(
        self, resource_id: str, resource_type: str, tags: Dict[str, str]
    ) -> None:
        """Apply labels to a GCP Compute resource"""
        if resource_type == "instance":
            self._tag_instance(resource_id, tags)
        else:
            raise ProviderException(f"Unsupported resource type: {resource_type}")

    def _tag_instance(self, instance_id: str, tags: Dict[str, str]) -> None:
        """Apply labels to a GCP Compute Engine instance"""
        try:
            # Parse instance ID
            if "/" in instance_id:
                zone, instance_name = instance_id.split("/", 1)
            else:
                zone = f"{self.config.region}-a"
                instance_name = instance_id

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
            raise ProviderException(f"Failed to tag instance {instance_id}: {e}")

    def estimate_cost(
        self, resource_type: str, config: Dict[str, Any]
    ) -> Dict[str, float]:
        """Estimate cost for GCP Compute resources"""
        if resource_type == "instance":
            return self._estimate_instance_cost(config)
        else:
            return {"hourly": 0.0, "monthly": 0.0}

    def _estimate_instance_cost(self, config: Dict[str, Any]) -> Dict[str, float]:
        """Estimate cost for GCP Compute Engine instance"""
        # Simplified cost estimation (you'd want actual GCP pricing API)
        machine_type = config.get("size", "e2-micro")

        # Basic cost estimates (USD per hour) - these are examples
        pricing = {
            "e2-micro": 0.008,
            "e2-small": 0.016,
            "e2-medium": 0.033,
            "e2-standard-2": 0.067,
            "e2-standard-4": 0.134,
            "e2-standard-8": 0.268,
        }

        hourly_cost = pricing.get(machine_type, 0.05)  # Default estimate
        monthly_cost = hourly_cost * 24 * 30  # Approximate monthly

        return {"hourly": hourly_cost, "monthly": monthly_cost}

    def validate_config(self, resource_type: str, config: Dict[str, Any]) -> List[str]:
        """Validate GCP Compute resource configuration"""
        errors = []

        if resource_type == "instance":
            if not config.get("name"):
                errors.append("Instance name is required")

            machine_type = config.get("size")
            if machine_type and not machine_type.startswith(
                ("e2-", "n1-", "n2-", "c2-", "m1-")
            ):
                errors.append(f"Invalid machine type: {machine_type}")

        return errors

    def get_resource_types(self) -> List[str]:
        """Get list of supported resource types"""
        return ["instance"]

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

    # Helper methods

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
                # Convert back from GCP label format to InfraDSL tag format
                # Convert underscores back to dots for infradsl keys
                if key.startswith("infradsl_"):
                    original_key = key.replace("_", ".")
                    tags.append(f"{original_key}:{value}")
                else:
                    # For user-defined labels, add as key:value format
                    tags.append(f"{key}:{value}")

        return {
            "id": f"{zone}/{instance.name}",  # GCP instances are zone-specific
            "name": instance.name,
            "status": instance.status,
            "machine_type": (
                instance.machine_type.split("/")[-1] if instance.machine_type else None
            ),
            "zone": zone,
            "region": zone.rsplit("-", 1)[0],  # Extract region from zone
            "ip_address": public_ip,
            "private_ip_address": private_ip,
            "tags": tags,
            "labels": dict(instance.labels) if instance.labels else {},
            "created_at": instance.creation_timestamp,
            "size": (
                instance.machine_type.split("/")[-1] if instance.machine_type else None
            ),
            "image": self._extract_image_family(instance),
            "backups": False,  # GCP doesn't have this concept for instances
            "ipv6": False,  # Simplified
            "monitoring": True,  # GCP monitoring is usually enabled by default
        }

    def _convert_tags_to_labels(self, tags: List[str]) -> Dict[str, str]:
        """Convert InfraDSL tags to GCP labels"""
        labels = {}

        for tag in tags:
            if ":" in tag:
                key, value = tag.split(":", 1)
                # GCP labels can't contain dots, replace with underscores
                gcp_key = key.replace(".", "_").lower()
                # GCP label values must be lowercase
                gcp_value = value.lower().replace(" ", "_")
                labels[gcp_key] = gcp_value
            else:
                # Tag without value
                gcp_key = tag.replace(".", "_").lower()
                labels[gcp_key] = "true"

        return labels

    def _extract_image_family(self, instance) -> Optional[str]:
        """Extract image family from GCP instance boot disk"""
        try:
            from google.cloud import compute_v1

            # Find the boot disk
            for disk in instance.disks:
                if disk.boot:
                    # For existing instances, we need to query the disk resource
                    # to get the source image information
                    if disk.source:
                        try:
                            # Extract disk name and zone from the source URL
                            # Format: https://www.googleapis.com/compute/v1/projects/PROJECT/zones/ZONE/disks/DISK_NAME
                            parts = disk.source.split("/")
                            if len(parts) >= 2:
                                disk_name = parts[-1]
                                zone = parts[-3] if len(parts) >= 3 else None

                                if zone and self._project_id:
                                    # Create a disks client using default authentication
                                    disks_client = compute_v1.DisksClient()

                                    # Get the disk resource
                                    disk_resource = disks_client.get(
                                        project=self._project_id,
                                        zone=zone,
                                        disk=disk_name,
                                    )

                                    # Extract source image from disk resource
                                    if (
                                        hasattr(disk_resource, "source_image")
                                        and disk_resource.source_image
                                    ):
                                        source_image = disk_resource.source_image
                                        # Extract image family from URL like:
                                        # https://www.googleapis.com/compute/v1/projects/ubuntu-os-cloud/global/images/ubuntu-2204-jammy-v20231201
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
                                                elif "ubuntu-1804" in image_name:
                                                    return "ubuntu-1804-lts"
                                                elif "debian-12" in image_name:
                                                    return "debian-12"
                                                elif "debian-11" in image_name:
                                                    return "debian-11"
                                                elif "debian-10" in image_name:
                                                    return "debian-10"
                                                elif "centos" in image_name:
                                                    return "centos-7"
                                                else:
                                                    # Return simplified image name
                                                    return (
                                                        image_name.split("-v")[0]
                                                        if "-v" in image_name
                                                        else image_name
                                                    )
                        except Exception as e:
                            print(
                                f"[DEBUG] Error extracting image from disk resource: {e}"
                            )
                            pass

                    # Fallback: check initialize_params (only works during creation)
                    if hasattr(disk, "initialize_params") and disk.initialize_params:
                        if (
                            hasattr(disk.initialize_params, "source_image")
                            and disk.initialize_params.source_image
                        ):
                            source_image = disk.initialize_params.source_image
                            # Extract image family from URL
                            parts = source_image.split("/")
                            if "family" in parts:
                                family_idx = parts.index("family")
                                if family_idx + 1 < len(parts):
                                    return parts[family_idx + 1]
                    break
        except Exception as e:
            print(f"[DEBUG] Error in _extract_image_family: {e}")
            # If image extraction fails, return None
            pass
        return None

    def _convert_tags_dict_to_labels(self, tags: Dict[str, str]) -> Dict[str, str]:
        """Convert InfraDSL tags dict to GCP labels"""
        labels = {}

        for key, value in tags.items():
            # GCP labels can't contain dots, replace with underscores
            gcp_key = key.replace(".", "_").lower()
            # GCP label values must be lowercase
            gcp_value = str(value).lower().replace(" ", "_")
            labels[gcp_key] = gcp_value

        return labels

    def _matches_query(self, instance: Dict[str, Any], query: ResourceQuery) -> bool:
        """Check if instance matches query filters"""
        filters = query.filters

        if "name" in filters and instance.get("name") != filters["name"]:
            return False

        if "id" in filters and instance.get("id") != filters["id"]:
            return False

        # Add more filter logic as needed

        return True

    def _resize_instance(
        self, instance_name: str, zone: str, new_machine_type: str
    ) -> None:
        """Resize a GCP Compute Engine instance"""
        # GCP requires instance to be stopped before resizing
        print(f"[DEBUG] Resizing instance {instance_name} to {new_machine_type}")

        # Stop the instance
        if not self._compute_client:
            raise ProviderException("GCP client not initialized")
        self._compute_client.stop(
            project=self._project_id, zone=zone, instance=instance_name
        )

        # Wait for it to stop
        self._wait_for_instance_status(instance_name, zone, "TERMINATED")

        # Change machine type
        from google.cloud import compute_v1

        request = compute_v1.InstancesSetMachineTypeRequest(
            machine_type=f"zones/{zone}/machineTypes/{new_machine_type}"
        )
        self._compute_client.set_machine_type(
            project=self._project_id,
            zone=zone,
            instance=instance_name,
            instances_set_machine_type_request_resource=request,
        )

        # Start the instance
        self._compute_client.start(
            project=self._project_id, zone=zone, instance=instance_name
        )

        # Wait for it to start
        self._wait_for_instance_status(instance_name, zone, "RUNNING")

    def _update_instance_labels(
        self, instance_name: str, zone: str, tags_update: Dict[str, Any]
    ) -> None:
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
            from google.cloud import compute_v1  # type: ignore

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

    def _wait_for_instance_status(
        self, instance_name: str, zone: str, target_status: str, timeout: int = 120
    ) -> None:
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

    def discover_resources(
        self, resource_type: str, query: Optional[ResourceQuery] = None
    ) -> List[Dict[str, Any]]:
        """Discover resources in GCP using broader discovery mechanisms"""
        return self.list_resources(resource_type, query)

    def plan_create(
        self, resource_type: str, config: Dict[str, Any], metadata: ResourceMetadata
    ) -> Dict[str, Any]:
        """Preview the creation of a GCP resource"""
        try:
            # Return a plan showing what would be created
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

            # Add resource-specific preview information
            if resource_type == "instance":
                plan["preview"] = {
                    "instance_name": config.get("name"),
                    "machine_type": config.get(
                        "machine_type", config.get("size", "e2-small")
                    ),
                    "zone": config.get("zone", f"{self.config.region}-a"),
                    "image_family": config.get(
                        "image_family", config.get("image", "ubuntu-2204-lts")
                    ),
                    "disk_size_gb": config.get("disk_size_gb", 20),
                    "public_ip": config.get("public_ip", True),
                    "ssh_keys": len(config.get("ssh_keys", [])),
                }

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
            # Get current resource state
            current_resource = self.get_resource(resource_id, resource_type)

            plan = {
                "action": "update",
                "resource_type": resource_type,
                "resource_id": resource_id,
                "provider": "gcp",
                "changes": updates,
                "current_state": current_resource,
            }

            # Add resource-specific update preview
            if resource_type == "instance":
                plan["preview"] = {
                    "instance_id": resource_id,
                    "changes": list(updates.keys()),
                    "requires_restart": "size" in updates,
                }

                if "size" in updates:
                    plan["warnings"] = [
                        "Changing machine type requires the instance to be stopped",
                        "This will cause downtime during the resize operation",
                    ]

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
            # Get current resource state
            current_resource = self.get_resource(resource_id, resource_type)

            plan = {
                "action": "delete",
                "resource_type": resource_type,
                "resource_id": resource_id,
                "provider": "gcp",
                "current_state": current_resource,
            }

            # Add resource-specific deletion warnings
            if resource_type == "instance":
                plan["warnings"] = [
                    "Instance and all attached disks will be permanently deleted",
                    "This action cannot be undone",
                    "All data on the instance will be lost",
                ]

            return plan
        except Exception as e:
            return {
                "action": "delete",
                "resource_type": resource_type,
                "resource_id": resource_id,
                "error": str(e),
            }

    def _list_instances_via_gcloud(self) -> List[Dict[str, Any]]:
        """List GCP instances using gcloud CLI as fallback"""
        try:
            import subprocess
            import json

            # Use gcloud CLI to list instances
            cmd = [
                "gcloud",
                "compute",
                "instances",
                "list",
                "--project",
                self._project_id,
                "--format",
                "json",
            ]

            # Add region filter if specified
            if self.config.region:
                cmd.extend(["--filter", f"zone:{self.config.region}"])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                print(f"[DEBUG] gcloud command failed: {result.stderr}")
                return []

            instances_data = json.loads(result.stdout)
            instances = []

            for instance_data in instances_data:
                # Convert gcloud format to our format
                instance_dict = {
                    "id": str(instance_data.get("id", "")),
                    "cloud_id": str(instance_data.get("id", "")),
                    "name": instance_data.get("name", ""),
                    "type": "VirtualMachine",
                    "provider": "gcp",
                    "zone": (
                        instance_data.get("zone", "").split("/")[-1]
                        if instance_data.get("zone")
                        else ""
                    ),
                    "region": self.config.region or "",
                    "project": self._project_id,
                    "status": instance_data.get("status", "").lower(),
                    "machine_type": (
                        instance_data.get("machineType", "").split("/")[-1]
                        if instance_data.get("machineType")
                        else ""
                    ),
                    "tags": self._extract_labels_from_gcloud(instance_data),
                    "configuration": {
                        "machine_type": (
                            instance_data.get("machineType", "").split("/")[-1]
                            if instance_data.get("machineType")
                            else ""
                        ),
                        "zone": (
                            instance_data.get("zone", "").split("/")[-1]
                            if instance_data.get("zone")
                            else ""
                        ),
                        "status": instance_data.get("status", ""),
                    },
                    "metadata": instance_data,
                }
                instances.append(instance_dict)

            print(f"[DEBUG] Found {len(instances)} GCP instances via gcloud CLI")
            return instances

        except Exception as e:
            print(f"[DEBUG] Failed to list instances via gcloud: {e}")
            return []

    def _extract_labels_from_gcloud(
        self, instance_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Extract labels from gcloud instance data"""
        labels = {}

        # Get labels from instance metadata
        if "labels" in instance_data:
            labels.update(instance_data["labels"])

        # Add system labels for tracking
        labels.update({"infradsl.discovered": "true", "infradsl.source": "gcloud-cli"})

        return labels


# Provider metadata for registration
METADATA = {
    "name": "Google Cloud Platform Compute Engine",
    "provider_type": ProviderType.GCP,
    "version": "1.0.0",
    "author": "InfraDSL Team",
    "description": "Google Cloud Platform Compute Engine provider for VM management",
    "resource_types": ["instance"],
    "regions": [
        "us-central1",
        "us-east1",
        "us-west1",
        "us-west2",
        "europe-west1",
        "europe-west2",
        "asia-east1",
        "asia-southeast1",
    ],
    "required_config": ["project"],
    "optional_config": ["region", "credentials"],
    "documentation_url": "https://cloud.google.com/compute/docs",
}
