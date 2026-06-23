"""Audit log endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_permissions
from app.schemas.audit_log import AuditLogFilter, AuditLogList
from app.services.audit_service import AuditService

router = APIRouter()


@router.get(
    "/",
    response_model=AuditLogList,
    dependencies=[Depends(require_permissions(["audit:read"]))],
)
async def list_audit_logs(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    action: str | None = Query(default=None),
    actor_email: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> AuditLogList:
    """List audit logs with filtering and pagination."""
    log_filter = AuditLogFilter(
        action=action,
        actor_email=actor_email,
        date_from=date_from,
        date_to=date_to,
    )
    service = AuditService(db)
    return await service.list_logs(page=page, size=size, log_filter=log_filter)
