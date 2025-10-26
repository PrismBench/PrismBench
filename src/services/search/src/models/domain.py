import asyncio
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from ..tree import Tree


class TaskStatus(str, Enum):
    """Enumeration for task statuses."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PhaseStatus(BaseModel):
    """Model for tracking phase execution status."""

    status: str = Field(..., description="Current phase status")
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    error: Optional[str] = None
    path: Optional[str] = None

    model_config = {"arbitrary_types_allowed": True}


class Session(BaseModel):
    """Domain model for a search session."""

    session_id: str = Field(
        ...,
        description="Unique session identifier",
    )
    tree: Tree = Field(
        ...,
        description="Associated tree structure",
    )
    status: str = Field(
        default="active",
        description="Session status",
    )
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"arbitrary_types_allowed": True}

    def update_status(self, status: str) -> None:
        """Update session status and timestamp."""
        self.status = status
        self.updated_at = datetime.now()


class Task(BaseModel):
    """Domain model for an execution task."""

    task_id: str = Field(
        ...,
        description="Unique task identifier",
    )
    session_id: str = Field(
        ...,
        description="Associated session ID",
    )
    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        description="Current task status",
    )
    phases: Dict[str, PhaseStatus] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    asyncio_task: Optional[asyncio.Task] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"arbitrary_types_allowed": True}

    def update_status(
        self,
        status: TaskStatus,
        error: str = None,
    ) -> None:
        """Update task status and relevant timestamps."""
        self.status = status
        if status == TaskStatus.RUNNING and not self.started_at:
            self.started_at = datetime.now()
        elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            self.completed_at = datetime.now()
        if error:
            self.error = error

    def add_phase(
        self,
        phase_name: str,
        phase_status: PhaseStatus,
    ) -> None:
        """Add or update a phase status."""
        self.phases[phase_name] = phase_status

    def get_phase(
        self,
        phase_name: str,
    ) -> Optional[PhaseStatus]:
        """Get phase status by name."""
        return self.phases.get(phase_name)

    def is_running(self) -> bool:
        """Check if task is currently running."""
        return self.status == TaskStatus.RUNNING

    def is_completed(self) -> bool:
        """Check if task is completed (success or failure)."""
        return self.status in [
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
        ]
