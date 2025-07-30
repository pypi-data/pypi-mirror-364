# pyright: reportGeneralTypeIssues=false
# The above directive disabled 'Cannot find reference' and similar general type issues for this file.

# pyright: reportMissingImports=false, reportUndefinedVariable=false

"""
Nexus gRPC Service - High-performance gRPC service for InfraDSL

This module implements the gRPC service that provides high-performance
resource operations and streaming capabilities for InfraDSL.
"""

import asyncio
import grpc
import logging
from concurrent import futures
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, AsyncGenerator
import uuid

from google.protobuf import timestamp_pb2, struct_pb2, empty_pb2

from infradsl.proto import nexus_pb2, nexus_pb2_grpc
from infradsl.core.nexus import NexusEngine
from infradsl.core.nexus.base_resource import BaseResource, ResourceState

logger = logging.getLogger(__name__)


class NexusGRPCService(nexus_pb2_grpc.NexusServiceServicer):
    """
    gRPC service implementation for InfraDSL Nexus Engine

    Provides high-performance resource operations and real-time streaming
    capabilities for infrastructure management.
    """

    def __init__(self, nexus_engine: Optional[NexusEngine] = None):
        """
        Initialize the gRPC service

        Args:
            nexus_engine: NexusEngine instance for resource operations
        """
        self.nexus_engine = nexus_engine or NexusEngine()
        self.operations: Dict[str, nexus_pb2.OperationResponse] = {}  # type: ignore
        self.event_subscribers: Dict[str, List[Any]] = {}
        self.operation_subscribers: Dict[str, List[Any]] = {}
        self.resource_subscribers: Dict[str, List[Any]] = {}
        self._shutdown = False

    def _datetime_to_timestamp(self, dt: datetime) -> timestamp_pb2.Timestamp:  # type: ignore
        """Convert datetime to protobuf timestamp"""
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(dt)
        return timestamp

    def _timestamp_to_datetime(self, ts: timestamp_pb2.Timestamp) -> datetime:
        """Convert protobuf timestamp to datetime"""
        return ts.ToDatetime()

    def _resource_to_pb(self, resource: BaseResource) -> nexus_pb2.ResourceResponse:
        """Convert BaseResource to protobuf ResourceResponse"""
        # Convert spec to protobuf Struct
        spec_struct = struct_pb2.Struct()  # type: ignore
        spec_dict = resource.to_dict().get("spec", {})
        if spec_dict:
            spec_struct.update(spec_dict)

        # Convert metadata to protobuf Metadata
        metadata = nexus_pb2.Metadata(
            project=resource.metadata.project or "",
            environment=resource.metadata.environment or "",
            labels=resource.metadata.labels or {},
            annotations=resource.metadata.annotations or {},
        )  # type: ignore

        # Create resource status
        status = nexus_pb2.ResourceStatus(
            state=resource.state.value,
            message=getattr(resource, "status_message", ""),
            cloud_id=getattr(resource, "cloud_id", ""),
            drift_detected=resource.state == ResourceState.DRIFTED,
            last_synced=self._datetime_to_timestamp(resource.metadata.updated_at),
        )

        return nexus_pb2.ResourceResponse(
            id=resource.metadata.id,
            name=resource.name,
            type=resource.__class__.__name__,
            provider=getattr(resource, "provider", "unknown"),
            status=status,
            spec=spec_struct,
            metadata=metadata,
            dependencies=[dep.metadata.id for dep in resource.dependencies],
            created_at=self._datetime_to_timestamp(resource.metadata.created_at),
            updated_at=self._datetime_to_timestamp(resource.metadata.updated_at),
        )

    def _create_operation_response(
        self,
        operation_id: str,
        resource_id: str,
        action: str,
        status: str,
        started_at: datetime,
        completed_at: Optional[datetime] = None,
        error: Optional[str] = None,
    ) -> nexus_pb2.OperationResponse:
        """Create an OperationResponse protobuf message"""
        response = nexus_pb2.OperationResponse(
            operation_id=operation_id,
            resource_id=resource_id,
            action=action,
            status=status,
            started_at=self._datetime_to_timestamp(started_at),
        )

        if completed_at:
            response.completed_at.CopyFrom(self._datetime_to_timestamp(completed_at))

        if error:
            response.error = error

        return response

    async def CreateResource(
        self, request: nexus_pb2.CreateResourceRequest, context: grpc.ServicerContext
    ) -> nexus_pb2.OperationResponse:
        """Create a new infrastructure resource"""
        try:
            # Generate operation ID
            operation_id = f"op-{uuid.uuid4().hex[:8]}"

            # Create operation record
            operation = self._create_operation_response(
                operation_id=operation_id,
                resource_id="pending",
                action="CREATE",
                status="IN_PROGRESS",
                started_at=datetime.now(timezone.utc),
            )

            self.operations[operation_id] = operation

            # Execute resource creation asynchronously
            asyncio.create_task(self._create_resource_async(operation_id, request))

            return operation

        except Exception as e:
            logger.error(f"Error creating resource: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return nexus_pb2.OperationResponse()

    async def GetResource(
        self, request: nexus_pb2.GetResourceRequest, context: grpc.ServicerContext
    ) -> nexus_pb2.ResourceResponse:
        """Get a specific resource by ID"""
        try:
            resource = self.nexus_engine.resource_registry.get(request.id)

            if not resource:
                context.set_details(f"Resource {request.id} not found")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return nexus_pb2.ResourceResponse()

            return self._resource_to_pb(resource)

        except Exception as e:
            logger.error(f"Error getting resource: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return nexus_pb2.ResourceResponse()

    async def UpdateResource(
        self, request: nexus_pb2.UpdateResourceRequest, context: grpc.ServicerContext
    ) -> nexus_pb2.OperationResponse:
        """Update an existing resource"""
        try:
            # Check if resource exists
            resource = self.nexus_engine.resource_registry.get(request.id)
            if not resource:
                context.set_details(f"Resource {request.id} not found")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return nexus_pb2.OperationResponse()

            # Generate operation ID
            operation_id = f"op-{uuid.uuid4().hex[:8]}"

            # Create operation record
            operation = self._create_operation_response(
                operation_id=operation_id,
                resource_id=request.id,
                action="UPDATE",
                status="IN_PROGRESS",
                started_at=datetime.now(timezone.utc),
            )

            self.operations[operation_id] = operation

            # Execute update asynchronously
            asyncio.create_task(self._update_resource_async(operation_id, request))

            return operation

        except Exception as e:
            logger.error(f"Error updating resource: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return nexus_pb2.OperationResponse()

    async def DeleteResource(
        self, request: nexus_pb2.DeleteResourceRequest, context: grpc.ServicerContext
    ) -> nexus_pb2.OperationResponse:
        """Delete a resource"""
        try:
            # Check if resource exists
            resource = self.nexus_engine.resource_registry.get(request.id)
            if not resource:
                context.set_details(f"Resource {request.id} not found")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return nexus_pb2.OperationResponse()

            # Generate operation ID
            operation_id = f"op-{uuid.uuid4().hex[:8]}"

            # Create operation record
            operation = self._create_operation_response(
                operation_id=operation_id,
                resource_id=request.id,
                action="DELETE",
                status="IN_PROGRESS",
                started_at=datetime.now(timezone.utc),
            )

            self.operations[operation_id] = operation

            # Execute deletion asynchronously
            asyncio.create_task(self._delete_resource_async(operation_id, request))

            return operation

        except Exception as e:
            logger.error(f"Error deleting resource: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return nexus_pb2.OperationResponse()

    async def ListResources(
        self, request: nexus_pb2.ListResourcesRequest, context: grpc.ServicerContext
    ) -> nexus_pb2.ListResourcesResponse:
        """List resources with optional filtering"""
        try:
            resources = []
            all_resources = self.nexus_engine.resource_registry.list_all()

            for resource in all_resources:
                # Apply filters
                if request.project and resource.metadata.project != request.project:
                    continue
                if (
                    request.environment
                    and resource.metadata.environment != request.environment
                ):
                    continue
                if (
                    request.provider
                    and getattr(resource, "provider", None) != request.provider
                ):
                    continue
                if (
                    request.resource_type
                    and resource.__class__.__name__ != request.resource_type
                ):
                    continue

                resources.append(self._resource_to_pb(resource))

            # Apply pagination
            total_count = len(resources)
            start_index = 0

            if request.page_token:
                try:
                    start_index = int(request.page_token)
                except ValueError:
                    start_index = 0

            page_size = request.page_size if request.page_size > 0 else 50
            end_index = start_index + page_size

            page_resources = resources[start_index:end_index]

            # Generate next page token
            next_page_token = ""
            if end_index < total_count:
                next_page_token = str(end_index)

            return nexus_pb2.ListResourcesResponse(
                resources=page_resources,
                next_page_token=next_page_token,
                total_count=total_count,
            )

        except Exception as e:
            logger.error(f"Error listing resources: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return nexus_pb2.ListResourcesResponse()

    async def GetOperation(
        self, request: nexus_pb2.GetOperationRequest, context: grpc.ServicerContext
    ) -> nexus_pb2.OperationResponse:
        """Get operation status"""
        try:
            if request.operation_id not in self.operations:
                context.set_details(f"Operation {request.operation_id} not found")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return nexus_pb2.OperationResponse()

            return self.operations[request.operation_id]

        except Exception as e:
            logger.error(f"Error getting operation: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return nexus_pb2.OperationResponse()

    async def CheckDrift(
        self, request: nexus_pb2.CheckDriftRequest, context: grpc.ServicerContext
    ) -> nexus_pb2.CheckDriftResponse:
        """Check drift for resources"""
        try:
            drift_results = []

            if request.resource_id:
                # Check specific resource
                resource = self.nexus_engine.resource_registry.get(request.resource_id)
                if resource and hasattr(resource, "check_drift"):
                    drift_detected = await resource.check_drift()
                    drift_results.append(
                        nexus_pb2.DriftResult(
                            resource_id=resource.metadata.id,
                            resource_name=resource.name,
                            drift_detected=drift_detected,
                            state=resource.state.value,
                            drift_details=[],
                        )
                    )
            else:
                # Check all resources
                resources = self.nexus_engine.resource_registry.list_all()
                for resource in resources:
                    if hasattr(resource, "check_drift"):
                        drift_detected = await resource.check_drift()
                        drift_results.append(
                            nexus_pb2.DriftResult(
                                resource_id=resource.metadata.id,
                                resource_name=resource.name,
                                drift_detected=drift_detected,
                                state=resource.state.value,
                                drift_details=[],
                            )
                        )

            drifted_count = sum(1 for r in drift_results if r.drift_detected)

            return nexus_pb2.CheckDriftResponse(
                total_resources=len(drift_results),
                drifted_resources=drifted_count,
                results=drift_results,
            )

        except Exception as e:
            logger.error(f"Error checking drift: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return nexus_pb2.CheckDriftResponse()

    async def HealDrift(
        self, request: nexus_pb2.HealDriftRequest, context: grpc.ServicerContext
    ) -> nexus_pb2.OperationResponse:
        """Heal drift for a resource"""
        try:
            # Generate operation ID
            operation_id = f"op-{uuid.uuid4().hex[:8]}"

            # Create operation record
            operation = self._create_operation_response(
                operation_id=operation_id,
                resource_id=request.resource_id,
                action="HEAL_DRIFT",
                status="IN_PROGRESS",
                started_at=datetime.now(timezone.utc),
            )

            self.operations[operation_id] = operation

            # Execute healing asynchronously
            asyncio.create_task(self._heal_drift_async(operation_id, request))

            return operation

        except Exception as e:
            logger.error(f"Error healing drift: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return nexus_pb2.OperationResponse()

    async def SyncState(
        self, request: nexus_pb2.SyncStateRequest, context: grpc.ServicerContext
    ) -> nexus_pb2.OperationResponse:
        """Sync state with cloud providers"""
        try:
            # Generate operation ID
            operation_id = f"op-{uuid.uuid4().hex[:8]}"

            # Create operation record
            operation = self._create_operation_response(
                operation_id=operation_id,
                resource_id="multiple",
                action="SYNC_STATE",
                status="IN_PROGRESS",
                started_at=datetime.now(timezone.utc),
            )

            self.operations[operation_id] = operation

            # Execute sync asynchronously
            asyncio.create_task(self._sync_state_async(operation_id, request))

            return operation

        except Exception as e:
            logger.error(f"Error syncing state: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return nexus_pb2.OperationResponse()

    async def ListProviders(
        self, request: empty_pb2.Empty, context: grpc.ServicerContext
    ) -> nexus_pb2.ListProvidersResponse:
        """List available providers"""
        try:
            # TODO: Implement provider listing
            providers = []
            return nexus_pb2.ListProvidersResponse(providers=providers)

        except Exception as e:
            logger.error(f"Error listing providers: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return nexus_pb2.ListProvidersResponse()

    async def GetProviderHealth(
        self, request: nexus_pb2.GetProviderHealthRequest, context: grpc.ServicerContext
    ) -> nexus_pb2.ProviderHealthResponse:
        """Get provider health status"""
        try:
            # TODO: Implement provider health checking
            return nexus_pb2.ProviderHealthResponse(
                provider=request.provider,
                status="healthy",
                message="Provider is operational",
                last_check=self._datetime_to_timestamp(datetime.now(timezone.utc)),
                metrics={},
            )

        except Exception as e:
            logger.error(f"Error getting provider health: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return nexus_pb2.ProviderHealthResponse()

    async def StreamEvents(
        self, request: nexus_pb2.StreamEventsRequest, context: grpc.ServicerContext
    ) -> AsyncGenerator[nexus_pb2.EventResponse, None]:
        """Stream events in real-time"""
        try:
            # Register subscriber
            subscriber_id = f"sub-{uuid.uuid4().hex[:8]}"
            if subscriber_id not in self.event_subscribers:
                self.event_subscribers[subscriber_id] = []

            # Stream events
            while not context.cancelled() and not self._shutdown:
                # TODO: Implement actual event streaming
                await asyncio.sleep(1)

                # Sample event
                event = nexus_pb2.EventResponse(
                    event_id=f"evt-{uuid.uuid4().hex[:8]}",
                    event_type="heartbeat",
                    resource_id="",
                    resource_name="",
                    timestamp=self._datetime_to_timestamp(datetime.now(timezone.utc)),
                    payload=struct_pb2.Struct(),
                )

                yield event

        except Exception as e:
            logger.error(f"Error streaming events: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
        finally:
            # Clean up subscriber
            if subscriber_id in self.event_subscribers:
                del self.event_subscribers[subscriber_id]

    async def StreamOperationStatus(
        self,
        request: nexus_pb2.StreamOperationStatusRequest,
        context: grpc.ServicerContext,
    ) -> AsyncGenerator[nexus_pb2.OperationResponse, None]:
        """Stream operation status updates"""
        try:
            while not context.cancelled() and not self._shutdown:
                if request.operation_id in self.operations:
                    yield self.operations[request.operation_id]

                    # Stop streaming if the operation is complete
                    if self.operations[request.operation_id].status in [
                        "COMPLETED",
                        "FAILED",
                        "CANCELLED",
                    ]:
                        break

                await asyncio.sleep(0.5)

        except Exception as e:
            logger.error(f"Error streaming operation status: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)

    async def StreamResourceUpdates(
        self,
        request: nexus_pb2.StreamResourceUpdatesRequest,
        context: grpc.ServicerContext,
    ) -> AsyncGenerator[nexus_pb2.ResourceResponse, None]:
        """Stream resource updates"""
        try:
            # Register subscriber
            subscriber_id = f"sub-{uuid.uuid4().hex[:8]}"
            if subscriber_id not in self.resource_subscribers:
                self.resource_subscribers[subscriber_id] = []

            while not context.cancelled() and not self._shutdown:
                # TODO: Implement actual resource update streaming
                await asyncio.sleep(2)

                # For now, yield current resources periodically
                resources = self.nexus_engine.resource_registry.list_all()
                for resource in resources:
                    # Apply filters
                    if request.project and resource.metadata.project != request.project:
                        continue
                    if (
                        request.environment
                        and resource.metadata.environment != request.environment
                    ):
                        continue
                    if (
                        request.resource_ids
                        and resource.metadata.id not in request.resource_ids
                    ):
                        continue

                    yield self._resource_to_pb(resource)

        except Exception as e:
            logger.error(f"Error streaming resource updates: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
        finally:
            # Clean up subscriber
            if subscriber_id in self.resource_subscribers:
                del self.resource_subscribers[subscriber_id]

    # Async operation handlers
    async def _create_resource_async(
        self, operation_id: str, request: nexus_pb2.CreateResourceRequest
    ):
        """Async resource creation handler"""
        operation = self.operations[operation_id]
        try:
            # TODO: Implement actual resource creation using NexusEngine
            await asyncio.sleep(2)  # Simulate work

            # Update operation status
            operation.status = "COMPLETED"
            operation.completed_at.CopyFrom(
                self._datetime_to_timestamp(datetime.now(timezone.utc))
            )
            operation.resource_id = f"res-{uuid.uuid4().hex[:8]}"

        except Exception as e:
            operation.status = "FAILED"
            operation.error = str(e)
            operation.completed_at.CopyFrom(
                self._datetime_to_timestamp(datetime.now(timezone.utc))
            )
            logger.error(f"Failed to create resource: {e}")

    async def _update_resource_async(
        self, operation_id: str, request: nexus_pb2.UpdateResourceRequest
    ):
        """Async resource update handler"""
        operation = self.operations[operation_id]
        try:
            # TODO: Implement actual resource update using NexusEngine
            await asyncio.sleep(2)  # Simulate work

            operation.status = "COMPLETED"
            operation.completed_at.CopyFrom(
                self._datetime_to_timestamp(datetime.now(timezone.utc))
            )

        except Exception as e:
            operation.status = "FAILED"
            operation.error = str(e)
            operation.completed_at.CopyFrom(
                self._datetime_to_timestamp(datetime.now(timezone.utc))
            )
            logger.error(f"Failed to update resource: {e}")

    async def _delete_resource_async(
        self, operation_id: str, request: nexus_pb2.DeleteResourceRequest
    ):
        """Async resource deletion handler"""
        operation = self.operations[operation_id]
        try:
            # TODO: Implement actual resource deletion using NexusEngine
            await asyncio.sleep(2)  # Simulate work

            operation.status = "COMPLETED"
            operation.completed_at.CopyFrom(
                self._datetime_to_timestamp(datetime.now(timezone.utc))
            )

        except Exception as e:
            operation.status = "FAILED"
            operation.error = str(e)
            operation.completed_at.CopyFrom(
                self._datetime_to_timestamp(datetime.now(timezone.utc))
            )
            logger.error(f"Failed to delete resource: {e}")

    async def _heal_drift_async(
        self, operation_id: str, request: nexus_pb2.HealDriftRequest
    ):
        """Async drift healing handler"""
        operation = self.operations[operation_id]
        try:
            # TODO: Implement actual drift healing using NexusEngine
            await asyncio.sleep(2)  # Simulate work

            operation.status = "COMPLETED"
            operation.completed_at.CopyFrom(
                self._datetime_to_timestamp(datetime.now(timezone.utc))
            )

        except Exception as e:
            operation.status = "FAILED"
            operation.error = str(e)
            operation.completed_at.CopyFrom(
                self._datetime_to_timestamp(datetime.now(timezone.utc))
            )
            logger.error(f"Failed to heal drift: {e}")

    async def _sync_state_async(
        self, operation_id: str, request: nexus_pb2.SyncStateRequest
    ):
        """Async state sync handler"""
        operation = self.operations[operation_id]
        try:
            # TODO: Implement actual state sync using NexusEngine
            await asyncio.sleep(2)  # Simulate work

            operation.status = "COMPLETED"
            operation.completed_at.CopyFrom(
                self._datetime_to_timestamp(datetime.now(timezone.utc))
            )

        except Exception as e:
            operation.status = "FAILED"
            operation.error = str(e)
            operation.completed_at.CopyFrom(
                self._datetime_to_timestamp(datetime.now(timezone.utc))
            )
            logger.error(f"Failed to sync state: {e}")

    def shutdown(self):
        """Shutdown the service"""
        self._shutdown = True


class NexusGRPCServer:
    """
    gRPC server wrapper for NexusGRPCService
    """

    def __init__(
        self,
        service: Optional[NexusGRPCService] = None,
        host: str = "[::]",
        port: int = 50051,
        max_workers: int = 10,
    ):
        """
        Initialize the gRPC server

        Args:
            service: NexusGRPCService instance
            host: Host to bind the server to
            port: Port to bind the server to
            max_workers: Maximum number of worker threads
        """
        self.service = service or NexusGRPCService()
        self.host = host
        self.port = port
        self.max_workers = max_workers
        self.server = None

    async def start(self):
        """Start the gRPC server"""
        self.server = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers=self.max_workers)
        )

        # Add service to server
        nexus_pb2_grpc.add_NexusServiceServicer_to_server(self.service, self.server)

        # Add insecure port (for development)
        listen_addr = f"{self.host}:{self.port}"
        self.server.add_insecure_port(listen_addr)

        logger.info(f"Starting gRPC server on {listen_addr}")
        await self.server.start()

        logger.info(f"gRPC server started successfully on {listen_addr}")

    async def stop(self, grace: int = 5):
        """Stop the gRPC server"""
        if self.server:
            logger.info("Stopping gRPC server...")
            self.service.shutdown()
            await self.server.stop(grace)
            logger.info("gRPC server stopped")

    async def serve(self):
        """Start the server and wait for termination"""
        await self.start()
        await self.server.wait_for_termination()


if __name__ == "__main__":
    # Example usage
    async def main():
        server = NexusGRPCServer()
        await server.serve()

    asyncio.run(main())
