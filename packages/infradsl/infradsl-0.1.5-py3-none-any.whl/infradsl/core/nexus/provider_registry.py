from typing import Dict, List, Type, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import importlib
import inspect
import logging
from typing import Iterator

try:
    from importlib.metadata import entry_points
except ImportError:
    from importlib_metadata import entry_points

from ..interfaces.provider import ProviderInterface, ProviderType, ProviderConfig
from ..exceptions import ProviderException


logger = logging.getLogger(__name__)


@dataclass
class ProviderCapability:
    """Describes a capability of a provider"""

    name: str
    version: str
    features: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)


@dataclass
class ProviderMetadata:
    """Metadata about a provider implementation"""

    name: str
    provider_type: ProviderType
    version: str
    author: str
    description: str
    capabilities: List[ProviderCapability] = field(default_factory=list)
    resource_types: List[str] = field(default_factory=list)
    regions: List[str] = field(default_factory=list)
    required_config: List[str] = field(default_factory=list)
    optional_config: List[str] = field(default_factory=list)


class ProviderRegistry:
    """
    Central registry for provider implementations.

    Responsibilities:
    - Register and manage provider implementations
    - Provider discovery and loading
    - Capability querying
    - Provider instantiation
    """

    def __init__(self):
        self._providers: Dict[ProviderType, Type[ProviderInterface]] = {}
        self._metadata: Dict[ProviderType, ProviderMetadata] = {}
        self._aliases: Dict[str, ProviderType] = {}
        self._load_callbacks: List[Callable[[ProviderType], None]] = []
        self._builtin_registered = False
        self._external_providers_loaded = False

        # Don't register built-in providers immediately to avoid circular imports

    def _ensure_builtin_providers(self) -> None:
        """Ensure built-in providers are registered"""
        if not self._builtin_registered:
            self._register_builtin_providers()
            self._builtin_registered = True

    def _ensure_external_providers(self) -> None:
        """Ensure external providers are discovered and loaded"""
        if not self._external_providers_loaded:
            self._discover_external_providers()
            self._external_providers_loaded = True

    def register(
        self, provider_class: Type[ProviderInterface], metadata: ProviderMetadata
    ) -> None:
        """Register a provider implementation"""
        provider_type = metadata.provider_type

        # Validate the provider class
        if not issubclass(provider_class, ProviderInterface):
            raise ProviderException(
                f"{provider_class.__name__} must inherit from ProviderInterface"
            )

        # Check required methods are implemented
        required_methods = [
            "_validate_config",
            "_initialize",
            "create_resource",
            "update_resource",
            "delete_resource",
            "get_resource",
            "list_resources",
            "tag_resource",
            "estimate_cost",
            "validate_config",
            "get_resource_types",
            "get_regions",
        ]

        for method in required_methods:
            if not hasattr(provider_class, method):
                raise ProviderException(
                    f"{provider_class.__name__} missing required method: {method}"
                )

        # Register the provider
        self._providers[provider_type] = provider_class
        self._metadata[provider_type] = metadata

        # Register aliases
        self._aliases[metadata.name.lower()] = provider_type
        self._aliases[provider_type.value.lower()] = provider_type

        logger.info(f"Registered provider: {metadata.name} ({provider_type.value})")

        # Notify callbacks
        for callback in self._load_callbacks:
            callback(provider_type)

    def get_provider_class(
        self, provider_type: ProviderType
    ) -> Type[ProviderInterface]:
        """Get a provider class by type"""
        self._ensure_builtin_providers()
        self._ensure_external_providers()
        if provider_type not in self._providers:
            raise ProviderException(f"Provider not found: {provider_type.value}")
        return self._providers[provider_type]

    def get_provider_by_name(self, name: str) -> Type[ProviderInterface]:
        """Get a provider class by name or alias"""
        self._ensure_builtin_providers()
        self._ensure_external_providers()
        name_lower = name.lower()

        # Check aliases
        if name_lower in self._aliases:
            provider_type = self._aliases[name_lower]
            return self._providers[provider_type]

        # Check direct type match
        try:
            provider_type = ProviderType(name_lower)
            return self.get_provider_class(provider_type)
        except ValueError:
            raise ProviderException(f"Provider not found: {name}")

    def create_provider(
        self, provider_type: ProviderType, config: ProviderConfig
    ) -> ProviderInterface:
        """Create a provider instance"""
        try:
            provider_class = self.get_provider_class(provider_type)

            # Validate required config
            metadata = self._metadata[provider_type]
            missing_config = []

            for required in metadata.required_config:
                # Check if the field exists directly on config
                if hasattr(config, required) and getattr(config, required) is not None:
                    continue
                # Check if the field exists in credentials
                elif (
                    config.credentials
                    and isinstance(config.credentials, dict)
                    and required in config.credentials
                    and config.credentials[required] is not None
                ):
                    continue
                else:
                    missing_config.append(required)

            if missing_config:
                raise ProviderException(
                    f"Missing required configuration for {provider_type.value}: "
                    f"{', '.join(missing_config)}"
                )

            # Check if caching is enabled
            import os
            cache_enabled = os.getenv("INFRADSL_CACHE_ENABLED", "false").lower() == "true"
            
            # If caching is enabled, try to use cached provider
            if cache_enabled:
                # Check if this provider has a cached version
                provider_name = provider_type.value.lower()
                cached_class_name = f"Cached{provider_class.__name__}"
                
                # Try to import the cached provider
                try:
                    if provider_name == "aws":
                        from ...providers.aws.cached_provider import CachedAWSProvider
                        return CachedAWSProvider(config)
                    elif provider_name == "gcp":
                        from ...providers.gcp.cached_provider import CachedGCPComputeProvider
                        return CachedGCPComputeProvider(config)
                    elif provider_name == "digitalocean":
                        from ...providers.digitalocean.cached_provider import CachedDigitalOceanProvider
                        return CachedDigitalOceanProvider(config)
                except ImportError:
                    # Cached provider not available, fall back to regular provider
                    logger.debug(f"Cached provider not available for {provider_name}, using regular provider")
            
            # Create regular provider instance
            return provider_class(config)
        except ProviderException as e:
            # Raise instead of returning a mock
            raise ProviderException(
                f"No provider registered for {provider_type.value}: {e}"
            )

    def list_providers(self) -> List[ProviderMetadata]:
        """List all registered providers"""
        self._ensure_builtin_providers()
        self._ensure_external_providers()
        return list(self._metadata.values())

    def get_metadata(self, provider_type: ProviderType) -> ProviderMetadata:
        """Get metadata for a provider"""
        if provider_type not in self._metadata:
            raise ProviderException(f"Provider not found: {provider_type.value}")
        return self._metadata[provider_type]

    def get_capabilities(self, provider_type: ProviderType) -> List[ProviderCapability]:
        """Get capabilities of a provider"""
        metadata = self.get_metadata(provider_type)
        return metadata.capabilities

    def supports_resource_type(
        self, provider_type: ProviderType, resource_type: str
    ) -> bool:
        """Check if a provider supports a resource type"""
        metadata = self.get_metadata(provider_type)
        return resource_type in metadata.resource_types

    def get_providers_for_resource(self, resource_type: str) -> List[ProviderType]:
        """Get all providers that support a resource type"""
        providers = []

        for provider_type, metadata in self._metadata.items():
            if resource_type in metadata.resource_types:
                providers.append(provider_type)

        return providers

    def on_provider_loaded(self, callback: Callable[[ProviderType], None]) -> None:
        """Register a callback for when providers are loaded"""
        self._load_callbacks.append(callback)

    def load_provider_module(self, module_path: str) -> None:
        """Dynamically load a provider module"""
        try:
            module = importlib.import_module(module_path)

            # Find provider classes in the module
            for name, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, ProviderInterface)
                    and obj != ProviderInterface
                ):

                    # Look for metadata
                    if hasattr(obj, "METADATA"):
                        self.register(obj, getattr(obj, "METADATA"))
                    else:
                        logger.warning(
                            f"Provider class {name} found but missing METADATA"
                        )

        except ImportError as e:
            raise ProviderException(
                f"Failed to load provider module {module_path}: {e}"
            )

    def _discover_external_providers(self) -> None:
        """Discover and load external providers via entry points"""
        try:
            # Look for providers registered via entry points
            for entry_point in entry_points(group="infradsl.providers"):
                try:
                    logger.info(f"Loading external provider: {entry_point.name}")
                    provider_class = entry_point.load()

                    if hasattr(provider_class, "METADATA"):
                        metadata = provider_class.METADATA
                        # Convert dict to ProviderMetadata if needed
                        if isinstance(metadata, dict):
                            metadata = ProviderMetadata(**metadata)
                        self.register(provider_class, metadata)
                        logger.info(
                            f"Successfully loaded external provider: {entry_point.name}"
                        )
                    else:
                        logger.warning(
                            f"External provider {entry_point.name} missing METADATA"
                        )
                except Exception as e:
                    logger.error(
                        f"Failed to load external provider {entry_point.name}: {e}"
                    )
                    continue

        except Exception as e:
            logger.error(f"Failed to discover external providers: {e}")

    def discover_providers_in_namespace(self, namespace: str) -> List[str]:
        """Discover providers in a specific namespace package"""
        discovered = []
        try:
            for entry_point in entry_points(group=namespace):
                try:
                    provider_class = entry_point.load()
                    if hasattr(provider_class, "METADATA"):
                        metadata = provider_class.METADATA
                        if isinstance(metadata, dict):
                            metadata = ProviderMetadata(**metadata)
                        self.register(provider_class, metadata)
                        discovered.append(entry_point.name)
                except Exception as e:
                    logger.error(f"Failed to load provider {entry_point.name}: {e}")
                    continue
        except Exception as e:
            logger.error(f"Failed to discover providers in namespace {namespace}: {e}")

        return discovered

    def _register_builtin_providers(self) -> None:
        """Register built-in provider implementations"""
        try:
            # Import and register DigitalOcean provider
            from ...providers.digitalocean import DigitalOceanProvider, METADATA

            # Convert METADATA dict to ProviderMetadata object
            metadata = ProviderMetadata(
                name=METADATA["name"],
                provider_type=METADATA["provider_type"],
                version=METADATA["version"],
                author=METADATA["author"],
                description=METADATA["description"],
                resource_types=METADATA["resource_types"],
                regions=METADATA["regions"],
                required_config=METADATA["required_config"],
                optional_config=METADATA["optional_config"],
            )

            self.register(DigitalOceanProvider, metadata)
        except ImportError as e:
            # Provider not available, skip registration
            logger.warning(f"Failed to import DigitalOcean provider: {e}")
        except Exception as e:
            # Other errors during registration
            logger.error(f"Failed to register DigitalOcean provider: {e}")

        # Register GCP provider
        try:
            from ...providers.gcp import GCPComputeProvider, METADATA

            # Convert METADATA dict to ProviderMetadata object
            metadata = ProviderMetadata(
                name=METADATA["name"],
                provider_type=METADATA["provider_type"],
                version=METADATA["version"],
                author=METADATA["author"],
                description=METADATA["description"],
                resource_types=METADATA["resource_types"],
                regions=METADATA["regions"],
                required_config=METADATA["required_config"],
                optional_config=METADATA["optional_config"],
            )
            self.register(GCPComputeProvider, metadata)
        except ImportError as e:
            # Provider not available, skip registration
            logger.warning(f"Failed to import GCP provider: {e}")
        except Exception as e:
            # Other errors during registration
            logger.error(f"Failed to register GCP provider: {e}")

        # Register AWS provider
        try:
            from ...providers.aws import AWSProvider, METADATA

            # Convert METADATA dict to ProviderMetadata object
            metadata = ProviderMetadata(
                name=METADATA["name"],
                provider_type=METADATA["provider_type"],
                version=METADATA["version"],
                author=METADATA["author"],
                description=METADATA["description"],
                resource_types=METADATA["resource_types"],
                regions=METADATA["regions"],
                required_config=METADATA["required_config"],
                optional_config=METADATA["optional_config"],
            )
            self.register(AWSProvider, metadata)
        except ImportError as e:
            # Provider not available, skip registration
            logger.warning(f"Failed to import AWS provider: {e}")
        except Exception as e:
            # Other errors during registration
            logger.error(f"Failed to register AWS provider: {e}")

    def validate_provider_config(
        self, provider_type: ProviderType, config: Dict[str, Any]
    ) -> List[str]:
        """Validate configuration for a provider without instantiating it"""
        metadata = self.get_metadata(provider_type)
        errors = []

        # Check required fields
        for required in metadata.required_config:
            if required not in config:
                errors.append(f"Missing required field: {required}")

        # Type validation would go here

        return errors


# Global registry instance
_registry = ProviderRegistry()


def get_registry() -> ProviderRegistry:
    """Get the global provider registry"""
    return _registry


def register_provider(
    provider_class: Type[ProviderInterface], metadata: ProviderMetadata
) -> None:
    """Register a provider with the global registry"""
    _registry.register(provider_class, metadata)


def get_provider(
    provider_type: ProviderType, config: ProviderConfig
) -> ProviderInterface:
    """Get a provider instance from the global registry"""
    return _registry.create_provider(provider_type, config)
