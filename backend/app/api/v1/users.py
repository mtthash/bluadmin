"""User endpoints -- profile & admin user management."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_permissions
from app.schemas.auth import CurrentUser
from app.schemas.user import UserList, UserRead
from app.services.user_service import UserService

router = APIRouter()


@router.get(
    "/me",
    response_model=UserRead,
)
async def get_current_user_profile(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    """Return the authenticated user's own profile."""
    service = UserService(db)
    return await service.get_by_email(current_user.email)


@router.get(
    "/",
    response_model=UserList,
    dependencies=[Depends(require_permissions(["user:manage"]))],
)
async def list_users(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> UserList:
    """List all local users (admin only)."""
    service = UserService(db)
    return await service.list_users(page=page, size=size)
