"""Application-level exception hierarchy for structured HTTP error responses."""

from typing import Any


class AppException(Exception):
    """Base exception that maps to an HTTP error response.

    Args:
        status_code: HTTP status code to return.
        detail: Human-readable error message.
        errors: Optional list of structured error details.
    """

    def __init__(self, status_code: int, detail: str, errors: list[Any] | None = None):
        self.status_code = status_code
        self.detail = detail
        self.errors = errors or []
        super().__init__(detail)


class NotFoundException(AppException):
    """Raised when a requested resource does not exist.

    Args:
        resource: Name of the resource type (e.g. "Task").
        resource_id: Identifier of the missing resource.
    """

    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            status_code=404,
            detail=f"{resource} with id '{resource_id}' not found",
        )


class BadRequestException(AppException):
    """Raised when the client sends an invalid request.

    Args:
        detail: Human-readable error message.
        errors: Optional list of structured validation errors.
    """

    def __init__(self, detail: str, errors: list[Any] | None = None):
        super().__init__(status_code=400, detail=detail, errors=errors)
