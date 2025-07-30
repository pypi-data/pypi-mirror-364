from typing import List, Any
from ...core.templates.base import BaseTemplate, TemplateMetadata, TemplateContext


class GenericVMTemplate(BaseTemplate):
    """
    Generic Virtual Machine Template
    
    A flexible template for creating virtual machines across different cloud providers.
    Automatically selects the appropriate provider implementation (AWS EC2, GCP Compute Engine, etc.)
    based on the configured provider.
    
    Parameters:
        instance_type: Instance size/type (default: "medium")
        os: Operating system (ubuntu, amazon_linux, windows, etc.)
        disk_size: Root disk size in GB
        additional_disks: List of additional disk configurations
        ssh_keys: List of SSH key names
        security_groups: List of security group names
        startup_script: Path to startup script file
        tags: Dictionary of tags to apply
        
    Outputs:
        instance_id: The created instance ID
        public_ip: Public IP address (if assigned)
        private_ip: Private IP address
        dns_name: Public DNS name
        
    Examples:
        # Basic VM
        vm = Template.GenericVM("web-server")
        
        # Customized VM
        vm = (Template.GenericVM("app-server")
              .with_parameters(
                  instance_type="large",
                  os="ubuntu",
                  disk_size=100)
              .production())
              
        # Extended VM with database
        vm = (Template.GenericVM("full-stack")
              .extend("Database")
              .with_parameters(
                  instance_type="xlarge",
                  additional_disks=[{"size": 500, "type": "ssd"}])
              .production())
    """
    
    def _create_metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            name="GenericVM",
            version="1.0.0",
            description="Generic virtual machine template supporting multiple cloud providers",
            author="InfraDSL Team",
            category="compute",
            tags=["vm", "compute", "server", "generic"],
            providers=["aws", "gcp", "azure"],
            min_infradsl_version="1.0.0",
            parameters_schema={
                "type": "object",
                "properties": {
                    "instance_type": {
                        "type": "string", 
                        "default": "medium",
                        "description": "Instance size (micro, small, medium, large, xlarge)"
                    },
                    "os": {
                        "type": "string",
                        "default": "ubuntu",
                        "description": "Operating system (ubuntu, amazon_linux, windows, debian, centos)"
                    },
                    "os_version": {
                        "type": "string", 
                        "default": "latest",
                        "description": "OS version"
                    },
                    "disk_size": {
                        "type": "integer",
                        "default": 20, 
                        "description": "Root disk size in GB"
                    },
                    "additional_disks": {
                        "type": "array",
                        "default": [],
                        "description": "Additional disk configurations"
                    },
                    "ssh_keys": {
                        "type": "array",
                        "default": [],
                        "description": "SSH key names"
                    },
                    "security_groups": {
                        "type": "array", 
                        "default": [],
                        "description": "Security group names"
                    },
                    "subnet": {
                        "type": "string",
                        "description": "Subnet ID or name"
                    },
                    "assign_public_ip": {
                        "type": "boolean",
                        "default": True,
                        "description": "Assign public IP address"
                    },
                    "startup_script": {
                        "type": "string",
                        "description": "Startup script path or content"
                    },
                    "monitoring": {
                        "type": "boolean", 
                        "default": False,
                        "description": "Enable detailed monitoring"
                    },
                    "backup": {
                        "type": "boolean",
                        "default": False, 
                        "description": "Enable automatic backups"
                    },
                    "tags": {
                        "type": "object",
                        "default": {},
                        "description": "Resource tags"
                    }
                },
                "required": []
            },
            outputs_schema={
                "type": "object", 
                "properties": {
                    "instance_id": {"type": "string", "description": "Instance ID"},
                    "public_ip": {"type": "string", "description": "Public IP address"},
                    "private_ip": {"type": "string", "description": "Private IP address"},
                    "dns_name": {"type": "string", "description": "Public DNS name"},
                    "ssh_command": {"type": "string", "description": "SSH connection command"}
                }
            },
            examples=[
                {
                    "name": "Basic Web Server",
                    "description": "Simple web server with Ubuntu",
                    "code": '''vm = Template.GenericVM("web-server").with_parameters(
    instance_type="medium",
    os="ubuntu", 
    startup_script="install-nginx.sh"
).production()'''
                },
                {
                    "name": "Database Server", 
                    "description": "Database server with additional storage",
                    "code": '''db = Template.GenericVM("database").with_parameters(
    instance_type="large",
    os="ubuntu",
    additional_disks=[{"size": 500, "type": "ssd", "mount": "/var/lib/mysql"}],
    security_groups=["db-sg"],
    assign_public_ip=False,
    backup=True
).production()'''
                }
            ]
        )
        
    def build(self, context: TemplateContext) -> List[Any]:
        """Build the virtual machine resource"""
        # Determine provider and create appropriate VM resource
        provider_type = self._detect_provider(context)
        
        if provider_type == "aws":
            return self._build_aws_vm(context)
        elif provider_type == "gcp":
            return self._build_gcp_vm(context)
        elif provider_type == "azure":
            return self._build_azure_vm(context)
        else:
            raise ValueError(f"Unsupported provider: {provider_type}")
            
    def _detect_provider(self, context: TemplateContext) -> str:
        """Detect the target cloud provider"""
        # This would check the current provider configuration
        # For now, default to AWS
        return context.provider_configs.get("type", "aws")
        
    def _build_aws_vm(self, context: TemplateContext) -> List[Any]:
        """Build AWS EC2 instance"""
        from ...resources.aws.compute.ec2 import AWSEC2
        
        # Get parameters
        instance_type = context.parameters.get("instance_type", "medium")
        os_name = context.parameters.get("os", "ubuntu")
        os_version = context.parameters.get("os_version", "latest")
        disk_size = context.parameters.get("disk_size", 20)
        additional_disks = context.parameters.get("additional_disks", [])
        ssh_keys = context.parameters.get("ssh_keys", [])
        security_groups = context.parameters.get("security_groups", [])
        subnet = context.parameters.get("subnet")
        assign_public_ip = context.parameters.get("assign_public_ip", True)
        startup_script = context.parameters.get("startup_script")
        monitoring = context.parameters.get("monitoring", False)
        backup = context.parameters.get("backup", False)
        tags = context.parameters.get("tags", {})
        
        # Create EC2 instance
        vm = AWSEC2(context.name)
        
        # Configure instance type
        instance_type_map = {
            "micro": "t3.micro",
            "small": "t3.small", 
            "medium": "t3.medium",
            "large": "t3.large",
            "xlarge": "t3.xlarge",
            "2xlarge": "t3.2xlarge"
        }
        vm = vm.instance_type(instance_type_map.get(instance_type, instance_type))
        
        # Configure OS
        if os_name == "ubuntu":
            vm = vm.ubuntu(os_version if os_version != "latest" else "22.04")
        elif os_name == "amazon_linux":
            vm = vm.amazon_linux(os_version if os_version != "latest" else "2")
        elif os_name == "windows":
            vm = vm.windows(os_version if os_version != "latest" else "2022")
        elif os_name == "debian":
            vm = vm.debian(os_version if os_version != "latest" else "11")
        elif os_name == "centos":
            vm = vm.centos(os_version if os_version != "latest" else "7")
        
        # Configure storage
        vm = vm.root_volume(disk_size, "gp3", encrypted=True)
        
        # Add additional disks
        for i, disk in enumerate(additional_disks):
            disk_size = disk.get("size", 100)
            disk_type = disk.get("type", "gp3")
            mount_point = disk.get("mount")
            vm = vm.add_disk(disk_size, mount_point, disk_type)
            
        # Configure SSH keys
        if ssh_keys:
            vm = vm.ssh_keys(ssh_keys)
            
        # Configure security groups  
        if security_groups:
            vm = vm.security_groups(security_groups)
            
        # Configure networking
        if subnet:
            if assign_public_ip:
                vm = vm.public_subnet(subnet)
            else:
                vm = vm.private_subnet(subnet)
        else:
            vm = vm.public_ip(assign_public_ip)
            
        # Configure startup script
        if startup_script:
            vm = vm.startup_script(startup_script)
            
        # Configure monitoring
        if monitoring:
            vm = vm.monitoring()
            
        # Configure tags
        default_tags = {
            "Template": "GenericVM",
            "Environment": context.environment
        }
        default_tags.update(tags)
        vm = vm.tags(default_tags)
        
        # Apply environment-specific configuration
        if context.environment == "production":
            vm = vm.production()
        elif context.environment == "staging":
            vm = vm.staging()
        elif context.environment == "development":
            vm = vm.development()
            
        # Set outputs
        self.set_output("instance_id", f"${{{vm.name}.id}}")
        self.set_output("public_ip", f"${{{vm.name}.public_ip}}")  
        self.set_output("private_ip", f"${{{vm.name}.private_ip}}")
        self.set_output("dns_name", f"${{{vm.name}.public_dns}}")
        
        if ssh_keys:
            key_name = ssh_keys[0] if isinstance(ssh_keys, list) else ssh_keys
            self.set_output("ssh_command", f"ssh -i ~/.ssh/{key_name} ubuntu@${{{vm.name}.public_ip}}")
        
        return [vm]
        
    def _build_gcp_vm(self, context: TemplateContext) -> List[Any]:
        """Build GCP Compute Engine instance"""
        from ...resources.compute.virtual_machine import VirtualMachine
        
        # Get parameters
        instance_type = context.parameters.get("instance_type", "medium")
        os_name = context.parameters.get("os", "ubuntu")
        os_version = context.parameters.get("os_version", "latest")
        disk_size = context.parameters.get("disk_size", 20)
        additional_disks = context.parameters.get("additional_disks", [])
        ssh_keys = context.parameters.get("ssh_keys", [])
        startup_script = context.parameters.get("startup_script")
        tags = context.parameters.get("tags", {})
        
        # Create GCP VM
        vm = VirtualMachine(context.name)
        
        # Configure instance type
        instance_type_map = {
            "micro": "e2-micro",
            "small": "e2-small",
            "medium": "e2-medium", 
            "large": "e2-standard-4",
            "xlarge": "e2-standard-8"
        }
        vm = vm.custom_size(instance_type_map.get(instance_type, instance_type))
        
        # Configure OS
        if os_name == "ubuntu":
            vm = vm.ubuntu(os_version if os_version != "latest" else "22.04")
        elif os_name == "debian":
            vm = vm.debian(os_version if os_version != "latest" else "11")
        elif os_name == "centos":
            vm = vm.centos(os_version if os_version != "latest" else "7")
        elif os_name == "windows":
            vm = vm.windows(os_version if os_version != "latest" else "2022")
            
        # Configure storage
        vm = vm.disk(disk_size, "ssd")
        
        # Add additional disks
        for disk in additional_disks:
            disk_size = disk.get("size", 100)
            disk_type = disk.get("type", "ssd")
            mount_point = disk.get("mount")
            vm = vm.add_disk(disk_size, mount_point, disk_type)
            
        # Configure SSH keys
        if ssh_keys:
            vm = vm.ssh_keys(ssh_keys)
            
        # Configure startup script
        if startup_script:
            vm = vm.startup_script(startup_script)
            
        # Configure tags
        default_tags = {
            "template": "generic-vm",
            "environment": context.environment
        }
        default_tags.update(tags)
        vm = vm.tags(default_tags)
        
        # Apply environment configuration
        if context.environment == "production":
            vm = vm.production()
        elif context.environment == "staging":
            vm = vm.staging()
        elif context.environment == "development":
            vm = vm.development()
            
        # Set outputs (GCP-specific)
        self.set_output("instance_id", f"${{{vm.name}.instance_id}}")
        self.set_output("public_ip", f"${{{vm.name}.public_ip}}")
        self.set_output("private_ip", f"${{{vm.name}.private_ip}}")
        self.set_output("dns_name", f"${{{vm.name}.public_dns}}")
        
        return [vm]
        
    def _build_azure_vm(self, context: TemplateContext) -> List[Any]:
        """Build Azure Virtual Machine"""
        # TODO: Implement Azure VM creation
        raise NotImplementedError("Azure VM support coming soon")
        
    # Template-specific convenience methods
    
    def with_os(self, os_name: str, version: str = "latest"):
        """Convenience method to set OS (chainable)"""
        return self.with_parameters(os=os_name, os_version=version)
        
    def with_instance_type(self, instance_type: str):
        """Convenience method to set instance type (chainable)"""
        return self.with_parameters(instance_type=instance_type)
        
    def with_disk(self, size: int, disk_type: str = "ssd"):
        """Convenience method to set disk configuration (chainable)"""
        return self.with_parameters(disk_size=size, disk_type=disk_type)
        
    def with_ssh_key(self, *keys):
        """Convenience method to set SSH keys (chainable)"""
        return self.with_parameters(ssh_keys=list(keys))
        
    def with_startup_script(self, script_path: str):
        """Convenience method to set startup script (chainable)"""
        return self.with_parameters(startup_script=script_path)
        
    def with_monitoring(self, enabled: bool = True):
        """Convenience method to enable monitoring (chainable)"""
        return self.with_parameters(monitoring=enabled)
        
    def with_backup(self, enabled: bool = True):
        """Convenience method to enable backup (chainable)"""
        return self.with_parameters(backup=enabled)
        
    def public(self):
        """Convenience method for public IP (chainable)"""
        return self.with_parameters(assign_public_ip=True)
        
    def private(self):
        """Convenience method for private IP only (chainable)"""
        return self.with_parameters(assign_public_ip=False)