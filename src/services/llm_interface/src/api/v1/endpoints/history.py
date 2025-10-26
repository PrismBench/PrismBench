from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from ....core.dependencies import get_session_service
from ....core.exceptions import SessionNotFoundException
from ....models.responses import HistoryResponse
from ....services.session_service import SessionService

router = APIRouter(tags=["History"])


@router.get(
    "/active_sessions",
    response_model=dict[str, dict],
    status_code=status.HTTP_200_OK,
    summary="Get all active sessions",
    responses={
        200: {"description": "Active sessions retrieved successfully"},
        500: {"description": "Internal server error"},
    },
)
async def get_active_sessions(
    session_service: SessionService = Depends(get_session_service),
) -> dict[str, dict]:
    """
    Get all active sessions.
    """
    return await session_service.get_active_sessions()


@router.get(
    "/session_history/{session_id}",
    response_model=HistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the history for a session",
    responses={
        200: {"description": "Session history retrieved successfully"},
        404: {"description": "Session not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_session_history(
    session_id: str,
    session_service: SessionService = Depends(get_session_service),
) -> HistoryResponse:
    """
    Retrieve the conversation history for a given session.
    """
    try:
        session_history = await session_service.get_session_history(session_id)

        return HistoryResponse(
            session_id=session_id,
            history=session_history,
        )
    except SessionNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error getting session history: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
