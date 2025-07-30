"""
Enhanced Provider Registry with Marketplace Support

This module extends the basic provider registry with semantic versioning,
compatibility checking, and marketplace integration features.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Type, Set, Tuple, Any
from packaging import version
from packaging.specifiers import SpecifierSet, InvalidSpecifier

from infradsl.core.nexus.provider_registry import (
    ProviderRegistry,
    ProviderMetadata,
    ProviderCapability,
)
from infradsl.core.interfaces.provider import ProviderInterface, ProviderType

logger = logging.getLogger(__name__)


@dataclass
class VersionRequirement:
    """Represents a version requirement for dependencies"""
    provider: str
    version_spec: str  # e.g., ">=1.0.0,<2.0.0"
    optional: bool = False
    
    def matches(self, version_str: str) -> bool:
        """Check if a version matches the requirement"""
        try:
            spec = SpecifierSet(self.version_spec)
            return version.parse(version_str) in spec
        except (InvalidSpecifier, version.InvalidVersion):
            return False


@dataclass
class ProviderInfo:
    """Extended provider information with versioning and dependencies"""
    metadata: ProviderMetadata
    provider_class: Type[ProviderInterface]
    version: str
    dependencies: List[VersionRequirement] = field(default_factory=list)
    conflicts: List[VersionRequirement] = field(default_factory=list)
    changelog: Dict[str, List[str]] = field(default_factory=dict)
    security_verified: bool = False
    signature: Optional[str] = None
    published_at: Optional[datetime] = None
    downloads: int = 0
    rating: float = 0.0
    license: str = "MIT"
    homepage: Optional[str] = None
    repository: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    @property
    def semver(self) -> version.Version:
        """Get parsed semantic version"""
        return version.parse(self.version)
    
    def is_compatible_with(self, other: "ProviderInfo") -> bool:
        """Check if this provider is compatible with another"""
        # Check if this provider conflicts with the other
        for conflict in self.conflicts:
            if conflict.provider == other.metadata.name:
                if conflict.matches(other.version):
                    return False
        
        # Check if the other provider conflicts with this one
        for conflict in other.conflicts:
            if conflict.provider == self.metadata.name:
                if conflict.matches(self.version):
                    return False
        
        return True


class EnhancedProviderRegistry(ProviderRegistry):
    """
    Enhanced provider registry with marketplace features
    
    Features:
    - Semantic versioning support
    - Dependency resolution
    - Compatibility checking
    - Provider security verification
    - Hot-reload capabilities
    - Marketplace integration
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        super().__init__()
        self.base_path = base_path or Path.home() / ".infradsl" / "providers"
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Enhanced storage for multiple versions
        self._provider_versions: Dict[str, Dict[str, ProviderInfo]] = {}
        self._active_versions: Dict[str, str] = {}  # provider_name -> active_version
        self._compatibility_cache: Dict[Tuple[str, str], bool] = {}
        
        # Security and verification
        self._trusted_publishers: Set[str] = set()
        self._security_reports: Dict[str, Dict[str, Any]] = {}
        
    def register_versioned(
        self,
        provider_info: ProviderInfo,
        activate: bool = True
    ) -> None:
        """Register a versioned provider"""
        provider_name = provider_info.metadata.name
        version_str = provider_info.version
        
        # Validate version format
        try:
            semver = version.parse(version_str)
        except version.InvalidVersion:
            raise ValueError(f"Invalid version format: {version_str}")
        
        # Initialize version storage
        if provider_name not in self._provider_versions:
            self._provider_versions[provider_name] = {}
        
        # Check for version conflicts
        if version_str in self._provider_versions[provider_name]:
            logger.warning(f"Provider {provider_name} v{version_str} already registered")
            return
        
        # Verify dependencies are available
        missing_deps = self._check_dependencies(provider_info.dependencies)
        if missing_deps:
            raise ValueError(
                f"Missing dependencies for {provider_name} v{version_str}: "
                f"{', '.join(missing_deps)}"
            )
        
        # Check compatibility with existing providers
        incompatible = self._check_compatibility(provider_info)
        if incompatible:
            raise ValueError(
                f"Provider {provider_name} v{version_str} conflicts with: "
                f"{', '.join(incompatible)}"
            )
        
        # Register the provider
        self._provider_versions[provider_name][version_str] = provider_info
        
        # Activate if requested and compatible
        if activate:
            self.activate_version(provider_name, version_str)
        
        logger.info(f"Registered provider {provider_name} v{version_str}")
        
    def activate_version(self, provider_name: str, version_str: str) -> None:
        """Activate a specific version of a provider"""
        if provider_name not in self._provider_versions:
            raise ValueError(f"Provider {provider_name} not found")
        
        if version_str not in self._provider_versions[provider_name]:
            raise ValueError(f"Version {version_str} not found for {provider_name}")
        
        provider_info = self._provider_versions[provider_name][version_str]
        
        # Register with base registry
        super().register(provider_info.provider_class, provider_info.metadata)
        
        # Track active version
        self._active_versions[provider_name] = version_str
        
        logger.info(f"Activated {provider_name} v{version_str}")
        
    def get_active_version(self, provider_name: str) -> Optional[str]:
        """Get the active version of a provider"""
        return self._active_versions.get(provider_name)
    
    def list_versions(self, provider_name: str) -> List[str]:
        """List all available versions of a provider"""
        if provider_name not in self._provider_versions:
            return []
        
        versions = list(self._provider_versions[provider_name].keys())
        # Sort by semantic version
        versions.sort(key=lambda v: version.parse(v), reverse=True)
        return versions
    
    def get_provider_info(
        self,
        provider_name: str,
        version_str: Optional[str] = None
    ) -> Optional[ProviderInfo]:
        """Get detailed information about a provider"""
        if provider_name not in self._provider_versions:
            return None
        
        if version_str is None:
            version_str = self._active_versions.get(provider_name)
            if version_str is None:
                # Get latest version
                versions = self.list_versions(provider_name)
                if versions:
                    version_str = versions[0]
                else:
                    return None
        
        return self._provider_versions[provider_name].get(version_str)
    
    def search_providers(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_rating: float = 0.0,
        resource_types: Optional[List[str]] = None
    ) -> List[ProviderInfo]:
        """Search for providers matching criteria"""
        results = []
        
        for provider_name, versions in self._provider_versions.items():
            # Get latest version for search
            latest_version = max(versions.keys(), key=lambda v: version.parse(v))
            provider_info = versions[latest_version]
            
            # Apply filters
            if query and query.lower() not in provider_name.lower():
                if not any(query.lower() in tag.lower() for tag in provider_info.tags):
                    continue
            
            if tags and not any(tag in provider_info.tags for tag in tags):
                continue
            
            if provider_info.rating < min_rating:
                continue
            
            if resource_types:
                provider_resources = set(provider_info.metadata.resource_types)
                if not any(rt in provider_resources for rt in resource_types):
                    continue
            
            results.append(provider_info)
        
        # Sort by rating and downloads
        results.sort(
            key=lambda p: (p.rating, p.downloads),
            reverse=True
        )
        
        return results
    
    def check_updates(self) -> Dict[str, str]:
        """Check for available updates for active providers"""
        updates = {}
        
        for provider_name, active_version in self._active_versions.items():
            versions = self.list_versions(provider_name)
            if versions and versions[0] != active_version:
                updates[provider_name] = f"{active_version} -> {versions[0]}"
        
        return updates
    
    def _check_dependencies(
        self,
        dependencies: List[VersionRequirement]
    ) -> List[str]:
        """Check if all dependencies are satisfied"""
        missing = []
        
        for dep in dependencies:
            if dep.optional:
                continue
            
            if dep.provider not in self._provider_versions:
                missing.append(f"{dep.provider} {dep.version_spec}")
                continue
            
            # Check if any version satisfies the requirement
            satisfied = False
            for version_str in self._provider_versions[dep.provider]:
                if dep.matches(version_str):
                    satisfied = True
                    break
            
            if not satisfied:
                missing.append(f"{dep.provider} {dep.version_spec}")
        
        return missing
    
    def _check_compatibility(self, provider_info: ProviderInfo) -> List[str]:
        """Check compatibility with existing providers"""
        incompatible = []
        
        for active_name, active_version in self._active_versions.items():
            if active_name == provider_info.metadata.name:
                continue
            
            active_info = self._provider_versions[active_name][active_version]
            
            # Check cache first
            cache_key = (
                f"{provider_info.metadata.name}@{provider_info.version}",
                f"{active_name}@{active_version}"
            )
            
            if cache_key in self._compatibility_cache:
                if not self._compatibility_cache[cache_key]:
                    incompatible.append(f"{active_name}@{active_version}")
                continue
            
            # Check compatibility
            compatible = provider_info.is_compatible_with(active_info)
            self._compatibility_cache[cache_key] = compatible
            
            if not compatible:
                incompatible.append(f"{active_name}@{active_version}")
        
        return incompatible
    
    def export_registry(self, path: Path) -> None:
        """Export registry state to file"""
        state = {
            "providers": {},
            "active_versions": self._active_versions,
            "trusted_publishers": list(self._trusted_publishers),
        }
        
        for provider_name, versions in self._provider_versions.items():
            state["providers"][provider_name] = {}
            for version_str, info in versions.items():
                state["providers"][provider_name][version_str] = {
                    "metadata": {
                        "name": info.metadata.name,
                        "provider_type": info.metadata.provider_type.value,
                        "version": info.metadata.version,
                        "author": info.metadata.author,
                        "description": info.metadata.description,
                        "resource_types": info.metadata.resource_types,
                        "regions": info.metadata.regions,
                    },
                    "version": info.version,
                    "dependencies": [
                        {
                            "provider": dep.provider,
                            "version_spec": dep.version_spec,
                            "optional": dep.optional,
                        }
                        for dep in info.dependencies
                    ],
                    "tags": info.tags,
                    "rating": info.rating,
                    "downloads": info.downloads,
                    "license": info.license,
                    "published_at": info.published_at.isoformat() if info.published_at else None,
                }
        
        with open(path, "w") as f:
            json.dump(state, f, indent=2)
    
    def import_registry(self, path: Path) -> None:
        """Import registry state from file"""
        with open(path, "r") as f:
            state = json.load(f)
        
        # Clear current state
        self._provider_versions.clear()
        self._active_versions.clear()
        self._trusted_publishers.clear()
        
        # Import trusted publishers
        self._trusted_publishers.update(state.get("trusted_publishers", []))
        
        # Import providers (Note: provider classes need to be re-registered)
        logger.info(f"Imported registry state from {path}")
        logger.warning(
            "Provider classes need to be re-registered after import"
        )


# Global enhanced registry instance
_enhanced_registry = None


def get_enhanced_registry() -> EnhancedProviderRegistry:
    """Get the global enhanced provider registry"""
    global _enhanced_registry
    if _enhanced_registry is None:
        _enhanced_registry = EnhancedProviderRegistry()
    return _enhanced_registry