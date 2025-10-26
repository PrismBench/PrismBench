import asyncio
from typing import Dict, Optional

from ..models.domain import Session
from .base import BaseRepository


class SessionRepository(BaseRepository[Session]):
    """In-memory session repository with thread-safe operations."""

    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        self._lock = asyncio.Lock()

    async def get(
        self,
        session_id: str,
    ) -> Optional[Session]:
        """Get a session by ID."""
        async with self._lock:
            return self._sessions.get(session_id)

    async def save(
        self,
        session: Session,
    ) -> None:
        """Save or update a session."""
        async with self._lock:
            self._sessions[session.session_id] = session

    async def delete(
        self,
        session_id: str,
    ) -> bool:
        """Delete a session by ID."""
        async with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False

    async def exists(
        self,
        session_id: str,
    ) -> bool:
        """Check if a session exists."""
        async with self._lock:
            return session_id in self._sessions

    async def get_all(
        self,
    ) -> Dict[str, Session]:
        """Get all sessions."""
        async with self._lock:
            return dict(self._sessions)

    async def get_active_sessions(
        self,
    ) -> Dict[str, Session]:
        """Get all active sessions."""
        async with self._lock:
            return {session_id: session for session_id, session in self._sessions.items() if session.status == "active"}

    async def update_session_status(
        self,
        session_id: str,
        status: str,
    ) -> bool:
        """Update session status."""
        async with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id].update_status(status)
                return True
            return False

    async def clear(
        self,
    ) -> None:
        """Clear all sessions (useful for testing)."""
        async with self._lock:
            self._sessions.clear()
