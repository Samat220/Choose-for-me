"""Dependency injection for API endpoints."""

from fastapi import Depends
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..services.media_service import MediaItemService


def get_media_service(db: Session = Depends(get_db)) -> MediaItemService:
    """Get media item service with dependency injection."""
    return MediaItemService(db)
