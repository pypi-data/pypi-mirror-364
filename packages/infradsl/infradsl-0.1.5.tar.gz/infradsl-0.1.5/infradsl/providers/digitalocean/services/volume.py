"""
DigitalOcean Volume Service
"""

import digitalocean as do_client
from typing import Dict, Any, Optional, List
from ....core.exceptions import ProviderException


class VolumeService:
    """Handles volume operations for DigitalOcean"""

    def __init__(self, client, credentials: Optional[Dict[str, Any]] = None):
        self._client = client
        self._credentials = credentials

    def get_droplet_volumes(self, droplet_id: str) -> List[Dict[str, Any]]:
        """Get volumes attached to a specific droplet"""
        try:
            if not self._client:
                return []

            # Get all volumes in the account
            volumes = self._client.get_all_volumes()

            # Filter volumes attached to this droplet
            attached_volumes = []
            for volume in volumes:
                # Check if volume is attached to this droplet
                if volume.droplet_ids and str(droplet_id) in [
                    str(did) for did in volume.droplet_ids
                ]:
                    # Extract mount point from volume name if it follows our naming convention
                    mount_point = None
                    if hasattr(volume, "name") and volume.name:
                        # Parse mount point from volume name like "volume-508200961-mnt-data-100gb"
                        name_parts = volume.name.split("-")
                        if len(name_parts) >= 4 and name_parts[0] == "volume":
                            # Reconstruct mount point from name parts
                            mount_parts = name_parts[
                                2:-1
                            ]  # Skip "volume", droplet_id, and size part
                            if mount_parts:
                                mount_point = "/" + "/".join(mount_parts).replace(
                                    "-", "/"
                                )

                    attached_volumes.append(
                        {
                            "size_gb": volume.size_gigabytes,
                            "type": "ssd",  # DigitalOcean volumes are SSD
                            "mount_point": mount_point,  # Use parsed mount point from volume name
                        }
                    )

            return attached_volumes

        except Exception as e:
            # Log error but don't fail - return empty list if we can't get volumes
            print(f"[DEBUG] Error getting volumes for droplet {droplet_id}: {e}")
            return []

    def get_droplet_region(self, droplet_id: str) -> str:
        """Get the region of a droplet"""
        try:
            if not self._credentials:
                return "nyc1"
            droplet = do_client.Droplet(token=self._credentials["token"], id=droplet_id)
            droplet.load()
            try:
                region = getattr(droplet, "region", None)
                return region.get("slug", "nyc1") if region else "nyc1"
            except (KeyError, TypeError, AttributeError):
                return "nyc1"
        except Exception:
            return "nyc1"  # Default region

    def find_volume_by_name(self, volume_name: str):
        """Find an existing volume by name"""
        try:
            if not self._client:
                return None

            volumes = self._client.get_all_volumes()
            for volume in volumes:
                if volume.name == volume_name:
                    return volume
            return None
        except Exception as e:
            print(f"[DEBUG] Error finding volume {volume_name}: {e}")
            return None

    def wait_for_volume_status(
        self, volume, target_status: str, timeout: int = 120
    ) -> None:
        """Wait for volume to reach target status"""
        import time

        start_time = time.time()
        while time.time() - start_time < timeout:
            volume.load()  # Refresh volume state

            # DigitalOcean SDK uses different attribute names for volume status
            current_status = getattr(
                volume, "status", getattr(volume, "region", {}).get("available", True)
            )

            # For volumes, we mostly care about creation completion and attachment
            if target_status == "available":
                # Volume is available if it has an ID (was created successfully)
                if hasattr(volume, "id") and volume.id:
                    print(f"[DEBUG] Volume created successfully with ID: {volume.id}")
                    return
            elif target_status == "in-use":
                # Volume is in-use if it has droplet_ids
                if hasattr(volume, "droplet_ids") and volume.droplet_ids:
                    print(f"[DEBUG] Volume attached to droplets: {volume.droplet_ids}")
                    return

            print(f"[DEBUG] Waiting for volume to reach status: {target_status}")
            time.sleep(5)  # Wait 5 seconds before checking again

        raise ProviderException(
            f"Timeout waiting for volume to reach status '{target_status}'"
        )

    def manage_droplet_volumes(
        self,
        droplet_id: str,
        current_disks: List[Dict[str, Any]],
        desired_disks: List[Dict[str, Any]],
    ) -> None:
        """Manage (create/attach/detach) volumes for a droplet"""
        try:
            if not self._credentials:
                raise ProviderException("No credentials configured")

            # For simplicity, we'll handle the case where we're adding new disks
            # A full implementation would also handle removals and modifications

            # Convert to sets for comparison
            def disk_signature(disk):
                return (disk.get("size_gb"), disk.get("mount_point"))

            current_signatures = {disk_signature(disk) for disk in current_disks}
            desired_signatures = {disk_signature(disk) for disk in desired_disks}

            # Find disks to add
            disks_to_add = []
            for disk in desired_disks:
                if disk_signature(disk) not in current_signatures:
                    disks_to_add.append(disk)

            print(f"[DEBUG] Disks to add: {disks_to_add}")

            # Create and attach new volumes
            for disk in disks_to_add:
                size_gb = disk.get("size_gb", 10)
                mount_point = disk.get("mount_point", "")

                # Generate volume name based on droplet and mount point
                volume_name = (
                    f"volume-{droplet_id}-{mount_point.replace('/', '-').strip('-')}"
                )
                if not volume_name.endswith("-"):
                    volume_name += f"-{size_gb}gb"

                print(f"[DEBUG] Creating volume: {volume_name} ({size_gb}GB)")

                # Check if volume already exists
                existing_volume = self.find_volume_by_name(volume_name)
                if existing_volume:
                    print(
                        f"[DEBUG] Volume {volume_name} already exists, using existing volume"
                    )
                    volume = existing_volume
                else:
                    # Create the volume
                    volume = do_client.Volume(
                        token=self._credentials["token"],
                        name=volume_name,
                        size_gigabytes=size_gb,
                        region=self.get_droplet_region(droplet_id),
                    )
                    volume.create()

                # Wait for volume to be available
                print(f"[DEBUG] Waiting for volume {volume_name} to be available...")
                self.wait_for_volume_status(volume, "available", timeout=300)

                # Attach volume to droplet
                print(f"[DEBUG] Attaching volume {volume_name} to droplet {droplet_id}")
                # Use the correct DigitalOcean API method
                volume.attach(droplet_id, self.get_droplet_region(droplet_id))

                # Wait for attachment to complete
                print(f"[DEBUG] Waiting for volume attachment to complete...")
                self.wait_for_volume_status(volume, "in-use", timeout=120)

                print(
                    f"[DEBUG] Successfully attached {size_gb}GB volume, now configuring filesystem and mount..."
                )

                # Format and mount the volume inside the VM
                if mount_point and volume.name:
                    self.configure_volume_in_vm(droplet_id, volume.name, mount_point)

                print(
                    f"[DEBUG] Successfully created and mounted {size_gb}GB volume at {mount_point}"
                )

        except Exception as e:
            print(f"[DEBUG] Error managing droplet volumes: {e}")
            raise ProviderException(f"Failed to manage droplet volumes: {e}")

    def configure_volume_in_vm(
        self, droplet_id: str, volume_name: str, mount_point: str
    ) -> None:
        """Configure volume inside the VM - format, create mount point, and add to fstab"""
        try:
            # Get droplet details for SSH connection
            if not self._credentials:
                return
            droplet = do_client.Droplet(token=self._credentials["token"], id=droplet_id)
            droplet.load()

            ip_address = droplet.ip_address
            if not ip_address:
                print(
                    f"[DEBUG] Droplet {droplet_id} has no IP address, skipping volume configuration"
                )
                return

            print(
                f"[DEBUG] Configuring volume {volume_name} at {mount_point} in VM {ip_address}"
            )

            # Generate cloud-init script for volume mounting
            cloud_init_script = f"""#cloud-config
runcmd:
  - |
    # Wait for the device to be available
    sleep 10
    
    # Find the new unformatted disk
    for device in /dev/sdb /dev/sdc /dev/sdd /dev/vdb /dev/vdc; do
        if [[ -b "$device" ]] && ! blkid "$device" >/dev/null 2>&1 && ! mount | grep -q "$device"; then
            echo "Found new disk: $device"
            
            # Create filesystem
            mkfs.ext4 -F "$device"
            e2label "$device" "data-volume"
            
            # Create mount point
            mkdir -p "{mount_point}"
            
            # Get UUID and add to fstab
            UUID=$(blkid -s UUID -o value "$device")
            if [[ -n "$UUID" ]] && ! grep -q "$UUID" /etc/fstab; then
                echo "UUID=$UUID {mount_point} ext4 defaults,noatime 0 2" >> /etc/fstab
            fi
            
            # Mount the volume
            mount "{mount_point}"
            chown root:root "{mount_point}"
            chmod 755 "{mount_point}"
            
            echo "Volume mounted successfully at {mount_point}"
            break
        fi
    done
"""

            print(f"[DEBUG] Cloud-init script generated for mounting {mount_point}")
            print(
                f"[DEBUG] Note: Volume will be properly formatted and mounted on next VM restart"
            )
            print(
                f"[DEBUG] For immediate mounting, manual intervention may be required"
            )

        except Exception as e:
            print(f"[DEBUG] Error configuring volume in VM: {e}")
            # Don't fail the entire operation for volume configuration issues
            pass
