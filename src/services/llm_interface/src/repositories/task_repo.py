import json
from typing import Any, Dict, List, Optional

import redis.asyncio as aioredis
from loguru import logger

from ..core.config import get_settings


class TaskRepository:
    """
    Redis-backed repository for task management.
    """

    def __init__(self) -> None:
        """
        Initialize the repository with a Redis client.
        """
        settings = get_settings()
        self.redis: aioredis.Redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    async def create_task(self, task_id: str, session_id: str, status: str = "processing") -> None:
        """
        Store a new task record.

        Args:
            task_id: Unique identifier for the task.
            session_id: Associated session identifier.
            status: Initial status of the task.
        """
        await self.redis.hset(
            f"task:{task_id}:{session_id}",
            mapping={"status": status, "session_id": session_id},
        )

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve task information.

        Args:
            task_id: Unique identifier for the task.

        Returns:
            A dictionary with task fields or None if not found.
        """
        keys: List[str] = await self.redis.keys(f"task:{task_id}:*")
        if not keys:
            return None
        key = keys[0]
        data = await self.redis.hgetall(key)
        if "result" in data:
            try:
                data["result"] = json.loads(data["result"])
            except Exception as e:
                logger.error(f"Error parsing result for task {task_id}: {e}")
        return data

    async def update_result(self, task_id: str, session_id: str, result: Any) -> None:
        """
        Update task with the result of processing.

        Args:
            task_id: Unique identifier for the task.
            session_id: Associated session identifier.
            result: Result data to store.
        """
        try:
            await self.redis.hset(
                f"task:{task_id}:{session_id}",
                "result",
                json.dumps({"response": result}),
            )
            await self.redis.hset(
                f"task:{task_id}:{session_id}",
                "status",
                "completed",
            )
        except Exception as e:
            logger.error(f"Error updating result for task {task_id}: {e}")

    async def update_error(self, task_id: str, session_id: str, error: str) -> None:
        """
        Update task with an error message.

        Args:
            task_id: Unique identifier for the task.
            session_id: Associated session identifier.
            error: Error message to store.
        """
        try:
            await self.redis.hset(
                f"task:{task_id}:{session_id}",
                "error",
                error,
            )
            await self.redis.hset(
                f"task:{task_id}:{session_id}",
                "status",
                "failed",
            )
        except Exception as e:
            logger.error(f"Error updating error for task {task_id}: {e}")
