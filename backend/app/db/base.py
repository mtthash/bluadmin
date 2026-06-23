"""SQLAlchemy declarative base with consistent constraint naming conventions."""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Naming convention ensures all auto-generated constraints have predictable,
# deterministic names -- critical for Alembic migrations and DB portability.
NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models in BluAdmin."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
