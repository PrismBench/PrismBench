from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from ....core.dependencies import get_session_service
from ....core.exceptions import SessionNotFoundException, map_to_http_exception
from ....models.responses import DeleteSessionResponse
from ....services.session_service import SessionService

router = APIRouter(tags=["Session"])


@router.delete(
    "/session/{session_id}",
    response_model=DeleteSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a session",
    responses={
        200: {"description": "Session deleted successfully"},
        404: {"description": "Session not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_session(
    session_id: str,
    session_service: SessionService = Depends(get_session_service),
) -> DeleteSessionResponse:
    """
    Delete an existing session and associated data.
    """
    try:
        await session_service.delete_session(session_id)
        return DeleteSessionResponse(message=f"Session {session_id} deleted")
    except SessionNotFoundException as e:
        raise map_to_http_exception(e)
    except Exception as e:
        logger.exception(f"Unexpected error deleting session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
