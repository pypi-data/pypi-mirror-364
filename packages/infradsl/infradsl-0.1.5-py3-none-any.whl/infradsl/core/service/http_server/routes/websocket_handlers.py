"""
WebSocket Routes - WebSocket endpoint handlers for real-time communication
"""

import logging
from fastapi import WebSocket

from infradsl.core.service.websocket_service import (
    NexusWebSocketService,
    NexusWebSocketEndpoints,
)

logger = logging.getLogger(__name__)


class WebSocketRoutes:
    """Handles WebSocket endpoints"""
    
    def __init__(self, websocket_service: NexusWebSocketService):
        self.websocket_service = websocket_service
        self.websocket_endpoints = NexusWebSocketEndpoints(websocket_service)
    
    def setup_routes(self, app):
        """Setup WebSocket routes"""
        
        @app.websocket("/ws/events")
        async def websocket_events(websocket: WebSocket):
            """WebSocket endpoint for real-time event streaming"""
            await self.websocket_endpoints.events_endpoint(websocket)

        @app.websocket("/ws/operations/{operation_id}")
        async def websocket_operation_status(websocket: WebSocket, operation_id: str):
            """WebSocket endpoint for tracking specific operation status"""
            await self.websocket_endpoints.operation_endpoint(websocket, operation_id)

        @app.websocket("/ws/resources")
        async def websocket_resource_updates(websocket: WebSocket):
            """WebSocket endpoint for resource updates"""
            await self.websocket_endpoints.resource_endpoint(websocket)