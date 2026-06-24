"""Employee management endpoints -- all require authentication."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_client_ip, get_current_user, get_db, require_permissions
from app.schemas.auth import CurrentUser
from app.schemas.user import OnboardResponse, UserCreate, UserList, UserRead
from app.services.employee_service import EmployeeService

router = APIRouter()


@router.post(
    "/onboard",
    status_code=status.HTTP_201_CREATED,
    response_model=OnboardResponse,
    dependencies=[Depends(require_permissions(["employee:create"]))],
)
async def onboard_employee(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    ip_address: str = Depends(get_client_ip),
) -> OnboardResponse:
    """Onboard a new employee."""
    service = EmployeeService(db)
    return await service.onboard(
        payload=payload,
        actor=current_user,
        ip_address=ip_address,
    )


@router.get(
    "/",
    response_model=UserList,
    dependencies=[Depends(require_permissions(["employee:list"]))],
)
async def list_employees(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> UserList:
    """List employees with pagination and optional status filter."""
    service = EmployeeService(db)
    return await service.list_employees(page=page, size=size, status=status)


@router.get(
    "/{employee_id}",
    response_model=UserRead,
    dependencies=[Depends(require_permissions(["employee:read"]))],
)
async def get_employee(
    employee_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    """Retrieve a single employee by ID."""
    service = EmployeeService(db)
    return await service.get_employee(employee_id=employee_id)


@router.post(
    "/{employee_id}/offboard",
    response_model=UserRead,
    dependencies=[Depends(require_permissions(["employee:disable"]))],
)
async def offboard_employee(
    employee_id: uuid.UUID,
    retention_minutes: int = Query(default=43200, ge=1, description="Minutes until permanent deletion (default 30 days)"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    ip_address: str = Depends(get_client_ip),
) -> UserRead:
    """Offboard (disable) an existing employee."""
    service = EmployeeService(db)
    return await service.offboard(
        employee_id=employee_id,
        actor=current_user,
        ip_address=ip_address,
        retention_minutes=retention_minutes,
    )


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permissions(["employee:disable"]))],
)
async def delete_employee(
    employee_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    ip_address: str = Depends(get_client_ip),
) -> None:
    """Permanently delete an employee from AD and database."""
    service = EmployeeService(db)
    await service.delete_employee(
        employee_id=employee_id,
        actor=current_user,
        ip_address=ip_address,
    )
