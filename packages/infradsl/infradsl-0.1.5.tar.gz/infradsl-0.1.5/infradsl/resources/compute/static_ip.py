from typing import Optional, Dict, Any, Self, TYPE_CHECKING

if TYPE_CHECKING:
    from infradsl.core.interfaces.provider import ProviderInterface

from dataclasses import dataclass, field
from enum import Enum

from ...core.nexus.base_resource import BaseResource, ResourceSpec


class IPType(Enum):
    """IP address types"""
    EXTERNAL = "EXTERNAL"
    INTERNAL = "INTERNAL"


class NetworkTier(Enum):
    """Network service tiers for GCP"""
    PREMIUM = "PREMIUM"
    STANDARD = "STANDARD"


@dataclass
class StaticIPSpec(ResourceSpec):
    """Specification for a static IP address resource"""
    
    # Core configuration
    ip_type: IPType = IPType.EXTERNAL
    network_tier: NetworkTier = NetworkTier.PREMIUM
    region: Optional[str] = None
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class StaticIP(BaseResource):
    """
    Static IP address resource that works across cloud providers.
    
    Examples:
        # Simple external IP
        ip = StaticIP("web-ip").external().create()
        
        # Regional internal IP
        ip = (StaticIP("internal-lb-ip")
              .internal()
              .region("us-central1")
              .create())
        
        # Attach to VM
        vm.attach_ip(ip)
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.spec: StaticIPSpec = self._create_spec()
        # Store resource type in annotations for cache fingerprinting
        self.metadata.annotations["resource_type"] = "StaticIP"
        
    def _create_spec(self) -> StaticIPSpec:
        return StaticIPSpec()
        
    def _validate_spec(self) -> None:
        """Validate static IP specification"""
        if self.spec.ip_type == IPType.INTERNAL and not self.spec.region:
            raise ValueError("Internal IPs require a region")
            
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
            "ip_type": self.spec.ip_type.value,
            "region": self.spec.region,
            "tags": self.metadata.to_tags(),
        }

        # Provider-specific mappings
        if provider_type_str.lower() == "gcp":
            config.update(self._to_gcp_config())
        elif provider_type_str.lower() == "aws":
            config.update(self._to_aws_config())

        # Apply provider-specific overrides
        config.update(self.spec.provider_config)

        return config

    def _to_gcp_config(self) -> Dict[str, Any]:
        """Convert to GCP static IP configuration"""
        config = {
            "resource_type": "global_address" if self.spec.ip_type == IPType.EXTERNAL else "address",
            "address_type": self.spec.ip_type.value,
            "network_tier": self.spec.network_tier.value,
        }
        
        # Regional vs global
        if self.spec.ip_type == IPType.EXTERNAL and not self.spec.region:
            # Global external IP
            config["resource_type"] = "global_address"
        else:
            # Regional IP (external or internal)
            config["resource_type"] = "address"
            config["region"] = self.spec.region

        return config

    def _to_aws_config(self) -> Dict[str, Any]:
        """Convert to AWS Elastic IP configuration"""
        config = {
            "resource_type": "eip",
            "domain": "vpc",  # VPC by default
        }
        
        # AWS doesn't have internal static IPs in the same way
        if self.spec.ip_type == IPType.INTERNAL:
            raise ValueError("AWS doesn't support static internal IPs via EIP")

        return config
        
    # Fluent interface methods
    
    def external(self) -> Self:
        """Set as external/public IP (chainable)"""
        self.spec.ip_type = IPType.EXTERNAL
        return self
        
    def internal(self) -> Self:
        """Set as internal/private IP (chainable)"""
        self.spec.ip_type = IPType.INTERNAL
        return self
        
    def region(self, region_name: str) -> Self:
        """Set region for IP allocation (chainable)"""
        self.spec.region = region_name
        return self
        
    def premium_tier(self) -> Self:
        """Use premium network tier (GCP-specific, chainable)"""
        self.spec.network_tier = NetworkTier.PREMIUM
        return self
        
    def standard_tier(self) -> Self:
        """Use standard network tier (GCP-specific, chainable)"""
        self.spec.network_tier = NetworkTier.STANDARD
        return self
        
    def provider_override(self, **kwargs) -> Self:
        """Override provider-specific settings (chainable)"""
        self.spec.provider_config.update(kwargs)
        return self
        
    def with_provider(self, provider) -> Self:
        """Associate this IP with a specific provider instance (chainable)"""
        self._provider = provider
        return self
        
    # Integration methods
    
    def attach_to_vm(self, vm) -> Self:
        """Attach this static IP to a VM (chainable)"""
        # Update VM's network configuration to use this static IP
        if hasattr(vm, 'spec') and hasattr(vm.spec, 'provider_config'):
            if "network_interfaces" not in vm.spec.provider_config:
                vm.network()  # Set default network
            
            # Update the first network interface to use this static IP
            for interface in vm.spec.provider_config["network_interfaces"]:
                if "access_configs" in interface:
                    for access_config in interface["access_configs"]:
                        access_config["nat_ip"] = self.get_ip_address()
                        
        return self
        
    # Provider-specific implementations
    
    def _provider_create(self) -> Dict[str, Any]:
        """Create the static IP via provider"""
        if not self._provider:
            raise ValueError("No provider attached")

        if isinstance(self._provider, str):
            raise ValueError(
                f"Provider '{self._provider}' is not resolved to an actual provider instance."
            )

        from typing import cast
        provider = cast("ProviderInterface", self._provider)

        config = self._to_provider_config()
        resource_type = config.pop("resource_type")

        return provider.create_resource(
            resource_type=resource_type, config=config, metadata=self.metadata
        )

    def _provider_destroy(self) -> None:
        """Destroy the static IP via provider"""
        if not self._provider:
            raise ValueError("No provider attached")

        if isinstance(self._provider, str):
            raise ValueError(
                f"Provider '{self._provider}' is not resolved to an actual provider instance."
            )

        if not self.status.cloud_id:
            raise ValueError(
                "Resource has no cloud ID - cannot destroy a resource that hasn't been created"
            )

        from typing import cast
        provider = cast("ProviderInterface", self._provider)

        config = self._to_provider_config()
        resource_type = config.pop("resource_type")

        provider.delete_resource(
            resource_id=self.status.cloud_id, resource_type=resource_type
        )

    def _provider_update(self, diff: Dict[str, Any]) -> Dict[str, Any]:
        """Update the static IP via provider"""
        # Static IPs generally don't support many updates
        # Most changes require recreation
        raise NotImplementedError("Static IP updates not supported - recreation required")
        
    # Convenience methods
    
    def get_ip_address(self) -> Optional[str]:
        """Get the IP address value"""
        return self.status.provider_data.get("address")
        
    def is_attached(self) -> bool:
        """Check if IP is attached to a resource"""
        return bool(self.status.provider_data.get("users"))