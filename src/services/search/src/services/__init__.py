from abc import ABC

from .mcts_service import MCTSService
from .session_service import SessionService
from .task_service import TaskService


class BaseService(ABC):
    """Abstract base service interface."""

    pass


__all__ = [
    "BaseService",
    "SessionService",
    "TaskService",
    "MCTSService",
]
