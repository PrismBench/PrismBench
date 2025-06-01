import os
import uuid

from ..core.config import Settings
from ..core.exceptions import SessionNotFoundException
from ..llm.interface import LLMInterface
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
        self.session_repo = session_repo
        self.settings = settings

    async def initialize_session(self, role: str) -> str:
        """
        Create and store a new session for the specified role.

        Args:
            role: Agent role to initialize the session.

        Returns:
            The generated session ID.

        Raises:
            SessionNotFoundException: If the role configuration file is not found.
        """
        # Construct path to role config
        config_dir = self.settings.AGENT_CONFIGS_PATH
        config_file = os.path.join(config_dir, f"{role}.yml")
        if not os.path.isfile(config_file):
            raise SessionNotFoundException(f"Role config not found for role '{role}'")

        # Validate role by instantiating LLMInterface
        LLMInterface.from_config_file(config_file)

        # Generate session ID and store session
        session_id = str(uuid.uuid4())
        await self.session_repo.create(session_id, role)
        return session_id

    async def clear_history(self, session_id: str) -> None:
        """
        Clear the conversation history for a given session.

        Args:
            session_id: Identifier of the session to clear.

        Raises:
            SessionNotFoundException: If the session does not exist.
        """
        session = await self.session_repo.get(session_id)
        if session is None:
            raise SessionNotFoundException(f"Session not found: {session_id}")
        await self.session_repo.update_history(session_id, [])

    async def delete_session(self, session_id: str) -> None:
        """
        Delete a session and all associated data.

        Args:
            session_id: Identifier of the session to delete.

        Raises:
            SessionNotFoundException: If the session does not exist.
        """
        session = await self.session_repo.get(session_id)
        if session is None:
            raise SessionNotFoundException(f"Session not found: {session_id}")
        await self.session_repo.delete(session_id)
