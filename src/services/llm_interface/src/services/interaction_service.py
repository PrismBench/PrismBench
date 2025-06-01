import asyncio
import os
import uuid
from typing import Any, Dict, List

from langchain_core.messages import AIMessage, HumanMessage

from ..core.config import Settings
from ..core.exceptions import SessionNotFoundException, TaskNotFoundException
from ..llm.interface import LLMInterface
from ..repositories.session_repo import SessionRepository
from ..repositories.task_repo import TaskRepository
from .session_service import SessionService


class InteractionService:
    """
    Business logic for processing interactions and task management.
    """

    def __init__(
        self,
        session_service: SessionService,
        task_repo: TaskRepository,
        settings: Settings,
    ) -> None:
        """
        Initialize the InteractionService.

        Args:
            session_service: Service for session operations.
            task_repo: Repository for task data.
            settings: Application settings.
        """
        self.session_service = session_service
        self.task_repo = task_repo
        # Access session repository via session service
        self.session_repo: SessionRepository = session_service.session_repo
        self.settings = settings

    async def submit_interact(
        self,
        session_id: str,
        input_data: Dict[str, Any],
        use_agent: bool = False,
    ) -> str:
        """
        Submit an interaction request for asynchronous processing.

        Args:
            session_id: Identifier of the session.
            input_data: Inputs to send to the LLM.
            use_agent: Whether to use agent mode.

        Returns:
            The created task ID.

        Raises:
            SessionNotFoundException: If the session does not exist.
        """
        session = await self.session_repo.get(session_id)
        if not session:
            raise SessionNotFoundException(f"Session not found: {session_id}")

        # Initialize task
        task_id = str(uuid.uuid4())
        await self.task_repo.create_task(task_id, session_id)

        # Process in background
        asyncio.create_task(self.process_interaction(task_id, session_id, input_data, use_agent))
        return task_id

    async def process_interaction(
        self,
        task_id: str,
        session_id: str,
        input_data: Dict[str, Any],
        use_agent: bool,
    ) -> None:
        """
        Process an interaction: restore LLM, replay history, interact, and update records.

        Args:
            task_id: Identifier of the task.
            session_id: Identifier of the session.
            input_data: Inputs for the LLM.
            use_agent: Whether to use agent mode.
        """
        try:
            # Retrieve session role and config
            session = await self.session_repo.get(session_id)
            role = session.get("role")
            config_file = os.path.join(self.settings.AGENT_CONFIGS_PATH, f"{role}.yml")
            # Instantiate LLMInterface
            llm = LLMInterface.from_config_file(config_file)

            # Restore conversation history
            history = await self.session_repo.get_history(session_id)
            if history:
                messages: List[Any] = []
                for msg in history:
                    if msg.get("role") == "human":
                        messages.append(HumanMessage(content=msg.get("content")))
                    elif msg.get("role") == "ai":
                        messages.append(AIMessage(content=msg.get("content")))
                llm.conversation_history = messages

            # Invoke LLM
            if use_agent:
                raise NotImplementedError("Agent mode not implemented")
            response = llm.interact(**input_data)

            # Update history and task
            updated_history = llm.get_conversation_history()
            await self.session_repo.update_history(session_id, updated_history)
            await self.task_repo.update_result(task_id, session_id, response)
        except Exception as e:
            await self.task_repo.update_error(task_id, session_id, f"Interaction failed: {e}")

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Retrieve the status of an asynchronous task.

        Args:
            task_id: Identifier of the task.

        Returns:
            A dictionary containing task details.

        Raises:
            TaskNotFoundException: If the task does not exist.
        """
        task = await self.task_repo.get_task(task_id)
        if not task:
            raise TaskNotFoundException(f"Task not found: {task_id}")
        return task

    async def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session.

        Args:
            session_id: Identifier of the session.

        Returns:
            A list of history entries.

        Raises:
            SessionNotFoundException: If the session does not exist.
        """
        session = await self.session_repo.get(session_id)
        if not session:
            raise SessionNotFoundException(f"Session not found: {session_id}")
        return await self.session_repo.get_history(session_id)

    async def clear_memory(self, session_id: str) -> None:
        """
        Clear conversation history for a session.

        Args:
            session_id: Identifier of the session.

        Raises:
            SessionNotFoundException: If the session does not exist.
        """
        session = await self.session_repo.get(session_id)
        if not session:
            raise SessionNotFoundException(f"Session not found: {session_id}")
        await self.session_repo.update_history(session_id, [])
