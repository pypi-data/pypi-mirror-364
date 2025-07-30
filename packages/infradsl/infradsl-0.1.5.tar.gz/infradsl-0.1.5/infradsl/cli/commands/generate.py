"""
Provider generation CLI command
"""

import os
import json
from argparse import Namespace
from pathlib import Path
from typing import TYPE_CHECKING
from typing import List

from .base import BaseCommand
from ..utils.errors import CommandError
from ...core.generation.provider_generator import (
    ProviderGenerator,
    GenerationConfig,
    ProviderType,
    ResourceType,
    ResourceDefinition,
    ResourceField,
    create_aws_generator,
    create_gcp_generator,
    create_digitalocean_generator,
)

if TYPE_CHECKING:
    from ..utils.output import Console
    from ..utils.config import CLIConfig


class GenerateCommand(BaseCommand):
    """Provider generation command"""

    @property
    def name(self) -> str:
        return "generate"

    @property
    def description(self) -> str:
        return "Generate provider code from APIs, schemas, and specifications"

    def register(self, subparsers) -> None:
        """Register generate command and subcommands"""
        parser = subparsers.add_parser(
            self.name,
            help=self.description,
            description="Generate provider code from APIs, schemas, and specifications",
        )

        generate_subparsers = parser.add_subparsers(
            dest="generate_action", help="Generation actions"
        )

        # Provider generation
        provider_parser = generate_subparsers.add_parser(
            "provider", help="Generate provider code"
        )
        provider_parser.add_argument(
            "provider_type",
            choices=["aws", "gcp", "azure", "digitalocean", "cloudflare"],
            help="Provider type to generate",
        )
        provider_parser.add_argument(
            "--output", "-o", required=True, help="Output directory for generated code"
        )
        provider_parser.add_argument("--openapi", help="OpenAPI specification file")
        provider_parser.add_argument(
            "--terraform", help="Terraform provider schema file"
        )
        provider_parser.add_argument(
            "--resources", help="JSON file with resource definitions"
        )
        provider_parser.add_argument(
            "--template-dir", help="Directory containing custom templates"
        )
        provider_parser.add_argument(
            "--no-async",
            action="store_true",
            help="Generate synchronous code (default: async)",
        )
        provider_parser.add_argument(
            "--no-tests", action="store_true", help="Skip test generation"
        )
        provider_parser.add_argument(
            "--no-docs", action="store_true", help="Skip documentation generation"
        )

        # Resource generation
        resource_parser = generate_subparsers.add_parser(
            "resource", help="Generate individual resource code"
        )
        resource_parser.add_argument(
            "resource_name", help="Name of the resource to generate"
        )
        resource_parser.add_argument(
            "provider_type",
            choices=["aws", "gcp", "azure", "digitalocean", "cloudflare"],
            help="Provider type",
        )
        resource_parser.add_argument(
            "--output", "-o", required=True, help="Output file for generated code"
        )
        resource_parser.add_argument(
            "--type",
            choices=[
                "compute",
                "storage",
                "network",
                "database",
                "security",
                "monitoring",
            ],
            default="compute",
            help="Resource type",
        )
        resource_parser.add_argument(
            "--fields", help="JSON file with field definitions"
        )
        resource_parser.add_argument(
            "--api-endpoint", help="API endpoint for the resource"
        )

        # Schema inspection
        inspect_parser = generate_subparsers.add_parser(
            "inspect", help="Inspect API schemas and specifications"
        )
        inspect_parser.add_argument("schema_file", help="Schema file to inspect")
        inspect_parser.add_argument(
            "--type",
            choices=["openapi", "terraform"],
            required=True,
            help="Schema type",
        )
        inspect_parser.add_argument(
            "--output-resources", help="Output discovered resources to JSON file"
        )

        # Template management
        template_parser = generate_subparsers.add_parser(
            "template", help="Manage generation templates"
        )
        template_subparsers = template_parser.add_subparsers(
            dest="template_action", help="Template actions"
        )

        # List templates
        template_subparsers.add_parser("list", help="List available templates")

        # Create template
        create_template_parser = template_subparsers.add_parser(
            "create", help="Create new template"
        )
        create_template_parser.add_argument("name", help="Template name")
        create_template_parser.add_argument(
            "--output", required=True, help="Output directory for template"
        )

    def execute(self, args: Namespace, config: "CLIConfig", console: "Console") -> int:
        """Execute generate command"""
        try:
            if not hasattr(args, "generate_action") or args.generate_action is None:
                console.error(
                    "No generate action specified. Use --help for available actions."
                )
                return 1

            if args.generate_action == "provider":
                return self._generate_provider(args, console)
            elif args.generate_action == "resource":
                return self._generate_resource(args, console)
            elif args.generate_action == "inspect":
                return self._inspect_schema(args, console)
            elif args.generate_action == "template":
                return self._manage_template(args, console)
            else:
                console.error(f"Unknown generate action: {args.generate_action}")
                return 1

        except Exception as e:
            console.error(f"Generate command failed: {str(e)}")
            return 1

    def _generate_provider(self, args: Namespace, console: "Console") -> int:
        """Generate provider code"""
        console.info(f"🚀 Generating {args.provider_type} provider...")

        # Create output directory
        output_path = Path(args.output)
        output_path.mkdir(parents=True, exist_ok=True)

        # Create configuration
        config = GenerationConfig(
            provider_type=ProviderType(args.provider_type),
            output_directory=str(output_path),
            template_directory=args.template_dir or "templates",
            generate_async=not args.no_async,
            generate_tests=not args.no_tests,
            generate_docs=not args.no_docs,
        )

        # Create generator
        generator = ProviderGenerator(config)

        # Load resources from various sources
        if args.openapi:
            console.info(f"📄 Loading resources from OpenAPI spec: {args.openapi}")
            generator.load_from_openapi(args.openapi)
        elif args.terraform:
            console.info(
                f"📄 Loading resources from Terraform schema: {args.terraform}"
            )
            generator.load_from_terraform(args.terraform)
        elif args.resources:
            console.info(f"📄 Loading resources from JSON file: {args.resources}")
            self._load_resources_from_json(generator, args.resources)
        else:
            # Add default resources for common providers
            console.info("📄 Adding default resources...")
            self._add_default_resources(generator, args.provider_type)

        console.info(f"📦 Found {len(generator.resources)} resources to generate")

        # Generate code
        console.info("🔨 Generating provider code...")
        generator.write_to_files()

        console.print(f"✅ Provider generated successfully in {output_path}")
        console.print(f"Generated files:")
        for file_path in output_path.glob("*.py"):
            console.print(f"  - {file_path.name}")

        return 0

    def _generate_resource(self, args: Namespace, console: "Console") -> int:
        """Generate individual resource code"""
        console.info(f"🚀 Generating {args.resource_name} resource...")

        # Create resource definition
        resource_type = ResourceType(args.type)
        provider_type = ProviderType(args.provider_type)

        # Load fields
        fields = []
        if args.fields:
            with open(args.fields, "r") as f:
                field_data = json.load(f)
                fields = [ResourceField(**field) for field in field_data]
        else:
            # Add default fields
            fields = self._get_default_fields(resource_type)

        resource = ResourceDefinition(
            name=args.resource_name,
            type=resource_type,
            provider=provider_type,
            description=f"Generated {args.resource_name} resource",
            fields=fields,
            api_endpoint=args.api_endpoint or f"/{args.resource_name.lower()}s",
        )

        # Create generator
        config = GenerationConfig(
            provider_type=provider_type, output_directory=str(Path(args.output).parent)
        )
        generator = ProviderGenerator(config)

        # Generate resource code
        resource_code = generator.generate_resource(resource)

        # Write to file
        with open(args.output, "w") as f:
            f.write(resource_code)

        console.print(f"✅ Resource generated successfully: {args.output}")
        return 0

    def _inspect_schema(self, args: Namespace, console: "Console") -> int:
        """Inspect API schema or specification"""
        console.info(f"🔍 Inspecting {args.type} schema: {args.schema_file}")

        # Create temporary generator for inspection
        config = GenerationConfig(
            provider_type=ProviderType.OPENAPI, output_directory="/tmp"
        )
        generator = ProviderGenerator(config)

        # Load schema
        if args.type == "openapi":
            generator.load_from_openapi(args.schema_file)
        elif args.type == "terraform":
            generator.load_from_terraform(args.schema_file)

        # Display discovered resources
        console.print(f"📊 Discovered {len(generator.resources)} resources:")

        for resource in generator.resources:
            console.print(f"🔹 {resource.name} ({resource.type.value})")
            console.print(f"   Description: {resource.description}")
            console.print(f"   Fields: {len(resource.fields)}")

            if resource.api_endpoint:
                console.print(f"   API Endpoint: {resource.api_endpoint}")

            if resource.terraform_resource_type:
                console.print(f"   Terraform Type: {resource.terraform_resource_type}")

        # Save to file if requested
        if args.output_resources:
            resource_data = []
            for resource in generator.resources:
                resource_dict = {
                    "name": resource.name,
                    "type": resource.type.value,
                    "provider": resource.provider.value,
                    "description": resource.description,
                    "fields": [
                        {
                            "name": field.name,
                            "type": field.type,
                            "description": field.description,
                            "required": field.required,
                            "default_value": field.default_value,
                            "constraints": field.constraints,
                        }
                        for field in resource.fields
                    ],
                    "api_endpoint": resource.api_endpoint,
                    "terraform_resource_type": resource.terraform_resource_type,
                }
                resource_data.append(resource_dict)

            with open(args.output_resources, "w") as f:
                json.dump(resource_data, f, indent=2)

            console.print(f"💾 Resource definitions saved to: {args.output_resources}")

        return 0

    def _manage_template(self, args: Namespace, console: "Console") -> int:
        """Manage generation templates"""
        if not hasattr(args, "template_action") or args.template_action is None:
            console.error(
                "No template action specified. Use --help for available actions."
            )
            return 1

        if args.template_action == "list":
            return self._list_templates(console)
        elif args.template_action == "create":
            return self._create_template(args, console)
        else:
            console.error(f"Unknown template action: {args.template_action}")
            return 1

    def _list_templates(self, console: "Console") -> int:
        """List available templates"""
        console.print("📋 Available Templates:")

        # Check for templates directory
        template_dir = Path("templates")
        if template_dir.exists():
            for template_file in template_dir.glob("*.j2"):
                console.print(f"  - {template_file.stem}")
        else:
            console.print("  No templates directory found")

        return 0

    def _create_template(self, args: Namespace, console: "Console") -> int:
        """Create new template"""
        console.info(f"🎨 Creating template: {args.name}")

        output_path = Path(args.output)
        output_path.mkdir(parents=True, exist_ok=True)

        # Create basic template
        template_content = '''"""
{{ name|title }} Template
Generated on {{ generation_date }}
"""

# Template variables available:
# - name: Template name
# - generation_date: Generation timestamp
# - provider_name: Provider name
# - resources: List of resource definitions
# - config: Generation configuration

# Add your template content here
'''

        template_file = output_path / f"{args.name}.j2"
        with open(template_file, "w") as f:
            f.write(template_content)

        console.print(f"✅ Template created: {template_file}")
        return 0

    def _load_resources_from_json(
        self, generator: ProviderGenerator, json_file: str
    ) -> None:
        """Load resources from JSON file"""
        with open(json_file, "r") as f:
            resource_data = json.load(f)

        for resource_dict in resource_data:
            fields = []
            for field_dict in resource_dict.get("fields", []):
                field = ResourceField(
                    name=field_dict["name"],
                    type=field_dict["type"],
                    description=field_dict.get("description", ""),
                    required=field_dict.get("required", False),
                    default_value=field_dict.get("default_value"),
                    constraints=field_dict.get("constraints", {}),
                )
                fields.append(field)

            resource = ResourceDefinition(
                name=resource_dict["name"],
                type=ResourceType(resource_dict["type"]),
                provider=ProviderType(resource_dict["provider"]),
                description=resource_dict.get("description", ""),
                fields=fields,
                api_endpoint=resource_dict.get("api_endpoint"),
                terraform_resource_type=resource_dict.get("terraform_resource_type"),
            )
            generator.add_resource(resource)

    def _add_default_resources(
        self, generator: ProviderGenerator, provider_type: str
    ) -> None:
        """Add default resources for common providers"""
        provider_enum = ProviderType(provider_type)

        if provider_type == "aws":
            # EC2 Instance
            generator.add_resource(
                ResourceDefinition(
                    name="Instance",
                    type=ResourceType.COMPUTE,
                    provider=provider_enum,
                    description="Amazon EC2 instance",
                    fields=[
                        ResourceField(
                            "instance_type", "str", "EC2 instance type", required=True
                        ),
                        ResourceField(
                            "ami", "str", "Amazon Machine Image ID", required=True
                        ),
                        ResourceField("key_name", "Optional[str]", "SSH key pair name"),
                        ResourceField(
                            "security_groups", "List[str]", "Security group IDs"
                        ),
                        ResourceField("subnet_id", "Optional[str]", "Subnet ID"),
                        ResourceField("user_data", "Optional[str]", "User data script"),
                        ResourceField(
                            "tags",
                            "Dict[str, str]",
                            "Resource tags",
                            default_value="{}",
                        ),
                    ],
                    api_endpoint="/instances",
                )
            )

            # S3 Bucket
            generator.add_resource(
                ResourceDefinition(
                    name="Bucket",
                    type=ResourceType.STORAGE,
                    provider=provider_enum,
                    description="Amazon S3 bucket",
                    fields=[
                        ResourceField(
                            "bucket_name", "str", "S3 bucket name", required=True
                        ),
                        ResourceField("region", "str", "AWS region", required=True),
                        ResourceField(
                            "versioning",
                            "bool",
                            "Enable versioning",
                            default_value="False",
                        ),
                        ResourceField(
                            "encryption",
                            "bool",
                            "Enable encryption",
                            default_value="True",
                        ),
                        ResourceField(
                            "public_access",
                            "bool",
                            "Allow public access",
                            default_value="False",
                        ),
                    ],
                    api_endpoint="/buckets",
                )
            )

        elif provider_type == "gcp":
            # Compute Instance
            generator.add_resource(
                ResourceDefinition(
                    name="Instance",
                    type=ResourceType.COMPUTE,
                    provider=provider_enum,
                    description="Google Compute Engine instance",
                    fields=[
                        ResourceField("name", "str", "Instance name", required=True),
                        ResourceField(
                            "machine_type", "str", "Machine type", required=True
                        ),
                        ResourceField("zone", "str", "Zone", required=True),
                        ResourceField("image", "str", "Boot disk image", required=True),
                        ResourceField(
                            "network", "str", "Network", default_value="default"
                        ),
                        ResourceField(
                            "tags", "List[str]", "Network tags", default_value="[]"
                        ),
                    ],
                    api_endpoint="/compute/v1/projects/{project}/zones/{zone}/instances",
                )
            )

        elif provider_type == "digitalocean":
            # Droplet
            generator.add_resource(
                ResourceDefinition(
                    name="Droplet",
                    type=ResourceType.COMPUTE,
                    provider=provider_enum,
                    description="DigitalOcean Droplet",
                    fields=[
                        ResourceField("name", "str", "Droplet name", required=True),
                        ResourceField("size", "str", "Droplet size", required=True),
                        ResourceField("image", "str", "Droplet image", required=True),
                        ResourceField("region", "str", "Region", required=True),
                        ResourceField(
                            "ssh_keys",
                            "List[str]",
                            "SSH key fingerprints",
                            default_value="[]",
                        ),
                        ResourceField("vpc_uuid", "Optional[str]", "VPC UUID"),
                        ResourceField("tags", "List[str]", "Tags", default_value="[]"),
                    ],
                    api_endpoint="/v2/droplets",
                )
            )

    def _get_default_fields(self, resource_type: ResourceType) -> List[ResourceField]:
        """Get default fields for resource type"""
        common_fields = [
            ResourceField("name", "str", "Resource name", required=True),
            ResourceField(
                "tags", "Dict[str, str]", "Resource tags", default_value="{}"
            ),
        ]

        if resource_type == ResourceType.COMPUTE:
            common_fields.extend(
                [
                    ResourceField(
                        "instance_type", "str", "Instance type", required=True
                    ),
                    ResourceField("image", "str", "Image ID", required=True),
                    ResourceField("region", "str", "Region", required=True),
                ]
            )
        elif resource_type == ResourceType.STORAGE:
            common_fields.extend(
                [
                    ResourceField("size", "int", "Size in GB", required=True),
                    ResourceField("type", "str", "Storage type", required=True),
                ]
            )
        elif resource_type == ResourceType.NETWORK:
            common_fields.extend(
                [
                    ResourceField("cidr_block", "str", "CIDR block", required=True),
                    ResourceField("region", "str", "Region", required=True),
                ]
            )
        elif resource_type == ResourceType.DATABASE:
            common_fields.extend(
                [
                    ResourceField("engine", "str", "Database engine", required=True),
                    ResourceField("version", "str", "Engine version", required=True),
                    ResourceField(
                        "instance_class", "str", "Instance class", required=True
                    ),
                ]
            )

        return common_fields
