import asyncio
from typing import Dict
from uuid import uuid4

from loguru import logger

from ..core.config import Settings
from ..core.exceptions import TaskExecutionException, TaskNotFoundException
from ..models.domain import PhaseStatus, Task, TaskStatus
from ..repositories.task_repository import TaskRepository
from ..services.mcts_service import MCTSService
from ..services.session_service import SessionService


class TaskService:
    """Service for managing task execution and orchestration."""

    def __init__(
        self,
        task_repo: TaskRepository,
        session_service: SessionService,
        mcts_service: MCTSService,
        settings: Settings,
    ):
        self.task_repo = task_repo
        self.session_service = session_service
        self.mcts_service = mcts_service
        self.settings = settings

    async def create_task(
        self,
        session_id: str,
    ) -> Task:
        """Create and start a new MCTS task."""
        task_id = str(uuid4())

        # Ensure session exists
        session = await self.session_service.get_or_create_session(session_id)

        # Create task with phase status tracking
        task = Task(
            task_id=task_id,
            session_id=session_id,
            status=TaskStatus.RUNNING,
            phases={
                "phase1": PhaseStatus(status="running"),
                "phase2": PhaseStatus(status="pending"),
                "phase3": PhaseStatus(status="pending"),
            },
        )

        # Start background execution
        asyncio_task = asyncio.create_task(self._execute_mcts_phases(task, session.tree))
        task.asyncio_task = asyncio_task

        await self.task_repo.save(task)
        logger.info(f"Created task {task_id} for session {session_id}")

        return task

    async def stop_task(
        self,
        task_id: str,
    ) -> Task:
        """Stop a running task."""
        task = await self.task_repo.get(task_id)
        if not task:
            raise TaskNotFoundException(f"Task {task_id} not found")

        if task.asyncio_task and not task.asyncio_task.done():
            task.asyncio_task.cancel()
            task.status = TaskStatus.CANCELLED

            # Update phase statuses
            for phase_status in task.phases.values():
                if phase_status.status in ["running", "pending"]:
                    phase_status.status = "cancelled"
                    phase_status.cancelled_at = asyncio.get_event_loop().time()

            await self.task_repo.save(task)
            logger.info(f"Cancelled task {task_id}")

        return task

    async def get_task(
        self,
        task_id: str,
    ) -> Task:
        """Get task by ID."""
        task = await self.task_repo.get(task_id)
        if not task:
            raise TaskNotFoundException(f"Task {task_id} not found")
        return task

    async def get_all_tasks(self) -> Dict[str, Task]:
        """Get all tasks."""
        return await self.task_repo.get_all()

    async def get_task_status_report(self) -> Dict:
        """Get formatted status report for all tasks."""
        tasks = await self.get_all_tasks()

        if not tasks:
            return {"message": "No tasks to report"}

        status_report = {}
        for task_id, task in tasks.items():
            status_report[task_id] = {
                "task_id": task_id,
                "session_id": task.session_id,
                "status": task.status.value,
                "phases": {
                    phase_name: {
                        "status": phase.status,
                        "created_at": phase.created_at,
                        "started_at": phase.started_at,
                        "completed_at": phase.completed_at,
                        "cancelled_at": phase.cancelled_at,
                        "error": phase.error,
                        "path": phase.path,
                    }
                    for phase_name, phase in task.phases.items()
                },
            }

        return status_report

    async def _execute_mcts_phases(
        self,
        task: Task,
        tree,
    ) -> None:
        """Execute MCTS phases in background."""
        try:
            if self.settings.experiment_config:
                phase_sequences = self.settings.experiment_config.phase_sequences
            else:
                phase_sequences = ["phase_1", "phase_2", "phase_3"]

            logger.info(
                f"Running experiment {self.settings.experiment_config.name} with phase sequences: {phase_sequences}"
            )

            for i, phase_name in enumerate(phase_sequences):
                if phase_name not in task.phases:
                    task.phases[phase_name] = PhaseStatus(status="pending" if i > 1 else "running")
            await self.task_repo.save(task)
            # run phases in sequence
            await self.mcts_service.run_multiple_phases(phase_sequences, tree, task)

            task.status = TaskStatus.COMPLETED
            await self.task_repo.save(task)

        except asyncio.CancelledError:
            logger.info(f"Task {task.task_id} was cancelled")
            raise
        except Exception as e:
            logger.exception(f"Error in task {task.task_id}: {e}")
            task.status = TaskStatus.FAILED
            # update running phases to error status
            for phase_status in task.phases.values():
                if phase_status.status == "running":
                    phase_status.status = "error"
                    phase_status.error = str(e)
            await self.task_repo.save(task)
            raise TaskExecutionException(f"Task execution failed: {e}")

    async def cleanup_old_tasks(
        self,
        max_age_hours: int = 24,
    ) -> int:
        """Clean up old completed tasks."""
        return await self.task_repo.cleanup_completed_tasks(max_age_hours)
