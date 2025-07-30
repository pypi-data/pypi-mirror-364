from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

from .base_resource import BaseResource, ResourceState, ResourceMetadata
from ..exceptions import ResourceException


logger = logging.getLogger(__name__)


class TrackingLevel(Enum):
    """Levels of resource tracking"""

    MINIMAL = "minimal"  # Basic metadata only
    STANDARD = "standard"  # Include state changes
    DETAILED = "detailed"  # Include all operations
    COMPREHENSIVE = "comprehensive"  # Include performance metrics


@dataclass
class ResourceOperation:
    """Represents an operation performed on a resource"""

    resource_id: str
    operation: str
    timestamp: datetime
    user: Optional[str] = None
    source: Optional[str] = None
    duration_ms: Optional[int] = None
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceSnapshot:
    """Snapshot of a resource's state at a point in time"""

    resource_id: str
    timestamp: datetime
    state: ResourceState
    spec_hash: str
    provider_data: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    cost_estimate: Optional[float] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceLifecycleEvent:
    """Event in a resource's lifecycle"""

    resource_id: str
    event_type: str
    timestamp: datetime
    old_state: Optional[ResourceState] = None
    new_state: Optional[ResourceState] = None
    triggered_by: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)


class ResourceTracker:
    """
    Tracks resource lifecycle, operations, and state changes.

    Provides:
    - Operation history and audit trail
    - State snapshots and change tracking
    - Performance metrics collection
    - Resource discovery and inventory
    - Cost tracking and optimization hints
    """

    def __init__(self, tracking_level: TrackingLevel = TrackingLevel.STANDARD):
        self.tracking_level = tracking_level
        self._operations: Dict[str, List[ResourceOperation]] = {}
        self._snapshots: Dict[str, List[ResourceSnapshot]] = {}
        self._lifecycle_events: Dict[str, List[ResourceLifecycleEvent]] = {}
        self._resource_index: Dict[str, ResourceMetadata] = {}
        self._tag_index: Dict[str, Set[str]] = {}
        self._type_index: Dict[str, Set[str]] = {}
        self._project_index: Dict[str, Set[str]] = {}
        self._environment_index: Dict[str, Set[str]] = {}

        # Performance tracking
        self._performance_metrics: Dict[str, Dict[str, Any]] = {}

        # Configuration
        self._retention_days = 30
        self._snapshot_interval = timedelta(hours=1)
        self._max_operations_per_resource = 1000

    def track_resource(self, resource: BaseResource) -> None:
        """Start tracking a resource"""
        resource_id = resource.metadata.id

        # Index the resource
        self._resource_index[resource_id] = resource.metadata

        # Update indices
        self._update_indices(resource)

        # Record initial lifecycle event
        self._record_lifecycle_event(
            resource_id=resource_id,
            event_type="resource_tracked",
            new_state=resource.status.state,
            triggered_by="tracker",
        )

        # Create initial snapshot
        if self.tracking_level in [TrackingLevel.DETAILED, TrackingLevel.COMPREHENSIVE]:
            self._create_snapshot(resource)

        logger.debug(f"Started tracking resource: {resource.metadata.name}")

    def untrack_resource(self, resource_id: str) -> None:
        """Stop tracking a resource"""
        if resource_id not in self._resource_index:
            return

        metadata = self._resource_index[resource_id]

        # Record final lifecycle event
        self._record_lifecycle_event(
            resource_id=resource_id,
            event_type="resource_untracked",
            triggered_by="tracker",
        )

        # Remove from indices
        self._remove_from_indices(resource_id, metadata)

        # Clean up old data if configured
        if self._retention_days > 0:
            self._cleanup_old_data(resource_id)

        logger.debug(f"Stopped tracking resource: {metadata.name}")

    def record_operation(
        self,
        resource_id: str,
        operation: str,
        user: Optional[str] = None,
        source: Optional[str] = None,
        duration_ms: Optional[int] = None,
        success: bool = True,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record an operation on a resource"""
        if resource_id not in self._resource_index:
            logger.warning(f"Recording operation on untracked resource: {resource_id}")
            return

        op = ResourceOperation(
            resource_id=resource_id,
            operation=operation,
            timestamp=datetime.utcnow(),
            user=user,
            source=source,
            duration_ms=duration_ms,
            success=success,
            error=error,
            metadata=metadata or {},
        )

        if resource_id not in self._operations:
            self._operations[resource_id] = []

        self._operations[resource_id].append(op)

        # Limit operation history
        if len(self._operations[resource_id]) > self._max_operations_per_resource:
            self._operations[resource_id] = self._operations[resource_id][
                -self._max_operations_per_resource :
            ]

        # Update performance metrics
        if self.tracking_level == TrackingLevel.COMPREHENSIVE and duration_ms:
            self._update_performance_metrics(resource_id, operation, duration_ms)

    def record_state_change(
        self,
        resource: BaseResource,
        old_state: Optional[ResourceState] = None,
        triggered_by: Optional[str] = None,
    ) -> None:
        """Record a state change for a resource"""
        resource_id = resource.metadata.id

        if resource_id not in self._resource_index:
            logger.warning(
                f"Recording state change on untracked resource: {resource_id}"
            )
            return

        # Record lifecycle event
        self._record_lifecycle_event(
            resource_id=resource_id,
            event_type="state_change",
            old_state=old_state,
            new_state=resource.status.state,
            triggered_by=triggered_by,
        )

        # Create snapshot if configured
        if self.tracking_level in [TrackingLevel.DETAILED, TrackingLevel.COMPREHENSIVE]:
            self._create_snapshot(resource)

    def create_snapshot(self, resource: BaseResource) -> None:
        """Create a snapshot of a resource's current state"""
        self._create_snapshot(resource)

    def _create_snapshot(self, resource: BaseResource) -> None:
        """Internal method to create a snapshot"""
        resource_id = resource.metadata.id

        # Calculate spec hash (simplified)
        spec_hash = str(hash(str(resource.spec)))

        snapshot = ResourceSnapshot(
            resource_id=resource_id,
            timestamp=datetime.utcnow(),
            state=resource.status.state,
            spec_hash=spec_hash,
            provider_data=resource.status.provider_data.copy(),
            tags=resource.metadata.to_tags(),
            cost_estimate=self._estimate_cost(resource),
            performance_metrics=self._get_performance_metrics(resource_id),
        )

        if resource_id not in self._snapshots:
            self._snapshots[resource_id] = []

        self._snapshots[resource_id].append(snapshot)

        # Limit snapshot history
        max_snapshots = 100
        if len(self._snapshots[resource_id]) > max_snapshots:
            self._snapshots[resource_id] = self._snapshots[resource_id][-max_snapshots:]

    def _record_lifecycle_event(
        self,
        resource_id: str,
        event_type: str,
        old_state: Optional[ResourceState] = None,
        new_state: Optional[ResourceState] = None,
        triggered_by: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a lifecycle event"""
        event = ResourceLifecycleEvent(
            resource_id=resource_id,
            event_type=event_type,
            timestamp=datetime.utcnow(),
            old_state=old_state,
            new_state=new_state,
            triggered_by=triggered_by,
            data=data or {},
        )

        if resource_id not in self._lifecycle_events:
            self._lifecycle_events[resource_id] = []

        self._lifecycle_events[resource_id].append(event)

    def _update_indices(self, resource: BaseResource) -> None:
        """Update search indices for a resource"""
        resource_id = resource.metadata.id
        metadata = resource.metadata

        # Type index
        resource_type = resource.__class__.__name__
        if resource_type not in self._type_index:
            self._type_index[resource_type] = set()
        self._type_index[resource_type].add(resource_id)

        # Project index
        if metadata.project:
            if metadata.project not in self._project_index:
                self._project_index[metadata.project] = set()
            self._project_index[metadata.project].add(resource_id)

        # Environment index
        if metadata.environment:
            if metadata.environment not in self._environment_index:
                self._environment_index[metadata.environment] = set()
            self._environment_index[metadata.environment].add(resource_id)

        # Tag index
        for tag_key, tag_value in metadata.labels.items():
            tag = f"{tag_key}={tag_value}"
            if tag not in self._tag_index:
                self._tag_index[tag] = set()
            self._tag_index[tag].add(resource_id)

    def _remove_from_indices(
        self, resource_id: str, metadata: ResourceMetadata
    ) -> None:
        """Remove a resource from all indices"""
        # Remove from all indices
        for index in [
            self._type_index,
            self._project_index,
            self._environment_index,
            self._tag_index,
        ]:
            for key, resource_set in index.items():
                resource_set.discard(resource_id)

        # Remove from main index
        self._resource_index.pop(resource_id, None)

    def _update_performance_metrics(
        self, resource_id: str, operation: str, duration_ms: int
    ) -> None:
        """Update performance metrics for a resource"""
        if resource_id not in self._performance_metrics:
            self._performance_metrics[resource_id] = {}

        if operation not in self._performance_metrics[resource_id]:
            self._performance_metrics[resource_id][operation] = {
                "count": 0,
                "total_duration": 0,
                "avg_duration": 0,
                "min_duration": float("inf"),
                "max_duration": 0,
            }

        metrics = self._performance_metrics[resource_id][operation]
        metrics["count"] += 1
        metrics["total_duration"] += duration_ms
        metrics["avg_duration"] = metrics["total_duration"] / metrics["count"]
        metrics["min_duration"] = min(metrics["min_duration"], duration_ms)
        metrics["max_duration"] = max(metrics["max_duration"], duration_ms)

    def _estimate_cost(self, resource: BaseResource) -> Optional[float]:
        """Estimate cost for a resource (placeholder)"""
        # This would integrate with provider cost estimation
        return None

    def _get_performance_metrics(self, resource_id: str) -> Dict[str, Any]:
        """Get performance metrics for a resource"""
        return self._performance_metrics.get(resource_id, {})

    def _cleanup_old_data(self, resource_id: str) -> None:
        """Clean up old data for a resource"""
        cutoff_time = datetime.utcnow() - timedelta(days=self._retention_days)

        # Clean up operations
        if resource_id in self._operations:
            self._operations[resource_id] = [
                op
                for op in self._operations[resource_id]
                if op.timestamp >= cutoff_time
            ]

        # Clean up snapshots
        if resource_id in self._snapshots:
            self._snapshots[resource_id] = [
                snapshot
                for snapshot in self._snapshots[resource_id]
                if snapshot.timestamp >= cutoff_time
            ]

        # Clean up lifecycle events
        if resource_id in self._lifecycle_events:
            self._lifecycle_events[resource_id] = [
                event
                for event in self._lifecycle_events[resource_id]
                if event.timestamp >= cutoff_time
            ]

    # Query methods

    def get_operations(
        self, resource_id: str, limit: Optional[int] = None
    ) -> List[ResourceOperation]:
        """Get operations for a resource"""
        operations = self._operations.get(resource_id, [])
        if limit:
            return operations[-limit:]
        return operations

    def get_snapshots(
        self, resource_id: str, limit: Optional[int] = None
    ) -> List[ResourceSnapshot]:
        """Get snapshots for a resource"""
        snapshots = self._snapshots.get(resource_id, [])
        if limit:
            return snapshots[-limit:]
        return snapshots

    def get_lifecycle_events(
        self, resource_id: str, limit: Optional[int] = None
    ) -> List[ResourceLifecycleEvent]:
        """Get lifecycle events for a resource"""
        events = self._lifecycle_events.get(resource_id, [])
        if limit:
            return events[-limit:]
        return events

    def find_resources_by_type(self, resource_type: str) -> List[str]:
        """Find resources by type"""
        return list(self._type_index.get(resource_type, set()))

    def find_resources_by_project(self, project: str) -> List[str]:
        """Find resources by project"""
        return list(self._project_index.get(project, set()))

    def find_resources_by_environment(self, environment: str) -> List[str]:
        """Find resources by environment"""
        return list(self._environment_index.get(environment, set()))

    def find_resources_by_tag(self, tag_key: str, tag_value: str) -> List[str]:
        """Find resources by tag"""
        tag = f"{tag_key}={tag_value}"
        return list(self._tag_index.get(tag, set()))

    def get_resource_metadata(self, resource_id: str) -> Optional[ResourceMetadata]:
        """Get metadata for a resource"""
        return self._resource_index.get(resource_id)

    def get_all_resources(self) -> List[ResourceMetadata]:
        """Get all tracked resources"""
        return list(self._resource_index.values())

    def get_resource_count(self) -> int:
        """Get total number of tracked resources"""
        return len(self._resource_index)

    def get_stats(self) -> Dict[str, Any]:
        """Get tracking statistics"""
        return {
            "total_resources": len(self._resource_index),
            "total_operations": sum(len(ops) for ops in self._operations.values()),
            "total_snapshots": sum(
                len(snapshots) for snapshots in self._snapshots.values()
            ),
            "total_events": sum(
                len(events) for events in self._lifecycle_events.values()
            ),
            "resources_by_type": {
                res_type: len(resources)
                for res_type, resources in self._type_index.items()
            },
            "tracking_level": self.tracking_level.value,
            "retention_days": self._retention_days,
        }

    # CLI-compatible methods
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all resources in CLI-compatible format"""
        resources = []
        for resource_id, metadata in self._resource_index.items():
            resources.append({
                "name": metadata.name,
                "type": metadata.id.split(":")[-1],  # Extract type from ID
                "id": resource_id,
                "project": metadata.project,
                "environment": metadata.environment,
                "status": "active",  # Default status
                "provider": "aws",  # Default provider
                "provider_id": resource_id,
                "created_at": metadata.created_at.isoformat() if metadata.created_at else None,
                "updated_at": metadata.updated_at.isoformat() if metadata.updated_at else None,
                "labels": metadata.labels,
                "configuration": {}  # Would be populated from snapshots
            })
        return resources

    def get_resource(self, resource_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific resource by name in CLI-compatible format"""
        for resource_id, metadata in self._resource_index.items():
            if metadata.name == resource_name:
                return {
                    "name": metadata.name,
                    "type": metadata.id.split(":")[-1],
                    "id": resource_id,
                    "project": metadata.project,
                    "environment": metadata.environment,
                    "status": "active",
                    "provider": "aws",
                    "provider_id": resource_id,
                    "created_at": metadata.created_at.isoformat() if metadata.created_at else None,
                    "updated_at": metadata.updated_at.isoformat() if metadata.updated_at else None,
                    "labels": metadata.labels,
                    "configuration": {}
                }
        return None

    def add_resource(self, resource_name: str, resource_type: str, resource_details: Dict[str, Any]) -> bool:
        """Add a new resource to tracking"""
        try:
            # Create a mock resource ID
            resource_id = f"{resource_type}:{resource_name}"
            
            # Create metadata
            metadata = ResourceMetadata(
                id=resource_id,
                name=resource_name,
                project=resource_details.get("project"),
                environment=resource_details.get("environment"),
                labels=resource_details.get("labels", {}),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Add to index
            self._resource_index[resource_id] = metadata
            
            # Update type index
            if resource_type not in self._type_index:
                self._type_index[resource_type] = set()
            self._type_index[resource_type].add(resource_id)
            
            # Record lifecycle event
            self._record_lifecycle_event(
                resource_id=resource_id,
                event_type="resource_imported",
                triggered_by="cli",
                data=resource_details
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to add resource {resource_name}: {e}")
            return False

    def update_resource(self, resource_name: str, resource_state: Dict[str, Any]) -> bool:
        """Update a resource's state"""
        try:
            # Find resource
            resource_id = None
            for rid, metadata in self._resource_index.items():
                if metadata.name == resource_name:
                    resource_id = rid
                    break
            
            if not resource_id:
                return False
            
            # Update metadata
            metadata = self._resource_index[resource_id]
            metadata.updated_at = datetime.utcnow()
            
            # Record lifecycle event
            self._record_lifecycle_event(
                resource_id=resource_id,
                event_type="resource_updated",
                triggered_by="cli",
                data=resource_state
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to update resource {resource_name}: {e}")
            return False

    def remove_resource(self, resource_name: str) -> bool:
        """Remove a resource from tracking"""
        try:
            # Find resource
            resource_id = None
            metadata = None
            for rid, meta in self._resource_index.items():
                if meta.name == resource_name:
                    resource_id = rid
                    metadata = meta
                    break
            
            if not resource_id or not metadata:
                return False
            
            # Remove from indices
            self._remove_from_indices(resource_id, metadata)
            
            # Record lifecycle event
            self._record_lifecycle_event(
                resource_id=resource_id,
                event_type="resource_removed",
                triggered_by="cli"
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to remove resource {resource_name}: {e}")
            return False

    def mark_resource_missing(self, resource_name: str) -> bool:
        """Mark a resource as missing from provider"""
        try:
            # Find resource
            resource_id = None
            for rid, metadata in self._resource_index.items():
                if metadata.name == resource_name:
                    resource_id = rid
                    break
            
            if not resource_id:
                return False
            
            # Record lifecycle event
            self._record_lifecycle_event(
                resource_id=resource_id,
                event_type="resource_missing",
                triggered_by="cli"
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to mark resource missing {resource_name}: {e}")
            return False
