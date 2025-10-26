from functools import lru_cache

import redis.asyncio as aioredis

from ..repositories.session_repo import SessionRepository
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
def get_session_service() -> SessionService:
    """Get session service instance."""
    return SessionService(
        session_repo=get_session_repository(),
        settings=get_config_settings(),
    )
