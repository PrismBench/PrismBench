from functools import lru_cache

import redis.asyncio as aioredis

from ..repositories.session_repo import SessionRepository
from ..repositories.task_repo import TaskRepository
from ..services.interaction_service import InteractionService
from ..services.session_service import SessionService
from .config import Settings, get_settings


def get_config_settings() -> Settings:
    """Get the application settings."""
    return get_settings()


@lru_cache()
def get_redis_client() -> aioredis.Redis:
    """Get Redis client instance."""
    settings: Settings = get_config_settings()
    return aioredis.from_url(settings.REDIS_URL, decode_responses=True)


@lru_cache()
def get_session_repository() -> SessionRepository:
    """Get session repository instance."""
    return SessionRepository()


@lru_cache()
def get_task_repository() -> TaskRepository:
    """Get task repository instance."""
    return TaskRepository()


@lru_cache()
def get_session_service() -> SessionService:
    """Get session service instance."""
    return SessionService(
        session_repo=get_session_repository(),
        settings=get_config_settings(),
    )


@lru_cache()
def get_interaction_service() -> InteractionService:
    """Get interaction service instance."""
    return InteractionService(
        session_service=get_session_service(),
        task_repo=get_task_repository(),
        settings=get_config_settings(),
    )
