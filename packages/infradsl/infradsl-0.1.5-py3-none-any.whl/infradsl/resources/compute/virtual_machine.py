from typing import Optional, List, Dict, Any, Self, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from infradsl.core.interfaces.provider import ProviderInterface

from dataclasses import dataclass, field
from enum import Enum

from ...core.nexus.base_resource import BaseResource, ResourceSpec
from ...core.interfaces.provider import ProviderType


class ImageType(Enum):
    """Common OS image types"""

    UBUNTU = "ubuntu"
    DEBIAN = "debian"
    CENTOS = "centos"
    RHEL = "rhel"
    WINDOWS = "windows"
    AMAZON_LINUX = "amazon_linux"
    CUSTOM = "custom"


class InstanceSize(Enum):
    """Standardized instance sizes"""

    NANO = "nano"  # 1 vCPU, 0.5GB RAM
    MICRO = "micro"  # 1 vCPU, 1GB RAM
    SMALL = "small"  # 1 vCPU, 2GB RAM
    MEDIUM = "medium"  # 2 vCPU, 4GB RAM
    LARGE = "large"  # 4 vCPU, 8GB RAM
    XLARGE = "xlarge"  # 8 vCPU, 16GB RAM
    CUSTOM = "custom"  # Custom specs


@dataclass
class VirtualMachineSpec(ResourceSpec):
    """Specification for a virtual machine resource"""

    # Core configuration
    image_type: ImageType = ImageType.UBUNTU
    image_version: str = "22.04"
    custom_image: Optional[str] = None
    instance_size: InstanceSize = InstanceSize.SMALL

    # Custom sizing (when instance_size is CUSTOM)
    cpu_cores: Optional[int] = None
    memory_gb: Optional[int] = None

    # Storage
    disk_size_gb: int = 20
    disk_type: str = "ssd"
    additional_disks: List[Dict[str, Any]] = field(default_factory=list)

    # Network
    public_ip: bool = True
    security_groups: List[str] = field(default_factory=list)
    subnet_id: Optional[str] = None
    vpc_id: Optional[str] = None

    # Access
    ssh_key: Optional[str] = None
    ssh_keys: List[str] = field(default_factory=list)
    user_data: Optional[str] = None
    admin_user: Optional[str] = None

    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)

    # Internal SSH key content storage
    _ssh_key_content: Dict[str, str] = field(default_factory=dict)


class VirtualMachine(BaseResource):
    """
    Universal virtual machine resource that works across all providers.

    Examples:
        # Simple VM
        vm = VirtualMachine("my-vm").ubuntu().create()

        # Custom configuration
        vm = (VirtualMachine("web-server")
              .ubuntu("20.04")
              .size(InstanceSize.MEDIUM)
              .disk(50)
              .public_ip(True)
              .ssh_key("my-key")
              .create())
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.spec: VirtualMachineSpec = self._create_spec()
        # Store resource type in annotations for cache fingerprinting
        self.metadata.annotations["resource_type"] = "VirtualMachine"

    def _create_spec(self) -> VirtualMachineSpec:
        return VirtualMachineSpec()

    def _validate_spec(self) -> None:
        """Validate VM specification"""
        if self.spec.instance_size == InstanceSize.CUSTOM:
            if not self.spec.cpu_cores or not self.spec.memory_gb:
                raise ValueError(
                    "Custom instance size requires cpu_cores and memory_gb"
                )

        if self.spec.disk_size_gb < 10:
            raise ValueError("Disk size must be at least 10GB")

        if self.spec.image_type == ImageType.CUSTOM and not self.spec.custom_image:
            raise ValueError("Custom image type requires custom_image")

    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        # Handle case where provider is still a string (not resolved)
        if isinstance(self._provider, str):
            provider_type_str = self._provider.lower()
        else:
            # Get provider type from provider object
            provider_type = self._provider.config.type
            provider_type_str = (
                provider_type.value
                if hasattr(provider_type, "value")
                else str(provider_type)
            )

        # Base configuration
        config = {
            "name": self.metadata.name,
            "image_type": self.spec.image_type.value,
            "image_version": self.spec.image_version,
            "instance_size": self.spec.instance_size.value,
            "disk_size_gb": self.spec.disk_size_gb,
            "disk_type": self.spec.disk_type,
            "public_ip": self.spec.public_ip,
            "security_groups": self.spec.security_groups,
            "ssh_keys": self.spec.ssh_keys,
            "user_data": self.spec.user_data,
            "tags": self.metadata.to_tags(),
        }

        # Add custom sizing if specified
        if self.spec.instance_size == InstanceSize.CUSTOM:
            config.update(
                {
                    "cpu_cores": self.spec.cpu_cores,
                    "memory_gb": self.spec.memory_gb,
                }
            )

        # Provider-specific mappings
        if provider_type_str.lower() == "aws":
            config.update(self._to_aws_config())
        elif provider_type_str.lower() == "gcp":
            config.update(self._to_gcp_config())
        elif provider_type_str.lower() in ["digital_ocean", "digitalocean"]:
            config.update(self._to_digitalocean_config())

        # Apply provider-specific overrides
        config.update(self.spec.provider_config)

        return config

    def _to_aws_config(self) -> Dict[str, Any]:
        """Convert to AWS EC2 configuration"""
        # Map instance sizes to AWS instance types
        size_mapping = {
            InstanceSize.NANO: "t3.nano",
            InstanceSize.MICRO: "t3.micro",
            InstanceSize.SMALL: "t3.small",
            InstanceSize.MEDIUM: "t3.medium",
            InstanceSize.LARGE: "t3.large",
            InstanceSize.XLARGE: "t3.xlarge",
        }

        # Map images to AMI patterns
        image_mapping = {
            ImageType.UBUNTU: f"ubuntu/images/hvm-ssd/ubuntu-*-{self.spec.image_version}-amd64-server-*",
            ImageType.AMAZON_LINUX: "amzn2-ami-hvm-*-x86_64-gp2",
            ImageType.RHEL: f"RHEL-{self.spec.image_version}*-x86_64-*",
        }

        config = {
            "resource_type": "ec2_instance",
            "instance_type": size_mapping.get(self.spec.instance_size, "t3.micro"),
            "ami_pattern": image_mapping.get(
                self.spec.image_type, image_mapping[ImageType.UBUNTU]
            ),
        }

        if self.spec.ssh_key:
            config["key_name"] = self.spec.ssh_key

        return config

    def _to_gcp_config(self) -> Dict[str, Any]:
        """Convert to GCP Compute Engine configuration"""
        # Map instance sizes to GCP machine types
        size_mapping = {
            InstanceSize.NANO: "f1-micro",
            InstanceSize.MICRO: "f1-micro",
            InstanceSize.SMALL: "e2-small",
            InstanceSize.MEDIUM: "e2-medium",
            InstanceSize.LARGE: "e2-standard-4",
            InstanceSize.XLARGE: "e2-standard-8",
        }

        # Map images to GCP image families
        image_mapping = {
            ImageType.UBUNTU: f"ubuntu-{self.spec.image_version.replace('.', '')}-lts",
            ImageType.DEBIAN: "debian-11",
            ImageType.CENTOS: "centos-7",
        }

        config = {
            "resource_type": "instance",
            "machine_type": self.spec.provider_config.get("machine_type") or size_mapping.get(self.spec.instance_size, "e2-small"),
            "image_family": image_mapping.get(
                self.spec.image_type, image_mapping[ImageType.UBUNTU]
            ),
            "image_project": (
                "ubuntu-os-cloud"
                if self.spec.image_type == ImageType.UBUNTU
                else "debian-cloud"
            ),
        }
        
        # Include zone from provider_config if set
        if "zone" in self.spec.provider_config:
            config["zone"] = self.spec.provider_config["zone"]
        
        # Include region from provider_config if set
        if "region" in self.spec.provider_config:
            config["region"] = self.spec.provider_config["region"]
            
        # Include disk configuration
        config["boot_disk"] = {
            "size_gb": self.spec.disk_size_gb,
            "type": "pd-ssd" if self.spec.disk_type == "ssd" else "pd-standard"
        }
        
        # Include network configuration
        if "network_interfaces" in self.spec.provider_config:
            config["network_interfaces"] = self.spec.provider_config["network_interfaces"]
        else:
            # Default network config with external IP
            config["network_interfaces"] = [{
                "network": "default",
                "access_configs": [{"type": "ONE_TO_ONE_NAT", "name": "External NAT"}] if self.spec.public_ip else []
            }]
        
        # Include metadata
        if "metadata" in self.spec.provider_config:
            config["metadata"] = self.spec.provider_config["metadata"]
        
        # Add startup script from user_data
        if self.spec.user_data:
            if "metadata" not in config:
                config["metadata"] = {}
            config["metadata"]["startup-script"] = self.spec.user_data
            
        # Include labels
        if "labels" in self.spec.provider_config:
            config["labels"] = self.spec.provider_config["labels"]
            
        # Include network tags
        if "tags" in self.spec.provider_config:
            config["tags"] = self.spec.provider_config["tags"]
            
        # Include service account
        if "service_account" in self.spec.provider_config:
            config["service_accounts"] = [self.spec.provider_config["service_account"]]
        
        # Include scheduling (preemptible, GPU, etc.)
        scheduling = {}
        if self.spec.provider_config.get("preemptible"):
            scheduling["preemptible"] = True
            scheduling["automatic_restart"] = self.spec.provider_config.get("automatic_restart", False)
        if "on_host_maintenance" in self.spec.provider_config:
            scheduling["on_host_maintenance"] = self.spec.provider_config["on_host_maintenance"]
        if scheduling:
            config["scheduling"] = scheduling
            
        # Include GPU accelerators
        if "guest_accelerators" in self.spec.provider_config:
            config["guest_accelerators"] = self.spec.provider_config["guest_accelerators"]
        
        # Include other GCP-specific settings
        for key in ["can_ip_forward", "deletion_protection", "shielded_instance_config", "confidential_instance_config"]:
            if key in self.spec.provider_config:
                config[key] = self.spec.provider_config[key]

        return config

    def _to_digitalocean_config(self) -> Dict[str, Any]:
        """Convert to DigitalOcean Droplet configuration"""
        # Map instance sizes to DO slugs
        size_mapping = {
            InstanceSize.NANO: "s-1vcpu-512mb-10gb",
            InstanceSize.MICRO: "s-1vcpu-1gb",
            InstanceSize.SMALL: "s-1vcpu-2gb",
            InstanceSize.MEDIUM: "s-2vcpu-4gb",
            InstanceSize.LARGE: "s-4vcpu-8gb",
            InstanceSize.XLARGE: "s-8vcpu-16gb",
        }

        # Map images to DO slugs
        image_mapping = {
            ImageType.UBUNTU: f"ubuntu-{self.spec.image_version.replace('.', '-')}-x64",
            ImageType.DEBIAN: "debian-11-x64",
            ImageType.CENTOS: "centos-7-x64",
        }

        # Generate user data for custom user creation
        user_data = self.spec.user_data
        if self.spec.admin_user and not user_data:
            user_data = self._generate_user_creation_script()

        config = {
            "resource_type": "droplet",
            "name": self.name,
            "size": size_mapping.get(self.spec.instance_size, "s-1vcpu-2gb"),
            "image": image_mapping.get(
                self.spec.image_type, image_mapping[ImageType.UBUNTU]
            ),
            "region": self.spec.provider_config.get("region", "nyc1"),
            "backups": getattr(self.spec, "backups", False),
            "ipv6": getattr(self.spec, "ipv6", True),
            "monitoring": getattr(self.spec, "monitoring", True),
            "user_data": user_data,
            "tags": self.metadata.to_tags(),
            "ssh_keys": self.spec.ssh_keys,
            "additional_disks": self.spec.additional_disks,  # Include additional disks for LEGO principle
        }

        # Include SSH key content if available
        if hasattr(self.spec, "_ssh_key_content"):
            config["_ssh_key_content"] = self.spec._ssh_key_content

        return config

    def _generate_user_creation_script(self) -> str:
        """Generate cloud-init script to create custom user"""
        if not self.spec.admin_user:
            return ""

        # Get the SSH public key content for the user
        ssh_key_content = ""
        if hasattr(self.spec, "_ssh_key_content") and self.spec._ssh_key_content:
            # Get the first SSH key content
            ssh_key_content = list(self.spec._ssh_key_content.values())[0]

        script = f"""#cloud-config
users:
  - name: {self.spec.admin_user}
    groups: sudo
    shell: /bin/bash
    sudo: ['ALL=(ALL) NOPASSWD:ALL']
    ssh_authorized_keys:"""

        if ssh_key_content:
            script += f"""
      - {ssh_key_content}"""
        else:
            script += """
      []"""

        # Add SSH key to root as well
        if ssh_key_content:
            script += f"""
  - name: root
    ssh_authorized_keys:
      - {ssh_key_content}

# Global SSH keys (fallback)
ssh_authorized_keys:
  - {ssh_key_content}"""

        script += (
            """

# Set hostname
hostname: """
            + self.name
            + """
manage_etc_hosts: true

# Update packages
package_update: true
package_upgrade: false

# Install essential packages
packages:
  - curl
  - wget
  - git
  - htop
  - vim
"""
        )

        return script

    # Fluent interface methods

    def ubuntu(self, version = "22.04") -> Self:
        """Set Ubuntu image
        
        Args:
            version: Version as string or numeric (e.g., "22.04", 22.04, 22_04)
            
        Examples:
            .ubuntu("22.04")
            .ubuntu(22.04)
            .ubuntu(22_04)
        """
        self.spec.image_type = ImageType.UBUNTU
        
        # Handle different version formats
        if isinstance(version, (int, float)):
            # Convert 22.04 or 2204 to "22.04"
            if version >= 1000:  # Looks like 2204
                version_str = f"{version // 100}.{version % 100:02d}"
            else:  # Looks like 22.04
                version_str = f"{version:.2f}"
        elif isinstance(version, str) and '_' in version:
            # Convert "22_04" to "22.04"
            version_str = version.replace('_', '.')
        else:
            version_str = str(version)
            
        self.spec.image_version = version_str
        return self

    def debian(self, version: str = "11") -> Self:
        """Set Debian image"""
        self.spec.image_type = ImageType.DEBIAN
        self.spec.image_version = version
        return self

    def centos(self, version: str = "7") -> Self:
        """Set CentOS image"""
        self.spec.image_type = ImageType.CENTOS
        self.spec.image_version = version
        return self

    def rhel(self, version: str = "8") -> Self:
        """Set RHEL image"""
        self.spec.image_type = ImageType.RHEL
        self.spec.image_version = version
        return self

    def windows(self, version: str = "2022") -> Self:
        """Set Windows image"""
        self.spec.image_type = ImageType.WINDOWS
        self.spec.image_version = version
        return self

    def amazon_linux(self, version: str = "2") -> Self:
        """Set Amazon Linux image"""
        self.spec.image_type = ImageType.AMAZON_LINUX
        self.spec.image_version = version
        return self

    def custom_image(self, image: str) -> Self:
        """Set custom image"""
        self.spec.image_type = ImageType.CUSTOM
        self.spec.custom_image = image
        return self

    def size(self, instance_size: InstanceSize) -> Self:
        """Set instance size"""
        self.spec.instance_size = instance_size
        return self

    def custom_size(self, cpu_cores: int, memory_gb: int) -> Self:
        """Set custom instance size"""
        self.spec.instance_size = InstanceSize.CUSTOM
        self.spec.cpu_cores = cpu_cores
        self.spec.memory_gb = memory_gb
        return self

    def disk(self, size_gb: int, disk_type: str = "ssd") -> Self:
        """Set disk configuration"""
        self.spec.disk_size_gb = size_gb
        self.spec.disk_type = disk_type
        return self

    def add_disk(
        self, size_gb: int, mount_point: Optional[str] = None, disk_type: str = "ssd"
    ) -> Self:
        """Add additional disk"""
        self.spec.additional_disks.append(
            {"size_gb": size_gb, "type": disk_type, "mount_point": mount_point}
        )
        return self

    def zone(self, zone_name) -> Self:
        """Set availability zone (GCP-specific)
        
        Args:
            zone_name: Zone name as string or Region enum value
            
        Examples:
            .zone("europe-west1-b")
            .zone(Region.EUROPE_WEST1_B)
        """
        # Handle both string and enum values
        from ...regions import Region
        if isinstance(zone_name, Region):
            zone_str = zone_name.value
        else:
            zone_str = str(zone_name)
            
        self.spec.provider_config["zone"] = zone_str
        # Store zone in annotations for cache fingerprinting
        self.metadata.annotations["zone"] = zone_str
        return self

    def region(self, region_name: str) -> Self:
        """Set region for resource deployment"""
        self.spec.provider_config["region"] = region_name
        return self

    def database(self, engine: str = "postgresql") -> Self:
        """Mark this VM as a database server - enables data protection mode"""
        self.metadata.labels["infradsl.workload"] = "database"
        self.metadata.labels["infradsl.database-engine"] = engine
        return self

    def is_database(self) -> bool:
        """Check if this VM is marked as a database"""
        return self.metadata.labels.get("infradsl.workload") == "database"

    def public_ip(self, enable: bool = True) -> Self:
        """Enable/disable public IP"""
        self.spec.public_ip = enable
        return self

    def ssh_key(self, key_name_or_path: str, name: Optional[str] = None) -> Self:
        """Set SSH key - accepts either a DO key name or local file path"""
        import os

        # Check if it's a file path
        if (
            key_name_or_path.startswith("~")
            or key_name_or_path.startswith("/")
            or "." in key_name_or_path
        ):
            # Expand user home directory
            key_path = os.path.expanduser(key_name_or_path)

            if os.path.exists(key_path):
                # Read the public key content
                try:
                    with open(key_path, "r") as f:
                        key_content = f.read().strip()

                    # Use provided name or generate one from the path
                    if name:
                        key_name = name
                    else:
                        # Use filename without extension as default name
                        import os

                        filename = os.path.basename(key_path)
                        if filename.endswith(".pub"):
                            filename = filename[:-4]  # Remove .pub extension
                        key_name = f"infradsl-{filename}"

                    # Store the key content for upload during creation
                    self.spec.ssh_key = key_name
                    if not hasattr(self.spec, "_ssh_key_content"):
                        self.spec._ssh_key_content = {}
                    self.spec._ssh_key_content[key_name] = key_content

                    if key_name not in self.spec.ssh_keys:
                        self.spec.ssh_keys.append(key_name)

                except Exception as e:
                    raise ValueError(f"Failed to read SSH key file {key_path}: {e}")
            else:
                raise ValueError(f"SSH key file not found: {key_path}")
        else:
            # It's a key name - use as-is
            self.spec.ssh_key = key_name_or_path
            if key_name_or_path not in self.spec.ssh_keys:
                self.spec.ssh_keys.append(key_name_or_path)

        return self

    def ssh_keys(self, keys: List[str]) -> Self:
        """Set multiple SSH keys"""
        self.spec.ssh_keys = keys
        return self

    def security_group(self, group: str) -> Self:
        """Add security group"""
        if group not in self.spec.security_groups:
            self.spec.security_groups.append(group)
        return self

    def security_groups(self, groups: List[str]) -> Self:
        """Set security groups"""
        self.spec.security_groups = groups
        return self

    def user_data(self, script: str) -> Self:
        """Set user data script"""
        self.spec.user_data = script
        return self

    def startup_script(self, script_or_path: str) -> Self:
        """Set startup script from string or file (chainable)
        
        Args:
            script_or_path: Either a script string or path to a script file
            
        Examples:
            .startup_script("#!/bin/bash\necho 'Hello'")
            .startup_script("./scripts/setup.sh")
            .startup_script("~/init-scripts/web-server.sh")
        """
        import os
        
        # Check if it looks like a file path
        if (script_or_path.startswith("./") or 
            script_or_path.startswith("~/") or
            script_or_path.startswith("/") or
            (os.sep in script_or_path and len(script_or_path.split('\n')) == 1)):
            
            # Expand user home directory
            script_path = os.path.expanduser(script_or_path)
            
            if os.path.exists(script_path):
                try:
                    with open(script_path, 'r', encoding='utf-8') as f:
                        script_content = f.read()
                    
                    # Validate it's a script (starts with shebang or has common script indicators)
                    if (script_content.startswith('#!') or 
                        'apt-get' in script_content or
                        'yum ' in script_content or
                        'systemctl' in script_content or
                        script_path.endswith(('.sh', '.bash', '.py', '.pl'))):
                        
                        return self.user_data(script_content)
                    else:
                        # Warn but still use it
                        import logging
                        logging.warning(f"File {script_path} doesn't look like a script, using anyway")
                        return self.user_data(script_content)
                        
                except Exception as e:
                    raise ValueError(f"Failed to read startup script file {script_path}: {e}")
            else:
                raise ValueError(f"Startup script file not found: {script_path}")
        else:
            # It's a script string
            return self.user_data(script_or_path)

    def meta(self, key: str, value: str) -> Self:
        """Add metadata key-value pair (chainable)"""
        if "metadata" not in self.spec.provider_config:
            self.spec.provider_config["metadata"] = {}
        self.spec.provider_config["metadata"][key] = value
        return self

    def user(self, username: str) -> Self:
        """Set admin user to be created on the VM"""
        self.spec.admin_user = username
        return self

    def subnet(self, subnet_id: str) -> Self:
        """Set subnet"""
        self.spec.subnet_id = subnet_id
        return self

    def vpc(self, vpc_id: str) -> Self:
        """Set VPC"""
        self.spec.vpc_id = vpc_id
        return self

    def with_provider(self, provider) -> Self:
        """Associate this VM with a specific provider instance
        
        Args:
            provider: Provider instance to associate with this VM
            
        Examples:
            .with_provider(google_cloud)
            .with_provider(aws_provider)
        """
        self._provider = provider
        return self

    def with_project(self, project_id: str) -> Self:
        """Set the cloud project/account ID for this VM
        
        Args:
            project_id: The project ID (GCP) or account ID (AWS/DO)
            
        Examples:
            .with_project("my-gcp-project-123")
            .with_project("123456789012")  # AWS account
        """
        self.spec.provider_config["project"] = project_id
        return self

    def provider_override(self, **kwargs) -> Self:
        """Override provider-specific settings"""
        self.spec.provider_config.update(kwargs)
        return self

    # GCP-specific methods
    
    def preemptible(self, automatic_restart: bool = False) -> Self:
        """Make instance preemptible/spot (GCP-specific, chainable)"""
        self.spec.provider_config["preemptible"] = True
        self.spec.provider_config["automatic_restart"] = automatic_restart
        self.spec.provider_config["on_host_maintenance"] = "TERMINATE"
        return self
    
    def spot(self) -> Self:
        """Alias for preemptible() for consistency with other clouds"""
        return self.preemptible()
    
    def gpu(self, gpu_type: str = "nvidia-tesla-t4", count: int = 1) -> Self:
        """Attach GPU to instance (GCP-specific, chainable)"""
        if "guest_accelerators" not in self.spec.provider_config:
            self.spec.provider_config["guest_accelerators"] = []
        
        self.spec.provider_config["guest_accelerators"].append({
            "type": gpu_type,
            "count": count
        })
        
        # GPU requires specific scheduling policy
        self.spec.provider_config["on_host_maintenance"] = "TERMINATE"
        self.spec.provider_config["automatic_restart"] = True
        return self
    
    def machine_type(self, machine_type: str) -> Self:
        """Set GCP machine type directly (GCP-specific, chainable)"""
        self.spec.provider_config["machine_type"] = machine_type
        return self
    
    def labels(self, labels_dict: Dict[str, str] = None, **labels) -> Self:
        """Set GCP labels (chainable)
        
        Args:
            labels_dict: Dictionary of labels (optional)
            **labels: Labels as keyword arguments
            
        Examples:
            .labels({"env": "prod", "team": "platform"})
            .labels(env="prod", team="platform")
        """
        if "labels" not in self.spec.provider_config:
            self.spec.provider_config["labels"] = {}
            
        # Handle dictionary argument
        if labels_dict:
            self.spec.provider_config["labels"].update(labels_dict)
            
        # Handle keyword arguments
        if labels:
            self.spec.provider_config["labels"].update(labels)
            
        return self
    
    def label(self, key: str, value: str) -> Self:
        """Add single GCP label (chainable)"""
        if "labels" not in self.spec.provider_config:
            self.spec.provider_config["labels"] = {}
        self.spec.provider_config["labels"][key] = value
        return self
    
    def tags(self, *tags: str) -> Self:
        """Set network tags (GCP-specific, chainable)"""
        self.spec.provider_config["tags"] = list(tags)
        return self
    
    def tag(self, *tags_to_add: str) -> Self:
        """Add network tags (GCP-specific, chainable)"""
        if "tags" not in self.spec.provider_config:
            self.spec.provider_config["tags"] = []
        for tag in tags_to_add:
            if tag not in self.spec.provider_config["tags"]:
                self.spec.provider_config["tags"].append(tag)
        return self
    
    def service_account(self, email: str = None, scopes: List[str] = None) -> Self:
        """Configure service account (GCP-specific, chainable)"""
        self.spec.provider_config["service_account"] = {
            "email": email or "default",
            "scopes": scopes or ["https://www.googleapis.com/auth/cloud-platform"]
        }
        return self
    
    def network(self, network: str = "default", subnet: str = None) -> Self:
        """Configure network (GCP-specific, chainable)"""
        network_config = {
            "network": network
        }
        if subnet:
            network_config["subnetwork"] = subnet
            
        self.spec.provider_config["network_interfaces"] = [network_config]
        return self
    
    def internal_only(self) -> Self:
        """Remove external IP (GCP-specific, chainable)"""
        # Ensure network interfaces exist
        if "network_interfaces" not in self.spec.provider_config:
            self.network()  # Set default network
        
        # Remove access configs (external IP)
        for interface in self.spec.provider_config["network_interfaces"]:
            interface.pop("access_configs", None)
        
        return self
    
    def can_ip_forward(self, enable: bool = True) -> Self:
        """Enable IP forwarding (GCP-specific, chainable)"""
        self.spec.provider_config["can_ip_forward"] = enable
        return self
    
    def deletion_protection(self, enable: bool = True) -> Self:
        """Enable deletion protection (GCP-specific, chainable)"""
        self.spec.provider_config["deletion_protection"] = enable
        return self
    
    def shielded_vm(self, secure_boot: bool = True, vtpm: bool = True, integrity_monitoring: bool = True) -> Self:
        """Enable shielded VM features (GCP-specific, chainable)"""
        self.spec.provider_config["shielded_instance_config"] = {
            "enable_secure_boot": secure_boot,
            "enable_vtpm": vtpm,
            "enable_integrity_monitoring": integrity_monitoring
        }
        return self
    
    def confidential_vm(self) -> Self:
        """Enable confidential VM (GCP-specific, chainable)"""
        self.spec.provider_config["confidential_instance_config"] = {
            "enable_confidential_compute": True
        }
        # Confidential VMs require N2D machine types
        if not self.spec.provider_config.get("machine_type", "").startswith("n2d-"):
            self.machine_type("n2d-standard-2")
        return self
    
    # LEGO principle methods - create related resources
    
    def static_ip(self, name: str = None) -> "StaticIP":
        """LEGO principle: create and attach static IP (chainable)"""
        from .static_ip import StaticIP
        
        ip_name = name or f"{self.name}-ip"
        static_ip = StaticIP(ip_name)
        
        # Configure based on VM's region/zone
        if "zone" in self.spec.provider_config:
            zone = self.spec.provider_config["zone"]
            # Extract region from zone (e.g., "us-central1-a" -> "us-central1")
            region = "-".join(zone.split("-")[:-1])
            static_ip.region(region)
        
        # Use same provider as VM
        if self._provider:
            static_ip.with_provider(self._provider)
            
        # Attach to this VM
        static_ip.attach_to_vm(self)
        
        return static_ip
    
    def instance_template(self, name: str = None) -> "InstanceTemplate":
        """LEGO principle: create instance template from this VM (chainable)"""
        from .instance_group import InstanceTemplate
        
        template_name = name or f"{self.name}-template"
        template = InstanceTemplate(template_name, self)
        
        # Use same provider as VM
        if self._provider:
            template.with_provider(self._provider)
            
        return template
        
    def instance_group(self, name: str = None, size: int = 3) -> "InstanceGroup":
        """LEGO principle: create instance group from this VM (chainable)"""
        from .instance_group import InstanceGroup
        
        # First create template
        template = self.instance_template(f"{self.name}-template")
        
        # Create instance group
        group_name = name or f"{self.name}-group"
        group = InstanceGroup(group_name)
        group.template(template)
        group.size(size)
        
        # Configure zones based on VM's zone
        if "zone" in self.spec.provider_config:
            vm_zone = self.spec.provider_config["zone"]
            region = "-".join(vm_zone.split("-")[:-1])
            
            # Create zone list for the same region
            zones = [
                f"{region}-a",
                f"{region}-b", 
                f"{region}-c"
            ]
            group.zones(zones)
        
        # Use same provider as VM
        if self._provider:
            group.with_provider(self._provider)
            
        return group
    
    def load_balancer(self, name: str = None, lb_type: str = "http") -> "LoadBalancer":
        """LEGO principle: create load balancer for this VM (chainable)"""
        from .load_balancer import LoadBalancer, LoadBalancerType
        
        lb_name = name or f"{self.name}-lb"
        lb = LoadBalancer(lb_name)
        
        # Configure based on type
        if lb_type.lower() == "http":
            lb.http()
        elif lb_type.lower() == "https":
            lb.https()
        elif lb_type.lower() == "tcp":
            lb.tcp(80)
        elif lb_type.lower() == "internal":
            lb.internal()
            
        # Add this VM as a backend
        lb.add_instance(self)
        
        # Configure region based on VM's zone
        if "zone" in self.spec.provider_config:
            zone = self.spec.provider_config["zone"]
            region = "-".join(zone.split("-")[:-1])
            if lb_type.lower() == "internal":
                lb.region(region)
        
        # Use same provider as VM
        if self._provider:
            lb.with_provider(self._provider)
            
        # Add default health check for HTTP/HTTPS
        if lb_type.lower() in ["http", "https"]:
            lb.health_check("/")
            
        return lb

    # Provider-specific implementations

    def _provider_create(self) -> Dict[str, Any]:
        """Create the VM via provider"""
        if not self._provider:
            raise ValueError("No provider attached")

        if isinstance(self._provider, str):
            raise ValueError(
                f"Provider '{self._provider}' is not resolved to an actual provider instance. Use a provider factory or ensure proper provider setup."
            )

        # Type cast to help type checker
        from typing import cast

        provider = cast("ProviderInterface", self._provider)

        config = self._to_provider_config()
        resource_type = config.pop("resource_type")

        return provider.create_resource(
            resource_type=resource_type, config=config, metadata=self.metadata
        )

    def _provider_update(self, diff: Dict[str, Any]) -> Dict[str, Any]:
        """Update the VM via provider"""
        if not self._provider:
            raise ValueError("No provider attached")

        if isinstance(self._provider, str):
            raise ValueError(
                f"Provider '{self._provider}' is not resolved to an actual provider instance. Use a provider factory or ensure proper provider setup."
            )

        if not self.status.cloud_id:
            raise ValueError(
                "Resource has no cloud ID - cannot update a resource that hasn't been created"
            )

        # Type cast to help type checker
        from typing import cast

        provider = cast("ProviderInterface", self._provider)

        config = self._to_provider_config()
        resource_type = config.pop("resource_type")

        return provider.update_resource(
            resource_id=self.status.cloud_id, resource_type=resource_type, updates=diff
        )

    def _provider_destroy(self) -> None:
        """Destroy the VM via provider"""
        if not self._provider:
            raise ValueError("No provider attached")

        if isinstance(self._provider, str):
            raise ValueError(
                f"Provider '{self._provider}' is not resolved to an actual provider instance. Use a provider factory or ensure proper provider setup."
            )

        if not self.status.cloud_id:
            raise ValueError(
                "Resource has no cloud ID - cannot destroy a resource that hasn't been created"
            )

        # Type cast to help type checker
        from typing import cast

        provider = cast("ProviderInterface", self._provider)

        config = self._to_provider_config()
        resource_type = config.pop("resource_type")

        provider.delete_resource(
            resource_id=self.status.cloud_id, resource_type=resource_type
        )

    # Convenience methods

    def get_ip(self) -> Optional[str]:
        """Get VM IP address"""
        return self.status.provider_data.get("ip_address")

    def get_private_ip(self) -> Optional[str]:
        """Get VM private IP address"""
        return self.status.provider_data.get("private_ip")

    def get_ssh_command(self, user: Optional[str] = None) -> str:
        """Get SSH command to connect to VM"""
        ip = self.get_ip()
        if not ip:
            raise ValueError("VM has no public IP")

        # Use specified user, or admin_user if set, or default to ubuntu
        ssh_user = user or self.spec.admin_user or "ubuntu"
        key_flag = f" -i {self.spec.ssh_key}" if self.spec.ssh_key else ""
        return f"ssh{key_flag} {ssh_user}@{ip}"
