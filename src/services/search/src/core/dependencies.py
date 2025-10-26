from functools import lru_cache

from ..core.config import Settings, get_settings
from ..repositories import SessionRepository, TaskRepository
from ..services import MCTSService, SessionService, TaskService


# configuration dependencies
def get_config_settings() -> Settings:
    """
    Get application settings.
    """
    return get_settings()


# repository dependencies
@lru_cache()
def get_session_repository() -> SessionRepository:
    """
    Get session repository instance.
    """
    return SessionRepository()


@lru_cache()
def get_task_repository() -> TaskRepository:
    """
    Get task repository instance.
    """
    return TaskRepository()


# service dependencies
@lru_cache()
def get_session_service() -> SessionService:
    """
    Get session service instance.
    """
    return SessionService(
        session_repo=get_session_repository(),
        settings=get_config_settings(),
    )


@lru_cache()
def get_mcts_service() -> MCTSService:
    """
    Get MCTS service instance.
    """
    return MCTSService(
        settings=get_config_settings(),
    )


@lru_cache()
def get_task_service() -> TaskService:
    """
    Get task service instance.
    """
    return TaskService(
        task_repo=get_task_repository(),
        session_service=get_session_service(),
        mcts_service=get_mcts_service(),
        settings=get_config_settings(),
    )
