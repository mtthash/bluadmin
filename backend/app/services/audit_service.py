"""Service layer for audit logging."""

from __future__ import annotations

import uuid
from typing import Any

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogFilter, AuditLogList, AuditLogRead

logger = structlog.get_logger(__name__)


class AuditService:
    """Handles creation and querying of audit log entries.

    Each instance is scoped to a single database session.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def log(
        self,
        action: str,
        actor_id: uuid.UUID | None,
        actor_email: str,
        target_user_id: uuid.UUID | None = None,
        target_email: str | None = None,
        details: dict[str, Any] | None = None,
        result: str = "success",
        error_message: str | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        """Create an audit log entry in the database.

        Also emits a structured log event so the audit trail is visible
        in both the database and the application log stream.

        Returns
        -------
        AuditLog
            The persisted audit log record.
        """
        entry = AuditLog(
            action=action,
            actor_id=actor_id,
            actor_email=actor_email,
            target_user_id=target_user_id,
            target_email=target_email,
            details=details,
            result=result,
            error_message=error_message.replace("\x00", "") if error_message else None,
            ip_address=ip_address,
        )

        self._db.add(entry)
        await self._db.flush()

        # Emit a structured log event mirroring the DB record.
        logger.info(
            "audit_event",
            action=action,
            actor_email=actor_email,
            target_email=target_email,
            result=result,
            error_message=error_message,
            ip_address=ip_address,
        )

        return entry

    async def list_logs(
        self,
        page: int = 1,
        size: int = 50,
        filters: AuditLogFilter | None = None,
    ) -> AuditLogList:
        """Return a paginated, filtered list of audit log entries.

        Parameters
        ----------
        page:
            1-based page number.
        size:
            Number of records per page.
        filters:
            Optional filter criteria (action, actor_email, date range).

        Returns
        -------
        AuditLogList
            Paginated response containing items and metadata.
        """
        # Base query
        query = select(AuditLog)
        count_query = select(func.count()).select_from(AuditLog)

        # Apply filters
        if filters:
            if filters.action:
                query = query.where(AuditLog.action == filters.action)
                count_query = count_query.where(AuditLog.action == filters.action)
            if filters.actor_email:
                query = query.where(AuditLog.actor_email == filters.actor_email)
                count_query = count_query.where(
                    AuditLog.actor_email == filters.actor_email
                )
            if filters.date_from:
                query = query.where(AuditLog.created_at >= filters.date_from)
                count_query = count_query.where(
                    AuditLog.created_at >= filters.date_from
                )
            if filters.date_to:
                query = query.where(AuditLog.created_at <= filters.date_to)
                count_query = count_query.where(
                    AuditLog.created_at <= filters.date_to
                )

        # Total count
        total_result = await self._db.execute(count_query)
        total = total_result.scalar_one()

        # Paginated rows (newest first)
        offset = (page - 1) * size
        query = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(size)

        result = await self._db.execute(query)
        rows = result.scalars().all()

        return AuditLogList(
            items=[AuditLogRead.model_validate(row) for row in rows],
            total=total,
            page=page,
            size=size,
        )
