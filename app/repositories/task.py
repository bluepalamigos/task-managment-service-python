"""Data access layer for Task entities."""

import uuid

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task


class TaskRepository:
    """Provides CRUD operations for tasks against the database.

    Args:
        session: An async SQLAlchemy session.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, task: Task) -> Task:
        """Persist a new task and return it with generated fields populated.

        Args:
            task: The Task instance to insert.

        Returns:
            The persisted Task with ``id``, ``created_at``, etc. populated.
        """
        self._session.add(task)
        await self._session.flush()
        await self._session.refresh(task)
        return task

    async def get_by_id(self, task_id: uuid.UUID) -> Task | None:
        """Fetch a non-deleted task by its ID.

        Args:
            task_id: UUID of the task to retrieve.

        Returns:
            The matching Task, or ``None`` if not found or soft-deleted.
        """
        stmt = select(Task).where(Task.id == task_id, Task.is_deleted.is_(False))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, limit: int, offset: int) -> tuple[list[Task], int]:
        """Return a paginated list of non-deleted tasks ordered by creation date.

        Args:
            limit: Maximum number of tasks to return.
            offset: Number of tasks to skip.

        Returns:
            A tuple of (task list, total count of non-deleted tasks).
        """
        base = select(Task).where(Task.is_deleted.is_(False))

        count_stmt = select(func.count()).select_from(base.subquery())
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        items_stmt = base.order_by(Task.created_at.desc()).limit(limit).offset(offset)
        items_result = await self._session.execute(items_stmt)
        items = list(items_result.scalars().all())

        return items, total

    async def update(self, task_id: uuid.UUID, data: dict) -> Task | None:
        """Update fields on a non-deleted task.

        Args:
            task_id: UUID of the task to update.
            data: Dictionary of column names to new values.

        Returns:
            The updated Task, or ``None`` if not found or soft-deleted.
        """
        stmt = (
            update(Task)
            .where(Task.id == task_id, Task.is_deleted.is_(False))
            .values(**data)
            .returning(Task)
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row:
            await self._session.refresh(row)
        return row

    async def soft_delete(self, task_id: uuid.UUID) -> bool:
        """Mark a task as deleted without removing it from the database.

        Args:
            task_id: UUID of the task to soft-delete.

        Returns:
            ``True`` if a row was updated, ``False`` if the task was not found.
        """
        stmt = (
            update(Task)
            .where(Task.id == task_id, Task.is_deleted.is_(False))
            .values(is_deleted=True)
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0
