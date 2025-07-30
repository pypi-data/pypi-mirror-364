"""
Example: Async Infrastructure Operations with InfraDSL

This example demonstrates how to use the async capabilities of InfraDSL
for high-performance infrastructure operations.
"""

import asyncio
from pathlib import Path
import sys

# Add the project root to the path so we can import infradsl
sys.path.insert(0, str(Path(__file__).parent.parent))

from infradsl.core.engines.async_engine import AsyncNexusEngine
from infradsl.core.adapters.async_provider_adapter import AsyncProviderManager
from infradsl.core.nexus.async_base_resource import AsyncBaseResource
from infradsl.core.nexus.base_resource import ResourceMetadata, ResourceSpec
from infradsl.core.interfaces.provider import ProviderConfig, ProviderType
from infradsl.providers.digitalocean.provider import DigitalOceanProvider
from infradsl.providers.aws.provider import AWSProvider
from infradsl.providers.gcp.provider import GCPComputeProvider


# Example async resource implementation
class AsyncDropletResource(AsyncBaseResource):
    """Example async droplet resource"""

    def __init__(self, name: str):
        super().__init__(name)
        self.region = "nyc1"
        self.size = "s-1vcpu-1gb"
        self.image = "ubuntu-22-04-x64"

    def _create_spec(self) -> ResourceSpec:
        return ResourceSpec()

    def _validate_spec(self) -> None:
        if not self.metadata.name:
            raise ValueError("Name is required")

    def _to_provider_config(self) -> dict:
        return {
            "name": self.metadata.name,
            "region": self.region,
            "size": self.size,
            "image": self.image,
            "tags": self.metadata.to_tags(),
        }

    async def _provider_create(self) -> dict:
        """Create droplet via provider"""
        return await self._execute_with_provider(
            "create_resource", "droplet", self._to_provider_config(), self.metadata
        )

    async def _provider_update(self, diff: dict) -> dict:
        """Update droplet via provider"""
        return await self._execute_with_provider(
            "update_resource", self.status.cloud_id, "droplet", diff
        )

    async def _provider_destroy(self) -> None:
        """Destroy droplet via provider"""
        await self._execute_with_provider(
            "delete_resource", self.status.cloud_id, "droplet"
        )


async def main():
    """Main async function demonstrating async operations"""
    print("🚀 Starting async infrastructure operations example")

    # Initialize async engine and provider manager
    engine = AsyncNexusEngine()
    provider_manager = AsyncProviderManager()

    # Setup DigitalOcean provider (sync provider with async adapter)
    do_config = ProviderConfig(
        type=ProviderType.DIGITAL_OCEAN,
        credentials={"token": "your_token_here"},  # Replace with real token
    )

    try:
        do_provider = DigitalOceanProvider(do_config)
        provider_manager.register_sync_provider("digitalocean", do_provider)
        provider = provider_manager.get_provider("digitalocean")
        if provider:
            engine.register_provider("digitalocean", provider)
            print("✅ DigitalOcean provider registered with async adapter")
        else:
            print("❌ Failed to get DigitalOcean provider from manager")
    except Exception as e:
        print(f"⚠️  DigitalOcean provider setup failed: {e}")

    # Example 1: Health check all providers
    print("\n📊 Checking provider health...")
    health_results = await provider_manager.health_check_all()
    for provider_name, is_healthy in health_results.items():
        status = "✅ healthy" if is_healthy else "❌ unhealthy"
        print(f"  {provider_name}: {status}")

    # Example 2: Create multiple resources in parallel
    print("\n🏗️  Creating multiple resources in parallel...")

    resources = []
    provider = provider_manager.get_provider("digitalocean")
    if not provider:
        print("❌ No DigitalOcean provider available, skipping resource creation")
        return

    for i in range(3):
        droplet = AsyncDropletResource(f"async-droplet-{i}")
        droplet.with_project("async-example")
        droplet.with_environment("development")
        droplet.with_provider(provider)
        resources.append(droplet)

    # Preview all resources in parallel
    print("\n👀 Previewing resources...")
    preview_tasks = [resource.preview() for resource in resources]
    preview_results = await asyncio.gather(*preview_tasks, return_exceptions=True)

    for i, result in enumerate(preview_results):
        if isinstance(result, Exception):
            print(f"  ❌ Preview failed for resource {i}: {result}")
        elif isinstance(result, dict):
            print(f"  ✅ Resource {i} preview: {result.get('action', 'unknown')}")
        else:
            print(f"  ⚠️  Resource {i} preview: unexpected result type")

    # Batch create resources (commented out to avoid actually creating resources)
    # print("\n🚀 Creating resources in batch...")
    # created_resources = await AsyncBaseResource.batch_create(resources)
    # print(f"Created {len(created_resources)} resources")

    # Example 3: Discover resources across providers
    print("\n🔍 Discovering resources across providers...")
    discovery_results = await engine.discover_all_resources()

    for provider_name, resource_types in discovery_results.items():
        print(f"  📦 {provider_name}:")
        for resource_type, resource_list in resource_types.items():
            print(f"    {resource_type}: {len(resource_list)} resources")

    # Example 4: Batch operations
    print("\n⚡ Demonstrating batch operations...")

    # Batch planning operations
    operations = [
        {
            "provider": "digitalocean",
            "action": "create",
            "resource_type": "droplet",
            "config": {
                "name": f"batch-droplet-{i}",
                "region": "nyc1",
                "size": "s-1vcpu-1gb",
                "image": "ubuntu-22-04-x64",
            },
            "metadata": ResourceMetadata(name=f"batch-droplet-{i}"),
        }
        for i in range(3)
    ]

    batch_plans = await engine.batch_plan_operations(operations)
    print(f"Generated {len(batch_plans)} plans in batch")

    for i, plan in enumerate(batch_plans):
        if isinstance(plan, Exception):
            print(f"  ❌ Plan {i} failed: {plan}")
        elif isinstance(plan, dict):
            print(f"  ✅ Plan {i}: {plan.get('action', 'unknown')}")
        else:
            print(f"  ⚠️  Plan {i}: unexpected result type")

    # Example 5: Dependency resolution and parallel execution
    print("\n🔗 Demonstrating dependency resolution...")

    # Create resources with dependencies
    database = AsyncDropletResource("database-server")
    database.with_provider(provider)

    app_server = AsyncDropletResource("app-server")
    app_server.depends_on(database)  # App server depends on database
    app_server.with_provider(provider)

    load_balancer = AsyncDropletResource("load-balancer")
    load_balancer.depends_on(app_server)  # Load balancer depends on app server
    load_balancer.with_provider(provider)

    # Resolve dependencies for load balancer
    dependency_chain = await load_balancer.resolve_dependencies()
    print(f"Dependency chain: {[r.name for r in dependency_chain]}")

    # Example 6: Parallel drift detection
    print("\n🔍 Parallel drift detection...")
    drift_results = await AsyncBaseResource.batch_check_drift(resources)

    for i, result in enumerate(drift_results):
        if isinstance(result, Exception):
            print(f"  ❌ Drift check failed for resource {i}: {result}")
        elif isinstance(result, dict):
            drift_status = "drifted" if result.get("drifted", False) else "in sync"
            print(f"  📊 Resource {i}: {drift_status}")
        else:
            print(f"  ⚠️  Resource {i}: unexpected result type")

    # Cleanup
    provider_manager.cleanup()
    print("\n✅ Async infrastructure operations example completed!")


if __name__ == "__main__":
    # Run the async example
    asyncio.run(main())
