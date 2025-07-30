"""
HTTP Server Models - Pydantic request/response models for the REST API
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ResourceCreateRequest(BaseModel):
    """Request model for creating a resource"""

    name: str = Field(..., description="Resource name")
    type: str = Field(..., description="Resource type (e.g., VirtualMachine, Database)")
    provider: str = Field(
        ..., description="Provider name (e.g., digitalocean, aws, gcp)"
    )
    spec: Dict[str, Any] = Field(..., description="Resource-specific configuration")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Resource metadata"
    )
    dependencies: Optional[List[str]] = Field(
        default_factory=list, description="List of dependency resource IDs"
    )


class ResourceUpdateRequest(BaseModel):
    """Request model for updating a resource"""

    spec: Optional[Dict[str, Any]] = Field(
        None, description="Updated resource configuration"
    )
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")


class ResourceResponse(BaseModel):
    """Response model for resource operations"""

    id: str = Field(..., description="Resource ID")
    name: str = Field(..., description="Resource name")
    type: str = Field(..., description="Resource type")
    provider: str = Field(..., description="Provider name")
    status: Dict[str, Any] = Field(..., description="Resource status")
    spec: Dict[str, Any] = Field(..., description="Resource configuration")
    metadata: Dict[str, Any] = Field(..., description="Resource metadata")
    dependencies: List[str] = Field(..., description="Resource dependencies")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class OperationResponse(BaseModel):
    """Response model for async operations"""

    operation_id: str = Field(..., description="Operation ID")
    resource_id: str = Field(..., description="Target resource ID")
    action: str = Field(..., description="Operation action (CREATE, UPDATE, DELETE)")
    status: str = Field(..., description="Operation status")
    started_at: datetime = Field(..., description="Operation start time")
    completed_at: Optional[datetime] = Field(
        None, description="Operation completion time"
    )
    error: Optional[str] = Field(None, description="Error message if failed")


class ErrorResponse(BaseModel):
    """Standard error response model"""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")