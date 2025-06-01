from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from ....core.dependencies import get_session_service
from ....core.exceptions import SearchServiceException, map_to_http_exception
from ....models.responses import TreeDataResponse
from ....services.session_service import SessionService

router = APIRouter(tags=["Tree"])


@router.get(
    "/tree/{session_id}",
    response_model=TreeDataResponse,
    summary="Get the current MCTS tree data for a session",
    responses={
        200: {"description": "Tree data successfully retrieved"},
        404: {"description": "Session ID not found"},
        500: {"description": "Error serializing tree data"},
    },
)
async def get_tree_data(
    session_id: str,
    session_service: SessionService = Depends(get_session_service),
) -> TreeDataResponse:
    """
    Retrieves the current state of the MCTS tree for the given session ID,
    serialized to a dictionary.

    Args:
        session_id: The session ID to retrieve tree data for

    Returns:
        TreeDataResponse with the tree structure and metadata
    """
    try:
        tree_dict = await session_service.get_session_tree_data(session_id)
        return TreeDataResponse(**tree_dict)
    except SearchServiceException as e:
        raise map_to_http_exception(e)
    except Exception as e:
        logger.exception(f"Error serializing tree for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error serializing tree data: {str(e)}")
