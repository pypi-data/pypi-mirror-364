"""
HTTP Server Discovery - Infrastructure resource discovery logic
"""

import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone

from infradsl.core.nexus.base_resource import (
    BaseResource,
    ResourceMetadata,
    ResourceStatus,
    ResourceState,
)

logger = logging.getLogger(__name__)


class InfrastructureDiscovery:
    """Handles discovery of real infrastructure resources from cloud providers"""
    
    def __init__(self):
        self.providers_registered = 0
    
    async def discover_infrastructure_resources(self) -> Dict[str, Any]:
        """Discover real infrastructure resources from cloud providers"""
        from dotenv import load_dotenv

        # Load environment variables
        try:
            load_dotenv()
        except Exception:
            pass

        try:
            from infradsl.core.state.engine import StateEngine
            from infradsl.core.interfaces.provider import ProviderConfig, ProviderType

            # Use file-based storage for caching
            engine = StateEngine(storage_backend="file")

            self.providers_registered = 0

            # Try to register DigitalOcean provider
            await self._register_digitalocean_provider(engine)

            # Try to register GCP provider
            await self._register_gcp_provider(engine)

            # Try to register AWS provider
            await self._register_aws_provider(engine)

            if self.providers_registered == 0:
                logger.info("No providers registered for discovery")
                return {}

            # Discover resources with a reasonable timeout
            logger.info(f"Starting discovery with {self.providers_registered} providers...")
            discovered_resources = engine.discover_all_resources(
                update_storage=True,
                timeout=5,  # 5 seconds timeout for better reliability
            )

            logger.info(
                f"Discovered {len(discovered_resources)} resources from {self.providers_registered} providers"
            )
            return discovered_resources

        except Exception as e:
            logger.error(f"Error during resource discovery: {e}")
            import traceback

            logger.error(f"Discovery traceback: {traceback.format_exc()}")

            # Return empty dict with error info for debugging
            return {
                "_error": {
                    "message": str(e),
                    "type": type(e).__name__,
                    "providers_attempted": self.providers_registered,
                }
            }
    
    async def _register_digitalocean_provider(self, engine):
        """Register DigitalOcean provider if credentials available"""
        try:
            from infradsl.providers.digitalocean import DigitalOceanProvider
            from infradsl.core.interfaces.provider import ProviderConfig, ProviderType

            token = os.getenv("DIGITALOCEAN_TOKEN")
            if token:
                config = ProviderConfig(
                    type=ProviderType.DIGITAL_OCEAN,
                    credentials={"token": token},
                    region="nyc1",
                )
                provider = DigitalOceanProvider(config=config)
                engine.register_provider("digitalocean", provider)
                self.providers_registered += 1
                logger.info("Registered DigitalOcean provider")
        except Exception as e:
            logger.debug(f"Could not register DigitalOcean provider: {e}")
    
    async def _register_gcp_provider(self, engine):
        """Register GCP provider if credentials available"""
        try:
            from infradsl.providers.gcp import GCPComputeProvider
            from infradsl.core.interfaces.provider import ProviderConfig, ProviderType

            project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
            region = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

            if not project_id:
                service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                if service_account_path and os.path.exists(service_account_path):
                    with open(service_account_path) as f:
                        creds = json.load(f)
                    project_id = creds.get("project_id")

            if project_id:
                config = ProviderConfig(
                    type=ProviderType.GCP, project=project_id, region=region
                )
                provider = GCPComputeProvider(config=config)
                engine.register_provider("gcp", provider)
                self.providers_registered += 1
                logger.info("Registered GCP provider")
        except Exception as e:
            logger.debug(f"Could not register GCP provider: {e}")
    
    async def _register_aws_provider(self, engine):
        """Register AWS provider if credentials available"""
        try:
            from infradsl.providers.aws_provider import AWSProvider
            from infradsl.core.interfaces.provider import ProviderConfig, ProviderType

            config = ProviderConfig(
                type=ProviderType.AWS, region=os.getenv("AWS_REGION", "us-east-1")
            )
            provider = AWSProvider(config)
            engine.register_provider("aws", provider)
            self.providers_registered += 1
            logger.info("Registered AWS provider")
        except Exception as e:
            logger.debug(f"Could not register AWS provider: {e}")
    
    def convert_to_base_resources(
        self, discovered_resources: Dict[str, Any]
    ) -> List[BaseResource]:
        """Convert discovered resources to BaseResource format for the graph builder"""
        base_resources = []

        for resource_id, resource_data in discovered_resources.items():
            try:
                # Create metadata
                metadata = ResourceMetadata(
                    id=resource_data.get("id", resource_id),
                    name=resource_data.get("name", resource_id),
                    project=resource_data.get("project", "default"),
                    environment=resource_data.get("environment", "unknown"),
                    labels=resource_data.get("tags", []),
                    annotations={},
                    created_at=datetime.now(timezone.utc),
                )

                # Create status
                status = ResourceStatus(
                    state=(
                        ResourceState.ACTIVE
                        if resource_data.get("state") == "active"
                        else ResourceState.PENDING
                    ),
                    message=f"Discovered from {resource_data.get('provider', 'unknown')} provider",
                )

                # Create a simple BaseResource-like object for the graph builder
                class DiscoveredResource:
                    def __init__(self, resource_data, metadata, status):
                        self.metadata = metadata
                        self.status = status
                        self.id = metadata.id
                        self.name = metadata.name
                        self.provider = resource_data.get("provider", "unknown")
                        self._resource_type = resource_data.get(
                            "type", "VirtualMachine"
                        )
                        self._dependencies = []
                        self.tags = resource_data.get("tags", [])

                    def dict(self):
                        return {
                            "id": self.id,
                            "name": self.name,
                            "type": self._resource_type,
                            "provider": self.provider,
                            "state": self.status.state.value,
                            "metadata": {
                                "project": self.metadata.project,
                                "environment": self.metadata.environment,
                            },
                        }

                resource = DiscoveredResource(resource_data, metadata, status)
                base_resources.append(resource)

            except Exception as e:
                logger.debug(f"Failed to convert resource {resource_id}: {e}")
                continue

        # Check for discovery errors
        if "_error" in discovered_resources:
            error_info = discovered_resources["_error"]
            logger.warning(f"Discovery had errors: {error_info['message']}")
            # Return empty list with error info in metadata
            base_resources.append(self._create_error_resource(error_info))

        logger.info(f"Converted {len(base_resources)} resources to BaseResource format")
        return base_resources
    
    def _create_error_resource(self, error_info):
        """Create a dummy resource to show discovery errors in the UI"""
        metadata = ResourceMetadata(
            id="discovery-error",
            name="Discovery Error",
            project="system",
            environment="error",
            labels=[],
            annotations={"error": error_info["message"]},
            created_at=datetime.now(timezone.utc),
        )

        status = ResourceStatus(
            state=ResourceState.FAILED,
            message=f"Discovery failed: {error_info['message']}",
        )

        class ErrorResource:
            def __init__(self, error_info, metadata, status):
                self.metadata = metadata
                self.status = status
                self.id = metadata.id
                self.name = metadata.name
                self.provider = "system"
                self._resource_type = "error"
                self._dependencies = []
                self.tags = [f"error:{error_info['type']}"]

            def dict(self):
                return {
                    "id": self.id,
                    "name": self.name,
                    "type": "error",
                    "provider": "system",
                    "state": "failed",
                    "error": error_info["message"],
                }

        return ErrorResource(error_info, metadata, status)