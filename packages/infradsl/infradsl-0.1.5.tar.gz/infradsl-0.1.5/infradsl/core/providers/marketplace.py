"""
Provider Marketplace - Publishing and Distribution System

This module implements the provider marketplace for discovering,
publishing, and installing InfraDSL providers.
"""

import hashlib
import json
import logging
import shutil
import tarfile
import tempfile
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, BinaryIO
from urllib.parse import urljoin
import aiohttp
import asyncio

from packaging import version

from .registry import ProviderInfo, EnhancedProviderRegistry, get_enhanced_registry
from .security import ProviderSecurityScanner, scan_provider

logger = logging.getLogger(__name__)


class PublishStatus(Enum):
    """Provider publication status"""

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PUBLISHED = "published"
    REJECTED = "rejected"
    DEPRECATED = "deprecated"


@dataclass
class ProviderVersion:
    """Represents a specific version of a provider package"""

    version: str
    release_notes: str
    published_at: datetime
    downloads: int = 0
    checksum: Optional[str] = None
    size_bytes: int = 0
    min_infradsl_version: Optional[str] = None
    max_infradsl_version: Optional[str] = None
    artifacts: Dict[str, str] = field(default_factory=dict)  # type -> url

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["published_at"] = self.published_at.isoformat()
        return data


@dataclass
class ProviderPackage:
    """Provider package metadata for marketplace"""

    name: str
    display_name: str
    author: str
    author_email: Optional[str]
    description: str
    long_description: Optional[str]
    homepage: Optional[str]
    repository: Optional[str]
    license: str
    tags: List[str]
    categories: List[str]
    provider_type: str
    resource_types: List[str]
    icon_url: Optional[str] = None
    screenshots: List[str] = field(default_factory=list)
    versions: Dict[str, ProviderVersion] = field(default_factory=dict)
    latest_version: Optional[str] = None
    total_downloads: int = 0
    rating: float = 0.0
    rating_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: PublishStatus = PublishStatus.DRAFT
    verified: bool = False
    featured: bool = False

    def get_latest_version(self) -> Optional[ProviderVersion]:
        """Get the latest version"""
        if not self.versions:
            return None

        if self.latest_version and self.latest_version in self.versions:
            return self.versions[self.latest_version]

        # Find latest by semantic version
        latest = max(self.versions.keys(), key=lambda v: version.parse(v))
        return self.versions[latest]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["status"] = self.status.value
        data["created_at"] = self.created_at.isoformat() if self.created_at else None
        data["updated_at"] = self.updated_at.isoformat() if self.updated_at else None
        data["versions"] = {v: ver.to_dict() for v, ver in self.versions.items()}
        return data


class ProviderMarketplace:
    """
    Provider marketplace for discovering and distributing providers

    Features:
    - Provider discovery and search
    - Package publishing and versioning
    - Security scanning and verification
    - Download statistics and ratings
    - Integration with package registries
    """

    def __init__(
        self,
        marketplace_url: Optional[str] = None,
        local_cache: Optional[Path] = None,
        registry: Optional[EnhancedProviderRegistry] = None,
    ):
        self.marketplace_url = marketplace_url or "https://marketplace.infradsl.dev"
        self.local_cache = local_cache or Path.home() / ".infradsl" / "marketplace"
        self.local_cache.mkdir(parents=True, exist_ok=True)

        self.registry = registry or get_enhanced_registry()
        self.security_scanner = ProviderSecurityScanner()

        # Local package store
        self.packages: Dict[str, ProviderPackage] = {}
        self._load_local_packages()

        # Session for API calls
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._session:
            await self._session.close()

    async def search(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        provider_type: Optional[str] = None,
        resource_types: Optional[List[str]] = None,
        min_rating: float = 0.0,
        verified_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ProviderPackage]:
        """Search for provider packages"""
        results = []

        # Search local packages first
        for package in self.packages.values():
            # Apply filters
            if query:
                query_lower = query.lower()
                if (
                    query_lower not in package.name.lower()
                    and query_lower not in package.display_name.lower()
                    and query_lower not in package.description.lower()
                ):
                    continue

            if tags and not any(tag in package.tags for tag in tags):
                continue

            if categories and not any(cat in package.categories for cat in categories):
                continue

            if provider_type and package.provider_type != provider_type:
                continue

            if resource_types:
                if not any(rt in package.resource_types for rt in resource_types):
                    continue

            if package.rating < min_rating:
                continue

            if verified_only and not package.verified:
                continue

            if package.status != PublishStatus.PUBLISHED:
                continue

            results.append(package)

        # Sort by relevance (rating * downloads)
        results.sort(
            key=lambda p: (
                p.rating * (p.total_downloads + 1),
                p.updated_at or datetime.min,
            ),
            reverse=True,
        )

        # Apply pagination
        return results[offset : offset + limit]

    async def get_package(self, name: str) -> Optional[ProviderPackage]:
        """Get a specific package by name"""
        # Check local cache
        if name in self.packages:
            return self.packages[name]

        # Try to fetch from marketplace
        try:
            if self._session:
                url = urljoin(self.marketplace_url, f"/api/packages/{name}")
                async with self._session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        package = self._package_from_dict(data)
                        self.packages[name] = package
                        self._save_local_packages()
                        return package
        except Exception as e:
            logger.error(f"Failed to fetch package {name}: {e}")

        return None

    async def publish_package(
        self,
        package_path: Path,
        metadata: Dict[str, Any],
        version_info: Dict[str, Any],
        dry_run: bool = False,
    ) -> ProviderPackage:
        """Publish a provider package"""
        # Validate package structure
        if not self._validate_package_structure(package_path):
            raise ValueError(f"Invalid package structure at {package_path}")

        # Run security scan
        security_report = await self.security_scanner.scan_directory(package_path)
        if security_report.has_critical_issues():
            raise ValueError(
                f"Security scan failed: {len(security_report.vulnerabilities)} vulnerabilities found"
            )

        # Create package metadata
        package = ProviderPackage(
            name=metadata["name"],
            display_name=metadata.get("display_name", metadata["name"]),
            author=metadata["author"],
            author_email=metadata.get("author_email"),
            description=metadata["description"],
            long_description=metadata.get("long_description"),
            homepage=metadata.get("homepage"),
            repository=metadata.get("repository"),
            license=metadata.get("license", "MIT"),
            tags=metadata.get("tags", []),
            categories=metadata.get("categories", []),
            provider_type=metadata["provider_type"],
            resource_types=metadata.get("resource_types", []),
            icon_url=metadata.get("icon_url"),
            screenshots=metadata.get("screenshots", []),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            status=PublishStatus.PENDING_REVIEW if not dry_run else PublishStatus.DRAFT,
        )

        # Create version
        version_obj = ProviderVersion(
            version=version_info["version"],
            release_notes=version_info.get("release_notes", ""),
            published_at=datetime.now(timezone.utc),
            min_infradsl_version=version_info.get("min_infradsl_version"),
            max_infradsl_version=version_info.get("max_infradsl_version"),
        )

        if not dry_run:
            # Create package archive
            archive_path = await self._create_package_archive(
                package_path, package.name, version_obj.version
            )

            # Calculate checksum
            version_obj.checksum = self._calculate_checksum(archive_path)
            version_obj.size_bytes = archive_path.stat().st_size

            # Store locally
            self._store_package_locally(package, version_obj, archive_path)

        # Add version to package
        package.versions[version_obj.version] = version_obj
        package.latest_version = version_obj.version

        # Save to local store
        self.packages[package.name] = package
        self._save_local_packages()

        logger.info(f"Published package {package.name} v{version_obj.version}")
        return package

    async def install_package(
        self,
        name: str,
        version_spec: Optional[str] = None,
        target_dir: Optional[Path] = None,
    ) -> ProviderInfo:
        """Install a provider package"""
        # Get package metadata
        package = await self.get_package(name)
        if not package:
            raise ValueError(f"Package {name} not found")

        # Resolve version
        if version_spec:
            target_version = self._resolve_version(package, version_spec)
            if not target_version:
                raise ValueError(f"No version matching {version_spec} for {name}")
        else:
            target_version = package.get_latest_version()
            if not target_version:
                raise ValueError(f"No versions available for {name}")

        # Check if already installed
        installed_info = self.registry.get_provider_info(name, target_version.version)
        if installed_info:
            logger.info(f"Package {name} v{target_version.version} already installed")
            return installed_info

        # Download package
        archive_path = await self._download_package(package, target_version)

        # Verify checksum
        if target_version.checksum:
            actual_checksum = self._calculate_checksum(archive_path)
            if actual_checksum != target_version.checksum:
                raise ValueError("Package checksum verification failed")

        # Extract and install
        install_dir = (
            target_dir or self.registry.base_path / name / target_version.version
        )
        install_dir.mkdir(parents=True, exist_ok=True)

        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(install_dir)

        # Load provider module
        provider_module = install_dir / "provider.py"
        if not provider_module.exists():
            raise ValueError("Provider module not found in package")

        # Import and register provider
        # This would normally use dynamic import
        logger.info(f"Installed {name} v{target_version.version} to {install_dir}")

        # Update download count
        target_version.downloads += 1
        package.total_downloads += 1
        self._save_local_packages()

        # Create provider info (mock for now)
        from infradsl.core.nexus.provider_registry import ProviderMetadata
        from infradsl.core.interfaces.provider import ProviderType

        provider_info = ProviderInfo(
            metadata=ProviderMetadata(
                name=package.name,
                provider_type=ProviderType.CUSTOM,
                version=target_version.version,
                author=package.author,
                description=package.description,
                resource_types=package.resource_types,
                capabilities=[],
                regions=[],
                required_config=[],
                optional_config=[],
            ),
            provider_class=None,  # Would be loaded dynamically
            version=target_version.version,
            license=package.license,
            homepage=package.homepage,
            repository=package.repository,
            tags=package.tags,
            published_at=target_version.published_at,
            downloads=target_version.downloads,
            rating=package.rating,
        )

        return provider_info

    def _validate_package_structure(self, package_path: Path) -> bool:
        """Validate provider package structure"""
        required_files = ["provider.py", "metadata.json", "README.md"]

        for file_name in required_files:
            if not (package_path / file_name).exists():
                logger.error(f"Missing required file: {file_name}")
                return False

        # Validate metadata
        try:
            with open(package_path / "metadata.json", "r") as f:
                metadata = json.load(f)

            required_fields = [
                "name",
                "version",
                "author",
                "description",
                "provider_type",
            ]
            for field in required_fields:
                if field not in metadata:
                    logger.error(f"Missing required metadata field: {field}")
                    return False

        except Exception as e:
            logger.error(f"Invalid metadata.json: {e}")
            return False

        return True

    async def _create_package_archive(
        self, package_path: Path, name: str, version: str
    ) -> Path:
        """Create a package archive"""
        archive_name = f"{name}-{version}.tar.gz"
        archive_path = self.local_cache / "archives" / archive_name
        archive_path.parent.mkdir(parents=True, exist_ok=True)

        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(package_path, arcname=name)

        return archive_path

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file"""
        sha256_hash = hashlib.sha256()

        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        return sha256_hash.hexdigest()

    def _store_package_locally(
        self, package: ProviderPackage, version: ProviderVersion, archive_path: Path
    ) -> None:
        """Store package archive locally"""
        local_dir = self.local_cache / "packages" / package.name / version.version
        local_dir.mkdir(parents=True, exist_ok=True)

        # Copy archive
        shutil.copy2(
            archive_path, local_dir / f"{package.name}-{version.version}.tar.gz"
        )

        # Store metadata
        with open(local_dir / "metadata.json", "w") as f:
            json.dump(package.to_dict(), f, indent=2)

    async def _download_package(
        self, package: ProviderPackage, version: ProviderVersion
    ) -> Path:
        """Download a package archive"""
        # Check local cache first
        local_archive = (
            self.local_cache
            / "packages"
            / package.name
            / version.version
            / f"{package.name}-{version.version}.tar.gz"
        )

        if local_archive.exists():
            return local_archive

        # Download from marketplace
        if self._session and "archive" in version.artifacts:
            url = version.artifacts["archive"]
            local_archive.parent.mkdir(parents=True, exist_ok=True)

            async with self._session.get(url) as response:
                if response.status == 200:
                    with open(local_archive, "wb") as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                    return local_archive

        raise ValueError(
            f"Failed to download package {package.name} v{version.version}"
        )

    def _resolve_version(
        self, package: ProviderPackage, version_spec: str
    ) -> Optional[ProviderVersion]:
        """Resolve version specification to specific version"""
        from packaging.specifiers import SpecifierSet

        try:
            spec = SpecifierSet(version_spec)

            # Find matching versions
            matching_versions = []
            for v_str, v_obj in package.versions.items():
                if version.parse(v_str) in spec:
                    matching_versions.append((v_str, v_obj))

            if not matching_versions:
                return None

            # Return latest matching version
            latest = max(matching_versions, key=lambda x: version.parse(x[0]))
            return latest[1]

        except Exception as e:
            logger.error(f"Invalid version spec {version_spec}: {e}")
            return None

    def _load_local_packages(self) -> None:
        """Load locally stored packages"""
        packages_dir = self.local_cache / "packages"
        if not packages_dir.exists():
            return

        for provider_dir in packages_dir.iterdir():
            if not provider_dir.is_dir():
                continue

            # Load latest version metadata
            versions = []
            for version_dir in provider_dir.iterdir():
                if version_dir.is_dir() and (version_dir / "metadata.json").exists():
                    versions.append(version_dir.name)

            if versions:
                latest = max(versions, key=lambda v: version.parse(v))
                metadata_file = provider_dir / latest / "metadata.json"

                try:
                    with open(metadata_file, "r") as f:
                        data = json.load(f)

                    package = self._package_from_dict(data)
                    self.packages[package.name] = package
                except Exception as e:
                    logger.error(f"Failed to load package {provider_dir.name}: {e}")

    def _save_local_packages(self) -> None:
        """Save package metadata to local cache"""
        index_file = self.local_cache / "index.json"

        index_data = {
            "packages": {name: pkg.to_dict() for name, pkg in self.packages.items()},
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        with open(index_file, "w") as f:
            json.dump(index_data, f, indent=2)

    def _package_from_dict(self, data: Dict[str, Any]) -> ProviderPackage:
        """Create package from dictionary"""
        package = ProviderPackage(
            name=data["name"],
            display_name=data["display_name"],
            author=data["author"],
            author_email=data.get("author_email"),
            description=data["description"],
            long_description=data.get("long_description"),
            homepage=data.get("homepage"),
            repository=data.get("repository"),
            license=data["license"],
            tags=data.get("tags", []),
            categories=data.get("categories", []),
            provider_type=data["provider_type"],
            resource_types=data.get("resource_types", []),
            icon_url=data.get("icon_url"),
            screenshots=data.get("screenshots", []),
            latest_version=data.get("latest_version"),
            total_downloads=data.get("total_downloads", 0),
            rating=data.get("rating", 0.0),
            rating_count=data.get("rating_count", 0),
            status=PublishStatus(data.get("status", "draft")),
            verified=data.get("verified", False),
            featured=data.get("featured", False),
        )

        # Parse dates
        if data.get("created_at"):
            package.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            package.updated_at = datetime.fromisoformat(data["updated_at"])

        # Parse versions
        for v_str, v_data in data.get("versions", {}).items():
            version_obj = ProviderVersion(
                version=v_data["version"],
                release_notes=v_data["release_notes"],
                published_at=datetime.fromisoformat(v_data["published_at"]),
                downloads=v_data.get("downloads", 0),
                checksum=v_data.get("checksum"),
                size_bytes=v_data.get("size_bytes", 0),
                min_infradsl_version=v_data.get("min_infradsl_version"),
                max_infradsl_version=v_data.get("max_infradsl_version"),
                artifacts=v_data.get("artifacts", {}),
            )
            package.versions[v_str] = version_obj

        return package


# Global marketplace instance
_marketplace = None


def get_marketplace() -> ProviderMarketplace:
    """Get the global provider marketplace instance"""
    global _marketplace
    if _marketplace is None:
        _marketplace = ProviderMarketplace()
    return _marketplace
