from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response for health check."""

    status: str = Field(
        ...,
        description="Service health status",
        example="healthy",
    )
    service: str = Field(
        ...,
        description="Service name",
        example="search",
    )


class SessionResponse(BaseModel):
    """Response for session operations."""

    session_id: str = Field(
        ...,
        description="Session identifier",
    )
    message: str = Field(
        ...,
        description="Response message",
    )
    tree_size: Optional[int] = Field(
        None,
        description="Number of nodes in the tree",
    )


class TaskResponse(BaseModel):
    """Response for task operations."""

    task_id: str = Field(
        ...,
        description="Task identifier",
    )
    session_id: str = Field(
        ...,
        description="Associated session ID",
    )
    message: str = Field(
        ...,
        description="Response message",
    )
    phases: Dict[str, Any] = Field(
        default_factory=dict,
        description="Phase status information",
    )


class TaskStatusResponse(BaseModel):
    """Response for task status queries."""

    tasks: Optional[Dict[str, Any]] = Field(
        None,
        description="Task status information",
    )
    message: Optional[str] = Field(
        None,
        description="Response message when no tasks exist",
    )


class TreeDataResponse(BaseModel):
    """Response for tree data queries."""

    nodes: List[Dict[str, Any]] = Field(
        ...,
        description="List of tree nodes",
    )
    concepts: List[str] = Field(
        ...,
        description="Available concepts",
    )
    difficulties: List[str] = Field(
        ...,
        description="Available difficulty levels",
    )


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str = Field(
        ...,
        description="Error detail message",
    )
    error_type: Optional[str] = Field(
        None,
        description="Type of error",
    )
