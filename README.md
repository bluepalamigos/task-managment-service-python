# Task Management Service

A REST API microservice for task management built with FastAPI, PostgreSQL, and SQLAlchemy 2.0 (async).

## Project Structure

```
app/
├── core/           # Config, exceptions, logging, middleware
├── db/             # Database engine, session, base model
├── models/         # SQLAlchemy ORM models
├── schemas/        # Pydantic request/response schemas
├── repositories/   # Data access layer
├── services/       # Business logic layer
├── routers/        # API route handlers
└── main.py         # FastAPI application entry point
alembic/            # Database migrations
tests/              # Integration tests (pytest + httpx)
```

## API Endpoints

| Method | Path                   | Description       |
|--------|------------------------|-------------------|
| POST   | `/api/v1/tasks`        | Create a task     |
| GET    | `/api/v1/tasks`        | List tasks        |
| GET    | `/api/v1/tasks/{id}`   | Get a task        |
| PUT    | `/api/v1/tasks/{id}`   | Update a task     |
| DELETE | `/api/v1/tasks/{id}`   | Soft delete task  |
| GET    | `/health`              | Health check      |

Pagination: `GET /api/v1/tasks?limit=20&offset=0`

## Running with Docker Compose

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`. Swagger docs at `/docs`.

## Running Locally

### 1. Start PostgreSQL

```bash
docker run -d --name taskdb \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=taskdb \
  -p 5432:5432 postgres:16-alpine
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env if your database connection differs from the defaults
```

### 4. Run migrations

```bash
alembic upgrade head
```

### 5. Start the server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Environment Variables

| Variable       | Default                                                        | Description                  |
|----------------|----------------------------------------------------------------|------------------------------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/taskdb` | Async PostgreSQL connection  |
| `LOG_LEVEL`    | `INFO`                                                         | Python logging level         |
| `DEBUG`        | `false`                                                        | Enable debug mode            |

## Running Tests

Tests are integration tests that run against a live PostgreSQL instance and the running application.

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Ensure PostgreSQL is running and migrations are applied
# Ensure the app is running (e.g. in another terminal)

# Run tests
pytest
```

## API Usage Examples

### Create a task

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread"}'
```

Response (`201 Created`):
```json
{
  "id": "a1b2c3d4-...",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "PENDING",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### List tasks

```bash
curl http://localhost:8000/api/v1/tasks?limit=10&offset=0
```

Response (`200 OK`):
```json
{
  "items": [{"id": "...", "title": "Buy groceries", "...": "..."}],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

### Get a task

```bash
curl http://localhost:8000/api/v1/tasks/{task_id}
```

### Update a task

```bash
curl -X PUT http://localhost:8000/api/v1/tasks/{task_id} \
  -H "Content-Type: application/json" \
  -d '{"status": "COMPLETED"}'
```

### Delete a task

```bash
curl -X DELETE http://localhost:8000/api/v1/tasks/{task_id}
```

Response: `204 No Content`

### Health check

```bash
curl http://localhost:8000/health
```

Response: `{"status": "ok"}`
