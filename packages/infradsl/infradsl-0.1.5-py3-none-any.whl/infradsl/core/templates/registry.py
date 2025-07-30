from typing import Dict, Any, List, Optional, Type, Union
import os
import json
import importlib
import inspect
from pathlib import Path
from urllib.parse import urlparse
import logging

from .base import BaseTemplate, TemplateMetadata


class TemplateRegistry:
    """
    Template Registry for discovering, loading, and managing infrastructure templates.
    
    The registry supports multiple sources:
    - Local directory-based registries
    - Remote HTTP/HTTPS registries
    - Git-based registries  
    - Package-based registries
    
    Templates are discovered dynamically and can be loaded on-demand.
    """
    
    def __init__(self):
        self._templates: Dict[str, Type[BaseTemplate]] = {}
        self._template_cache: Dict[str, BaseTemplate] = {}
        self._registry_sources: List[Dict[str, Any]] = []
        self._metadata_cache: Dict[str, TemplateMetadata] = {}
        self.logger = logging.getLogger(__name__)
        
        # Default registry locations
        self._setup_default_registries()
        
    def _setup_default_registries(self):
        """Setup default template registry locations"""
        # Register built-in templates first (highest priority)
        self._register_builtin_templates()
        
        # Local user registry
        user_registry = Path.home() / ".infradsl" / "templates"
        if user_registry.exists():
            self.add_local_registry(str(user_registry))
            
        # Built-in templates (as fallback from files)
        builtin_registry = Path(__file__).parent.parent.parent / "templates" / "builtin"
        if builtin_registry.exists():
            self.add_local_registry(str(builtin_registry), priority=1)
        
        # Project-local templates
        project_registry = Path.cwd() / "infra_templates"
        if project_registry.exists():
            self.add_local_registry(str(project_registry), priority=2)
            
    def _register_builtin_templates(self):
        """Register built-in templates directly"""
        # Disable automatic built-in template registration to avoid circular imports
        # Templates will be loaded dynamically when requested via Template.TemplateName()
        self.logger.info("Built-in templates will be loaded on demand")
        return
        
        # try:
        #     # Import built-in templates
        #     from ...templates.builtin.generic_vm import GenericVMTemplate
        #     from ...templates.builtin.web_app import WebAppTemplate
        #     from ...templates.builtin.database import DatabaseTemplate
        #     
        #     # Register templates directly
        #     self._templates["GenericVM"] = GenericVMTemplate
        #     self._templates["WebApp"] = WebAppTemplate  
        #     self._templates["Database"] = DatabaseTemplate
        #     
        #     # Cache metadata
        #     for name, template_class in self._templates.items():
        #         try:
        #             temp_instance = template_class("temp")
        #             metadata = temp_instance._create_metadata()
        #             self._metadata_cache[name] = metadata
        #         except Exception as e:
        #             self.logger.warning(f"Failed to cache metadata for {name}: {e}")
        #             
        #     self.logger.info(f"Registered {len(self._templates)} built-in templates")
        #     
        # except ImportError as e:
        #     self.logger.warning(f"Failed to import built-in templates: {e}")
        # except Exception as e:
        #     self.logger.error(f"Failed to register built-in templates: {e}")
            
    def add_local_registry(self, path: str, priority: int = 0):
        """Add local directory-based registry"""
        registry_config = {
            "type": "local",
            "path": path,
            "priority": priority,
            "enabled": True
        }
        self._registry_sources.append(registry_config)
        self._registry_sources.sort(key=lambda x: x.get("priority", 0), reverse=True)
        
    def add_remote_registry(self, url: str, priority: int = 0, auth_token: str = None):
        """Add remote HTTP/HTTPS registry"""
        registry_config = {
            "type": "remote",
            "url": url,
            "priority": priority,
            "enabled": True,
            "auth_token": auth_token
        }
        self._registry_sources.append(registry_config)
        self._registry_sources.sort(key=lambda x: x.get("priority", 0), reverse=True)
        
    def add_git_registry(self, repo_url: str, branch: str = "main", priority: int = 0):
        """Add Git-based registry"""
        registry_config = {
            "type": "git",
            "repo_url": repo_url,
            "branch": branch,
            "priority": priority,
            "enabled": True
        }
        self._registry_sources.append(registry_config)
        self._registry_sources.sort(key=lambda x: x.get("priority", 0), reverse=True)
        
    def discover_templates(self, force_refresh: bool = False) -> List[TemplateMetadata]:
        """Discover all available templates from registries"""
        if force_refresh:
            self._templates.clear()
            self._metadata_cache.clear()
            
        all_metadata = []
        
        for registry in self._registry_sources:
            if not registry.get("enabled", True):
                continue
                
            try:
                metadata_list = self._discover_from_registry(registry)
                all_metadata.extend(metadata_list)
            except Exception as e:
                self.logger.warning(f"Failed to discover templates from {registry}: {e}")
                
        return all_metadata
        
    def _discover_from_registry(self, registry: Dict[str, Any]) -> List[TemplateMetadata]:
        """Discover templates from a specific registry"""
        registry_type = registry["type"]
        
        if registry_type == "local":
            return self._discover_local(registry["path"])
        elif registry_type == "remote":
            return self._discover_remote(registry["url"], registry.get("auth_token"))
        elif registry_type == "git":
            return self._discover_git(registry["repo_url"], registry.get("branch", "main"))
        else:
            raise ValueError(f"Unsupported registry type: {registry_type}")
            
    def _discover_local(self, registry_path: str) -> List[TemplateMetadata]:
        """Discover templates from local directory"""
        templates = []
        registry_dir = Path(registry_path)
        
        if not registry_dir.exists():
            return templates
            
        # Look for template.py files or template directories
        for item in registry_dir.iterdir():
            if item.is_file() and item.name == "template.py":
                # Single template file
                metadata = self._load_local_template_metadata(item)
                if metadata:
                    templates.append(metadata)
            elif item.is_dir():
                # Template directory
                template_file = item / "template.py"
                metadata_file = item / "metadata.json"
                
                if template_file.exists():
                    if metadata_file.exists():
                        # Load metadata from JSON
                        metadata = self._load_metadata_json(metadata_file)
                    else:
                        # Load metadata from Python file
                        metadata = self._load_local_template_metadata(template_file)
                    
                    if metadata:
                        templates.append(metadata)
                        
        return templates
        
    def _discover_remote(self, registry_url: str, auth_token: str = None) -> List[TemplateMetadata]:
        """Discover templates from remote registry"""
        # This would make HTTP requests to discover templates
        # Implementation would depend on the registry API format
        templates = []
        
        # TODO: Implement remote template discovery
        # This would involve:
        # 1. GET request to registry API
        # 2. Parse response for template listings
        # 3. Create TemplateMetadata objects
        
        return templates
        
    def _discover_git(self, repo_url: str, branch: str = "main") -> List[TemplateMetadata]:
        """Discover templates from Git repository"""
        templates = []
        
        # TODO: Implement Git-based template discovery
        # This would involve:
        # 1. Clone or fetch repository
        # 2. Scan for template files
        # 3. Load metadata
        
        return templates
        
    def _load_local_template_metadata(self, template_file: Path) -> Optional[TemplateMetadata]:
        """Load template metadata from local Python file"""
        try:
            # Import the template module dynamically
            spec = importlib.util.spec_from_file_location("template", template_file)
            if not spec or not spec.loader:
                return None
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find template classes in the module
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseTemplate) and obj != BaseTemplate:
                    # Create instance to get metadata
                    try:
                        temp_instance = obj("temp")
                        metadata = temp_instance._create_metadata()
                        self._templates[metadata.name] = obj
                        return metadata
                    except Exception as e:
                        self.logger.warning(f"Failed to load template {name}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Failed to load template from {template_file}: {e}")
            
        return None
        
    def _load_metadata_json(self, metadata_file: Path) -> Optional[TemplateMetadata]:
        """Load template metadata from JSON file"""
        try:
            with open(metadata_file, 'r') as f:
                data = json.load(f)
            return TemplateMetadata.from_dict(data)
        except Exception as e:
            self.logger.error(f"Failed to load metadata from {metadata_file}: {e}")
            return None
            
    def get_template(self, name: str, version: str = "latest") -> Optional[Type[BaseTemplate]]:
        """Get template class by name and version"""
        # First check if template is already loaded
        if name in self._templates:
            return self._templates[name]
            
        # Try to discover templates if not found
        self.discover_templates()
        
        return self._templates.get(name)
        
    def create_template(self, template_name: str, instance_name: str, **kwargs) -> Optional[BaseTemplate]:
        """Create template instance by name"""
        template_class = self.get_template(template_name)
        if not template_class:
            raise ValueError(f"Template '{template_name}' not found in any registry")
            
        return template_class(instance_name, **kwargs)
        
    def list_templates(self, category: str = None, tags: List[str] = None) -> List[TemplateMetadata]:
        """List available templates with optional filtering"""
        templates = self.discover_templates()
        
        # Apply filters
        if category:
            templates = [t for t in templates if t.category == category]
            
        if tags:
            templates = [t for t in templates if any(tag in t.tags for tag in tags)]
            
        return templates
        
    def search_templates(self, query: str) -> List[TemplateMetadata]:
        """Search templates by name, description, or tags"""
        templates = self.discover_templates()
        query_lower = query.lower()
        
        results = []
        for template in templates:
            if (query_lower in template.name.lower() or
                query_lower in template.description.lower() or
                any(query_lower in tag.lower() for tag in template.tags)):
                results.append(template)
                
        return results
        
    def get_template_metadata(self, name: str) -> Optional[TemplateMetadata]:
        """Get template metadata by name"""
        if name in self._metadata_cache:
            return self._metadata_cache[name]
            
        template_class = self.get_template(name)
        if template_class:
            try:
                temp_instance = template_class("temp")
                metadata = temp_instance._create_metadata()
                self._metadata_cache[name] = metadata
                return metadata
            except Exception as e:
                self.logger.error(f"Failed to get metadata for template {name}: {e}")
                
        return None
        
    def validate_template(self, template: BaseTemplate) -> List[str]:
        """Validate template configuration and dependencies"""
        errors = []
        
        # Check required dependencies
        metadata = template.get_metadata()
        for required_template in metadata.requires:
            if not self.get_template(required_template):
                errors.append(f"Required template '{required_template}' not found")
                
        # Validate parameters against schema
        try:
            template._validate_parameters()
        except ValueError as e:
            errors.append(str(e))
            
        return errors
        
    def publish_template(self, template: BaseTemplate, registry_url: str = None):
        """Publish template to registry"""
        # TODO: Implement template publishing
        # This would involve:
        # 1. Package template files
        # 2. Upload to registry
        # 3. Update registry index
        pass
        
    def update_template(self, name: str, version: str = None):
        """Update template from registry"""
        # TODO: Implement template updates
        # This would involve:
        # 1. Check for newer versions
        # 2. Download updates
        # 3. Update local cache
        pass
        
    def remove_template(self, name: str):
        """Remove template from local cache"""
        if name in self._templates:
            del self._templates[name]
        if name in self._template_cache:
            del self._template_cache[name]
        if name in self._metadata_cache:
            del self._metadata_cache[name]


# Global registry instance
_global_registry: Optional[TemplateRegistry] = None

def get_global_registry() -> TemplateRegistry:
    """Get the global template registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = TemplateRegistry()
    return _global_registry