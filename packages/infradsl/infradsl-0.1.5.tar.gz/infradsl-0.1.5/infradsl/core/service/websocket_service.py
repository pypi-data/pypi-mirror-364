"""
Nexus WebSocket Service - Extensible WebSocket service for InfraDSL

This module provides a dedicated WebSocket service for real-time event streaming,
separate from the main HTTP server to allow for better extensibility and maintenance.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class WebSocketEvent(BaseModel):
    """WebSocket event model"""

    event_id: str = Field(..., description="Unique event ID")
    event_type: str = Field(
        ..., description="Event type (resource_created, resource_updated, etc.)"
    )
    timestamp: datetime = Field(..., description="Event timestamp")
    resource_id: Optional[str] = Field(None, description="Related resource ID")
    resource_name: Optional[str] = Field(None, description="Related resource name")
    operation_id: Optional[str] = Field(None, description="Related operation ID")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event payload")
    project: Optional[str] = Field(None, description="Project context")
    environment: Optional[str] = Field(None, description="Environment context")


class WebSocketConnectionInfo(BaseModel):
    """Information about a WebSocket connection"""

    connection_id: str = Field(..., description="Unique connection ID")
    connected_at: datetime = Field(..., description="Connection timestamp")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    filters: Dict[str, Any] = Field(
        default_factory=dict, description="Connection filters"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Connection metadata"
    )


class NexusWebSocketService:
    """
    Extensible WebSocket service for real-time event streaming

    This service manages WebSocket connections, event broadcasting, and provides
    extensibility hooks for custom event handling and filtering.
    """

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_info: Dict[str, WebSocketConnectionInfo] = {}
        self.event_queue: asyncio.Queue[WebSocketEvent] = asyncio.Queue()
        self._background_task: Optional[asyncio.Task] = None
        self._shutdown = False

        # Extensibility hooks
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.connection_handlers: Dict[str, List[Callable]] = {}
        self.filter_validators: List[Callable] = []

        # Statistics
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "events_sent": 0,
            "events_queued": 0,
            "errors": 0,
        }

    async def connect(
        self,
        websocket: WebSocket,
        connection_id: str,
        filters: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Accept a WebSocket connection"""
        try:
            await websocket.accept()

            # Store connection
            self.active_connections[connection_id] = websocket
            self.connection_info[connection_id] = WebSocketConnectionInfo(
                connection_id=connection_id,
                connected_at=datetime.now(timezone.utc),
                last_activity=datetime.now(timezone.utc),
                filters=filters or {},
                metadata=metadata or {},
            )

            # Update statistics
            self.stats["total_connections"] += 1
            self.stats["active_connections"] = len(self.active_connections)

            # Start a background task if not already running
            if self._background_task is None or self._background_task.done():
                self._background_task = asyncio.create_task(self._event_broadcaster())

            # Trigger connection handlers
            await self._trigger_handlers("connection_established", connection_id)

            logger.info(f"WebSocket connection {connection_id} established")

        except Exception as e:
            logger.error(f"Error accepting WebSocket connection {connection_id}: {e}")
            self.stats["errors"] += 1
            raise

    def disconnect(self, connection_id: str):
        """Remove a WebSocket connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            del self.connection_info[connection_id]

            # Update statistics
            self.stats["active_connections"] = len(self.active_connections)

            # Trigger connection handlers
            asyncio.create_task(
                self._trigger_handlers("connection_closed", connection_id)
            )

            logger.info(f"WebSocket connection {connection_id} closed")

    async def send_event(self, event: WebSocketEvent):
        """Queue an event for broadcasting"""
        if self._shutdown:
            return

        await self.event_queue.put(event)
        self.stats["events_queued"] += 1

    async def send_direct_message(self, connection_id: str, message: Dict[str, Any]):
        """Send a direct message to a specific connection"""
        if connection_id not in self.active_connections:
            logger.warning(f"Connection {connection_id} not found for direct message")
            return False

        try:
            websocket = self.active_connections[connection_id]
            await websocket.send_text(json.dumps(message))

            # Update last activity
            if connection_id in self.connection_info:
                self.connection_info[connection_id].last_activity = datetime.now(
                    timezone.utc
                )

            return True

        except Exception as e:
            logger.error(f"Error sending direct message to {connection_id}: {e}")
            self.disconnect(connection_id)
            self.stats["errors"] += 1
            return False

    async def update_connection_filters(
        self, connection_id: str, filters: Dict[str, Any]
    ):
        """Update filters for a specific connection"""
        if connection_id not in self.connection_info:
            logger.warning(f"Connection {connection_id} not found for filter update")
            return False

        # Validate filters
        if not await self._validate_filters(filters):
            logger.warning(f"Invalid filters for connection {connection_id}")
            return False

        # Update filters
        self.connection_info[connection_id].filters = filters
        self.connection_info[connection_id].last_activity = datetime.now(timezone.utc)

        logger.info(f"Updated filters for connection {connection_id}")
        return True

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket service statistics"""
        return {
            **self.stats,
            "connections": [
                {
                    "id": conn_id,
                    "connected_at": info.connected_at.isoformat(),
                    "last_activity": info.last_activity.isoformat(),
                    "filters": info.filters,
                    "metadata": info.metadata,
                }
                for conn_id, info in self.connection_info.items()
            ],
        }

    def register_event_handler(self, event_type: str, handler: Callable):
        """Register a custom event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered event handler for {event_type}")

    def register_connection_handler(self, event_type: str, handler: Callable):
        """Register a custom connection handler"""
        if event_type not in self.connection_handlers:
            self.connection_handlers[event_type] = []
        self.connection_handlers[event_type].append(handler)
        logger.info(f"Registered connection handler for {event_type}")

    def register_filter_validator(self, validator: Callable):
        """Register a custom filter validator"""
        self.filter_validators.append(validator)
        logger.info("Registered filter validator")

    async def _event_broadcaster(self):
        """Background task to broadcast events to connected clients"""
        while not self._shutdown:
            try:
                event = await self.event_queue.get()
                await self._broadcast_event(event)

                # Trigger event handlers
                await self._trigger_handlers("event_broadcasted", event)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error broadcasting event: {e}")
                self.stats["errors"] += 1

    async def _broadcast_event(self, event: WebSocketEvent):
        """Broadcast an event to all matching connections"""
        if not self.active_connections:
            return

        # Find connections that match the event filters
        matching_connections = []

        for conn_id, websocket in self.active_connections.items():
            conn_info = self.connection_info.get(conn_id)
            if not conn_info:
                continue

            # Apply filters
            if self._event_matches_filters(event, conn_info.filters):
                matching_connections.append((conn_id, websocket, conn_info))

        # Send to matching connections
        if matching_connections:
            event_data = event.model_dump_json()
            disconnected_connections = []

            for conn_id, websocket, conn_info in matching_connections:
                try:
                    await websocket.send_text(event_data)

                    # Update last activity
                    conn_info.last_activity = datetime.now(timezone.utc)

                    self.stats["events_sent"] += 1

                except Exception as e:
                    logger.warning(f"Failed to send event to connection {conn_id}: {e}")
                    disconnected_connections.append(conn_id)
                    self.stats["errors"] += 1

            # Clean up disconnected connections
            for conn_id in disconnected_connections:
                self.disconnect(conn_id)

    def _event_matches_filters(
        self, event: WebSocketEvent, filters: Dict[str, Any]
    ) -> bool:
        """Check if an event matches the connection filters"""
        if not filters:
            return True

        # Filter by event types
        if "event_types" in filters:
            if event.event_type not in filters["event_types"]:
                return False

        # Filter by resource IDs
        if "resource_ids" in filters:
            if event.resource_id and event.resource_id not in filters["resource_ids"]:
                return False

        # Filter by operation IDs
        if "operation_ids" in filters:
            if (
                event.operation_id
                and event.operation_id not in filters["operation_ids"]
            ):
                return False

        # Filter by project
        if "project" in filters:
            if event.project != filters["project"]:
                return False

        # Filter by environment
        if "environment" in filters:
            if event.environment != filters["environment"]:
                return False

        # Custom filter logic can be added here
        return True

    async def _validate_filters(self, filters: Dict[str, Any]) -> bool:
        """Validate connection filters"""
        # Basic validation
        if not isinstance(filters, dict):
            return False

        # Check for valid filter keys
        valid_keys = {
            "event_types",
            "resource_ids",
            "operation_ids",
            "project",
            "environment",
        }
        for key in filters.keys():
            if key not in valid_keys:
                logger.warning(f"Invalid filter key: {key}")
                return False

        # Run custom validators
        for validator in self.filter_validators:
            try:
                if not await validator(filters):
                    return False
            except Exception as e:
                logger.error(f"Error in filter validator: {e}")
                return False

        return True

    async def _trigger_handlers(self, event_type: str, data: Any):
        """Trigger registered handlers for an event type"""
        handlers = []

        # Get event handlers
        if event_type in self.event_handlers:
            handlers.extend(self.event_handlers[event_type])

        # Get connection handlers
        if event_type in self.connection_handlers:
            handlers.extend(self.connection_handlers[event_type])

        # Execute handlers
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                logger.error(f"Error in handler for {event_type}: {e}")
                self.stats["errors"] += 1

    async def shutdown(self):
        """Shutdown the WebSocket service"""
        self._shutdown = True

        # Cancel a background task
        if self._background_task:
            self._background_task.cancel()
            try:
                await self._background_task
            except asyncio.CancelledError:
                pass

        # Close all connections
        for conn_id, websocket in self.active_connections.items():
            try:
                await websocket.close()
            except WebSocketDisconnect:
                pass

        self.active_connections.clear()
        self.connection_info.clear()

        # Update statistics
        self.stats["active_connections"] = 0

        logger.info("WebSocket service shut down")


class NexusWebSocketEndpoints:
    """
    WebSocket endpoint handlers for FastAPI integration

    This class provides pre-built WebSocket endpoint handlers that can be
    easily integrated into FastAPI applications.
    """

    def __init__(self, websocket_service: NexusWebSocketService):
        self.websocket_service = websocket_service

    async def events_endpoint(self, websocket: WebSocket):
        """WebSocket endpoint for general event streaming"""
        connection_id = f"conn-{uuid.uuid4().hex[:8]}"

        try:
            await self.websocket_service.connect(websocket, connection_id)

            # Send initial connection event
            await self.websocket_service.send_event(
                WebSocketEvent(
                    event_id=f"evt-{uuid.uuid4().hex[:8]}",
                    event_type="connection_established",
                    timestamp=datetime.now(timezone.utc),
                    payload={"connection_id": connection_id},
                    project=None,
                    environment=None,
                    resource_id=None,
                    resource_name=None,
                    operation_id=None,
                )
            )

            # Handle messages
            await self._handle_connection_messages(websocket, connection_id)

        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.error(f"Error in events endpoint: {e}")
        finally:
            self.websocket_service.disconnect(connection_id)

    async def operation_endpoint(self, websocket: WebSocket, operation_id: str):
        """WebSocket endpoint for operation-specific streaming"""
        connection_id = f"op-conn-{uuid.uuid4().hex[:8]}"

        try:
            # Set up filters for this operation
            filters = {
                "event_types": [
                    "operation_started",
                    "operation_completed",
                    "operation_failed",
                ],
                "operation_ids": [operation_id],
            }

            await self.websocket_service.connect(websocket, connection_id, filters)

            # Send initial status if available,
            # This would be integrated with the actual operation tracking

            # Handle messages
            await self._handle_connection_messages(websocket, connection_id)

        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.error(f"Error in operation endpoint: {e}")
        finally:
            self.websocket_service.disconnect(connection_id)

    async def resource_endpoint(self, websocket: WebSocket):
        """WebSocket endpoint for resource-specific streaming"""
        connection_id = f"res-conn-{uuid.uuid4().hex[:8]}"

        try:
            # Set up filters for resource events
            filters = {
                "event_types": [
                    "resource_created",
                    "resource_updated",
                    "resource_deleted",
                    "resource_drift_detected",
                ]
            }

            await self.websocket_service.connect(websocket, connection_id, filters)

            # Handle messages
            await self._handle_connection_messages(websocket, connection_id)

        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.error(f"Error in resource endpoint: {e}")
        finally:
            self.websocket_service.disconnect(connection_id)

    async def _handle_connection_messages(
        self, websocket: WebSocket, connection_id: str
    ):
        """Handle incoming WebSocket messages"""
        while True:
            try:
                message = await websocket.receive_text()
                data = json.loads(message)

                # Handle filter updates
                if "filters" in data:
                    success = await self.websocket_service.update_connection_filters(
                        connection_id, data["filters"]
                    )

                    # Send acknowledgment
                    await self.websocket_service.send_direct_message(
                        connection_id,
                        {
                            "type": "filter_update_response",
                            "success": success,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        },
                    )

                # Handle ping/pong
                elif data.get("type") == "ping":
                    await self.websocket_service.send_direct_message(
                        connection_id,
                        {
                            "type": "pong",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        },
                    )

                # Handle stats request
                elif data.get("type") == "stats":
                    stats = self.websocket_service.get_connection_stats()
                    await self.websocket_service.send_direct_message(
                        connection_id,
                        {
                            "type": "stats_response",
                            "stats": stats,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        },
                    )

                # Send general acknowledgment
                else:
                    await self.websocket_service.send_direct_message(
                        connection_id,
                        {
                            "type": "ack",
                            "message": "Message received",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        },
                    )

            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await self.websocket_service.send_direct_message(
                    connection_id,
                    {
                        "type": "error",
                        "message": "Invalid JSON format",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                )
            except Exception as e:
                logger.error(f"Error handling message for {connection_id}: {e}")
                await self.websocket_service.send_direct_message(
                    connection_id,
                    {
                        "type": "error",
                        "message": "Internal server error",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                )
                break
