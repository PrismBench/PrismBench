from fastapi import HTTPException, status


class SearchServiceException(Exception):
    """
    Base exception for search service.
    """

    pass


class SessionNotFoundException(SearchServiceException):
    """
    Raised when session is not found.
    """

    pass


class TaskNotFoundException(SearchServiceException):
    """
    Raised when task is not found.
    """

    pass


class SessionAlreadyExistsException(SearchServiceException):
    """
    Raised when trying to create existing session.
    """

    pass


class TaskExecutionException(SearchServiceException):
    """
    Raised when task execution fails.
    """

    pass


class TreeInitializationException(SearchServiceException):
    """
    Raised when tree initialization fails.
    """

    pass


class ConfigurationException(SearchServiceException):
    """
    Raised when configuration is invalid.
    """

    pass


class MCTSExecutionException(SearchServiceException):
    """
    Raised when MCTS execution encounters an error.
    """

    pass


def map_to_http_exception(exc: SearchServiceException) -> HTTPException:
    """
    Map custom exceptions to HTTP exceptions.

    Args:
        exc: The custom exception to map

    Returns:
        HTTPException with appropriate status code and detail
    """
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
        TreeInitializationException: (
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Tree initialization failed",
        ),
        ConfigurationException: (
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Configuration error",
        ),
        MCTSExecutionException: (
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "MCTS execution failed",
        ),
    }

    status_code, detail = mapping.get(type(exc), (status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)))
    return HTTPException(status_code=status_code, detail=detail)
