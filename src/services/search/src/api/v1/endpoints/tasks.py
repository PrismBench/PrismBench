from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from loguru import logger

from ....core.dependencies import get_task_service
from ....core.exceptions import SearchServiceException, map_to_http_exception
from ....models.requests import TaskCreateRequest
from ....models.responses import TaskResponse, TaskStatusResponse
from ....services.task_service import TaskService

router = APIRouter(tags=["Interaction"])


@router.post(
    "/run",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Run an MCTS cycle",
    responses={
        202: {"description": "Request accepted and being processed"},
        404: {"description": "Session not found"},
        500: {"description": "Server error during task creation"},
    },
)
async def run_mcts(
    request: Optional[TaskCreateRequest] = None,
    task_service: TaskService = Depends(get_task_service),
) -> JSONResponse:
    """
    Start MCTS execution asynchronously.

    This endpoint starts processing the request in the background and returns immediately
    with a task_id that can be used to check the status of the request.

    Args:
        request: Task creation request containing session_id and optional resume parameters

    Returns:
        TaskResponse with task_id for status tracking.
    """
    try:
        # Use provided session_id or generate a new one
        session_id = request.session_id if request else None
        if not session_id:
            from uuid import uuid4

            session_id = str(uuid4())

        # Extract resume parameters if provided
        resume_kwargs = {}
        if request and request.resume:
            resume_kwargs = {
                "resume": request.resume,
                "tree_pickle_path": request.tree_pickle_path,
                "resume_phase": request.resume_phase,
                "resume_iteration": request.resume_iteration,
            }

        task = await task_service.create_task(session_id, **resume_kwargs)

        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content=TaskResponse(
                task_id=task.task_id,
                session_id=task.session_id,
                message="Request is being processed asynchronously",
                phases={
                    phase_name: {
                        "status": phase.status,
                        "created_at": phase.created_at.isoformat() if phase.created_at else None,
                        "started_at": phase.started_at,
                        "completed_at": phase.completed_at,
                        "cancelled_at": phase.cancelled_at,
                        "error": phase.error,
                        "path": phase.path,
                    }
                    for phase_name, phase in task.phases.items()
                },
            ).model_dump(),
        )
    except SearchServiceException as e:
        raise map_to_http_exception(e)
    except Exception as e:
        logger.exception(f"Unexpected error creating task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/stop/{task_id}",
    response_model=TaskResponse,
    summary="Stop a running MCTS job",
    responses={
        200: {"description": "Task stopped successfully"},
        404: {"description": "Task not found"},
        400: {"description": "Task cannot be stopped (already completed or failed)"},
        500: {"description": "Server error during task cancellation"},
    },
)
async def stop_task(
    task_id: str,
    task_service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    """
    Stop a running MCTS task.

    This endpoint cancels the background task associated with the given task_id
    and updates the status of any running or pending phases to "cancelled".

    Args:
        task_id: The task ID to stop

    Returns:
        TaskResponse with the result of the stop operation and updated phase statuses.
    """
    try:
        task = await task_service.stop_task(task_id)
        return TaskResponse(
            task_id=task.task_id,
            session_id=task.session_id,
            message="Task cancelled successfully",
            phases={
                phase_name: {
                    "status": phase.status,
                    "created_at": phase.created_at.isoformat() if phase.created_at else None,
                    "started_at": phase.started_at,
                    "completed_at": phase.completed_at,
                    "cancelled_at": phase.cancelled_at,
                    "error": phase.error,
                    "path": phase.path,
                }
                for phase_name, phase in task.phases.items()
            },
        )
    except SearchServiceException as e:
        raise map_to_http_exception(e)
    except Exception as e:
        logger.exception(f"Unexpected error stopping task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/status",
    response_model=TaskStatusResponse,
    summary="Get the status of all tasks",
    responses={
        200: {"description": "Task status retrieved successfully"},
        500: {"description": "Server error during status retrieval"},
    },
)
async def get_status(
    task_service: TaskService = Depends(get_task_service),
) -> TaskStatusResponse:
    """
    Get the status of all tasks.

    Returns:
        TaskStatusResponse with the status of all tasks.
    """
    try:
        status_report = await task_service.get_task_status_report()

        if "message" in status_report:
            # No tasks to report
            return TaskStatusResponse(message=status_report["message"])
        else:
            # Return task statuses
            return TaskStatusResponse(tasks=status_report)

    except Exception as e:
        logger.exception(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Get specific task status",
    responses={
        200: {"description": "Task status retrieved successfully"},
        404: {"description": "Task not found"},
        500: {"description": "Server error during status retrieval"},
    },
)
async def get_task_status(
    task_id: str,
    task_service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    """
    Get the status of a specific task.

    Args:
        task_id: The ID of the task to get the status of.

    Returns:
        TaskResponse with the status of the task.
    """
    try:
        task = await task_service.get_task(task_id)
        return TaskResponse(
            task_id=task.task_id,
            session_id=task.session_id,
            message=f"Task status: {task.status.value}",
            phases={
                phase_name: {
                    "status": phase.status,
                    "created_at": phase.created_at.isoformat() if phase.created_at else None,
                    "started_at": phase.started_at,
                    "completed_at": phase.completed_at,
                    "cancelled_at": phase.cancelled_at,
                    "error": phase.error,
                    "path": phase.path,
                }
                for phase_name, phase in task.phases.items()
            },
        )
    except SearchServiceException as e:
        raise map_to_http_exception(e)
    except Exception as e:
        logger.exception(f"Error getting task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
