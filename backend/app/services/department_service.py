"""Service layer for department operations — DB-primary, LDAP-optional."""

from __future__ import annotations

import asyncio

import structlog
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateDepartmentError
from app.models.department import Department
from app.schemas.department import DepartmentCreate, DepartmentRead

logger = structlog.get_logger(__name__)


class DepartmentService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_departments(self) -> list[DepartmentRead]:
        stmt = select(Department).order_by(Department.name)
        result = await self._db.execute(stmt)
        departments = result.scalars().all()

        logger.info("departments_listed", count=len(departments))
        return [
            DepartmentRead(
                id=str(dept.id),
                display_name=dept.name,
                description=dept.description,
                mail=dept.mail,
            )
            for dept in departments
        ]

    async def create_department(self, payload: DepartmentCreate) -> DepartmentRead:
        department = Department(
            name=payload.name,
            description=payload.description,
        )

        ad_group_dn = await self._try_ldap_sync(payload.name, payload.description)
        if ad_group_dn:
            department.ad_group_dn = ad_group_dn

        self._db.add(department)
        try:
            await self._db.flush()
        except IntegrityError:
            await self._db.rollback()
            raise DuplicateDepartmentError(payload.name)

        await self._try_create_folder(payload.name)

        logger.info("department_created", department_id=str(department.id), name=payload.name)
        return DepartmentRead(
            id=str(department.id),
            display_name=department.name,
            description=department.description,
            mail=department.mail,
        )

    async def _try_create_folder(self, name: str) -> None:
        try:
            from app.integrations.fileshare.folders import create_department_folder
            await asyncio.to_thread(create_department_folder, name)
        except Exception as exc:
            logger.warning("department_folder_creation_skipped", name=name, error=str(exc))

    async def _try_ldap_sync(self, name: str, description: str | None) -> str | None:
        try:
            from app.integrations.ldap.groups import ensure_group_exists
            dn = await asyncio.to_thread(ensure_group_exists, name, description)
            logger.info("department_ldap_synced", name=name, dn=dn)
            return dn
        except Exception as exc:
            logger.warning("department_ldap_sync_skipped", name=name, error=str(exc))
            return None
