#!/usr/bin/env python3
"""
Auth Command for InfraDSL CLI

Provides authentication management commands:
- infra auth setup     - Configure Firebase authentication
- infra auth login     - Login with email/password
- infra auth register  - Register new account
- infra auth logout    - Logout and clear tokens
- infra auth whoami    - Show current user info
"""

import argparse
from typing import Optional, TYPE_CHECKING
from pathlib import Path

from ..utils.output import Console
from .base import BaseCommand
from ...auth import FirebaseAuth, setup_firebase_auth_interactive
from ...core.config import get_config, set_config

if TYPE_CHECKING:
    from ..utils.config import CLIConfig


class AuthCommand(BaseCommand):
    """Authentication management command"""
    
    @property
    def name(self) -> str:
        return "auth"
        
    @property
    def description(self) -> str:
        return "Authentication management"
        
    def register(self, subparsers) -> None:
        """Register auth command and subcommands"""
        parser = subparsers.add_parser(
            self.name,
            help=self.description,
            description="Manage InfraDSL authentication"
        )
        
        auth_subparsers = parser.add_subparsers(
            dest="auth_action",
            help="Authentication actions",
            metavar="ACTION"
        )
        
        # Setup command
        setup_parser = auth_subparsers.add_parser(
            "setup",
            help="Configure Firebase authentication"
        )
        setup_parser.add_argument(
            "--api-key",
            help="Firebase Web API key"
        )
        setup_parser.add_argument(
            "--project-id",
            help="Firebase project ID"
        )
        
        # Login command
        login_parser = auth_subparsers.add_parser(
            "login",
            help="Login with email and password"
        )
        login_parser.add_argument(
            "--email",
            help="Email address"
        )
        login_parser.add_argument(
            "--password",
            help="Password (will prompt if not provided)"
        )
        
        # Register command
        register_parser = auth_subparsers.add_parser(
            "register",
            help="Register new account"
        )
        register_parser.add_argument(
            "--email",
            help="Email address"
        )
        register_parser.add_argument(
            "--password",
            help="Password (will prompt if not provided)"
        )
        register_parser.add_argument(
            "--display-name",
            help="Display name"
        )
        
        # Logout command
        auth_subparsers.add_parser(
            "logout",
            help="Logout and clear tokens"
        )
        
        # Whoami command
        auth_subparsers.add_parser(
            "whoami",
            help="Show current user info"
        )
        
    def execute(self, args: argparse.Namespace, config: "CLIConfig", console: Console) -> int:
        """Execute auth command"""
        if not hasattr(args, 'auth_action') or not args.auth_action:
            console.print("[red]No auth action specified. Use --help for available actions.")
            return 1
            
        try:
            if args.auth_action == "setup":
                return self._handle_setup(args, console)
            elif args.auth_action == "login":
                return self._handle_login(args, console)
            elif args.auth_action == "register":
                return self._handle_register(args, console)
            elif args.auth_action == "logout":
                return self._handle_logout(args, console)
            elif args.auth_action == "whoami":
                return self._handle_whoami(args, console)
            else:
                console.print(f"[red]Unknown auth action: {args.auth_action}")
                return 1
                
        except Exception as e:
            console.print(f"[red]Auth command failed: {e}")
            return 1
            
    def _handle_setup(self, args: argparse.Namespace, console: Console) -> int:
        """Handle setup command"""
        if args.api_key and args.project_id:
            # Non-interactive setup
            auth = FirebaseAuth()
            success = auth.setup_firebase_project(args.api_key, args.project_id)
            return 0 if success else 1
        else:
            # Interactive setup
            success = setup_firebase_auth_interactive()
            return 0 if success else 1
            
    def _handle_login(self, args: argparse.Namespace, console: Console) -> int:
        """Handle login command"""
        import click
        
        # Get email and password
        email = args.email or click.prompt("Email")
        password = args.password or click.prompt("Password", hide_input=True)
        
        # Authenticate with Firebase
        auth = FirebaseAuth()
        user_data = auth.sign_in_with_email(email, password)
        
        if not user_data:
            return 1
            
        # Generate workspace from email
        workspace = auth.get_workspace_from_email(email)
        
        # Store authentication data
        config = get_config()
        if "auth" not in config:
            config["auth"] = {}
            
        config["auth"].update({
            "user_id": user_data["localId"],
            "email": user_data["email"],
            "id_token": user_data["idToken"],
            "refresh_token": user_data["refreshToken"],
            "workspace": workspace,
            "display_name": user_data.get("displayName", ""),
            "provider": "firebase"
        })
        
        # Also store in registry section for backward compatibility
        if "registry" not in config:
            config["registry"] = {}
        config["registry"].update({
            "auth_token": user_data["idToken"],
            "workspace": workspace,
            "username": email
        })
        
        set_config(config)
        
        console.print(f"[green]✅ Successfully logged in!")
        console.print(f"Email: {email}")
        console.print(f"Workspace: {workspace}")
        
        return 0
        
    def _handle_register(self, args: argparse.Namespace, console: Console) -> int:
        """Handle register command"""
        import click
        
        # Get registration details
        email = args.email or click.prompt("Email")
        password = args.password or click.prompt("Password", hide_input=True, confirmation_prompt=True)
        display_name = args.display_name or click.prompt("Display Name", default="")
        
        # Register with Firebase
        auth = FirebaseAuth()
        user_data = auth.sign_up_with_email(email, password, display_name)
        
        if not user_data:
            return 1
            
        # Generate workspace from email
        workspace = auth.get_workspace_from_email(email)
        
        console.print(f"[green]✅ Account created successfully!")
        console.print(f"Email: {email}")
        console.print(f"Workspace: {workspace}")
        console.print("\nYou can now login with: [cyan]infra auth login")
        
        return 0
        
    def _handle_logout(self, args: argparse.Namespace, console: Console) -> int:
        """Handle logout command"""
        config = get_config()
        
        # Clear auth data
        if "auth" in config:
            del config["auth"]
        if "registry" in config:
            if "auth_token" in config["registry"]:
                del config["registry"]["auth_token"]
            if "username" in config["registry"]:
                del config["registry"]["username"]
            if "workspace" in config["registry"]:
                del config["registry"]["workspace"]
                
        set_config(config)
        
        console.print("[green]✅ Successfully logged out!")
        return 0
        
    def _handle_whoami(self, args: argparse.Namespace, console: Console) -> int:
        """Handle whoami command"""
        config = get_config()
        auth_data = config.get("auth", {})
        
        if not auth_data:
            console.print("[yellow]Not logged in. Use 'infra auth login' to authenticate.")
            return 0
            
        console.print("[bold cyan]Current User:[/bold cyan]")
        console.print(f"Email: {auth_data.get('email', 'N/A')}")
        console.print(f"Display Name: {auth_data.get('display_name', 'N/A')}")
        console.print(f"Workspace: {auth_data.get('workspace', 'N/A')}")
        console.print(f"User ID: {auth_data.get('user_id', 'N/A')}")
        console.print(f"Provider: {auth_data.get('provider', 'N/A')}")
        
        # Check if token is still valid
        if auth_data.get('id_token'):
            auth = FirebaseAuth()
            user_info = auth.verify_token(auth_data['id_token'])
            if user_info:
                console.print(f"Token Status: [green]Valid[/green]")
            else:
                console.print(f"Token Status: [red]Expired[/red]")
                console.print("[yellow]Run 'infra auth login' to refresh your session.")
        else:
            console.print(f"Token Status: [red]None[/red]")
            
        return 0