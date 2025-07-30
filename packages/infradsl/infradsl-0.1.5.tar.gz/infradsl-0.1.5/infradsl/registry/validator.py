"""
Template Validator

Validates template packages for registry publishing.
"""

import os
import json
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Tuple
from rich.console import Console

from ..core.templates.base import BaseTemplate


console = Console()


class TemplateValidator:
    """
    Validates template packages for registry compliance.
    
    Checks:
    - Required file structure
    - Template metadata
    - Template class implementation
    - Documentation completeness
    - Example validity
    """
    
    def __init__(self, template_dir: Path):
        self.template_dir = Path(template_dir)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate template package.
        
        Returns:
            (is_valid, validation_report)
        """
        self.errors.clear()
        self.warnings.clear()
        
        # Check file structure
        self._validate_file_structure()
        
        # Validate metadata
        metadata = self._validate_metadata()
        
        # Validate template class
        self._validate_template_class()
        
        # Validate documentation
        self._validate_documentation()
        
        # Validate examples
        self._validate_examples()
        
        # Generate report
        report = {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": metadata,
            "file_count": len(list(self.template_dir.rglob("*"))),
            "validation_timestamp": None  # Would be set by registry
        }
        
        return len(self.errors) == 0, report
        
    def _validate_file_structure(self):
        """Validate required file structure"""
        required_files = [
            "README.md",
            "version.py", 
            "template.py"
        ]
        
        recommended_files = [
            "examples/basic_usage.py",
            ".gitignore"
        ]
        
        # Check required files
        for file_path in required_files:
            full_path = self.template_dir / file_path
            if not full_path.exists():
                self.errors.append(f"Missing required file: {file_path}")
                
        # Check recommended files
        for file_path in recommended_files:
            full_path = self.template_dir / file_path
            if not full_path.exists():
                self.warnings.append(f"Missing recommended file: {file_path}")
                
        # Check for examples directory
        examples_dir = self.template_dir / "examples"
        if examples_dir.exists():
            if not any(examples_dir.glob("*.py")):
                self.warnings.append("Examples directory exists but contains no Python files")
        else:
            self.warnings.append("No examples directory found")
            
        # Check for tests directory
        tests_dir = self.template_dir / "tests"
        if not tests_dir.exists():
            self.warnings.append("No tests directory found")
        elif not any(tests_dir.glob("test_*.py")):
            self.warnings.append("Tests directory exists but contains no test files")
            
    def _validate_metadata(self) -> Dict[str, Any]:
        """Validate version.py metadata"""
        version_file = self.template_dir / "version.py"
        if not version_file.exists():
            return {}
            
        try:
            spec = importlib.util.spec_from_file_location("version", version_file)
            if not spec or not spec.loader:
                self.errors.append("Invalid version.py file")
                return {}
                
            version_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(version_module)
            
            # Required fields
            required_fields = {
                "name": str,
                "version": str,
                "description": str,
                "author": str
            }
            
            metadata = {}
            for field, expected_type in required_fields.items():
                if not hasattr(version_module, field):
                    self.errors.append(f"Missing required metadata field: {field}")
                else:
                    value = getattr(version_module, field)
                    if not isinstance(value, expected_type):
                        self.errors.append(f"Invalid type for {field}: expected {expected_type.__name__}")
                    else:
                        metadata[field] = value
                        
            # Optional fields
            optional_fields = {
                "category": str,
                "tags": list,
                "providers": list,
                "requires": list,
                "min_infradsl_version": str,
                "documentation_url": str,
                "repository_url": str,
                "license": str,
                "parameters_schema": dict,
                "outputs_schema": dict
            }
            
            for field, expected_type in optional_fields.items():
                if hasattr(version_module, field):
                    value = getattr(version_module, field)
                    if not isinstance(value, expected_type):
                        self.warnings.append(f"Invalid type for optional field {field}: expected {expected_type.__name__}")
                    else:
                        metadata[field] = value
                        
            # Validate version format
            if "version" in metadata:
                version_str = metadata["version"]
                if not self._is_valid_version(version_str):
                    self.warnings.append(f"Version '{version_str}' does not follow semantic versioning (x.y.z)")
                    
            # Validate schemas if present
            if "parameters_schema" in metadata:
                self._validate_json_schema(metadata["parameters_schema"], "parameters_schema")
            if "outputs_schema" in metadata:
                self._validate_json_schema(metadata["outputs_schema"], "outputs_schema")
                
            return metadata
            
        except Exception as e:
            self.errors.append(f"Error loading version.py: {e}")
            return {}
            
    def _validate_template_class(self):
        """Validate template.py contains valid template class"""
        template_file = self.template_dir / "template.py"
        if not template_file.exists():
            return
            
        try:
            spec = importlib.util.spec_from_file_location("template", template_file)
            if not spec or not spec.loader:
                self.errors.append("Invalid template.py file")
                return
                
            template_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(template_module)
            
            # Find template classes
            template_classes = []
            for name, obj in vars(template_module).items():
                if (isinstance(obj, type) and 
                    issubclass(obj, BaseTemplate) and 
                    obj != BaseTemplate):
                    template_classes.append((name, obj))
                    
            if not template_classes:
                self.errors.append("No template class found inheriting from BaseTemplate")
                return
            elif len(template_classes) > 1:
                self.warnings.append(f"Multiple template classes found: {[name for name, _ in template_classes]}")
                
            # Validate template class
            template_name, template_class = template_classes[0]
            
            try:
                # Test instantiation
                test_instance = template_class("test")
                
                # Check required methods
                if not hasattr(test_instance, '_create_metadata'):
                    self.errors.append("Template class missing _create_metadata method")
                if not hasattr(test_instance, 'build'):
                    self.errors.append("Template class missing build method")
                    
                # Test metadata creation
                try:
                    metadata = test_instance._create_metadata()
                    if not hasattr(metadata, 'name') or not metadata.name:
                        self.errors.append("Template metadata missing or empty name")
                except Exception as e:
                    self.errors.append(f"Error creating template metadata: {e}")
                    
            except Exception as e:
                self.errors.append(f"Error instantiating template class: {e}")
                
        except Exception as e:
            self.errors.append(f"Error loading template.py: {e}")
            
    def _validate_documentation(self):
        """Validate README.md documentation"""
        readme_file = self.template_dir / "README.md"
        if not readme_file.exists():
            return
            
        try:
            content = readme_file.read_text()
            
            # Check for required sections
            required_sections = [
                "# ",  # Title
                "## Overview" or "## Description",
                "## Usage" or "## Examples",
            ]
            
            recommended_sections = [
                "## Parameters",
                "## Outputs", 
                "## Requirements",
                "## Author",
                "## License"
            ]
            
            for section in required_sections:
                if section not in content:
                    self.warnings.append(f"README missing recommended section: {section.strip('# ')}")
                    
            for section in recommended_sections:
                if section not in content:
                    self.warnings.append(f"README missing recommended section: {section.strip('# ')}")
                    
            # Check minimum length
            if len(content.strip()) < 200:
                self.warnings.append("README.md seems too short (< 200 characters)")
                
            # Check for code examples
            if "```python" not in content:
                self.warnings.append("README.md missing Python code examples")
                
        except Exception as e:
            self.warnings.append(f"Error reading README.md: {e}")
            
    def _validate_examples(self):
        """Validate example files"""
        examples_dir = self.template_dir / "examples"
        if not examples_dir.exists():
            return
            
        python_files = list(examples_dir.glob("*.py"))
        if not python_files:
            self.warnings.append("Examples directory contains no Python files")
            return
            
        for example_file in python_files:
            try:
                # Basic syntax check
                with open(example_file, 'r') as f:
                    content = f.read()
                    
                # Try to compile (basic syntax check)
                compile(content, str(example_file), 'exec')
                
                # Check if it imports templates
                if "from infradsl.templates import Template" not in content:
                    self.warnings.append(f"Example {example_file.name} doesn't import templates")
                    
            except SyntaxError as e:
                self.errors.append(f"Syntax error in example {example_file.name}: {e}")
            except Exception as e:
                self.warnings.append(f"Error validating example {example_file.name}: {e}")
                
    def _is_valid_version(self, version: str) -> bool:
        """Check if version follows semantic versioning"""
        import re
        pattern = r'^\\d+\\.\\d+\\.\\d+(-[\\w\\d\\.]+)?$'
        return bool(re.match(pattern, version))
        
    def _validate_json_schema(self, schema: Dict[str, Any], schema_name: str):
        """Validate JSON schema structure"""
        if not isinstance(schema, dict):
            self.warnings.append(f"{schema_name} is not a valid JSON schema object")
            return
            
        # Basic schema validation
        if "type" not in schema:
            self.warnings.append(f"{schema_name} missing 'type' field")
            
        if schema.get("type") == "object" and "properties" not in schema:
            self.warnings.append(f"{schema_name} is object type but missing 'properties'")
            
    def print_report(self, validation_report: Dict[str, Any]):
        """Print validation report to console"""
        if validation_report["valid"]:
            console.print("[green]✅ Template validation passed!")
        else:
            console.print("[red]❌ Template validation failed!")
            
        if validation_report["errors"]:
            console.print(f"\\n[red]Errors ({len(validation_report['errors'])}):")
            for error in validation_report["errors"]:
                console.print(f"  ❌ {error}")
                
        if validation_report["warnings"]:
            console.print(f"\\n[yellow]Warnings ({len(validation_report['warnings'])}):")
            for warning in validation_report["warnings"]:
                console.print(f"  ⚠️  {warning}")
                
        # Summary
        console.print(f"\\n[blue]Summary:")
        console.print(f"  Files: {validation_report['file_count']}")
        console.print(f"  Errors: {len(validation_report['errors'])}")
        console.print(f"  Warnings: {len(validation_report['warnings'])}")
        
        if validation_report["metadata"]:
            metadata = validation_report["metadata"]
            console.print(f"\\n[cyan]Template Metadata:")
            console.print(f"  Name: {metadata.get('name', 'N/A')}")
            console.print(f"  Version: {metadata.get('version', 'N/A')}")
            console.print(f"  Author: {metadata.get('author', 'N/A')}")
            console.print(f"  Category: {metadata.get('category', 'N/A')}")


def validate_template_package(template_dir: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Convenience function to validate a template package.
    
    Args:
        template_dir: Path to template directory
        
    Returns:
        (is_valid, validation_report)
    """
    validator = TemplateValidator(template_dir)
    return validator.validate()