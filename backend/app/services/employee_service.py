"""Service layer for employee lifecycle management (onboard / offboard).

This is the main orchestrator that coordinates calls to Microsoft Graph,
local database operations, and audit logging.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    DuplicateEmployeeError,
    EmployeeNotFoundError,
    GraphAPIError,
)
from app.integrations.graph.groups import (
    add_group_member,
    get_user_groups,
    remove_group_member,
)
from app.integrations.graph.licenses import remove_all_licenses
from app.integrations.graph.users import (
    create_entra_user,
    disable_entra_user,
    revoke_sessions,
)
from app.models.user import User
from app.schemas.auth import CurrentUser
from app.schemas.user import OnboardResponse, UserCreate, UserList, UserRead
from app.services.audit_service import AuditService
from app.services.user_service import UserService

logger = structlog.get_logger(__name__)


class EmployeeService:
    """Orchestrates employee onboarding and offboarding workflows.

    Each instance is scoped to a single database session and composes
    :class:`UserService` and :class:`AuditService` internally.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._user_service = UserService(db)
        self._audit_service = AuditService(db)

    # ── Onboard ─────────────────────────────────────────────────────────

    async def onboard(
        self,
        payload: UserCreate,
        actor: CurrentUser,
        ip_address: str,
    ) -> OnboardResponse:
        """Create a new employee in Entra ID and record them locally.

        Steps
        -----
        1. Build display name and UPN from the payload.
        2. Create the user in Entra ID.
        3. Optionally add the user to a department group.
        4. Persist a local user record.
        5. Log an audit entry.

        On any error the audit entry is recorded with ``result="failure"``
        and the original exception is re-raised.

        Returns
        -------
        OnboardResponse
            Contains the user data and the temporary password.
        """
        display_name = f"{payload.first_name} {payload.last_name}"

        # Extract domain from the actor's email to build the UPN
        domain = actor.email.split("@", 1)[1] if "@" in actor.email else "contoso.com"
        upn = f"{payload.mail_nickname}@{domain}"

        try:
            # 1. Create user in Entra ID
            entra_user = await create_entra_user(
                display_name=display_name,
                mail_nickname=payload.mail_nickname,
                upn=upn,
                password=payload.password,
                job_title=payload.job_title,
            )

            entra_id = entra_user.id  # type: ignore[union-attr]

            # 2. Add to department group if specified
            if payload.department_group_id:
                await add_group_member(
                    group_id=payload.department_group_id,
                    user_id=entra_id,
                )

            # 3. Save local user record
            local_user = User(
                entra_id=entra_id,
                display_name=display_name,
                email=upn,
                user_principal_name=upn,
                job_title=payload.job_title,
                department=payload.department_name,
                department_group_id=payload.department_group_id,
                status="active",
                created_by=actor.id,
            )
            self._db.add(local_user)
            await self._db.flush()

            # 4. Audit log
            await self._audit_service.log(
                action="user.onboard",
                actor_id=actor.id,
                actor_email=actor.email,
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
                entra_id=entra_id,
                upn=upn,
            )

            return OnboardResponse(
                user=UserRead.model_validate(local_user),
                temporary_password=payload.password,
                status="created",
            )

        except Exception as exc:
            # Log the failure
            await self._audit_service.log(
                action="user.onboard",
                actor_id=actor.id,
                actor_email=actor.email,
                target_email=upn,
                details={
                    "display_name": display_name,
                    "mail_nickname": payload.mail_nickname,
                },
                result="failure",
                error_message=str(exc),
                ip_address=ip_address,
            )
            logger.error(
                "employee_onboard_failed",
                upn=upn,
                error=str(exc),
            )
            raise

    # ── Offboard ────────────────────────────────────────────────────────

    async def offboard(
        self,
        employee_id: uuid.UUID,
        actor: CurrentUser,
        ip_address: str,
    ) -> UserRead:
        """Disable an employee in Entra ID and mark them as disabled locally.

        Steps
        -----
        1. Look up the local user; 404 if not found.
        2. Verify the user is active; 409 if already disabled.
        3. Disable the Entra user account.
        4. Revoke all active sessions.
        5. Remove the user from all groups.
        6. Remove all license assignments.
        7. Update the local record to ``status="disabled"``.
        8. Log an audit entry.

        Each Entra step is individually error-handled so that partial
        completion is possible (and recorded as ``result="partial"``).

        Returns
        -------
        UserRead
            The updated user record.
        """
        # 1. Get local user
        local_user = await self._user_service.get_by_id(employee_id)
        if local_user is None:
            raise EmployeeNotFoundError(str(employee_id))

        # 2. Check status
        if local_user.status == "disabled":
            raise DuplicateEmployeeError(
                message="Employee is already disabled",
                detail={"employee_id": str(employee_id), "status": local_user.status},
            )

        entra_id = local_user.entra_id
        errors: list[str] = []

        # 3. Disable Entra user (block sign-in)
        try:
            await disable_entra_user(entra_id)
        except GraphAPIError as exc:
            errors.append(f"disable_user: {exc.message}")
            logger.warning("offboard_step_failed", step="disable_user", error=str(exc))

        # 4. Revoke sessions
        try:
            await revoke_sessions(entra_id)
        except GraphAPIError as exc:
            errors.append(f"revoke_sessions: {exc.message}")
            logger.warning(
                "offboard_step_failed", step="revoke_sessions", error=str(exc)
            )

        # 5. Remove from all groups
        try:
            groups = await get_user_groups(entra_id)
            for group in groups:
                group_id = group.get("id")
                if group_id:
                    try:
                        await remove_group_member(group_id=group_id, user_id=entra_id)
                    except GraphAPIError as exc:
                        errors.append(
                            f"remove_group_member({group_id}): {exc.message}"
                        )
                        logger.warning(
                            "offboard_step_failed",
                            step="remove_group_member",
                            group_id=group_id,
                            error=str(exc),
                        )
        except GraphAPIError as exc:
            errors.append(f"get_user_groups: {exc.message}")
            logger.warning(
                "offboard_step_failed", step="get_user_groups", error=str(exc)
            )

        # 6. Remove all licenses
        try:
            await remove_all_licenses(entra_id)
        except GraphAPIError as exc:
            errors.append(f"remove_licenses: {exc.message}")
            logger.warning(
                "offboard_step_failed", step="remove_licenses", error=str(exc)
            )

        # 7. Update local record
        local_user.status = "disabled"
        local_user.disabled_by = actor.id
        local_user.disabled_at = datetime.now(timezone.utc)
        await self._db.flush()

        # 8. Audit log
        audit_result = "partial" if errors else "success"
        await self._audit_service.log(
            action="user.offboard",
            actor_id=actor.id,
            actor_email=actor.email,
            target_user_id=local_user.id,
            target_email=local_user.email,
            details={
                "entra_id": entra_id,
                "errors": errors if errors else None,
            },
            result=audit_result,
            error_message="; ".join(errors) if errors else None,
            ip_address=ip_address,
        )

        logger.info(
            "employee_offboarded",
            local_user_id=str(local_user.id),
            entra_id=entra_id,
            result=audit_result,
            error_count=len(errors),
        )

        return UserRead.model_validate(local_user)

    # ── Read helpers ────────────────────────────────────────────────────

    async def get_employee(self, employee_id: uuid.UUID) -> UserRead:
        """Retrieve a single employee by local UUID.

        Raises
        ------
        EmployeeNotFoundError
            If no user with the given ID exists.
        """
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
        """Return a paginated list of employees.

        Parameters
        ----------
        page:
            1-based page number.
        size:
            Records per page.
        status:
            Optional status filter (``"active"``, ``"disabled"``).

        Returns
        -------
        UserList
            Paginated response with user records and metadata.
        """
        users, total = await self._user_service.list_users(
            page=page,
            size=size,
            status_filter=status,
        )

        return UserList(
            items=[UserRead.model_validate(u) for u in users],
            total=total,
            page=page,
            size=size,
        )
