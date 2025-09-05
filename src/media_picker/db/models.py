"""SQLAlchemy models for the media picker application."""

import json
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def generate_id() -> str:
    """Generate a unique identifier."""
    return uuid.uuid4().hex


class MediaItem(Base):
    """Media item model with enhanced features."""

    __tablename__ = "media_items"

    # Primary fields
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_id, index=True)
    type: Mapped[str] = mapped_column(
        String(10), nullable=False, index=True, comment="Type of media: game or movie"
    )
    title: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True, comment="Title of the media item"
    )
    platform: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, index=True, comment="Platform where media is available"
    )
    cover_url: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="URL to cover image"
    )

    # JSON field for tags (better than comma-separated string)
    tags_json: Mapped[Optional[Any]] = mapped_column(
        JSON, nullable=True, comment="JSON array of tags"
    )

    # Status and metadata
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        index=True,
        comment="Status: active, done, or archived",
    )
    added_at: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=lambda: int(time.time()),
        index=True,
        comment="Unix timestamp when item was added",
    )

    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Creation timestamp",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Last update timestamp",
    )

    # Soft delete support
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True, comment="Soft delete flag"
    )

    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<MediaItem(id='{self.id}', title='{self.title}', type='{self.type}')>"

    @property
    def tags(self) -> List[str]:
        """Get tags as a list."""
        if self.tags_json:
            try:
                if isinstance(self.tags_json, list):
                    return [str(tag) for tag in self.tags_json if isinstance(tag, str)]
                if isinstance(self.tags_json, str):
                    parsed = json.loads(self.tags_json)
                    if isinstance(parsed, list):
                        return [str(tag) for tag in parsed if isinstance(tag, str)]
                return []
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    @tags.setter
    def tags(self, value: List[str]) -> None:
        """Set tags from a list."""
        if value:
            # Clean and validate tags
            clean_tags = []
            for tag in value:
                if isinstance(tag, str) and tag.strip():
                    clean_tags.append(tag.strip().lower())

            # Remove duplicates while preserving order
            seen = set()
            unique_tags = []
            for tag in clean_tags:
                if tag not in seen:
                    seen.add(tag)
                    unique_tags.append(tag)

            self.tags_json = unique_tags
        else:
            self.tags_json = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "platform": self.platform,
            "coverUrl": self.cover_url,
            "tags": self.tags,
            "status": self.status,
            "addedAt": self.added_at,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update model from dictionary."""
        # Map external field names to internal ones
        field_mapping = {
            "coverUrl": "cover_url",
            "addedAt": "added_at",
        }

        has_updates = False
        for key, value in data.items():
            # Skip None values and computed fields
            if value is None or key in ("id", "created_at", "updated_at"):
                continue

            # Map field name
            field_name = field_mapping.get(key, key)

            # Special handling for tags
            if key == "tags" and hasattr(self, "tags"):
                self.tags = value
                has_updates = True
            elif hasattr(self, field_name):
                setattr(self, field_name, value)
                has_updates = True

        # Set updated_at timestamp if there were updates
        if has_updates:
            self.updated_at = datetime.now()

    @classmethod
    def create_from_dict(cls, data: Dict[str, Any]) -> "MediaItem":
        """Create new instance from dictionary."""
        # Extract and map fields
        field_mapping = {
            "coverUrl": "cover_url",
            "addedAt": "added_at",
        }

        mapped_data = {}
        tags_value = None

        # Filter out invalid fields and apply mappings
        for key, value in data.items():
            if key == "tags":
                tags_value = value
            elif key in field_mapping:
                mapped_data[field_mapping[key]] = value
            elif key in (
                "type",
                "title",
                "platform",
                "cover_url",
                "status",
                "added_at",
                "is_deleted",
            ):
                mapped_data[key] = value
            # Ignore unknown fields silently

        # Set defaults for required fields if not provided
        if "status" not in mapped_data:
            mapped_data["status"] = "active"
        if "is_deleted" not in mapped_data:
            mapped_data["is_deleted"] = False
        if "added_at" not in mapped_data:
            mapped_data["added_at"] = int(time.time())

        # Don't set id, created_at, updated_at - let SQLAlchemy handle defaults
        # Create instance
        instance = cls(**mapped_data)

        # Set tags separately (defaults to empty list in property)
        if tags_value is not None:
            instance.tags = tags_value

        return instance
