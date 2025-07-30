"""
Resource Routes - CRUD endpoints for infrastructure resources
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException, Depends, status

from ..models import (
    ResourceCreateRequest,
    ResourceUpdateRequest,
    ResourceResponse,
    OperationResponse,
)
from infradsl.core.nexus import NexusEngine
from infradsl.core.nexus.base_resource import BaseResource, ResourceState

logger = logging.getLogger(__name__)


class ResourceRoutes:
    """Handles resource CRUD operations"""
    
    def __init__(self, nexus_engine: NexusEngine, operations: dict, event_sender):
        self.nexus_engine = nexus_engine
        self.operations = operations
        self.event_sender = event_sender
    
    def setup_routes(self, app, auth_dependency):
        """Setup resource routes"""
        
        @app.post(
            "/api/resources",
            response_model=OperationResponse,
            status_code=status.HTTP_202_ACCEPTED,
            tags=["Resources"],
        )
        async def create_resource(
            request: ResourceCreateRequest, auth=Depends(auth_dependency)
        ):
            """Create a new infrastructure resource"""
            try:
                # Generate operation ID
                operation_id = f"op-{datetime.now(timezone.utc).timestamp()}"

                # Create operation record
                operation = OperationResponse(
                    operation_id=operation_id,
                    resource_id="pending",
                    action="CREATE",
                    status="IN_PROGRESS",
                    started_at=datetime.now(timezone.utc),
                    completed_at=datetime.now(timezone.utc),
                    error=None,
                )
                self.operations[operation_id] = operation

                # Execute resource creation asynchronously
                asyncio.create_task(self._create_resource_async(operation_id, request))

                return operation

            except Exception as e:
                logger.error(f"Error creating resource: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e),
                )

        @app.get(
            "/api/resources/{resource_id}",
            response_model=ResourceResponse,
            tags=["Resources"],
        )
        async def get_resource(resource_id: str, auth=Depends(auth_dependency)):
            """Get a specific resource by ID"""
            try:
                resource = self.nexus_engine.get_registry().get(resource_id)
                if not resource:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Resource {resource_id} not found",
                    )

                return self._resource_to_response(resource)

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting resource: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e),
                )

        @app.get(
            "/api/resources",
            response_model=List[ResourceResponse],
            tags=["Resources"],
        )
        async def list_resources(
            project: Optional[str] = None,
            environment: Optional[str] = None,
            provider: Optional[str] = None,
            resource_type: Optional[str] = None,
            auth=Depends(auth_dependency),
        ):
            """List all resources with optional filtering"""
            try:
                resources = []
                all_resources = self.nexus_engine.get_registry().list_all()

                for resource in all_resources:
                    # Apply filters
                    if project and resource.metadata.project != project:
                        continue
                    if (
                        environment
                        and resource.metadata.environment != environment
                    ):
                        continue
                    if (
                        provider
                        and getattr(resource, "provider", None) != provider
                    ):
                        continue
                    if (
                        resource_type
                        and resource.__class__.__name__ != resource_type
                    ):
                        continue

                    resources.append(self._resource_to_response(resource))

                return resources

            except Exception as e:
                logger.error(f"Error listing resources: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e),
                )

        @app.put(
            "/api/resources/{resource_id}",
            response_model=OperationResponse,
            status_code=status.HTTP_202_ACCEPTED,
            tags=["Resources"],
        )
        async def update_resource(
            resource_id: str,
            request: ResourceUpdateRequest,
            auth=Depends(auth_dependency),
        ):
            """Update an existing resource"""
            try:
                # Check if resource exists
                resource = self.nexus_engine.get_registry().get(resource_id)
                if not resource:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Resource {resource_id} not found",
                    )

                # Generate operation ID
                operation_id = f"op-{datetime.now(timezone.utc).timestamp()}"

                # Create operation record
                operation = OperationResponse(
                    operation_id=operation_id,
                    resource_id=resource_id,
                    action="UPDATE",
                    status="IN_PROGRESS",
                    started_at=datetime.now(timezone.utc),
                    completed_at=datetime.now(timezone.utc),
                    error=None,
                )
                self.operations[operation_id] = operation

                # Execute update asynchronously
                asyncio.create_task(
                    self._update_resource_async(operation_id, resource_id, request)
                )

                return operation

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error updating resource: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e),
                )

        @app.delete(
            "/api/resources/{resource_id}",
            response_model=OperationResponse,
            status_code=status.HTTP_202_ACCEPTED,
            tags=["Resources"],
        )
        async def delete_resource(resource_id: str, auth=Depends(auth_dependency)):
            """Delete a resource"""
            try:
                # Check if resource exists
                resource = self.nexus_engine.get_registry().get(resource_id)
                if not resource:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Resource {resource_id} not found",
                    )

                # Generate operation ID
                operation_id = f"op-{datetime.now(timezone.utc).timestamp()}"

                # Create operation record
                operation = OperationResponse(
                    operation_id=operation_id,
                    resource_id=resource_id,
                    action="DELETE",
                    status="IN_PROGRESS",
                    started_at=datetime.now(timezone.utc),
                    completed_at=None,
                    error=None,
                )
                self.operations[operation_id] = operation

                # Execute deletion asynchronously
                asyncio.create_task(
                    self._delete_resource_async(operation_id, resource_id)
                )

                return operation

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error deleting resource: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e),
                )
    
    async def _create_resource_async(
        self, operation_id: str, request: ResourceCreateRequest
    ):
        """Async resource creation handler"""
        operation = self.operations[operation_id]
        try:
            # Send operation started event
            await self.event_sender.send_operation_event(operation, "operation_started")

            # TODO: Implement actual resource creation using NexusEngine
            # This is a placeholder implementation
            await asyncio.sleep(2)  # Simulate work

            # Update operation status
            operation.status = "COMPLETED"
            operation.completed_at = datetime.now(timezone.utc)
            operation.resource_id = (
                f"res-{datetime.now(timezone.utc).timestamp()}"
            )

            # Send operation completed and resource created events
            await self.event_sender.send_operation_event(operation, "operation_completed")
            await self.event_sender.send_resource_event(
                operation.resource_id,
                request.name,
                "resource_created",
                {
                    "resource_type": request.type,
                    "provider": request.provider,
                    "spec": request.spec,
                    "metadata": request.metadata,
                },
            )

        except Exception as e:
            operation.status = "FAILED"
            operation.error = str(e)
            operation.completed_at = datetime.now(timezone.utc)
            logger.error(f"Failed to create resource: {e}")

            # Send operation failed event
            await self.event_sender.send_operation_event(operation, "operation_failed")

    async def _update_resource_async(
        self,
        operation_id: str,
        resource_id: str,
        request: ResourceUpdateRequest,
    ):
        """Async resource update handler"""
        operation = self.operations[operation_id]
        try:
            # Send operation started event
            await self.event_sender.send_operation_event(operation, "operation_started")

            # TODO: Implement actual resource update using NexusEngine
            await asyncio.sleep(2)  # Simulate work

            operation.status = "COMPLETED"
            operation.completed_at = datetime.now(timezone.utc)

            # Send operation completed and resource updated events
            await self.event_sender.send_operation_event(operation, "operation_completed")
            await self.event_sender.send_resource_event(
                resource_id,
                f"resource-{resource_id}",
                "resource_updated",
                {
                    "updated_spec": request.spec,
                    "updated_metadata": request.metadata,
                },
            )

        except Exception as e:
            operation.status = "FAILED"
            operation.error = str(e)
            operation.completed_at = datetime.now(timezone.utc)
            logger.error(f"Failed to update resource: {e}")

            # Send operation failed event
            await self.event_sender.send_operation_event(operation, "operation_failed")

    async def _delete_resource_async(self, operation_id: str, resource_id: str):
        """Async resource deletion handler"""
        operation = self.operations[operation_id]
        try:
            # Send operation started event
            await self.event_sender.send_operation_event(operation, "operation_started")

            # TODO: Implement actual resource deletion using NexusEngine
            await asyncio.sleep(2)  # Simulate work

            operation.status = "COMPLETED"
            operation.completed_at = datetime.now(timezone.utc)

            # Send operation completed and resource deleted events
            await self.event_sender.send_operation_event(operation, "operation_completed")
            await self.event_sender.send_resource_event(
                resource_id,
                f"resource-{resource_id}",
                "resource_deleted",
                {"deleted_at": datetime.now(timezone.utc).isoformat()},
            )

        except Exception as e:
            operation.status = "FAILED"
            operation.error = str(e)
            operation.completed_at = datetime.now(timezone.utc)
            logger.error(f"Failed to delete resource: {e}")

            # Send operation failed event
            await self.event_sender.send_operation_event(operation, "operation_failed")
    
    def _resource_to_response(self, resource: BaseResource) -> ResourceResponse:
        """Convert a BaseResource to ResourceResponse"""
        return ResourceResponse(
            id=resource.metadata.id,
            name=resource.metadata.name,
            type=resource.__class__.__name__,
            provider=getattr(resource, "provider", "unknown"),
            status={
                "state": resource.status.state.value,
                "message": getattr(resource, "status_message", ""),
                "cloud_id": getattr(resource, "cloud_id", None),
                "drift_detected": resource.status.state == ResourceState.DRIFTED,
            },
            spec=resource.to_dict().get("spec", {}),
            metadata={
                "project": resource.metadata.project,
                "environment": resource.metadata.environment,
                "labels": resource.metadata.labels,
                "annotations": resource.metadata.annotations,
            },
            dependencies=[dep.metadata.id for dep in resource._dependencies],
            created_at=resource.metadata.created_at or datetime.now(timezone.utc),
            updated_at=resource.metadata.updated_at or datetime.now(timezone.utc),
        )