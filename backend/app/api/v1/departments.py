"""Department endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_permissions
from app.schemas.department import DepartmentRead
from app.services.department_service import DepartmentService

router = APIRouter()


@router.get(
    "/",
    response_model=list[DepartmentRead],
    dependencies=[Depends(require_permissions(["department:read"]))],
)
async def list_departments(
    db: AsyncSession = Depends(get_db),
) -> list[DepartmentRead]:
    """Return all departments."""
    service = DepartmentService(db)
    return await service.list_departments()
