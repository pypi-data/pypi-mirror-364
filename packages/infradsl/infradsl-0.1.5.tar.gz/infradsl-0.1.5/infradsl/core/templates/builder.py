from typing import Dict, Any, List, Optional, Type, Union, Callable
from pathlib import Path
import json
from datetime import datetime

from .base import BaseTemplate, TemplateMetadata, TemplateContext
from .registry import TemplateRegistry


class TemplateBuilder:
    """
    Builder for creating custom templates programmatically.
    
    Allows users to:
    - Create new templates from scratch
    - Extend existing templates  
    - Compose multiple templates
    - Define parameters and outputs
    - Publish to registries
    
    Example Usage:
        # Create a custom web application template
        builder = (Template.create("WebAppStack")
                   .base("GenericVM")
                   .add_component("LoadBalancer") 
                   .add_component("Database")
                   .with_parameter("instance_count", int, default=2)
                   .with_parameter("ssl_cert_arn", str, required=True)
                   .with_output("lb_dns_name")
                   .with_output("database_endpoint")
                   .description("Complete web application stack")
                   .category("web")
                   .tags(["web", "scalable", "database"])
                   .author("My Team"))
    """
    
    def __init__(self, name: str = None, base_template: str = None, registry: TemplateRegistry = None):
        self.name = name
        self.base_template = base_template
        self.registry = registry
        
        # Template definition
        self.components: List[Dict[str, Any]] = []
        self.parameters: Dict[str, Dict[str, Any]] = {}
        self.outputs: Dict[str, str] = {}
        self.build_logic: Optional[Callable] = None
        
        # Metadata
        self.metadata_dict = {
            "name": name or "CustomTemplate",
            "version": "1.0.0",
            "description": "",
            "author": "",
            "tags": [],
            "category": "custom",
            "requires": [],
            "providers": [],
            "min_infradsl_version": "1.0.0",
            "examples": [],
            "documentation_url": "",
            "repository_url": "",
            "parameters_schema": {"type": "object", "properties": {}, "required": []},
            "outputs_schema": {"type": "object", "properties": {}},
        }
        
        if base_template:
            self.metadata_dict["requires"].append(base_template)
            
    # Metadata configuration methods
    
    def description(self, desc: str) -> "TemplateBuilder":
        """Set template description (chainable)"""
        self.metadata_dict["description"] = desc
        return self
        
    def version(self, version: str) -> "TemplateBuilder":
        """Set template version (chainable)"""
        self.metadata_dict["version"] = version
        return self
        
    def author(self, author: str) -> "TemplateBuilder":
        """Set template author (chainable)"""
        self.metadata_dict["author"] = author
        return self
        
    def category(self, category: str) -> "TemplateBuilder":
        """Set template category (chainable)"""
        self.metadata_dict["category"] = category
        return self
        
    def tags(self, *tags: str) -> "TemplateBuilder":
        """Add tags to template (chainable)"""
        self.metadata_dict["tags"].extend(tags)
        return self
        
    def requires(self, *templates: str) -> "TemplateBuilder":
        """Add required templates (chainable)"""
        self.metadata_dict["requires"].extend(templates)
        return self
        
    def supports_providers(self, *providers: str) -> "TemplateBuilder":
        """Add supported providers (chainable)"""
        self.metadata_dict["providers"].extend(providers)
        return self
        
    def documentation(self, url: str) -> "TemplateBuilder":
        """Set documentation URL (chainable)"""
        self.metadata_dict["documentation_url"] = url
        return self
        
    def repository(self, url: str) -> "TemplateBuilder":
        """Set repository URL (chainable)"""
        self.metadata_dict["repository_url"] = url
        return self
        
    # Template composition methods
    
    def base(self, template_name: str) -> "TemplateBuilder":
        """Set base template to extend (chainable)"""
        self.base_template = template_name
        if template_name not in self.metadata_dict["requires"]:
            self.metadata_dict["requires"].append(template_name)
        return self
        
    def add_component(self, component: Union[str, Dict[str, Any]], **kwargs) -> "TemplateBuilder":
        """Add a component template or resource (chainable)"""
        if isinstance(component, str):
            component_config = {
                "type": "template",
                "template": component,
                "parameters": kwargs
            }
        else:
            component_config = component
            component_config.update(kwargs)
            
        self.components.append(component_config)
        return self
        
    def add_resource(self, resource_type: str, name: str, **config) -> "TemplateBuilder":
        """Add a raw resource (chainable)"""
        resource_config = {
            "type": "resource",
            "resource_type": resource_type,
            "name": name,
            "config": config
        }
        self.components.append(resource_config)
        return self
        
    # Parameter and output definition
    
    def with_parameter(self, name: str, param_type: Type, 
                      description: str = "", default: Any = None,
                      required: bool = None) -> "TemplateBuilder":
        """Add a parameter definition (chainable)"""
        param_schema = {
            "type": self._type_to_json_schema(param_type),
            "description": description
        }
        
        if default is not None:
            param_schema["default"] = default
            
        if required is None:
            required = (default is None)
            
        self.parameters[name] = {
            "schema": param_schema,
            "required": required
        }
        
        # Update metadata schema
        self.metadata_dict["parameters_schema"]["properties"][name] = param_schema
        if required:
            self.metadata_dict["parameters_schema"]["required"].append(name)
            
        return self
        
    def with_output(self, name: str, description: str = "") -> "TemplateBuilder":
        """Add an output definition (chainable)"""
        self.outputs[name] = description
        
        # Update metadata schema
        self.metadata_dict["outputs_schema"]["properties"][name] = {
            "type": "string",
            "description": description
        }
        
        return self
        
    def _type_to_json_schema(self, param_type: Type) -> str:
        """Convert Python type to JSON schema type"""
        type_mapping = {
            str: "string",
            int: "integer", 
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object"
        }
        return type_mapping.get(param_type, "string")
        
    # Template logic definition
    
    def with_build_logic(self, build_func: Callable[[TemplateContext], List[Any]]) -> "TemplateBuilder":
        """Set custom build logic (chainable)"""
        self.build_logic = build_func
        return self
        
    def with_conditional_component(self, condition: str, component: str, **kwargs) -> "TemplateBuilder":
        """Add component conditionally based on parameter (chainable)"""
        component_config = {
            "type": "template", 
            "template": component,
            "parameters": kwargs,
            "condition": condition
        }
        self.components.append(component_config)
        return self
        
    # Template examples and documentation
    
    def add_example(self, name: str, description: str, code: str) -> "TemplateBuilder":
        """Add usage example (chainable)"""
        example = {
            "name": name,
            "description": description,
            "code": code
        }
        self.metadata_dict["examples"].append(example)
        return self
        
    # Build and publishing
    
    def build_class(self) -> Type[BaseTemplate]:
        """Build the template class"""
        builder_instance = self
        
        class CustomTemplate(BaseTemplate):
            """Dynamically created template class"""
            
            def _create_metadata(self) -> TemplateMetadata:
                return TemplateMetadata.from_dict(builder_instance.metadata_dict)
                
            def build(self, context: TemplateContext) -> List[Any]:
                """Build template resources"""
                resources = []
                
                # If custom build logic is provided, use it
                if builder_instance.build_logic:
                    return builder_instance.build_logic(context)
                    
                # Otherwise, build from components
                for component in builder_instance.components:
                    component_resources = self._build_component(component, context)
                    resources.extend(component_resources)
                    
                return resources
                
            def _build_component(self, component: Dict[str, Any], context: TemplateContext) -> List[Any]:
                """Build a single component"""
                resources = []
                
                # Check condition if present
                if "condition" in component:
                    condition = component["condition"]
                    # Simple condition evaluation (could be enhanced)
                    param_name = condition.strip()
                    if not context.parameters.get(param_name, False):
                        return resources
                        
                component_type = component["type"]
                
                if component_type == "template":
                    # Load and build sub-template
                    template_name = component["template"] 
                    parameters = component.get("parameters", {})
                    
                    if builder_instance.registry:
                        sub_template = builder_instance.registry.create_template(
                            template_name, f"{context.name}-{template_name}", **parameters)
                        resources.extend(sub_template.render())
                        
                elif component_type == "resource":
                    # Create raw resource (would need resource factory)
                    # This is a simplified implementation
                    pass
                    
                return resources
                
        return CustomTemplate
        
    def save_to_file(self, file_path: str):
        """Save template definition to file"""
        template_data = {
            "metadata": self.metadata_dict,
            "base_template": self.base_template,
            "components": self.components,
            "parameters": self.parameters,
            "outputs": self.outputs,
            "created_at": datetime.now().isoformat()
        }
        
        with open(file_path, 'w') as f:
            json.dump(template_data, f, indent=2)
            
    def publish(self, registry_name: str = "local") -> "TemplateBuilder":
        """Publish template to registry (chainable)"""
        template_class = self.build_class()
        
        if registry_name == "local":
            # Save to local templates directory
            local_dir = Path.home() / ".infradsl" / "templates" / self.metadata_dict["name"]
            local_dir.mkdir(parents=True, exist_ok=True)
            
            # Save metadata
            metadata_file = local_dir / "metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(self.metadata_dict, f, indent=2)
                
            # Save template definition
            template_file = local_dir / "template.json"
            self.save_to_file(str(template_file))
            
        else:
            # Publish to remote registry
            if self.registry:
                self.registry.publish_template(template_class(), registry_name)
                
        return self
        
    @classmethod
    def from_file(cls, file_path: str) -> "TemplateBuilder":
        """Load template builder from file"""
        with open(file_path, 'r') as f:
            template_data = json.load(f)
            
        builder = cls(name=template_data["metadata"]["name"])
        builder.metadata_dict = template_data["metadata"]
        builder.base_template = template_data.get("base_template")
        builder.components = template_data.get("components", [])
        builder.parameters = template_data.get("parameters", {})
        builder.outputs = template_data.get("outputs", {})
        
        return builder


# Template creation shortcuts

def create_vm_template(name: str) -> TemplateBuilder:
    """Create a virtual machine template builder"""
    return (TemplateBuilder(name)
            .category("compute")
            .tags("vm", "compute")
            .with_parameter("instance_type", str, "Instance type", default="t3.medium")
            .with_parameter("os", str, "Operating system", default="ubuntu")
            .with_parameter("disk_size", int, "Disk size in GB", default=20)
            .with_output("instance_id", "EC2 instance ID")
            .with_output("public_ip", "Public IP address"))

def create_web_app_template(name: str) -> TemplateBuilder:
    """Create a web application template builder"""  
    return (TemplateBuilder(name)
            .category("web")
            .tags("web", "app", "scalable")
            .base("GenericVM")
            .add_component("LoadBalancer")
            .with_parameter("instance_count", int, "Number of instances", default=2)
            .with_parameter("ssl_cert_arn", str, "SSL certificate ARN", required=True)
            .with_output("load_balancer_dns", "Load balancer DNS name")
            .with_output("application_url", "Application URL"))

def create_database_template(name: str) -> TemplateBuilder:
    """Create a database template builder"""
    return (TemplateBuilder(name)
            .category("database")
            .tags("database", "storage")
            .with_parameter("engine", str, "Database engine", default="postgresql")
            .with_parameter("instance_class", str, "Instance class", default="db.t3.micro") 
            .with_parameter("allocated_storage", int, "Storage in GB", default=20)
            .with_output("endpoint", "Database endpoint")
            .with_output("port", "Database port"))