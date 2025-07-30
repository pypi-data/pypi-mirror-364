from typing import List, Any
from ...core.templates.base import BaseTemplate, TemplateMetadata, TemplateContext
from ...notifications import notify_discord


class HelloWorldCloudRunTemplate(BaseTemplate):
    """
    Hello World CloudRun Template

    A simple template for deploying a "Hello World" application to Google Cloud Run with:
    - Pre-built container image from Artifact Registry
    - Configurable scaling (min/max instances)
    - Environment variables support
    - Unauthenticated access by default
    - Optional Discord notifications
    - Production-ready defaults with .production()

    Perfect for getting started with serverless containers on Google Cloud.
    """

    def _create_metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            name="HelloWorldCloudRun",
            version="1.0.0",
            description="Simple Hello World application deployed to Google Cloud Run",
            author="InfraDSL Team",
            category="serverless",
            tags=["cloudrun", "serverless", "hello-world", "gcp", "containerized"],
            providers=["gcp"],
            parameters_schema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "GCP project ID"},
                    "region": {
                        "type": "string",
                        "default": "europe-north1",
                        "description": "GCP region for deployment",
                    },
                    "repository_name": {
                        "type": "string",
                        "default": "infradsl-apps",
                        "description": "Artifact Registry repository name",
                    },
                    "image_name": {
                        "type": "string",
                        "default": "helloworld-service",
                        "description": "Container image name",
                    },
                    "image_tag": {
                        "type": "string",
                        "default": "latest",
                        "description": "Container image tag",
                    },
                    "min_instances": {
                        "type": "integer",
                        "default": 0,
                        "description": "Minimum number of instances (0 = scale to zero)",
                    },
                    "max_instances": {
                        "type": "integer",
                        "default": 10,
                        "description": "Maximum number of instances",
                    },
                    "environment_variables": {
                        "type": "object",
                        "default": {"SERVICE_NAME": "helloworld", "VERSION": "1.0.0"},
                        "description": "Environment variables for the container",
                    },
                    "allow_unauthenticated": {
                        "type": "boolean",
                        "default": True,
                        "description": "Allow unauthenticated requests",
                    },
                    "discord_webhook": {
                        "type": "string",
                        "description": "Discord webhook URL for notifications (optional)",
                    },
                },
                "required": ["project_id"],
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "service_url": {"type": "string"},
                    "service_name": {"type": "string"},
                    "region": {"type": "string"},
                },
            },
            examples=[
                {
                    "name": "Basic Hello World",
                    "description": "Deploy a simple hello world service",
                    "code": """hello = Templates.HelloWorldCloudRun("my-hello-world").with_parameters(
    project_id="my-project-123"
).production()""",
                },
                {
                    "name": "With Discord Notifications",
                    "description": "Deploy with Discord notifications enabled",
                    "code": """hello = Templates.HelloWorldCloudRun("my-hello-world").with_parameters(
    project_id="my-project-123",
    min_instances=1,
    max_instances=5
).notify_discord("https://discord.com/api/webhooks/...").production()""",
                },
                {
                    "name": "Custom Configuration",
                    "description": "Deploy with custom image and environment",
                    "code": """hello = Templates.HelloWorldCloudRun("custom-hello").with_parameters(
    project_id="my-project-123",
    image_name="my-custom-hello",
    image_tag="v2.0.0",
    region="us-central1",
    environment_variables={"APP_ENV": "production", "DEBUG": "false"}
).production()""",
                },
            ],
        )

    def notify_discord(self, webhook_url: str) -> "HelloWorldCloudRunTemplate":
        """
        Enable Discord notifications for all infrastructure events (chainable)

        Args:
            webhook_url: Discord webhook URL

        Returns:
            Self for method chaining
        """
        self.context.parameters["discord_webhook"] = webhook_url
        return self

    def build(self, context: TemplateContext) -> List[Any]:
        """Build the Hello World CloudRun infrastructure"""
        from ...resources.compute.cloud_run import CloudRun

        # Setup Discord notifications if webhook is provided
        discord_webhook = context.parameters.get("discord_webhook")
        if discord_webhook:
            notify_discord(discord_webhook)

        # Get parameters with defaults
        project_id = context.parameters["project_id"]
        region = context.parameters.get("region", "europe-north1")
        repository_name = context.parameters.get("repository_name", "infradsl-apps")
        image_name = context.parameters.get("image_name", "helloworld-service")
        image_tag = context.parameters.get("image_tag", "latest")
        min_instances = context.parameters.get("min_instances", 0)
        max_instances = context.parameters.get("max_instances", 10)
        environment_variables = context.parameters.get(
            "environment_variables", {"SERVICE_NAME": "helloworld", "VERSION": "1.0.0"}
        )
        allow_unauthenticated = context.parameters.get("allow_unauthenticated", True)

        # Create the CloudRun service
        service = (
            CloudRun(context.name)
            .artifact_registry(
                project_id, region, repository_name, image_name, image_tag
            )
            .min_instances(min_instances)
            .max_instances(max_instances)
            .environment_variables(environment_variables)
            .region(region)
        )

        # Configure authentication
        if allow_unauthenticated:
            service = service.allow_unauthenticated()

        # Apply environment-specific configurations
        if context.environment == "production":
            service = service.production()
        elif context.environment == "staging":
            service = service.staging()
        else:
            service = service.development()

        # Set template outputs
        self.set_output("service_name", context.name)
        self.set_output("region", region)
        self.set_output(
            "service_url", f"https://{context.name}-{project_id}.a.run.app"
        )  # CloudRun URL pattern

        return [service]


# Convenience factory function for the dream API
class Templates:
    """Template registry with fluent API access"""

    @staticmethod
    def HelloWorldCloudRun(name: str) -> HelloWorldCloudRunTemplate:
        """
        Create a Hello World CloudRun template instance

        Usage:
            hello = Templates.HelloWorldCloudRun("my-hello-world")
                .with_parameters(project_id="my-project")
                .notify_discord("https://discord.com/...")
                .production()
        """
        return HelloWorldCloudRunTemplate(name)
