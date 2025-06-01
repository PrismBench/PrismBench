import asyncio
from typing import Dict, List, Optional

from ..models.domain import Task, TaskStatus
from .base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """In-memory task repository with thread-safe operations."""

    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._lock = asyncio.Lock()

    async def get(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        async with self._lock:
            return self._tasks.get(task_id)

    async def save(self, task: Task) -> None:
        """Save or update a task."""
        async with self._lock:
            self._tasks[task.task_id] = task

    async def delete(self, task_id: str) -> bool:
        """Delete a task by ID."""
        async with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                return True
            return False

    async def exists(self, task_id: str) -> bool:
        """Check if a task exists."""
        async with self._lock:
            return task_id in self._tasks

    async def get_all(self) -> Dict[str, Task]:
        """Get all tasks."""
        async with self._lock:
            return dict(self._tasks)

    async def get_by_session(
        self,
        session_id: str,
    ) -> List[Task]:
        """Get all tasks for a specific session."""
        async with self._lock:
            return [task for task in self._tasks.values() if task.session_id == session_id]

    async def get_by_status(
        self,
        status: TaskStatus,
    ) -> List[Task]:
        """Get all tasks with a specific status."""
        async with self._lock:
            return [task for task in self._tasks.values() if task.status == status]

    async def get_running_tasks(self) -> List[Task]:
        """Get all currently running tasks."""
        return await self.get_by_status(TaskStatus.RUNNING)

    async def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks."""
        return await self.get_by_status(TaskStatus.PENDING)

    async def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        error: str = None,
    ) -> bool:
        """Update task status."""
        async with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id].update_status(status, error)
                return True
            return False

    async def cancel_running_tasks_for_session(
        self,
        session_id: str,
    ) -> List[str]:
        """Cancel all running tasks for a session and return their IDs."""
        cancelled_task_ids = []
        async with self._lock:
            for task in self._tasks.values():
                if task.session_id == session_id and task.status == TaskStatus.RUNNING:
                    task.update_status(TaskStatus.CANCELLED)
                    if task.asyncio_task and not task.asyncio_task.done():
                        task.asyncio_task.cancel()
                    cancelled_task_ids.append(task.task_id)
        return cancelled_task_ids

    async def cleanup_completed_tasks(
        self,
        max_age_hours: int = 24,
    ) -> int:
        """Remove completed tasks older than specified hours."""
        from datetime import datetime, timedelta

        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        removed_count = 0

        async with self._lock:
            tasks_to_remove = []
            for task_id, task in self._tasks.items():
                if task.is_completed() and task.completed_at and task.completed_at < cutoff_time:
                    tasks_to_remove.append(task_id)

            for task_id in tasks_to_remove:
                del self._tasks[task_id]
                removed_count += 1

        return removed_count

    async def clear(self) -> None:
        """Clear all tasks (useful for testing)."""
        async with self._lock:
            self._tasks.clear()
