"""
Resource Loader Module - handles infrastructure file loading and filtering
"""

import logging
from pathlib import Path
from typing import Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ...utils.output import Console

logger = logging.getLogger(__name__)


class ResourceLoader:
    """Handles loading and filtering of infrastructure resources"""

    def load_infrastructure(self, infrastructure_file: Path, console: "Console") -> List[Any]:
        """Load infrastructure from Python file"""
        import importlib.util
        import sys
        from dotenv import load_dotenv
        
        try:
            # Load environment variables first
            self._load_environment_variables(infrastructure_file, console)
            
            # Load the Python file as a module
            spec = importlib.util.spec_from_file_location("infrastructure", infrastructure_file)
            if spec is None or spec.loader is None:
                console.error(f"Could not load infrastructure file: {infrastructure_file}")
                return []

            module = importlib.util.module_from_spec(spec)
            sys.modules["infrastructure"] = module
            spec.loader.exec_module(module)

            # Extract all resource instances
            resources = []
            for name in dir(module):
                obj = getattr(module, name)
                if self._is_infrastructure_resource(obj):
                    resources.append(obj)

            console.debug(f"Loaded {len(resources)} resources from {infrastructure_file}")
            return resources

        except Exception as e:
            console.error(f"Error loading infrastructure file: {e}")
            return []

    def filter_resources(self, resources: List[Any], targets: List[str], console: "Console") -> List[Any]:
        """Filter resources by target names"""
        if not targets:
            return resources

        filtered = []
        for resource in resources:
            resource_name = getattr(resource, 'name', str(resource))
            if resource_name in targets:
                filtered.append(resource)

        console.debug(f"Filtered to {len(filtered)} resources matching targets: {targets}")
        return filtered

    def _load_environment_variables(self, file_path: Path, console: "Console") -> None:
        """Load environment variables from .env file"""
        from dotenv import load_dotenv
        
        # ALWAYS load .env file if it exists - this is the Rails way
        env_path = file_path.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            console.debug(f"Loaded environment from {env_path}")
        else:
            # Also check current working directory
            current_env = Path(".env")
            if current_env.exists():
                load_dotenv()
                console.debug("Loaded environment from .env")

    def _is_infrastructure_resource(self, obj: Any) -> bool:
        """Check if object is an infrastructure resource"""
        # Skip property objects and other non-resource types
        if isinstance(obj, property) or callable(obj) or isinstance(obj, type):
            return False
            
        # Check for common resource attributes
        return (
            hasattr(obj, '_resource_type') and 
            hasattr(obj, 'name') and 
            not isinstance(getattr(obj, 'name', None), property) and
            (hasattr(obj, 'spec') or hasattr(obj, '_to_provider_config'))
        )