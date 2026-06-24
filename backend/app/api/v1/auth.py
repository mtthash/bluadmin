"""Authentication endpoint — local platform user login."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import verify_password
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token
from app.auth.permissions import resolve_permissions
from app.db.session import get_db
from app.models.platform_user import PlatformUser
from app.schemas.auth import LoginRequest, LoginResponse

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LoginResponse:
    result = await db.execute(
        select(PlatformUser).where(PlatformUser.username == credentials.username)
    )
    user = result.scalar_one_or_none()

    if user is None or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario ou senha invalidos",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Conta desativada",
        )

    role_map = {"admin": "Admin", "hr": "HR", "it": "IT", "viewer": "Viewer"}
    mapped_role = role_map.get(user.role, user.role)
    permissions = resolve_permissions([mapped_role])

    token = create_access_token({
        "sub": user.username,
        "display_name": user.display_name,
        "role": user.role,
        "permissions": permissions,
        "user_id": str(user.id),
    })

    return LoginResponse(access_token=token)
