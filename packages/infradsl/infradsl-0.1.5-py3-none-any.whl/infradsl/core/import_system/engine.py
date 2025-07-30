"""
Core Import Engine for "Codify My Cloud" functionality

This module provides the main ImportEngine class that orchestrates the process
of discovering cloud resources and generating InfraDSL Python code.
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from collections import defaultdict

from .models import (
    ImportConfig,
    ImportResult,
    ImportStatus,
    CloudResource,
    DependencyGraph,
    ResourceType,
)
from .analyzer import ResourceAnalyzer
from .generator import CodeGenerator
from ..state.engine import StateEngine
from ..interfaces.provider import ProviderInterface
from ..exceptions import NexusException
from ..cache.cache_manager import CacheManager

logger = logging.getLogger(__name__)


class ImportEngine:
    """
    Core engine for reverse-engineering cloud infrastructure.

    This engine orchestrates the complete import process:
    1. Discovery: Find resources in cloud provider
    2. Analysis: Analyze configurations and dependencies
    3. Generation: Generate executable InfraDSL Python code
    """

    def __init__(self, state_engine: Optional[StateEngine] = None, cache_manager: Optional[CacheManager] = None):
        """
        Initialize the import engine.

        Args:
            state_engine: Optional state engine for resource discovery
            cache_manager: Optional cache manager for instant caching
        """
        self.state_engine = state_engine or StateEngine()
        self.cache_manager = cache_manager or CacheManager()
        self.analyzer = ResourceAnalyzer()
        self.generator = CodeGenerator()
        self._providers: Dict[str, ProviderInterface] = {}

    def register_provider(self, name: str, provider: ProviderInterface) -> None:
        """
        Register a provider for import operations.

        Args:
            name: Provider name (e.g., 'gcp', 'aws', 'digitalocean')
            provider: Provider implementation
        """
        self._providers[name] = provider
        self.state_engine.register_provider(name, provider)
        logger.info(f"Registered provider for import: {name}")

    async def import_from_provider(self, config: ImportConfig) -> ImportResult:
        """
        Import resources from a cloud provider and generate Python code.

        Args:
            config: Import configuration

        Returns:
            ImportResult with discovered resources and generated code
        """
        result = ImportResult(
            status=ImportStatus.PENDING, config=config, started_at=datetime.utcnow()
        )

        try:
            logger.info(f"Starting import from {config.provider}")

            # Validate configuration
            self._validate_config(config, result)
            if result.status == ImportStatus.FAILED:
                return result

            # Step 1: Discover resources
            result.status = ImportStatus.DISCOVERING
            discovered_resources = await self._discover_resources(config, result)
            result.discovered_resources = discovered_resources
            result.total_resources_found = len(discovered_resources)

            # Check if we have any resources to work with (discovered or already-managed)
            total_resources = len(discovered_resources) + getattr(result, 'total_resources_skipped', 0)
            if not discovered_resources and total_resources == 0:
                result.add_warning("No resources found matching the specified criteria")
                result.complete(ImportStatus.COMPLETED)
                return result

            # Step 2: Analyze dependencies
            result.status = ImportStatus.ANALYZING
            dependency_graph = await self._analyze_dependencies(
                discovered_resources, config, result
            )
            result.dependency_graph = dependency_graph

            # Step 3: Instant tagging and caching (Pillar 1 enhancement)
            if config.tag_resources:
                result.status = ImportStatus.TAGGING
                await self._tag_imported_resources(discovered_resources, config, result)
            
            if config.cache_imported:
                result.status = ImportStatus.CACHING
                # Cache both discovered and already-managed resources
                already_managed = getattr(result, 'already_managed_resources', [])
                all_resources_to_cache = discovered_resources + already_managed
                logger.info(f"Caching {len(discovered_resources)} new + {len(already_managed)} already-managed = {len(all_resources_to_cache)} total resources")
                await self._cache_imported_resources(all_resources_to_cache, config, result)

            # Step 4: Generate code
            result.status = ImportStatus.GENERATING
            generated_code = await self._generate_code(dependency_graph, config, result)
            result.generated_code = generated_code
            result.total_resources_imported = (
                len(dependency_graph.resources) if dependency_graph else 0
            )

            # Complete successfully
            result.complete(ImportStatus.COMPLETED)
            logger.info(
                f"Import completed successfully: {result.total_resources_imported} resources"
            )

        except Exception as e:
            logger.error(f"Import failed: {e}")
            result.add_error(f"Import failed: {str(e)}")
            result.complete(ImportStatus.FAILED)

        return result

    def _validate_config(self, config: ImportConfig, result: ImportResult) -> None:
        """Validate import configuration"""
        if not config.provider:
            result.add_error("Provider is required")
            return

        # Check if provider is registered in the state engine
        registered_providers = self.state_engine.get_registered_providers()
        if config.provider not in registered_providers:
            result.add_error(f"Provider '{config.provider}' is not registered")
            return

        if config.max_resources and config.max_resources <= 0:
            result.add_error("max_resources must be positive")
            return

        if config.timeout_seconds <= 0:
            result.add_error("timeout_seconds must be positive")
            return

    async def _discover_resources(
        self, config: ImportConfig, result: ImportResult
    ) -> List[CloudResource]:
        """
        Discover resources from the cloud provider.

        Args:
            config: Import configuration
            result: Import result to update with progress

        Returns:
            List of discovered cloud resources
        """
        logger.info(f"Discovering resources from {config.provider}")

        try:
            # Use state engine's discover_all_resources method with import mode
            all_resources = self.state_engine.discover_all_resources(
                update_storage=True,
                timeout=30,
                include_unmanaged=True,  # For import, include all resources!
            )
            logger.info(
                f"Found {len(all_resources)} total resources from all providers"
            )

            # Filter resources to only include the requested provider
            provider_resources = []
            for resource_id, resource_data in all_resources.items():
                logger.info(
                    f"DEBUG: Resource {resource_id} has provider '{resource_data.get('provider')}', looking for '{config.provider}'"
                )
                if resource_data.get("provider") == config.provider:
                    provider_resources.append(resource_data)

            raw_resources = provider_resources
            logger.info(
                f"Found {len(raw_resources)} raw resources from {config.provider}"
            )

            # Convert to CloudResource objects
            cloud_resources = []
            already_managed_resources = []  # Track for caching
            skipped_already_managed = 0
            
            for raw_resource in raw_resources:
                try:
                    cloud_resource = self._convert_to_cloud_resource(
                        raw_resource, config
                    )
                    if cloud_resource:
                        # Check if already managed first (for separate counting)
                        if self._is_already_managed(cloud_resource):
                            skipped_already_managed += 1
                            already_managed_resources.append(cloud_resource)  # Keep for caching
                            logger.info(f"Found already-managed resource {cloud_resource.name}: will cache and generate code")
                            # Still include in code generation - user wants the complete infrastructure definition
                            if self._should_include_resource(cloud_resource, config):
                                cloud_resources.append(cloud_resource)
                        elif self._should_include_resource(cloud_resource, config):
                            cloud_resources.append(cloud_resource)
                except Exception as e:
                    logger.warning(
                        f"Failed to convert resource {raw_resource.get('id', 'unknown')}: {e}"
                    )
                    result.add_warning(f"Skipped resource due to conversion error: {e}")
            
            # Update result with skipped count
            result.total_resources_skipped = skipped_already_managed

            # Apply resource limit if specified
            if config.max_resources and len(cloud_resources) > config.max_resources:
                logger.info(f"Limiting resources to {config.max_resources}")
                cloud_resources = cloud_resources[: config.max_resources]

            logger.info(f"Discovered {len(cloud_resources)} importable resources")
            
            # Store already-managed resources for caching 
            result.already_managed_resources = already_managed_resources
            logger.info(f"Found {len(already_managed_resources)} already-managed resources for caching")
            
            return cloud_resources

        except Exception as e:
            logger.error(f"Resource discovery failed: {e}")
            raise NexusException(f"Failed to discover resources: {e}")

    def _convert_to_cloud_resource(
        self, raw_resource: Dict[str, Any], config: ImportConfig
    ) -> Optional[CloudResource]:
        """
        Convert raw provider resource to CloudResource.

        Args:
            raw_resource: Raw resource data from provider
            config: Import configuration

        Returns:
            CloudResource or None if conversion fails
        """
        try:
            # Extract basic information
            resource_id = raw_resource.get("cloud_id") or raw_resource.get("id")
            if not resource_id:
                logger.warning("Resource missing ID, skipping")
                return None

            name = raw_resource.get("name", f"imported-{resource_id}")

            # Determine resource type
            resource_type = self._determine_resource_type(raw_resource)

            # Extract configuration
            configuration = self._extract_configuration(raw_resource)

            # Extract metadata and tags
            metadata = raw_resource.get("metadata", {})
            tags = self._extract_tags(raw_resource)

            return CloudResource(
                id=str(resource_id),
                name=name,
                type=resource_type,
                provider=config.provider,
                region=raw_resource.get("region"),
                zone=raw_resource.get("zone"),
                project=config.project or raw_resource.get("project"),
                configuration=configuration,
                metadata=metadata,
                tags=tags,
                discovered_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Failed to convert resource: {e}")
            return None

    def _determine_resource_type(self, raw_resource: Dict[str, Any]) -> ResourceType:
        """Determine the resource type from raw resource data"""
        resource_type = raw_resource.get("type", "").lower()

        # Map provider-specific types to standard types
        type_mappings = {
            "virtualmachine": ResourceType.VIRTUAL_MACHINE,
            "instance": ResourceType.VIRTUAL_MACHINE,
            "droplet": ResourceType.VIRTUAL_MACHINE,
            "manageddatabase": ResourceType.DATABASE,
            "database": ResourceType.DATABASE,
            "bucket": ResourceType.STORAGE,
            "volume": ResourceType.STORAGE,
            "disk": ResourceType.STORAGE,
            "network": ResourceType.NETWORK,
            "vpc": ResourceType.NETWORK,
            "subnet": ResourceType.NETWORK,
            "loadbalancer": ResourceType.LOAD_BALANCER,
            "securitygroup": ResourceType.SECURITY_GROUP,
        }

        for key, mapped_type in type_mappings.items():
            if key in resource_type:
                return mapped_type

        return ResourceType.UNKNOWN

    def _extract_configuration(self, raw_resource: Dict[str, Any]) -> Dict[str, Any]:
        """Extract configuration from raw resource data"""
        configuration = raw_resource.get("configuration", {}).copy()

        # Add important fields to configuration
        important_fields = [
            "size",
            "machine_type",
            "instance_type",
            "image",
            "engine",
            "version",
            "region",
            "zone",
            "ip_address",
            "private_ip_address",
        ]

        for field in important_fields:
            if field in raw_resource and field not in configuration:
                configuration[field] = raw_resource[field]

        return configuration

    def _extract_tags(self, raw_resource: Dict[str, Any]) -> Dict[str, str]:
        """Extract tags from raw resource data"""
        tags = {}

        # Handle different tag formats
        raw_tags = raw_resource.get("tags", [])

        if isinstance(raw_tags, dict):
            # Dict format: {"key": "value"}
            tags = raw_tags.copy()
        elif isinstance(raw_tags, list):
            # List format: ["key:value", "key2:value2"]
            for tag in raw_tags:
                if isinstance(tag, str) and ":" in tag:
                    key, value = tag.split(":", 1)
                    tags[key] = value
                elif isinstance(tag, dict):
                    tags.update(tag)

        return tags

    def _should_include_resource(
        self, resource: CloudResource, config: ImportConfig
    ) -> bool:
        """
        Check if a resource should be included based on filters.
        
        Note: This method does NOT check for already-managed resources,
        as that check is handled separately in the discovery loop.

        Args:
            resource: Cloud resource to check
            config: Import configuration with filters

        Returns:
            True if resource should be included
        """
        # Filter by resource types
        if config.resource_types:
            resource_type_str = resource.type.value if hasattr(resource.type, 'value') else str(resource.type)
            if resource_type_str not in config.resource_types:
                return False

        # Filter by name patterns
        if config.name_patterns:
            import re

            name_matches = False
            for pattern in config.name_patterns:
                if re.search(pattern, resource.name, re.IGNORECASE):
                    name_matches = True
                    break
            if not name_matches:
                return False

        # Filter by tags
        if config.tag_filters:
            for tag_key, tag_value in config.tag_filters.items():
                if tag_key not in resource.tags:
                    return False
                if tag_value != "*" and resource.tags[tag_key] != tag_value:
                    return False

        return True

    def _is_already_managed(self, resource: CloudResource) -> bool:
        """
        Check if a resource is already managed by InfraDSL.
        
        Args:
            resource: Cloud resource to check
            
        Returns:
            True if resource has InfraDSL management tags
        """
        if not resource.tags:
            return False
            
        # Check for various formats of InfraDSL management tags
        # Different cloud providers may format these differently
        managed_tag_variants = [
            "infradsl.managed",      # Standard format
            "infradsl_managed",      # GCP format (dots become underscores)
            "infradsl-managed",      # Some providers use hyphens
            "infradsl:managed",      # Colon format
        ]
        
        id_tag_variants = [
            "infradsl.id",
            "infradsl_id", 
            "infradsl-id",
            "infradsl:id",
        ]
        
        # Check if resource has InfraDSL managed tag set to true
        has_managed_tag = False
        for variant in managed_tag_variants:
            if variant in resource.tags:
                value = resource.tags[variant].lower()
                if value in ["true", "1", "yes"]:
                    has_managed_tag = True
                    break
        
        # Check if resource has InfraDSL ID tag (UUID format)
        has_id_tag = False
        for variant in id_tag_variants:
            if variant in resource.tags:
                id_value = resource.tags[variant]
                # Basic UUID format check (8-4-4-4-12 characters)
                if len(id_value) >= 32 and ("-" in id_value or len(id_value) == 32):
                    has_id_tag = True
                    break
        
        is_managed = has_managed_tag and has_id_tag
        
        if is_managed:
            # Log which tags were found for debugging
            managed_tag_found = next((v for v in managed_tag_variants if v in resource.tags), None)
            id_tag_found = next((v for v in id_tag_variants if v in resource.tags), None)
            logger.debug(f"Resource {resource.name} already managed: {managed_tag_found}={resource.tags.get(managed_tag_found)}, {id_tag_found}={resource.tags.get(id_tag_found)}")
        
        return is_managed

    async def _analyze_dependencies(
        self, resources: List[CloudResource], config: ImportConfig, result: ImportResult
    ) -> DependencyGraph:
        """
        Analyze resource dependencies and build dependency graph.

        Args:
            resources: List of discovered resources
            config: Import configuration
            result: Import result to update

        Returns:
            DependencyGraph with resources and relationships
        """
        logger.info(f"Analyzing dependencies for {len(resources)} resources")

        # Use the analyzer to build dependency graph
        dependency_graph = await self.analyzer.build_dependency_graph(resources, config)

        # Check for circular dependencies
        cycles = dependency_graph.detect_cycles()
        if cycles:
            for cycle in cycles:
                cycle_str = " -> ".join(cycle)
                result.add_warning(f"Circular dependency detected: {cycle_str}")
                logger.warning(f"Circular dependency: {cycle_str}")

        logger.info(
            f"Built dependency graph with {len(dependency_graph.resources)} resources and {len(dependency_graph.edges)} dependencies"
        )
        return dependency_graph

    async def _generate_code(
        self,
        dependency_graph: DependencyGraph,
        config: ImportConfig,
        result: ImportResult,
    ) -> Optional[Any]:
        """
        Generate InfraDSL Python code from dependency graph.

        Args:
            dependency_graph: Resource dependency graph
            config: Import configuration
            result: Import result to update

        Returns:
            GeneratedCode object
        """
        logger.info(
            f"Generating Python code for {len(dependency_graph.resources)} resources"
        )

        # Use the generator to create Python code
        generated_code = await self.generator.generate_python_code(
            dependency_graph, config
        )

        if not generated_code:
            result.add_error("Failed to generate Python code")
            return None

        logger.info(
            f"Generated {len(generated_code.content)} characters of Python code"
        )
        return generated_code

    def get_supported_providers(self) -> List[str]:
        """Get list of supported providers"""
        return list(self._providers.keys())

    def get_provider_info(self, provider_name: str) -> Dict[str, Any]:
        """Get information about a specific provider"""
        if provider_name not in self._providers:
            raise ValueError(f"Provider {provider_name} not found")

        provider = self._providers[provider_name]

        return {
            "name": provider_name,
            "resource_types": getattr(provider, "get_resource_types", lambda: [])(),
            "regions": getattr(provider, "get_regions", lambda: [])(),
            "supports_discovery": hasattr(provider, "discover_resources"),
        }

    # Pillar 1: Enhanced "Codify My Cloud" - Instant Management During Import

    async def _tag_imported_resources(
        self, resources: List[CloudResource], config: ImportConfig, result: ImportResult
    ) -> None:
        """
        Tag imported resources as InfraDSL-managed in the cloud.
        
        This implements Pillar 1 from the superior-iac-plan.md - instant management
        during import so resources are immediately recognized as managed.
        """
        logger.info(f"Tagging {len(resources)} imported resources as InfraDSL-managed")
        
        try:
            # Group resources by provider for batch operations
            by_provider = defaultdict(list)
            for resource in resources:
                by_provider[resource.provider].append(resource)
            
            # Tag resources in parallel with rate limiting
            tasks = []
            for provider_name, provider_resources in by_provider.items():
                # Batch resources to respect API rate limits (10 resources per batch)
                for batch in self._batch_resources(provider_resources, batch_size=10):
                    task = self._tag_resource_batch(provider_name, batch)
                    tasks.append(task)
            
            # Execute with controlled concurrency
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any failures gracefully
            failed_tags = [r for r in results if isinstance(r, Exception)]
            if failed_tags:
                logger.warning(f"Failed to tag {len(failed_tags)} resource batches")
                for error in failed_tags:
                    result.add_warning(f"Tagging failed: {str(error)}")
            else:
                logger.info(f"Successfully tagged all {len(resources)} resources")
                
        except Exception as e:
            logger.error(f"Resource tagging failed: {e}")
            import traceback
            logger.debug(f"Tagging error traceback: {traceback.format_exc()}")
            result.add_error(f"Failed to tag resources: {str(e)}")

    async def _tag_resource_batch(self, provider_name: str, resources: List[CloudResource]) -> None:
        """Tag a batch of resources in parallel."""
        if provider_name not in self._providers:
            raise ValueError(f"Provider {provider_name} not registered")
        
        provider = self._providers[provider_name]
        
        # Tag each resource in the batch
        tag_tasks = []
        for resource in resources:
            task = self._tag_imported_resource(provider_name, resource)
            tag_tasks.append(task)
        
        await asyncio.gather(*tag_tasks)

    async def _tag_imported_resource(self, provider_name: str, resource: CloudResource) -> None:
        """Tag a single resource in the cloud as InfraDSL-managed during import."""
        provider = self._providers[provider_name]
        
        # Generate deterministic UUID from resource name + type
        resource_type_str = resource.type.value if hasattr(resource.type, 'value') else str(resource.type)
        resource_id = self._generate_deterministic_id(resource.name, resource_type_str)
        
        tags = {
            "infradsl.managed": "true",
            "infradsl.id": resource_id,
            "infradsl.imported_at": datetime.utcnow().isoformat(),
            "infradsl.import_version": "1.0"
        }
        
        try:
            # Apply tags to actual cloud resource
            if hasattr(provider, 'update_resource_tags'):
                await provider.update_resource_tags(resource.id, tags)
            else:
                logger.warning(f"Provider {provider_name} doesn't support tag updates")
            
            # Update the resource object with new tags
            resource.metadata["infradsl_id"] = resource_id
            if "tags" not in resource.configuration:
                resource.configuration["tags"] = {}
            resource.configuration["tags"].update(tags)
            
            logger.debug(f"Tagged resource {resource.name} with ID {resource_id}")
            
        except Exception as e:
            logger.error(f"Failed to tag resource {resource.name}: {e}")
            raise

    async def _cache_imported_resources(
        self, resources: List[CloudResource], config: ImportConfig, result: ImportResult
    ) -> None:
        """
        Cache imported resources for immediate state recognition.
        
        This ensures imported resources are instantly recognized as managed
        without needing to run 'infra apply'.
        """
        logger.info(f"Caching {len(resources)} imported resources for immediate management")
        
        try:
            for resource in resources:
                await self._cache_tagged_resource(resource)
            
            logger.info(f"Successfully cached all {len(resources)} resources")
            
        except Exception as e:
            logger.error(f"Resource caching failed: {e}")
            import traceback
            logger.debug(f"Caching error traceback: {traceback.format_exc()}")
            result.add_error(f"Failed to cache resources: {str(e)}")

    async def _cache_tagged_resource(self, resource: CloudResource) -> None:
        """Cache the tagged resource for immediate state recognition."""
        # Use the resource's InfraDSL ID if available, otherwise generate one
        resource_uuid = resource.metadata.get("infradsl_id")
        
        # Handle both ResourceType enum and string types
        resource_type_str = resource.type.value if hasattr(resource.type, 'value') else str(resource.type)
        
        if not resource_uuid:
            resource_uuid = self._generate_deterministic_id(resource.name, resource_type_str)
        
        cache_key = f"resource:{resource_uuid}"
        
        state_data = {
            "id": resource_uuid,
            "type": resource_type_str,
            "name": resource.name,
            "provider": resource.provider,
            "configuration": resource.configuration,
            "tags": resource.configuration.get("tags", {}),
            "fingerprint": self._generate_fingerprint(resource),
            "cached_at": datetime.utcnow().isoformat(),
            "imported": True,  # Mark as imported resource
            "cloud_id": resource.id,  # Store original cloud ID
            "region": resource.region,
            "zone": resource.zone,
            "project": resource.project
        }
        
        # Store in cache with extended TTL (1 hour)
        from ..cache.cache_manager import CacheType
        await self.cache_manager.set(CacheType.RESOURCE_DISCOVERY, state_data, resource_uuid)
        
        # Also update the discovery cache for faster lookups  
        discovery_key = f"discovery:{resource.provider}:{resource_type_str}"
        await self.cache_manager.append_to_list(discovery_key, state_data)
        
        logger.debug(f"Cached resource {resource.name} with key {cache_key}")

    def _batch_resources(self, resources: List[CloudResource], batch_size: int = 10) -> List[List[CloudResource]]:
        """Split resources into batches for parallel processing."""
        batches = []
        for i in range(0, len(resources), batch_size):
            batch = resources[i:i + batch_size]
            batches.append(batch)
        return batches

    def _generate_deterministic_id(self, name: str, resource_type: str) -> str:
        """Generate a deterministic UUID from resource name and type."""
        # Create a deterministic UUID based on name and type
        # This ensures the same resource always gets the same ID
        seed = f"{name}:{resource_type}".encode('utf-8')
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, seed.decode('utf-8')))

    def _generate_fingerprint(self, resource: CloudResource) -> str:
        """Generate a fingerprint for the resource configuration."""
        import hashlib
        import json
        
        # Create a stable representation of the resource for fingerprinting
        resource_type_str = resource.type.value if hasattr(resource.type, 'value') else str(resource.type)
        
        fingerprint_data = {
            "name": resource.name,
            "type": resource_type_str,
            "provider": resource.provider,
            "configuration": resource.configuration,
            "region": resource.region,
            "zone": resource.zone
        }
        
        # Sort keys to ensure consistent ordering
        stable_json = json.dumps(fingerprint_data, sort_keys=True, default=str)
        return hashlib.sha256(stable_json.encode()).hexdigest()[:16]
