from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


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
        example="Request is being processed asynchronously",
    )
    task_id: str = Field(
        ...,
        description="Identifier for the asynchronous task",
        example="123e4567-e89b-12d3-a456-426614174001",
    )
    session_id: str = Field(
        ...,
        description="Identifier of the session",
        example="123e4567-e89b-12d3-a456-426614174000",
    )


class TaskStatusResponse(BaseModel):
    """
    Response model for task status endpoint.
    """

    status: str = Field(
        ...,
        description="Status of the task (processing, completed, failed)",
        example="completed",
    )
    result: Optional[Dict[str, Any]] = Field(
        None,
        description="Result returned by the LLM",
        example={"response": "Paris is the capital of France."},
    )
    error: Optional[str] = Field(
        None,
        description="Error message if the task failed",
        example=None,
    )


class HistoryResponse(BaseModel):
    """
    Response model for conversation history endpoint.
    """

    session_id: str = Field(
        ...,
        description="Identifier of the session",
        example="123e4567-e89b-12d3-a456-426614174000",
    )
    history: List[Dict[str, Any]] = Field(
        ...,
        description="List of conversation history entries",
        example=[
            {"role": "human", "content": "What is the capital of France?"},
            {"role": "ai", "content": "Paris is the capital of France."},
        ],
    )


class ClearMemoryResponse(BaseModel):
    """
    Response model for clear memory endpoint.
    """

    message: str = Field(
        ...,
        description="Result message of the operation",
        example="Conversation history cleared",
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
