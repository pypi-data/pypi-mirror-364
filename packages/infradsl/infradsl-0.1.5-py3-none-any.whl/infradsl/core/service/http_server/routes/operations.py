"""
Operation Routes - Endpoints for tracking operation status
"""

import logging
from fastapi import HTTPException, Depends, status

from ..models import OperationResponse

logger = logging.getLogger(__name__)


class OperationRoutes:
    """Handles operation status tracking"""
    
    def __init__(self, operations: dict):
        self.operations = operations
    
    def setup_routes(self, app, auth_dependency):
        """Setup operation routes"""
        
        @app.get(
            "/api/operations/{operation_id}",
            response_model=OperationResponse,
            tags=["Operations"],
        )
        async def get_operation_status(
            operation_id: str, auth=Depends(auth_dependency)
        ):
            """Get operation status"""
            if operation_id not in self.operations:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Operation {operation_id} not found",
                )

            return self.operations[operation_id]