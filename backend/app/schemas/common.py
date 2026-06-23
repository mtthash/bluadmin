"""Shared / generic response schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error envelope returned by the API."""

    detail: str
    error_code: str | None = None


class SuccessResponse(BaseModel):
    """Generic success envelope."""

    message: str
    data: dict[str, Any] | None = None
