#!/usr/bin/env python3
"""
Registry Command for InfraDSL CLI

Provides template registry management commands:
- infra registry login
- infra registry push /path/to/template/
- infra registry pull workspace/template-name  
- infra registry list
- infra registry search query
- infra registry info workspace/template-name
"""

import argparse
from typing import Optional, TYPE_CHECKING
from pathlib import Path

from ..utils.output import Console
from .base import BaseCommand

if TYPE_CHECKING:
    # Import for type hints only
    from ..registry import TemplateRegistryClient
    from ..utils.config import CLIConfig


class RegistryCommand(BaseCommand):
    """Registry management command"""
    
    @property
    def name(self) -> str:
        return "registry"
        
    @property
    def description(self) -> str:
        return "Template registry management"
        
    def register(self, subparsers) -> None:
        """Register registry command and subcommands"""
        parser = subparsers.add_parser(
            self.name,
            help=self.description,
            description="Manage InfraDSL template registry"
        )
        
        registry_subparsers = parser.add_subparsers(
            dest="registry_action",
            help="Registry actions",
            metavar="ACTION"
        )
        
        # Login command
        login_parser = registry_subparsers.add_parser(
            "login",
            help="Login to template registry"
        )
        login_parser.add_argument(
            "--registry-url",
            help="Registry URL (default: https://registry.infradsl.dev)"
        )
        
        # Push command
        push_parser = registry_subparsers.add_parser(
            "push", 
            help="Push template to registry"
        )
        push_parser.add_argument(
            "template_path",
            type=Path,
            help="Path to template directory"
        )
        push_parser.add_argument(
            "--visibility",
            choices=["public", "private"],
            default="private",
            help="Template visibility (default: private)"
        )
        push_parser.add_argument(
            "--registry-url",
            help="Registry URL"
        )
        
        # Pull command
        pull_parser = registry_subparsers.add_parser(
            "pull",
            help="Pull template from registry"
        )
        pull_parser.add_argument(
            "template_ref",
            help="Template reference (workspace/name or name)"
        )
        pull_parser.add_argument(
            "--destination", "-d",
            help="Destination directory"
        )
        pull_parser.add_argument(
            "--registry-url",
            help="Registry URL"
        )
        
        # List command
        list_parser = registry_subparsers.add_parser(
            "list",
            help="List templates"
        )
        list_parser.add_argument(
            "--workspace", "-w",
            help="Workspace to list (default: your workspace)"
        )
        list_parser.add_argument(
            "--all",
            action="store_true",
            help="Show templates from all workspaces"
        )
        list_parser.add_argument(
            "--registry-url",
            help="Registry URL"
        )
        
        # Search command
        search_parser = registry_subparsers.add_parser(
            "search",
            help="Search templates"
        )
        search_parser.add_argument(
            "query",
            help="Search query"
        )
        search_parser.add_argument(
            "--workspace", "-w",
            help="Search within specific workspace"
        )
        search_parser.add_argument(
            "--registry-url",
            help="Registry URL"
        )
        
        # Info command
        info_parser = registry_subparsers.add_parser(
            "info",
            help="Get template information"
        )
        info_parser.add_argument(
            "template_ref",
            help="Template reference (workspace/name or name)"
        )
        info_parser.add_argument(
            "--registry-url",
            help="Registry URL"
        )
        
    def execute(self, args: argparse.Namespace, config: "CLIConfig", console: Console) -> int:
        """Execute registry command"""
        if not hasattr(args, 'registry_action') or not args.registry_action:
            console.print("[red]No registry action specified. Use --help for available actions.")
            return 1
            
        try:
            # Import dynamically to avoid circular imports  
            from ..registry import TemplateRegistryClient
            client = TemplateRegistryClient(args.registry_url if hasattr(args, 'registry_url') else None)
            
            if args.registry_action == "login":
                return self._handle_login(client, args, console)
            elif args.registry_action == "push":
                return self._handle_push(client, args, console)  
            elif args.registry_action == "pull":
                return self._handle_pull(client, args, console)
            elif args.registry_action == "list":
                return self._handle_list(client, args, console)
            elif args.registry_action == "search":
                return self._handle_search(client, args, console)
            elif args.registry_action == "info":
                return self._handle_info(client, args, console)
            else:
                console.print(f"[red]Unknown registry action: {args.registry_action}")
                return 1
                
        except Exception as e:
            console.print(f"[red]Registry command failed: {e}")
            return 1
            
    def _handle_login(self, client: "TemplateRegistryClient", args: argparse.Namespace, console: Console) -> int:
        """Handle login command"""
        import click
        
        username = click.prompt("Username")
        password = click.prompt("Password", hide_input=True)
        
        success = client.login(username, password)
        return 0 if success else 1
        
    def _handle_push(self, client: "TemplateRegistryClient", args: argparse.Namespace, console: Console) -> int:
        """Handle push command"""
        if not client.auth_token:
            console.print("[red]Authentication required. Run 'infra auth login' first.")
            return 1
            
        if not args.template_path.exists():
            console.print(f"[red]Template directory not found: {args.template_path}")
            return 1
            
        success = client.push_template(str(args.template_path), args.visibility)
        return 0 if success else 1
        
    def _handle_pull(self, client: "TemplateRegistryClient", args: argparse.Namespace, console: Console) -> int:
        """Handle pull command"""
        success = client.pull_template(args.template_ref, args.destination)
        return 0 if success else 1
        
    def _handle_list(self, client: "TemplateRegistryClient", args: argparse.Namespace, console: Console) -> int:
        """Handle list command"""
        templates = client.list_templates(args.workspace, args.all)
        
        if not templates:
            console.print("No templates found")
            return 0
            
        from rich.table import Table
        
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
        return 0
        
    def _handle_search(self, client: "TemplateRegistryClient", args: argparse.Namespace, console: Console) -> int:
        """Handle search command"""
        templates = client.search_templates(args.query, args.workspace)
        
        if not templates:
            console.print(f"No templates found for query: {args.query}")
            return 0
            
        from rich.table import Table
        
        table = Table(title=f"Search Results: '{args.query}'")
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
        return 0
        
    def _handle_info(self, client: "TemplateRegistryClient", args: argparse.Namespace, console: Console) -> int:
        """Handle info command"""
        template_info = client.get_template_info(args.template_ref)
        
        if not template_info:
            console.print(f"Template not found: {args.template_ref}")
            return 1
            
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
            
        return 0