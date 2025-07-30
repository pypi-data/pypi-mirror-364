"""
Initialize new InfraDSL project
"""

import os
import json
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Any
from argparse import Namespace

from .base import BaseCommand
from ..utils.errors import CommandError

if TYPE_CHECKING:
    from ..utils.output import Console
    from ..utils.config import CLIConfig


class InitCommand(BaseCommand):
    """Initialize a new InfraDSL project"""
    
    @property
    def name(self) -> str:
        return "init"
    
    @property
    def description(self) -> str:
        return "Initialize a new InfraDSL project"
    
    def register(self, subparsers) -> None:
        """Register command arguments"""
        parser = subparsers.add_parser(
            self.name,
            help=self.description,
            description="Initialize a new InfraDSL project with configuration and templates"
        )
        
        parser.add_argument(
            "name",
            nargs="?",
            help="Project name (default: current directory name)"
        )
        
        parser.add_argument(
            "--provider",
            choices=["digitalocean", "gcp", "aws"],
            action="append",
            help="Cloud provider to configure (can be used multiple times)"
        )
        
        parser.add_argument(
            "--template",
            choices=["minimal", "web-app", "api", "database"],
            default="minimal",
            help="Project template to use (default: minimal)"
        )
        
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force initialization even if project already exists"
        )
        
        self.add_common_arguments(parser)
    
    def execute(self, args: Namespace, config: "CLIConfig", console: "Console") -> int:
        """Execute the init command"""
        try:
            # Determine project name and directory
            project_name = args.name or Path.cwd().name
            
            # If name is provided, create subdirectory; otherwise use current directory
            if args.name:
                project_dir = Path.cwd() / project_name
                # Check if directory exists
                if project_dir.exists() and not args.force:
                    if not console.confirm(f"Directory '{project_name}' exists. Continue?"):
                        console.info("Initialization cancelled")
                        return 0
                project_dir.mkdir(exist_ok=True)
            else:
                project_dir = Path.cwd()
                # Check if project already exists in current directory
                if (project_dir / ".infradsl").exists() and not args.force:
                    console.error("InfraDSL project already exists. Use --force to overwrite.")
                    return 1

            console.info(f"Initializing InfraDSL project: {project_name}")

            # Create project structure
            self._create_project_structure(project_dir, console)

            # Create configuration
            config_data = self._create_project_config(
                project_dir, project_name, args.provider or [], console
            )

            # Create template files
            self._create_template_files(project_dir, args.template, config_data, console)

            # Create .env template
            self._create_env_template(project_dir, args.provider or [], console)

            # Create .gitignore
            self._create_gitignore(project_dir, console)

            console.success(f"✓ InfraDSL project '{project_name}' initialized successfully!")
            console.info("")
            console.info("Next steps:")
            if args.name:
                console.info(f"  cd {project_name}")
            console.info("  1. Copy .env.example to .env and configure credentials")
            console.info("  2. Review and customize infrastructure.py")
            console.info("  3. Run 'infra preview' to see planned changes")
            console.info("  4. Run 'infra apply' to create your infrastructure")

            return 0

        except Exception as e:
            raise CommandError(f"Failed to initialize project: {e}")
    
    def _create_project_structure(self, project_dir: Path, console: "Console") -> None:
        """Create basic project directory structure"""
        console.debug("Creating project structure...")

        # Create .infradsl directory
        infradsl_dir = project_dir / ".infradsl"
        infradsl_dir.mkdir(exist_ok=True)

        # Create subdirectories
        (infradsl_dir / "state").mkdir(exist_ok=True)
        (infradsl_dir / "templates").mkdir(exist_ok=True)
        (infradsl_dir / "hooks").mkdir(exist_ok=True)

        console.debug("✓ Project structure created")

    def _create_project_config(
        self, project_dir: Path, project_name: str, providers: list, console: "Console"
    ) -> Dict[str, Any]:
        """Create project configuration"""
        console.debug("Creating project configuration...")

        config = {
            "project": {
                "name": project_name,
                "version": "1.0.0",
                "description": f"InfraDSL project: {project_name}",
            },
            "providers": {},
            "settings": {
                "auto_approve": False,
                "parallel_operations": 10,
                "state_backend": "file",
                "drift_detection": True,
            },
            "environments": {
                "development": {
                    "auto_approve": False,
                    "parallel_operations": 5,
                },
                "staging": {
                    "auto_approve": False,
                    "parallel_operations": 8,
                },
                "production": {
                    "auto_approve": False,
                    "parallel_operations": 3,
                },
            },
        }

        # Add provider configurations
        for provider in providers:
            if provider == "digitalocean":
                config["providers"]["digitalocean"] = {
                    "type": "digitalocean",
                    "region": "nyc1",
                    "credentials": {
                        "token": "${DIGITALOCEAN_TOKEN}",
                    },
                }
            elif provider == "gcp":
                config["providers"]["gcp"] = {
                    "type": "gcp",
                    "project": "${GOOGLE_CLOUD_PROJECT}",
                    "region": "us-central1",
                    "credentials": {
                        "service_account_path": "${GOOGLE_APPLICATION_CREDENTIALS}",
                    },
                }
            elif provider == "aws":
                config["providers"]["aws"] = {
                    "type": "aws",
                    "region": "us-east-1",
                    "credentials": {
                        "access_key_id": "${AWS_ACCESS_KEY_ID}",
                        "secret_access_key": "${AWS_SECRET_ACCESS_KEY}",
                    },
                }

        # Write configuration file
        config_file = project_dir / ".infradsl" / "config.json"
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

        console.debug("✓ Project configuration created")
        return config
    
    def _create_template_files(
        self, project_dir: Path, template: str, config: Dict[str, Any], console: "Console"
    ) -> None:
        """Create template infrastructure files"""
        console.debug(f"Creating template files for: {template}")

        if template == "minimal":
            self._create_minimal_template(project_dir, config, console)
        elif template == "web-app":
            self._create_web_app_template(project_dir, config, console)
        elif template == "api":
            self._create_api_template(project_dir, config, console)
        elif template == "database":
            self._create_database_template(project_dir, config, console)

        console.debug("✓ Template files created")

    def _create_minimal_template(
        self, project_dir: Path, config: Dict[str, Any], console: "Console"
    ) -> None:
        """Create minimal infrastructure template"""
        providers = list(config["providers"].keys())
        primary_provider = providers[0] if providers else "digitalocean"

        template_content = f'''#!/usr/bin/env python3
"""
{config["project"]["name"]} - InfraDSL Infrastructure
"""
import os
from infradsl import {self._get_provider_import(primary_provider)}, InstanceSize

# Configure provider
{self._get_provider_config(primary_provider)}

# Define infrastructure
vm = (
    {self._get_provider_class(primary_provider)}.VM("example-vm")
    .ubuntu("22.04")
    .size(InstanceSize.SMALL)
    .disk(20)
    .public_ip(True)
    .environment("development")
    .labels(project="{config["project"]["name"]}", purpose="example")
)
'''

        with open(project_dir / "infrastructure.py", "w") as f:
            f.write(template_content)

    def _create_web_app_template(
        self, project_dir: Path, config: Dict[str, Any], console: "Console"
    ) -> None:
        """Create web application template"""
        providers = list(config["providers"].keys())
        primary_provider = providers[0] if providers else "digitalocean"

        template_content = f'''#!/usr/bin/env python3
"""
{config["project"]["name"]} - Web Application Infrastructure
"""
import os
from infradsl import {self._get_provider_import(primary_provider)}, InstanceSize

# Configure provider
{self._get_provider_config(primary_provider)}

# Web server
web_server = (
    {self._get_provider_class(primary_provider)}.VM("web-server")
    .ubuntu("22.04")
    .size(InstanceSize.MEDIUM)
    .disk(40)
    .public_ip(True)
    .environment("production")
    .labels(project="{config["project"]["name"]}", tier="web")
    .user_data("""
#!/bin/bash
apt-get update
apt-get install -y nginx
systemctl start nginx
systemctl enable nginx
""")
)

# Database server
database = (
    {self._get_provider_class(primary_provider)}.VM("database")
    .ubuntu("22.04")
    .size(InstanceSize.MEDIUM)
    .disk(100)
    .public_ip(False)
    .environment("production")
    .labels(project="{config["project"]["name"]}", tier="database")
    .user_data("""
#!/bin/bash
apt-get update
apt-get install -y postgresql postgresql-contrib
systemctl start postgresql
systemctl enable postgresql
""")
)
'''

        with open(project_dir / "infrastructure.py", "w") as f:
            f.write(template_content)

    def _create_api_template(
        self, project_dir: Path, config: Dict[str, Any], console: "Console"
    ) -> None:
        """Create API backend template"""
        providers = list(config["providers"].keys())
        primary_provider = providers[0] if providers else "digitalocean"

        template_content = f'''#!/usr/bin/env python3
"""
{config["project"]["name"]} - API Backend Infrastructure
"""
import os
from infradsl import {self._get_provider_import(primary_provider)}, InstanceSize

# Configure provider
{self._get_provider_config(primary_provider)}

# API server
api_server = (
    {self._get_provider_class(primary_provider)}.VM("api-server")
    .ubuntu("22.04")
    .size(InstanceSize.MEDIUM)
    .disk(30)
    .public_ip(True)
    .environment("production")
    .labels(project="{config["project"]["name"]}", tier="api")
    .user_data("""
#!/bin/bash
apt-get update
apt-get install -y python3 python3-pip nginx
pip3 install fastapi uvicorn
systemctl start nginx
systemctl enable nginx
""")
)

# Redis cache
cache = (
    {self._get_provider_class(primary_provider)}.VM("cache")
    .ubuntu("22.04")
    .size(InstanceSize.SMALL)
    .disk(20)
    .public_ip(False)
    .environment("production")
    .labels(project="{config["project"]["name"]}", tier="cache")
    .user_data("""
#!/bin/bash
apt-get update
apt-get install -y redis-server
systemctl start redis-server
systemctl enable redis-server
""")
)
'''

        with open(project_dir / "infrastructure.py", "w") as f:
            f.write(template_content)

    def _create_database_template(
        self, project_dir: Path, config: Dict[str, Any], console: "Console"
    ) -> None:
        """Create database-focused template"""
        providers = list(config["providers"].keys())
        primary_provider = providers[0] if providers else "digitalocean"

        template_content = f'''#!/usr/bin/env python3
"""
{config["project"]["name"]} - Database Infrastructure
"""
import os
from infradsl import {self._get_provider_import(primary_provider)}, InstanceSize

# Configure provider
{self._get_provider_config(primary_provider)}

# Primary database
primary_db = (
    {self._get_provider_class(primary_provider)}.VM("primary-db")
    .ubuntu("22.04")
    .size(InstanceSize.LARGE)
    .disk(200)
    .public_ip(False)
    .environment("production")
    .labels(project="{config["project"]["name"]}", tier="database", role="primary")
    .user_data("""
#!/bin/bash
apt-get update
apt-get install -y postgresql postgresql-contrib
systemctl start postgresql
systemctl enable postgresql
""")
)

# Read replica
read_replica = (
    {self._get_provider_class(primary_provider)}.VM("read-replica")
    .ubuntu("22.04")
    .size(InstanceSize.MEDIUM)
    .disk(200)
    .public_ip(False)
    .environment("production")
    .labels(project="{config["project"]["name"]}", tier="database", role="replica")
    .user_data("""
#!/bin/bash
apt-get update
apt-get install -y postgresql postgresql-contrib
systemctl start postgresql
systemctl enable postgresql
""")
)
'''

        with open(project_dir / "infrastructure.py", "w") as f:
            f.write(template_content)

    def _create_env_template(
        self, project_dir: Path, providers: list, console: "Console"
    ) -> None:
        """Create .env template file"""
        console.debug("Creating .env template...")

        env_content = f'''# {Path.cwd().name} - Environment Configuration
# Copy this file to .env and fill in your actual values

# General Settings
INFRADSL_ENVIRONMENT=development
INFRADSL_AUTO_APPROVE=false

'''

        for provider in providers:
            if provider == "digitalocean":
                env_content += '''# DigitalOcean Configuration
DIGITALOCEAN_TOKEN=your_digitalocean_token_here

'''
            elif provider == "gcp":
                env_content += '''# Google Cloud Platform Configuration
GOOGLE_CLOUD_PROJECT=your_project_id_here
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GOOGLE_CLOUD_REGION=us-central1

'''
            elif provider == "aws":
                env_content += '''# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=us-east-1

'''

        with open(project_dir / ".env.example", "w") as f:
            f.write(env_content)

        console.debug("✓ .env template created")

    def _create_gitignore(self, project_dir: Path, console: "Console") -> None:
        """Create .gitignore file"""
        console.debug("Creating .gitignore...")

        gitignore_content = '''# InfraDSL
.env
.infradsl/state/
*.pyc
__pycache__/

# Cloud provider credentials
service-account.json
*.pem
*.key

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Python
*.egg-info/
dist/
build/
'''

        with open(project_dir / ".gitignore", "w") as f:
            f.write(gitignore_content)

        console.debug("✓ .gitignore created")

    def _get_provider_import(self, provider: str) -> str:
        """Get provider import statement"""
        imports = {
            "digitalocean": "DigitalOcean",
            "gcp": "GoogleCloud",
            "aws": "AWS",
        }
        return imports.get(provider, "DigitalOcean")

    def _get_provider_config(self, provider: str) -> str:
        """Get provider configuration code"""
        configs = {
            "digitalocean": '''DigitalOcean.configure(
    token=os.getenv("DIGITALOCEAN_TOKEN"),
    region=os.getenv("DIGITALOCEAN_REGION", "nyc1"),
)''',
            "gcp": '''GoogleCloud.configure(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    region=os.getenv("GOOGLE_CLOUD_REGION", "us-central1"),
)''',
            "aws": '''AWS.configure(
    access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
)''',
        }
        return configs.get(provider, configs["digitalocean"])

    def _get_provider_class(self, provider: str) -> str:
        """Get provider class name"""
        classes = {
            "digitalocean": "DigitalOcean",
            "gcp": "GoogleCloud",
            "aws": "AWS",
        }
        return classes.get(provider, "DigitalOcean")