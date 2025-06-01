from typing import Optional

from pydantic import BaseModel, Field


class SessionRequest(BaseModel):
    """Request for session configuration."""

    session_id: str = Field(
        ...,
        description="Unique session identifier",
        example="123e4567-e89b-12d3-a456-426614174000",
    )


class TaskCreateRequest(BaseModel):
    """Request for creating a new task."""

    session_id: Optional[str] = Field(
        None,
        description="Session ID for the task. If not provided, will be auto-generated",
    )


class TaskStopRequest(BaseModel):
    """Request for stopping a task."""

    task_id: str = Field(
        ...,
        description="Task ID to stop",
    )
