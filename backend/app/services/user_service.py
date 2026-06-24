"""Service layer for local user record management."""

from __future__ import annotations

import uuid

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

logger = structlog.get_logger(__name__)


class UserService:
    """CRUD operations on the local ``users`` table.

    This service manages the local copy of user data; the authoritative
    source for identity is Microsoft Entra ID.  Each instance is scoped
    to a single database session.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_or_create_local_user(
        self,
        ad_username: str,
        email: str,
        display_name: str,
    ) -> User:
        """Find a user by ``ad_username``, creating them if they don't exist.

        If the user already exists but their ``email`` or ``display_name``
        have changed upstream, the local record is updated accordingly.

        Parameters
        ----------
        ad_username:
            The Microsoft Entra object ID (``oid`` claim from the JWT).
        email:
            The user's email address.
        display_name:
            The user's display name.

        Returns
        -------
        User
            The existing or newly created user record.
        """
        stmt = select(User).where(User.ad_username == ad_username)
        result = await self._db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is not None:
            # Update fields if they changed in Entra ID
            changed = False
            if user.email != email:
                user.email = email
                changed = True
            if user.display_name != display_name:
                user.display_name = display_name
                changed = True

            if changed:
                await self._db.flush()
                logger.info(
                    "local_user_updated",
                    ad_username=ad_username,
                    email=email,
                    display_name=display_name,
                )
            return user

        # User doesn't exist locally -- create
        user = User(
            ad_username=ad_username,
            email=email,
            display_name=display_name,
            user_principal_name=email,  # default UPN to email
            status="active",
        )
        self._db.add(user)
        await self._db.flush()

        logger.info(
            "local_user_created",
            user_id=str(user.id),
            ad_username=ad_username,
            email=email,
        )
        return user

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Look up a user by their local UUID primary key.

        Returns ``None`` if no matching user exists.
        """
        stmt = select(User).where(User.id == user_id)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ad_username(self, ad_username: str) -> User | None:
        """Look up a user by their Microsoft Entra object ID.

        Returns ``None`` if no matching user exists.
        """
        stmt = select(User).where(User.ad_username == ad_username)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_users(
        self,
        page: int = 1,
        size: int = 50,
        status_filter: str | None = None,
    ) -> tuple[list[User], int]:
        """Return a paginated list of users with an optional status filter.

        Parameters
        ----------
        page:
            1-based page number.
        size:
            Number of records per page.
        status_filter:
            If provided, only users with this status are returned
            (e.g. ``"active"``, ``"disabled"``).

        Returns
        -------
        tuple[list[User], int]
            A tuple of ``(users, total_count)``.
        """
        query = select(User)
        count_query = select(func.count()).select_from(User)

        if status_filter:
            query = query.where(User.status == status_filter)
            count_query = count_query.where(User.status == status_filter)

        # Total count
        total_result = await self._db.execute(count_query)
        total = total_result.scalar_one()

        # Paginated rows (newest first)
        offset = (page - 1) * size
        query = query.order_by(User.created_at.desc()).offset(offset).limit(size)

        result = await self._db.execute(query)
        users = list(result.scalars().all())

        return users, total
