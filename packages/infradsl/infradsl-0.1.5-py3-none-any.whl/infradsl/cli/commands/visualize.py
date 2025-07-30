"""
Visualization CLI Command - Generate infrastructure topology diagrams

This module provides the CLI command for generating infrastructure
topology visualizations in various formats.
"""

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import TYPE_CHECKING

from .base import BaseCommand

if TYPE_CHECKING:
    from ..utils.output import Console
    from ..utils.config import CLIConfig


class VisualizeCommand(BaseCommand):
    """Generate infrastructure topology visualizations"""

    @property
    def name(self) -> str:
        return "visualize"

    @property
    def description(self) -> str:
        return "Generate infrastructure topology diagrams and visualizations"

    def register(self, subparsers) -> None:
        """Register command arguments"""
        parser = subparsers.add_parser(
            self.name,
            help=self.description,
            description="Generate infrastructure topology diagrams in various formats",
        )

        # Output configuration
        parser.add_argument(
            "-o", "--output",
            help="Output file path (default: topology.<format>)"
        )
        parser.add_argument(
            "-f", "--format",
            choices=["svg", "png", "html", "json", "dot"],
            default="svg",
            help="Output format (default: svg)"
        )

        # Visualization options
        parser.add_argument(
            "--width",
            type=int,
            default=1200,
            help="Width of the visualization in pixels (default: 1200)"
        )
        parser.add_argument(
            "--height",
            type=int,
            default=800,
            help="Height of the visualization in pixels (default: 800)"
        )
        parser.add_argument(
            "--color-scheme",
            choices=["default", "colorblind", "dark", "light", "provider_based"],
            default="default",
            help="Color scheme for visualization (default: default)"
        )
        
        # Content options
        parser.add_argument(
            "--no-labels",
            action="store_true",
            help="Hide resource labels"
        )
        parser.add_argument(
            "--no-drift",
            action="store_true",
            help="Hide drift status indicators"
        )
        parser.add_argument(
            "--no-dependencies",
            action="store_true",
            help="Hide dependency lines"
        )
        parser.add_argument(
            "--no-provider-icons",
            action="store_true",
            help="Hide provider icons"
        )
        
        # Layout options
        parser.add_argument(
            "--direction",
            choices=["TB", "BT", "LR", "RL"],
            default="TB",
            help="Layout direction: TB (top-bottom), BT (bottom-top), LR (left-right), RL (right-left)"
        )
        parser.add_argument(
            "--group-by-provider",
            action="store_true",
            help="Group resources by provider"
        )
        parser.add_argument(
            "--highlight-critical",
            action="store_true",
            help="Highlight critical path in the dependency graph"
        )
        
        # Filtering options
        parser.add_argument(
            "--project",
            help="Filter by project"
        )
        parser.add_argument(
            "--environment",
            help="Filter by environment"
        )
        parser.add_argument(
            "--provider",
            help="Filter by provider"
        )
        parser.add_argument(
            "--resource-type",
            help="Filter by resource type"
        )
        
        # Advanced options
        parser.add_argument(
            "--theme",
            help="Custom theme JSON file path"
        )
        parser.add_argument(
            "--no-metadata",
            action="store_true",
            help="Exclude metadata from output"
        )
        parser.add_argument(
            "--font-size",
            type=int,
            default=10,
            help="Font size for labels (default: 10)"
        )
        parser.add_argument(
            "--node-spacing",
            type=float,
            default=2.0,
            help="Spacing between nodes (default: 2.0)"
        )
        parser.add_argument(
            "--edge-thickness",
            type=float,
            default=1.0,
            help="Thickness of dependency lines (default: 1.0)"
        )
        
        # Server mode
        parser.add_argument(
            "--server",
            action="store_true",
            help="Start interactive visualization server (opens in browser)"
        )
        parser.add_argument(
            "--server-port",
            type=int,
            default=8080,
            help="Port for visualization server (default: 8080)"
        )

        self.add_common_arguments(parser)

    def execute(self, args: Namespace, config: "CLIConfig", console: "Console") -> int:
        """Execute the visualize command"""
        try:
            # Import required modules
            from infradsl.core.nexus import NexusEngine
            from infradsl.core.visualization.graph import DependencyGraphBuilder, GraphDirection
            from infradsl.core.visualization.visualizer import (
                TopologyVisualizer,
                VisualizationConfig,
                OutputFormat,
                ColorScheme,
            )
            from infradsl.core.state.engine import StateEngine
            from infradsl.core.interfaces.provider import ProviderConfig, ProviderType
            import os
            from dotenv import load_dotenv
            
            # Load environment variables
            load_dotenv()
            
            console.info("🎨 Generating infrastructure topology visualization...")
            
            # Create NexusEngine and discover resources
            nexus_engine = NexusEngine()
            
            # Use StateEngine to discover resources from cloud providers
            engine = StateEngine(storage_backend="file")
            
            # Register available providers
            providers_registered = 0
            
            # Try to register DigitalOcean provider
            try:
                from infradsl.providers.digitalocean import DigitalOceanProvider
                
                token = os.getenv("DIGITALOCEAN_TOKEN")
                if token:
                    config_do = ProviderConfig(
                        type=ProviderType.DIGITAL_OCEAN,
                        credentials={"token": token},
                        region="nyc1",
                    )
                    provider = DigitalOceanProvider(config=config_do)
                    engine.register_provider("digitalocean", provider)
                    providers_registered += 1
                    console.debug("Registered DigitalOcean provider")
            except Exception as e:
                console.debug(f"Could not register DigitalOcean provider: {e}")
            
            # Try to register GCP provider
            try:
                from infradsl.providers.gcp import GCPComputeProvider
                import json
                
                project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
                region = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
                
                if not project_id:
                    service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                    if service_account_path and os.path.exists(service_account_path):
                        with open(service_account_path) as f:
                            creds = json.load(f)
                        project_id = creds.get("project_id")
                
                if project_id:
                    config_gcp = ProviderConfig(
                        type=ProviderType.GCP, project=project_id, region=region
                    )
                    provider = GCPComputeProvider(config=config_gcp)
                    engine.register_provider("gcp", provider)
                    providers_registered += 1
                    console.debug("Registered GCP provider")
            except Exception as e:
                console.debug(f"Could not register GCP provider: {e}")
            
            # Try to register AWS provider
            try:
                from infradsl.providers.aws_provider import AWSProvider
                
                config_aws = ProviderConfig(
                    type=ProviderType.AWS, region=os.getenv("AWS_REGION", "us-east-1")
                )
                provider = AWSProvider(config_aws)
                engine.register_provider("aws", provider)
                providers_registered += 1
                console.debug("Registered AWS provider")
            except Exception as e:
                console.debug(f"Could not register AWS provider: {e}")
            
            if providers_registered == 0:
                console.warning("⚠️  No cloud providers configured. Generating visualization from local state only.")
            else:
                console.info(f"🔍 Discovering resources from {providers_registered} provider(s)...")
                # Discover resources
                discovered_resources = engine.discover_all_resources(
                    update_storage=True,
                    timeout=10,  # 10 seconds timeout
                )
                console.info(f"✅ Discovered {len(discovered_resources)} resources")
            
            # Convert discovered resources to BaseResource format
            base_resources = self._convert_to_base_resources(discovered_resources if providers_registered > 0 else {})
            
            # Apply filters if specified
            if args.project:
                base_resources = [r for r in base_resources if r.metadata.project == args.project]
            if args.environment:
                base_resources = [r for r in base_resources if r.metadata.environment == args.environment]
            if args.provider:
                base_resources = [r for r in base_resources if getattr(r, 'provider', '') == args.provider]
            if args.resource_type:
                base_resources = [r for r in base_resources if r.__class__.__name__ == args.resource_type]
            
            console.info(f"📊 Building dependency graph for {len(base_resources)} resources...")
            
            # Build dependency graph
            graph_builder = DependencyGraphBuilder()
            graph = graph_builder.build_graph(base_resources)
            
            # Create visualization config
            viz_config = VisualizationConfig(
                format=OutputFormat(args.format),
                width=args.width,
                height=args.height,
                color_scheme=ColorScheme(args.color_scheme),
                show_labels=not args.no_labels,
                show_drift_status=not args.no_drift,
                show_dependencies=not args.no_dependencies,
                show_provider_icons=not args.no_provider_icons,
                font_size=args.font_size,
                node_spacing=args.node_spacing,
                edge_thickness=args.edge_thickness,
                highlight_critical_path=args.highlight_critical,
                group_by_provider=args.group_by_provider,
                layout_direction=GraphDirection(args.direction),
                include_metadata=not args.no_metadata,
            )
            
            # Load custom theme if specified
            if args.theme:
                try:
                    import json
                    with open(args.theme, 'r') as f:
                        viz_config.theme = json.load(f)
                except Exception as e:
                    console.warning(f"⚠️  Failed to load theme file: {e}")
            
            # Handle server mode
            if args.server:
                console.info(f"🌐 Starting visualization server on port {args.server_port}...")
                return self._start_visualization_server(
                    graph, viz_config, args.server_port, console
                )
            
            # Generate visualization
            visualizer = TopologyVisualizer(viz_config)
            
            # Determine output path
            output_path = args.output or f"topology.{args.format}"
            
            console.info(f"🎨 Rendering {args.format.upper()} visualization...")
            
            # Visualize and save
            result = visualizer.visualize(graph, output_path=output_path)
            
            console.success(f"✅ Visualization saved to: {output_path}")
            
            # Print graph statistics
            stats = graph.get_statistics()
            console.info(f"\n📊 Graph Statistics:")
            console.info(f"   • Total nodes: {stats['total_nodes']}")
            console.info(f"   • Total edges: {stats['total_edges']}")
            console.info(f"   • Providers: {', '.join(stats['providers'])}")
            console.info(f"   • Resource types: {stats['node_types']}")
            
            if graph.has_cycles():
                console.warning(f"⚠️  Circular dependencies detected: {len(graph.get_cycles())} cycles")
            
            return 0
            
        except ImportError as e:
            console.error(f"❌ Missing dependency: {e}")
            console.info("💡 Install visualization dependencies with: pip install 'infradsl[viz]'")
            return 1
        except Exception as e:
            console.error(f"❌ Visualization failed: {e}")
            if console.verbosity >= 2:
                import traceback
                console.error(traceback.format_exc())
            return 1

    def _convert_to_base_resources(self, discovered_resources: dict) -> list:
        """Convert discovered resources to BaseResource format"""
        from infradsl.core.nexus.base_resource import (
            BaseResource,
            ResourceMetadata,
            ResourceStatus,
            ResourceState,
        )
        from datetime import datetime, timezone

        base_resources = []

        for resource_id, resource_data in discovered_resources.items():
            try:
                # Create metadata
                metadata = ResourceMetadata(
                    id=resource_data.get("id", resource_id),
                    name=resource_data.get("name", resource_id),
                    project=resource_data.get("project", "default"),
                    environment=resource_data.get("environment", "unknown"),
                    labels=resource_data.get("tags", []),
                    annotations={},
                    created_at=datetime.now(timezone.utc),
                )

                # Create status
                status = ResourceStatus(
                    state=(
                        ResourceState.ACTIVE
                        if resource_data.get("state") == "active"
                        else ResourceState.PENDING
                    ),
                    message=f"Discovered from {resource_data.get('provider', 'unknown')} provider",
                )

                # Create a simple BaseResource-like object
                class DiscoveredResource:
                    def __init__(self, resource_data, metadata, status):
                        self.metadata = metadata
                        self.status = status
                        self.id = metadata.id
                        self.name = metadata.name
                        self.provider = resource_data.get("provider", "unknown")
                        self._resource_type = resource_data.get("type", "VirtualMachine")
                        self._dependencies = []
                        self.tags = resource_data.get("tags", [])

                    def dict(self):
                        return {
                            "id": self.id,
                            "name": self.name,
                            "type": self._resource_type,
                            "provider": self.provider,
                            "state": self.status.state.value,
                            "metadata": {
                                "project": self.metadata.project,
                                "environment": self.metadata.environment,
                            },
                        }

                resource = DiscoveredResource(resource_data, metadata, status)
                base_resources.append(resource)

            except Exception as e:
                # Skip resources that can't be converted
                continue

        return base_resources

    def _start_visualization_server(
        self, graph, config, port: int, console: "Console"
    ) -> int:
        """Start an interactive visualization server"""
        try:
            import webbrowser
            from http.server import HTTPServer, SimpleHTTPRequestHandler
            import tempfile
            import os
            
            # Generate HTML visualization
            from infradsl.core.visualization.visualizer import TopologyVisualizer
            
            visualizer = TopologyVisualizer(config)
            
            # Create temporary directory
            with tempfile.TemporaryDirectory() as tmpdir:
                # Generate HTML file
                html_path = os.path.join(tmpdir, "index.html")
                config.format = OutputFormat.HTML
                visualizer.visualize(graph, output_path=html_path)
                
                # Change to temp directory
                os.chdir(tmpdir)
                
                # Start server
                server = HTTPServer(("localhost", port), SimpleHTTPRequestHandler)
                
                # Open browser
                url = f"http://localhost:{port}"
                console.info(f"🌐 Opening browser at: {url}")
                webbrowser.open(url)
                
                console.info("Press Ctrl+C to stop the server")
                
                # Serve forever
                try:
                    server.serve_forever()
                except KeyboardInterrupt:
                    console.info("\n🛑 Stopping visualization server...")
                    server.shutdown()
                    
            return 0
            
        except Exception as e:
            console.error(f"❌ Failed to start visualization server: {e}")
            return 1