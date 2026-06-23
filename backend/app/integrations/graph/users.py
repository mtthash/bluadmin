"""Graph API operations on Entra ID user accounts."""

from __future__ import annotations

import structlog
from msgraph.generated.models.password_profile import PasswordProfile
from msgraph.generated.models.user import User

from app.core.exceptions import GraphAPIError
from app.integrations.graph.client import GraphAPIClient

logger = structlog.get_logger(__name__)


async def create_entra_user(
    display_name: str,
    mail_nickname: str,
    upn: str,
    password: str,
    job_title: str | None = None,
) -> User:
    """Create a new user in Microsoft Entra ID.

    The user is created with ``account_enabled=True`` and
    ``force_change_password_next_sign_in=True`` so that the employee must
    set their own password on first login.

    Returns
    -------
    User
        The newly created user object from the Graph API.

    Raises
    ------
    GraphAPIError
        If the Graph API call fails for any reason.
    """
    client = GraphAPIClient.get_client()

    request_body = User(
        account_enabled=True,
        display_name=display_name,
        mail_nickname=mail_nickname,
        user_principal_name=upn,
        password_profile=PasswordProfile(
            force_change_password_next_sign_in=True,
            password=password,
        ),
    )

    if job_title is not None:
        request_body.job_title = job_title

    try:
        created_user = await client.users.post(request_body)
        logger.info(
            "entra_user_created",
            display_name=display_name,
            upn=upn,
            entra_id=created_user.id if created_user else None,
        )
        return created_user  # type: ignore[return-value]
    except Exception as exc:
        logger.error("entra_user_create_failed", upn=upn, error=str(exc))
        raise GraphAPIError(
            operation="create_user",
            detail=str(exc),
        ) from exc


async def disable_entra_user(entra_user_id: str) -> None:
    """Disable an Entra ID user account by setting ``account_enabled=False``.

    Raises
    ------
    GraphAPIError
        If the Graph API call fails.
    """
    client = GraphAPIClient.get_client()

    request_body = User(account_enabled=False)

    try:
        await client.users.by_user_id(entra_user_id).patch(request_body)
        logger.info("entra_user_disabled", entra_user_id=entra_user_id)
    except Exception as exc:
        logger.error(
            "entra_user_disable_failed",
            entra_user_id=entra_user_id,
            error=str(exc),
        )
        raise GraphAPIError(
            operation="disable_user",
            detail=str(exc),
        ) from exc


async def revoke_sessions(entra_user_id: str) -> None:
    """Revoke all active sign-in sessions for an Entra ID user.

    Raises
    ------
    GraphAPIError
        If the Graph API call fails.
    """
    client = GraphAPIClient.get_client()

    try:
        await client.users.by_user_id(entra_user_id).revoke_sign_in_sessions.post()
        logger.info("entra_sessions_revoked", entra_user_id=entra_user_id)
    except Exception as exc:
        logger.error(
            "entra_session_revoke_failed",
            entra_user_id=entra_user_id,
            error=str(exc),
        )
        raise GraphAPIError(
            operation="revoke_sessions",
            detail=str(exc),
        ) from exc


async def get_entra_user(entra_user_id: str) -> User:
    """Retrieve a user from Entra ID by their object ID.

    Returns
    -------
    User
        The user object from the Graph API.

    Raises
    ------
    GraphAPIError
        If the Graph API call fails (including user not found).
    """
    client = GraphAPIClient.get_client()

    try:
        user = await client.users.by_user_id(entra_user_id).get()
        return user  # type: ignore[return-value]
    except Exception as exc:
        logger.error(
            "entra_user_get_failed",
            entra_user_id=entra_user_id,
            error=str(exc),
        )
        raise GraphAPIError(
            operation="get_user",
            detail=str(exc),
        ) from exc
