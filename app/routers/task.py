import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.repositories.task import TaskRepository
from app.schemas.task import (
    ErrorResponse,
    PaginatedTaskResponse,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)
from app.services.task import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_service(session: Annotated[AsyncSession, Depends(get_session)]) -> TaskService:
    repository = TaskRepository(session)
    return TaskService(repository)


ServiceDep = Annotated[TaskService, Depends(get_task_service)]


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
)
async def create_task(payload: TaskCreate, service: ServiceDep) -> TaskResponse:
    return await service.create_task(payload)


@router.get("", response_model=PaginatedTaskResponse)
async def list_tasks(
    service: ServiceDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PaginatedTaskResponse:
    return await service.list_tasks(limit=limit, offset=offset)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_task(task_id: uuid.UUID, service: ServiceDep) -> TaskResponse:
    return await service.get_task(task_id)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    responses={404: {"model": ErrorResponse}},
)
async def update_task(
    task_id: uuid.UUID, payload: TaskUpdate, service: ServiceDep
) -> TaskResponse:
    return await service.update_task(task_id, payload)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
async def delete_task(task_id: uuid.UUID, service: ServiceDep) -> None:
    await service.delete_task(task_id)
