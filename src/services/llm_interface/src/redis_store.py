import json
import os
from typing import Any, Dict, Optional

import redis.asyncio as redis
from loguru import logger

from .llm.interface import LLMInterface

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
_redis = None


async def get_redis():
    """
    Get or create Redis connection.
    This function returns a Redis connection. If the connection is not already created, it will create a new one.
    """
    global _redis
    if _redis is None:
        logger.info(f"Connecting to Redis at {REDIS_URL}")
        _redis = redis.from_url(REDIS_URL, decode_responses=True)

    return _redis


async def store_session(
    session_id: str,
    role: str,
    llm_instance: LLMInterface = None,
) -> None:
    """
    Store session information and conversation history in Redis.

    Args:
        session_id: The session ID
        role: The role for this session
        llm_instance: Optional LLMInterface instance to extract history from
    """
    redis_conn = await get_redis()

    await redis_conn.hset(
        f"session:{session_id}",
        mapping={"role": role},
    )

    try:
        history = llm_instance.get_conversation_history()
        await redis_conn.set(f"history:{session_id}", json.dumps(history))
        logger.debug(f"Stored conversation history for session {session_id}")
    except Exception as e:
        logger.error(f"Error storing conversation history: {e}")

    logger.debug(f"Stored session {session_id} in Redis")


async def get_session(session_id: str) -> Optional[Dict[str, str]]:
    """
    Retrieve session information from Redis.

    Args:
        session_id(str): The session ID

    Returns:
        Optional[Dict[str, str]]: Session information
    """
    redis_conn = await get_redis()
    session = await redis_conn.hgetall(f"session:{session_id}")

    if not session:
        return None

    return session


async def delete_session(session_id: str) -> None:
    """
    Delete a session and its data from Redis.

    Args:
        session_id(str): The session ID
    """
    redis_conn = await get_redis()

    keys_to_delete = [
        f"session:{session_id}",
        f"history:{session_id}",
    ]

    # Find and delete tasks
    task_keys = await redis_conn.keys(f"task:*:{session_id}")
    if task_keys:
        keys_to_delete.extend(task_keys)

    if keys_to_delete:
        await redis_conn.delete(*keys_to_delete)

    logger.debug(f"Deleted session {session_id} from Redis")


async def get_conversation_history(session_id: str) -> list:
    """
    Retrieve conversation history from Redis.

    Args:
        session_id(str): The session ID

    Returns:
        list: Conversation history
    """
    redis_conn = await get_redis()
    history_json = await redis_conn.get(f"history:{session_id}")

    if not history_json:
        return []

    try:
        return json.loads(history_json)
    except Exception as e:
        logger.error(f"Error parsing conversation history: {e}")
        return []


async def update_conversation_history(session_id: str, history: list) -> None:
    """
    Update conversation history in Redis.

    Args:
        session_id(str): The session ID
        history(list): The conversation history
    """
    redis_conn = await get_redis()
    try:
        await redis_conn.set(f"history:{session_id}", json.dumps(history))
        logger.debug(f"Updated conversation history for session {session_id}")
    except Exception as e:
        logger.error(f"Error updating conversation history: {e}")


async def store_task(
    task_id: str,
    session_id: str,
    status: str = "processing",
) -> None:
    """Store task information in Redis.

    Args:
        task_id(str): The task ID
        session_id(str): The session ID
    """
    redis_conn = await get_redis()
    await redis_conn.hset(
        f"task:{task_id}:{session_id}",
        mapping={
            "status": status,
            "session_id": session_id,
        },
    )


async def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve task information from Redis.

    Args:
        task_id(str): The task ID

    Returns:
        Optional[Dict[str, Any]]: Task information
    """
    redis_conn = await get_redis()
    keys = await redis_conn.keys(f"task:{task_id}:*")
    if not keys:
        return None

    task_key = keys[0]
    task = await redis_conn.hgetall(task_key)

    if "result" in task:
        task["result"] = json.loads(task["result"])

    return task


async def update_task_result(task_id: str, session_id: str, result: Any) -> None:
    """
    Update task with result.

    Args:
        task_id(str): The task ID
        session_id(str): The session ID
        result(Any): The result
    """
    redis_conn = await get_redis()
    await redis_conn.hset(
        f"task:{task_id}:{session_id}",
        "result",
        json.dumps({"response": result}),
    )
    await redis_conn.hset(
        f"task:{task_id}:{session_id}",
        "status",
        "completed",
    )


async def update_task_error(task_id: str, session_id: str, error: str) -> None:
    """
    Update task with error.

    Args:
        task_id(str): The task ID
        session_id(str): The session ID
        error(str): The error
    """
    redis_conn = await get_redis()
    await redis_conn.hset(
        f"task:{task_id}:{session_id}",
        "error",
        error,
    )
    await redis_conn.hset(
        f"task:{task_id}:{session_id}",
        "status",
        "failed",
    )


async def cleanup():
    """Close Redis connection when shutting down.

    This function closes the Redis connection when the application shuts down.
    """
    global _redis

    if _redis is not None:
        await _redis.close()
        _redis = None

    logger.info("Redis connection closed")
