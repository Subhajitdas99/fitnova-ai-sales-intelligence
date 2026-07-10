from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    environment: Literal["local", "development", "staging", "production"] = (
        "development"
    )
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./backend/fitnova_ai.db"
    streamlit_backend_url: str = "http://localhost:8000"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    whisper_model_size: str = "base"
    whisper_device: Literal["auto", "cpu", "cuda"] = "auto"
    whisper_temperature: float = 0.0
    huggingface_auth_token: str | None = None
    transcription_provider: Literal["whisper"] = "whisper"
    diarization_provider: Literal["heuristic", "whisperx"] = "heuristic"
    analysis_provider: Literal["heuristic", "openai"] = "heuristic"
    storage_dir: Path = Path("backend/storage/audio")
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

    @computed_field  # type: ignore[misc]
    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @computed_field  # type: ignore[misc]
    @property
    def normalized_storage_dir(self) -> Path:
        return self.storage_dir.resolve()


@lru_cache
def get_settings() -> Settings:
    """Return a cached application settings object."""

    return Settings()
