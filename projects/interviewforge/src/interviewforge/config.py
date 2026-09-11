"""Typed startup configuration; credentials are never included in error output."""

from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field, SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="INTERVIEWFORGE_", env_file=".env", extra="ignore", hide_input_in_errors=True
    )

    environment: Literal["development", "test", "production"] = "development"
    database_url: SecretStr | None = None
    db_connect_timeout: int = Field(default=3, ge=1, le=10)
    llm_provider: Literal["disabled", "anthropic", "openai"] = "disabled"
    llm_model: str | None = None
    anthropic_api_key: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("ANTHROPIC_API_KEY", "INTERVIEWFORGE_ANTHROPIC_API_KEY"),
    )
    amazon_mcp_server_url: str | None = None
    amazon_mcp_tool: str = "search_amazon_company_knowledge"
    leetcode_mcp_server_url: str | None = None
    leetcode_mcp_tool: str = "search_problems"
    knowledge_path: Path = Path(".interviewforge/amazon_knowledge.json")
    knowledge_refresh_hours: int = Field(default=24, ge=1, le=168)
    local_state_path: Path = Path(".interviewforge/state.json")

    @property
    def claude_ready(self) -> bool:
        return bool(
            self.llm_provider == "anthropic"
            and self.llm_model
            and self.anthropic_api_key
            and self.anthropic_api_key.get_secret_value().strip()
        )

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: SecretStr | None) -> SecretStr | None:
        if value is None:
            return None
        try:
            url = make_url(value.get_secret_value())
            valid = url.drivername == "postgresql+psycopg" and bool(url.host and url.database)
        except (ArgumentError, TypeError, ValueError):
            valid = False
        if not valid:
            raise ValueError("Use a postgresql+psycopg URL with host and database")
        return value


def load_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as exc:
        fields = ", ".join(".".join(map(str, item["loc"])) for item in exc.errors())
        raise RuntimeError(
            f"Invalid configuration: {fields}. Check INTERVIEWFORGE_ variables and .env.example."
        ) from None
