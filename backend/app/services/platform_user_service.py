"""Service layer for platform user management."""

from __future__ import annotations

import uuid

from app.core.security import hash_password
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateEmployeeError, ValidationError
from app.models.platform_user import PlatformUser
from app.schemas.platform_user import PlatformUserCreate, PlatformUserUpdate
from app.services.audit_service import AuditService


class PlatformUserService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._audit = AuditService(db)

    def _is_root_admin(self, user: PlatformUser) -> bool:
        return user.username == "admin"

    async def _log(self, action: str, actor: str, target: str, result: str = "success",
                   details: dict | None = None, error_message: str | None = None,
                   ip: str | None = None) -> None:
        await self._audit.log(
            action=action,
            actor_id=None,
            actor_email=actor,
            target_email=target,
            details=details,
            result=result,
            error_message=error_message,
            ip_address=ip,
        )

    async def create(self, payload: PlatformUserCreate, actor_username: str = "",
                     ip_address: str | None = None) -> PlatformUser:
        existing = await self._db.execute(
            select(PlatformUser).where(PlatformUser.username == payload.username)
        )
        if existing.scalar_one_or_none():
            raise DuplicateEmployeeError(
                message=f"Usuario '{payload.username}' ja existe",
                detail={"username": payload.username},
            )

        user = PlatformUser(
            username=payload.username,
            password_hash=hash_password(payload.password),
            display_name=payload.display_name,
            role=payload.role,
            is_active=True,
        )
        self._db.add(user)
        await self._db.flush()

        await self._log(
            action="platform_user.create",
            actor=actor_username,
            target=payload.username,
            details={"display_name": payload.display_name, "role": payload.role},
            ip=ip_address,
        )

        return user

    async def update(self, user_id: uuid.UUID, payload: PlatformUserUpdate,
                     actor_username: str = "", ip_address: str | None = None) -> PlatformUser:
        result = await self._db.execute(
            select(PlatformUser).where(PlatformUser.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            raise ValidationError("Usuario nao encontrado")

        if self._is_root_admin(user):
            if payload.role is not None and payload.role != "admin":
                await self._log(
                    action="platform_user.protect",
                    actor=actor_username,
                    target=user.username,
                    result="blocked",
                    details={"attempted_action": "rebaixar_role", "attempted_value": payload.role},
                    ip=ip_address,
                )
                raise ValidationError("Nao e permitido rebaixar o administrador principal")
            if payload.is_active is not None and not payload.is_active:
                await self._log(
                    action="platform_user.protect",
                    actor=actor_username,
                    target=user.username,
                    result="blocked",
                    details={"attempted_action": "desativar"},
                    ip=ip_address,
                )
                raise ValidationError("Nao e permitido desativar o administrador principal")

        changes = {}
        if payload.display_name is not None and payload.display_name != user.display_name:
            changes["display_name"] = {"from": user.display_name, "to": payload.display_name}
            user.display_name = payload.display_name
        if payload.role is not None and payload.role != user.role:
            changes["role"] = {"from": user.role, "to": payload.role}
            user.role = payload.role
        if payload.is_active is not None and payload.is_active != user.is_active:
            changes["is_active"] = {"from": user.is_active, "to": payload.is_active}
            user.is_active = payload.is_active
        if payload.password is not None:
            changes["password"] = "alterada"
            user.password_hash = hash_password(payload.password)

        await self._db.flush()

        if changes:
            await self._log(
                action="platform_user.update",
                actor=actor_username,
                target=user.username,
                details=changes,
                ip=ip_address,
            )

        return user

    async def delete(self, user_id: uuid.UUID, actor_username: str = "",
                     ip_address: str | None = None) -> None:
        result = await self._db.execute(
            select(PlatformUser).where(PlatformUser.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            raise ValidationError("Usuario nao encontrado")

        if self._is_root_admin(user):
            await self._log(
                action="platform_user.protect",
                actor=actor_username,
                target=user.username,
                result="blocked",
                details={"attempted_action": "remover"},
                ip=ip_address,
            )
            raise ValidationError("Nao e permitido remover o administrador principal")

        user.is_active = False
        await self._db.flush()

        await self._log(
            action="platform_user.deactivate",
            actor=actor_username,
            target=user.username,
            ip=ip_address,
        )

    async def remove(self, user_id: uuid.UUID, actor_username: str = "",
                     ip_address: str | None = None) -> None:
        result = await self._db.execute(
            select(PlatformUser).where(PlatformUser.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            raise ValidationError("Usuario nao encontrado")

        if self._is_root_admin(user):
            await self._log(
                action="platform_user.protect",
                actor=actor_username,
                target=user.username,
                result="blocked",
                details={"attempted_action": "remover"},
                ip=ip_address,
            )
            raise ValidationError("Nao e permitido remover o administrador principal")

        username = user.username
        await self._db.delete(user)
        await self._db.flush()

        await self._log(
            action="platform_user.remove",
            actor=actor_username,
            target=username,
            ip=ip_address,
        )

    async def list_all(self) -> tuple[list[PlatformUser], int]:
        total_result = await self._db.execute(
            select(func.count()).select_from(PlatformUser)
        )
        total = total_result.scalar_one()

        result = await self._db.execute(
            select(PlatformUser).order_by(PlatformUser.created_at.asc())
        )
        users = list(result.scalars().all())
        return users, total
