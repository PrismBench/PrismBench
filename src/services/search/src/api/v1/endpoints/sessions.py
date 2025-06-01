from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from ....core.dependencies import get_session_service
from ....core.exceptions import SearchServiceException, map_to_http_exception
from ....models.requests import SessionRequest
from ....models.responses import SessionResponse
from ....services.session_service import SessionService

router = APIRouter(tags=["Session"])


@router.post(
    "/initialize",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Initialize a new search tree",
    responses={
        200: {"description": "Tree initialized successfully"},
        409: {"description": "Session already exists"},
        500: {"description": "Server error during initialization"},
    },
)
async def initialize_session(
    request: SessionRequest,
    session_service: SessionService = Depends(get_session_service),
) -> SessionResponse:
    """
    Initialize a new tree with the specified session ID.

    If the session already exists, returns the tree for that session.

    Args:
        request: Session request containing the session_id

    Returns:
        SessionResponse with initialization status and tree information.
    """
    try:
        session = await session_service.get_or_create_session(request.session_id)
        return SessionResponse(
            session_id=session.session_id,
            message="Session initialized successfully",
            tree_size=len(session.tree.nodes),
        )
    except SearchServiceException as e:
        raise map_to_http_exception(e)
    except Exception as e:
        logger.exception(f"Unexpected error initializing session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/sessions/{session_id}",
    response_model=SessionResponse,
    summary="Get session information",
    responses={
        200: {"description": "Session information retrieved successfully"},
        404: {"description": "Session not found"},
        500: {"description": "Server error"},
    },
)
async def get_session(
    session_id: str,
    session_service: SessionService = Depends(get_session_service),
) -> SessionResponse:
    """Get information about a specific session.

    Args:
        session_id: The ID of the session to get information about.

    Returns:
        SessionResponse with session information.
    """
    try:
        session = await session_service.get_session(session_id)
        return SessionResponse(
            session_id=session.session_id,
            message="Session found",
            tree_size=len(session.tree.nodes),
        )
    except SearchServiceException as e:
        raise map_to_http_exception(e)
    except Exception as e:
        logger.exception(f"Unexpected error getting session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
