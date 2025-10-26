import os
from typing import Any, Dict

from loguru import logger

from ..core.config import Settings
from ..core.exceptions import SessionNotFoundException
from ..llm.interface import LLMInterface
from ..models.domain import Session
from ..repositories.session_repo import SessionRepository


class SessionService:
    """
    Business logic for session management operations.
    """

    def __init__(self, session_repo: SessionRepository, settings: Settings) -> None:
        """
        Initialize the SessionService.

        Args:
            session_repo: Repository for session data.
            settings: Application settings.
        """
        self.session_repo: SessionRepository = session_repo
        self.settings: Settings = settings

    async def initialize_session(self, session_id: str, role: str) -> LLMInterface:
        """
        Create and store a new session for the specified role.

        Args:
            session_id: Identifier of the session to initialize.
            role: Agent role to initialize the session.

        Returns:
            The LLMInterface object.

        Raises:
            SessionNotFoundException: If the role configuration file is not found.
        """
        # construct path to role config
        config_dir = self.settings.AGENT_CONFIGS_PATH
        config_file = os.path.join(config_dir, f"{role}.yaml")
        if not os.path.isfile(config_file):
            raise SessionNotFoundException(f"Role config not found for role '{role}'")

        # generate session ID and store session
        await self.session_repo.create(session_id, role)
        return LLMInterface(config_file_path=config_file)

    async def get_session(self, session_id: str, role: str) -> LLMInterface:
        """
        Get the information about a session.

        Args:
            session_id: Identifier of the session to get information about.
            role: Role of the agent to get information about.

        Returns:
            The LLMInterface object.
        """
        session_history = await self.session_repo.get_history(session_id)
        if not session_history or role not in session_history.keys():
            logger.info(f"Session history not found for role {role} in session {session_id} - initializing session")
            return await self.initialize_session(session_id, role)

        return LLMInterface(
            config_file_path=os.path.join(self.settings.AGENT_CONFIGS_PATH, f"{role}.yaml"),
            past_messages=session_history[role].history,
        )

    async def delete_session(self, session_id: str) -> None:
        """
        Delete a session and all associated data.

        Args:
            session_id: Identifier of the session to delete.

        Raises:
            SessionNotFoundException: If the session does not exist.
        """
        session_history = await self.session_repo.get_history(session_id)
        if not session_history:
            raise SessionNotFoundException(f"Session not found: {session_id}")
        session = Session(session_id=session_id, roles=list(session_history.keys()))

        await self.session_repo.delete(session)

    async def submit_interact(
        self,
        session_id: str,
        role: str,
        input_data: Dict[str, Any],
        use_agent: bool = False,
    ) -> str:
        """
        Submit an interaction request for asynchronous processing.

        Args:
            session_id: Identifier of the session to interact with.
            role: Role of the agent to interact with.
            input_data: Input data for the agent.
            use_agent: Whether to use agent mode.

        Returns:
            The response from the agent.
        """

        llm_interface = await self.get_session(session_id, role)
        response = await llm_interface.interact(**input_data)
        await self.session_repo.save_past_messages(session_id, role, llm_interface.past_messages)
        logger.info(f"Submitted interaction for {role} in session {session_id}")
        return response

    async def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active sessions.
        """
        return await self.session_repo.get_all()

    async def get_session_history(self, session_id: str) -> Dict[str, Any]:
        """
        Get the history of a session.
        """
        return await self.session_repo.get_history(session_id)
