"""HTTP middleware for request tracing and access logging."""

import logging
import time
import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Assigns a unique request ID to each incoming request.

    Uses the ``X-Request-ID`` header if provided by the client,
    otherwise generates a UUID4. The ID is stored in a context var
    and echoed back in the response header.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process the request and attach a request ID.

        Args:
            request: The incoming HTTP request.
            call_next: Callable to invoke the next middleware or route handler.

        Returns:
            The HTTP response with ``X-Request-ID`` header set.
        """
        rid = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_ctx.set(rid)
        request.state.request_id = rid
        response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs the start and completion of each HTTP request with timing."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Log request start/completion with method, path, status, and duration.

        Args:
            request: The incoming HTTP request.
            call_next: Callable to invoke the next middleware or route handler.

        Returns:
            The HTTP response from downstream handlers.
        """
        rid = getattr(request.state, "request_id", "")
        start = time.monotonic()

        logger.info(
            "%s %s started",
            request.method,
            request.url.path,
            extra={"request_id": rid},
        )

        response = await call_next(request)
        duration_ms = round((time.monotonic() - start) * 1000, 2)

        logger.info(
            "%s %s completed status=%d duration=%sms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            extra={"request_id": rid},
        )
        return response
