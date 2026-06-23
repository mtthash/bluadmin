"""Global exception handlers.

All error responses follow a uniform JSON shape so clients can parse
errors deterministically::

    {"detail": "...", "error_code": "..."}

5xx details are **never** leaked to the client; they are logged
server-side for debugging.
"""

from __future__ import annotations

import re

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from app.core.exceptions import BluAdminError

logger = structlog.get_logger(__name__)


def _error_response(
    status_code: int, detail: str, error_code: str
) -> JSONResponse:
    """Build a uniform error JSON response."""
    return JSONResponse(
        status_code=status_code,
        content={"detail": detail, "error_code": error_code},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach exception handlers to the FastAPI application instance."""

    @app.exception_handler(BluAdminError)
    async def _handle_bluadmin_error(
        request: Request, exc: BluAdminError
    ) -> JSONResponse:
        """Handle application-defined errors (4xx / 5xx)."""
        # Derive a stable error_code from the exception class name or
        # fall back to a generic code based on the HTTP status.
        error_code = getattr(exc, "error_code", None)
        if error_code is None:
            class_name = type(exc).__name__
            # Convert CamelCase to UPPER_SNAKE, e.g.
            # EmployeeNotFoundError -> EMPLOYEE_NOT_FOUND_ERROR
            error_code = re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).upper()

        if exc.status_code >= 500:
            await logger.aerror(
                "bluadmin_error",
                error_code=error_code,
                detail=exc.message,
            )
        return _error_response(exc.status_code, exc.message, error_code)

    @app.exception_handler(HTTPException)
    async def _handle_http_exception(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        """Pass through FastAPI/Starlette HTTP exceptions."""
        return _error_response(
            exc.status_code,
            str(exc.detail),
            f"HTTP_{exc.status_code}",
        )

    @app.exception_handler(RequestValidationError)
    async def _handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Return 422 with sanitised validation details.

        Field values are stripped to avoid echoing user-supplied
        secrets (e.g. passwords) back in the error response.
        """
        sanitised_errors: list[dict[str, object]] = []
        for err in exc.errors():
            sanitised_errors.append(
                {
                    "loc": err.get("loc", []),
                    "msg": err.get("msg", ""),
                    "type": err.get("type", ""),
                    # Deliberately omit "input" / "ctx" -- may contain PII.
                }
            )

        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation error",
                "error_code": "VALIDATION_ERROR",
                "errors": sanitised_errors,
            },
        )

    @app.exception_handler(Exception)
    async def _handle_unhandled_exception(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Catch-all for unexpected errors.

        The full traceback is logged server-side but only a generic
        message is returned to the client -- never leak internals.
        """
        await logger.aerror(
            "unhandled_exception",
            exc_type=type(exc).__name__,
            exc_message=str(exc),
            exc_info=True,
        )
        return _error_response(
            500,
            "Internal server error",
            "INTERNAL_ERROR",
        )
