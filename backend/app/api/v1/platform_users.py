"""Platform user management endpoints."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_client_ip, get_current_user, get_db, require_permissions
from app.schemas.auth import CurrentUser
from app.schemas.platform_user import (
    PlatformUserCreate,
    PlatformUserList,
    PlatformUserRead,
    PlatformUserUpdate,
)
from app.services.platform_user_service import PlatformUserService

router = APIRouter()


@router.get(
    "/",
    response_model=PlatformUserList,
    dependencies=[Depends(require_permissions(["user:manage"]))],
)
async def list_platform_users(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlatformUserList:
    service = PlatformUserService(db)
    users, total = await service.list_all()
    return PlatformUserList(
        items=[PlatformUserRead.model_validate(u) for u in users],
        total=total,
    )


@router.post(
    "/",
    response_model=PlatformUserRead,
    status_code=201,
    dependencies=[Depends(require_permissions(["user:manage"]))],
)
async def create_platform_user(
    payload: PlatformUserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser = Depends(get_current_user),
    ip_address: str = Depends(get_client_ip),
) -> PlatformUserRead:
    service = PlatformUserService(db)
    user = await service.create(payload, actor_username=current_user.username, ip_address=ip_address)
    await db.commit()
    return PlatformUserRead.model_validate(user)


@router.put(
    "/{user_id}",
    response_model=PlatformUserRead,
    dependencies=[Depends(require_permissions(["user:manage"]))],
)
async def update_platform_user(
    user_id: uuid.UUID,
    payload: PlatformUserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser = Depends(get_current_user),
    ip_address: str = Depends(get_client_ip),
) -> PlatformUserRead:
    service = PlatformUserService(db)
    user = await service.update(user_id, payload, actor_username=current_user.username, ip_address=ip_address)
    await db.commit()
    return PlatformUserRead.model_validate(user)


@router.delete(
    "/{user_id}",
    status_code=204,
    dependencies=[Depends(require_permissions(["user:manage"]))],
)
async def delete_platform_user(
    user_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser = Depends(get_current_user),
    ip_address: str = Depends(get_client_ip),
) -> None:
    service = PlatformUserService(db)
    await service.remove(user_id, actor_username=current_user.username, ip_address=ip_address)
    await db.commit()
