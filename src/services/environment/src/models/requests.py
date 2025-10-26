from typing import List, Optional

from pydantic import BaseModel, Field


class ChallengeRequest(BaseModel):
    """Request model for running a coding challenge."""

    concept: str | List[str] = Field(
        ...,
        description="The programming concept to test. Can be a single concept or a list of concepts.",
    )
    difficulty_level: str = Field(
        ...,
        description="The difficulty level of the challenge.",
    )
    max_attempts: Optional[int] = Field(
        default=None,
        description="Maximum solution attempts allowed per problem. If not provided, uses environment default.",
    )
    previous_problems: Optional[List[str]] = Field(
        default=None,
        description="List of previous problems to provide context or avoid repetition. If not provided, no previous problems are considered.",
    )
