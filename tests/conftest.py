from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/taskdb"
APP_BASE_URL = "http://localhost:8000"


@pytest_asyncio.fixture(autouse=True)
async def clean_tasks():
    """Delete all tasks before each test for isolation."""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.execute(text("DELETE FROM tasks"))
    await engine.dispose()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(base_url=APP_BASE_URL) as ac:
        yield ac
