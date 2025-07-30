"""
Template Package Builder

Utilities for creating well-structured template packages.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from rich.console import Console

console = Console()


class TemplatePackageBuilder:
    """
    Builder for creating template packages with proper structure.
    
    Creates a complete template package with:
    - README.md
    - version.py  
    - template.py
    - examples/
    - tests/
    """
    
    def __init__(self, name: str, directory: str = None):
        self.name = name
        self.directory = Path(directory or name)
        self.metadata = {
            "name": name,
            "version": "1.0.0",
            "description": f"InfraDSL template: {name}",
            "author": "Template Author",
            "category": "general",
            "tags": [],
            "providers": [],
            "requires": []
        }
        
    def set_metadata(self, **metadata) -> "TemplatePackageBuilder":
        """Set template metadata (chainable)"""
        self.metadata.update(metadata)
        return self
        
    def create_package(self, overwrite: bool = False) -> Path:
        """Create the template package structure"""
        if self.directory.exists() and not overwrite:
            raise FileExistsError(f"Directory {self.directory} already exists")
            
        # Create directory structure
        self.directory.mkdir(parents=True, exist_ok=overwrite)
        (self.directory / "examples").mkdir(exist_ok=True)
        (self.directory / "tests").mkdir(exist_ok=True)
        
        # Generate files
        self._create_version_file()
        self._create_readme_file()
        self._create_template_file()
        self._create_example_file()
        self._create_test_file()
        self._create_gitignore()
        
        console.print(f"[green]Created template package: {self.directory}")
        return self.directory
        
    def _create_version_file(self):
        """Create version.py file"""
        content = f'''"""
{self.name} Template Metadata
"""

name = "{self.metadata["name"]}"
version = "{self.metadata["version"]}"
description = "{self.metadata["description"]}"
author = "{self.metadata["author"]}"
category = "{self.metadata["category"]}"
tags = {self.metadata["tags"]!r}
providers = {self.metadata["providers"]!r}
requires = {self.metadata["requires"]!r}

# Additional metadata
min_infradsl_version = "1.0.0"
documentation_url = ""
repository_url = ""
license = "MIT"

# Parameter schema (JSON Schema)
parameters_schema = {{
    "type": "object",
    "properties": {{
        "instance_type": {{
            "type": "string",
            "default": "medium",
            "description": "Instance size (micro, small, medium, large, xlarge)"
        }},
        "environment": {{
            "type": "string",
            "default": "development",
            "description": "Environment (development, staging, production)"
        }}
    }},
    "required": []
}}

# Output schema
outputs_schema = {{
    "type": "object",
    "properties": {{
        "resource_id": {{
            "type": "string", 
            "description": "Created resource ID"
        }},
        "endpoint": {{
            "type": "string",
            "description": "Resource endpoint"
        }}
    }}
}}
'''
        (self.directory / "version.py").write_text(content)
        
    def _create_readme_file(self):
        """Create README.md file"""
        content = f'''# {self.name}

{self.metadata["description"]}

## Overview

This template provides infrastructure resources for {self.name.lower().replace("-", " ")}.

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| instance_type | string | medium | Instance size (micro, small, medium, large, xlarge) |
| environment | string | development | Environment (development, staging, production) |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| resource_id | string | Created resource ID |
| endpoint | string | Resource endpoint |

## Usage

```python
from infradsl.templates import Template

# Basic usage
resource = Template.{self.name}("my-{self.name.lower()}")

# With parameters
resource = (Template.{self.name}("my-{self.name.lower()}")
            .with_parameters(
                instance_type="large",
                environment="production"
            )
            .production())

# Get outputs
outputs = resource.get_outputs()
print(f"Resource ID: {{outputs['resource_id']}}")
print(f"Endpoint: {{outputs['endpoint']}}")
```

## Examples

See the `examples/` directory for detailed usage examples.

## Testing

Run template tests:

```bash
python -m pytest tests/
```

## Requirements

- InfraDSL >= 1.0.0
{chr(10).join(f"- Template: {req}" for req in self.metadata["requires"])}

## Supported Providers

{chr(10).join(f"- {provider.upper()}" for provider in self.metadata["providers"]) or "- All providers"}

## Author

{self.metadata["author"]}

## License

MIT License

## Publishing

To publish this template to the registry:

```python
from infradsl import BuildPushRegistry

if __name__ == "__main__":
    BuildPushRegistry(
        name="{self.name}",
        version="{self.metadata["version"]}",
        description="{self.metadata["description"]}",
        author="{self.metadata["author"]}",
        category="{self.metadata["category"]}",
        tags={self.metadata["tags"]!r},
        providers={self.metadata["providers"]!r},
        visibility="public"  # or "private"
    )
```

Then run:

```bash
python template.py
```
'''
        (self.directory / "README.md").write_text(content)
        
    def _create_template_file(self):
        """Create template.py file"""
        content = f'''"""
{self.name} Template

{self.metadata["description"]}
"""

from typing import List, Any
from infradsl.core.templates.base import BaseTemplate, TemplateMetadata, TemplateContext


class {self.name}Template(BaseTemplate):
    """
    {self.name} Template
    
    {self.metadata["description"]}
    """
    
    def _create_metadata(self) -> TemplateMetadata:
        # Import metadata from version.py
        from . import version
        
        return TemplateMetadata(
            name=version.name,
            version=version.version,
            description=version.description,
            author=version.author,
            category=version.category,
            tags=version.tags,
            providers=version.providers,
            requires=version.requires,
            min_infradsl_version=version.min_infradsl_version,
            parameters_schema=version.parameters_schema,
            outputs_schema=version.outputs_schema,
            documentation_url=version.documentation_url,
            repository_url=version.repository_url
        )
        
    def build(self, context: TemplateContext) -> List[Any]:
        """Build the template resources"""
        resources = []
        
        # Get parameters
        instance_type = context.parameters.get("instance_type", "medium")
        environment = context.parameters.get("environment", "development")
        
        # TODO: Implement your template logic here
        # Example:
        # from infradsl.resources.aws.compute.ec2 import AWSEC2
        # 
        # vm = (AWSEC2(context.name)
        #       .instance_type(instance_type)
        #       .ubuntu("22.04"))
        #       
        # if environment == "production":
        #     vm = vm.production()
        # elif environment == "staging":
        #     vm = vm.staging()
        # else:
        #     vm = vm.development()
        #     
        # resources.append(vm)
        # 
        # # Set outputs
        # self.set_output("resource_id", "vm-resource-id")
        # self.set_output("endpoint", "vm-endpoint")
        
        return resources


# Auto-publish to registry when run directly
if __name__ == "__main__":
    from infradsl import BuildPushRegistry
    
    BuildPushRegistry(
        name="{self.name}",
        version="{self.metadata["version"]}",
        description="{self.metadata["description"]}",
        author="{self.metadata["author"]}",
        category="{self.metadata["category"]}",
        tags={self.metadata["tags"]!r},
        providers={self.metadata["providers"]!r},
        visibility="private"  # Change to "public" to make publicly available
    )
'''
        (self.directory / "template.py").write_text(content)
        
    def _create_example_file(self):
        """Create example usage file"""
        content = f'''#!/usr/bin/env python3
"""
{self.name} Template Usage Examples
"""

from infradsl.templates import Template


def basic_example():
    """Basic usage example"""
    resource = Template.{self.name}("basic-example")
    
    print(f"Created template: {{resource.context.name}}")
    print(f"Template version: {{resource.get_metadata().version}}")
    

def customized_example():
    """Customized usage example"""
    resource = (
        Template.{self.name}("customized-example")
        .with_parameters(
            instance_type="large",
            environment="production"
        )
        .production()
    )
    
    print(f"Created customized template: {{resource.context.name}}")
    print(f"Parameters: {{resource.context.parameters}}")
    print(f"Environment: {{resource.context.environment}}")


def extended_example():
    """Extended template example"""
    # Example of extending with another template
    resource = (
        Template.{self.name}("extended-example")
        .extend("Database")  # Extend with database template
        .with_parameters(
            instance_type="xlarge",
            environment="production",
            # Database parameters
            engine="postgresql",
            allocated_storage=500
        )
        .production()
    )
    
    print(f"Created extended template: {{resource.context.name}}")
    print(f"Extensions: {{resource.context.extensions}}")


if __name__ == "__main__":
    print("=== {self.name} Template Examples ===")
    
    print("\\n1. Basic Example:")
    basic_example()
    
    print("\\n2. Customized Example:")
    customized_example()
    
    print("\\n3. Extended Example:")
    extended_example()
    
    print("\\n✅ All examples completed!")
'''
        (self.directory / "examples" / "basic_usage.py").write_text(content)
        
    def _create_test_file(self):
        """Create test file"""
        content = f'''"""
Tests for {self.name} Template
"""

import pytest
from infradsl.templates import Template


class Test{self.name}Template:
    """Test suite for {self.name} template"""
    
    def test_template_creation(self):
        """Test basic template creation"""
        template = Template.{self.name}("test-instance")
        
        assert template.context.name == "test-instance"
        assert template.get_metadata().name == "{self.name}"
        assert template.get_metadata().version == "{self.metadata["version"]}"
        
    def test_parameter_customization(self):
        """Test parameter customization"""
        template = (
            Template.{self.name}("test-instance")
            .with_parameters(
                instance_type="large",
                environment="production"
            )
        )
        
        assert template.context.parameters["instance_type"] == "large"
        assert template.context.parameters["environment"] == "production"
        
    def test_environment_configuration(self):
        """Test environment configuration"""
        template = Template.{self.name}("test-instance").production()
        
        assert template.context.environment == "production"
        
    def test_parameter_override(self):
        """Test parameter override"""
        template = (
            Template.{self.name}("test-instance")
            .with_parameters(instance_type="medium")
            .override(instance_type="large")
        )
        
        assert template.context.parameters["instance_type"] == "medium"
        assert template.context.overrides["instance_type"] == "large"
        
    def test_template_extension(self):
        """Test template extension"""
        template = (
            Template.{self.name}("test-instance")
            .extend("Database")
        )
        
        assert "Database" in template.context.extensions
        
    def test_metadata_validation(self):
        """Test template metadata"""
        template = Template.{self.name}("test-instance")
        metadata = template.get_metadata()
        
        assert metadata.name == "{self.name}"
        assert metadata.version == "{self.metadata["version"]}"
        assert metadata.description == "{self.metadata["description"]}"
        assert metadata.author == "{self.metadata["author"]}"
        assert metadata.category == "{self.metadata["category"]}"
        
        # Test schema validation
        assert "parameters_schema" in metadata.to_dict()
        assert "outputs_schema" in metadata.to_dict()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
        (self.directory / "tests" / f"test_{self.name.lower()}.py").write_text(content)
        
    def _create_gitignore(self):
        """Create .gitignore file"""
        content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log

# InfraDSL
.infradsl/
*.tfstate
*.tfstate.*
.terraform/
'''
        (self.directory / ".gitignore").write_text(content)


def create_template_package(
    name: str, 
    directory: str = None,
    **metadata
) -> Path:
    """
    Convenience function to create a template package.
    
    Args:
        name: Template name
        directory: Directory to create (defaults to name)
        **metadata: Template metadata
        
    Returns:
        Path to created template directory
    """
    builder = TemplatePackageBuilder(name, directory)
    if metadata:
        builder.set_metadata(**metadata)
    return builder.create_package()