"""FastAPI dependencies for authentication, authorisation, and request context.

All route handlers that need an authenticated user inject ``get_current_user``.
Routes that additionally require specific permissions use the
``require_permissions`` factory.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.azure_ad import validate_token
from app.auth.permissions import check_permissions, resolve_permissions
from app.auth.role_mapping import resolve_roles_from_groups
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import CurrentUser

# ── Bearer token extraction ─────────────────────────────────────────────────
bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CurrentUser:
    """Validate the JWT, resolve roles/permissions, and upsert the local user.

    Returns a ``CurrentUser`` schema populated from Azure AD claims and
    the local database record.

    Raises
    ------
    HTTPException (401)
        If the token is missing, invalid, or the user account is disabled.
    """
    # ── Validate token ──────────────────────────────────────────────────
    payload = await validate_token(credentials.credentials)

    entra_id: str = payload.get("oid", "")
    email: str = payload.get("preferred_username", "")
    display_name: str = payload.get("name", "")
    group_ids: list[str] = payload.get("groups", [])

    if not entra_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing required 'oid' claim",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ── Resolve roles and permissions ───────────────────────────────────
    roles = resolve_roles_from_groups(group_ids)
    permissions = resolve_permissions(roles)

    # ── Upsert local user record ────────────────────────────────────────
    result = await db.execute(
        select(User).where(User.entra_id == entra_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            entra_id=entra_id,
            email=email,
            display_name=display_name,
            user_principal_name=email,
            status="active",
        )
        db.add(user)
        await db.flush()
    else:
        # Update mutable fields from the latest token claims.
        user.email = email
        user.display_name = display_name
        await db.flush()

    # ── Guard: disabled accounts must not proceed ───────────────────────
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return CurrentUser(
        id=user.id,
        entra_id=user.entra_id,
        email=user.email,
        display_name=user.display_name,
        roles=roles,
        permissions=permissions,
    )


def require_permissions(required: list[str]) -> Callable:
    """Factory that returns a dependency enforcing the given permissions.

    Usage::

        @router.get(
            "/admin-only",
            dependencies=[Depends(require_permissions(["user:manage"]))],
        )
        async def admin_only_route(): ...

    Raises
    ------
    HTTPException (403)
        If the authenticated user lacks any of the required permissions.
    """

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
    """Extract the client IP address from the request.

    Checks ``X-Forwarded-For`` first (set by reverse proxies), falling
    back to the direct connection address.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For may contain a comma-separated list; the first
        # entry is the original client.
        return forwarded_for.split(",")[0].strip()

    if request.client:
        return request.client.host

    return "unknown"
