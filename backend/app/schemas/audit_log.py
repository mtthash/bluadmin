"""Pydantic schemas for audit-log payloads."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    """Public representation of an audit-log entry."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    action: str
    actor_email: str
    target_email: str | None = None
    details: dict[str, Any] | None = None
    result: str
    error_message: str | None = None
    ip_address: str | None = None
    created_at: datetime


class AuditLogFilter(BaseModel):
    """Query parameters for filtering audit logs."""

    action: str | None = None
    actor_email: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None


class AuditLogList(BaseModel):
    """Paginated list of audit-log entries."""

    items: list[AuditLogRead]
    total: int
    page: int
    size: int
