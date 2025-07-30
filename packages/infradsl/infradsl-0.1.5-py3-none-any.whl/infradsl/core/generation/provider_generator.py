"""
Provider Generation Tooling for InfraDSL

This module provides tools to automatically generate provider boilerplate code
from cloud provider APIs, OpenAPI specifications, and Terraform schemas.
"""

import json
import os
import re
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from enum import Enum
import yaml
import requests
from jinja2 import Template, Environment, FileSystemLoader

logger = logging.getLogger(__name__)


class ProviderType(Enum):
    """Supported provider types for generation"""
    
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    DIGITAL_OCEAN = "digitalocean"
    CLOUDFLARE = "cloudflare"
    KUBERNETES = "kubernetes"
    TERRAFORM = "terraform"
    OPENAPI = "openapi"


class ResourceType(Enum):
    """Types of resources that can be generated"""
    
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    SECURITY = "security"
    MONITORING = "monitoring"
    CONTAINER = "container"
    SERVERLESS = "serverless"


@dataclass
class ResourceField:
    """A field in a resource definition"""
    
    name: str
    type: str
    description: str = ""
    required: bool = False
    default_value: Any = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    examples: List[Any] = field(default_factory=list)


@dataclass
class ResourceDefinition:
    """Definition of a cloud resource"""
    
    name: str
    type: ResourceType
    provider: ProviderType
    description: str = ""
    fields: List[ResourceField] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # API-specific information
    api_endpoint: Optional[str] = None
    api_version: Optional[str] = None
    terraform_resource_type: Optional[str] = None


@dataclass
class GenerationConfig:
    """Configuration for provider generation"""
    
    provider_type: ProviderType
    output_directory: str
    template_directory: str = "templates"
    
    # Generation options
    generate_async: bool = True
    generate_tests: bool = True
    generate_docs: bool = True
    generate_examples: bool = True
    
    # Code style options
    use_dataclasses: bool = True
    use_type_hints: bool = True
    use_docstrings: bool = True
    
    # Provider-specific options
    provider_config: Dict[str, Any] = field(default_factory=dict)


class ProviderGenerator:
    """Main provider generation class"""
    
    def __init__(self, config: GenerationConfig):
        self.config = config
        self.resources: List[ResourceDefinition] = []
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Environment:
        """Load Jinja2 templates"""
        template_dir = Path(self.config.template_directory)
        if not template_dir.exists():
            template_dir.mkdir(parents=True)
            self._create_default_templates(template_dir)
        
        return Environment(loader=FileSystemLoader(str(template_dir)))
    
    def _create_default_templates(self, template_dir: Path) -> None:
        """Create default templates if they don't exist"""
        
        # Provider base template
        provider_template = '''"""
{{ provider_name|title }} Provider for InfraDSL
Generated on {{ generation_date }}
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ...interfaces.provider import ProviderInterface, ProviderConfig, ResourceQuery
from ...nexus.base_resource import ResourceMetadata

logger = logging.getLogger(__name__)


@dataclass
class {{ provider_name|title }}Config(ProviderConfig):
    """Configuration for {{ provider_name|title }} provider"""
    
    {% for field in config_fields %}
    {{ field.name }}: {{ field.type }} = {{ field.default_value or 'None' }}
    {% endfor %}


class {{ provider_name|title }}Provider(ProviderInterface):
    """{{ provider_name|title }} provider implementation"""
    
    def __init__(self, config: {{ provider_name|title }}Config):
        super().__init__(config)
        self.client = None
        
    def _validate_config(self) -> None:
        """Validate provider configuration"""
        required_fields = [{% for field in config_fields if field.required %}"{{ field.name }}"{% if not loop.last %}, {% endif %}{% endfor %}]
        
        for field in required_fields:
            if not getattr(self.config, field, None):
                raise ValueError(f"Missing required configuration: {field}")
    
    def _initialize(self) -> None:
        """Initialize provider connection"""
        try:
            # Initialize {{ provider_name }} client
            self.client = self._create_client()
            logger.info("{{ provider_name|title }} provider initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize {{ provider_name }} provider: {e}")
            raise
    
    def _create_client(self):
        """Create {{ provider_name }} client"""
        # Implementation depends on provider SDK
        pass
    
    {% for resource in resources %}
    def create_{{ resource.name.lower() }}(self, config: Dict[str, Any], metadata: ResourceMetadata) -> Dict[str, Any]:
        """Create {{ resource.name.lower() }} resource"""
        try:
            # Validate configuration
            self._validate_{{ resource.name.lower() }}_config(config)
            
            # Create resource via API
            result = self._call_api("POST", "{{ resource.api_endpoint }}", config)
            
            # Apply tags for tracking
            if result.get("id"):
                self.tag_resource(result["id"], "{{ resource.name.lower() }}", metadata.to_tags())
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create {{ resource.name.lower() }}: {e}")
            raise
    
    def update_{{ resource.name.lower() }}(self, resource_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update {{ resource.name.lower() }} resource"""
        try:
            endpoint = f"{{ resource.api_endpoint }}/{resource_id}"
            return self._call_api("PUT", endpoint, updates)
        except Exception as e:
            logger.error(f"Failed to update {{ resource.name.lower() }} {resource_id}: {e}")
            raise
    
    def delete_{{ resource.name.lower() }}(self, resource_id: str) -> None:
        """Delete {{ resource.name.lower() }} resource"""
        try:
            endpoint = f"{{ resource.api_endpoint }}/{resource_id}"
            self._call_api("DELETE", endpoint)
        except Exception as e:
            logger.error(f"Failed to delete {{ resource.name.lower() }} {resource_id}: {e}")
            raise
    
    def get_{{ resource.name.lower() }}(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get {{ resource.name.lower() }} resource"""
        try:
            endpoint = f"{{ resource.api_endpoint }}/{resource_id}"
            return self._call_api("GET", endpoint)
        except Exception as e:
            logger.error(f"Failed to get {{ resource.name.lower() }} {resource_id}: {e}")
            return None
    
    def list_{{ resource.name.lower() }}s(self, query: Optional[ResourceQuery] = None) -> List[Dict[str, Any]]:
        """List {{ resource.name.lower() }} resources"""
        try:
            params = self._build_query_params(query) if query else {}
            return self._call_api("GET", "{{ resource.api_endpoint }}", params=params)
        except Exception as e:
            logger.error(f"Failed to list {{ resource.name.lower() }}s: {e}")
            return []
    
    def _validate_{{ resource.name.lower() }}_config(self, config: Dict[str, Any]) -> None:
        """Validate {{ resource.name.lower() }} configuration"""
        required_fields = [{% for field in resource.fields if field.required %}"{{ field.name }}"{% if not loop.last %}, {% endif %}{% endfor %}]
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
    
    {% endfor %}
    
    # Base provider methods
    def create_resource(self, resource_type: str, config: Dict[str, Any], metadata: ResourceMetadata) -> Dict[str, Any]:
        """Create a resource of the specified type"""
        method_name = f"create_{resource_type.lower()}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(config, metadata)
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")
    
    def update_resource(self, resource_id: str, resource_type: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a resource"""
        method_name = f"update_{resource_type.lower()}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(resource_id, updates)
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")
    
    def delete_resource(self, resource_id: str, resource_type: str) -> None:
        """Delete a resource"""
        method_name = f"delete_{resource_type.lower()}"
        if hasattr(self, method_name):
            getattr(self, method_name)(resource_id)
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")
    
    def get_resource(self, resource_id: str, resource_type: str) -> Optional[Dict[str, Any]]:
        """Get a resource"""
        method_name = f"get_{resource_type.lower()}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(resource_id)
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")
    
    def list_resources(self, resource_type: str, query: Optional[ResourceQuery] = None) -> List[Dict[str, Any]]:
        """List resources"""
        method_name = f"list_{resource_type.lower()}s"
        if hasattr(self, method_name):
            return getattr(self, method_name)(query)
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")
    
    def discover_resources(self, resource_type: str, query: Optional[ResourceQuery] = None) -> List[Dict[str, Any]]:
        """Discover resources"""
        return self.list_resources(resource_type, query)
    
    def plan_create(self, resource_type: str, config: Dict[str, Any], metadata: ResourceMetadata) -> Dict[str, Any]:
        """Plan resource creation"""
        return {
            "action": "create",
            "resource_type": resource_type,
            "config": config,
            "estimated_cost": self.estimate_cost(resource_type, config)
        }
    
    def plan_update(self, resource_id: str, resource_type: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Plan resource update"""
        current = self.get_resource(resource_id, resource_type)
        return {
            "action": "update",
            "resource_id": resource_id,
            "resource_type": resource_type,
            "current": current,
            "updates": updates,
            "changes": self._calculate_changes(current, updates)
        }
    
    def plan_delete(self, resource_id: str, resource_type: str) -> Dict[str, Any]:
        """Plan resource deletion"""
        return {
            "action": "delete",
            "resource_id": resource_id,
            "resource_type": resource_type,
            "warning": "This action cannot be undone"
        }
    
    def tag_resource(self, resource_id: str, resource_type: str, tags: Dict[str, str]) -> None:
        """Apply tags to a resource"""
        # Implementation depends on provider tagging API
        pass
    
    def estimate_cost(self, resource_type: str, config: Dict[str, Any]) -> Dict[str, float]:
        """Estimate cost for resource configuration"""
        # Implementation depends on provider pricing API
        return {"hourly": 0.0, "monthly": 0.0}
    
    def validate_config(self, resource_type: str, config: Dict[str, Any]) -> List[str]:
        """Validate resource configuration"""
        errors = []
        method_name = f"_validate_{resource_type.lower()}_config"
        if hasattr(self, method_name):
            try:
                getattr(self, method_name)(config)
            except ValueError as e:
                errors.append(str(e))
        return errors
    
    def get_resource_types(self) -> List[str]:
        """Get supported resource types"""
        return [{% for resource in resources %}"{{ resource.name.lower() }}"{% if not loop.last %}, {% endif %}{% endfor %}]
    
    def get_regions(self) -> List[str]:
        """Get available regions"""
        # Implementation depends on provider regions API
        return ["us-east-1", "us-west-2", "eu-west-1"]
    
    def _call_api(self, method: str, endpoint: str, data: Dict[str, Any] = None, params: Dict[str, Any] = None) -> Any:
        """Make API call to provider"""
        # Implementation depends on provider SDK
        pass
    
    def _build_query_params(self, query: ResourceQuery) -> Dict[str, Any]:
        """Build query parameters from ResourceQuery"""
        params = {}
        if query.filters:
            params.update(query.filters)
        return params
    
    def _calculate_changes(self, current: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate changes between current and updated config"""
        changes = {}
        for key, new_value in updates.items():
            old_value = current.get(key)
            if old_value != new_value:
                changes[key] = {"old": old_value, "new": new_value}
        return changes
'''

        # Resource template
        resource_template = '''"""
{{ resource_name|title }} Resource for {{ provider_name|title }}
Generated on {{ generation_date }}
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum


@dataclass
class {{ resource_name|title }}Config:
    """Configuration for {{ resource_name|title }} resource"""
    
    {% for field in fields %}
    {{ field.name }}: {{ field.type }}{% if field.default_value %} = {{ field.default_value }}{% endif %}{% if field.description %}  # {{ field.description }}{% endif %}
    {% endfor %}
    
    def validate(self) -> List[str]:
        """Validate configuration"""
        errors = []
        {% for field in fields if field.required %}
        if not self.{{ field.name }}:
            errors.append("{{ field.name }} is required")
        {% endfor %}
        {% for field in fields if field.constraints %}
        {% for constraint, value in field.constraints.items() %}
        {% if constraint == "min_length" %}
        if len(str(self.{{ field.name }})) < {{ value }}:
            errors.append("{{ field.name }} must be at least {{ value }} characters")
        {% elif constraint == "max_length" %}
        if len(str(self.{{ field.name }})) > {{ value }}:
            errors.append("{{ field.name }} must be no more than {{ value }} characters")
        {% elif constraint == "pattern" %}
        import re
        if not re.match(r"{{ value }}", str(self.{{ field.name }})):
            errors.append("{{ field.name }} does not match required pattern")
        {% endif %}
        {% endfor %}
        {% endfor %}
        return errors


class {{ resource_name|title }}States(Enum):
    """Possible states for {{ resource_name|title }} resource"""
    
    CREATING = "creating"
    ACTIVE = "active"
    UPDATING = "updating"
    DELETING = "deleting"
    DELETED = "deleted"
    ERROR = "error"


class {{ resource_name|title }}Resource:
    """{{ resource_name|title }} resource implementation"""
    
    def __init__(self, provider_client, config: {{ resource_name|title }}Config):
        self.client = provider_client
        self.config = config
        self.state = {{ resource_name|title }}States.CREATING
        self.resource_id: Optional[str] = None
        self.metadata: Dict[str, Any] = {}
    
    def create(self) -> Dict[str, Any]:
        """Create the resource"""
        # Validate configuration
        errors = self.config.validate()
        if errors:
            raise ValueError(f"Configuration errors: {errors}")
        
        # Create resource via provider API
        result = self.client.create_{{ resource_name.lower() }}(self.config.__dict__)
        
        self.resource_id = result.get("id")
        self.state = {{ resource_name|title }}States.ACTIVE
        self.metadata = result
        
        return result
    
    def update(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update the resource"""
        if not self.resource_id:
            raise ValueError("Resource not created yet")
        
        result = self.client.update_{{ resource_name.lower() }}(self.resource_id, updates)
        self.metadata.update(result)
        
        return result
    
    def delete(self) -> None:
        """Delete the resource"""
        if not self.resource_id:
            raise ValueError("Resource not created yet")
        
        self.client.delete_{{ resource_name.lower() }}(self.resource_id)
        self.state = {{ resource_name|title }}States.DELETED
        self.resource_id = None
    
    def get_state(self) -> Dict[str, Any]:
        """Get current resource state"""
        if not self.resource_id:
            return {"state": self.state.value}
        
        current = self.client.get_{{ resource_name.lower() }}(self.resource_id)
        if current:
            self.metadata = current
        
        return current or {"state": self.state.value}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert resource to dictionary"""
        return {
            "id": self.resource_id,
            "state": self.state.value,
            "config": self.config.__dict__,
            "metadata": self.metadata
        }
'''

        # Write templates
        with open(template_dir / "provider.py.j2", "w") as f:
            f.write(provider_template)
        
        with open(template_dir / "resource.py.j2", "w") as f:
            f.write(resource_template)
    
    def add_resource(self, resource: ResourceDefinition) -> None:
        """Add a resource definition"""
        self.resources.append(resource)
        logger.info(f"Added resource definition: {resource.name}")
    
    def load_from_openapi(self, spec_path: str) -> None:
        """Load resources from OpenAPI specification"""
        try:
            with open(spec_path, 'r') as f:
                if spec_path.endswith('.yaml') or spec_path.endswith('.yml'):
                    spec = yaml.safe_load(f)
                else:
                    spec = json.load(f)
            
            self._parse_openapi_spec(spec)
            logger.info(f"Loaded resources from OpenAPI spec: {spec_path}")
            
        except Exception as e:
            logger.error(f"Failed to load OpenAPI spec: {e}")
            raise
    
    def load_from_terraform(self, schema_path: str) -> None:
        """Load resources from Terraform provider schema"""
        try:
            with open(schema_path, 'r') as f:
                schema = json.load(f)
            
            self._parse_terraform_schema(schema)
            logger.info(f"Loaded resources from Terraform schema: {schema_path}")
            
        except Exception as e:
            logger.error(f"Failed to load Terraform schema: {e}")
            raise
    
    def _parse_openapi_spec(self, spec: Dict[str, Any]) -> None:
        """Parse OpenAPI specification and extract resources"""
        paths = spec.get("paths", {})
        components = spec.get("components", {})
        schemas = components.get("schemas", {})
        
        for path, methods in paths.items():
            # Extract resource name from path
            resource_name = self._extract_resource_name(path)
            if not resource_name:
                continue
            
            # Determine resource type
            resource_type = self._determine_resource_type(resource_name, path)
            
            # Extract fields from schema
            fields = []
            if "post" in methods:
                post_method = methods["post"]
                request_body = post_method.get("requestBody", {})
                content = request_body.get("content", {})
                json_content = content.get("application/json", {})
                schema_ref = json_content.get("schema", {})
                
                if "$ref" in schema_ref:
                    schema_name = schema_ref["$ref"].split("/")[-1]
                    schema_def = schemas.get(schema_name, {})
                    fields = self._extract_fields_from_schema(schema_def)
            
            # Create resource definition
            resource = ResourceDefinition(
                name=resource_name,
                type=resource_type,
                provider=self.config.provider_type,
                description=f"Generated from OpenAPI spec: {path}",
                fields=fields,
                api_endpoint=path
            )
            
            self.add_resource(resource)
    
    def _parse_terraform_schema(self, schema: Dict[str, Any]) -> None:
        """Parse Terraform schema and extract resources"""
        provider_schemas = schema.get("provider_schemas", {})
        
        for provider_name, provider_schema in provider_schemas.items():
            resource_schemas = provider_schema.get("resource_schemas", {})
            
            for resource_type, resource_schema in resource_schemas.items():
                # Extract resource name
                resource_name = resource_type.split("_")[-1]
                
                # Determine resource type
                res_type = self._determine_resource_type(resource_name, resource_type)
                
                # Extract fields
                fields = self._extract_fields_from_terraform_schema(resource_schema)
                
                # Create resource definition
                resource = ResourceDefinition(
                    name=resource_name,
                    type=res_type,
                    provider=self.config.provider_type,
                    description=resource_schema.get("description", ""),
                    fields=fields,
                    terraform_resource_type=resource_type
                )
                
                self.add_resource(resource)
    
    def _extract_resource_name(self, path: str) -> Optional[str]:
        """Extract resource name from API path"""
        # Remove leading slash and split by /
        parts = path.strip("/").split("/")
        
        # Look for resource-like patterns
        for part in parts:
            if part and not part.startswith("{") and part != "v1" and part != "api":
                return part.rstrip("s")  # Remove plural suffix
        
        return None
    
    def _determine_resource_type(self, resource_name: str, context: str) -> ResourceType:
        """Determine resource type from name and context"""
        name_lower = resource_name.lower()
        context_lower = context.lower()
        
        # Keyword mappings
        type_keywords = {
            ResourceType.COMPUTE: ["instance", "vm", "server", "machine", "compute"],
            ResourceType.STORAGE: ["bucket", "volume", "disk", "storage", "blob"],
            ResourceType.NETWORK: ["network", "subnet", "vpc", "firewall", "lb", "loadbalancer"],
            ResourceType.DATABASE: ["database", "db", "table", "cluster", "postgres", "mysql"],
            ResourceType.SECURITY: ["security", "iam", "role", "policy", "key"],
            ResourceType.MONITORING: ["monitor", "alert", "log", "metric", "dashboard"],
            ResourceType.CONTAINER: ["container", "pod", "deployment", "service", "k8s"],
            ResourceType.SERVERLESS: ["function", "lambda", "serverless", "trigger"]
        }
        
        for resource_type, keywords in type_keywords.items():
            if any(keyword in name_lower or keyword in context_lower for keyword in keywords):
                return resource_type
        
        return ResourceType.COMPUTE  # Default
    
    def _extract_fields_from_schema(self, schema: Dict[str, Any]) -> List[ResourceField]:
        """Extract fields from OpenAPI schema"""
        fields = []
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        for field_name, field_schema in properties.items():
            field_type = self._map_openapi_type(field_schema.get("type", "string"))
            
            field = ResourceField(
                name=field_name,
                type=field_type,
                description=field_schema.get("description", ""),
                required=field_name in required,
                default_value=field_schema.get("default"),
                constraints=self._extract_constraints(field_schema)
            )
            
            fields.append(field)
        
        return fields
    
    def _extract_fields_from_terraform_schema(self, schema: Dict[str, Any]) -> List[ResourceField]:
        """Extract fields from Terraform schema"""
        fields = []
        block = schema.get("block", {})
        attributes = block.get("attributes", {})
        
        for field_name, field_schema in attributes.items():
            field_type = self._map_terraform_type(field_schema.get("type"))
            
            field = ResourceField(
                name=field_name,
                type=field_type,
                description=field_schema.get("description", ""),
                required=field_schema.get("required", False),
                constraints=self._extract_terraform_constraints(field_schema)
            )
            
            fields.append(field)
        
        return fields
    
    def _map_openapi_type(self, openapi_type: str) -> str:
        """Map OpenAPI type to Python type"""
        type_map = {
            "string": "str",
            "integer": "int",
            "number": "float",
            "boolean": "bool",
            "array": "List[Any]",
            "object": "Dict[str, Any]"
        }
        return type_map.get(openapi_type, "str")
    
    def _map_terraform_type(self, terraform_type: Any) -> str:
        """Map Terraform type to Python type"""
        if isinstance(terraform_type, str):
            type_map = {
                "string": "str",
                "number": "float",
                "bool": "bool"
            }
            return type_map.get(terraform_type, "str")
        elif isinstance(terraform_type, list):
            if terraform_type == ["list", "string"]:
                return "List[str]"
            elif terraform_type == ["map", "string"]:
                return "Dict[str, str]"
            elif terraform_type == ["set", "string"]:
                return "Set[str]"
        
        return "Any"
    
    def _extract_constraints(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract constraints from OpenAPI schema"""
        constraints = {}
        
        if "minLength" in schema:
            constraints["min_length"] = schema["minLength"]
        if "maxLength" in schema:
            constraints["max_length"] = schema["maxLength"]
        if "pattern" in schema:
            constraints["pattern"] = schema["pattern"]
        if "minimum" in schema:
            constraints["minimum"] = schema["minimum"]
        if "maximum" in schema:
            constraints["maximum"] = schema["maximum"]
        if "enum" in schema:
            constraints["enum"] = schema["enum"]
        
        return constraints
    
    def _extract_terraform_constraints(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract constraints from Terraform schema"""
        constraints = {}
        
        # Terraform doesn't have as rich constraint info as OpenAPI
        # but we can extract some basic info
        if "sensitive" in schema:
            constraints["sensitive"] = schema["sensitive"]
        
        return constraints
    
    def generate_provider(self) -> str:
        """Generate provider code"""
        template = self.templates.get_template("provider.py.j2")
        
        # Prepare template context
        context = {
            "provider_name": self.config.provider_type.value,
            "generation_date": datetime.now().isoformat(),
            "resources": self.resources,
            "config_fields": self._get_config_fields(),
            "use_async": self.config.generate_async,
            "use_type_hints": self.config.use_type_hints
        }
        
        return template.render(context)
    
    def generate_resource(self, resource: ResourceDefinition) -> str:
        """Generate resource code"""
        template = self.templates.get_template("resource.py.j2")
        
        context = {
            "resource_name": resource.name,
            "provider_name": self.config.provider_type.value,
            "generation_date": datetime.now().isoformat(),
            "fields": resource.fields,
            "description": resource.description
        }
        
        return template.render(context)
    
    def _get_config_fields(self) -> List[ResourceField]:
        """Get configuration fields for the provider"""
        common_fields = [
            ResourceField("api_key", "str", "API key for authentication", required=True),
            ResourceField("region", "str", "Default region", required=True),
            ResourceField("project_id", "Optional[str]", "Project ID"),
            ResourceField("timeout", "int", "Request timeout in seconds", default_value="30")
        ]
        
        # Add provider-specific fields
        provider_fields = self.config.provider_config.get("fields", [])
        for field_data in provider_fields:
            field = ResourceField(**field_data)
            common_fields.append(field)
        
        return common_fields
    
    def generate_all(self) -> Dict[str, str]:
        """Generate all provider code"""
        generated = {}
        
        # Generate main provider
        generated["provider.py"] = self.generate_provider()
        
        # Generate resources
        for resource in self.resources:
            filename = f"{resource.name.lower()}.py"
            generated[filename] = self.generate_resource(resource)
        
        return generated
    
    def write_to_files(self, output_dir: Optional[str] = None) -> None:
        """Write generated code to files"""
        output_dir = output_dir or self.config.output_directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        generated = self.generate_all()
        
        for filename, content in generated.items():
            file_path = output_path / filename
            with open(file_path, 'w') as f:
                f.write(content)
            
            logger.info(f"Generated: {file_path}")
        
        # Generate __init__.py
        init_content = self._generate_init_file()
        with open(output_path / "__init__.py", 'w') as f:
            f.write(init_content)
        
        logger.info(f"Provider generation complete: {output_path}")
    
    def _generate_init_file(self) -> str:
        """Generate __init__.py file"""
        provider_name = self.config.provider_type.value
        
        imports = [f"from .provider import {provider_name.title()}Provider, {provider_name.title()}Config"]
        
        for resource in self.resources:
            resource_name = resource.name
            imports.append(f"from .{resource_name.lower()} import {resource_name.title()}Resource, {resource_name.title()}Config")
        
        return f'''"""
{provider_name.title()} Provider Package
Generated on {datetime.now().isoformat()}
"""

{chr(10).join(imports)}

__all__ = [
    "{provider_name.title()}Provider",
    "{provider_name.title()}Config",
    {chr(10).join(f'    "{resource.name.title()}Resource",' for resource in self.resources)}
    {chr(10).join(f'    "{resource.name.title()}Config",' for resource in self.resources)}
]
'''


def create_aws_generator(output_dir: str) -> ProviderGenerator:
    """Create generator for AWS provider"""
    config = GenerationConfig(
        provider_type=ProviderType.AWS,
        output_directory=output_dir,
        provider_config={
            "fields": [
                {"name": "aws_access_key_id", "type": "str", "description": "AWS access key", "required": True},
                {"name": "aws_secret_access_key", "type": "str", "description": "AWS secret key", "required": True},
                {"name": "aws_session_token", "type": "Optional[str]", "description": "AWS session token"}
            ]
        }
    )
    return ProviderGenerator(config)


def create_gcp_generator(output_dir: str) -> ProviderGenerator:
    """Create generator for GCP provider"""
    config = GenerationConfig(
        provider_type=ProviderType.GCP,
        output_directory=output_dir,
        provider_config={
            "fields": [
                {"name": "service_account_key", "type": "str", "description": "Service account key JSON", "required": True},
                {"name": "project_id", "type": "str", "description": "GCP project ID", "required": True}
            ]
        }
    )
    return ProviderGenerator(config)


def create_digitalocean_generator(output_dir: str) -> ProviderGenerator:
    """Create generator for DigitalOcean provider"""
    config = GenerationConfig(
        provider_type=ProviderType.DIGITAL_OCEAN,
        output_directory=output_dir,
        provider_config={
            "fields": [
                {"name": "token", "type": "str", "description": "DigitalOcean API token", "required": True}
            ]
        }
    )
    return ProviderGenerator(config)


# CLI interface
def main():
    """CLI entry point for provider generation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate InfraDSL provider code")
    parser.add_argument("provider", choices=["aws", "gcp", "digitalocean"], help="Provider type")
    parser.add_argument("--output", "-o", required=True, help="Output directory")
    parser.add_argument("--openapi", help="OpenAPI spec file")
    parser.add_argument("--terraform", help="Terraform schema file")
    
    args = parser.parse_args()
    
    # Create generator
    if args.provider == "aws":
        generator = create_aws_generator(args.output)
    elif args.provider == "gcp":
        generator = create_gcp_generator(args.output)
    elif args.provider == "digitalocean":
        generator = create_digitalocean_generator(args.output)
    else:
        raise ValueError(f"Unsupported provider: {args.provider}")
    
    # Load resources
    if args.openapi:
        generator.load_from_openapi(args.openapi)
    elif args.terraform:
        generator.load_from_terraform(args.terraform)
    else:
        # Add some default resources
        if args.provider == "aws":
            generator.add_resource(ResourceDefinition(
                name="Instance",
                type=ResourceType.COMPUTE,
                provider=ProviderType.AWS,
                description="EC2 instance",
                fields=[
                    ResourceField("instance_type", "str", "EC2 instance type", required=True),
                    ResourceField("ami", "str", "AMI ID", required=True),
                    ResourceField("key_name", "Optional[str]", "SSH key pair name"),
                    ResourceField("security_groups", "List[str]", "Security group IDs")
                ],
                api_endpoint="/instances"
            ))
    
    # Generate code
    generator.write_to_files()
    print(f"Generated {args.provider} provider in {args.output}")


if __name__ == "__main__":
    main()