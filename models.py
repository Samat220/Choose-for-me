import json
import re
from typing import Literal

from pydantic import BaseModel, Field, validator


class MediaItemCreate(BaseModel):
    type: Literal["game", "movie"] = Field(..., description="Type of media item")
    title: str = Field(..., min_length=1, max_length=200, description="Title of the media item")
    platform: str | None = Field(
        None, max_length=50, description="Platform where the media is available"
    )
    coverUrl: str | None = Field(None, description="URL to cover image")
    tags: list[str] = Field(default_factory=list, description="List of tags")

    @validator("title")
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @validator("platform")
    def validate_platform(cls, v, values):
        if v is None:
            return v

        platforms = {
            "game": ["PC", "PlayStation", "Xbox", "Nintendo"],
            "movie": ["Netflix", "Amazon", "Apple TV", "Crunchyroll", "Ororo.tv"],
        }

        media_type = values.get("type")
        if media_type and v not in platforms.get(media_type, []):
            raise ValueError(f'Invalid platform "{v}" for type "{media_type}"')

        return v

    @validator("coverUrl")
    def validate_cover_url(cls, v):
        if v is None or v.strip() == "":
            return None

        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        if not url_pattern.match(v):
            raise ValueError("Invalid URL format")

        return v.strip()

    @validator("tags")
    def validate_tags(cls, v):
        if not v:
            return []

        # Clean and validate tags
        cleaned_tags = []
        for tag in v:
            if isinstance(tag, str):
                clean_tag = tag.strip()
                if clean_tag and len(clean_tag) <= 30:
                    cleaned_tags.append(clean_tag)

        # Remove duplicates while preserving order
        seen = set()
        unique_tags = []
        for tag in cleaned_tags:
            if tag.lower() not in seen:
                seen.add(tag.lower())
                unique_tags.append(tag)

        return unique_tags[:10]  # Limit to 10 tags


class MediaItemUpdate(BaseModel):
    type: Literal["game", "movie"] | None = None
    title: str | None = Field(None, min_length=1, max_length=200)
    platform: str | None = Field(None, max_length=50)
    coverUrl: str | None = None
    tags: list[str] | None = None
    status: Literal["active", "done", "archived"] | None = None

    @validator("title")
    def validate_title(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip() if v else v

    @validator("platform")
    def validate_platform(cls, v, values):
        if v is None:
            return v

        platforms = {
            "game": ["PC", "PlayStation", "Xbox", "Nintendo"],
            "movie": ["Netflix", "Amazon", "Apple TV", "Crunchyroll", "Ororo.tv"],
        }

        media_type = values.get("type")
        if media_type and v not in platforms.get(media_type, []):
            raise ValueError(f'Invalid platform "{v}" for type "{media_type}"')

        return v


class MediaItemResponse(BaseModel):
    id: str
    type: str
    title: str
    platform: str | None = None
    coverUrl: str | None = None
    tags: list[str] = []
    status: str
    addedAt: int

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, db_item):
        return cls(
            id=db_item.id,
            type=db_item.type,
            title=db_item.title,
            platform=db_item.platform,
            coverUrl=db_item.cover_url,
            tags=json.loads(db_item.tags) if db_item.tags else [],
            status=db_item.status,
            addedAt=db_item.added_at,
        )


class SpinResponse(BaseModel):
    winner: MediaItemResponse | None
    pool: list[MediaItemResponse]
