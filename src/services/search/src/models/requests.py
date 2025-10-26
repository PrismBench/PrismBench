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
    # resume functionality
    resume: Optional[bool] = Field(
        False,
        description="Whether to resume from a previous run",
    )
    tree_pickle_path: Optional[str] = Field(
        None,
        description="Path to the pickle file containing the tree state to resume from",
    )
    resume_phase: Optional[str] = Field(
        None,
        description="Phase name to resume from (e.g., 'phase_1', 'phase_2')",
    )
    resume_iteration: Optional[int] = Field(
        None,
        description="Last completed iteration number to resume from",
    )


class TaskStopRequest(BaseModel):
    """Request for stopping a task."""

    task_id: str = Field(
        ...,
        description="Task ID to stop",
    )
