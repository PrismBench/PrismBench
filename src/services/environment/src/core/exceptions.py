from fastapi import HTTPException, status


class EnvironmentServiceException(Exception):
    """Base exception for environment service."""

    pass


class EnvironmentExecutionException(EnvironmentServiceException):
    """Raised when environment execution fails."""

    pass


class ConfigurationException(EnvironmentServiceException):
    """Raised when configuration is invalid."""

    pass


class ValidationException(EnvironmentServiceException):
    """Raised when validation fails."""

    pass


def map_to_http_exception(exc: EnvironmentServiceException) -> HTTPException:
    """
    Map custom exceptions to HTTP exceptions.

    Args:
        exc: The custom exception to map

    Returns:
        HTTPException with appropriate status code and detail
    """
    mapping = {
        EnvironmentExecutionException: (
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Environment execution failed",
        ),
        ConfigurationException: (
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Configuration error",
        ),
        ValidationException: (
            status.HTTP_400_BAD_REQUEST,
            "Validation error",
        ),
    }

    status_code, detail = mapping.get(type(exc), (status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)))
    return HTTPException(status_code=status_code, detail=detail)
