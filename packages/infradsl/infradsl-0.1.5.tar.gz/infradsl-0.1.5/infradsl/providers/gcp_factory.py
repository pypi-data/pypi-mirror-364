"""
Google Cloud Provider - Simple factory for GCP resources
"""

from typing import Any, Dict, Optional

from ..resources.compute.virtual_machine import VirtualMachine
from ..resources.network.cloud_dns import CloudDNS
from ..core.nexus import get_registry
from ..core.interfaces.provider import ProviderType, ProviderConfig


class GoogleCloud:
    """
    Google Cloud provider factory for creating resources.

    Usage:
        vm = GoogleCloud.VM("my-vm").ubuntu().create()
        app = GoogleCloud.CloudRun("my-app").container("web", "./src", 8080).create()
    """

    _default_config: Optional[ProviderConfig] = None

    @classmethod
    def configure(
        cls,
        project: str,
        region: str = "us-central1",
        credentials: Optional[Dict[str, Any]] = None,
        service_account_file: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Configure GCP provider defaults
        
        Args:
            project: GCP project ID
            region: Default region for resources
            credentials: Dict with credential configuration
            service_account_file: Path to service account JSON file
            **kwargs: Additional provider options
            
        Examples:
            # Using service account file
            GoogleCloud.configure(
                project="my-project",
                service_account_file="./service-account.json"
            )
            
            # Using environment credentials
            GoogleCloud.configure(project="my-project")
        """
        # If service_account_file is provided, use it
        if service_account_file and not credentials:
            credentials = {"service_account_path": service_account_file}
        
        cls._default_config = ProviderConfig(
            type=ProviderType.GCP,
            project=project,
            region=region,
            credentials=credentials,
            options=kwargs,
        )

    @classmethod
    def _get_provider(cls):
        """Get GCP provider instance"""
        # Auto-load .env file if it exists - Rails way!
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass  # dotenv is optional but recommended
            
        if not cls._default_config:
            # Try to get project from environment or gcloud config
            import os
            import subprocess
            
            project = os.getenv("GOOGLE_CLOUD_PROJECT")
            if not project:
                # Try to get from gcloud config
                try:
                    result = subprocess.run(
                        ["gcloud", "config", "get-value", "project"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        project = result.stdout.strip()
                    else:
                        project = "your-project-id"  # Fallback
                except Exception:
                    project = "your-project-id"  # Fallback
            
            region = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
            
            cls._default_config = ProviderConfig(
                type=ProviderType.GCP, 
                region=region,
                project=project
            )

        registry = get_registry()
        return registry.create_provider(ProviderType.GCP, cls._default_config)

    @classmethod
    def VM(cls, name: str) -> VirtualMachine:
        """Create a Compute Engine instance"""
        vm = VirtualMachine(name)
        provider = cls._get_provider()
        vm._provider = provider
        
        # Store reference to update provider config when zone is set
        original_zone_method = vm.zone
        def zone_with_provider_update(zone_name):
            # Handle both string and Region enum values
            from ..regions import Region
            if isinstance(zone_name, Region):
                zone_str = zone_name.value
            else:
                zone_str = str(zone_name)
            
            # Extract region from zone (e.g., "europe-west1-b" -> "europe-west1")
            if '-' in zone_str:
                zone_parts = zone_str.split('-')
                if len(zone_parts) >= 2:
                    region = '-'.join(zone_parts[:-1])
                    # Update provider config region
                    if hasattr(provider, 'config'):
                        provider.config.region = region
            
            # Call original zone method
            return original_zone_method(zone_name)
        
        # Replace the zone method to update provider config
        vm.zone = zone_with_provider_update
        return vm

    @classmethod
    def Instance(cls, name: str) -> VirtualMachine:
        """Alias for VM"""
        return cls.VM(name)

    @classmethod
    def ComputeEngine(cls, name: str) -> VirtualMachine:
        """Alias for VM"""
        return cls.VM(name)

    @classmethod
    def CloudDNS(cls, name: str) -> CloudDNS:
        """Create a Cloud DNS zone"""
        dns = CloudDNS(name)
        provider = cls._get_provider()
        dns._provider = provider
        return dns

    @classmethod
    def DNS(cls, name: str) -> CloudDNS:
        """Alias for CloudDNS"""
        return cls.CloudDNS(name)

    # TODO: Add other GCP resources
    # @classmethod
    # def CloudRun(cls, name: str) -> CloudRunService:
    #     """Create a Cloud Run service"""
    #     pass

    # @classmethod
    # def GKE(cls, name: str) -> GKECluster:
    #     """Create a GKE cluster"""
    #     pass
