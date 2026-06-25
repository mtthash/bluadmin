"""Service layer for employee lifecycle management (onboard / offboard)."""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timedelta, timezone

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    DuplicateEmployeeError,
    EmployeeNotFoundError,
    LDAPOperationError,
)
from app.integrations.ldap.groups import (
    add_group_member,
    get_user_groups,
    remove_group_member,
)
from app.integrations.ldap.users import (
    create_ldap_user,
    delete_ldap_user,
    disable_ldap_user,
    search_user,
)
from app.models.user import User
from app.schemas.auth import CurrentUser
from app.schemas.user import OnboardResponse, UserCreate, UserList, UserRead
from app.services.audit_service import AuditService
from app.services.user_service import UserService

logger = structlog.get_logger(__name__)


class EmployeeService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._user_service = UserService(db)
        self._audit_service = AuditService(db)

    async def onboard(
        self,
        payload: UserCreate,
        actor: CurrentUser,
        ip_address: str,
    ) -> OnboardResponse:
        display_name = f"{payload.first_name} {payload.last_name}"
        from app.config import get_settings
        settings = get_settings()
        upn = f"{payload.mail_nickname}@{settings.ldap_domain}"

        try:
            ldap_user = await asyncio.to_thread(
                create_ldap_user,
                display_name=display_name,
                sam_account_name=payload.mail_nickname,
                password=payload.password,
                job_title=payload.job_title,
            )

            user_dn = ldap_user["dn"]

            dept_id = None
            ad_group_dn = None
            if payload.department_group_id:
                try:
                    dept_id = uuid.UUID(payload.department_group_id)
                    from app.models.department import Department
                    from sqlalchemy import select
                    dept = (await self._db.execute(
                        select(Department).where(Department.id == dept_id)
                    )).scalar_one_or_none()
                    if dept and dept.ad_group_dn:
                        ad_group_dn = dept.ad_group_dn
                except ValueError:
                    ad_group_dn = payload.department_group_id

            if ad_group_dn:
                try:
                    await asyncio.to_thread(
                        add_group_member,
                        group_dn=ad_group_dn,
                        user_dn=user_dn,
                    )
                except LDAPOperationError as exc:
                    logger.warning("ldap_group_add_failed", group_dn=ad_group_dn, error=str(exc))

            local_user = User(
                ad_username=payload.mail_nickname,
                display_name=display_name,
                email=upn,
                user_principal_name=upn,
                job_title=payload.job_title,
                department=payload.department_name,
                department_group_id=payload.department_group_id,
                department_id=dept_id,
                status="active",
                created_by=None,
            )
            self._db.add(local_user)
            await self._db.flush()

            if payload.department_name:
                from app.services.folder_mapping_service import FolderMappingService
                folder_service = FolderMappingService(self._db)
                await folder_service.create_default_mapping(
                    local_user.id, payload.department_name
                )

            await self._audit_service.log(
                action="user.onboard",
                actor_id=None,
                actor_email=actor.username,
                target_user_id=local_user.id,
                target_email=upn,
                details={
                    "display_name": display_name,
                    "mail_nickname": payload.mail_nickname,
                    "department_group_id": payload.department_group_id,
                    "job_title": payload.job_title,
                },
                result="success",
                ip_address=ip_address,
            )

            logger.info(
                "employee_onboarded",
                local_user_id=str(local_user.id),
                ad_username=payload.mail_nickname,
                upn=upn,
            )

            password_set = ldap_user.get("password_set", False)
            return OnboardResponse(
                user=UserRead.model_validate(local_user),
                temporary_password=payload.password if password_set else "",
                status="created" if password_set else "created_no_password",
            )

        except Exception as exc:
            await self._audit_service.log(
                action="user.onboard",
                actor_id=None,
                actor_email=actor.username,
                target_email=upn,
                details={
                    "display_name": display_name,
                    "mail_nickname": payload.mail_nickname,
                },
                result="failure",
                error_message=str(exc),
                ip_address=ip_address,
            )
            logger.error("employee_onboard_failed", upn=upn, error=str(exc))
            raise

    async def offboard(
        self,
        employee_id: uuid.UUID,
        actor: CurrentUser,
        ip_address: str,
        retention_minutes: int = 43200,
    ) -> UserRead:
        local_user = await self._user_service.get_by_id(employee_id)
        if local_user is None:
            raise EmployeeNotFoundError(str(employee_id))

        if local_user.status == "disabled":
            raise DuplicateEmployeeError(
                message="Employee is already disabled",
                detail={"employee_id": str(employee_id), "status": local_user.status},
            )

        ad_username = local_user.ad_username
        errors: list[str] = []

        # Find user DN in AD
        user_data = await asyncio.to_thread(search_user, ad_username)
        user_dn = user_data["dn"] if user_data else None

        if user_dn:
            # Disable AD account
            try:
                await asyncio.to_thread(disable_ldap_user, user_dn)
            except LDAPOperationError as exc:
                errors.append(f"disable_user: {exc.message}")
                logger.warning("offboard_step_failed", step="disable_user", error=str(exc))

            # Remove from all groups
            try:
                groups = await asyncio.to_thread(get_user_groups, user_dn)
                for group in groups:
                    group_dn = group.get("dn")
                    if group_dn:
                        try:
                            await asyncio.to_thread(remove_group_member, group_dn, user_dn)
                        except LDAPOperationError as exc:
                            errors.append(f"remove_group({group_dn}): {exc.message}")
                            logger.warning("offboard_step_failed", step="remove_group", error=str(exc))
            except LDAPOperationError as exc:
                errors.append(f"get_user_groups: {exc.message}")
                logger.warning("offboard_step_failed", step="get_user_groups", error=str(exc))
        else:
            errors.append("User not found in Active Directory")

        now = datetime.now(timezone.utc)
        local_user.status = "disabled"
        local_user.disabled_by = None
        local_user.disabled_at = now
        local_user.scheduled_deletion_at = now + timedelta(minutes=retention_minutes)
        await self._db.flush()

        audit_result = "partial" if errors else "success"
        await self._audit_service.log(
            action="user.offboard",
            actor_id=None,
            actor_email=actor.username,
            target_user_id=local_user.id,
            target_email=local_user.email,
            details={
                "ad_username": ad_username,
                "errors": errors if errors else None,
            },
            result=audit_result,
            error_message="; ".join(errors) if errors else None,
            ip_address=ip_address,
        )

        logger.info(
            "employee_offboarded",
            local_user_id=str(local_user.id),
            ad_username=ad_username,
            result=audit_result,
        )

        return UserRead.model_validate(local_user)

    async def get_employee(self, employee_id: uuid.UUID) -> UserRead:
        user = await self._user_service.get_by_id(employee_id)
        if user is None:
            raise EmployeeNotFoundError(str(employee_id))
        return UserRead.model_validate(user)

    async def list_employees(
        self,
        page: int = 1,
        size: int = 50,
        status: str | None = None,
    ) -> UserList:
        users, total = await self._user_service.list_users(
            page=page, size=size, status_filter=status,
        )
        return UserList(
            items=[UserRead.model_validate(u) for u in users],
            total=total, page=page, size=size,
        )

    async def delete_employee(
        self,
        employee_id: uuid.UUID,
        actor: CurrentUser,
        ip_address: str,
    ) -> None:
        from app.models.audit_log import AuditLog

        local_user = await self._user_service.get_by_id(employee_id)
        if local_user is None:
            raise EmployeeNotFoundError(str(employee_id))

        ad_username = local_user.ad_username
        email = local_user.email

        user_data = await asyncio.to_thread(search_user, ad_username)
        if user_data:
            try:
                await asyncio.to_thread(delete_ldap_user, user_data["dn"])
            except LDAPOperationError as exc:
                logger.warning("delete_ad_user_failed", error=str(exc))

        from sqlalchemy import update
        await self._db.execute(
            update(AuditLog).where(AuditLog.target_user_id == employee_id).values(target_user_id=None)
        )
        await self._db.execute(
            update(AuditLog).where(AuditLog.actor_id == employee_id).values(actor_id=None)
        )

        await self._db.delete(local_user)
        await self._db.flush()

        await self._audit_service.log(
            action="user.delete",
            actor_id=None,
            actor_email=actor.username,
            target_email=local_user.email,
            details={"ad_username": ad_username},
            result="success",
            ip_address=ip_address,
        )

        logger.info("employee_deleted", ad_username=ad_username)
