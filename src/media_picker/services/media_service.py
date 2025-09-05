"""Media item service for business logic."""

import random
from typing import List, Optional

from sqlalchemy.orm import Session

from ..core.exceptions import ItemNotFoundError, ServiceError, ValidationError
from ..core.logging import get_logger
from ..db.repository import MediaItemRepository
from ..schemas.media import (
    MediaItemCreate,
    MediaItemFilter,
    MediaItemResponse,
    MediaItemUpdate,
    SpinRequest,
    SpinResponse,
)

logger = get_logger("media_service")


class MediaItemService:
    """Service class for media item business logic."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = MediaItemRepository(db)

    def get_all_items(
        self, filter_params: Optional[MediaItemFilter] = None
    ) -> List[MediaItemResponse]:
        """Get all media items with optional filtering."""
        try:
            if filter_params:
                items = self.repository.get_filtered(filter_params)
            else:
                items = self.repository.get_all()

            return [self._item_to_response(item) for item in items]
        except Exception as e:
            logger.error(f"Error getting all items: {e}")
            raise ServiceError(f"Failed to get items: {e}") from e

    def get_item_by_id(self, item_id: str) -> MediaItemResponse:
        """Get a specific media item by ID."""
        try:
            item = self.repository.get_by_id(item_id)
            if not item:
                raise ItemNotFoundError(item_id)
            return self._item_to_response(item)
        except ItemNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting item {item_id}: {e}")
            raise ServiceError(f"Failed to get item: {e}") from e

    def create_item(self, item_data: MediaItemCreate) -> MediaItemResponse:
        """Create a new media item."""
        try:
            # Validate the data (Pydantic already does basic validation)
            self._validate_create_data(item_data)

            # Convert to dict for repository
            data = item_data.model_dump(by_alias=True)

            # Create the item
            item = self.repository.create(data)

            logger.info(f"Created new media item: {item.id} - {item.title}")
            return self._item_to_response(item)
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error creating item: {e}")
            raise ServiceError(f"Failed to create item: {e}") from e

    def update_item(self, item_id: str, update_data: MediaItemUpdate) -> MediaItemResponse:
        """Update an existing media item."""
        try:
            # Validate the update data
            self._validate_update_data(update_data)

            # Get only non-None fields for partial update
            data = update_data.model_dump(by_alias=True, exclude_none=True)

            if not data:
                raise ValidationError("No valid fields provided for update")

            # Update the item
            item = self.repository.update(item_id, data)

            logger.info(f"Updated media item: {item.id} - {item.title}")
            return self._item_to_response(item)
        except (ItemNotFoundError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error updating item {item_id}: {e}")
            raise ServiceError(f"Failed to update item: {e}") from e

    def delete_item(self, item_id: str) -> bool:
        """Delete a media item (soft delete)."""
        try:
            success = self.repository.delete(item_id)
            if success:
                logger.info(f"Deleted media item: {item_id}")
            return success
        except ItemNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error deleting item {item_id}: {e}")
            raise ServiceError(f"Failed to delete item: {e}") from e

    def spin_wheel(self, spin_request: SpinRequest) -> SpinResponse:
        """Spin the wheel to get a random item."""
        try:
            # Convert spin request to filter
            filter_params = MediaItemFilter(
                type=spin_request.type,
                tags=spin_request.tags,
                include_archived=spin_request.include_archived,
                status=spin_request.status,
                limit=None,
                offset=None,
                search=None,
            )

            # 1) Get filtered DB items
            items = self.repository.get_filtered(filter_params)

            # 2) Build response pool (for the wheel)
            pool_responses = [self._item_to_response(item) for item in items]

            # 3) Choose winner from raw items, then convert once
            winner_response = None
            if items:
                chosen_item = random.choice(items)  # may be patched in tests
                winner_response = self._item_to_response(chosen_item)
                logger.info(f"Spin wheel selected: {winner_response.id} - {winner_response.title}")
            else:
                logger.info("Spin wheel found no items in pool")

            return SpinResponse(
                winner=winner_response,
                pool=pool_responses,
                total_pool_size=len(pool_responses),
            )
        except Exception as e:
            logger.error(f"Error spinning wheel: {e}")
            raise ServiceError(f"Failed to spin wheel: {e}") from e

    def get_statistics(self) -> dict:
        """Get media library statistics."""
        try:
            stats = {
                "total": self.repository.count_total(),
                "active": self.repository.count_by_status("active"),
                "done": self.repository.count_by_status("done"),
                "archived": self.repository.count_by_status("archived"),
                "games": len(self.repository.get_by_type("game")),
                "movies": len(self.repository.get_by_type("movie")),
            }
            return stats
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            raise ServiceError(f"Failed to get statistics: {e}") from e

    def _item_to_response(self, item) -> MediaItemResponse:
        """Convert database item to response schema."""
        # Handle None values for testing (fallback to current timestamp)
        added_at_value = item.added_at
        if added_at_value is None:
            import time
            added_at_value = int(time.time())
        
        return MediaItemResponse(
            id=item.id,
            type=item.type,
            title=item.title,
            platform=item.platform,
            coverUrl=item.cover_url,  # Use alias field name
            tags=item.tags,
            status=item.status,
            addedAt=added_at_value,  # Use alias field name
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    def _validate_create_data(self, data: MediaItemCreate) -> None:
        """Validate data for creating a new item."""
        # Additional business logic validation can go here
        # For example, checking if title already exists

    def _validate_update_data(self, data: MediaItemUpdate) -> None:
        """Validate data for updating an item."""
        # Additional business logic validation can go here
