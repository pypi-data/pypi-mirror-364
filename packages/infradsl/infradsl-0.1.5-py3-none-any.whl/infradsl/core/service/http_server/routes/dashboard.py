"""
Dashboard Routes - Endpoints for visualization and topology dashboard
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from fastapi import HTTPException, Depends, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..discovery import InfrastructureDiscovery
from infradsl.core.visualization.graph import DependencyGraphBuilder
from infradsl.core.visualization.visualizer import (
    TopologyVisualizer,
    VisualizationConfig,
    OutputFormat,
)

logger = logging.getLogger(__name__)


class DashboardRoutes:
    """Handles dashboard and visualization endpoints"""
    
    def __init__(self, templates: Jinja2Templates, host: str, port: int):
        self.templates = templates
        self.host = host
        self.port = port
        self.graph_builder = DependencyGraphBuilder()
        self.visualizer = TopologyVisualizer()
        self.discovery = InfrastructureDiscovery()
        
        # Discovery cache for performance
        self._discovery_cache = {}
        self._cache_timestamp = 0
        self._cache_duration = 60  # 60 seconds cache
        self._discovery_lock = asyncio.Lock()
    
    def setup_routes(self, app, auth_dependency):
        """Setup dashboard and visualization routes"""
        
        @app.get("/dashboard", response_class=HTMLResponse, tags=["Dashboard"])
        async def dashboard(request: Request, auth=Depends(auth_dependency)):
            """Interactive topology visualization dashboard"""
            try:
                # Load dashboard immediately with empty data - discovery happens via AJAX
                logger.info("Loading dashboard (fast mode)...")

                # Create empty graph for instant loading
                empty_graph = self.graph_builder.build_graph([])
                graph_data = empty_graph.to_dict()

                # Get color mappings
                color_mappings = self.visualizer._load_color_mappings()

                # Render dashboard template immediately
                return self.templates.TemplateResponse(
                    "dashboard.html",
                    {
                        "request": request,
                        "graph_data": json.dumps(graph_data, default=str),
                        "node_colors": json.dumps(
                            color_mappings.get("default", {})
                        ),
                        "title": "Infrastructure Topology Dashboard",
                        "websocket_url": f"ws://{request.client.host if request.client else 'localhost'}:{self.port}/ws/resources",
                    },
                )
            except Exception as e:
                logger.error(f"Error rendering dashboard: {e}")
                import traceback

                logger.error(f"Traceback: {traceback.format_exc()}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Dashboard error: {str(e)}",
                )

        @app.get("/api/visualization/graph", tags=["Visualization"])
        async def get_topology_graph(
            format: str = "json", auth=Depends(auth_dependency)
        ):
            """Get topology graph data in various formats (with caching for performance)"""
            try:
                # Use lock to prevent concurrent discovery requests
                async with self._discovery_lock:
                    # Check cache first to avoid slow discovery
                    current_time = time.time()
                    cache_age = current_time - self._cache_timestamp

                    if (
                        cache_age < self._cache_duration
                        and self._discovery_cache
                    ):
                        logger.info(
                            f"Using cached resource data (cache age: {cache_age:.1f}s)"
                        )
                        discovered_resources = self._discovery_cache
                    else:
                        # Discover real infrastructure resources from cloud providers
                        logger.info("Discovering fresh resource data...")
                        start_time = time.time()
                        discovered_resources = (
                            await self.discovery.discover_infrastructure_resources()
                        )
                        discovery_time = time.time() - start_time
                        logger.info(
                            f"Resource discovery took {discovery_time:.2f} seconds"
                        )

                        # Cache the results
                        self._discovery_cache = discovered_resources
                        self._cache_timestamp = current_time
                        logger.info(
                            f"Cached {len(discovered_resources)} resources for {self._cache_duration}s"
                        )

                # Convert discovered resources to BaseResource format for the graph builder
                base_resources = self.discovery.convert_to_base_resources(
                    discovered_resources
                )

                # Build dependency graph
                graph = self.graph_builder.build_graph(base_resources)

                if format == "json":
                    return graph.to_dict()
                elif format == "dot":
                    config = VisualizationConfig(format=OutputFormat.DOT)
                    return {"dot": self.visualizer._render_dot(graph, config)}
                elif format == "html":
                    config = VisualizationConfig(format=OutputFormat.HTML)
                    return {"html": self.visualizer._render_html(graph, config)}
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Unsupported format: {format}",
                    )
            except Exception as e:
                logger.error(f"Error generating topology graph: {e}")
                import traceback

                logger.error(f"Traceback: {traceback.format_exc()}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e),
                )

        @app.post("/api/cache/invalidate", tags=["Cache"])
        async def invalidate_cache(auth=Depends(auth_dependency)):
            """Invalidate the resource discovery cache"""
            self._discovery_cache = {}
            self._cache_timestamp = 0
            logger.info("Discovery cache invalidated")
            return {
                "status": "cache_invalidated",
                "timestamp": datetime.now(timezone.utc),
            }