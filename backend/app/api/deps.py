"""FastAPI dependencies for authentication, authorisation, and request context."""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import validate_token
from app.auth.permissions import check_permissions, resolve_permissions
from app.config import get_settings
from app.db.session import get_db
from app.models.platform_user import PlatformUser
from app.schemas.auth import CurrentUser

bearer_scheme = HTTPBearer(auto_error=False)


async def _get_dev_user(db: AsyncSession) -> CurrentUser:
    result = await db.execute(
        select(PlatformUser).where(PlatformUser.username == "admin")
    )
    user = result.scalar_one_or_none()

    if user is None:
        from app.core.security import hash_password
        user = PlatformUser(
            username="admin",
            password_hash=hash_password("admin"),
            display_name="Dev Admin",
            role="admin",
            is_active=True,
        )
        db.add(user)
        await db.flush()

    permissions = resolve_permissions(["Admin"])

    return CurrentUser(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        role=user.role,
        permissions=permissions,
    )


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CurrentUser:
    settings = get_settings()
    if settings.dev_auth_bypass and settings.environment != "production":
        return await _get_dev_user(db)

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = validate_token(credentials.credentials)

    username: str = payload.get("sub", "")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing required 'sub' claim",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(
        select(PlatformUser).where(PlatformUser.username == username)
    )
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found or disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role_map = {"admin": "Admin", "hr": "HR", "it": "IT", "viewer": "Viewer"}
    mapped_role = role_map.get(user.role, user.role)
    permissions = resolve_permissions([mapped_role])

    return CurrentUser(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        role=user.role,
        permissions=permissions,
    )


def require_permissions(required: list[str]) -> Callable:
    async def _check(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
    ) -> CurrentUser:
        if not check_permissions(current_user.permissions, required):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _check


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"
