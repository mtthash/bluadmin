"""Graph API operations on Entra ID groups (used as departments)."""

from __future__ import annotations

from typing import Any

import structlog
from msgraph.generated.groups.groups_request_builder import GroupsRequestBuilder
from msgraph.generated.models.reference_create import ReferenceCreate

from app.core.exceptions import GraphAPIError
from app.integrations.graph.client import GraphAPIClient

logger = structlog.get_logger(__name__)


async def list_groups(filter_prefix: str | None = None) -> list[dict[str, Any]]:
    """Fetch groups from Microsoft Entra ID.

    Parameters
    ----------
    filter_prefix:
        If provided, only groups whose ``displayName`` starts with this
        prefix are returned (case-insensitive OData ``startswith`` filter).

    Returns
    -------
    list[dict]
        Each dict contains: ``id``, ``displayName``, ``description``, ``mail``.

    Raises
    ------
    GraphAPIError
        If the Graph API call fails.
    """
    client = GraphAPIClient.get_client()

    try:
        query_params = GroupsRequestBuilder.GroupsRequestBuilderGetQueryParameters(
            select=["id", "displayName", "description", "mail"],
            orderby=["displayName"],
            top=999,
        )

        if filter_prefix:
            query_params.filter = f"startswith(displayName, '{filter_prefix}')"

        request_config = GroupsRequestBuilder.GroupsRequestBuilderGetRequestConfiguration(
            query_parameters=query_params,
        )

        result = await client.groups.get(request_configuration=request_config)

        groups: list[dict[str, Any]] = []
        if result and result.value:
            for group in result.value:
                groups.append(
                    {
                        "id": group.id,
                        "displayName": group.display_name,
                        "description": group.description,
                        "mail": group.mail,
                    }
                )

        logger.info("groups_listed", count=len(groups), filter_prefix=filter_prefix)
        return groups

    except GraphAPIError:
        raise
    except Exception as exc:
        logger.error("groups_list_failed", error=str(exc))
        raise GraphAPIError(
            operation="list_groups",
            detail=str(exc),
        ) from exc


async def add_group_member(group_id: str, user_id: str) -> None:
    """Add a user to an Entra ID group.

    Parameters
    ----------
    group_id:
        The object ID of the target group.
    user_id:
        The object ID of the user to add.

    Raises
    ------
    GraphAPIError
        If the Graph API call fails.
    """
    client = GraphAPIClient.get_client()

    try:
        request_body = ReferenceCreate(
            odata_id=f"https://graph.microsoft.com/v1.0/directoryObjects/{user_id}",
        )
        await client.groups.by_group_id(group_id).members.ref.post(request_body)
        logger.info("group_member_added", group_id=group_id, user_id=user_id)
    except Exception as exc:
        logger.error(
            "group_member_add_failed",
            group_id=group_id,
            user_id=user_id,
            error=str(exc),
        )
        raise GraphAPIError(
            operation="add_group_member",
            detail=str(exc),
        ) from exc


async def remove_group_member(group_id: str, user_id: str) -> None:
    """Remove a user from an Entra ID group.

    Parameters
    ----------
    group_id:
        The object ID of the target group.
    user_id:
        The object ID of the user to remove.

    Raises
    ------
    GraphAPIError
        If the Graph API call fails.
    """
    client = GraphAPIClient.get_client()

    try:
        await client.groups.by_group_id(group_id).members.by_directory_object_id(
            user_id
        ).ref.delete()
        logger.info("group_member_removed", group_id=group_id, user_id=user_id)
    except Exception as exc:
        logger.error(
            "group_member_remove_failed",
            group_id=group_id,
            user_id=user_id,
            error=str(exc),
        )
        raise GraphAPIError(
            operation="remove_group_member",
            detail=str(exc),
        ) from exc


async def get_user_groups(user_id: str) -> list[dict[str, Any]]:
    """Get all groups that a user is a member of.

    Parameters
    ----------
    user_id:
        The Entra ID object ID of the user.

    Returns
    -------
    list[dict]
        Each dict contains: ``id``, ``displayName``, ``description``, ``mail``.

    Raises
    ------
    GraphAPIError
        If the Graph API call fails.
    """
    client = GraphAPIClient.get_client()

    try:
        result = await client.users.by_user_id(user_id).member_of.get()

        groups: list[dict[str, Any]] = []
        if result and result.value:
            for directory_object in result.value:
                # Only include groups (not roles or other directory objects)
                if hasattr(directory_object, "display_name"):
                    groups.append(
                        {
                            "id": directory_object.id,
                            "displayName": getattr(directory_object, "display_name", None),
                            "description": getattr(directory_object, "description", None),
                            "mail": getattr(directory_object, "mail", None),
                        }
                    )

        logger.info("user_groups_fetched", user_id=user_id, count=len(groups))
        return groups

    except GraphAPIError:
        raise
    except Exception as exc:
        logger.error("user_groups_fetch_failed", user_id=user_id, error=str(exc))
        raise GraphAPIError(
            operation="get_user_groups",
            detail=str(exc),
        ) from exc
