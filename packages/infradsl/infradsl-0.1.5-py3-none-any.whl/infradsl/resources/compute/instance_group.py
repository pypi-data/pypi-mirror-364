from typing import Optional, Dict, Any, Self, List, TYPE_CHECKING

if TYPE_CHECKING:
    from infradsl.core.interfaces.provider import ProviderInterface
    from .virtual_machine import VirtualMachine

from dataclasses import dataclass, field
from enum import Enum

from ...core.nexus.base_resource import BaseResource, ResourceSpec


class UpdatePolicy(Enum):
    """Update policies for instance groups"""
    PROACTIVE = "PROACTIVE"
    OPPORTUNISTIC = "OPPORTUNISTIC"


class DistributionPolicy(Enum):
    """Distribution policies for instances across zones"""
    BALANCED = "BALANCED"
    ANY = "ANY"


@dataclass
class InstanceGroupSpec(ResourceSpec):
    """Specification for an instance group resource"""
    
    # Core configuration
    base_instance_name: str = "instance"
    target_size: int = 3
    zones: List[str] = field(default_factory=list)
    region: Optional[str] = None
    
    # Template reference
    instance_template: Optional[str] = None
    
    # Scaling configuration
    min_size: int = 1
    max_size: int = 10
    target_cpu_utilization: float = 0.6
    
    # Update configuration
    update_policy: UpdatePolicy = UpdatePolicy.PROACTIVE
    max_surge: int = 1
    max_unavailable: int = 1
    
    # Distribution
    distribution_policy: DistributionPolicy = DistributionPolicy.BALANCED
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InstanceTemplateSpec(ResourceSpec):
    """Specification for an instance template"""
    
    # VM configuration (from VirtualMachine)
    vm_config: Dict[str, Any] = field(default_factory=dict)
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class InstanceTemplate(BaseResource):
    """
    Instance template for creating identical VMs.
    
    Examples:
        # Create template from VM
        template = InstanceTemplate("web-template", vm)
        
        # Create template with config
        template = (InstanceTemplate("api-template")
                   .machine_type("e2-medium")
                   .ubuntu("22.04")
                   .startup_script("./setup.sh"))
    """
    
    def __init__(self, name: str, vm: Optional["VirtualMachine"] = None):
        super().__init__(name)
        self.spec: InstanceTemplateSpec = self._create_spec()
        
        # If VM provided, copy its configuration
        if vm:
            self.spec.vm_config = vm._to_gcp_config()
            
        # Store resource type in annotations for cache fingerprinting
        self.metadata.annotations["resource_type"] = "InstanceTemplate"
        
    def _create_spec(self) -> InstanceTemplateSpec:
        return InstanceTemplateSpec()
        
    def _validate_spec(self) -> None:
        """Validate instance template specification"""
        if not self.spec.vm_config:
            raise ValueError("Instance template requires VM configuration")
        
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        config = {
            "name": self.metadata.name,
            "tags": self.metadata.to_tags(),
        }

        # Provider-specific mappings
        if hasattr(self._provider, 'config') and hasattr(self._provider.config, 'type'):
            provider_type_str = self._provider.config.type.value.lower()
        else:
            provider_type_str = str(self._provider).lower()

        if provider_type_str == "gcp":
            config.update(self._to_gcp_config())

        # Apply provider-specific overrides
        config.update(self.spec.provider_config)

        return config

    def _to_gcp_config(self) -> Dict[str, Any]:
        """Convert to GCP instance template configuration"""
        config = {
            "resource_type": "instance_template",
            "properties": self.spec.vm_config
        }
        
        return config
        
    def with_provider(self, provider) -> Self:
        """Associate with provider (chainable)"""
        self._provider = provider
        return self

    def _provider_create(self) -> Dict[str, Any]:
        """Create the template via provider"""
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
        """Update the template via provider"""
        # Templates are immutable - recreation required
        raise NotImplementedError("Instance template updates not supported - recreation required")

    def _provider_destroy(self) -> None:
        """Destroy the template via provider"""
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


class InstanceGroup(BaseResource):
    """
    Managed instance group for scaling VMs.
    
    Examples:
        # Simple instance group
        group = (InstanceGroup("web-group")
                .template(template)
                .size(5)
                .zones(["us-central1-a", "us-central1-b"]))
        
        # Auto-scaling group
        group = (InstanceGroup("api-group")
                .template(template)
                .auto_scale(min_size=2, max_size=20, target_cpu=0.7))
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.spec: InstanceGroupSpec = self._create_spec()
        # Store resource type in annotations for cache fingerprinting
        self.metadata.annotations["resource_type"] = "InstanceGroup"
        
    def _create_spec(self) -> InstanceGroupSpec:
        return InstanceGroupSpec()
        
    def _validate_spec(self) -> None:
        """Validate instance group specification"""
        if not self.spec.instance_template:
            raise ValueError("Instance group requires an instance template")
            
        if self.spec.target_size < self.spec.min_size:
            raise ValueError("Target size cannot be less than min size")
            
        if self.spec.target_size > self.spec.max_size:
            raise ValueError("Target size cannot be greater than max size")
            
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        config = {
            "name": self.metadata.name,
            "base_instance_name": self.spec.base_instance_name,
            "target_size": self.spec.target_size,
            "instance_template": self.spec.instance_template,
            "tags": self.metadata.to_tags(),
        }

        # Provider-specific mappings
        if hasattr(self._provider, 'config') and hasattr(self._provider.config, 'type'):
            provider_type_str = self._provider.config.type.value.lower()
        else:
            provider_type_str = str(self._provider).lower()

        if provider_type_str == "gcp":
            config.update(self._to_gcp_config())

        # Apply provider-specific overrides
        config.update(self.spec.provider_config)

        return config

    def _to_gcp_config(self) -> Dict[str, Any]:
        """Convert to GCP managed instance group configuration"""
        config = {
            "resource_type": "instance_group_manager",
            "base_instance_name": self.spec.base_instance_name,
            "target_size": self.spec.target_size,
            "instance_template": self.spec.instance_template,
        }
        
        # Regional vs zonal
        if self.spec.region:
            config["resource_type"] = "region_instance_group_manager"
            config["region"] = self.spec.region
            config["distribution_policy_zones"] = self.spec.zones
        elif self.spec.zones:
            config["zone"] = self.spec.zones[0]  # Use first zone for zonal
            
        # Auto-scaling configuration
        if self.spec.max_size > self.spec.target_size:
            config["auto_scaling_policy"] = {
                "min_num_replicas": self.spec.min_size,
                "max_num_replicas": self.spec.max_size,
                "cpu_utilization": {
                    "target": self.spec.target_cpu_utilization
                }
            }
            
        # Update policy
        config["update_policy"] = {
            "type": self.spec.update_policy.value,
            "max_surge_fixed": self.spec.max_surge,
            "max_unavailable_fixed": self.spec.max_unavailable
        }

        return config
        
    # Fluent interface methods
    
    def template(self, instance_template: InstanceTemplate) -> Self:
        """Set instance template (chainable)"""
        self.spec.instance_template = instance_template.name
        
        # Use same provider as template
        if instance_template._provider:
            self._provider = instance_template._provider
            
        return self
        
    def size(self, target_size: int) -> Self:
        """Set target size (chainable)"""
        self.spec.target_size = target_size
        return self
        
    def zones(self, zone_list: List[str]) -> Self:
        """Set zones for distribution (chainable)"""
        self.spec.zones = zone_list
        
        # Extract region from first zone
        if zone_list:
            first_zone = zone_list[0]
            self.spec.region = "-".join(first_zone.split("-")[:-1])
            
        return self
        
    def region(self, region_name: str) -> Self:
        """Set region (makes it a regional instance group, chainable)"""
        self.spec.region = region_name
        return self
        
    def auto_scale(self, min_size: int = 1, max_size: int = 10, target_cpu: float = 0.6) -> Self:
        """Enable auto-scaling (chainable)"""
        self.spec.min_size = min_size
        self.spec.max_size = max_size
        self.spec.target_cpu_utilization = target_cpu
        
        # Adjust target size if needed
        if self.spec.target_size < min_size:
            self.spec.target_size = min_size
        elif self.spec.target_size > max_size:
            self.spec.target_size = max_size
            
        return self
        
    def update_policy(self, policy: UpdatePolicy, max_surge: int = 1, max_unavailable: int = 1) -> Self:
        """Set update policy (chainable)"""
        self.spec.update_policy = policy
        self.spec.max_surge = max_surge
        self.spec.max_unavailable = max_unavailable
        return self
        
    def base_name(self, name: str) -> Self:
        """Set base instance name (chainable)"""
        self.spec.base_instance_name = name
        return self
        
    def with_provider(self, provider) -> Self:
        """Associate with provider (chainable)"""
        self._provider = provider
        return self
        
    # Convenience methods
    
    def get_instances(self) -> List[Dict[str, Any]]:
        """Get list of instances in the group"""
        return self.status.provider_data.get("instances", [])
        
    def get_current_size(self) -> int:
        """Get current number of instances"""
        return len(self.get_instances())
        
    def is_stable(self) -> bool:
        """Check if group is stable (target size reached)"""
        return self.get_current_size() == self.spec.target_size

    def _provider_create(self) -> Dict[str, Any]:
        """Create the instance group via provider"""
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
        """Update the instance group via provider"""
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
        """Destroy the instance group via provider"""
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