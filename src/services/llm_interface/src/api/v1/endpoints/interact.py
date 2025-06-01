from fastapi import APIRouter, Depends, HTTPException, status

from ....core.dependencies import get_interaction_service
from ....core.exceptions import SessionNotFoundException
from ....models.requests import InteractRequest
from ....models.responses import InteractResponse

router = APIRouter(tags=["Interaction"])


@router.post(
    "/interact",
    response_model=InteractResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Interact with the LLM asynchronously",
)
async def interact(
    request: InteractRequest,
    interaction_service=Depends(get_interaction_service),
) -> InteractResponse:
    """
    Submit an interaction request to the LLM asynchronously.
    """
    try:
        task_id = await interaction_service.submit_interact(
            request.session_id, request.input_data, request.use_agent
        )
        return InteractResponse(
            message="Request is being processed asynchronously",
            task_id=task_id,
            session_id=request.session_id,
        )
    except SessionNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
