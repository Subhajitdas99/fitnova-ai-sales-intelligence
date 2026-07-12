from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.app.core.exceptions import StartupConfigurationError


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="FITNOVA_",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "FitNova AI Sales Intelligence"
    app_version: str = "1.0.0"
    environment: Literal["local", "development", "test", "staging", "production"] = (
        "development"
    )
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    database_url: str = Field(
        default="sqlite:///./backend/fitnova_ai.db",
        validation_alias=AliasChoices("DATABASE_URL", "FITNOVA_DATABASE_URL"),
    )
    streamlit_backend_url: str = "http://localhost:8000"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    openrouter_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "OPENROUTER_API_KEY", "FITNOVA_OPENROUTER_API_KEY"
        ),
    )
    openrouter_model: str = Field(
        default="openai/gpt-4.1-mini",
        validation_alias=AliasChoices("OPENROUTER_MODEL", "FITNOVA_OPENROUTER_MODEL"),
    )
    whisper_model_size: str = Field(
        default="base",
        validation_alias=AliasChoices(
            "WHISPER_MODEL",
            "FITNOVA_WHISPER_MODEL",
            "FITNOVA_WHISPER_MODEL_SIZE",
        ),
    )
    whisper_device: Literal["auto", "cpu", "cuda"] = "auto"
    whisper_temperature: float = 0.0
    whisperx_model: str | None = Field(
        default=None,
        validation_alias=AliasChoices("WHISPERX_MODEL", "FITNOVA_WHISPERX_MODEL"),
    )
    whisperx_device: Literal["cpu", "cuda"] = "cpu"
    huggingface_auth_token: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "HUGGINGFACE_TOKEN",
            "HUGGINGFACE_AUTH_TOKEN",
            "FITNOVA_HUGGINGFACE_AUTH_TOKEN",
        ),
    )
    transcription_provider: Literal["whisper"] = "whisper"
    diarization_provider: Literal["heuristic", "whisperx"] = "whisperx"
    analysis_provider: Literal["openrouter", "openai", "heuristic"] = "openrouter"
    storage_dir: Path = Field(
        default=Path("backend/storage/audio"),
        validation_alias=AliasChoices("UPLOAD_DIRECTORY", "FITNOVA_UPLOAD_DIRECTORY"),
    )
    default_language: str = "auto"
    max_upload_size_mb: int = 100
    transcription_retry_attempts: int = 3
    transcription_retry_delay_seconds: float = 2.0
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:8501",
            "http://127.0.0.1:8501",
        ]
    )
    log_level: str = "INFO"
    request_timeout_seconds: float = 60.0
    strict_startup_validation: bool | None = None

    @field_validator(
        "openrouter_api_key",
        "openai_api_key",
        "huggingface_auth_token",
        "whisperx_model",
        mode="before",
    )
    @classmethod
    def blank_strings_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @computed_field  # type: ignore[misc]
    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @computed_field  # type: ignore[misc]
    @property
    def normalized_storage_dir(self) -> Path:
        return self.storage_dir.resolve()

    @property
    def is_openrouter_configured(self) -> bool:
        return bool(self.openrouter_api_key)

    def validate_for_startup(self) -> None:
        """Validate deploy-time configuration and raise a clear startup error."""

        strict = (
            self.strict_startup_validation
            if self.strict_startup_validation is not None
            else self.environment in {"staging", "production"}
        )
        missing: list[str] = []

        if self.analysis_provider == "openrouter" and not self.openrouter_api_key:
            missing.append("OPENROUTER_API_KEY")

        if strict and missing:
            joined = ", ".join(missing)
            raise StartupConfigurationError(
                f"Missing required production configuration: {joined}."
            )


@lru_cache
def get_settings() -> Settings:
    """Return a cached application settings object."""

    return Settings()
