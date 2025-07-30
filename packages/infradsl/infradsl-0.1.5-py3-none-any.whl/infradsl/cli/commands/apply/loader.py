"""
Infrastructure Loader - handles loading and filtering resources
"""

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, List
from dotenv import load_dotenv

from ...utils.errors import CommandError

if TYPE_CHECKING:
    from ...utils.output import Console


class InfrastructureLoader:
    """Loads infrastructure resources from Python files"""

    def load_infrastructure(self, file_path: Path, console: "Console") -> List[Any]:
        """Load infrastructure resources from Python file"""
        # Load environment variables first
        self._load_environment_variables(file_path, console)
        
        # Load the Python module
        import importlib.util

        spec = importlib.util.spec_from_file_location("infrastructure", file_path)
        if spec is None or spec.loader is None:
            raise CommandError(f"Cannot load infrastructure file: {file_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Extract resources from module
        resources = []
        for name in dir(module):
            obj = getattr(module, name)
            # Only include instances, not classes
            if (
                hasattr(obj, "_resource_type")
                and hasattr(obj, "name")
                and not isinstance(obj, type)
            ):
                resources.append(obj)

        console.debug(f"Loaded {len(resources)} resources from {file_path}")
        return resources

    def filter_resources(
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

    def _load_environment_variables(self, file_path: Path, console: "Console") -> None:
        """Load environment variables from .env file"""
        # ALWAYS load .env file if it exists - this is the Rails way
        env_path = file_path.parent / ".env"
        console.info(f"Checking for .env at: {env_path}")
        if env_path.exists():
            load_dotenv(env_path)
            console.info(f"Loaded environment from {env_path}")
        else:
            # Also check current working directory
            current_env = Path(".env")
            console.info(f"Checking for .env at: {current_env.absolute()}")
            if current_env.exists():
                load_dotenv()
                console.info("Loaded environment from .env")
            else:
                console.info("No .env file found")

        # Debug: Check if DIGITALOCEAN_TOKEN is loaded
        token = os.getenv("DIGITALOCEAN_TOKEN")
        if token:
            console.debug(f"DIGITALOCEAN_TOKEN is set: {token[:10]}...")
        else:
            console.debug("DIGITALOCEAN_TOKEN is not set")