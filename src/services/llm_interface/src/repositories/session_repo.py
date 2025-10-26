import asyncio
import json
from typing import Any, Dict, List

import redis.asyncio as aioredis
from loguru import logger

from ..core.config import get_settings
from ..models.domain import RoleHistory, Session


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
        Create a new session record and initialize empty roles.
        If the session already exists, add the role to the session if it doesn't exist.
        If the role already exists, do nothing.

        Args:
            session_id: Unique identifier for the session.
            role: Role assigned to the session.
        """
        if not await self.redis.exists(f"session:{session_id}"):
            logger.info(f"Creating new session: {session_id}")
            session = Session(session_id=session_id, roles=[role])
            await self.redis.hset(
                f"session:{session.session_id}",
                mapping={"data": json.dumps(session.model_dump())},
            )
            await asyncio.gather(
                *[
                    self.redis.hset(
                        f"session:{session.session_id}:{role}",
                        mapping={"data": json.dumps(RoleHistory(role=role, history=[]).model_dump())},
                    )
                    for role in session.roles
                ]
            )
        else:
            logger.info(f"Session already exists: {session_id}")
            # get session from redis and rebuild the session object
            session_data = await self.redis.hgetall(f"session:{session_id}")
            session = Session(**json.loads(session_data["data"]))

            # add role to session if it doesn't exist o.w. do nothing
            if role not in session.roles:
                logger.info(f"Adding new role: {role} to session: {session_id}")
                session.roles.append(role)
                await self.redis.hset(
                    f"session:{session_id}",
                    mapping={"data": json.dumps(session.model_dump())},
                )
                await self.redis.hset(
                    f"session:{session_id}:{role}",
                    mapping={"data": json.dumps(RoleHistory(role=role, history=[]).model_dump())},
                )
            else:
                logger.warning(f"Role already exists: {role} in session: {session_id}")

    async def get_history(self, session_id: str) -> Dict[str, RoleHistory]:
        """
        Retrieve session history.

        Args:
            session_id: Unique identifier for the session.

        Returns:
            A dictionary with session fields or empty dict if not found.
        """
        session_history = {}
        session_data = await self.redis.hgetall(f"session:{session_id}")

        if session_data:
            logger.info(f"Session has data: {session_data}")
            session = Session(**json.loads(session_data["data"]))
            for role in session.roles:
                role_data = await self.redis.hgetall(f"session:{session_id}:{role}")
                role_history = RoleHistory(**json.loads(role_data["data"]))
                session_history.setdefault(role, role_history)
        return session_history

    async def get_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all session-related data from Redis.

        Returns:
            A dictionary where keys are Redis keys and values are the hash data for each key.
            Includes both main session keys (session:id) and role-specific keys (session:id:role).
        """
        all_session_data = {}

        # Find all session-related keys
        async for key in self.redis.scan_iter(match="session:*"):
            # Get the hash data for each key
            key_data = await self.redis.hgetall(key)
            if key_data:
                # Parse JSON fields where applicable
                for field, value in key_data.items():
                    try:
                        key_data[field] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        # Keep as string if not valid JSON
                        pass
                all_session_data[key] = key_data

        return all_session_data

    async def save_past_messages(
        self,
        session_id: str,
        role: str,
        past_messages: List[Dict[str, Any]],
    ) -> None:
        """
        Save past messages for a role in a session.

        Args:
            session_id: Unique identifier for the session.
            role: Role of the agent to save past messages for.
            past_messages: List of past messages to save.
        """
        logger.info(f"Saving past messages for {role} in session {session_id}")
        role_history = RoleHistory(role=role, history=past_messages)
        await self.redis.hset(
            f"session:{session_id}:{role}",
            mapping={"data": json.dumps(role_history.model_dump())},
        )

    async def delete(self, session: Session) -> None:
        """
        Delete a session and all its associated data.

        Args:
            session: Session to delete.
        """
        await self.redis.delete(f"session:{session.session_id}")
        await asyncio.gather(*[self.redis.delete(f"session:{session.session_id}:{role}") for role in session.roles])

        logger.info(f"Deleted session: {session.session_id}")
