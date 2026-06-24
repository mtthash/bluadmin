"""Service layer for department (AD group) operations."""

from __future__ import annotations

import asyncio

import structlog

from app.integrations.ldap.groups import ensure_group_exists, list_groups
from app.schemas.department import DepartmentCreate, DepartmentRead

logger = structlog.get_logger(__name__)


_AD_BUILTIN_GROUPS = {
    "Domain Computers", "Domain Controllers", "Schema Admins",
    "Enterprise Admins", "Cert Publishers", "Domain Admins",
    "Domain Users", "Domain Guests", "Group Policy Creator Owners",
    "RAS and IAS Servers", "Allowed RODC Password Replication Group",
    "Denied RODC Password Replication Group", "Read-only Domain Controllers",
    "Enterprise Read-only Domain Controllers", "Cloneable Domain Controllers",
    "Protected Users", "Key Admins", "Enterprise Key Admins",
    "DnsAdmins", "DnsUpdateProxy",
}


class DepartmentService:
    async def list_departments(self) -> list[DepartmentRead]:
        groups = await asyncio.to_thread(list_groups)

        departments = [
            DepartmentRead(
                id=group["dn"],
                display_name=group["cn"],
                description=group.get("description"),
                mail=group.get("mail"),
            )
            for group in groups
            if group["cn"] not in _AD_BUILTIN_GROUPS
            and not group["cn"].startswith("BluAdmin-")
        ]

        logger.info("departments_listed", count=len(departments))
        return departments

    async def create_department(self, payload: DepartmentCreate) -> DepartmentRead:
        dn = await asyncio.to_thread(
            ensure_group_exists, payload.name, payload.description
        )
        logger.info("department_created", name=payload.name, dn=dn)
        return DepartmentRead(
            id=dn,
            display_name=payload.name,
            description=payload.description,
        )
