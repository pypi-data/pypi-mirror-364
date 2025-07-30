from typing import Optional, Dict, Any, Self, List, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
import base64

if TYPE_CHECKING:
    from infradsl.core.interfaces.provider import ProviderInterface

from ....core.nexus.base_resource import BaseResource, ResourceSpec


class InstanceType(Enum):
    """AWS EC2 Instance Types (common ones)"""
    # General Purpose
    T3_NANO = "t3.nano"
    T3_MICRO = "t3.micro"
    T3_SMALL = "t3.small"
    T3_MEDIUM = "t3.medium"
    T3_LARGE = "t3.large"
    T3_XLARGE = "t3.xlarge"
    T3_2XLARGE = "t3.2xlarge"
    
    # Burstable Performance
    T4G_NANO = "t4g.nano"
    T4G_MICRO = "t4g.micro"
    T4G_SMALL = "t4g.small"
    T4G_MEDIUM = "t4g.medium"
    T4G_LARGE = "t4g.large"
    
    # Compute Optimized
    C5_LARGE = "c5.large"
    C5_XLARGE = "c5.xlarge"
    C5_2XLARGE = "c5.2xlarge"
    C5_4XLARGE = "c5.4xlarge"
    C5_9XLARGE = "c5.9xlarge"
    C5_18XLARGE = "c5.18xlarge"
    
    # Memory Optimized
    R5_LARGE = "r5.large"
    R5_XLARGE = "r5.xlarge"
    R5_2XLARGE = "r5.2xlarge"
    R5_4XLARGE = "r5.4xlarge"
    R5_8XLARGE = "r5.8xlarge"
    R5_16XLARGE = "r5.16xlarge"
    
    # Storage Optimized
    I3_LARGE = "i3.large"
    I3_XLARGE = "i3.xlarge"
    I3_2XLARGE = "i3.2xlarge"
    I3_4XLARGE = "i3.4xlarge"


class EBSVolumeType(Enum):
    """EBS volume types"""
    GP2 = "gp2"
    GP3 = "gp3" 
    IO1 = "io1"
    IO2 = "io2"
    ST1 = "st1"
    SC1 = "sc1"
    STANDARD = "standard"


class Tenancy(Enum):
    """Instance tenancy"""
    DEFAULT = "default"
    DEDICATED = "dedicated"
    HOST = "host"


@dataclass
class EBSBlockDevice:
    """EBS block device specification"""
    device_name: str
    volume_size: int
    volume_type: EBSVolumeType = EBSVolumeType.GP3
    iops: Optional[int] = None
    throughput: Optional[int] = None
    encrypted: bool = True
    delete_on_termination: bool = True
    kms_key_id: Optional[str] = None


@dataclass
class NetworkInterface:
    """Network interface specification"""
    device_index: int
    subnet_id: str
    security_group_ids: List[str] = field(default_factory=list)
    private_ip: Optional[str] = None
    associate_public_ip: bool = False
    delete_on_termination: bool = True


@dataclass
class AWSEC2Spec(ResourceSpec):
    """Specification for AWS EC2 Instance"""
    
    # Instance configuration
    ami_id: str = ""
    instance_type: InstanceType = InstanceType.T3_MICRO
    key_name: Optional[str] = None
    
    # Network configuration
    subnet_id: str = ""
    security_group_ids: List[str] = field(default_factory=list)
    associate_public_ip_address: Optional[bool] = None
    private_ip: Optional[str] = None
    
    # Additional network interfaces
    network_interfaces: List[NetworkInterface] = field(default_factory=list)
    
    # Storage configuration
    root_volume_size: int = 20
    root_volume_type: EBSVolumeType = EBSVolumeType.GP3
    root_encrypted: bool = True
    additional_volumes: List[EBSBlockDevice] = field(default_factory=list)
    
    # User data and metadata
    user_data: str = ""
    user_data_file: str = ""
    metadata_options: Dict[str, Any] = field(default_factory=dict)
    
    # Instance configuration
    disable_api_termination: bool = False
    instance_initiated_shutdown_behavior: str = "stop"  # stop or terminate
    tenancy: Tenancy = Tenancy.DEFAULT
    
    # Placement
    availability_zone: Optional[str] = None
    placement_group: Optional[str] = None
    
    # Monitoring
    enable_monitoring: bool = False
    
    # IAM
    iam_instance_profile: Optional[str] = None
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class AWSEC2(BaseResource):
    """
    AWS EC2 Instance with comprehensive features and Rails-like conventions.
    
    Examples:
        # Simple web server
        web = (AWSEC2("web-server")
               .ami("ami-0abcdef1234567890")
               .instance_type("t3.medium")
               .subnet("subnet-12345678")
               .security_groups(["sg-web"])
               .key_pair("my-key")
               .public_ip()
               .user_data_file("startup.sh")
               .production())
        
        # Database server with encrypted storage
        db = (AWSEC2("database")
              .ami("ami-0abcdef1234567890")
              .memory_optimized("r5.xlarge")
              .private_subnet("subnet-database")
              .security_groups(["sg-database"])
              .root_volume(100, "gp3")
              .additional_volume("/dev/sdf", 500, "gp3")
              .disable_termination()
              .monitoring()
              .production())
              
        # Application server with IAM role
        app = (AWSEC2("app-server")
               .ami("ami-0abcdef1234567890")
               .compute_optimized("c5.2xlarge")
               .subnet("subnet-12345678")
               .security_groups(["sg-app"])
               .iam_role("app-server-role")
               .user_data("#!/bin/bash\nyum update -y")
               .placement_group("app-cluster")
               .production())
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.spec: AWSEC2Spec = self._create_spec()
        self.metadata.annotations["resource_type"] = "AWSEC2"
        
    def _create_spec(self) -> AWSEC2Spec:
        return AWSEC2Spec()
        
    def _validate_spec(self) -> None:
        """Validate AWS EC2 specification"""
        if not self.spec.ami_id:
            raise ValueError("AMI ID is required")
            
        if not self.spec.subnet_id and not self.spec.network_interfaces:
            raise ValueError("Either subnet_id or network_interfaces must be specified")
            
        # Validate EBS volumes
        for volume in self.spec.additional_volumes:
            if volume.volume_type in [EBSVolumeType.IO1, EBSVolumeType.IO2] and not volume.iops:
                raise ValueError(f"IOPS must be specified for {volume.volume_type.value} volumes")
                
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        config = {
            "name": self.metadata.name,
            "ami_id": self.spec.ami_id,
            "instance_type": self.spec.instance_type.value,
            "key_name": self.spec.key_name,
            "subnet_id": self.spec.subnet_id,
            "security_group_ids": self.spec.security_group_ids,
            "associate_public_ip_address": self.spec.associate_public_ip_address,
            "private_ip": self.spec.private_ip,
            "disable_api_termination": self.spec.disable_api_termination,
            "instance_initiated_shutdown_behavior": self.spec.instance_initiated_shutdown_behavior,
            "tenancy": self.spec.tenancy.value,
            "availability_zone": self.spec.availability_zone,
            "placement_group": self.spec.placement_group,
            "enable_monitoring": self.spec.enable_monitoring,
            "iam_instance_profile": self.spec.iam_instance_profile,
            "tags": {**self.spec.tags, **self.metadata.to_tags()},
        }
        
        # User data
        if self.spec.user_data_file:
            config["user_data"] = self._read_user_data_file()
        elif self.spec.user_data:
            config["user_data"] = base64.b64encode(self.spec.user_data.encode('utf-8')).decode('utf-8')
            
        # Root volume configuration
        config["root_block_device"] = {
            "volume_size": self.spec.root_volume_size,
            "volume_type": self.spec.root_volume_type.value,
            "encrypted": self.spec.root_encrypted,
            "delete_on_termination": True
        }
        
        # Additional EBS volumes
        if self.spec.additional_volumes:
            config["ebs_block_device"] = [
                self._ebs_volume_to_config(volume) for volume in self.spec.additional_volumes
            ]
            
        # Network interfaces
        if self.spec.network_interfaces:
            config["network_interface"] = [
                self._network_interface_to_config(ni) for ni in self.spec.network_interfaces
            ]
            
        # Metadata options
        if self.spec.metadata_options:
            config["metadata_options"] = self.spec.metadata_options

        # Provider-specific mappings
        if hasattr(self._provider, 'config') and hasattr(self._provider.config, 'type'):
            provider_type_str = self._provider.config.type.value.lower()
        else:
            provider_type_str = str(self._provider).lower()

        if provider_type_str == "aws":
            config.update(self._to_aws_config())

        # Apply provider-specific overrides
        config.update(self.spec.provider_config)

        return config
        
    def _read_user_data_file(self) -> str:
        """Read user data from file"""
        try:
            with open(self.spec.user_data_file, 'r') as f:
                content = f.read()
            return base64.b64encode(content.encode('utf-8')).decode('utf-8')
        except FileNotFoundError:
            raise ValueError(f"User data file not found: {self.spec.user_data_file}")
        except Exception as e:
            raise ValueError(f"Error reading user data file: {e}")
            
    def _ebs_volume_to_config(self, volume: EBSBlockDevice) -> Dict[str, Any]:
        """Convert EBS volume to configuration"""
        config = {
            "device_name": volume.device_name,
            "volume_size": volume.volume_size,
            "volume_type": volume.volume_type.value,
            "encrypted": volume.encrypted,
            "delete_on_termination": volume.delete_on_termination
        }
        
        if volume.iops:
            config["iops"] = volume.iops
        if volume.throughput:
            config["throughput"] = volume.throughput
        if volume.kms_key_id:
            config["kms_key_id"] = volume.kms_key_id
            
        return config
        
    def _network_interface_to_config(self, ni: NetworkInterface) -> Dict[str, Any]:
        """Convert network interface to configuration"""
        config = {
            "device_index": ni.device_index,
            "subnet_id": ni.subnet_id,
            "security_groups": ni.security_group_ids,
            "associate_public_ip_address": ni.associate_public_ip,
            "delete_on_termination": ni.delete_on_termination
        }
        
        if ni.private_ip:
            config["private_ip"] = ni.private_ip
            
        return config

    def _to_aws_config(self) -> Dict[str, Any]:
        """Convert to AWS EC2 configuration"""
        return {
            "resource_type": "aws_instance"
        }
        
    # Fluent interface methods
    
    # Basic configuration
    
    def ami(self, ami_id: str) -> Self:
        """Set AMI ID (chainable)"""
        self.spec.ami_id = ami_id
        return self
        
    # Operating System convenience methods
    
    def ubuntu(self, version: str = "22.04") -> Self:
        """Use Ubuntu AMI (chainable)"""
        # These would be resolved by the provider to latest AMI IDs
        version_map = {
            "20.04": "ubuntu-focal",
            "22.04": "ubuntu-jammy", 
            "24.04": "ubuntu-noble"
        }
        ami_pattern = version_map.get(version, f"ubuntu-{version}")
        self.spec.provider_config["ami_pattern"] = ami_pattern
        return self
        
    def amazon_linux(self, version: str = "2") -> Self:
        """Use Amazon Linux AMI (chainable)"""
        if version == "2":
            ami_pattern = "amzn2-ami-hvm-*-x86_64-gp2"
        elif version == "2023":
            ami_pattern = "al2023-ami-*-x86_64"
        else:
            ami_pattern = f"amzn-ami-hvm-{version}*-x86_64-gp2"
        self.spec.provider_config["ami_pattern"] = ami_pattern
        return self
        
    def debian(self, version: str = "11") -> Self:
        """Use Debian AMI (chainable)"""
        version_map = {
            "10": "debian-10",
            "11": "debian-11", 
            "12": "debian-12"
        }
        ami_pattern = version_map.get(version, f"debian-{version}")
        self.spec.provider_config["ami_pattern"] = ami_pattern
        return self
        
    def centos(self, version: str = "7") -> Self:
        """Use CentOS AMI (chainable)"""
        ami_pattern = f"CentOS-{version}*-x86_64*"
        self.spec.provider_config["ami_pattern"] = ami_pattern
        return self
        
    def rhel(self, version: str = "8") -> Self:
        """Use Red Hat Enterprise Linux AMI (chainable)"""
        ami_pattern = f"RHEL-{version}*-x86_64*"
        self.spec.provider_config["ami_pattern"] = ami_pattern
        return self
        
    def windows(self, version: str = "2022") -> Self:
        """Use Windows Server AMI (chainable)"""
        version_map = {
            "2019": "Windows_Server-2019-English-Full-Base",
            "2022": "Windows_Server-2022-English-Full-Base"
        }
        ami_pattern = version_map.get(version, f"Windows_Server-{version}-English-Full-Base")
        self.spec.provider_config["ami_pattern"] = ami_pattern
        return self
        
    def custom_image(self, ami_id: str) -> Self:
        """Use custom AMI (chainable)"""
        return self.ami(ami_id)
        
    def instance_type(self, instance_type: Union[str, InstanceType]) -> Self:
        """Set instance type (chainable)"""
        if isinstance(instance_type, str):
            # Try to find matching enum, otherwise use custom type
            try:
                self.spec.instance_type = InstanceType(instance_type)
            except ValueError:
                # Store as string for custom instance types
                self.spec.instance_type = instance_type
        else:
            self.spec.instance_type = instance_type
        return self
        
    def key_pair(self, key_name: str) -> Self:
        """Set EC2 key pair (chainable)"""
        self.spec.key_name = key_name
        return self
        
    def ssh_key(self, key_name: str) -> Self:
        """Set SSH key pair (Rails-like alias) (chainable)"""
        return self.key_pair(key_name)
        
    def ssh_keys(self, key_names: List[str]) -> Self:
        """Set multiple SSH keys (uses first one, stores others in tags) (chainable)"""
        if key_names:
            self.key_pair(key_names[0])
            if len(key_names) > 1:
                self.tag("AdditionalSSHKeys", ",".join(key_names[1:]))
        return self
        
    # Instance type conveniences
    
    def burstable(self, size: str = "micro") -> Self:
        """Use burstable performance instance (chainable)"""
        type_map = {
            "nano": InstanceType.T3_NANO,
            "micro": InstanceType.T3_MICRO,
            "small": InstanceType.T3_SMALL,
            "medium": InstanceType.T3_MEDIUM,
            "large": InstanceType.T3_LARGE,
            "xlarge": InstanceType.T3_XLARGE,
            "2xlarge": InstanceType.T3_2XLARGE
        }
        self.spec.instance_type = type_map.get(size, InstanceType.T3_MICRO)
        return self
        
    def general_purpose(self, size: str = "large") -> Self:
        """Use general purpose instance (chainable)"""
        if isinstance(size, str) and not size.startswith("m5."):
            size = f"m5.{size}"
        return self.instance_type(size)
        
    def compute_optimized(self, size: str = "large") -> Self:
        """Use compute-optimized instance (chainable)"""
        if isinstance(size, str) and not size.startswith("c5."):
            size = f"c5.{size}"
        return self.instance_type(size)
        
    def memory_optimized(self, size: str = "large") -> Self:
        """Use memory-optimized instance (chainable)"""
        if isinstance(size, str) and not size.startswith("r5."):
            size = f"r5.{size}"
        return self.instance_type(size)
        
    def storage_optimized(self, size: str = "large") -> Self:
        """Use storage-optimized instance (chainable)"""
        if isinstance(size, str) and not size.startswith("i3."):
            size = f"i3.{size}"
        return self.instance_type(size)
        
    # Network configuration
    
    def subnet(self, subnet_id: str) -> Self:
        """Set subnet (chainable)"""
        self.spec.subnet_id = subnet_id
        return self
        
    def private_subnet(self, subnet_id: str) -> Self:
        """Set private subnet (no public IP) (chainable)"""
        self.spec.subnet_id = subnet_id
        self.spec.associate_public_ip_address = False
        return self
        
    def public_subnet(self, subnet_id: str) -> Self:
        """Set public subnet with public IP (chainable)"""
        self.spec.subnet_id = subnet_id
        self.spec.associate_public_ip_address = True
        return self
        
    def security_groups(self, sg_ids: List[str]) -> Self:
        """Set security groups (chainable)"""
        self.spec.security_group_ids = sg_ids.copy()
        return self
        
    def security_group(self, sg_id: str) -> Self:
        """Add security group (chainable)"""
        if sg_id not in self.spec.security_group_ids:
            self.spec.security_group_ids.append(sg_id)
        return self
        
    def public_ip(self, enabled: bool = True) -> Self:
        """Enable/disable public IP (chainable)"""
        self.spec.associate_public_ip_address = enabled
        return self
        
    def private_ip(self, ip_address: str) -> Self:
        """Set private IP address (chainable)"""
        self.spec.private_ip = ip_address
        return self
        
    def elastic_ip(self, allocate: bool = True) -> Self:
        """Allocate and associate Elastic IP (chainable)"""
        # Enable public IP first
        self.public_ip(True)
        
        # Store in provider config for the provider to handle EIP allocation
        self.spec.provider_config["allocate_elastic_ip"] = allocate
        self.tag("ElasticIP", "allocated" if allocate else "none")
        
        return self
        
    def availability_zone(self, az: str) -> Self:
        """Set availability zone (chainable)"""
        self.spec.availability_zone = az
        return self
        
    # Storage configuration
    
    def root_volume(self, size: int, volume_type: str = "gp3", encrypted: bool = True) -> Self:
        """Configure root volume (chainable)"""
        self.spec.root_volume_size = size
        self.spec.root_volume_type = EBSVolumeType(volume_type)
        self.spec.root_encrypted = encrypted
        return self
        
    def additional_volume(self, device: str, size: int, volume_type: str = "gp3",
                         iops: int = None, encrypted: bool = True) -> Self:
        """Add additional EBS volume (chainable)"""
        volume = EBSBlockDevice(
            device_name=device,
            volume_size=size,
            volume_type=EBSVolumeType(volume_type),
            iops=iops,
            encrypted=encrypted
        )
        self.spec.additional_volumes.append(volume)
        return self
        
    def ebs_volume(self, name: str, size: int = 20, volume_type: str = "gp3",
                   iops: int = None, encrypted: bool = True) -> Self:
        """Add EBS volume with Rails-like naming (chainable)"""
        # Auto-generate device name based on the number of existing volumes
        device_name = f"/dev/sd{chr(98 + len(self.spec.additional_volumes))}"  # /dev/sdb, /dev/sdc, etc.
        
        volume = EBSBlockDevice(
            device_name=device_name,
            volume_size=size,
            volume_type=EBSVolumeType(volume_type),
            iops=iops,
            encrypted=encrypted
        )
        self.spec.additional_volumes.append(volume)
        
        # Tag the volume with the friendly name for reference
        self.tag(f"Volume-{name}", device_name)
        
        return self
        
    def high_performance_volume(self, device: str, size: int, iops: int, 
                               volume_type: str = "io2") -> Self:
        """Add high-performance volume (chainable)"""
        return self.additional_volume(device, size, volume_type, iops, True)
        
    # Disk convenience methods (Rails-like)
    
    def disk(self, size_gb: int, disk_type: str = "gp3") -> Self:
        """Add additional disk (chainable)"""
        device_name = f"/dev/sd{chr(98 + len(self.spec.additional_volumes))}"  # /dev/sdb, /dev/sdc, etc.
        return self.additional_volume(device_name, size_gb, disk_type)
        
    def add_disk(self, size_gb: int, mount_point: str = None, disk_type: str = "gp3") -> Self:
        """Add additional disk with optional mount point (chainable)"""
        disk_config = self.disk(size_gb, disk_type)
        if mount_point:
            # Store mount point in tags for the user data script to handle
            self.tag(f"MountPoint-{len(self.spec.additional_volumes)}", mount_point)
        return disk_config
        
    def ssd_disk(self, size_gb: int) -> Self:
        """Add SSD disk (chainable)"""
        return self.disk(size_gb, "gp3")
        
    def nvme_disk(self, size_gb: int) -> Self:
        """Add NVMe SSD disk (chainable)"""
        return self.disk(size_gb, "gp3")  # gp3 is NVMe-based
        
    # User data
    
    def user_data(self, script: str) -> Self:
        """Set user data script (chainable)"""
        self.spec.user_data = script
        self.spec.user_data_file = ""
        return self
        
    def user_data_file(self, file_path: str) -> Self:
        """Set user data from file (chainable)"""
        self.spec.user_data_file = file_path
        self.spec.user_data = ""
        return self
        
    def bootstrap_script(self, script: str) -> Self:
        """Add bootstrap script (chainable)"""
        return self.user_data(script)
        
    def startup_script(self, script_or_path: str) -> Self:
        """Set startup script from string or file (chainable)"""
        if script_or_path.endswith(('.sh', '.ps1', '.py', '.yml', '.yaml')):
            return self.user_data_file(script_or_path)
        else:
            return self.user_data(script_or_path)
        
    # Instance configuration
    
    def disable_termination(self, disabled: bool = True) -> Self:
        """Disable API termination (chainable)"""
        self.spec.disable_api_termination = disabled
        return self
        
    def shutdown_behavior(self, behavior: str) -> Self:
        """Set shutdown behavior: stop or terminate (chainable)"""
        if behavior not in ["stop", "terminate"]:
            raise ValueError("Shutdown behavior must be 'stop' or 'terminate'")
        self.spec.instance_initiated_shutdown_behavior = behavior
        return self
        
    def dedicated_tenancy(self) -> Self:
        """Use dedicated tenancy (chainable)"""
        self.spec.tenancy = Tenancy.DEDICATED
        return self
        
    def placement_group(self, group_name: str) -> Self:
        """Set placement group (chainable)"""
        self.spec.placement_group = group_name
        return self
        
    # Monitoring and IAM
    
    def monitoring(self, enabled: bool = True) -> Self:
        """Enable detailed monitoring (chainable)"""
        self.spec.enable_monitoring = enabled
        return self
        
    def iam_role(self, role_name: str) -> Self:
        """Set IAM instance profile (chainable)"""
        self.spec.iam_instance_profile = role_name
        return self
        
    # Metadata configuration
    
    def imdsv2_required(self) -> Self:
        """Require IMDSv2 (chainable)"""
        self.spec.metadata_options = {
            "http_endpoint": "enabled",
            "http_tokens": "required",
            "http_put_response_hop_limit": 1
        }
        return self
        
    def imdsv2_optional(self) -> Self:
        """Allow IMDSv1 and IMDSv2 (chainable)"""
        self.spec.metadata_options = {
            "http_endpoint": "enabled",
            "http_tokens": "optional",
            "http_put_response_hop_limit": 2
        }
        return self
        
    # Tags
    
    def tag(self, key: str, value: str) -> Self:
        """Add a tag (chainable)"""
        self.spec.tags[key] = value
        return self
        
    def tags(self, tags_dict: Dict[str, str] = None, **tags) -> Self:
        """Set multiple tags (chainable)"""
        if tags_dict:
            self.spec.tags.update(tags_dict)
        if tags:
            self.spec.tags.update(tags)
        return self
        
    def environment(self, env: str) -> Self:
        """Set environment tag (chainable)"""
        self.spec.tags["Environment"] = env
        # Also update metadata for filtering
        self.metadata.environment = env
        return self
        
    # Environment-based conveniences
    
    def production(self) -> Self:
        """Configure for production environment (chainable)"""
        return (self
                .disable_termination()
                .monitoring()
                .imdsv2_required()
                .root_volume(50, "gp3", True)
                .tag("Environment", "production")
                .tag("Backup", "required")
                .tag("Monitoring", "enabled"))
                
    def staging(self) -> Self:
        """Configure for staging environment (chainable)"""
        return (self
                .monitoring()
                .imdsv2_required()
                .root_volume(30, "gp3", True)
                .tag("Environment", "staging")
                .tag("Backup", "optional"))
                
    def development(self) -> Self:
        """Configure for development environment (chainable)"""
        return (self
                .burstable("small")
                .imdsv2_optional()
                .tag("Environment", "development")
                .tag("AutoShutdown", "enabled"))
                
    # Common server types
    
    def web_server(self, size: str = "medium") -> Self:
        """Configure as web server (chainable)"""
        return (self
                .burstable(size)
                .public_ip()
                .user_data("#!/bin/bash\nyum update -y\nyum install -y httpd\nsystemctl start httpd\nsystemctl enable httpd"))
                
    def database_server(self, size: str = "xlarge") -> Self:
        """Configure as database server (chainable)"""
        return (self
                .memory_optimized(size)
                .additional_volume("/dev/sdf", 100, "gp3")
                .disable_termination()
                .private_subnet(self.spec.subnet_id))
                
    def application_server(self, size: str = "large") -> Self:
        """Configure as application server (chainable)"""
        return (self
                .compute_optimized(size)
                .monitoring()
                .iam_role("app-server-role"))
                
    # Provider implementation methods
    
    def _provider_create(self) -> Dict[str, Any]:
        """Create the EC2 instance via provider"""
        if not self._provider:
            raise ValueError("No provider attached")
        
        from typing import cast
        provider = cast("ProviderInterface", self._provider)
        
        config = self._to_provider_config()
        resource_type = config.pop("resource_type")
        
        return provider.create_resource(
            resource_type=resource_type, config=config, metadata=self.metadata
        )

    def _provider_update(self, diff: Dict[str, Any]) -> Dict[str, Any]:
        """Update the EC2 instance via provider"""
        if not self._provider:
            raise ValueError("No provider attached")
        
        if not self.status.cloud_id:
            raise ValueError("Resource has no cloud ID")
        
        from typing import cast
        provider = cast("ProviderInterface", self._provider)
        
        config = self._to_provider_config()
        resource_type = config.pop("resource_type")
        
        return provider.update_resource(
            resource_id=self.status.cloud_id, resource_type=resource_type, updates=diff
        )

    def _provider_destroy(self) -> None:
        """Destroy the EC2 instance via provider"""
        if not self._provider:
            raise ValueError("No provider attached")
        
        if not self.status.cloud_id:
            raise ValueError("Resource has no cloud ID")
        
        from typing import cast
        provider = cast("ProviderInterface", self._provider)
        
        config = self._to_provider_config()
        resource_type = config.pop("resource_type")
        
        provider.delete_resource(
            resource_id=self.status.cloud_id, resource_type=resource_type
        )
        
    # Convenience methods
    
    def get_instance_type(self) -> str:
        """Get instance type"""
        return self.spec.instance_type.value if isinstance(self.spec.instance_type, InstanceType) else str(self.spec.instance_type)
        
    def is_root_encrypted(self) -> bool:
        """Check if root volume is encrypted"""
        return self.spec.root_encrypted
        
    def get_subnet_id(self) -> str:
        """Get subnet ID"""
        return self.spec.subnet_id
        
    def get_security_groups(self) -> List[str]:
        """Get security group IDs"""
        return self.spec.security_group_ids.copy()
        
    def has_public_ip(self) -> bool:
        """Check if instance has public IP"""
        return self.spec.associate_public_ip_address is True
        
    def get_volumes(self) -> Dict[str, Any]:
        """Get all volume configurations"""
        return {
            "root": {
                "size": self.spec.root_volume_size,
                "type": self.spec.root_volume_type.value,
                "encrypted": self.spec.root_encrypted
            },
            "additional": [
                {
                    "device": vol.device_name,
                    "size": vol.volume_size,
                    "type": vol.volume_type.value,
                    "encrypted": vol.encrypted
                }
                for vol in self.spec.additional_volumes
            ]
        }