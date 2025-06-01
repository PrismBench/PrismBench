from typing import List

from pydantic import BaseModel, Field

from .domain import ChallengeDataTrail


class ChallengeResults(BaseModel):
    """Response model for challenge execution results."""

    success: bool = Field(
        default=False,
        description="Whether the challenge was successful",
    )
    data_trail: List[ChallengeDataTrail] = Field(
        default_factory=list,
        description="List of challenge data trails",
    )


class HealthResponse(BaseModel):
    """Response model for health check."""

    message: str = Field(
        ...,
        description="Health status message",
    )
    documentation: str = Field(
        ...,
        description="Link to API documentation",
    )
    redoc: str = Field(
        ...,
        description="Link to ReDoc documentation",
    )
    health: str = Field(
        ...,
        description="Link to health endpoint",
    )
