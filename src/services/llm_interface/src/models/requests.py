from typing import Any, Dict

from pydantic import BaseModel, Field


class SessionRequest(BaseModel):
    """
    Request model for initializing a session.
    """

    role: str = Field(
        ...,
        description="Agent role to initialize the session",
        example="problem_solver",
    )


class InteractRequest(BaseModel):
    """
    Request model for interacting with an LLM session.
    """

    session_id: str = Field(
        ...,
        description="Unique identifier for the session",
        example="123e4567-e89b-12d3-a456-426614174000",
    )
    input_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Input data for the LLM, such as prompt and context",
        example={"concepts": ["recursion", "dynamic programming"], "difficulty_level": "medium"},
    )
    role: str = Field(
        default="challenge_designer",
        description="Role of the agent to interact with",
        example="challenge_designer",
    )
    use_agent: bool = Field(
        False,
        description="Whether to use an agent for more complex reasoning",
        example=False,
    )
