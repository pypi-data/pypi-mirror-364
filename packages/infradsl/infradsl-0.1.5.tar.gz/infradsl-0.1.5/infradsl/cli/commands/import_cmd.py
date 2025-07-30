"""
"Codify My Cloud" Import CLI command
"""

import asyncio
from argparse import Namespace
from typing import TYPE_CHECKING, List, Optional, Dict, Any
from pathlib import Path

from .base import BaseCommand
from ..utils.errors import CommandError
import importlib


class SimpleCacheWrapper:
    """Wrapper to adapt SimplePostgreSQLCache to async CacheManager interface"""
    
    def __init__(self, simple_cache):
        self.simple_cache = simple_cache
    
    async def set(self, cache_type, data: Dict[str, Any], key: str) -> None:
        """Store data in cache with proper resource state format"""
        # Extract resource info from data for simple cache format
        provider = data.get("provider", "unknown")
        resource_type = data.get("type", "unknown")
        resource_id = data.get("cloud_id") or data.get("id", key)
        resource_name = data.get("name", "unknown")
        
        # Use simple cache method
        self.simple_cache.cache_resource_state(
            provider=provider,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            state_data=data,
            project=data.get("project", ""),
            environment=data.get("environment", "development"),
            region=data.get("region", ""),
            ttl_seconds=3600  # 1 hour TTL
        )
    
    async def append_to_list(self, list_key: str, data: Dict[str, Any]) -> None:
        """Append data to a list - for simple cache we just store individual resources"""
        # For simple cache, we store each resource individually
        # The list functionality is handled by discovery queries
        resource_id = data.get("cloud_id") or data.get("id", "unknown")
        await self.set("RESOURCE_DISCOVERY", data, resource_id)

# Import from the 'import_system' module using importlib
import_module = importlib.import_module("infradsl.core.import_system")
ImportEngine = import_module.ImportEngine
ImportConfig = import_module.ImportConfig
ImportStatus = import_module.ImportStatus
from ...core.nexus.provider_registry import get_registry
from ...core.state.engine import StateEngine

if TYPE_CHECKING:
    from ..utils.output import Console
    from ..utils.config import CLIConfig


class ImportCommand(BaseCommand):
    """Import existing cloud infrastructure to InfraDSL Python code"""

    @property
    def name(self) -> str:
        return "import"

    @property
    def description(self) -> str:
        return "Import existing cloud infrastructure and generate InfraDSL Python code"

    def register(self, subparsers) -> None:
        """Register import command"""
        parser = subparsers.add_parser(
            self.name,
            help=self.description,
            description=(
                "Import existing cloud resources and generate executable InfraDSL Python code. "
                "This 'Codify My Cloud' feature allows you to migrate from other tools or "
                "manually-managed infrastructure to InfraDSL."
            ),
        )

        # Required arguments
        parser.add_argument(
            "--provider",
            required=True,
            choices=["gcp", "aws", "digitalocean"],
            help="Cloud provider to import from",
        )

        # Provider-specific options
        parser.add_argument(
            "--project",
            help="Project ID (for GCP) or account ID (for AWS)",
        )
        parser.add_argument(
            "--region",
            help="Cloud region to import from (e.g., us-west-2)",
        )

        # Filtering options
        parser.add_argument(
            "--resource-types",
            nargs="+",
            help="Resource types to import (e.g., virtual_machine database)",
        )
        parser.add_argument(
            "--name-pattern",
            help="Regular expression pattern to filter resources by name",
        )
        parser.add_argument(
            "--tags",
            nargs="+",
            help="Filter by tags (format: key=value)",
        )

        # Output options
        parser.add_argument(
            "--output",
            "-o",
            help="Output file path for generated Python code",
        )
        parser.add_argument(
            "--no-comments",
            action="store_true",
            help="Don't include comments in generated code",
        )
        parser.add_argument(
            "--group-by-type",
            action="store_true",
            help="Group resources by type in the output",
        )

        # Advanced options
        parser.add_argument(
            "--max-resources",
            type=int,
            help="Maximum number of resources to import",
        )
        parser.add_argument(
            "--no-dependencies",
            action="store_true",
            help="Don't analyze resource dependencies",
        )
        parser.add_argument(
            "--preview",
            action="store_true",
            help="Preview resources without generating code",
        )
        
        # Superior Import System Options
        parser.add_argument(
            "--organization",
            choices=["service", "environment", "layer", "hybrid"],
            default="service",
            help="File organization strategy for generated code",
        )
        parser.add_argument(
            "--max-workers",
            type=int,
            default=10,
            help="Maximum parallel workers for discovery",
        )
        parser.add_argument(
            "--batch-size", 
            type=int,
            default=50,
            help="Batch size for parallel operations",
        )
        parser.add_argument(
            "--use-superior-import",
            action="store_true",
            help="Use the new Superior Import System with dependency analysis",
        )
        
        # Pillar 1: Instant Management Options
        parser.add_argument(
            "--no-tag-resources",
            action="store_true",
            help="Don't tag imported resources as InfraDSL-managed",
        )
        parser.add_argument(
            "--no-cache-imported", 
            action="store_true",
            help="Don't cache imported resources for immediate management",
        )

        # Add common arguments
        self.add_common_arguments(parser)

    def execute(self, args: Namespace, config: "CLIConfig", console: "Console") -> int:
        """Execute the import command"""
        try:
            # Use Superior Import System if requested
            if args.use_superior_import:
                result = asyncio.run(self._execute_superior_import(args, config, console))
            else:
                # Use legacy import system
                result = asyncio.run(self._execute_async(args, config, console))
            return result
        except KeyboardInterrupt:
            console.error("\nImport cancelled by user")
            return 1
        except Exception as e:
            console.error(f"Import failed: {str(e)}")
            return 1

    async def _execute_async(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Execute import asynchronously"""
        console.info(f"Importing resources from {args.provider.upper()}...")

        # Create import configuration
        import_config = self._create_import_config(args)

        # Initialize engines using the same discovery mechanism as state command
        state_engine = self._create_state_engine_with_providers(args, console)
        
        # Initialize simple PostgreSQL cache for Pillar 1 functionality
        # This ensures compatibility with preview/apply/destroy commands
        from ...core.cache.simple_postgres_cache import get_simple_cache
        from ...core.cache.cache_manager import CacheManager
        try:
            simple_cache = get_simple_cache()
            # Wrap the simple cache to work with async CacheManager interface
            cache_manager = SimpleCacheWrapper(simple_cache)
            console.debug("Simple PostgreSQL cache manager initialized")
        except Exception as e:
            console.warning(f"Could not initialize simple PostgreSQL cache: {e}")
            # Fall back to in-memory cache
            cache_manager = CacheManager()
            console.debug("Using in-memory cache as fallback")
        
        import_engine = ImportEngine(state_engine, cache_manager)

        # Register the same providers with the import engine for tagging
        registered_providers = state_engine.get_registered_providers()
        for provider_name in registered_providers:
            # Get provider from discoverer which contains the provider reference
            discoverer = state_engine.discoverers.get(provider_name)
            if discoverer and hasattr(discoverer, 'provider'):
                provider = discoverer.provider
                import_engine.register_provider(provider_name, provider)
                console.debug(f"Registered {provider_name} provider with import engine")
            else:
                console.warning(f"Could not get provider instance for {provider_name}")

        # Preview mode - just show what would be imported
        if args.preview:
            return await self._preview_import(import_engine, import_config, console)

        # Execute import
        with console.progress("Importing resources...") as progress:
            # Add tasks for progress tracking
            discover_task = progress.add_task(
                "[blue]Discovering resources...", total=None
            )
            analyze_task = progress.add_task(
                "[yellow]Analyzing dependencies...", total=None
            )
            tag_task = progress.add_task("[cyan]Tagging resources...", total=None)
            cache_task = progress.add_task("[magenta]Caching resources...", total=None)
            generate_task = progress.add_task("[green]Generating code...", total=None)

            # Execute import
            result = await import_engine.import_from_provider(import_config)

            # Update progress based on status
            if result.status in [
                ImportStatus.DISCOVERING,
                ImportStatus.ANALYZING,
                ImportStatus.TAGGING,
                ImportStatus.CACHING,
                ImportStatus.GENERATING,
                ImportStatus.COMPLETED,
            ]:
                progress.update(discover_task, completed=100)
            if result.status in [
                ImportStatus.ANALYZING,
                ImportStatus.TAGGING,
                ImportStatus.CACHING,
                ImportStatus.GENERATING,
                ImportStatus.COMPLETED,
            ]:
                progress.update(analyze_task, completed=100)
            if result.status in [
                ImportStatus.TAGGING,
                ImportStatus.CACHING,
                ImportStatus.GENERATING,
                ImportStatus.COMPLETED,
            ]:
                progress.update(tag_task, completed=100)
            if result.status in [
                ImportStatus.CACHING,
                ImportStatus.GENERATING,
                ImportStatus.COMPLETED,
            ]:
                progress.update(cache_task, completed=100)
            if result.status == ImportStatus.COMPLETED:
                progress.update(generate_task, completed=100)

        # Handle results
        if result.status == ImportStatus.FAILED:
            console.error("Import failed!")
            for error in result.errors:
                console.error(f"  • {error}")
            return 1

        # Show warnings if any
        if result.warnings:
            console.warning("Import completed with warnings:")
            for warning in result.warnings:
                console.warning(f"  • {warning}")

        # Show summary
        console.success(f"\nImport completed successfully!")
        if import_config.tag_resources:
            console.info("✅ Resources tagged as InfraDSL-managed in the cloud")
        if import_config.cache_imported:
            console.info("✅ Resources cached for immediate management")
        self._show_import_summary(result, console)

        # Write output file
        if result.generated_code and not args.dry_run:
            output_path = Path(
                import_config.output_file or result.generated_code.filename
            )

            # Confirm before writing
            if output_path.exists() and not args.yes:
                if not console.confirm(f"File '{output_path}' exists. Overwrite?"):
                    console.info("Import cancelled")
                    return 0

            # Write the file
            output_path.write_text(result.generated_code.content)
            console.success(f"\nGenerated code written to: {output_path}")
            console.info(f"\nTo apply this infrastructure, run:")
            console.info(f"  infra apply {output_path}")

        return 0

    async def _preview_import(
        self,
        import_engine: ImportEngine,
        config: ImportConfig,
        console: "Console",
    ) -> int:
        """Preview what would be imported"""
        console.info("Discovering resources (preview mode)...")

        # Just do discovery, not full import
        result = await import_engine.import_from_provider(
            ImportConfig(
                provider=config.provider,
                project=config.project,
                region=config.region,
                resource_types=config.resource_types,
                name_patterns=config.name_patterns,
                tag_filters=config.tag_filters,
                dry_run=True,
                max_resources=config.max_resources,
                timeout_seconds=30,  # Shorter timeout for preview
                # Disable tagging and caching for preview mode
                tag_resources=False,
                cache_imported=False,
            )
        )

        if result.status == ImportStatus.FAILED:
            console.error("Discovery failed!")
            for error in result.errors:
                console.error(f"  • {error}")
            return 1

        # Show discovered resources
        console.info(f"\nDiscovered {len(result.discovered_resources)} resources:")

        # Group by type
        resources_by_type = {}
        for resource in result.discovered_resources:
            if resource.type not in resources_by_type:
                resources_by_type[resource.type] = []
            resources_by_type[resource.type].append(resource)

        # Display resources
        for resource_type, resources in resources_by_type.items():
            console.info(f"\n{resource_type.value.replace('_', ' ').title()}:")
            for resource in resources:
                console.info(f"  • {resource.name} (ID: {resource.id})")
                if resource.region:
                    console.info(f"    Region: {resource.region}")
                if resource.tags:
                    console.info(
                        f"    Tags: {', '.join(f'{k}={v}' for k, v in resource.tags.items())}"
                    )

        return 0

    def _create_import_config(self, args: Namespace) -> ImportConfig:
        """Create import configuration from arguments"""
        # Parse tag filters
        tag_filters = {}
        if args.tags:
            for tag in args.tags:
                if "=" in tag:
                    key, value = tag.split("=", 1)
                    tag_filters[key] = value
                else:
                    tag_filters[tag] = "*"

        # Parse name patterns
        name_patterns = []
        if args.name_pattern:
            name_patterns.append(args.name_pattern)

        return ImportConfig(
            provider=args.provider,
            project=args.project,
            region=args.region,
            resource_types=args.resource_types,
            name_patterns=name_patterns,
            tag_filters=tag_filters,
            output_file=args.output,
            include_dependencies=not args.no_dependencies,
            generate_comments=not args.no_comments,
            group_by_type=args.group_by_type,
            dry_run=args.dry_run,
            max_resources=args.max_resources,
            timeout_seconds=args.timeout,
            # Pillar 1: Instant Management Options
            tag_resources=not args.no_tag_resources,      # Default True, disabled by --no-tag-resources
            cache_imported=not args.no_cache_imported,    # Default True, disabled by --no-cache-imported
        )

    def _create_state_engine_with_providers(
        self, args: Namespace, console: "Console"
    ) -> StateEngine:
        """Create state engine with registered providers (same as state command)"""
        import os
        from ...core.state.engine import StateEngine
        from ...core.interfaces.provider import ProviderConfig, ProviderType

        try:
            from dotenv import load_dotenv

            load_dotenv()
            console.debug("Loaded environment variables")
        except Exception as e:
            console.debug(f"Failed to load dotenv: {e}")

        # Debug: Check if environment variables are loaded
        do_token = os.getenv("DIGITALOCEAN_TOKEN")
        if do_token:
            console.debug(f"DIGITALOCEAN_TOKEN found: {do_token[:10]}...")
        else:
            console.debug("DIGITALOCEAN_TOKEN not found in environment")

        # Use file-based storage for caching instead of async in-memory
        engine = StateEngine(storage_backend="file")
        console.debug("State engine initialized")

        # Register providers with the discovery engine
        providers_registered = 0

        # Try to register DigitalOcean provider
        console.debug("Checking for DigitalOcean provider...")
        try:
            from ...providers.digitalocean import DigitalOceanProvider

            console.debug("Attempting to register DigitalOcean provider")
            token = os.getenv("DIGITALOCEAN_TOKEN")
            if token:
                console.info(f"Found DIGITALOCEAN_TOKEN, creating config...")
                config = ProviderConfig(
                    type=ProviderType.DIGITAL_OCEAN,
                    credentials={"token": token},
                    region="nyc1",
                )
                console.info("Creating DigitalOcean provider instance...")
                provider = DigitalOceanProvider(config=config)
                console.info(
                    "Registering DigitalOcean provider with discovery engine..."
                )
                engine.register_provider("digitalocean", provider)
                providers_registered += 1
                console.info("Registered DigitalOcean provider")
            else:
                console.info("No DIGITALOCEAN_TOKEN found, skipping DigitalOcean")
        except Exception as e:
            console.info(f"Could not register DigitalOcean provider: {e}")
            import traceback

            console.debug(f"Exception details: {traceback.format_exc()}")

        # Try to register GCP provider
        console.debug("Checking for GCP provider...")
        try:
            from ...providers.gcp import GCPComputeProvider

            console.debug("Attempting to register GCP provider")

            # Try to auto-discover GCP project from environment
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
            # Use region from args, environment, or default to europe-west1
            region = getattr(args, "region", None) or os.getenv(
                "GOOGLE_CLOUD_REGION", "europe-west1"
            )

            # Try to get project from service account file
            if not project_id:
                try:
                    import json

                    service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                    if service_account_path and os.path.exists(service_account_path):
                        console.debug(
                            f"Reading service account file: {service_account_path}"
                        )
                        with open(service_account_path) as f:
                            creds = json.load(f)
                        project_id = creds.get("project_id")
                        console.debug(
                            f"Found project ID from service account: {project_id}"
                        )
                except Exception as e:
                    console.debug(f"Could not read service account file: {e}")

            if project_id:
                console.info(f"Found GCP project: {project_id}")
                config = ProviderConfig(
                    type=ProviderType.GCP,
                    project=project_id,
                    region=region,
                )
                console.info("Creating GCP provider instance...")
                provider = GCPComputeProvider(config=config)
                console.info("Registering GCP provider with discovery engine...")
                engine.register_provider("gcp", provider)
                providers_registered += 1
                console.info("Registered GCP provider")
            else:
                console.info("No GCP project ID found, skipping GCP")
        except Exception as e:
            console.info(f"Could not register GCP provider: {e}")
            import traceback

            console.debug(f"Exception details: {traceback.format_exc()}")

        console.debug(f"Successfully registered {providers_registered} providers")
        return engine

    def _show_import_summary(self, result, console: "Console") -> None:
        """Show import result summary"""
        summary = result.get_summary()

        console.info(f"\nImport Summary:")
        console.info(f"  Provider: {summary['provider']}")
        if summary["project"]:
            console.info(f"  Project: {summary['project']}")
        console.info(f"  Resources discovered: {summary['total_resources_found']}")
        console.info(f"  Resources imported: {summary['total_resources_imported']}")
        if summary["total_resources_skipped"] > 0:
            console.info(f"  Resources skipped (already managed): {summary['total_resources_skipped']}")
        console.info(f"  Execution time: {summary['execution_time_seconds']:.2f}s")

        if summary["warnings_count"] > 0:
            console.warning(f"  Warnings: {summary['warnings_count']}")
        if summary["errors_count"] > 0:
            console.error(f"  Errors: {summary['errors_count']}")

    async def _execute_superior_import(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Execute import using the Superior Import System"""
        from ...core.import_system.resource_discovery import ResourceDiscoveryEngine
        from ...core.import_system.file_organizer import FileOrganizer, OrganizationStrategy
        from ...core.import_system.code_generator import CodeGenerator
        from pathlib import Path
        
        console.info("🚀 Using Superior Import System with dependency analysis")
        console.info(f"   Provider: {args.provider}")
        console.info(f"   Organization: {args.organization}")
        console.info(f"   Max workers: {args.max_workers}")
        
        try:
            # Phase 1: Parallel Resource Discovery
            console.info("\n📡 Phase 1: Parallel Resource Discovery")
            
            discovery_engine = ResourceDiscoveryEngine(
                max_workers=args.max_workers,
                batch_size=args.batch_size
            )
            
            # Prepare discovery parameters
            providers = [args.provider]
            if args.region:
                # Support comma-separated regions
                region_list = [r.strip() for r in args.region.split(",")]
                regions = {args.provider: region_list}
            else:
                regions = None
            
            # Parse filters
            filters = {}
            if args.tags:
                for tag in args.tags:
                    if "=" in tag:
                        key, value = tag.split("=", 1)
                        filters[key] = value
            
            # Discover resources
            with console.progress("Discovering resources...") as progress:
                task = progress.add_task("[blue]Discovering...", total=None)
                
                dependency_graph = await discovery_engine.discover_all_resources(
                    providers=providers,
                    regions=regions,
                    filters=filters,
                    auto_tag=not args.no_tag_resources
                )
                
                progress.update(task, completed=100)
            
            # Get statistics
            stats = discovery_engine.get_statistics()
            resource_count = len(dependency_graph.nodes)
            
            console.info(f"✅ Discovery complete!")
            console.info(f"   📊 {resource_count} resources discovered")
            console.info(f"   ⚡ {stats['discovery_rate']:.1f} resources/sec")
            console.info(f"   🏷️  {stats['total_resources_tagged']} resources tagged")
            console.info(f"   💾 {stats['total_resources_cached']} resources cached")
            
            if args.preview:
                # Show preview and exit
                console.info("\n🔍 Preview Mode - Resources that would be imported:")
                
                resources_by_type = {}
                for resource in dependency_graph.nodes.values():
                    if resource.type not in resources_by_type:
                        resources_by_type[resource.type] = []
                    resources_by_type[resource.type].append(resource)
                
                for resource_type, resources in resources_by_type.items():
                    console.info(f"\n{resource_type.replace('_', ' ').title()}:")
                    for resource in resources[:5]:  # Show first 5
                        console.info(f"  • {resource.name} (ID: {resource.id[:20]}...)")
                    if len(resources) > 5:
                        console.info(f"  ... and {len(resources) - 5} more")
                
                return 0
            
            # Phase 2: Dependency Analysis
            console.info("\n🔗 Phase 2: Dependency Analysis")
            
            with console.progress("Analyzing dependencies...") as progress:
                task = progress.add_task("[yellow]Analyzing...", total=None)
                
                # Dependencies are already analyzed during discovery
                dep_stats = dependency_graph.get_statistics()
                
                progress.update(task, completed=100)
            
            console.info(f"✅ Dependency analysis complete!")
            console.info(f"   🔗 {dep_stats['total_dependencies']} dependencies found")
            console.info(f"   📊 {dep_stats['average_dependencies_per_resource']:.1f} avg per resource")
            
            if dep_stats['circular_dependencies'] > 0:
                console.warning(f"   ⚠️  {dep_stats['circular_dependencies']} circular dependencies detected")
            
            # Phase 3: Intelligent File Organization  
            console.info("\n📁 Phase 3: Intelligent File Organization")
            
            strategy_map = {
                "service": OrganizationStrategy.SERVICE,
                "environment": OrganizationStrategy.ENVIRONMENT,
                "layer": OrganizationStrategy.LAYER,
                "hybrid": OrganizationStrategy.HYBRID
            }
            
            organizer = FileOrganizer(strategy=strategy_map[args.organization])
            output_dir = args.output or "infrastructure"
            
            with console.progress("Organizing files...") as progress:
                task = progress.add_task("[cyan]Organizing...", total=None)
                
                file_groups = organizer.organize(dependency_graph, output_dir)
                
                progress.update(task, completed=100)
            
            org_stats = organizer.get_statistics(file_groups)
            console.info(f"✅ File organization complete!")
            console.info(f"   📄 {org_stats['total_files']} files will be created")
            console.info(f"   📊 {org_stats['average_resources_per_file']:.1f} avg resources per file")
            console.info(f"   📂 Largest file: {Path(org_stats['largest_file']).name}")
            
            # Phase 4: Clean Code Generation
            console.info("\n⚡ Phase 4: Clean Code Generation")
            
            generator = CodeGenerator()
            creation_order = organizer.get_creation_order(file_groups)
            generated_files = []
            
            with console.progress("Generating code...") as progress:
                task = progress.add_task("[green]Generating...", total=len(creation_order))
                
                for i, file_path in enumerate(creation_order):
                    file_group = file_groups[file_path]
                    
                    # Generate code
                    code = generator.generate_file(file_group, dependency_graph, file_groups)
                    formatted_code = generator.format_code(code)
                    
                    # Create directory if needed
                    output_path = Path(file_path)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Write file
                    with open(output_path, "w") as f:
                        f.write(formatted_code)
                    
                    generated_files.append(file_path)
                    progress.update(task, advance=1)
            
            console.info(f"✅ Code generation complete!")
            console.info(f"   📝 {len(generated_files)} files generated")
            console.info(f"   📂 Output directory: {output_dir}")
            
            # Show summary
            console.success("\n🎉 Superior Import Complete!")
            console.info(f"   📊 {resource_count} resources imported")
            console.info(f"   📁 {len(file_groups)} files created")
            console.info(f"   ⚡ Organized using {args.organization} strategy")
            console.info(f"   📂 Output: {output_dir}/")
            
            if not args.no_tag_resources:
                console.info("   🏷️  Resources tagged as InfraDSL-managed in the cloud")
            if not args.no_cache_imported:
                console.info("   💾 Resources cached for immediate management")
            
            console.info("\n🚀 Next steps:")
            console.info("   1. Review the generated code")
            console.info("   2. Run 'infra preview' to verify the infrastructure")
            console.info("   3. Use 'infra apply' to manage your infrastructure")
            
            return 0
            
        except Exception as e:
            console.error(f"Superior import failed: {e}")
            import traceback
            console.debug(traceback.format_exc())
            return 1
