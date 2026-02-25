"""Business logic layer for task operations."""

import logging
import uuid
from datetime import datetime, timezone

from app.core.exceptions import NotFoundException
from app.models.task import Task
from app.repositories.task import TaskRepository
from app.schemas.task import PaginatedTaskResponse, TaskCreate, TaskResponse, TaskUpdate

logger = logging.getLogger(__name__)


class TaskService:
    """Orchestrates task CRUD operations between the router and repository layers.

    Args:
        repository: The data access object for tasks.
    """

    def __init__(self, repository: TaskRepository):
        self._repository = repository

    async def create_task(self, payload: TaskCreate) -> TaskResponse:
        """Create a new task.

        Args:
            payload: Validated creation data.

        Returns:
            The newly created task.
        """
        task = Task(
            title=payload.title,
            description=payload.description,
            status=payload.status.value,
        )
        created = await self._repository.create(task)
        logger.info("Task created id=%s", created.id)
        return TaskResponse.model_validate(created)

    async def get_task(self, task_id: uuid.UUID) -> TaskResponse:
        """Retrieve a single task by ID.

        Args:
            task_id: UUID of the task.

        Returns:
            The matching task.

        Raises:
            NotFoundException: If the task does not exist or is soft-deleted.
        """
        task = await self._repository.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task", str(task_id))
        return TaskResponse.model_validate(task)

    async def list_tasks(self, limit: int, offset: int) -> PaginatedTaskResponse:
        """Return a paginated list of tasks.

        Args:
            limit: Maximum number of tasks to return.
            offset: Number of tasks to skip.

        Returns:
            Paginated response containing tasks and total count.
        """
        items, total = await self._repository.list(limit=limit, offset=offset)
        return PaginatedTaskResponse(
            items=[TaskResponse.model_validate(t) for t in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def update_task(self, task_id: uuid.UUID, payload: TaskUpdate) -> TaskResponse:
        """Update an existing task with the provided fields.

        If no fields are provided, returns the current task unchanged.

        Args:
            task_id: UUID of the task to update.
            payload: Validated update data (only set fields are applied).

        Returns:
            The updated task.

        Raises:
            NotFoundException: If the task does not exist or is soft-deleted.
        """
        data = payload.model_dump(exclude_unset=True)
        if not data:
            return await self.get_task(task_id)

        data["updated_at"] = datetime.now(timezone.utc)

        task = await self._repository.update(task_id, data)
        if not task:
            raise NotFoundException("Task", str(task_id))
        logger.info("Task updated id=%s", task_id)
        return TaskResponse.model_validate(task)

    async def delete_task(self, task_id: uuid.UUID) -> None:
        """Soft-delete a task.

        Args:
            task_id: UUID of the task to delete.

        Raises:
            NotFoundException: If the task does not exist or is already deleted.
        """
        deleted = await self._repository.soft_delete(task_id)
        if not deleted:
            raise NotFoundException("Task", str(task_id))
        logger.info("Task soft-deleted id=%s", task_id)
