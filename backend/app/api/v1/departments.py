"""Department endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_permissions
from app.schemas.department import DepartmentCreate, DepartmentRead
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
    service = DepartmentService(db)
    return await service.list_departments()


@router.post(
    "/",
    response_model=DepartmentRead,
    status_code=201,
    dependencies=[Depends(require_permissions(["user:manage"]))],
)
async def create_department(
    payload: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
) -> DepartmentRead:
    service = DepartmentService(db)
    return await service.create_department(payload)
