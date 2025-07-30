"""
Topology Visualizer for Infrastructure Dependencies

This module provides visualization capabilities for infrastructure dependency graphs,
supporting multiple output formats and interactive features.
"""

import json
import io
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field
from collections import Counter

try:
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from .graph import (
    DependencyGraph,
    NodeType,
    GraphDirection,
)


class OutputFormat(Enum):
    """Supported output formats for visualization"""

    SVG = "svg"
    PNG = "png"
    HTML = "html"
    JSON = "json"
    DOT = "dot"
    INTERACTIVE = "interactive"


class ColorScheme(Enum):
    """Color schemes for visualization"""

    DEFAULT = "default"
    COLORBLIND = "colorblind"
    DARK = "dark"
    LIGHT = "light"
    PROVIDER_BASED = "provider_based"


@dataclass
class VisualizationConfig:
    """Configuration for visualization rendering"""

    format: OutputFormat = OutputFormat.SVG
    width: int = 1200
    height: int = 800
    color_scheme: ColorScheme = ColorScheme.DEFAULT
    show_labels: bool = True
    show_drift_status: bool = True
    show_dependencies: bool = True
    show_provider_icons: bool = True
    font_size: int = 10
    node_spacing: float = 2.0
    edge_thickness: float = 1.0
    highlight_critical_path: bool = False
    group_by_provider: bool = False
    layout_direction: GraphDirection = GraphDirection.TOP_DOWN
    include_metadata: bool = True
    animation_enabled: bool = False
    theme: Dict[str, Any] = field(default_factory=dict)


class TopologyVisualizer:
    """
    Visualizes infrastructure dependency graphs in various formats

    This class takes a DependencyGraph and renders it using different
    visualization engines and output formats.
    """

    def __init__(self, config: Optional[VisualizationConfig] = None):
        """Initialize the visualizer with configuration"""
        self.config = config or VisualizationConfig()
        self._color_mappings = self._load_color_mappings()
        self._node_shapes = self._load_node_shapes()
        self._template_dir = Path(__file__).parent / "templates"
        self._config_dir = Path(__file__).parent / "config"

    def visualize(
        self,
        graph: DependencyGraph,
        output_path: Optional[Union[str, Path]] = None,
        config: Optional[VisualizationConfig] = None,
        **kwargs,
    ) -> str:
        """
        Visualize a dependency graph

        Args:
            graph: The dependency graph to visualize
            output_path: Optional path to save the visualization
            config: Optional configuration object
            **kwargs: Additional configuration overrides

        Returns:
            String content of the visualization (path if saved to file)
        """
        # Use provided config or default, then merge with overrides
        if config is not None:
            merged_config = self._merge_config(config.__dict__, kwargs)
        else:
            merged_config = self._merge_config(self.config.__dict__, kwargs)

        # Validate graph
        if not graph.nodes:
            raise ValueError("Cannot visualize empty graph")

        # Choose rendering method based on format
        if merged_config.format == OutputFormat.JSON:
            result = self._render_json(graph, merged_config)
        elif merged_config.format == OutputFormat.DOT:
            result = self._render_dot(graph, merged_config)
        elif merged_config.format == OutputFormat.HTML:
            result = self._render_html(graph, merged_config)
        elif merged_config.format == OutputFormat.INTERACTIVE:
            result = self._render_interactive(graph, merged_config)
        elif merged_config.format in [OutputFormat.SVG, OutputFormat.PNG]:
            if not MATPLOTLIB_AVAILABLE:
                raise ImportError("matplotlib required for SVG/PNG output")
            result = self._render_matplotlib(graph, merged_config)
        else:
            raise ValueError(f"Unsupported output format: {merged_config.format}")

        # Save to file if path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if merged_config.format == OutputFormat.PNG:
                # Handle binary PNG data
                with open(output_path, "wb") as f:
                    f.write(result)
            else:
                # Handle text formats
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(result)
            return str(output_path)

        return result

    def _merge_config(
        self, base_config: Dict[str, Any], overrides: Dict[str, Any]
    ) -> VisualizationConfig:
        """Merge configuration with overrides"""
        merged = {**base_config, **overrides}
        return VisualizationConfig(**merged)

    def _load_color_mappings(self) -> Dict[str, Dict[str, str]]:
        """Load color mappings from configuration file"""
        try:
            config_path = Path(__file__).parent / "config" / "color_schemes.json"
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Fallback to default colors if config file is missing or invalid
            return {
                ColorScheme.DEFAULT.value: {
                    NodeType.COMPUTE.value: "#4CAF50",
                    NodeType.NETWORK.value: "#2196F3",
                    NodeType.STORAGE.value: "#FF9800",
                    NodeType.DATABASE.value: "#9C27B0",
                    NodeType.SECURITY.value: "#F44336",
                    NodeType.LOADBALANCER.value: "#00BCD4",
                    NodeType.FUNCTION.value: "#FFEB3B",
                    NodeType.DNS.value: "#795548",
                    NodeType.MONITORING.value: "#607D8B",
                    NodeType.KUBERNETES.value: "#326CE5",
                    NodeType.CONTAINER.value: "#0db7ed",
                    NodeType.CICD.value: "#8BC34A",
                    NodeType.UNKNOWN.value: "#9E9E9E",
                }
            }

    def _load_node_shapes(self) -> Dict[str, str]:
        """Load node shapes from configuration file"""
        try:
            config_path = Path(__file__).parent / "config" / "node_shapes.json"
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Fallback to default shapes if config file is missing or invalid
            return {
                NodeType.COMPUTE.value: "box",
                NodeType.NETWORK.value: "diamond",
                NodeType.STORAGE.value: "cylinder",
                NodeType.DATABASE.value: "cylinder",
                NodeType.SECURITY.value: "shield",
                NodeType.LOADBALANCER.value: "ellipse",
                NodeType.FUNCTION.value: "hexagon",
                NodeType.DNS.value: "circle",
                NodeType.MONITORING.value: "octagon",
                NodeType.KUBERNETES.value: "box",
                NodeType.CONTAINER.value: "box",
                NodeType.CICD.value: "octagon",
                NodeType.UNKNOWN.value: "circle",
            }

    def _render_json(self, graph: DependencyGraph, config: VisualizationConfig) -> str:
        """Render graph as JSON"""
        graph_dict = graph.to_dict()

        # Add visualization metadata
        graph_dict["visualization"] = {
            "format": config.format.value,
            "config": {
                "width": config.width,
                "height": config.height,
                "color_scheme": config.color_scheme.value,
                "layout_direction": config.layout_direction.value,
            },
        }

        return json.dumps(graph_dict, indent=2, default=str)

    def _render_dot(self, graph: DependencyGraph, config: VisualizationConfig) -> str:
        """Render graph as DOT (Graphviz) format"""
        lines = ["digraph infrastructure {"]
        lines.append("    rankdir=TB;")
        lines.append("    node [shape=box, style=filled];")
        lines.append("    edge [dir=forward];")
        lines.append("")

        # Add nodes
        colors = self._color_mappings[config.color_scheme.value]
        for node in graph.nodes.values():
            color = colors.get(node.type.value, colors[NodeType.UNKNOWN.value])
            shape = self._node_shapes.get(node.type.value, "box")

            # Handle drifted nodes
            if node.is_drifted:
                color = "#FF5722"  # Red for drifted

            lines.append(f'    "{node.id}" [')
            lines.append(f'        label="{node.display_name}\\n({node.type.value})",')
            lines.append(f'        fillcolor="{color}",')
            lines.append(f'        shape="{shape}",')
            lines.append(f'        tooltip="{node.provider}: {node.name}"')
            lines.append("    ];")

        lines.append("")

        # Add edges
        for edge in graph.edges:
            style = "solid" if edge.is_critical else "dashed"
            color = "#333333"

            if edge.dependency_type == "explicit":
                color = "#2196F3"
            elif edge.dependency_type == "implicit":
                color = "#FF9800"

            lines.append(f'    "{edge.source_id}" -> "{edge.target_id}" [')
            lines.append(f'        style="{style}",')
            lines.append(f'        color="{color}",')
            lines.append(f'        label="{edge.dependency_type}"')
            lines.append("    ];")

        lines.append("}")
        return "\n".join(lines)

    def _render_html(self, graph: DependencyGraph, config: VisualizationConfig) -> str:
        """Render graph as interactive HTML"""
        # Load HTML template
        html_template = self._load_template("topology.html")

        # Load CSS and JS
        css_content = self._load_template("topology.css")
        js_content = self._load_template("topology.js")

        # Prepare data
        graph_data = json.dumps(graph.to_dict(), default=str)
        node_colors = json.dumps(
            self._color_mappings.get(
                config.color_scheme.value, self._color_mappings["default"]
            )
        )

        # Replace placeholders in template
        html_content = html_template.replace("{{width}}", str(config.width))
        html_content = html_content.replace("{{height}}", str(config.height))
        html_content = html_content.replace("{{graph_data}}", graph_data)
        html_content = html_content.replace("{{node_colors}}", node_colors)

        # Embed CSS and JS directly in the HTML for standalone file
        html_content = html_content.replace(
            '<link rel="stylesheet" href="topology.css">',
            f"<style>{css_content}</style>",
        )
        html_content = html_content.replace(
            '<script src="topology.js"></script>', f"<script>{js_content}</script>"
        )

        return html_content

    def _load_template(self, template_name: str) -> str:
        """Load template file content"""
        try:
            template_path = self._template_dir / template_name
            with open(template_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            # Fallback to minimal template if file is missing
            if template_name == "topology.html":
                return """<!DOCTYPE html>
<html>
<head>
    <title>Infrastructure Topology</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
</head>
<body>
    <div>
        <h1>Infrastructure Topology</h1>
        <svg id="topology" width="{{width}}" height="{{height}}"></svg>
    </div>
    <script>
        const graphData = {{graph_data}};
        console.log('Graph data:', graphData);
    </script>
</body>
</html>"""
            elif template_name == "topology.css":
                return "body { font-family: Arial, sans-serif; }"
            elif template_name == "topology.js":
                return "console.log('Topology visualization loaded');"
            else:
                return ""

    def _render_interactive(
        self, graph: DependencyGraph, config: VisualizationConfig
    ) -> str:
        """Render graph as interactive web component"""
        # This would generate a more advanced interactive visualization
        # For now, return the HTML version
        return self._render_html(graph, config)

    def _render_matplotlib(
        self, graph: DependencyGraph, config: VisualizationConfig
    ) -> Union[str, bytes]:
        """Render graph using matplotlib"""
        ax = plt.subplots(figsize=(config.width / 100, config.height / 100))

        # Setup colors
        colors = self._color_mappings[config.color_scheme.value]

        # Draw nodes
        for node in graph.nodes.values():
            if node.position:
                x, y = node.position
                color = colors.get(node.type.value, colors[NodeType.UNKNOWN.value])

                # Use different style for drifted nodes
                if node.is_drifted:
                    edge_color = "#FF5722"
                    linewidth = 3
                else:
                    edge_color = "#333333"
                    linewidth = 2

                # Draw node
                circle = plt.Circle(
                    (x, y), 20, color=color, ec=edge_color, linewidth=linewidth
                )
                ax.add_patch(circle)

                # Add label
                if config.show_labels:
                    ax.text(
                        x,
                        y - 30,
                        node.display_name,
                        ha="center",
                        va="top",
                        fontsize=config.font_size,
                        weight="bold",
                    )
                    ax.text(
                        x,
                        y - 45,
                        f"({node.type.value})",
                        ha="center",
                        va="top",
                        fontsize=config.font_size - 2,
                        style="italic",
                    )

        # Draw edges
        if config.show_dependencies:
            for edge in graph.edges:
                source = graph.get_node(edge.source_id)
                target = graph.get_node(edge.target_id)

                if source and target and source.position and target.position:
                    x1, y1 = source.position
                    x2, y2 = target.position

                    # Choose color based on dependency type
                    if edge.dependency_type == "explicit":
                        color = "#2196F3"
                    elif edge.dependency_type == "implicit":
                        color = "#FF9800"
                    else:
                        color = "#666666"

                    # Draw arrow
                    ax.annotate(
                        "",
                        xy=(x2, y2),
                        xytext=(x1, y1),
                        arrowprops=dict(
                            arrowstyle="->",
                            color=color,
                            lw=config.edge_thickness,
                            linestyle="solid" if edge.is_critical else "dashed",
                        ),
                    )

        # Setup axes
        ax.set_xlim(-100, config.width + 100)
        ax.set_ylim(-100, config.height + 100)
        ax.set_aspect("equal")
        ax.axis("off")

        # Add title
        plt.title(
            f"Infrastructure Topology ({len(graph.nodes)} resources, {len(graph.edges)} dependencies)",
            fontsize=16,
            weight="bold",
            pad=20,
        )

        # Add legend
        legend_elements = []
        for node_type, color in colors.items():
            if any(node.type.value == node_type for node in graph.nodes.values()):
                legend_elements.append(
                    plt.Line2D(
                        [0],
                        [0],
                        marker="o",
                        color="w",
                        markerfacecolor=color,
                        markersize=10,
                        label=node_type.title(),
                    )
                )

        if legend_elements:
            ax.legend(handles=legend_elements, loc="upper right", bbox_to_anchor=(1, 1))

        plt.tight_layout()

        # Return based on format
        if config.format == OutputFormat.PNG:
            # Return PNG bytes
            buffer = io.BytesIO()
            plt.savefig(buffer, format="png", dpi=300, bbox_inches="tight")
            buffer.seek(0)
            result = buffer.read()
            plt.close()
            return result
        else:
            # Return SVG string
            buffer = io.StringIO()
            plt.savefig(buffer, format="svg", bbox_inches="tight")
            buffer.seek(0)
            result = buffer.read()
            plt.close()
            return result

    def generate_report(self, graph: DependencyGraph) -> Dict[str, Any]:
        """Generate a comprehensive visualization report"""
        report = {
            "summary": {
                "total_nodes": len(graph.nodes),
                "total_edges": len(graph.edges),
                "drift_count": sum(1 for n in graph.nodes.values() if n.is_drifted),
                "providers": list(set(n.provider for n in graph.nodes.values())),
                "node_types": dict(Counter(n.type.value for n in graph.nodes.values())),
            },
            "analysis": {
                "circular_dependencies": graph.metadata.get(
                    "circular_dependencies", []
                ),
                "critical_path": self._find_critical_path(graph),
                "isolated_nodes": self._find_isolated_nodes(graph),
                "provider_distribution": self._analyze_provider_distribution(graph),
            },
            "recommendations": self._generate_recommendations(graph),
        }

        return report

    def _find_critical_path(self, graph: DependencyGraph) -> List[str]:
        """Find the critical path in the dependency graph"""
        # This is a simplified version - in practice, you'd use more sophisticated algorithms
        critical_nodes = []

        # Find nodes with the most dependencies
        dependency_counts = {}
        for edge in graph.edges:
            dependency_counts[edge.target_id] = (
                dependency_counts.get(edge.target_id, 0) + 1
            )

        # Sort by dependency count
        sorted_nodes = sorted(
            dependency_counts.items(), key=lambda x: x[1], reverse=True
        )
        critical_nodes = [node_id for node_id, count in sorted_nodes[:5]]  # Top 5

        return critical_nodes

    def _find_isolated_nodes(self, graph: DependencyGraph) -> List[str]:
        """Find nodes with no dependencies"""
        connected_nodes = set()
        for edge in graph.edges:
            connected_nodes.add(edge.source_id)
            connected_nodes.add(edge.target_id)

        isolated = []
        for node_id in graph.nodes:
            if node_id not in connected_nodes:
                isolated.append(node_id)

        return isolated

    def _analyze_provider_distribution(self, graph: DependencyGraph) -> Dict[str, int]:
        """Analyze distribution of resources across providers"""
        providers = [node.provider for node in graph.nodes.values()]
        return dict(Counter(providers))

    def _generate_recommendations(self, graph: DependencyGraph) -> List[str]:
        """Generate recommendations based on graph analysis"""
        recommendations = []

        # Check for circular dependencies
        if graph.metadata.get("circular_dependencies"):
            recommendations.append(
                "Circular dependencies detected - consider refactoring to break cycles"
            )

        # Check for drift
        drift_count = sum(1 for n in graph.nodes.values() if n.is_drifted)
        if drift_count > 0:
            recommendations.append(
                f"{drift_count} resources have drifted - consider applying infrastructure updates"
            )

        # Check for isolated resources
        isolated = self._find_isolated_nodes(graph)
        if isolated:
            recommendations.append(
                f"{len(isolated)} isolated resources found - verify if they're needed"
            )

        # Check provider distribution
        provider_dist = self._analyze_provider_distribution(graph)
        if len(provider_dist) > 3:
            recommendations.append(
                "Multiple cloud providers detected - consider consolidation for easier management"
            )

        return recommendations
