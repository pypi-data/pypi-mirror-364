"""
Async Apply infrastructure changes - High-performance version
"""

import asyncio
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from argparse import Namespace

from .base import BaseCommand
from ..utils.errors import CommandError
from ...core.engines.async_engine import AsyncNexusEngine
from ...core.adapters.async_provider_adapter import AsyncProviderManager
from ...core.nexus.base_resource import ResourceState
from ...core.services.state_detection import create_state_detector
from ...core.services.dependency_resolver import DependencyResolver

if TYPE_CHECKING:
    from ..utils.output import Console
    from ..utils.config import CLIConfig


class AsyncApplyCommand(BaseCommand):
    """Apply infrastructure changes asynchronously for better performance"""

    @property
    def name(self) -> str:
        return "async-apply"

    @property
    def description(self) -> str:
        return "Apply infrastructure changes asynchronously"

    def register(self, subparsers) -> None:
        """Register command arguments"""
        parser = subparsers.add_parser(
            self.name,
            help=self.description,
            description="Apply infrastructure changes from a Python file with async performance",
        )

        parser.add_argument("file", type=Path, help="Infrastructure file to apply")

        parser.add_argument(
            "--auto-approve", action="store_true", help="Skip confirmation prompts"
        )

        parser.add_argument(
            "--parallelism",
            type=int,
            default=10,
            help="Maximum number of concurrent operations (default: 10)",
        )

        parser.add_argument(
            "--timeout",
            type=int,
            default=300,
            help="Timeout for individual operations in seconds (default: 300)",
        )

        parser.add_argument(
            "--batch-size",
            type=int,
            default=5,
            help="Batch size for parallel operations (default: 5)",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without making changes",
        )

        parser.add_argument(
            "--force",
            action="store_true",
            help="Force apply even if drift is detected",
        )

        parser.add_argument(
            "--skip-drift-check",
            action="store_true",
            help="Skip drift detection for faster applies",
        )

        parser.add_argument(
            "--provider-health-check",
            action="store_true",
            help="Check provider health before applying",
        )

    async def run_async(self, args: Namespace, console: "Console", config: "CLIConfig") -> None:
        """Run the async apply command"""
        start_time = time.time()

        try:
            # Initialize async engine and provider manager
            engine = AsyncNexusEngine()
            provider_manager = AsyncProviderManager()

            # Load and execute the infrastructure file
            resources = await self._load_infrastructure(args.file, console)
            
            # Store resources for lookup during execution
            self._resources = {resource.name: resource for resource in resources}

            # Setup providers
            await self._setup_providers(engine, provider_manager, resources, console)

            # Check provider health if requested
            if args.provider_health_check:
                await self._check_provider_health(provider_manager, console)

            # Resolve dependencies
            dependency_resolver = DependencyResolver()
            dependency_resolver.add_resources(resources)
            execution_plan = dependency_resolver.resolve_creation_order()

            console.print(f"Found {len(resources)} resources to process")

            # Check for drift if not skipped
            if not args.skip_drift_check:
                await self._check_drift(engine, resources, console, args.force)

            # Generate execution plan
            plan = await self._generate_plan(engine, execution_plan, console)

            # Show plan and get confirmation
            if not args.dry_run:
                if not args.auto_approve:
                    await self._show_plan_and_confirm(plan, console)
                
                # Execute the plan
                await self._execute_plan(
                    engine, 
                    plan, 
                    console, 
                    args.parallelism, 
                    args.timeout, 
                    args.batch_size
                )

            # Cleanup
            provider_manager.cleanup()

            elapsed_time = time.time() - start_time
            console.print(f"✅ Apply completed in {elapsed_time:.2f} seconds")

        except Exception as e:
            console.error(f"Apply failed: {str(e)}")
            raise CommandError(f"Apply failed: {str(e)}")

    def execute(self, args: Namespace, config: "CLIConfig", console: "Console") -> int:
        """Execute the command - wraps async execution"""
        try:
            asyncio.run(self.run_async(args, console, config))
            return 0
        except Exception as e:
            console.error(f"Command failed: {e}")
            return 1

    async def _load_infrastructure(self, file_path: Path, console: "Console") -> List[Any]:
        """Load infrastructure resources from file"""
        console.print(f"Loading infrastructure from {file_path}")
        
        if not file_path.exists():
            raise CommandError(f"Infrastructure file not found: {file_path}")

        # Import the infrastructure file
        import importlib.util
        import sys

        spec = importlib.util.spec_from_file_location("infrastructure", file_path)
        if spec is None or spec.loader is None:
            raise CommandError(f"Failed to load infrastructure file: {file_path}")

        infrastructure_module = importlib.util.module_from_spec(spec)
        sys.modules["infrastructure"] = infrastructure_module
        spec.loader.exec_module(infrastructure_module)

        # Extract resources
        resources = []
        for attr_name in dir(infrastructure_module):
            attr = getattr(infrastructure_module, attr_name)
            if hasattr(attr, '_resource_type') and hasattr(attr, 'metadata'):
                resources.append(attr)

        if not resources:
            raise CommandError("No resources found in infrastructure file")

        return resources

    async def _setup_providers(
        self, 
        engine: AsyncNexusEngine, 
        provider_manager: AsyncProviderManager, 
        resources: List[Any], 
        console: "Console"
    ) -> None:
        """Setup providers for resources"""
        console.print("Setting up providers...")
        
        # Get unique providers from resources
        providers_needed = set()
        for resource in resources:
            if hasattr(resource, '_provider') and resource._provider:
                provider_name = resource._provider.__class__.__name__
                providers_needed.add((provider_name, resource._provider))

        # Register providers
        for provider_name, provider in providers_needed:
            if hasattr(provider, 'create_resource'):
                # Check if it's an async provider
                if asyncio.iscoroutinefunction(provider.create_resource):
                    provider_manager.register_async_provider(provider_name, provider)
                    console.print(f"Registered async provider: {provider_name}")
                else:
                    provider_manager.register_sync_provider(provider_name, provider)
                    console.print(f"Registered sync provider: {provider_name} (with async adapter)")
                
                managed_provider = provider_manager.get_provider(provider_name)
                if managed_provider:
                    engine.register_provider(provider_name, managed_provider)

    async def _check_provider_health(
        self, 
        provider_manager: AsyncProviderManager, 
        console: "Console"
    ) -> None:
        """Check health of all providers"""
        console.print("Checking provider health...")
        
        health_results = await provider_manager.health_check_all()
        
        for provider_name, is_healthy in health_results.items():
            if is_healthy:
                console.print(f"✅ {provider_name}: healthy")
            else:
                console.error(f"❌ {provider_name}: unhealthy")
                raise CommandError(f"Provider {provider_name} is unhealthy")

    async def _check_drift(
        self, 
        engine: AsyncNexusEngine, 
        resources: List[Any], 
        console: "Console", 
        force: bool
    ) -> None:
        """Check for drift in resources"""
        console.print("Checking for drift...")
        
        # Check drift for all resources in parallel
        tasks = []
        for resource in resources:
            if hasattr(resource, 'check_drift'):
                tasks.append(resource.check_drift())
        
        drift_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        drift_detected = False
        for i, result in enumerate(drift_results):
            if isinstance(result, Exception):
                console.error(f"Failed to check drift for {resources[i].name}: {result}")
                continue
            
            if isinstance(result, dict) and result.get("drifted", False):
                drift_detected = True
                console.warning(f"Drift detected in {resources[i].name}: {result.get('reason', 'Unknown')}")
        
        if drift_detected and not force:
            raise CommandError("Drift detected. Use --force to proceed anyway or fix the drift first.")

    async def _generate_plan(
        self, 
        engine: AsyncNexusEngine, 
        execution_plan: List[Any], 
        console: "Console"
    ) -> List[Dict[str, Any]]:
        """Generate execution plan"""
        console.print("Generating execution plan...")
        
        plan = []
        
        # Generate plans for each resource
        for resource in execution_plan:
            if hasattr(resource, 'preview'):
                resource_plan = await resource.preview()
                
                # Determine operation type
                if resource_plan.get("action") == "create":
                    plan.append({
                        "type": "create",
                        "resource": resource.name,
                        "changes": resource_plan.get("diff", {}),
                        "resource_plan": resource_plan
                    })
                elif resource_plan.get("action") == "update":
                    plan.append({
                        "type": "update",
                        "resource": resource.name,
                        "changes": resource_plan.get("diff", {}),
                        "resource_plan": resource_plan
                    })
        
        return plan

    async def _show_plan_and_confirm(
        self, 
        plan: List[Dict[str, Any]], 
        console: "Console"
    ) -> None:
        """Show execution plan and get user confirmation"""
        console.print("\n📋 Execution Plan:")
        
        total_operations = len(plan)
        for op in plan:
            console.print(f"  {op['type'].upper()} {op['resource']}")
            if op["changes"]:
                for key, change in op["changes"].items():
                    if isinstance(change, dict):
                        console.print(f"    {key}: {change.get('current')} -> {change.get('desired')}")
                    else:
                        console.print(f"    {key}: {change}")
        
        console.print(f"\nTotal operations: {total_operations}")
        
        # Get confirmation
        response = input("\nDo you want to proceed? (yes/no): ").lower()
        if response not in ['yes', 'y']:
            raise CommandError("Apply cancelled by user")

    async def _execute_plan(
        self, 
        engine: AsyncNexusEngine, 
        plan: List[Dict[str, Any]], 
        console: "Console",
        parallelism: int,
        timeout: int,
        batch_size: int
    ) -> None:
        """Execute the infrastructure plan"""
        console.print(f"\n🚀 Executing plan with parallelism={parallelism}, timeout={timeout}s")
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(parallelism)
        
        # Execute all resources in parallel (they're already dependency-ordered)
        tasks = []
        for operation in plan:
            resource = self._find_resource_by_name(operation["resource"])
            if resource:
                task = self._execute_resource(resource, semaphore, timeout, console)
                tasks.append(task)
        
        # Wait for all resources to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for errors
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                console.error(f"Failed to execute resource: {result}")
                raise CommandError(f"Execution failed: {result}")
            else:
                console.print(f"✅ Resource completed successfully")

    async def _execute_resource(
        self, 
        resource: Any, 
        semaphore: asyncio.Semaphore,
        timeout: int,
        console: "Console"
    ) -> Any:
        """Execute a single resource with timeout and concurrency control"""
        async with semaphore:
            try:
                # Set timeout for the operation
                if hasattr(resource, 'create'):
                    return await asyncio.wait_for(
                        resource.create(), 
                        timeout=timeout
                    )
                else:
                    console.warning(f"Resource {resource.name} doesn't support async operations")
                    return resource
                    
            except asyncio.TimeoutError:
                raise CommandError(f"Resource {resource.name} timed out after {timeout} seconds")
            except Exception as e:
                raise CommandError(f"Failed to execute resource {resource.name}: {e}")

    def _find_resource_by_name(self, name: str) -> Optional[Any]:
        """Find resource by name"""
        return getattr(self, '_resources', {}).get(name)