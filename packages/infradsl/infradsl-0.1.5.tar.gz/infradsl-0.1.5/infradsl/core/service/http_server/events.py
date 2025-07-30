"""
Event Sender - Utility for sending WebSocket events
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any

from ..websocket_service import WebSocketEvent, NexusWebSocketService

logger = logging.getLogger(__name__)


class EventSender:
    """Handles sending WebSocket events for server operations"""
    
    def __init__(self, websocket_service: NexusWebSocketService):
        self.websocket_service = websocket_service
    
    async def send_event(self, event):
        """Send an event to WebSocket clients"""
        await self.websocket_service.send_event(event)

    async def send_operation_event(self, operation, event_type: str):
        """Send an operation-related event"""
        event = WebSocketEvent(
            event_id=f"evt-{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            operation_id=operation.operation_id,
            resource_id=operation.resource_id,
            resource_name=getattr(
                operation, "resource_name", f"resource-{operation.resource_id}"
            ),
            payload={
                "operation": operation.model_dump(),
                "status": operation.status,
            },
            project=getattr(operation, "project", None),
            environment=getattr(operation, "environment", None),
        )
        await self.send_event(event)

    async def send_resource_event(
        self,
        resource_id: str,
        resource_name: str,
        event_type: str,
        payload: Dict[str, Any],
    ):
        """Send a resource-related event"""
        event = WebSocketEvent(
            event_id=f"evt-{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            resource_id=resource_id,
            resource_name=resource_name,
            payload=payload,
            operation_id=None,
            project=None,
            environment=None,
        )
        await self.send_event(event)