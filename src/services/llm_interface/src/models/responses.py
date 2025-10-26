from typing import Dict

from pydantic import BaseModel, Field

from .domain import RoleHistory


class HealthResponse(BaseModel):
    """
    Response model for health check endpoint.
    """

    status: str = Field(
        ...,
        description="Service status",
        example="healthy",
    )
    service: str = Field(
        ...,
        description="Service name",
        example="llm_interface",
    )


class SessionResponse(BaseModel):
    """
    Response model for session initialization and deletion.
    """

    message: str = Field(
        ...,
        description="Result message of the operation",
        example="Session initialized successfully",
    )
    session_id: str = Field(
        ...,
        description="Identifier of the session",
        example="123e4567-e89b-12d3-a456-426614174000",
    )


class InteractResponse(BaseModel):
    """
    Response model for interaction requests.
    """

    message: str = Field(
        ...,
        description="Result message of the operation",
        example="I am a large language model",
    )

    session_id: str = Field(
        ...,
        description="Identifier of the session",
        example="123e4567-e89b-12d3-a456-426614174000",
    )


class HistoryResponse(BaseModel):
    """
    Response model for session history endpoint.
    """

    session_id: str = Field(
        ...,
        description="Identifier of the session",
        example="123e4567-e89b-12d3-a456-426614174000",
    )
    history: Dict[str, RoleHistory] = Field(
        ...,
        description="List of session history entries",
        example={
            "challenge_designer": {
                "role": "challenge_designer",
                "history": [
                    {"role": "human", "content": "What is the capital of France?"},
                    {"role": "ai", "content": "Paris is the capital of France."},
                ],
            },
            "challenge_solver": {
                "role": "challenge_solver",
                "history": [
                    {"role": "human", "content": "What is the capital of France?"},
                    {"role": "ai", "content": "Paris is the capital of France."},
                ],
            },
        },
    )


class DeleteSessionResponse(BaseModel):
    """
    Response model for delete session endpoint.
    """

    message: str = Field(
        ...,
        description="Result message of the operation",
        example="Session 123e4567-e89b-12d3-a456-426614174000 deleted",
    )
