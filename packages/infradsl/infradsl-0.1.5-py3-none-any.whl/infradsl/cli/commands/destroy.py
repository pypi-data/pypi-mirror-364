"""
Destroy infrastructure resources
"""

import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, List
from argparse import Namespace

from .base import BaseCommand
from ..utils.errors import CommandError
from ...core.nexus.engine import NexusEngine
from ...core.nexus.lifecycle import LifecycleManager
from ...core.hooks.lifecycle_hooks import trigger_lifecycle_event, LifecycleEvent

if TYPE_CHECKING:
    from ..utils.output import Console
    from ..utils.config import CLIConfig


class DestroyCommand(BaseCommand):
    """Destroy infrastructure resources"""

    @property
    def name(self) -> str:
        return "destroy"

    @property
    def description(self) -> str:
        return "Destroy infrastructure resources"

    def register(self, subparsers) -> None:
        """Register command arguments"""
        parser = subparsers.add_parser(
            self.name,
            help=self.description,
            description="Destroy infrastructure resources defined in a Python file",
        )

        parser.add_argument("file", type=Path, help="Infrastructure file to destroy")

        parser.add_argument(
            "--auto-approve", action="store_true", help="Skip confirmation prompts"
        )

        parser.add_argument(
            "--target",
            action="append",
            help="Target specific resources (can be used multiple times)",
        )

        parser.add_argument(
            "--force",
            action="store_true",
            help="Force destruction even if resources have dependencies",
        )

        parser.add_argument(
            "--parallelism",
            type=int,
            default=10,
            help="Number of parallel operations (default: 10)",
        )

        self.add_common_arguments(parser)

    def execute(self, args: Namespace, config: "CLIConfig", console: "Console") -> int:
        """Execute the destroy command"""
        infrastructure_file = args.file

        if not infrastructure_file.exists():
            console.error(f"Infrastructure file not found: {infrastructure_file}")
            return 1

        console.info(f"Destroying infrastructure from: {infrastructure_file}")

        try:
            # Load and parse infrastructure file
            resources = self._load_infrastructure(infrastructure_file, console)

            if not resources:
                console.info("No resources found to destroy")
                return 0

            # Initialize engines
            engine = NexusEngine()
            lifecycle_manager = LifecycleManager()

            # Filter resources by target if specified
            if args.target:
                resources = self._filter_resources(resources, args.target, console)

            # Get existing resources
            console.info("Checking existing resources...")

            with console.status("Analyzing resources..."):
                existing_resources = self._get_existing_resources(resources, console)

            if not existing_resources:
                console.success("No resources found to destroy")
                return 0

            # Display resources to be destroyed
            self._display_resources(existing_resources, console)

            # Confirm destruction
            if not args.auto_approve and not config.auto_approve:
                console.warning("This will permanently destroy the listed resources!")
                if not console.confirm("Continue with destruction?"):
                    console.info("Destruction cancelled")
                    return 0

            # Destroy resources
            return self._destroy_resources(
                existing_resources, engine, lifecycle_manager, console, args
            )

        except Exception as e:
            raise CommandError(f"Failed to destroy infrastructure: {e}")

    def _load_infrastructure(self, file_path: Path, console: "Console") -> List[Any]:
        """Load infrastructure resources from Python file"""
        import importlib.util
        from dotenv import load_dotenv
        
        # Load .env file if it exists - same as apply command
        env_path = file_path.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            console.debug(f"Loaded environment from {env_path}")
        else:
            # Also check current working directory
            if Path(".env").exists():
                load_dotenv()
                console.debug("Loaded environment from .env")

        spec = importlib.util.spec_from_file_location("infrastructure", file_path)
        if spec is None or spec.loader is None:
            raise CommandError(f"Cannot load infrastructure file: {file_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Extract resources from module
        resources = []
        for name in dir(module):
            obj = getattr(module, name)
            if hasattr(obj, "_resource_type") and hasattr(obj, "name"):
                resources.append(obj)

        console.debug(f"Loaded {len(resources)} resources from {file_path}")
        return resources

    def _filter_resources(
        self, resources: List[Any], targets: List[str], console: "Console"
    ) -> List[Any]:
        """Filter resources by target names"""
        filtered = []
        for resource in resources:
            if resource.name in targets:
                filtered.append(resource)

        console.debug(
            f"Filtered to {len(filtered)} resources matching targets: {targets}"
        )
        return filtered

    def _get_existing_resources(
        self, resources: List[Any], console: "Console"
    ) -> List[Any]:
        """Get resources that actually exist and can be destroyed"""
        existing = []

        for resource in resources:
            # Check if resource exists in provider using state detection
            if self._resource_exists(resource):
                existing.append(resource)

        console.debug(f"Found {len(existing)} existing resources to destroy")
        return existing

    def _resource_exists(self, resource: Any) -> bool:
        """Check if resource exists in provider"""
        try:
            # Use the same state detection as apply command
            if hasattr(resource, "_provider") and resource._provider:
                from ...core.services.state_detection import create_state_detector
                state_detector = create_state_detector(resource._provider)
                current_state = state_detector.get_current_state(resource)
                return current_state is not None
            return False
        except Exception as e:
            # If we can't check state, assume resource doesn't exist
            return False

    def _display_resources(self, resources: List[Any], console: "Console") -> None:
        """Display resources to be destroyed"""
        console.info("")
        console.info(f"The following {len(resources)} resources will be destroyed:")
        console.info("")

        # Group by resource type
        resource_groups = {}
        for resource in resources:
            resource_type = resource._resource_type
            if resource_type not in resource_groups:
                resource_groups[resource_type] = []
            resource_groups[resource_type].append(resource)

        # Display grouped resources with provider info
        for resource_type, group_resources in resource_groups.items():
            console.info(f"  {resource_type}:")
            for resource in group_resources:
                # Get provider info
                provider_info = ""
                if hasattr(resource, "_provider") and resource._provider:
                    provider_type = resource._provider.config.type.value if hasattr(resource._provider.config.type, 'value') else str(resource._provider.config.type)
                    provider_info = f" ({provider_type})"
                
                # Get resource state info
                state_info = ""
                try:
                    if hasattr(resource, "_provider") and resource._provider:
                        from ...core.services.state_detection import create_state_detector
                        state_detector = create_state_detector(resource._provider)
                        current_state = state_detector.get_current_state(resource)
                        if current_state:
                            status = current_state.get("status", "unknown")
                            region = current_state.get("region", "")
                            if region:
                                state_info = f" [status: {status}, region: {region}]"
                            else:
                                state_info = f" [status: {status}]"
                except Exception:
                    pass
                
                console.info(f"    - {resource.name}{provider_info}{state_info}")
        
        console.info("")

    def _destroy_resources(
        self,
        resources: List[Any],
        engine: NexusEngine,
        lifecycle_manager: LifecycleManager,
        console: "Console",
        args: Namespace,
    ) -> int:
        """Destroy the resources"""
        console.info("\\nDestroying resources...")

        start_time = time.time()
        destroyed_count = 0
        failed_count = 0

        # Reverse the order for destruction (dependencies first)
        resources_to_destroy = list(reversed(resources))

        for resource in resources_to_destroy:
            try:
                # Get provider info for display
                provider_info = ""
                if hasattr(resource, "_provider") and resource._provider:
                    provider_type = resource._provider.config.type.value if hasattr(resource._provider.config.type, 'value') else str(resource._provider.config.type)
                    provider_info = f" ({provider_type})"
                
                with console.status(f"Destroying {resource.name}{provider_info}..."):
                    result = self._destroy_resource(
                        resource, engine, lifecycle_manager, console, args.force
                    )

                if result:
                    console.success(f"✓ Destroyed {resource.name}{provider_info}")
                    destroyed_count += 1
                else:
                    console.error(f"✗ Failed to destroy {resource.name}{provider_info}")
                    failed_count += 1

            except Exception as e:
                console.error(f"✗ Error destroying {resource.name}: {e}")
                failed_count += 1

        # Summary
        duration = time.time() - start_time
        console.info("")
        console.info(f"Destruction completed in {duration:.1f}s")
        
        if destroyed_count > 0:
            console.info(f"✓ {destroyed_count} resource(s) destroyed successfully")
        
        if failed_count > 0:
            console.error(f"✗ {failed_count} resource(s) failed to destroy")
            return 1
        else:
            console.success("All resources destroyed successfully")
            return 0

    def _destroy_resource(
        self,
        resource: Any,
        engine: NexusEngine,
        lifecycle_manager: LifecycleManager,
        console: "Console",
        force: bool = False,
    ) -> bool:
        """Destroy a single resource"""
        try:
            # Check dependencies if not forcing
            if not force and self._has_dependencies(resource):
                console.warning(
                    f"Resource {resource.name} has dependencies. Use --force to override."
                )
                return False

            # Use the resource's destroy method directly
            if hasattr(resource, "destroy"):
                resource.destroy()
                
                # Trigger after_destroy lifecycle hook
                try:
                    import asyncio
                    console.debug(f"Triggering after_destroy hook for {resource.name}")
                    asyncio.run(trigger_lifecycle_event(LifecycleEvent.AFTER_DESTROY, resource))
                except Exception as hook_error:
                    console.debug(f"Lifecycle hook error: {hook_error}")
                
                # Remove from cache after successful destruction
                self._remove_from_cache(resource, console)
                
                return True
            else:
                console.error(f"Resource {resource.name} does not support destruction")
                return False

        except Exception as e:
            # Provide detailed error information
            console.error(f"Failed to delete resource {resource.name}: {e}")
            if console.verbosity >= 2:
                import traceback
                console.error(traceback.format_exc())
            return False

    def _has_dependencies(self, resource: Any) -> bool:
        """Check if resource has dependencies that prevent destruction"""
        # This would check for actual dependencies
        # For now, assume no dependencies
        return False
    
    def _remove_from_cache(self, resource: Any, console: "Console") -> None:
        """Remove resource from cache after successful destruction"""
        try:
            # Remove from file-based cache
            from ...core.state.engine import StateEngine
            cache_engine = StateEngine(storage_backend="file")
            cache_engine.storage.delete(resource.name)
            console.debug(f"Removed {resource.name} from file cache")

            # Remove from PostgreSQL cache if available
            from ...core.cache.simple_postgres_cache import get_simple_cache
            pg_cache = get_simple_cache()
            
            # Get resource type from resource metadata
            resource_type = getattr(resource, '_resource_type', 'unknown')
            
            # Use cloud_id (actual cloud resource ID) for cache invalidation to match caching behavior
            resource_id = None
            if hasattr(resource, 'status') and resource.status and resource.status.cloud_id:
                resource_id = resource.status.cloud_id
            else:
                # Fallback to resource name if cloud_id not available
                resource_id = getattr(resource, 'id', resource.name)
            
            # Get provider info for cache key
            if hasattr(resource, "_provider") and resource._provider:
                provider_type = resource._provider.config.type.value if hasattr(resource._provider.config.type, 'value') else str(resource._provider.config.type)
                pg_cache.invalidate_resource(provider_type, resource_type, resource_id)
                console.debug(f"Removed {resource.name} from PostgreSQL cache (cache_key: {provider_type}:{resource_type}:{resource_id})")

        except Exception as e:
            # Cache cleanup is not critical, log and continue
            console.debug(f"Failed to remove {resource.name} from cache: {e}")
