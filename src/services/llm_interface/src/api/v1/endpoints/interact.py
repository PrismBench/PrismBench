from fastapi import APIRouter, Depends, HTTPException, status

from ....core.dependencies import get_session_service
from ....core.exceptions import SessionNotFoundException
from ....models.requests import InteractRequest
from ....models.responses import InteractResponse

router = APIRouter(tags=["Interaction"])


@router.post(
    "/interact",
    response_model=InteractResponse,
    status_code=status.HTTP_200_OK,
    summary="Interact with the LLM asynchronously",
    responses={
        200: {"description": "Interact with the LLM asynchronously"},
        404: {"description": "Session not found"},
        500: {"description": "Internal server error"},
    },
)
async def interact(
    request: InteractRequest,
    session_service=Depends(get_session_service),
) -> InteractResponse:
    """
    Submit an interaction request to the LLM asynchronously.
    """
    try:
        response = await session_service.submit_interact(
            request.session_id,
            request.role,
            request.input_data,
            request.use_agent,
        )
        return InteractResponse(
            message=response,
            session_id=request.session_id,
        )
    except SessionNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
