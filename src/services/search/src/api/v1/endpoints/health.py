from fastapi import APIRouter, status

from ....models.responses import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
    responses={
        200: {"description": "Service is healthy"},
    },
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint for Docker and monitoring.

    Returns:
        HealthResponse with service status
    """
    return HealthResponse(status="healthy", service="search")
