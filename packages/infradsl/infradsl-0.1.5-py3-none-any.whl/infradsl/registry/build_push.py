"""
BuildPushRegistry - Helper for template authors

This utility allows template authors to easily publish their templates
by adding a simple call at the end of their template files.
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any
import click
from rich.console import Console
from rich.prompt import Confirm

# Import TemplateRegistryClient dynamically to avoid circular imports


console = Console()


class BuildPushRegistry:
    """
    Helper for building and pushing templates to the registry.
    
    Usage:
        from infradsl import BuildPushRegistry
        
        if __name__ == "__main__":
            BuildPushRegistry(
                name="MyTemplate",
                version="1.0.0", 
                description="My awesome template",
                author="Your Name",
                category="compute",
                tags=["vm", "scalable"],
                providers=["aws", "gcp"],
                visibility="public"  # or "private"
            )
    """
    
    def __init__(
        self,
        name: str,
        version: str,
        description: str,
        author: str,
        category: str = "general",
        tags: List[str] = None,
        providers: List[str] = None,
        requires: List[str] = None,
        visibility: str = "private",
        auto_generate_files: bool = True,
        interactive: bool = True
    ):
        self.metadata = {
            "name": name,
            "version": version,
            "description": description,
            "author": author,
            "category": category,
            "tags": tags or [],
            "providers": providers or [],
            "requires": requires or [],
        }
        self.visibility = visibility
        self.auto_generate_files = auto_generate_files
        self.interactive = interactive
        
        # Get the directory containing the template file
        # This works when called from a template.py file
        frame = sys._getframe(1)
        self.template_dir = Path(frame.f_globals.get("__file__", ".")).parent
        
        # Initialize and run
        self._initialize()
        
    def _initialize(self):
        """Initialize the build and push process"""
        if self.interactive:
            console.print("[bold cyan]InfraDSL Template Publisher[/bold cyan]")
            console.print(f"Template: {self.metadata['name']} v{self.metadata['version']}")
            console.print(f"Directory: {self.template_dir}")
            
            if not Confirm.ask("Continue with template publishing?"):
                console.print("[yellow]Publishing cancelled.")
                return
                
        # Generate required files if needed
        if self.auto_generate_files:
            self._generate_required_files()
            
        # Validate template structure
        if not self._validate_template():
            console.print("[red]Template validation failed. Aborting.")
            return
            
        # Push to registry
        if self.interactive:
            if Confirm.ask(f"Push template to registry with visibility '{self.visibility}'?"):
                self._push_to_registry()
            else:
                console.print("[yellow]Push cancelled. Template files generated.")
        else:
            self._push_to_registry()
            
    def _generate_required_files(self):
        """Generate required template files"""
        console.print("[blue]Generating template files...")
        
        # Generate version.py
        version_file = self.template_dir / "version.py"
        if not version_file.exists():
            self._generate_version_file(version_file)
            console.print(f"  ✓ Generated {version_file.name}")
        else:
            console.print(f"  - {version_file.name} already exists")
            
        # Generate README.md
        readme_file = self.template_dir / "README.md"
        if not readme_file.exists():
            self._generate_readme_file(readme_file)
            console.print(f"  ✓ Generated {readme_file.name}")
        else:
            console.print(f"  - {readme_file.name} already exists")
            
        # Generate examples directory
        examples_dir = self.template_dir / "examples"
        if not examples_dir.exists():
            examples_dir.mkdir()
            self._generate_example_file(examples_dir / "basic_usage.py")
            console.print(f"  ✓ Generated examples/ directory")
        else:
            console.print(f"  - examples/ directory already exists")
            
    def _generate_version_file(self, version_file: Path):
        """Generate version.py file"""
        content = f'''"""
Template metadata for {self.metadata["name"]}
"""

name = "{self.metadata["name"]}"
version = "{self.metadata["version"]}"
description = "{self.metadata["description"]}"
author = "{self.metadata["author"]}"
category = "{self.metadata["category"]}"
tags = {self.metadata["tags"]}
providers = {self.metadata["providers"]}
requires = {self.metadata["requires"]}

# Additional metadata
min_infradsl_version = "1.0.0"
documentation_url = ""
repository_url = ""
license = "MIT"

# Parameter schema (JSON Schema)
parameters_schema = {{
    "type": "object",
    "properties": {{
        # Define your template parameters here
        # Example:
        # "instance_type": {{
        #     "type": "string",
        #     "default": "medium",
        #     "description": "Instance size"
        # }}
    }},
    "required": []
}}

# Output schema
outputs_schema = {{
    "type": "object", 
    "properties": {{
        # Define your template outputs here
        # Example:
        # "instance_id": {{
        #     "type": "string",
        #     "description": "Created instance ID"
        # }}
    }}
}}
'''
        version_file.write_text(content)
        
    def _generate_readme_file(self, readme_file: Path):
        """Generate README.md file"""
        content = f'''# {self.metadata["name"]}

{self.metadata["description"]}

## Overview

<!-- Add your template overview here -->

## Parameters

<!-- Document your template parameters here -->

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| | | | |

## Outputs

<!-- Document your template outputs here -->

| Output | Type | Description |
|--------|------|-------------|
| | | |

## Usage

```python
from infradsl.templates import Template

# Basic usage
resource = Template.{self.metadata["name"]}("my-instance")

# With parameters
resource = (Template.{self.metadata["name"]}("my-instance")
            .with_parameters(
                # Add parameters here
            )
            .production())
```

## Examples

See the `examples/` directory for detailed usage examples.

## Requirements

- InfraDSL >= 1.0.0
{chr(10).join(f"- Template: {req}" for req in self.metadata["requires"])}

## Supported Providers

{chr(10).join(f"- {provider}" for provider in self.metadata["providers"])}

## Author

{self.metadata["author"]}

## License

MIT License
'''
        readme_file.write_text(content)
        
    def _generate_example_file(self, example_file: Path):
        """Generate example usage file"""
        content = f'''#!/usr/bin/env python3
"""
Basic usage example for {self.metadata["name"]} template
"""

from infradsl.templates import Template

# Basic usage
resource = Template.{self.metadata["name"]}("example-instance")

# Customized usage
customized_resource = (
    Template.{self.metadata["name"]}("custom-instance")
    .with_parameters(
        # Add your parameters here
    )
    .production()
)

# Print template information
print(f"Template: {{resource.get_metadata().name}}")
print(f"Version: {{resource.get_metadata().version}}")
print(f"Description: {{resource.get_metadata().description}}")
'''
        example_file.write_text(content)
        
    def _validate_template(self) -> bool:
        """Validate template structure"""
        console.print("[blue]Validating template...")
        
        required_files = ["README.md", "version.py", "template.py"]
        missing_files = []
        
        for file_name in required_files:
            if not (self.template_dir / file_name).exists():
                missing_files.append(file_name)
                
        if missing_files:
            console.print(f"[red]Missing required files: {', '.join(missing_files)}")
            return False
            
        # Validate template.py contains a template class
        template_file = self.template_dir / "template.py"
        try:
            self._validate_template_class(template_file)
        except Exception as e:
            console.print(f"[red]Template validation error: {e}")
            return False
            
        console.print("[green]Template validation passed!")
        return True
        
    def _validate_template_class(self, template_file: Path):
        """Validate template.py contains valid template class"""
        import importlib.util
        
        spec = importlib.util.spec_from_file_location("template", template_file)
        if not spec or not spec.loader:
            raise ValueError("Invalid template.py file")
            
        template_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(template_module)
        
        # Look for template class
        from ..core.templates.base import BaseTemplate
        
        template_classes = []
        for name, obj in vars(template_module).items():
            if (isinstance(obj, type) and 
                issubclass(obj, BaseTemplate) and 
                obj != BaseTemplate):
                template_classes.append(obj)
                
        if not template_classes:
            raise ValueError("No template class found inheriting from BaseTemplate")
        if len(template_classes) > 1:
            raise ValueError("Multiple template classes found, only one allowed per template")
            
    def _push_to_registry(self):
        """Push template to registry"""
        console.print("[blue]Pushing to registry...")
        
        try:
            # Import dynamically to avoid circular imports
            from ..cli.registry import TemplateRegistryClient
            client = TemplateRegistryClient()
            
            if not client.auth_token:
                console.print("[red]Authentication required.")
                console.print("Run: [yellow]infra registry login[/yellow]")
                return
                
            success = client.push_template(str(self.template_dir), self.visibility)
            
            if success:
                console.print("[green]Template successfully published to registry!")
                if client.workspace:
                    console.print(f"Access it with: [cyan]infra registry pull {client.workspace}/{self.metadata['name']}[/cyan]")
            else:
                console.print("[red]Failed to push template to registry")
                
        except Exception as e:
            console.print(f"[red]Registry push failed: {e}")
            
    @classmethod
    def quick_publish(
        cls,
        name: str,
        version: str = "1.0.0", 
        description: str = "",
        author: str = "",
        **kwargs
    ):
        """
        Quick publish with minimal required information.
        
        Usage:
            from infradsl import BuildPushRegistry
            
            if __name__ == "__main__":
                BuildPushRegistry.quick_publish(
                    name="MyTemplate",
                    description="My awesome template"
                )
        """
        return cls(
            name=name,
            version=version,
            description=description or f"Infrastructure template: {name}",
            author=author or "Anonymous",
            **kwargs
        )


# Convenience function for direct import
def publish_template(
    name: str,
    version: str = "1.0.0",
    description: str = "",
    author: str = "",
    **kwargs
):
    """
    Convenience function for publishing templates.
    
    Usage:
        from infradsl import publish_template
        
        if __name__ == "__main__":
            publish_template(
                name="MyTemplate",
                description="My awesome template"
            )
    """
    return BuildPushRegistry(
        name=name,
        version=version,
        description=description or f"Infrastructure template: {name}",
        author=author or "Anonymous",
        **kwargs
    )