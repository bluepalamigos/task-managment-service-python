"""Pydantic schemas for task API request/response validation."""

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(str, Enum):
    """Allowed lifecycle states for a task."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class TaskCreate(BaseModel):
    """Request body for creating a new task.

    Attributes:
        title: Task title (1-255 characters, required).
        description: Optional longer description.
        status: Initial status, defaults to PENDING.
    """

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus = TaskStatus.PENDING


class TaskUpdate(BaseModel):
    """Request body for updating an existing task.

    All fields are optional; only provided fields are updated.

    Attributes:
        title: New title (1-255 characters).
        description: New description.
        status: New status.
    """

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None


class TaskResponse(BaseModel):
    """Response body representing a single task.

    Attributes:
        id: Task UUID.
        title: Task title.
        description: Task description, may be ``None``.
        status: Current lifecycle state.
        created_at: UTC timestamp of creation.
        updated_at: UTC timestamp of last update.
    """

    id: uuid.UUID
    title: str
    description: str | None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedTaskResponse(BaseModel):
    """Paginated list response for tasks.

    Attributes:
        items: List of tasks for the current page.
        total: Total number of non-deleted tasks.
        limit: Maximum items per page.
        offset: Number of items skipped.
    """

    items: list[TaskResponse]
    total: int
    limit: int
    offset: int


class ErrorResponse(BaseModel):
    """Standard error response body.

    Attributes:
        detail: Human-readable error message.
        errors: Optional list of structured error details.
    """

    detail: str
    errors: list | None = None
