"""Application configuration loaded from environment variables via pydantic-settings."""

from functools import cached_property
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """BluAdmin application settings.

    All values are read from environment variables or a .env file.
    Sensitive values (secrets, tokens) must never be logged or exposed.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Database ──────────────────────────────────────────────────────────
    database_url: str

    # ── Azure / Entra ID ──────────────────────────────────────────────────
    azure_tenant_id: str
    azure_client_id: str
    azure_client_secret: str
    azure_frontend_client_id: str

    # ── Azure AD Group IDs for role mapping ───────────────────────────────
    azure_group_id_hr: str
    azure_group_id_it: str
    azure_group_id_admin: str

    # ── Application ───────────────────────────────────────────────────────
    cors_origins: list[str] = ["http://localhost:3000"]
    log_level: str = "INFO"
    environment: Literal["dev", "production"] = "dev"

    # ── Validators ────────────────────────────────────────────────────────
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Accept a comma-separated string or an existing list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("log_level", mode="before")
    @classmethod
    def normalise_log_level(cls, v: str) -> str:
        return v.upper()

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v:
            raise ValueError("database_url must not be empty")
        return v

    # ── Derived properties ────────────────────────────────────────────────
    @cached_property
    def azure_authority_url(self) -> str:
        return f"https://login.microsoftonline.com/{self.azure_tenant_id}"

    @cached_property
    def azure_jwks_url(self) -> str:
        return (
            f"https://login.microsoftonline.com/{self.azure_tenant_id}"
            f"/discovery/v2.0/keys"
        )

    @property
    def docs_url(self) -> str | None:
        """Disable Swagger UI in production."""
        if self.environment == "production":
            return None
        return "/docs"

    @property
    def openapi_url(self) -> str | None:
        """Disable OpenAPI schema endpoint in production."""
        if self.environment == "production":
            return None
        return "/openapi.json"


def get_settings() -> Settings:
    """Factory that creates a Settings instance.

    Call once at startup; use FastAPI dependency injection afterwards.
    """
    return Settings()  # type: ignore[call-arg]
