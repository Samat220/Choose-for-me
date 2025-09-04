"""Core configuration module using Pydantic V2 settings."""

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Core Application Settings
    app_name: str = Field(default="Media Picker", description="Application name")
    version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # Server Configuration
    host: str = Field(default="127.0.0.1", description="Server host")
    port: int = Field(default=8000, description="Server port", gt=0, le=65535)
    reload: bool = Field(default=False, description="Auto-reload on changes")
    workers: int = Field(default=1, description="Number of worker processes", gt=0, le=8)

    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./data/media_picker.db",
        description="Database connection URL",
    )

    # Security Settings
    secret_key: str = Field(
        default="dev-secret-key-please-change-in-production",
        description="Secret key for sessions and JWT",
        min_length=32,
    )
    allowed_origins: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:8000"],
        description="CORS allowed origins",
    )

    # Path Configuration
    data_dir: Path = Field(default=Path("data"), description="Data directory")
    static_dir: Path = Field(default=Path("static"), description="Static files directory")
    templates_dir: Path = Field(default=Path("templates"), description="Templates directory")

    # Media Item Configuration
    max_tags_per_item: int = Field(default=10, description="Maximum tags per media item", gt=0)
    max_tag_length: int = Field(default=30, description="Maximum tag length", gt=0)
    max_title_length: int = Field(default=200, description="Maximum title length", gt=0)
    max_platform_length: int = Field(default=50, description="Maximum platform length", gt=0)

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: Any, info: ValidationInfo) -> list[str]:
        """Parse allowed origins from string or list."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        if isinstance(value, list):
            return value
        return []

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper_value = value.upper()
        if upper_value not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return upper_value

    def configure_logging(self) -> None:
        """Configure application logging."""
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            force=True,
        )


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Global settings instance
settings = get_settings()
