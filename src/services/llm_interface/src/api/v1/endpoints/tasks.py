from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from ....core.dependencies import get_interaction_service
from ....core.exceptions import TaskNotFoundException, map_to_http_exception
from ....models.responses import TaskStatusResponse
from ....services.interaction_service import InteractionService

router = APIRouter(tags=["Interaction"])


@router.get(
    "/task_status/{task_id}",
    response_model=TaskStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the status of an asynchronous task",
    responses={
        200: {"description": "Task status retrieved successfully"},
        404: {"description": "Task not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_task_status(
    task_id: str,
    interaction_service: InteractionService = Depends(get_interaction_service),
) -> TaskStatusResponse:
    """
    Retrieve the status and result of an asynchronous LLM interaction task.
    """
    try:
        task = await interaction_service.get_task_status(task_id)
        return TaskStatusResponse(
            status=task.get("status"),
            result=task.get("result"),
            error=task.get("error"),
        )
    except TaskNotFoundException as e:
        raise map_to_http_exception(e)
    except Exception as e:
        logger.exception(f"Unexpected error getting task status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
