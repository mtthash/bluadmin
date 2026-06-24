"""Background task to delete employees whose retention period has expired."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import structlog
from sqlalchemy import select, update

from app.db.session import session_manager
from app.integrations.ldap.users import delete_ldap_user, search_user
from app.models.audit_log import AuditLog
from app.models.user import User

logger = structlog.get_logger(__name__)


async def _process_expired_deletions() -> int:
    async with session_manager.session() as db:
        now = datetime.now(timezone.utc)
        result = await db.execute(
            select(User).where(
                User.status == "disabled",
                User.scheduled_deletion_at.isnot(None),
                User.scheduled_deletion_at <= now,
            )
        )
        expired = list(result.scalars().all())

        if not expired:
            return 0

        deleted = 0
        for user in expired:
            try:
                user_data = await asyncio.to_thread(search_user, user.ad_username)
                if user_data:
                    await asyncio.to_thread(delete_ldap_user, user_data["dn"])

                await db.execute(
                    update(AuditLog).where(AuditLog.target_user_id == user.id).values(target_user_id=None)
                )
                await db.execute(
                    update(AuditLog).where(AuditLog.actor_id == user.id).values(actor_id=None)
                )
                await db.delete(user)
                deleted += 1
                logger.info("scheduled_deletion_executed", ad_username=user.ad_username)
            except Exception as exc:
                logger.error(
                    "scheduled_deletion_failed",
                    ad_username=user.ad_username,
                    error=str(exc),
                )

        await db.commit()
        return deleted


async def run_deletion_scheduler(check_interval: int = 60) -> None:
    """Periodically check for and process expired deletions."""
    while True:
        try:
            count = await _process_expired_deletions()
            if count > 0:
                logger.info("deletion_scheduler_cycle", deleted=count)
        except Exception as exc:
            logger.error("deletion_scheduler_error", error=str(exc))

        await asyncio.sleep(check_interval)
