from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger

from ....core.dependencies import get_environment_service
from ....core.exceptions import EnvironmentServiceException, map_to_http_exception
from ....models.requests import ChallengeRequest
from ....models.responses import ChallengeResults
from ....services.environment_service import EnvironmentService

router = APIRouter(tags=["Environment"])


@router.post(
    "/run-challenge",
    response_model=ChallengeResults,
    status_code=status.HTTP_200_OK,
    summary="Run a coding challenge",
    description="""
    Executes a coding challenge using the specified environment. Available environments:
    - environment_coding_challenge: Standard coding challenge with basic agents
    - environment_enhanced_coding_challenge: Enhanced challenge with additional validation and multiple problems
    
    The environment determines which agents are used and the default parameters for the challenge.
    """,
    responses={
        200: {
            "description": "Challenge executed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data_trail": [
                            {
                                "attempt_num": 0,
                                "problem_statement": "Write a function that...",
                                "test_cases": "def test_solution()...",
                                "solution_code": "def solution()...",
                                "tests_passed_num": 5,
                                "tests_failed_num": 0,
                                "tests_errored_num": 0,
                                "success": True,
                                "output": "All tests passed.",
                            }
                        ],
                    }
                }
            },
        },
        500: {
            "description": "Error running the challenge",
            "content": {"application/json": {"example": {"detail": "Error message describing the issue"}}},
        },
    },
)
async def run_challenge(
    request: ChallengeRequest,
    environment_name: Optional[str] = Query(
        default="environment_coding_challenge", description="Name of the environment to use for the challenge"
    ),
    environment_service: EnvironmentService = Depends(get_environment_service),
) -> Dict:
    """
    Run a coding challenge with the specified parameters.

    This endpoint processes a coding challenge request and returns the results. The environment
    determines which agents are used and the default parameters (max_attempts, timeout, num_problems).

    Args:
        request: The challenge request parameters including:
            - concept: The programming concept to test
            - difficulty_level: The difficulty level (easy, medium, hard)
            - max_attempts: Maximum solution attempts (optional, uses environment default if not provided)
        environment_name: Name of the environment to use (defaults to standard coding challenge)
        environment_service: Environment service dependency

    Returns:
        Dict: The results of running the challenge, including all attempts and test outcomes
    """
    try:
        results = await environment_service.run_challenge(environment_name, request)
        return results

    except EnvironmentServiceException as e:
        raise map_to_http_exception(e)
    except Exception as e:
        logger.exception(f"Unexpected error running challenge: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
