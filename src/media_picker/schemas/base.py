"""Base schema classes and utilities."""

from typing import Any, Dict, Type, TypeVar

from pydantic import BaseModel, ConfigDict


T = TypeVar("T", bound="BaseSchema")


class BaseSchema(BaseModel):
    """Base schema class with common configuration."""

    model_config = ConfigDict(
        # Pydantic V2 configuration
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        frozen=False,
        # JSON schema generation
        json_schema_extra={
            "examples": [],
        },
    )

    def model_dump_json_safe(self) -> Dict[str, Any]:
        """Dump model to dict with safe JSON serialization."""
        return self.model_dump(mode="json", exclude_none=True)

    @classmethod
    def model_validate_json_safe(cls: Type[T], json_data: str | bytes) -> T:
        """Validate JSON data with better error handling."""
        try:
            return cls.model_validate_json(json_data)
        except Exception as e:
            raise ValueError(f"Invalid JSON data for {cls.__name__}: {e}") from e
