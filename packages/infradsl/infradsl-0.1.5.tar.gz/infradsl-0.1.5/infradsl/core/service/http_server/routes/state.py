"""
State Routes - Endpoints for state management and drift checking
"""

import logging
from datetime import datetime, timezone
from fastapi import HTTPException, Depends, status

from infradsl.core.nexus import NexusEngine

logger = logging.getLogger(__name__)


class StateRoutes:
    """Handles state management operations"""
    
    def __init__(self, nexus_engine: NexusEngine):
        self.nexus_engine = nexus_engine
    
    def setup_routes(self, app, auth_dependency):
        """Setup state management routes"""
        
        @app.get("/api/state/drift", tags=["State"])
        async def check_drift(auth=Depends(auth_dependency)):
            """Check drift for all resources"""
            try:
                drift_results = []
                resources = self.nexus_engine.get_registry().list_all()

                for resource in resources:
                    if hasattr(resource, "check_drift"):
                        drift_detected = resource.check_drift()
                        drift_results.append(
                            {
                                "resource_id": resource.metadata.id,
                                "resource_name": resource.metadata.name,
                                "drift_detected": drift_detected,
                                "state": resource.status.state.value,
                            }
                        )

                return {
                    "total_resources": len(resources),
                    "drifted_resources": sum(
                        1 for r in drift_results if r["drift_detected"]
                    ),
                    "results": drift_results,
                }

            except Exception as e:
                logger.error(f"Error checking drift: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e),
                )