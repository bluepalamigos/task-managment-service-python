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

1. Start PostgreSQL:
```bash
docker run -d --name taskdb -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=taskdb -p 5432:5432 postgres:16-alpine
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy and configure environment:
```bash
cp .env.example .env
```

4. Run migrations:
```bash
alembic upgrade head
```

5. Start the server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Environment Variables

| Variable       | Default                                                    | Description          |
|----------------|------------------------------------------------------------|----------------------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/taskdb` | PostgreSQL connection string |
| `LOG_LEVEL`    | `INFO`                                                     | Logging level        |
| `DEBUG`        | `false`                                                    | Debug mode           |
