"""
DigitalOcean Factory Class
"""

from typing import Any, Dict, Optional
from ...core.interfaces.provider import ProviderType, ProviderConfig
from ...core.exceptions import ProviderException


class DigitalOcean:
    """
    DigitalOcean provider factory for creating resources.

    Usage:
        vm = DigitalOcean.Droplet("my-vm").ubuntu().create()
    """

    _default_config: Optional[ProviderConfig] = None

    @classmethod
    def configure(
        cls,
        region: str = "nyc1",
        credentials: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        """Configure DigitalOcean provider defaults"""
        cls._default_config = ProviderConfig(
            type=ProviderType.DIGITAL_OCEAN,
            region=region,
            credentials=credentials,
            options=kwargs,
        )

    @classmethod
    def _get_provider(cls):
        """Get DigitalOcean provider instance"""
        # Auto-load .env file if it exists - Rails way!
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            pass  # dotenv is optional but recommended
        
        if not cls._default_config:
            # Get token from environment
            import os
            token = os.getenv("DIGITALOCEAN_TOKEN")
# Debug removed
            if not token:
                raise ProviderException(
                    "DigitalOcean token not found. Set DIGITALOCEAN_TOKEN environment variable."
                )
            
            # Use default configuration with token
            cls._default_config = ProviderConfig(
                type=ProviderType.DIGITAL_OCEAN, 
                region="nyc1",
                credentials={"token": token}
            )

        # Import here to avoid circular dependency
        from ...core.nexus.provider_registry import get_registry

        registry = get_registry()
        return registry.create_provider(ProviderType.DIGITAL_OCEAN, cls._default_config)

    @classmethod
    def Droplet(cls, name: str):
        """Create a DigitalOcean Droplet"""
        from ...resources.compute.virtual_machine import VirtualMachine

        vm = VirtualMachine(name)
        provider = cls._get_provider()
        vm._provider = provider
        return vm

    @classmethod
    def VM(cls, name: str):
        """Alias for Droplet"""
        return cls.Droplet(name)

    @classmethod
    def Instance(cls, name: str):
        """Alias for Droplet"""
        return cls.Droplet(name)
