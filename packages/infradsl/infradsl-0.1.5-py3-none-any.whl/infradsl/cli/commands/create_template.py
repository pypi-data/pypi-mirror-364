#!/usr/bin/env python3
"""
InfraDSL Create Template Command

Automatically convert existing infrastructure files into reusable templates.
This revolutionary feature lets users write infrastructure naturally first,
then convert it to templates with a fluent API automatically.
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, TYPE_CHECKING
from argparse import Namespace
from datetime import datetime

from .base import BaseCommand
from ...core.templates.base import TemplateMetadata

if TYPE_CHECKING:
    from ..utils.output import Console
    from ..utils.config import CLIConfig


class InfrastructureAnalyzer:
    """Analyzes Python infrastructure files to extract template patterns"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.source_code = self.file_path.read_text()
        self.tree = ast.parse(self.source_code)
        self.extracted_params: Dict[str, Any] = {}
        self.resources: List[Dict[str, Any]] = []
        self.imports: List[str] = []
        self.notification_calls: List[Dict[str, Any]] = []
        
    def analyze(self) -> Dict[str, Any]:
        """Main analysis method"""
        self._extract_imports()
        self._extract_notification_calls()
        self._extract_resources()
        self._extract_parameters()
        
        return {
            "imports": self.imports,
            "notifications": self.notification_calls,
            "resources": self.resources,
            "parameters": self.extracted_params,
            "original_source": self.source_code
        }
    
    def _extract_imports(self):
        """Extract import statements"""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    self.imports.append(f"from {module} import {alias.name}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports.append(f"import {alias.name}")
    
    def _extract_notification_calls(self):
        """Extract notification function calls like notify_discord()"""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id.startswith("notify_"):
                        notification_type = node.func.id.replace("notify_", "")
                        if node.args and isinstance(node.args[0], ast.Constant):
                            webhook_url = node.args[0].value
                            self.notification_calls.append({
                                "type": notification_type,
                                "method": node.func.id,
                                "webhook_url": webhook_url,
                                "parameter_name": f"{notification_type}_webhook"
                            })
    
    def _extract_resources(self):
        """Extract infrastructure resource definitions"""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign):
                # Look for assignments that create resources
                if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                    resource_name = node.targets[0].id
                    if isinstance(node.value, ast.Call):
                        resource_info = self._analyze_resource_call(node.value, resource_name)
                        if resource_info:
                            self.resources.append(resource_info)
    
    def _analyze_resource_call(self, call_node: ast.Call, variable_name: str) -> Optional[Dict[str, Any]]:
        """Analyze a resource creation call (like CloudRun(...).artifact_registry(...))"""
        # Handle chained method calls
        current_node = call_node
        method_chain = []
        
        while True:
            if isinstance(current_node, ast.Call):
                if isinstance(current_node.func, ast.Attribute):
                    # Method call like .artifact_registry(...)
                    method_info = self._extract_method_call_info(current_node)
                    method_chain.insert(0, method_info)
                    current_node = current_node.func.value
                elif isinstance(current_node.func, ast.Name):
                    # Constructor call like CloudRun(...)
                    constructor_info = self._extract_constructor_info(current_node)
                    method_chain.insert(0, constructor_info)
                    break
                else:
                    break
            else:
                break
        
        if method_chain:
            return {
                "variable_name": variable_name,
                "method_chain": method_chain,
                "resource_type": method_chain[0].get("method_name", "Unknown")
            }
        
        return None
    
    def _extract_method_call_info(self, call_node: ast.Call) -> Dict[str, Any]:
        """Extract information from a method call"""
        method_name = call_node.func.attr
        args = []
        kwargs = {}
        
        # Extract positional arguments
        for arg in call_node.args:
            if isinstance(arg, ast.Constant):
                args.append(arg.value)
            else:
                args.append(f"<{type(arg).__name__}>")
        
        # Extract keyword arguments
        for keyword in call_node.keywords:
            if isinstance(keyword.value, ast.Constant):
                kwargs[keyword.arg] = keyword.value.value
            else:
                kwargs[keyword.arg] = f"<{type(keyword.value).__name__}>"
        
        return {
            "method_name": method_name,
            "args": args,
            "kwargs": kwargs
        }
    
    def _extract_constructor_info(self, call_node: ast.Call) -> Dict[str, Any]:
        """Extract information from a constructor call"""
        if isinstance(call_node.func, ast.Name):
            constructor_name = call_node.func.id
        elif isinstance(call_node.func, ast.Attribute):
            constructor_name = call_node.func.attr
        else:
            constructor_name = "Unknown"
        
        args = []
        for arg in call_node.args:
            if isinstance(arg, ast.Constant):
                args.append(arg.value)
            else:
                args.append(f"<{type(arg).__name__}>")
        
        return {
            "method_name": constructor_name,
            "args": args,
            "kwargs": {},
            "is_constructor": True
        }
    
    def _extract_parameters(self):
        """Extract potential template parameters from hardcoded values"""
        # Analyze notification webhooks
        for notification in self.notification_calls:
            param_name = notification["parameter_name"]
            self.extracted_params[param_name] = {
                "type": "string",
                "description": f"{notification['type'].title()} webhook URL for notifications",
                "default": None,
                "required": False
            }
        
        # Analyze resource parameters
        for resource in self.resources:
            for method_info in resource["method_chain"]:
                if method_info["method_name"] == "artifact_registry" and len(method_info["args"]) >= 5:
                    # artifact_registry(project, location, repo, image, tag)
                    self._add_param("project_id", method_info["args"][0], "string", "GCP project ID", True)
                    self._add_param("region", method_info["args"][1], "string", "GCP region for deployment")
                    self._add_param("repository_name", method_info["args"][2], "string", "Artifact Registry repository name")
                    self._add_param("image_name", method_info["args"][3], "string", "Container image name")
                    self._add_param("image_tag", method_info["args"][4], "string", "Container image tag")
                
                elif method_info["method_name"] == "min_instances":
                    self._add_param("min_instances", method_info["args"][0], "integer", "Minimum number of instances")
                
                elif method_info["method_name"] == "max_instances":
                    self._add_param("max_instances", method_info["args"][0], "integer", "Maximum number of instances")
                
                elif method_info["method_name"] == "environment_variables" and method_info["args"]:
                    default_env = method_info["args"][0] if isinstance(method_info["args"][0], dict) else {}
                    self._add_param("environment_variables", default_env, "object", "Environment variables for the container")
                
                elif method_info["method_name"] == "region":
                    self._add_param("region", method_info["args"][0], "string", "GCP region for deployment")
    
    def _add_param(self, name: str, value: Any, param_type: str, description: str, required: bool = False):
        """Add a parameter to the extracted parameters"""
        if name not in self.extracted_params:
            self.extracted_params[name] = {
                "type": param_type,
                "description": description,
                "default": value if not required else None,
                "required": required
            }


class TemplateGenerator:
    """Generates template classes from analyzed infrastructure"""
    
    def __init__(self, analysis: Dict[str, Any], template_name: str, output_path: Optional[str] = None):
        self.analysis = analysis
        self.template_name = template_name
        self.class_name = f"{template_name}Template"
        self.output_path = Path(output_path) if output_path else None
        self.use_relative_imports = self._should_use_relative_imports()
        
    def generate(self) -> str:
        """Generate the complete template file"""
        imports = self._generate_imports()
        class_def = self._generate_class()
        factory_class = self._generate_factory()
        
        return f"""{imports}


{class_def}


{factory_class}
"""
    
    def _should_use_relative_imports(self) -> bool:
        """Determine if we should use relative imports based on output location"""
        if not self.output_path:
            return True  # Default behavior for package structure
        
        # Check if the output path is within the infradsl package structure
        try:
            # Get the infradsl package root
            current_file = Path(__file__)
            infradsl_root = current_file.parent.parent.parent  # Go up to infradsl/
            
            # Check if output path is within infradsl package
            if self.output_path.is_absolute():
                try:
                    self.output_path.relative_to(infradsl_root)
                    return True  # Inside package, use relative imports
                except ValueError:
                    return False  # Outside package, use absolute imports
            else:
                # Relative path - check if it would end up in infradsl structure
                if str(self.output_path).startswith("infradsl/"):
                    return True
                else:
                    return False
        except:
            # When in doubt, use absolute imports for standalone files
            return False
    
    def _generate_imports(self) -> str:
        """Generate import statements with proper relative/absolute imports"""
        base_imports = ["from typing import List, Any"]
        
        # Choose import style based on context
        if self.use_relative_imports:
            # Relative imports for files within the InfraDSL package
            base_imports.append("from ...core.templates.base import BaseTemplate, TemplateMetadata, TemplateContext")
            
            # Add notification imports if needed
            if self.analysis["notifications"]:
                base_imports.append("from ...notifications import notify_discord")
            
            # Add resource imports
            for resource in self.analysis["resources"]:
                for method_info in resource["method_chain"]:
                    if method_info.get("is_constructor") and method_info["method_name"] in ["CloudRun"]:
                        base_imports.append("from ...resources.compute.cloud_run import CloudRun")
        else:
            # Absolute imports for standalone files
            base_imports.append("from infradsl.core.templates.base import BaseTemplate, TemplateMetadata, TemplateContext")
            
            # Add notification imports if needed
            if self.analysis["notifications"]:
                base_imports.append("from infradsl.notifications import notify_discord")
            
            # Add resource imports
            for resource in self.analysis["resources"]:
                for method_info in resource["method_chain"]:
                    if method_info.get("is_constructor") and method_info["method_name"] in ["CloudRun"]:
                        base_imports.append("from infradsl.resources.compute.cloud_run import CloudRun")
        
        return "\n".join(base_imports)
    
    def _generate_class(self) -> str:
        """Generate the main template class"""
        metadata = self._generate_metadata()
        notification_methods = self._generate_notification_methods()
        build_method = self._generate_build_method()
        
        return f'''class {self.class_name}(BaseTemplate):
    """
    {self.template_name} Template
    
    Auto-generated from existing infrastructure code.
    Provides a reusable template with fluent API for easy deployment.
    """
    
    def _create_metadata(self) -> TemplateMetadata:
{metadata}
{notification_methods}
    def build(self, context: TemplateContext) -> List[Any]:
{build_method}'''
    
    def _generate_metadata(self) -> str:
        """Generate template metadata"""
        parameters = self.analysis["parameters"]
        required_params = [name for name, info in parameters.items() if info.get("required", False)]
        
        # Build parameters schema with proper formatting
        props_lines = []
        for name, info in parameters.items():
            prop_def = {
                "type": info["type"],
                "description": info["description"]
            }
            # Handle defaults properly
            if info["default"] is not None:
                # Convert complex types to proper representation
                if isinstance(info["default"], dict):
                    prop_def["default"] = info["default"]
                else:
                    prop_def["default"] = info["default"]
            
            # Format each property nicely
            props_lines.append(f'                    "{name}": {self._format_dict(prop_def, indent=24)}')
        
        props_str = ",\n".join(props_lines)
        required_str = ", ".join(f'"{req}"' for req in required_params)
        
        return f'''        return TemplateMetadata(
            name="{self.template_name}",
            version="1.0.0",
            description="Auto-generated template from existing infrastructure",
            author="InfraDSL Auto-Generator",
            category="auto-generated",
            tags=["auto-generated", "cloudrun", "serverless"],
            providers=["gcp"],
            parameters_schema={{
                "type": "object",
                "properties": {{
{props_str}
                }},
                "required": [{required_str}]
            }}
        )'''
    
    def _format_dict(self, d: dict, indent: int = 0) -> str:
        """Format a dictionary with proper indentation and multiline support"""
        if not d:
            return "{}"
        
        # Simple case - single line if short enough
        simple_repr = repr(d)
        if len(simple_repr) < 60:
            return simple_repr
        
        # Multi-line formatting
        items = []
        for key, value in d.items():
            if isinstance(value, dict):
                value_str = self._format_dict(value, indent + 4)
                items.append(f'"{key}": {value_str}')
            else:
                items.append(f'"{key}": {repr(value)}')
        
        if len(items) <= 2:
            return "{" + ", ".join(items) + "}"
        
        # Multi-line format for complex objects
        indent_str = " " * indent
        inner_indent_str = " " * (indent + 4)
        items_str = f",\n{inner_indent_str}".join(items)
        return f"{{\n{inner_indent_str}{items_str}\n{indent_str}}}"
    
    def _generate_notification_methods(self) -> str:
        """Generate notification methods"""
        methods = []
        for notification in self.analysis["notifications"]:
            method_name = f"notify_{notification['type']}"
            param_name = notification["parameter_name"]
            
            methods.append(f'''
    def {method_name}(self, webhook_url: str) -> "{self.class_name}":
        """Enable {notification['type'].title()} notifications (chainable)"""
        self.context.parameters["{param_name}"] = webhook_url
        return self''')
        
        return "\n".join(methods)
    
    def _generate_build_method(self) -> str:
        """Generate the build method with resource creation"""
        lines = ['        """Build the infrastructure resources"""']
        
        # Add imports within build method (using same import style as header)
        for resource in self.analysis["resources"]:
            resource_type = resource["resource_type"]
            if resource_type == "CloudRun":
                if self.use_relative_imports:
                    lines.append("        from ...resources.compute.cloud_run import CloudRun")
                else:
                    lines.append("        from infradsl.resources.compute.cloud_run import CloudRun")
        
        lines.append("")
        
        # Setup notifications
        for notification in self.analysis["notifications"]:
            param_name = notification["parameter_name"]
            lines.append(f"        # Setup {notification['type']} notifications if provided")
            lines.append(f"        {param_name} = context.parameters.get('{param_name}')")
            lines.append(f"        if {param_name}:")
            lines.append(f"            {notification['method']}({param_name})")
            lines.append("")
        
        # Generate resources
        for resource in self.analysis["resources"]:
            lines.extend(self._generate_resource_creation(resource))
        
        # Return resources
        resource_vars = [resource["variable_name"] for resource in self.analysis["resources"]]
        lines.append(f"        return [{', '.join(resource_vars)}]")
        
        return "\n".join(lines)
    
    def _generate_resource_creation(self, resource: Dict[str, Any]) -> List[str]:
        """Generate resource creation code"""
        lines = []
        var_name = resource["variable_name"]
        method_chain = resource["method_chain"]
        
        # Start with constructor
        constructor = method_chain[0]
        if constructor.get("is_constructor"):
            lines.append(f"        {var_name} = (")
            
            # Use context.name for the resource name if it was a string
            if constructor["args"] and isinstance(constructor["args"][0], str):
                lines.append(f"            {constructor['method_name']}(context.name)")
            else:
                args_str = ", ".join([repr(arg) for arg in constructor["args"]])
                lines.append(f"            {constructor['method_name']}({args_str})")
        
        # Add chained methods
        for method_info in method_chain[1:]:
            method_name = method_info["method_name"]
            
            # Handle special parameter substitution
            if method_name == "artifact_registry":
                lines.append("            .artifact_registry(")
                lines.append("                context.parameters['project_id'],")
                lines.append("                context.parameters.get('region', 'europe-north1'),")
                lines.append("                context.parameters.get('repository_name', 'infradsl-apps'),")
                lines.append("                context.parameters.get('image_name', 'helloworld-service'),")
                lines.append("                context.parameters.get('image_tag', 'latest')")
                lines.append("            )")
            elif method_name in ["min_instances", "max_instances"]:
                param_name = method_name
                default_val = method_info["args"][0] if method_info["args"] else 0
                lines.append(f"            .{method_name}(context.parameters.get('{param_name}', {default_val}))")
            elif method_name == "environment_variables":
                # Get the default from extracted parameters, or fall back to method args
                default_env = self.analysis["parameters"].get("environment_variables", {}).get("default", {})
                if not default_env and method_info['args']:
                    default_env = method_info['args'][0] if isinstance(method_info['args'][0], dict) else {}
                lines.append(f"            .{method_name}(context.parameters.get('environment_variables', {repr(default_env)}))")
            elif method_name == "region":
                lines.append("            .region(context.parameters.get('region', 'europe-north1'))")
            else:
                # Use original arguments
                args_str = ", ".join([repr(arg) for arg in method_info["args"]])
                lines.append(f"            .{method_name}({args_str})")
        
        lines.append("        )")
        lines.append("")
        
        return lines
    
    def _generate_factory(self) -> str:
        """Generate the Templates factory class"""
        return f'''class Templates:
    """Template factory with fluent API access"""
    
    @staticmethod
    def {self.template_name}(name: str) -> {self.class_name}:
        """
        Create a {self.template_name} template instance
        
        Usage:
            template = Templates.{self.template_name}("my-service")
                .with_parameters(project_id="my-project")
                .production()
        """
        return {self.class_name}(name)'''


class CreateTemplateCommand(BaseCommand):
    """Command to create templates from existing infrastructure files"""
    
    @property
    def name(self) -> str:
        return "create"
    
    @property
    def description(self) -> str:
        return "Create reusable templates from existing infrastructure files"
    
    def register(self, subparsers) -> None:
        """Register the create template command and subcommands"""
        parser = subparsers.add_parser(
            self.name,
            help=self.description,
            description="Create templates from existing infrastructure"
        )
        
        # Create subcommands for create
        create_subparsers = parser.add_subparsers(
            dest="create_subcommand",
            help="Create operations"
        )
        
        # Template subcommand
        template_parser = create_subparsers.add_parser(
            "template",
            help="Create template from infrastructure file"
        )
        template_parser.add_argument(
            "source_file",
            help="Source infrastructure file to convert"
        )
        template_parser.add_argument(
            "--name", "-n",
            help="Template name (auto-detected if not provided)"
        )
        template_parser.add_argument(
            "--output", "-o",
            help="Output file path"
        )
        template_parser.add_argument(
            "--interactive", "-i",
            action="store_true",
            help="Interactive parameter configuration"
        )
        
        self.add_common_arguments(template_parser)
    
    def execute(self, args: Namespace, config: "CLIConfig", console: "Console") -> int:
        """Execute the create command"""
        if args.create_subcommand == "template":
            return self._create_template(args, config, console)
        else:
            console.error("Invalid create subcommand")
            return 1
    
    def _create_template(self, args: Namespace, config: "CLIConfig", console: "Console") -> int:
        """Create a template from infrastructure file"""
        try:
            console.info(f"🔍 Analyzing infrastructure file: {args.source_file}")
            
            # Verify source file exists
            source_path = Path(args.source_file)
            if not source_path.exists():
                console.error(f"Source file not found: {args.source_file}")
                return 1
            
            # Analyze the source file
            analyzer = InfrastructureAnalyzer(args.source_file)
            analysis = analyzer.analyze()
            
            # Auto-detect template name if not provided
            name = args.name
            if not name:
                base_name = source_path.stem.replace('test_', '').replace('_', ' ').title().replace(' ', '')
                name = base_name
                console.info(f"📝 Auto-detected template name: {name}")
            
            # Show analysis results
            console.success(f"✅ Found {len(analysis['resources'])} resources")
            console.success(f"✅ Extracted {len(analysis['parameters'])} parameters")
            
            if analysis['notifications']:
                console.success(f"✅ Found {len(analysis['notifications'])} notification integrations")
            
            # Determine output path first
            output_path = args.output
            if not output_path:
                output_path = f"infradsl/templates/builtin/{name.lower()}_template.py"
            
            # Generate template
            console.info("🏗️  Generating template...")
            generator = TemplateGenerator(analysis, name, output_path)
            template_code = generator.generate()
            
            final_output_path = Path(output_path)
            final_output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write template file
            final_output_path.write_text(template_code)
            
            console.success(f"🎉 Template created successfully!")
            console.success(f"📁 Location: {final_output_path}")
            console.success(f"🚀 Usage: Templates.{name}('my-instance').with_parameters(...).production()")
            
            # Show sample usage
            console.print("\\n" + "="*60)
            console.print("SAMPLE USAGE:")
            console.print("="*60)
            console.print(f"from infradsl.templates import Templates\\n")
            
            # Generate sample based on detected parameters
            sample_params = []
            for param_name, param_info in analysis['parameters'].items():
                if param_info.get('required'):
                    if param_name == 'project_id':
                        sample_params.append('project_id="my-project-123"')
                    else:
                        sample_params.append(f'{param_name}="<your-value>"')
            
            param_str = ', '.join(sample_params)
            console.print(f"service = Templates.{name}('my-service')")
            if param_str:
                console.print(f"    .with_parameters({param_str})")
            
            # Add notification example if found
            for notification in analysis['notifications']:
                console.print(f"    .notify_{notification['type']}('https://your-webhook-url')")
            
            console.print("    .production()")
            
            return 0
            
        except Exception as e:
            console.error(f"❌ Failed to create template: {str(e)}")
            # Show traceback for debugging
            import traceback
            console.error(traceback.format_exc())
            return 1