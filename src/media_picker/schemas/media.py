"""Media item schemas using Pydantic V2."""

import re
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import Field, field_validator, model_validator

from ..core.config import settings
from .base import BaseSchema


class MediaType(str):
    """Media type enumeration."""

    GAME = "game"
    MOVIE = "movie"


class MediaStatus(str):
    """Media status enumeration."""

    ACTIVE = "active"
    DONE = "done"
    ARCHIVED = "archived"


# Platform mappings for validation
PLATFORM_MAPPINGS = {
    MediaType.GAME: {
        "PC",
        "PlayStation",
        "PlayStation 4",
        "PlayStation 5",
        "Xbox",
        "Xbox One",
        "Xbox Series X/S",
        "Nintendo Switch",
        "Nintendo 3DS",
        "Steam",
        "Epic Games",
        "GOG",
    },
    MediaType.MOVIE: {
        "Netflix",
        "Amazon Prime",
        "Disney+",
        "Apple TV+",
        "HBO Max",
        "Hulu",
        "Crunchyroll",
        "Ororo.tv",
        "Cinema",
        "Blu-ray",
        "DVD",
    },
}

# Platform aliases to normalize user input
MOVIE_PLATFORM_ALIASES = {
    "amazon": "Amazon Prime",
    "amazon prime": "Amazon Prime",
    "netflix": "Netflix",
    "apple tv": "Apple TV+",
    "apple tv+": "Apple TV+",
    "disney": "Disney+",
    "disney+": "Disney+",
    "hbo": "HBO Max",
    "hbo max": "HBO Max",
    "crunchyroll": "Crunchyroll",
    "ororo.tv": "Ororo.tv",
    "ororo": "Ororo.tv",
    "cinema": "Cinema",
    "blu-ray": "Blu-ray",
    "bluray": "Blu-ray",
    "dvd": "DVD",
    "hulu": "Hulu",
}


class TagSchema(BaseSchema):
    """Individual tag schema."""

    name: str = Field(..., min_length=1, max_length=settings.max_tag_length, description="Tag name")

    @field_validator("name")
    @classmethod
    def validate_tag_name(cls, value: str) -> str:
        """Validate and clean tag name."""
        cleaned = value.strip().lower()
        if not cleaned:
            raise ValueError("Tag name cannot be empty")
        if len(cleaned) > settings.max_tag_length:
            raise ValueError(f"Tag name too long (max {settings.max_tag_length} characters)")
        return cleaned


class MediaItemBase(BaseSchema):
    """Base media item schema with common fields."""

    type: Literal["game", "movie"] = Field(..., description="Type of media item")
    title: str = Field(
        ...,
        min_length=1,
        max_length=settings.max_title_length,
        description="Title of the media item",
    )
    platform: Optional[str] = Field(
        None,
        max_length=settings.max_platform_length,
        description="Platform where the media is available",
    )
    cover_url: Optional[str] = Field(None, alias="coverUrl", description="URL to cover image")
    tags: List[str] = Field(
        default_factory=list, description="List of tags", max_length=settings.max_tags_per_item
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        """Validate and clean title."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Title cannot be empty")
        return cleaned

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, value: Optional[str], info) -> Optional[str]:
        """Validate platform based on media type with alias support."""
        if value is None:
            return None

        cleaned = value.strip()
        if not cleaned:
            return None

        # Get the media type from the model data
        media_type = getattr(info, "data", {}).get("type") if info else None

        # For movies, normalize platform aliases
        if media_type == "movie":
            normalized = MOVIE_PLATFORM_ALIASES.get(cleaned.lower(), cleaned)
            return normalized

        return cleaned

    @field_validator("cover_url")
    @classmethod
    def validate_cover_url(cls, value: Optional[str]) -> Optional[str]:
        """Validate cover URL format."""
        if not value or not value.strip():
            return None

        value = value.strip()
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        if not url_pattern.match(value):
            raise ValueError("Invalid URL format")
        return value

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: List[str]) -> List[str]:
        """Validate and clean tags."""
        if not value:
            return []

        # Clean and validate tags
        cleaned_tags = []
        for tag in value:
            if isinstance(tag, str):
                clean_tag = tag.strip().lower()
                if clean_tag and len(clean_tag) <= settings.max_tag_length:
                    cleaned_tags.append(clean_tag)

        # Remove duplicates while preserving order
        seen = set()
        unique_tags = []
        for tag in cleaned_tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)

        # Limit number of tags
        return unique_tags[: settings.max_tags_per_item]

    @model_validator(mode="after")
    def validate_platform_for_type(self) -> "MediaItemBase":
        """Validate platform compatibility with media type."""
        if self.platform and self.type:
            valid_platforms = PLATFORM_MAPPINGS.get(self.type, set())
            if valid_platforms and self.platform not in valid_platforms:
                raise ValueError(
                    f'Invalid platform "{self.platform}" for type "{self.type}". '
                    f"Valid platforms: {', '.join(sorted(valid_platforms))}"
                )
        return self


class MediaItemCreate(MediaItemBase):
    """Schema for creating a new media item."""

    model_config = BaseSchema.model_config.copy()
    model_config.update(
        {
            "json_schema_extra": {
                "examples": [
                    {
                        "type": "game",
                        "title": "The Witcher 3: Wild Hunt",
                        "platform": "PC",
                        "coverUrl": "https://example.com/witcher3.jpg",
                        "tags": ["rpg", "open-world", "fantasy"],
                    },
                    {
                        "type": "movie",
                        "title": "Inception",
                        "platform": "Netflix",
                        "coverUrl": "https://example.com/inception.jpg",
                        "tags": ["sci-fi", "thriller", "christopher-nolan"],
                    },
                ]
            }
        }
    )


class MediaItemUpdate(BaseSchema):
    """Schema for updating an existing media item."""

    type: Optional[Literal["game", "movie"]] = Field(None, description="Type of media item")
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=settings.max_title_length,
        description="Title of the media item",
    )
    platform: Optional[str] = Field(
        None,
        max_length=settings.max_platform_length,
        description="Platform where the media is available",
    )
    cover_url: Optional[str] = Field(None, alias="coverUrl", description="URL to cover image")
    tags: Optional[List[str]] = Field(
        None, description="List of tags", max_length=settings.max_tags_per_item
    )
    status: Optional[Literal["active", "done", "archived"]] = Field(
        None, description="Status of the media item"
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: Optional[str]) -> Optional[str]:
        """Validate and clean title."""
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Title cannot be empty")
        return cleaned

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, value: Optional[str], info) -> Optional[str]:
        """Validate platform with alias support."""
        if value is None:
            return None

        cleaned = value.strip()
        if not cleaned:
            return None

        # Get the media type from the model data
        media_type = getattr(info, "data", {}).get("type") if info else None

        # For movies, normalize platform aliases
        if media_type == "movie":
            normalized = MOVIE_PLATFORM_ALIASES.get(cleaned.lower(), cleaned)
            return normalized

        return cleaned

    @field_validator("cover_url")
    @classmethod
    def validate_cover_url(cls, value: Optional[str]) -> Optional[str]:
        """Validate cover URL format."""
        if not value or not value.strip():
            return None

        value = value.strip()
        url_pattern = re.compile(
            r"^https?://"
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
            r"localhost|"
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
            r"(?::\d+)?"
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        if not url_pattern.match(value):
            raise ValueError("Invalid URL format")
        return value

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        """Validate and clean tags."""
        if value is None:
            return None

        if not value:
            return []

        # Clean and validate tags
        cleaned_tags = []
        for tag in value:
            if isinstance(tag, str):
                clean_tag = tag.strip().lower()
                if clean_tag and len(clean_tag) <= settings.max_tag_length:
                    cleaned_tags.append(clean_tag)

        # Remove duplicates while preserving order
        seen = set()
        unique_tags = []
        for tag in cleaned_tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)

        return unique_tags[: settings.max_tags_per_item]


class MediaItemResponse(BaseSchema):
    """Schema for media item responses."""

    id: str = Field(..., description="Unique identifier")
    type: str = Field(..., description="Type of media item")
    title: str = Field(..., description="Title of the media item")
    platform: Optional[str] = Field(None, description="Platform")
    cover_url: Optional[str] = Field(None, alias="coverUrl", description="Cover image URL")
    tags: List[str] = Field(default_factory=list, description="List of tags")
    status: str = Field(..., description="Status of the item")
    added_at: int = Field(..., alias="addedAt", description="Unix timestamp when item was added")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = BaseSchema.model_config.copy()
    model_config.update(
        {
            "from_attributes": True,
            "json_schema_extra": {
                "examples": [
                    {
                        "id": "abc123def456",
                        "type": "game",
                        "title": "The Witcher 3: Wild Hunt",
                        "platform": "PC",
                        "coverUrl": "https://example.com/witcher3.jpg",
                        "tags": ["rpg", "open-world", "fantasy"],
                        "status": "active",
                        "addedAt": 1640995200,
                        "created_at": "2022-01-01T00:00:00Z",
                        "updated_at": "2022-01-01T00:00:00Z",
                    }
                ]
            },
        }
    )


class SpinRequest(BaseSchema):
    """Schema for spin wheel requests."""

    type: Optional[Literal["game", "movie"]] = Field(None, description="Filter by media type")
    tags: Optional[str] = Field(None, description="Comma-separated tags to filter by")
    include_archived: bool = Field(False, description="Include archived items")
    status: Optional[Literal["active", "done", "archived"]] = Field(
        None, description="Filter by status"
    )


class SpinResponse(BaseSchema):
    """Schema for spin wheel responses."""

    winner: Optional[MediaItemResponse] = Field(None, description="Selected item")
    pool: List[MediaItemResponse] = Field(
        default_factory=list, description="Pool of items that were considered"
    )
    total_pool_size: int = Field(0, description="Total number of items in the pool")

    model_config = BaseSchema.model_config.copy()
    model_config.update(
        {
            "json_schema_extra": {
                "examples": [
                    {
                        "winner": {
                            "id": "abc123",
                            "type": "game",
                            "title": "The Witcher 3",
                            "platform": "PC",
                            "tags": ["rpg"],
                            "status": "active",
                            "addedAt": 1640995200,
                        },
                        "pool": [],
                        "total_pool_size": 10,
                    }
                ]
            }
        }
    )


class MediaItemFilter(BaseSchema):
    """Schema for filtering media items."""

    type: Optional[Literal["game", "movie"]] = Field(None, description="Filter by media type")
    tags: Optional[str] = Field(None, description="Comma-separated tags to filter by")
    include_archived: bool = Field(False, description="Include archived items")
    status: Optional[Literal["active", "done", "archived"]] = Field(
        None, description="Filter by status"
    )
    limit: Optional[int] = Field(None, ge=1, le=1000, description="Limit number of results")
    offset: Optional[int] = Field(None, ge=0, description="Offset for pagination")
    search: Optional[str] = Field(None, min_length=1, description="Search in title")

    @field_validator("search")
    @classmethod
    def validate_search(cls, value: Optional[str]) -> Optional[str]:
        """Validate search term."""
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned if cleaned else None
