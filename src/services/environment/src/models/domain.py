from pydantic import BaseModel, Field


class ChallengeDataTrail(BaseModel):
    """Domain model for the challenge data trail."""

    problem_statement: str | None = Field(
        default=None,
        description="Problem statement for the challenge",
    )
    test_cases: str | None = Field(
        default=None,
        description="Test cases for the challenge",
    )
    solution_code: str | None = Field(
        default=None,
        description="Solution code for the challenge",
    )
    success: bool = Field(
        default=False,
        description="Whether the solution was successful",
    )
    output: str | None = Field(
        default=None,
        description="Output of the solution",
    )
    tests_passed_num: int = Field(
        default=0,
        description="Number of tests passed",
    )
    tests_failed_num: int = Field(
        default=0,
        description="Number of tests failed",
    )
    tests_errored_num: int = Field(
        default=0,
        description="Number of tests that errored",
    )
    fixed_by_problem_fixer: bool = Field(
        default=False,
        description="Whether the problem fixer fixed the solution",
    )
    attempt_num: int = Field(
        default=0,
        description="Attempt number",
    )
    error_feedback: str | None = Field(
        default=None,
        description="Feedback regarding errors encountered",
    )
    test_validation: str | None = Field(
        default=None,
        description="Test validation report",
    )
    test_error_analysis: str | None = Field(
        default=None,
        description="Test error analysis report",
    )
