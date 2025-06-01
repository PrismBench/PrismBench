from fastapi import HTTPException, status


class LLMInterfaceException(Exception):
    """Base exception for LLM Interface service."""

    pass


class SessionNotFoundException(LLMInterfaceException):
    """Raised when a session is not found."""

    pass


class TaskNotFoundException(LLMInterfaceException):
    """Raised when a task is not found."""

    pass


class SessionAlreadyExistsException(LLMInterfaceException):
    """Raised when attempting to create a session that already exists."""

    pass


class TaskExecutionException(LLMInterfaceException):
    """Raised when task execution fails."""

    pass


def map_to_http_exception(exc: LLMInterfaceException) -> HTTPException:
    """Map custom exceptions to FastAPI HTTPExceptions."""
    mapping = {
        SessionNotFoundException: (
            status.HTTP_404_NOT_FOUND,
            "Session not found",
        ),
        TaskNotFoundException: (
            status.HTTP_404_NOT_FOUND,
            "Task not found",
        ),
        SessionAlreadyExistsException: (
            status.HTTP_409_CONFLICT,
            "Session already exists",
        ),
        TaskExecutionException: (
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Task execution failed",
        ),
    }
    status_code, detail = mapping.get(
        type(exc),
        (status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)),
    )
    return HTTPException(status_code=status_code, detail=detail)
