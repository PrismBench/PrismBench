from typing import Dict

from loguru import logger

from ..core.config import Settings
from ..core.exceptions import SessionAlreadyExistsException, SessionNotFoundException
from ..models.domain import Session
from ..repositories.session_repository import SessionRepository
from ..tree import Tree


class SessionService:
    """Service for managing search sessions and tree initialization."""

    def __init__(
        self,
        session_repo: SessionRepository,
        settings: Settings,
    ):
        self.session_repo = session_repo
        self.settings = settings

    async def create_session(
        self,
        session_id: str,
    ) -> Session:
        """Create a new session with initialized tree."""
        if await self.session_repo.exists(session_id):
            raise SessionAlreadyExistsException(f"Session {session_id} already exists")

        # Create and initialize tree
        tree = Tree(
            concepts=self.settings.tree_config.concepts,
            difficulties=self.settings.tree_config.difficulties,
        )
        tree.initialize_tree()

        session = Session(session_id=session_id, tree=tree, status="active")

        await self.session_repo.save(session)
        logger.info(f"Created session {session_id} with {len(tree.nodes)} nodes")

        return session

    async def get_session(
        self,
        session_id: str,
    ) -> Session:
        """Get existing session."""
        session = await self.session_repo.get(session_id)
        if not session:
            raise SessionNotFoundException(f"Session {session_id} not found")
        return session

    async def get_or_create_session(
        self,
        session_id: str,
    ) -> Session:
        """Get existing session or create new one."""
        try:
            return await self.get_session(session_id)
        except SessionNotFoundException:
            return await self.create_session(session_id)

    async def delete_session(
        self,
        session_id: str,
    ) -> bool:
        """Delete a session."""
        return await self.session_repo.delete(session_id)

    async def list_sessions(self) -> Dict[str, Session]:
        """List all sessions."""
        return await self.session_repo.get_all()

    async def get_session_tree_data(
        self,
        session_id: str,
    ) -> Dict:
        """Get tree data for a session."""
        session = await self.get_session(session_id)
        return session.tree.to_dict()
