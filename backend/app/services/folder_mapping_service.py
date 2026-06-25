"""Service layer for folder mapping operations."""

from __future__ import annotations

import uuid

import asyncio
import re

import structlog
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.exceptions import BluAdminError
from app.models.folder_mapping import FolderMapping
from app.models.user import User
from app.schemas.folder_mapping import FolderMappingCreate, FolderMappingRead

logger = structlog.get_logger(__name__)

_VALID_DRIVES = set(f"{c}:" for c in "DEFGHIJKLMNOPQRSTUVWXYZ")


class DriveLetterConflictError(BluAdminError):
    def __init__(self, drive_letter: str) -> None:
        super().__init__(
            message=f"O drive '{drive_letter}' ja esta mapeado para este usuario",
            status_code=409,
            detail={"drive_letter": drive_letter},
        )


class InvalidDriveError(BluAdminError):
    def __init__(self, drive_letter: str) -> None:
        super().__init__(
            message=f"Disco inexistente: '{drive_letter}' nao e uma letra de drive valida (D: a Z:)",
            status_code=422,
            detail={"drive_letter": drive_letter},
        )


class FolderNotFoundError(BluAdminError):
    def __init__(self, folder_name: str) -> None:
        super().__init__(
            message=f"Diretorio inexistente: a pasta '{folder_name}' nao existe no servidor de arquivos",
            status_code=404,
            detail={"folder_name": folder_name},
        )


class FolderMappingService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._settings = get_settings()

    def _build_unc(self, folder_name: str) -> str:
        return f"{self._settings.file_share_unc}\\{folder_name}"

    def _to_read(self, mapping: FolderMapping) -> FolderMappingRead:
        return FolderMappingRead(
            id=str(mapping.id),
            folder_name=mapping.folder_name,
            drive_letter=mapping.drive_letter,
            unc_path=self._build_unc(mapping.folder_name),
            is_default=mapping.is_default,
            created_at=mapping.created_at,
        )

    async def list_mappings(self, user_id: uuid.UUID) -> list[FolderMappingRead]:
        stmt = (
            select(FolderMapping)
            .where(FolderMapping.user_id == user_id)
            .order_by(FolderMapping.drive_letter)
        )
        result = await self._db.execute(stmt)
        return [self._to_read(m) for m in result.scalars().all()]

    async def add_mapping(
        self, user_id: uuid.UUID, payload: FolderMappingCreate
    ) -> FolderMappingRead:
        if payload.drive_letter not in _VALID_DRIVES:
            raise InvalidDriveError(payload.drive_letter)

        try:
            from app.integrations.fileshare.folders import check_folder_exists
            exists = await asyncio.to_thread(check_folder_exists, payload.folder_name)
            if not exists:
                raise FolderNotFoundError(payload.folder_name)
        except FolderNotFoundError:
            raise
        except Exception as exc:
            logger.warning("folder_check_skipped", error=str(exc))

        mapping = FolderMapping(
            user_id=user_id,
            folder_name=payload.folder_name,
            drive_letter=payload.drive_letter,
            is_default=False,
        )
        self._db.add(mapping)
        try:
            await self._db.flush()
        except IntegrityError:
            await self._db.rollback()
            raise DriveLetterConflictError(payload.drive_letter)

        logger.info(
            "folder_mapping_added",
            user_id=str(user_id),
            folder=payload.folder_name,
            drive=payload.drive_letter,
        )
        return self._to_read(mapping)

    async def remove_mapping(
        self, user_id: uuid.UUID, mapping_id: uuid.UUID
    ) -> None:
        stmt = select(FolderMapping).where(
            FolderMapping.id == mapping_id,
            FolderMapping.user_id == user_id,
        )
        result = await self._db.execute(stmt)
        mapping = result.scalar_one_or_none()
        if mapping is None:
            raise BluAdminError(
                message="Folder mapping not found",
                status_code=404,
            )
        await self._db.delete(mapping)
        await self._db.flush()
        logger.info(
            "folder_mapping_removed",
            user_id=str(user_id),
            mapping_id=str(mapping_id),
        )

    async def create_default_mapping(
        self, user_id: uuid.UUID, department_name: str
    ) -> FolderMappingRead | None:
        drive = self._settings.file_share_default_drive
        mapping = FolderMapping(
            user_id=user_id,
            folder_name=department_name,
            drive_letter=drive,
            is_default=True,
        )
        self._db.add(mapping)
        try:
            await self._db.flush()
        except IntegrityError:
            await self._db.rollback()
            logger.warning(
                "default_folder_mapping_skipped",
                user_id=str(user_id),
                department=department_name,
                reason="drive letter conflict",
            )
            return None

        logger.info(
            "default_folder_mapping_created",
            user_id=str(user_id),
            department=department_name,
            drive=drive,
        )
        return self._to_read(mapping)

    async def get_mappings_by_username(
        self, username: str
    ) -> list[FolderMappingRead]:
        stmt = (
            select(FolderMapping)
            .join(User, FolderMapping.user_id == User.id)
            .where(User.ad_username == username, User.status == "active")
            .order_by(FolderMapping.drive_letter)
        )
        result = await self._db.execute(stmt)
        return [self._to_read(m) for m in result.scalars().all()]
