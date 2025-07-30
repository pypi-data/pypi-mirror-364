"""
HTTP Server - Main FastAPI server class that coordinates all components
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .middleware import MiddlewareManager
from .routes import (
    ResourceRoutes,
    OperationRoutes,
    StateRoutes,
    DashboardRoutes,
    WebSocketRoutes,
    RegistryRoutes,
)
from .models import OperationResponse
from .events import EventSender
from infradsl.core.nexus import NexusEngine
from infradsl.core.service.websocket_service import NexusWebSocketService

logger = logging.getLogger(__name__)


class NexusAPIServer:
    """
    FastAPI-based HTTP server for InfraDSL Nexus Engine

    Provides REST API endpoints for infrastructure resource management,
    state synchronization, drift detection, and real-time monitoring.
    """

    def __init__(
        self,
        nexus_engine: Optional[NexusEngine] = None,
        host: str = "0.0.0.0",
        port: int = 8000,
        auth_enabled: bool = True,
        rate_limit_enabled: bool = True,
        rate_limit_requests: int = 100,
        rate_limit_window: int = 60,
    ):
        """
        Initialize the Nexus API Server

        Args:
            nexus_engine: Existing NexusEngine instance (creates new if None)
            host: Host to bind the server to
            port: Port to bind the server to
            auth_enabled: Enable authentication middleware
            rate_limit_enabled: Enable rate limiting
            rate_limit_requests: Max requests per window
            rate_limit_window: Rate limit window in seconds
        """
        self.nexus_engine = nexus_engine or NexusEngine()
        self.host = host
        self.port = port

        # Component managers
        self.middleware_manager = MiddlewareManager(
            auth_enabled=auth_enabled,
            rate_limit_enabled=rate_limit_enabled,
            rate_limit_requests=rate_limit_requests,
            rate_limit_window=rate_limit_window,
        )

        # Create FastAPI app with lifespan manager
        self.app = FastAPI(
            title="InfraDSL Nexus API",
            description="Enterprise Infrastructure Management API",
            version="1.0.0",
            lifespan=self._create_lifespan(),
        )

        # Setup middleware
        self.middleware_manager.setup_middleware(self.app)

        # Track ongoing operations
        self.operations: Dict[str, OperationResponse] = {}

        # WebSocket service and event sender
        self.websocket_service = NexusWebSocketService()
        self.event_sender = EventSender(self.websocket_service)

        # Dashboard templates
        templates_dir = Path(__file__).parent.parent / "templates"
        self.templates = Jinja2Templates(directory=str(templates_dir))

        # Mount static files for dashboard CSS/JS
        self.app.mount(
            "/static", StaticFiles(directory=str(templates_dir)), name="static"
        )

        # Initialize route handlers
        self._setup_route_handlers()

        # Setup routes
        self._setup_routes()

    def _setup_route_handlers(self):
        """Initialize all route handler classes"""
        self.resource_routes = ResourceRoutes(
            self.nexus_engine, self.operations, self.event_sender
        )
        self.operation_routes = OperationRoutes(self.operations)
        self.state_routes = StateRoutes(self.nexus_engine)
        self.dashboard_routes = DashboardRoutes(
            self.templates, self.host, self.port
        )
        self.websocket_routes = WebSocketRoutes(self.websocket_service)
        self.registry_routes = RegistryRoutes(
            self.templates, self.host, self.port
        )

    def _setup_routes(self):
        """Setup all API routes"""
        # Get auth dependency
        auth_dependency = self.middleware_manager.get_auth_dependency()

        # Health check
        @self.app.get("/health", tags=["System"])
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc),
                "version": "1.0.0",
            }

        # Setup route groups
        self.resource_routes.setup_routes(self.app, auth_dependency)
        self.operation_routes.setup_routes(self.app, auth_dependency)
        self.state_routes.setup_routes(self.app, auth_dependency)
        self.dashboard_routes.setup_routes(self.app, auth_dependency)
        self.websocket_routes.setup_routes(self.app)
        self.registry_routes.setup_routes(self.app, auth_dependency)

    def _create_lifespan(self):
        """Create the lifespan context manager"""

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            """Lifespan context manager for startup/shutdown"""
            # Startup
            logger.info(f"Starting Nexus API Server on {self.host}:{self.port}")
            logger.info(
                f"Dashboard URL: http://{self.host}:{self.port}/dashboard"
            )
            await self._startup()
            yield
            # Shutdown
            logger.info("Shutting down Nexus API Server")
            await self._shutdown()

        return lifespan

    async def _startup(self):
        """Perform startup tasks"""
        # Initialize cache
        # await cache_manager.initialize()  # TODO: Implement cache manager

        # Initialize resource registry
        if hasattr(self.nexus_engine, "resource_registry"):
            logger.info("Resource registry initialized")

    async def _shutdown(self):
        """Perform shutdown tasks"""
        # Close cache connections
        # await cache_manager.close()  # TODO: Implement cache manager

        # Shutdown WebSocket connections
        await self.websocket_service.shutdown()

        # Cancel any pending operations
        for op_id, operation in self.operations.items():
            if operation.status == "IN_PROGRESS":
                operation.status = "CANCELLED"
                operation.error = "Server shutdown"
                operation.completed_at = datetime.now(timezone.utc)

    def run(self):
        """Run the API server"""
        uvicorn.run(self.app, host=self.host, port=self.port, log_level="info")


if __name__ == "__main__":
    # Example usage
    server = NexusAPIServer()
    server.run()