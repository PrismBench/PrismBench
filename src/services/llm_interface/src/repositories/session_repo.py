import json
from typing import Any, Dict, List, Optional

import redis.asyncio as aioredis
from loguru import logger

from ..core.config import get_settings


class SessionRepository:
    """
    Redis-backed repository for session and conversation history management.
    """

    def __init__(self) -> None:
        """
        Initialize the repository with a Redis client.
        """
        settings = get_settings()
        self.redis: aioredis.Redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    async def create(self, session_id: str, role: str) -> None:
        """
        Create a new session record and initialize empty history.

        Args:
            session_id: Unique identifier for the session.
            role: Role assigned to the session.
        """
        await self.redis.hset(f"session:{session_id}", mapping={"role": role})
        # Initialize empty history list
        await self.redis.set(f"history:{session_id}", json.dumps([]))

    async def get(self, session_id: str) -> Optional[Dict[str, str]]:
        """
        Retrieve session information.

        Args:
            session_id: Unique identifier for the session.

        Returns:
            A dictionary with session fields or None if not found.
        """
        data = await self.redis.hgetall(f"session:{session_id}")
        return data or None

    async def delete(self, session_id: str) -> None:
        """
        Delete a session and all its associated data.

        Args:
            session_id: Unique identifier for the session.
        """
        # Identify keys to delete
        keys: List[str] = [f"session:{session_id}", f"history:{session_id}"]
        # Include associated tasks
        task_keys = await self.redis.keys(f"task:*:{session_id}")
        if task_keys:
            keys.extend(task_keys)
        if keys:
            await self.redis.delete(*keys)

    async def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history for a session.

        Args:
            session_id: Unique identifier for the session.

        Returns:
            A list of history entries (role and content).
        """
        history_json = await self.redis.get(f"history:{session_id}")
        if not history_json:
            return []
        try:
            return json.loads(history_json)
        except Exception as e:
            logger.error(f"Error parsing history for session {session_id}: {e}")
            return []

    async def update_history(self, session_id: str, history: List[Dict[str, Any]]) -> None:
        """
        Update conversation history for a session.

        Args:
            session_id: Unique identifier for the session.
            history: List of history entries to store.
        """
        try:
            await self.redis.set(f"history:{session_id}", json.dumps(history))
        except Exception as e:
            logger.error(f"Error updating history for session {session_id}: {e}")
