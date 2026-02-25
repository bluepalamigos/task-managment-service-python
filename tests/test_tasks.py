import uuid

import pytest
from httpx import AsyncClient

API_PREFIX = "/api/v1/tasks"


# --- Helper ---

async def create_task(client: AsyncClient, **overrides) -> dict:
    payload = {"title": "Test task", "description": "A test task", **overrides}
    response = await client.post(API_PREFIX, json=payload)
    assert response.status_code == 201
    return response.json()


# --- Create ---

@pytest.mark.asyncio
async def test_create_task_defaults(client: AsyncClient):
    data = await create_task(client)
    assert data["title"] == "Test task"
    assert data["description"] == "A test task"
    assert data["status"] == "PENDING"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_task_with_status(client: AsyncClient):
    data = await create_task(client, status="IN_PROGRESS")
    assert data["status"] == "IN_PROGRESS"


@pytest.mark.asyncio
async def test_create_task_without_description(client: AsyncClient):
    data = await create_task(client, title="No desc", description=None)
    assert data["description"] is None


@pytest.mark.asyncio
async def test_create_task_empty_title_rejected(client: AsyncClient):
    response = await client.post(API_PREFIX, json={"title": ""})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_task_missing_title_rejected(client: AsyncClient):
    response = await client.post(API_PREFIX, json={"description": "no title"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_task_invalid_status_rejected(client: AsyncClient):
    response = await client.post(API_PREFIX, json={"title": "t", "status": "INVALID"})
    assert response.status_code == 422


# --- Get ---

@pytest.mark.asyncio
async def test_get_task(client: AsyncClient):
    created = await create_task(client)
    response = await client.get(f"{API_PREFIX}/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


@pytest.mark.asyncio
async def test_get_task_not_found(client: AsyncClient):
    fake_id = str(uuid.uuid4())
    response = await client.get(f"{API_PREFIX}/{fake_id}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_task_invalid_uuid(client: AsyncClient):
    response = await client.get(f"{API_PREFIX}/not-a-uuid")
    assert response.status_code == 422


# --- List ---

@pytest.mark.asyncio
async def test_list_tasks_empty(client: AsyncClient):
    response = await client.get(API_PREFIX)
    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 0


@pytest.mark.asyncio
async def test_list_tasks_returns_created(client: AsyncClient):
    await create_task(client, title="Task 1")
    await create_task(client, title="Task 2")
    response = await client.get(API_PREFIX)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2


@pytest.mark.asyncio
async def test_list_tasks_pagination(client: AsyncClient):
    for i in range(5):
        await create_task(client, title=f"Task {i}")

    response = await client.get(API_PREFIX, params={"limit": 2, "offset": 0})
    body = response.json()
    assert len(body["items"]) == 2
    assert body["total"] == 5

    response = await client.get(API_PREFIX, params={"limit": 2, "offset": 4})
    body = response.json()
    assert len(body["items"]) == 1


@pytest.mark.asyncio
async def test_list_tasks_invalid_limit(client: AsyncClient):
    response = await client.get(API_PREFIX, params={"limit": 0})
    assert response.status_code == 422


# --- Update ---

@pytest.mark.asyncio
async def test_update_task_title(client: AsyncClient):
    created = await create_task(client)
    response = await client.put(
        f"{API_PREFIX}/{created['id']}", json={"title": "Updated"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"


@pytest.mark.asyncio
async def test_update_task_status(client: AsyncClient):
    created = await create_task(client)
    response = await client.put(
        f"{API_PREFIX}/{created['id']}", json={"status": "COMPLETED"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_update_task_not_found(client: AsyncClient):
    fake_id = str(uuid.uuid4())
    response = await client.put(f"{API_PREFIX}/{fake_id}", json={"title": "x"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_task_empty_body_returns_current(client: AsyncClient):
    created = await create_task(client)
    response = await client.put(f"{API_PREFIX}/{created['id']}", json={})
    assert response.status_code == 200
    assert response.json()["title"] == created["title"]


# --- Delete ---

@pytest.mark.asyncio
async def test_delete_task(client: AsyncClient):
    created = await create_task(client)
    response = await client.delete(f"{API_PREFIX}/{created['id']}")
    assert response.status_code == 204

    # Verify it's gone (soft-deleted)
    response = await client.get(f"{API_PREFIX}/{created['id']}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_task_not_found(client: AsyncClient):
    fake_id = str(uuid.uuid4())
    response = await client.delete(f"{API_PREFIX}/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_task_twice(client: AsyncClient):
    created = await create_task(client)
    response = await client.delete(f"{API_PREFIX}/{created['id']}")
    assert response.status_code == 204

    response = await client.delete(f"{API_PREFIX}/{created['id']}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_deleted_task_excluded_from_list(client: AsyncClient):
    created = await create_task(client)
    await client.delete(f"{API_PREFIX}/{created['id']}")

    response = await client.get(API_PREFIX)
    body = response.json()
    ids = [item["id"] for item in body["items"]]
    assert created["id"] not in ids
