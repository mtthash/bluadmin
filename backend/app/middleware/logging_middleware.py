"""Structured request/response logging middleware.

Each request receives a unique ``request_id`` (UUID v4) that is bound
to the structlog context for the duration of the request, making it
trivial to correlate all log entries for a single HTTP round-trip.

Sensitive data (query parameters, request bodies) is deliberately
omitted from log output.
"""

from __future__ import annotations

import time
import uuid

import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger(__name__)


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request/response with a unique correlation ID."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # ── Prepare context ─────────────────────────────────────────────
        request_id = str(uuid.uuid4())
        client_ip = self._get_client_ip(request)

        clear_contextvars()
        bind_contextvars(request_id=request_id)

        # ── Log request (no query params or body -- may be sensitive) ───
        await logger.ainfo(
            "request_started",
            method=request.method,
            path=request.url.path,
            client_ip=client_ip,
        )

        start = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            await logger.aerror(
                "request_failed",
                method=request.method,
                path=request.url.path,
                duration_ms=duration_ms,
            )
            raise
        else:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            await logger.ainfo(
                "request_completed",
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

        finally:
            clear_contextvars()

        # Attach the request ID as a response header for client-side tracing.
        response.headers["X-Request-ID"] = request_id
        return response

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """Extract the client IP, preferring X-Forwarded-For."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"
