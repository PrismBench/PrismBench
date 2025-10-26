from functools import lru_cache

from ..services.environment_service import EnvironmentService
from .config import Settings, get_settings


# Configuration dependencies
def get_config_settings() -> Settings:
    """Get application settings."""
    return get_settings()


# Service dependencies
@lru_cache()
def get_environment_service() -> EnvironmentService:
    """Get environment service instance."""
    settings = get_config_settings()
    return EnvironmentService(settings=settings)
