"""
Main state management engine for multi-cloud infrastructure

Orchestrates state discovery, storage, and reconciliation across multiple
cloud providers with a unified interface.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from .interfaces.state_discoverer import StateDiscoverer
from .interfaces.state_storage import StateStorage
from .discovery.factory import create_discoverer
from .storage.factory import create_storage
from ..interfaces.provider import ProviderInterface


logger = logging.getLogger(__name__)


class StateEngine:
    """
    Central state management engine for multi-cloud resources.

    Provides a unified interface for discovering, storing, and managing
    infrastructure state across multiple cloud providers.
    """

    def __init__(self, storage_backend: str = "memory"):
        """
        Initialize the state engine.

        Args:
            storage_backend: Storage backend type ("memory", "file", "database")
        """
        self.storage = create_storage(storage_backend)
        self.discoverers: Dict[str, StateDiscoverer] = {}
        self._logger = logger

    def register_provider(
        self, provider_name: str, provider: ProviderInterface
    ) -> None:
        """
        Register a cloud provider for state discovery.

        Args:
            provider_name: Name of the provider (e.g., "gcp", "digitalocean", "aws")
            provider: The provider implementation

        Raises:
            ValueError: If provider discovery implementation is not available
        """
        try:
            discoverer = create_discoverer(provider_name, provider)
            self.discoverers[provider_name] = discoverer
            self._logger.debug(
                f"Registered {provider_name} provider for state discovery"
            )
        except Exception as e:
            self._logger.warning(f"Failed to register {provider_name} provider: {e}")
            raise ValueError(f"Cannot register provider {provider_name}: {e}")

    def discover_all_resources(
        self,
        update_storage: bool = True,
        timeout: int = 30,
        use_cache: bool = True,
        include_unmanaged: bool = False,
    ) -> Dict[str, Any]:
        """
        Discover resources from all registered providers.

        Args:
            update_storage: Whether to update storage with discovered resources
            timeout: Timeout in seconds for each provider discovery
            use_cache: Whether to use cached results if available

        Returns:
            Dictionary mapping resource names to their discovered states
        """
        import signal
        import time

        # Check cache first if enabled
        if use_cache:
            cached_resources = self._check_cache()
            if cached_resources:
                self._logger.info(
                    f"Using cached resources: {len(cached_resources)} resources"
                )
                return cached_resources

        all_resources = {}
        discovery_summary = {"total_resources": 0, "providers_scanned": 0, "errors": []}

        self._logger.debug(
            f"Starting fresh discovery for {len(self.discoverers)} providers"
        )

        for provider_name, discoverer in self.discoverers.items():
            try:
                self._logger.debug(f"Discovering resources from {provider_name}")

                # Set up timeout handler
                def timeout_handler(signum, frame):
                    raise TimeoutError(
                        f"Provider {provider_name} discovery timed out after {timeout} seconds"
                    )

                # Set timeout for this provider
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout)

                try:
                    self._logger.debug(
                        f"Calling discover_resources for {provider_name} (include_unmanaged={include_unmanaged})"
                    )
                    resources = discoverer.discover_resources(
                        include_unmanaged=include_unmanaged
                    )
                    self._logger.debug(
                        f"Got {len(resources)} resources from {provider_name}"
                    )

                    for resource in resources:
                        resource_name = resource.get("name")
                        if resource_name:
                            # Resources are already normalized by discover_resources()
                            all_resources[resource_name] = resource

                            # Update storage if requested
                            if update_storage:
                                self.storage.set(resource_name, resource)

                    discovery_summary["providers_scanned"] += 1
                    self._logger.info(
                        f"Discovered {len(resources)} resources from {provider_name}"
                    )

                finally:
                    # Clear the timeout
                    signal.alarm(0)

            except TimeoutError as e:
                error_msg = f"Timeout discovering resources from {provider_name}: {e}"
                self._logger.error(error_msg)
                discovery_summary["errors"].append(error_msg)

            except Exception as e:
                error_msg = f"Error discovering resources from {provider_name}: {e}"
                self._logger.error(error_msg)
                discovery_summary["errors"].append(error_msg)

        discovery_summary["total_resources"] = len(all_resources)
        self._logger.info(
            f"Discovery complete: {discovery_summary['total_resources']} resources "
            f"from {discovery_summary['providers_scanned']} providers"
        )

        return all_resources

    def discover_provider_resources(self, provider_name: str) -> List[Dict[str, Any]]:
        """
        Discover resources from a specific provider.

        Args:
            provider_name: Name of the provider to query

        Returns:
            List of discovered resources from the provider

        Raises:
            ValueError: If provider is not registered
        """
        if provider_name not in self.discoverers:
            raise ValueError(f"Provider {provider_name} is not registered")

        discoverer = self.discoverers[provider_name]
        return discoverer.discover_resources()

    def get_resource_state(self, resource_name: str) -> Optional[Dict[str, Any]]:
        """
        Get current state of a specific resource.

        Args:
            resource_name: Name of the resource

        Returns:
            Resource state dictionary or None if not found
        """
        return self.storage.get(resource_name)

    def update_resource_state(self, resource_name: str, state: Dict[str, Any]) -> None:
        """
        Update state for a specific resource.

        Args:
            resource_name: Name of the resource
            state: Updated resource state
        """
        state["updated_at"] = datetime.utcnow().isoformat()
        self.storage.set(resource_name, state)

    def delete_resource_state(self, resource_name: str) -> bool:
        """
        Delete state for a specific resource.

        Args:
            resource_name: Name of the resource

        Returns:
            True if resource was deleted, False if not found
        """
        return self.storage.delete(resource_name)

    def list_all_resources(self) -> Dict[str, Dict[str, Any]]:
        """
        List all resources from storage.

        Returns:
            Dictionary mapping resource names to their states
        """
        return self.storage.list_all()

    def get_resources_by_provider(
        self, provider_name: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get all resources for a specific provider.

        Args:
            provider_name: Name of the provider

        Returns:
            Dictionary of resources from the provider
        """
        return self.storage.get_by_provider(provider_name)

    def get_registered_providers(self) -> List[str]:
        """
        Get list of registered provider names.

        Returns:
            List of registered provider names
        """
        return list(self.discoverers.keys())

    def get_resources_by_project(self, project_name: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all resources for a specific project.

        Args:
            project_name: Name of the project

        Returns:
            Dictionary of resources from the project
        """
        return self.storage.get_by_project(project_name)

    def get_resources_by_environment(
        self, environment: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get all resources for a specific environment.

        Args:
            environment: Environment name

        Returns:
            Dictionary of resources from the environment
        """
        return self.storage.get_by_environment(environment)

    def sync_state(self) -> Dict[str, Any]:
        """
        Synchronize storage with current cloud state.

        Discovers resources from all providers and updates storage,
        handling additions, updates, and removals.

        Returns:
            Sync summary with statistics
        """
        # Get current stored state
        stored_resources = self.storage.list_all()
        stored_names = set(stored_resources.keys())

        # Discover current cloud state
        discovered_resources = self.discover_all_resources(update_storage=False)
        discovered_names = set(discovered_resources.keys())

        # Calculate changes
        added = discovered_names - stored_names
        removed = stored_names - discovered_names
        potentially_updated = discovered_names & stored_names

        # Apply changes
        for name in added:
            self.storage.set(name, discovered_resources[name])

        for name in removed:
            self.storage.delete(name)

        updated_count = 0
        for name in potentially_updated:
            stored = stored_resources[name]
            discovered = discovered_resources[name]

            # Simple change detection - could be enhanced
            if stored.get("cloud_id") != discovered.get("cloud_id") or stored.get(
                "state"
            ) != discovered.get("state"):
                self.storage.set(name, discovered)
                updated_count += 1

        sync_summary = {
            "added": len(added),
            "removed": len(removed),
            "updated": updated_count,
            "total_resources": len(discovered_resources),
            "synced_at": datetime.utcnow().isoformat(),
        }

        self._logger.info(
            f"State sync complete: +{sync_summary['added']} "
            f"-{sync_summary['removed']} ~{sync_summary['updated']}"
        )

        return sync_summary

    def clear_all_state(self) -> None:
        """
        Clear all stored state.

        Warning: This will remove all resource state data.
        """
        self.storage.clear()
        self._logger.warning("All state data cleared")

    def _check_cache(self, max_age_seconds: int = 300) -> Dict[str, Any]:
        """
        Check if cached resources are available and valid.

        Args:
            max_age_seconds: Maximum age of cached data in seconds (default: 5 minutes)

        Returns:
            Dictionary of cached resources if valid, empty dict otherwise
        """
        try:
            cached_resources = self.storage.list_all()
            if not cached_resources:
                return {}

            # Check if cache is too old
            from datetime import datetime, timedelta

            current_time = datetime.utcnow()
            cache_valid = True

            # Check if any resource has a recent discovery timestamp
            for resource_name, resource_data in cached_resources.items():
                discovered_at = resource_data.get("discovered_at")
                if discovered_at:
                    try:
                        discovered_time = datetime.fromisoformat(
                            discovered_at.replace("Z", "+00:00")
                        )
                        if current_time - discovered_time > timedelta(
                            seconds=max_age_seconds
                        ):
                            cache_valid = False
                            break
                    except ValueError:
                        # Invalid datetime format, invalidate cache
                        cache_valid = False
                        break
                else:
                    # No discovery timestamp, invalidate cache
                    cache_valid = False
                    break

            if cache_valid:
                self._logger.info(
                    f"Cache is valid, returning {len(cached_resources)} cached resources"
                )
                return cached_resources
            else:
                self._logger.info("Cache is expired, will perform fresh discovery")
                return {}

        except Exception as e:
            self._logger.debug(f"Error checking cache: {e}")
            return {}
