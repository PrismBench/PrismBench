import asyncio
from typing import Any, Dict, List

from loguru import logger

from ..core.config import Settings
from ..core.exceptions import MCTSExecutionException
from ..environment_client import EnvironmentClient
from ..mcts.phase_registry import phase_registry
from ..models.domain import Task
from ..tree import Tree


class MCTSService:
    """Service for managing MCTS execution across multiple phases."""

    def __init__(
        self,
        settings: Settings,
    ):
        self.settings = settings

        # automatically load all phase modules
        phase_registry.load_phase_modules()

        # get all available phases
        self.phases = phase_registry.list_phases()
        logger.info(f"Available phases: {self.phases}")

    def _build_phase_config(
        self,
        phase_config: Any,
        search_config: Any,
        scoring_config: Any,
        environment: Any,
    ) -> Dict:
        """Build proper configuration format for phase creation."""
        return {
            "phase_params": phase_config.__dict__,
            "search_params": search_config.__dict__,
            "scoring_params": scoring_config.__dict__,
            "environment": environment.__dict__,
        }

    def _get_phase_config(self, phase_name: str) -> Any:
        """
        Get configuration for a specific phase.

        Args:
            phase_name: Name of the phase (e.g., 'phase_1', 'custom_phase')

        Returns:
            Phase configuration object
        """
        # load configs
        if hasattr(self.settings, "phase_configs"):
            if phase_name in self.settings.phase_configs:
                return self.settings.phase_configs[phase_name]
            else:
                logger.warning(f"No phase configs found for {phase_name}")
                return None
        else:
            logger.warning(f"No phase configs found for {phase_name}")
            return None

    async def run_phase(
        self,
        phase_name: str,
        tree: Tree,
        task: Task,
    ) -> None:
        """Run a generic phase by name.

        Args:
            phase_name: Name of the phase to run (e.g., 'phase_1', 'custom_phase')
            tree: Tree instance
            task: Task instance
        """
        if phase_name not in self.phases:
            raise MCTSExecutionException(f"Phase '{phase_name}' not found. Available: {self.phases}")

        try:
            logger.info(f"Starting {phase_name} for task {task.task_id}")

            # Update phase status
            phase_status = task.get_phase(phase_name)
            if phase_status:
                phase_status.status = "running"
                phase_status.started_at = asyncio.get_event_loop().time()

            # Build configuration
            phase_config = self._get_phase_config(phase_name)
            config = self._build_phase_config(
                phase_config.phase_params,
                phase_config.search_params,
                phase_config.scoring_params,
                phase_config.environment,
            )

            # get environment
            environment = EnvironmentClient(config["environment"])

            # Lazy import to avoid circular import
            from ..mcts.utils import create_phase

            # Create and run phase
            phase = create_phase(
                phase_name=phase_name,
                tree=tree,
                environment=environment,
                config=config,
            )

            # check for resume flag
            resume_iteration = task.metadata.get("resume_iteration", None)
            resume_phase = task.metadata.get("resume_phase", None)
            if resume_iteration is not None and phase_name == resume_phase:
                phase.set_resume_state(iteration=resume_iteration)
                logger.info(f"Resuming {phase_name} from iteration {resume_iteration}")

            await phase.run()

            # Update phase status to completed
            if phase_status:
                phase_status.status = "completed"
                phase_status.completed_at = asyncio.get_event_loop().time()
                phase_status.path = phase.path

            logger.info(f"{phase_name} completed for task {task.task_id}")

        except Exception as e:
            logger.exception(f"Error in {phase_name} for task {task.task_id}: {e}")
            phase_status = task.get_phase(phase_name)
            if phase_status:
                phase_status.status = "error"
                phase_status.error = str(e)
            raise MCTSExecutionException(f"{phase_name} execution failed: {e}")

    async def run_multiple_phases(
        self,
        phase_sequence: List[str],
        tree: Tree,
        task: Task,
    ) -> None:
        """Run multiple phases in sequence.

        Args:
            phase_sequence: List of phase names to run in order
            tree: Tree instance
            task: Task instance
        """
        for phase_name in phase_sequence:
            phase_status = task.get_phase(phase_name)
            if phase_status.status == "completed":
                logger.info(f"Skipping {phase_name} because it is already completed")
                continue
            await self.run_phase(phase_name, tree, task)
