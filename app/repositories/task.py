import uuid

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, task: Task) -> Task:
        self._session.add(task)
        await self._session.flush()
        await self._session.refresh(task)
        return task

    async def get_by_id(self, task_id: uuid.UUID) -> Task | None:
        stmt = select(Task).where(Task.id == task_id, Task.is_deleted.is_(False))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, limit: int, offset: int) -> tuple[list[Task], int]:
        base = select(Task).where(Task.is_deleted.is_(False))

        count_stmt = select(func.count()).select_from(base.subquery())
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        items_stmt = base.order_by(Task.created_at.desc()).limit(limit).offset(offset)
        items_result = await self._session.execute(items_stmt)
        items = list(items_result.scalars().all())

        return items, total

    async def update(self, task_id: uuid.UUID, data: dict) -> Task | None:
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
        stmt = (
            update(Task)
            .where(Task.id == task_id, Task.is_deleted.is_(False))
            .values(is_deleted=True)
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0
