"""Folder mapping endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_permissions
from app.config import get_settings
from app.schemas.folder_mapping import FolderMappingCreate, FolderMappingRead
from app.services.folder_mapping_service import FolderMappingService

router = APIRouter()


@router.get(
    "/employees/{employee_id}/folder-mappings",
    response_model=list[FolderMappingRead],
    dependencies=[Depends(require_permissions(["employee:read"]))],
    tags=["Folder Mappings"],
)
async def list_folder_mappings(
    employee_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[FolderMappingRead]:
    service = FolderMappingService(db)
    return await service.list_mappings(employee_id)


@router.post(
    "/employees/{employee_id}/folder-mappings",
    response_model=FolderMappingRead,
    status_code=201,
    dependencies=[Depends(require_permissions(["user:manage"]))],
    tags=["Folder Mappings"],
)
async def add_folder_mapping(
    employee_id: uuid.UUID,
    payload: FolderMappingCreate,
    db: AsyncSession = Depends(get_db),
) -> FolderMappingRead:
    service = FolderMappingService(db)
    return await service.add_mapping(employee_id, payload)


@router.delete(
    "/employees/{employee_id}/folder-mappings/{mapping_id}",
    status_code=204,
    dependencies=[Depends(require_permissions(["user:manage"]))],
    tags=["Folder Mappings"],
)
async def remove_folder_mapping(
    employee_id: uuid.UUID,
    mapping_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    service = FolderMappingService(db)
    await service.remove_mapping(employee_id, mapping_id)


@router.get(
    "/folder-mappings/login/{username}",
    response_model=list[FolderMappingRead],
    tags=["Folder Mappings"],
)
async def get_login_mappings(
    username: str,
    x_api_key: str = Header(..., alias="X-Api-Key"),
    db: AsyncSession = Depends(get_db),
) -> list[FolderMappingRead]:
    settings = get_settings()
    if x_api_key != settings.folder_mapping_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    service = FolderMappingService(db)
    return await service.get_mappings_by_username(username)
