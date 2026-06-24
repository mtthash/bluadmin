"""User endpoints -- profile & admin user management."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_permissions
from app.schemas.auth import CurrentUser
from app.schemas.user import UserList
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me")
async def get_current_user_profile(
    current_user: CurrentUser = Depends(get_current_user),
) -> dict:
    """Return the authenticated platform user's profile."""
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "display_name": current_user.display_name,
        "role": current_user.role,
        "permissions": current_user.permissions,
    }


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
    """List all local employee users (admin only)."""
    service = UserService(db)
    users, total = await service.list_users(page=page, size=size)
    return UserList(
        items=[],
        total=total,
        page=page,
        size=size,
    )
