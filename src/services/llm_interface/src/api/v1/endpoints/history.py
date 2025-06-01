from fastapi import APIRouter, Depends, HTTPException, status

from ....core.dependencies import get_interaction_service
from ....core.exceptions import SessionNotFoundException
from ....models.responses import ClearMemoryResponse, HistoryResponse

router = APIRouter(tags=["History"])


@router.get(
    "/conversation_history/{session_id}",
    response_model=HistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the conversation history for a session",
)
async def get_conversation_history(
    session_id: str,
    interaction_service=Depends(get_interaction_service),
) -> HistoryResponse:
    """
    Retrieve the conversation history for a given session.
    """
    try:
        history = await interaction_service.get_history(session_id)
        return HistoryResponse(session_id=session_id, history=history)
    except SessionNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/clear_memory/{session_id}",
    response_model=ClearMemoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Clear the conversation history for a session",
)
async def clear_memory(
    session_id: str,
    interaction_service=Depends(get_interaction_service),
) -> ClearMemoryResponse:
    """
    Clear the conversation history for a given session.
    """
    try:
        await interaction_service.clear_memory(session_id)
        return ClearMemoryResponse(message="Conversation history cleared")
    except SessionNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
