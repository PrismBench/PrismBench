from fastapi import APIRouter, status

from ....models.responses import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
    responses={200: {"description": "API is healthy"}},
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint to verify the API is operational.

    Returns:
        HealthResponse with service status and documentation links
    """
    return HealthResponse(
        message="PrismBench - Environment Service - Alive",
        documentation="/docs",
        redoc="/redoc",
        health="/health",
    )
