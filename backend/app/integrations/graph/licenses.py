"""Graph API operations on Entra ID license assignments."""

from __future__ import annotations

from typing import Any

import structlog
from msgraph.generated.users.item.assign_license.assign_license_post_request_body import (
    AssignLicensePostRequestBody,
)
from msgraph.generated.models.assigned_license import AssignedLicense

from app.core.exceptions import GraphAPIError
from app.integrations.graph.client import GraphAPIClient

logger = structlog.get_logger(__name__)


async def get_user_licenses(user_id: str) -> list[dict[str, Any]]:
    """Get all license assignments for a user.

    Parameters
    ----------
    user_id:
        The Entra ID object ID of the user.

    Returns
    -------
    list[dict]
        Each dict contains the license assignment details (sku_id, etc.).

    Raises
    ------
    GraphAPIError
        If the Graph API call fails.
    """
    client = GraphAPIClient.get_client()

    try:
        result = await client.users.by_user_id(user_id).license_details.get()

        licenses: list[dict[str, Any]] = []
        if result and result.value:
            for lic in result.value:
                licenses.append(
                    {
                        "id": lic.id,
                        "sku_id": str(lic.sku_id) if lic.sku_id else None,
                        "sku_part_number": lic.sku_part_number,
                    }
                )

        logger.info("user_licenses_fetched", user_id=user_id, count=len(licenses))
        return licenses

    except GraphAPIError:
        raise
    except Exception as exc:
        logger.error("user_licenses_fetch_failed", user_id=user_id, error=str(exc))
        raise GraphAPIError(
            operation="get_user_licenses",
            detail=str(exc),
        ) from exc


async def remove_all_licenses(user_id: str) -> None:
    """Remove all license assignments from a user.

    Fetches the user's current licenses and removes every one of them
    in a single ``assignLicense`` call with an empty ``addLicenses`` list.

    Parameters
    ----------
    user_id:
        The Entra ID object ID of the user.

    Raises
    ------
    GraphAPIError
        If the Graph API call fails.
    """
    client = GraphAPIClient.get_client()

    try:
        # First, get current license assignments from the user object
        user = await client.users.by_user_id(user_id).get()

        if not user or not user.assigned_licenses:
            logger.info("user_no_licenses_to_remove", user_id=user_id)
            return

        # Collect all SKU IDs to remove
        sku_ids_to_remove = [
            lic.sku_id
            for lic in user.assigned_licenses
            if lic.sku_id is not None
        ]

        if not sku_ids_to_remove:
            logger.info("user_no_licenses_to_remove", user_id=user_id)
            return

        # Build the request body: remove all, add none
        request_body = AssignLicensePostRequestBody(
            add_licenses=[],
            remove_licenses=sku_ids_to_remove,
        )

        await client.users.by_user_id(user_id).assign_license.post(request_body)
        logger.info(
            "user_licenses_removed",
            user_id=user_id,
            removed_count=len(sku_ids_to_remove),
        )

    except GraphAPIError:
        raise
    except Exception as exc:
        logger.error("user_licenses_remove_failed", user_id=user_id, error=str(exc))
        raise GraphAPIError(
            operation="remove_all_licenses",
            detail=str(exc),
        ) from exc
