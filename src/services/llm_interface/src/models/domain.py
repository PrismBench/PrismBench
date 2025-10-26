from typing import Any, Dict, List

from pydantic import BaseModel, Field


class Session(BaseModel):
    """
    Domain model representing a session.

    Attributes:
        session_id: The unique identifier for the session.
        roles: List of roles in the session.
    """

    session_id: str = Field(description="The unique identifier for the session.")
    roles: List[str] = Field(default=[], description="List of roles in the session.")


class RoleHistory(BaseModel):
    """
    Domain model representing the history of a role.

    Attributes:
        role: The role of the history.
        history: The history of the role.
    """

    role: str = Field(description="The role of the history.")
    history: List[Dict[str, Any]] = Field(default=[], description="The history of the role.")
