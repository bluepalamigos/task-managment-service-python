from typing import Any


class AppException(Exception):
    def __init__(self, status_code: int, detail: str, errors: list[Any] | None = None):
        self.status_code = status_code
        self.detail = detail
        self.errors = errors or []
        super().__init__(detail)


class NotFoundException(AppException):
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            status_code=404,
            detail=f"{resource} with id '{resource_id}' not found",
        )


class BadRequestException(AppException):
    def __init__(self, detail: str, errors: list[Any] | None = None):
        super().__init__(status_code=400, detail=detail, errors=errors)
