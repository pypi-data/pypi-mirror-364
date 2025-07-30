"""
InfraDSL Template Registry CLI Commands

Provides CLI commands for interacting with the template registry:
- infra registry login
- infra registry push /path/to/template/
- infra registry pull workspace/template-name
- infra registry list
- infra registry search query
- infra registry info workspace/template-name

Template Structure:
my-template/
├── README.md          # Template documentation
├── version.py          # Version and metadata
├── template.py         # Main template implementation
├── examples/          # Usage examples (optional)
└── tests/            # Template tests (optional)
"""

import os
import json
import tarfile
import tempfile
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
import click
from rich.console import Console
from rich.table import Table
from rich.progress import track

from ..core.templates.base import BaseTemplate, TemplateMetadata
from ..core.config import get_config, set_config


console = Console()


class TemplateRegistryClient:
    """Client for interacting with the InfraDSL template registry"""
    
    def __init__(self, registry_url: str = None):
        self.registry_url = registry_url or "https://registry.infradsl.dev"
        self.auth_token = self._get_auth_token()
        self.workspace = self._get_workspace()
        
    def _get_auth_token(self) -> Optional[str]:
        """Get stored authentication token"""
        config = get_config()
        return config.get("registry", {}).get("auth_token")
        
    def _get_workspace(self) -> Optional[str]:
        """Get current workspace"""
        config = get_config()
        return config.get("registry", {}).get("workspace")
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated request to registry"""
        headers = kwargs.pop("headers", {})
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        headers["User-Agent"] = "InfraDSL-CLI/1.0"
        
        url = f"{self.registry_url}/api/v1{endpoint}"
        response = requests.request(method, url, headers=headers, **kwargs)
        
        if response.status_code == 401:
            raise click.ClickException("Authentication required. Run 'infra auth login' first.")
        elif response.status_code >= 400:
            try:
                error_data = response.json()
                error_msg = error_data.get("message", f"HTTP {response.status_code}")
            except:
                error_msg = f"HTTP {response.status_code}"
            raise click.ClickException(f"Registry error: {error_msg}")
            
        return response
        
    def login(self, username: str, password: str) -> bool:
        """Authenticate with the registry (deprecated - use 'infra auth login')"""
        console.print("[yellow]Registry login is deprecated. Use 'infra auth login' for Firebase authentication.")
        console.print("[yellow]This will redirect to Firebase auth...")
        
        # Import and use Firebase auth
        try:
            from ..auth import FirebaseAuth
            
            auth = FirebaseAuth()
            user_data = auth.sign_in_with_email(username, password)
            
            if not user_data:
                return False
                
            # Generate workspace from email
            workspace = auth.get_workspace_from_email(username)
            
            # Store authentication data
            config = get_config()
            if "registry" not in config:
                config["registry"] = {}
            config["registry"]["auth_token"] = user_data["idToken"]
            config["registry"]["workspace"] = workspace
            config["registry"]["username"] = username
            set_config(config)
            
            self.auth_token = user_data["idToken"]
            self.workspace = workspace
            
            console.print(f"[green]Successfully logged in as {username} (workspace: {workspace})")
            console.print("[cyan]Note: Use 'infra auth login' for future logins")
            return True
            
        except Exception as e:
            console.print(f"[red]Firebase authentication failed: {e}")
            console.print("[yellow]Please ensure Firebase is configured with 'infra auth setup'")
            return False
            
    def push_template(self, template_path: str, visibility: str = "private") -> bool:
        """Push template to registry"""
        template_dir = Path(template_path)
        if not template_dir.exists() or not template_dir.is_dir():
            console.print(f"[red]Template directory not found: {template_path}")
            return False
            
        # Validate template structure
        validation_result = self._validate_template_structure(template_dir)
        if not validation_result["valid"]:
            console.print(f"[red]Template validation failed:")
            for error in validation_result["errors"]:
                console.print(f"  - {error}")
            return False
            
        template_metadata = validation_result["metadata"]
        
        try:
            # Create template archive
            with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as temp_file:
                self._create_template_archive(template_dir, temp_file.name)
                
                # Upload to registry
                with open(temp_file.name, "rb") as archive_file:
                    files = {"template": archive_file}
                    data = {
                        "name": template_metadata["name"],
                        "version": template_metadata["version"],
                        "visibility": visibility,
                        "metadata": json.dumps(template_metadata)
                    }
                    
                    response = self._make_request("POST", "/templates", files=files, data=data)
                    
                    if response.status_code == 201:
                        template_info = response.json()
                        console.print(f"[green]Successfully pushed template:")
                        console.print(f"  Name: {template_info['name']}")
                        console.print(f"  Version: {template_info['version']}")  
                        console.print(f"  Workspace: {self.workspace}")
                        console.print(f"  Visibility: {visibility}")
                        console.print(f"  Registry URL: {template_info['registry_url']}")
                        return True
                    else:
                        console.print(f"[red]Push failed: HTTP {response.status_code}")
                        return False
                        
        except Exception as e:
            console.print(f"[red]Push failed: {e}")
            return False
        finally:
            # Clean up temp file
            if "temp_file" in locals():
                os.unlink(temp_file.name)
                
    def pull_template(self, template_ref: str, destination: str = None) -> bool:
        """Pull template from registry"""
        # Parse template reference: workspace/template-name or template-name
        if "/" in template_ref:
            workspace, template_name = template_ref.split("/", 1)
        else:
            workspace = self.workspace
            template_name = template_ref
            
        if not workspace:
            console.print("[red]No workspace specified. Use format: workspace/template-name")
            return False
            
        try:
            # Download template
            response = self._make_request("GET", f"/templates/{workspace}/{template_name}/download")
            
            if response.status_code == 200:
                # Determine destination
                if destination is None:
                    destination = template_name
                    
                dest_path = Path(destination)
                if dest_path.exists():
                    if not click.confirm(f"Directory {destination} already exists. Overwrite?"):
                        return False
                        
                # Extract template
                with tempfile.NamedTemporaryFile(suffix=".tar.gz") as temp_file:
                    temp_file.write(response.content)
                    temp_file.flush()
                    
                    with tarfile.open(temp_file.name, "r:gz") as tar:
                        tar.extractall(dest_path.parent if dest_path.name != "." else ".")
                        
                console.print(f"[green]Successfully pulled template to {destination}")
                return True
            else:
                console.print(f"[red]Template not found: {workspace}/{template_name}")
                return False
                
        except Exception as e:
            console.print(f"[red]Pull failed: {e}")
            return False
            
    def list_templates(self, workspace: str = None, show_all: bool = False) -> List[Dict[str, Any]]:
        """List templates in workspace"""
        try:
            params = {}
            if workspace:
                params["workspace"] = workspace
            elif not show_all and self.workspace:
                params["workspace"] = self.workspace
                
            response = self._make_request("GET", "/templates", params=params)
            
            if response.status_code == 200:
                return response.json()["templates"]
            else:
                return []
                
        except Exception as e:
            console.print(f"[red]List failed: {e}")
            return []
            
    def search_templates(self, query: str, workspace: str = None) -> List[Dict[str, Any]]:
        """Search templates"""
        try:
            params = {"q": query}
            if workspace:
                params["workspace"] = workspace
                
            response = self._make_request("GET", "/templates/search", params=params)
            
            if response.status_code == 200:
                return response.json()["templates"]
            else:
                return []
                
        except Exception as e:
            console.print(f"[red]Search failed: {e}")
            return []
            
    def get_template_info(self, template_ref: str) -> Optional[Dict[str, Any]]:
        """Get template information"""
        if "/" in template_ref:
            workspace, template_name = template_ref.split("/", 1)
        else:
            workspace = self.workspace
            template_name = template_ref
            
        try:
            response = self._make_request("GET", f"/templates/{workspace}/{template_name}")
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            console.print(f"[red]Info failed: {e}")
            return None
            
    def _validate_template_structure(self, template_dir: Path) -> Dict[str, Any]:
        """Validate template directory structure"""
        errors = []
        
        # Check required files
        readme_file = template_dir / "README.md"
        version_file = template_dir / "version.py"
        template_file = template_dir / "template.py"
        
        if not readme_file.exists():
            errors.append("README.md file is required")
        if not version_file.exists():
            errors.append("version.py file is required")
        if not template_file.exists():
            errors.append("template.py file is required")
            
        if errors:
            return {"valid": False, "errors": errors}
            
        # Load version metadata
        try:
            version_data = self._load_version_file(version_file)
        except Exception as e:
            errors.append(f"Invalid version.py: {e}")
            return {"valid": False, "errors": errors}
            
        # Validate template.py
        try:
            self._validate_template_file(template_file)
        except Exception as e:
            errors.append(f"Invalid template.py: {e}")
            return {"valid": False, "errors": errors}
            
        return {
            "valid": True,
            "metadata": version_data,
            "errors": []
        }
        
    def _load_version_file(self, version_file: Path) -> Dict[str, Any]:
        """Load version.py metadata"""
        import importlib.util
        
        spec = importlib.util.spec_from_file_location("version", version_file)
        if not spec or not spec.loader:
            raise ValueError("Invalid version.py file")
            
        version_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(version_module)
        
        # Extract metadata
        metadata = {}
        required_fields = ["name", "version", "description", "author"]
        
        for field in required_fields:
            if not hasattr(version_module, field):
                raise ValueError(f"Missing required field: {field}")
            metadata[field] = getattr(version_module, field)
            
        # Optional fields
        optional_fields = ["tags", "category", "providers", "requires", "examples"]
        for field in optional_fields:
            if hasattr(version_module, field):
                metadata[field] = getattr(version_module, field)
            else:
                metadata[field] = [] if field in ["tags", "providers", "requires", "examples"] else ""
                
        return metadata
        
    def _validate_template_file(self, template_file: Path):
        """Validate template.py contains valid template class"""
        import importlib.util
        
        spec = importlib.util.spec_from_file_location("template", template_file)
        if not spec or not spec.loader:
            raise ValueError("Invalid template.py file")
            
        template_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(template_module)
        
        # Look for template class
        template_classes = []
        for name, obj in vars(template_module).items():
            if (isinstance(obj, type) and 
                issubclass(obj, BaseTemplate) and 
                obj != BaseTemplate):
                template_classes.append(obj)
                
        if not template_classes:
            raise ValueError("No template class found inheriting from BaseTemplate")
        if len(template_classes) > 1:
            raise ValueError("Multiple template classes found, only one allowed")
            
    def _create_template_archive(self, template_dir: Path, archive_path: str):
        """Create template archive"""
        with tarfile.open(archive_path, "w:gz") as tar:
            for file_path in template_dir.rglob("*"):
                if file_path.is_file() and not self._should_exclude_file(file_path):
                    arcname = file_path.relative_to(template_dir)
                    tar.add(file_path, arcname=arcname)
                    
    def _should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from archive"""
        exclude_patterns = [
            "__pycache__",
            "*.pyc", 
            "*.pyo",
            ".git",
            ".gitignore",
            "*.log",
            ".DS_Store",
            "Thumbs.db"
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in exclude_patterns)


# CLI Commands

@click.group()
def registry():
    """Template registry commands"""
    pass


@registry.command()
@click.option("--registry-url", help="Registry URL (default: https://registry.infradsl.dev)")
def login(registry_url):
    """Login to template registry"""
    username = click.prompt("Username")
    password = click.prompt("Password", hide_input=True)
    
    client = TemplateRegistryClient(registry_url)
    success = client.login(username, password)
    
    if not success:
        raise click.ClickException("Login failed")


@registry.command()
@click.argument("template_path", type=click.Path(exists=True))
@click.option("--visibility", type=click.Choice(["public", "private"]), default="private",
              help="Template visibility (default: private)")
@click.option("--registry-url", help="Registry URL")
def push(template_path, visibility, registry_url):
    """Push template to registry"""
    client = TemplateRegistryClient(registry_url)
    
    if not client.auth_token:
        raise click.ClickException("Authentication required. Run 'infra registry login' first.")
        
    success = client.push_template(template_path, visibility)
    
    if not success:
        raise click.ClickException("Push failed")


@registry.command()
@click.argument("template_ref")
@click.option("--destination", "-d", help="Destination directory")
@click.option("--registry-url", help="Registry URL")
def pull(template_ref, destination, registry_url):
    """Pull template from registry"""
    client = TemplateRegistryClient(registry_url)
    
    success = client.pull_template(template_ref, destination)
    
    if not success:
        raise click.ClickException("Pull failed")


@registry.command("list")
@click.option("--workspace", "-w", help="Workspace to list (default: your workspace)")
@click.option("--all", "show_all", is_flag=True, help="Show templates from all workspaces")
@click.option("--registry-url", help="Registry URL")
def list_templates(workspace, show_all, registry_url):
    """List templates"""
    client = TemplateRegistryClient(registry_url)
    
    templates = client.list_templates(workspace, show_all)
    
    if not templates:
        console.print("No templates found")
        return
        
    table = Table(title="InfraDSL Templates")
    table.add_column("Workspace", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Version", style="green")
    table.add_column("Description", style="white")
    table.add_column("Visibility", style="yellow")
    
    for template in templates:
        table.add_row(
            template["workspace"],
            template["name"],
            template["version"],
            template["description"][:50] + "..." if len(template["description"]) > 50 else template["description"],
            template["visibility"]
        )
        
    console.print(table)


@registry.command()
@click.argument("query")
@click.option("--workspace", "-w", help="Search within specific workspace")
@click.option("--registry-url", help="Registry URL")
def search(query, workspace, registry_url):
    """Search templates"""
    client = TemplateRegistryClient(registry_url)
    
    templates = client.search_templates(query, workspace)
    
    if not templates:
        console.print(f"No templates found for query: {query}")
        return
        
    table = Table(title=f"Search Results: '{query}'")
    table.add_column("Workspace/Name", style="cyan")
    table.add_column("Version", style="green")
    table.add_column("Description", style="white")
    table.add_column("Tags", style="yellow")
    
    for template in templates:
        table.add_row(
            f"{template['workspace']}/{template['name']}",
            template["version"],
            template["description"][:50] + "..." if len(template["description"]) > 50 else template["description"],
            ", ".join(template.get("tags", []))
        )
        
    console.print(table)


@registry.command()
@click.argument("template_ref")
@click.option("--registry-url", help="Registry URL")
def info(template_ref, registry_url):
    """Get template information"""
    client = TemplateRegistryClient(registry_url)
    
    template_info = client.get_template_info(template_ref)
    
    if not template_info:
        console.print(f"Template not found: {template_ref}")
        return
        
    console.print(f"[bold cyan]{template_info['workspace']}/{template_info['name']}[/bold cyan]")
    console.print(f"Version: {template_info['version']}")
    console.print(f"Description: {template_info['description']}")
    console.print(f"Author: {template_info['author']}")
    console.print(f"Category: {template_info.get('category', 'N/A')}")
    console.print(f"Tags: {', '.join(template_info.get('tags', []))}")
    console.print(f"Providers: {', '.join(template_info.get('providers', []))}")
    console.print(f"Visibility: {template_info['visibility']}")
    console.print(f"Downloads: {template_info.get('download_count', 0)}")
    console.print(f"Created: {template_info['created_at']}")
    console.print(f"Updated: {template_info['updated_at']}")
    
    if template_info.get('requires'):
        console.print(f"Dependencies: {', '.join(template_info['requires'])}")


if __name__ == "__main__":
    registry()