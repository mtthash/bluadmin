"""Application configuration loaded from environment variables via pydantic-settings."""

import json
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Database ──────────────────────────────────────────────────────────
    database_url: str

    # ── LDAP / Active Directory ──────────────────────────────────────────
    ldap_server: str = "192.168.1.250"
    ldap_port: int = 389
    ldap_use_ssl: bool = False
    ldap_bind_dn: str = "CN=admin,CN=Users,DC=bluilu,DC=local"
    ldap_bind_password: str = "admin"
    ldap_base_dn: str = "CN=Users,DC=bluilu,DC=local"
    ldap_domain: str = "bluilu.local"

    # ── JWT ───────────────────────────────────────────────────────────────
    jwt_secret_key: str = "bluadmin-dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 480

    # ── Application ───────────────────────────────────────────────────────
    cors_origins: list[str] = ["http://localhost:3000"]
    log_level: str = "INFO"
    environment: Literal["dev", "production"] = "dev"
    dev_auth_bypass: bool = False

    # ── Validators ────────────────────────────────────────────────────────
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, ValueError):
                pass
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

    @property
    def docs_url(self) -> str | None:
        if self.environment == "production":
            return None
        return "/docs"

    @property
    def openapi_url(self) -> str | None:
        if self.environment == "production":
            return None
        return "/openapi.json"


def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
