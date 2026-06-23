"""Service layer for department (Entra ID group) operations."""

from __future__ import annotations

import structlog

from app.integrations.graph.groups import list_groups
from app.schemas.department import DepartmentRead

logger = structlog.get_logger(__name__)


class DepartmentService:
    """Maps Entra ID groups to the ``DepartmentRead`` schema.

    Departments are sourced entirely from Microsoft Graph -- there is no
    local database table.  This service acts as a thin adapter between the
    Graph integration and the API layer.
    """

    def __init__(self) -> None:
        pass

    async def list_departments(self) -> list[DepartmentRead]:
        """Fetch all groups from Entra ID and return them as departments.

        Returns
        -------
        list[DepartmentRead]
            A list of departments mapped from Entra ID groups.
        """
        groups = await list_groups()

        departments = [
            DepartmentRead(
                id=group["id"],
                display_name=group["displayName"],
                description=group.get("description"),
                mail=group.get("mail"),
            )
            for group in groups
        ]

        logger.info("departments_listed", count=len(departments))
        return departments
