"""Async database session management.

Provides a DatabaseSessionManager that owns the engine lifecycle and
an async generator ``get_db`` for FastAPI dependency injection.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class DatabaseSessionManager:
    """Manages the async engine and session factory lifecycle.

    Usage (at application startup/shutdown)::

        session_manager = DatabaseSessionManager()
        session_manager.init(database_url)
        ...
        await session_manager.close()
    """

    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = None

    def init(self, database_url: str) -> None:
        """Create the async engine and session factory.

        Must be called exactly once before any session is requested.
        """
        if self._engine is not None:
            raise RuntimeError("DatabaseSessionManager is already initialised")

        self._engine = create_async_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False,
        )
        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    async def close(self) -> None:
        """Dispose of the engine and release all pool connections."""
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._sessionmaker = None

    @asynccontextmanager
    async def connect(self) -> AsyncGenerator[AsyncConnection, None]:
        """Yield a raw async connection (useful for migrations)."""
        if self._engine is None:
            raise RuntimeError("DatabaseSessionManager is not initialised")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Yield a transactional async session with automatic commit/rollback."""
        if self._sessionmaker is None:
            raise RuntimeError("DatabaseSessionManager is not initialised")

        session = self._sessionmaker()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Module-level singleton -- initialised via ``init()`` during app startup.
session_manager = DatabaseSessionManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides an async database session.

    The session is automatically committed on success or rolled back on error.
    """
    async with session_manager.session() as session:
        yield session
