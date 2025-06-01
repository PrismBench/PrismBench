from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Session(BaseModel):
    """
    Domain model representing a session.
    """

    session_id: str
    role: str


class Task(BaseModel):
    """
    Domain model representing a task.
    """

    task_id: str
    session_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class HistoryItem(BaseModel):
    """
    Domain model for a conversation history entry.
    """

    role: str
    content: str


History = List[HistoryItem]
