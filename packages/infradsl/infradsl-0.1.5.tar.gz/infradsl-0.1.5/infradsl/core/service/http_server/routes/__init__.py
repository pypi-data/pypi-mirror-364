"""
HTTP Server Routes - Route handlers for the REST API endpoints
"""

from .resources import ResourceRoutes
from .operations import OperationRoutes
from .state import StateRoutes
from .dashboard import DashboardRoutes
from .websocket_handlers import WebSocketRoutes
from .registry import RegistryRoutes

__all__ = [
    "ResourceRoutes",
    "OperationRoutes", 
    "StateRoutes",
    "DashboardRoutes",
    "WebSocketRoutes",
    "RegistryRoutes",
]