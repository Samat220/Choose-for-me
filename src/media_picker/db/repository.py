"""Repository pattern implementation for data access."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from ..core.exceptions import DatabaseError, ItemNotFoundError
from ..core.logging import get_logger
from ..schemas.media import MediaItemFilter
from .models import MediaItem

logger = get_logger("repository")

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository class."""

    def __init__(self, db: Session, model: Type[T]) -> None:
        self.db = db
        self.model = model

    @abstractmethod
    def get_by_id(self, id: str) -> Optional[T]:
        """Get item by ID."""

    @abstractmethod
    def get_all(self) -> List[T]:
        """Get all items."""

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> T:
        """Create new item."""

    @abstractmethod
    def update(self, id: str, data: Dict[str, Any]) -> T:
        """Update existing item."""

    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete item."""


class MediaItemRepository(BaseRepository[MediaItem]):
    """Repository for media items with advanced filtering."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, MediaItem)

    def get_by_id(self, id: str) -> Optional[MediaItem]:
        """Get media item by ID."""
        try:
            return (
                self.db.query(MediaItem)
                .filter(and_(MediaItem.id == id, not MediaItem.is_deleted))
                .first()
            )
        except Exception as e:
            logger.error(f"Error getting item by ID {id}: {e}")
            raise DatabaseError(f"Failed to get item: {e}") from e

    def get_all(self) -> List[MediaItem]:
        """Get all non-deleted media items."""
        try:
            return (
                self.db.query(MediaItem)
                .filter(not MediaItem.is_deleted)
                .order_by(desc(MediaItem.added_at))
                .all()
            )
        except Exception as e:
            logger.error(f"Error getting all items: {e}")
            raise DatabaseError(f"Failed to get items: {e}") from e

    def get_filtered(self, filter_params: MediaItemFilter) -> List[MediaItem]:
        """Get filtered media items."""
        try:
            query = self.db.query(MediaItem).filter(not MediaItem.is_deleted)

            # Filter by type
            if filter_params.type:
                query = query.filter(MediaItem.type == filter_params.type)

            # Filter by status
            if filter_params.status:
                query = query.filter(MediaItem.status == filter_params.status)
            elif not filter_params.include_archived:
                query = query.filter(MediaItem.status != "archived")

            # Search in title
            if filter_params.search:
                search_term = f"%{filter_params.search.lower()}%"
                query = query.filter(MediaItem.title.ilike(search_term))

            # Order by added_at desc
            query = query.order_by(desc(MediaItem.added_at))

            # Apply pagination
            if filter_params.offset:
                query = query.offset(filter_params.offset)
            if filter_params.limit:
                query = query.limit(filter_params.limit)

            items = query.all()

            # Filter by tags if specified (post-query filtering for JSON tags)
            if filter_params.tags:
                tag_filters = [tag.strip().lower() for tag in filter_params.tags.split(",")]
                filtered_items = []
                for item in items:
                    item_tags = [tag.lower() for tag in item.tags]
                    if any(tag in item_tags for tag in tag_filters):
                        filtered_items.append(item)
                return filtered_items

            return items

        except Exception as e:
            logger.error(f"Error filtering items: {e}")
            raise DatabaseError(f"Failed to filter items: {e}") from e

    def create(self, data: Dict[str, Any]) -> MediaItem:
        """Create new media item."""
        try:
            item = MediaItem.create_from_dict(data)
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            logger.info(f"Created media item: {item.id}")
            return item
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating item: {e}")
            raise DatabaseError(f"Failed to create item: {e}") from e

    def update(self, id: str, data: Dict[str, Any]) -> MediaItem:
        """Update existing media item."""
        try:
            item = self.get_by_id(id)
            if not item:
                raise ItemNotFoundError(id)

            item.update_from_dict(data)
            self.db.commit()
            self.db.refresh(item)
            logger.info(f"Updated media item: {item.id}")
            return item
        except ItemNotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating item {id}: {e}")
            raise DatabaseError(f"Failed to update item: {e}") from e

    def delete(self, id: str) -> bool:
        """Soft delete media item."""
        try:
            item = self.get_by_id(id)
            if not item:
                raise ItemNotFoundError(id)

            item.is_deleted = True
            self.db.commit()
            logger.info(f"Deleted media item: {item.id}")
            return True
        except ItemNotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting item {id}: {e}")
            raise DatabaseError(f"Failed to delete item: {e}") from e

    def hard_delete(self, id: str) -> bool:
        """Permanently delete media item."""
        try:
            item = self.get_by_id(id)
            if not item:
                raise ItemNotFoundError(id)

            self.db.delete(item)
            self.db.commit()
            logger.info(f"Hard deleted media item: {id}")
            return True
        except ItemNotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error hard deleting item {id}: {e}")
            raise DatabaseError(f"Failed to hard delete item: {e}") from e

    def get_by_status(self, status: str) -> List[MediaItem]:
        """Get items by status."""
        try:
            return (
                self.db.query(MediaItem)
                .filter(and_(MediaItem.status == status, not MediaItem.is_deleted))
                .order_by(desc(MediaItem.added_at))
                .all()
            )
        except Exception as e:
            logger.error(f"Error getting items by status {status}: {e}")
            raise DatabaseError(f"Failed to get items by status: {e}") from e

    def get_by_type(self, type: str) -> List[MediaItem]:
        """Get items by type."""
        try:
            return (
                self.db.query(MediaItem)
                .filter(and_(MediaItem.type == type, not MediaItem.is_deleted))
                .order_by(desc(MediaItem.added_at))
                .all()
            )
        except Exception as e:
            logger.error(f"Error getting items by type {type}: {e}")
            raise DatabaseError(f"Failed to get items by type: {e}") from e

    def count_total(self) -> int:
        """Count total non-deleted items."""
        try:
            return self.db.query(MediaItem).filter(~MediaItem.is_deleted).count()
        except Exception as e:
            logger.error(f"Error counting items: {e}")
            raise DatabaseError(f"Failed to count items: {e}") from e

    def count_by_status(self, status: str) -> int:
        """Count items by status."""
        try:
            return (
                self.db.query(MediaItem)
                .filter(and_(MediaItem.status == status, ~MediaItem.is_deleted))
                .count()
            )
        except Exception as e:
            logger.error(f"Error counting items by status {status}: {e}")
            raise DatabaseError(f"Failed to count items by status: {e}") from e
