"""API endpoints for media items."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from ..core.exceptions import ItemNotFoundError, ServiceError, ValidationError
from ..core.logging import get_logger
from ..schemas.media import (
    MediaItemCreate,
    MediaItemFilter,
    MediaItemResponse,
    MediaItemUpdate,
    SpinRequest,
    SpinResponse,
)
from ..services.media_service import MediaItemService
from .dependencies import get_media_service

logger = get_logger("api.media")

router = APIRouter(prefix="/api", tags=["media"])


@router.get("/items", response_model=List[MediaItemResponse])
async def get_items(
    type: Optional[str] = Query(None, regex="^(game|movie)$", description="Filter by media type"),
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter by"),
    include_archived: bool = Query(False, description="Include archived items"),
    includeArchived: Optional[bool] = Query(None, description="Include archived items (legacy parameter)"),
    status: Optional[str] = Query(
        None, 
        regex="^(active|done|archived)$", 
        description="Filter by status"
    ),
    search: Optional[str] = Query(None, min_length=1, description="Search in titles"),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit results"),
    offset: Optional[int] = Query(None, ge=0, description="Offset for pagination"),
    service: MediaItemService = Depends(get_media_service),
) -> List[MediaItemResponse]:
    """Get filtered list of media items."""
    try:
        # Support both parameter names for backward compatibility
        include_arch = includeArchived if includeArchived is not None else include_archived
        
        filter_params = MediaItemFilter(
            type=type,
            tags=tags,
            include_archived=include_arch,
            status=status,
            search=search,
            limit=limit,
            offset=offset,
        )
        
        items = service.get_all_items(filter_params)
        logger.info(f"Retrieved {len(items)} media items")
        return items
    except Exception as e:
        logger.error(f"Error retrieving items: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve items") from e


@router.get("/items/{item_id}", response_model=MediaItemResponse)
async def get_item(
    item_id: str,
    service: MediaItemService = Depends(get_media_service),
) -> MediaItemResponse:
    """Get a specific media item by ID."""
    try:
        item = service.get_item_by_id(item_id)
        logger.info(f"Retrieved media item: {item_id}")
        return item
    except ItemNotFoundError:
        raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        logger.error(f"Error retrieving item {item_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve item") from e


@router.post("/items", response_model=MediaItemResponse, status_code=201)
async def create_item(
    item_data: MediaItemCreate,
    service: MediaItemService = Depends(get_media_service),
) -> MediaItemResponse:
    """Create a new media item."""
    try:
        item = service.create_item(item_data)
        logger.info(f"Created media item: {item.id}")
        return item
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating item: {e}")
        raise HTTPException(status_code=500, detail="Failed to create item") from e


@router.patch("/items/{item_id}", response_model=MediaItemResponse)
async def update_item(
    item_id: str,
    update_data: MediaItemUpdate,
    service: MediaItemService = Depends(get_media_service),
) -> MediaItemResponse:
    """Update an existing media item."""
    try:
        item = service.update_item(item_id, update_data)
        logger.info(f"Updated media item: {item_id}")
        return item
    except ItemNotFoundError:
        raise HTTPException(status_code=404, detail="Item not found")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating item {item_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update item") from e


@router.delete("/items", status_code=204)
async def delete_item_by_query(
    id: str = Query(..., description="ID of the item to delete"),
    service: MediaItemService = Depends(get_media_service),
) -> None:
    """Delete a media item by query parameter (backward compatibility)."""
    try:
        success = service.delete_item(id)
        if success:
            logger.info(f"Deleted media item: {id}")
    except ItemNotFoundError:
        raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        logger.error(f"Error deleting item {id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete item") from e


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(
    item_id: str,
    service: MediaItemService = Depends(get_media_service),
) -> None:
    """Delete a media item."""
    try:
        success = service.delete_item(item_id)
        if success:
            logger.info(f"Deleted media item: {item_id}")
    except ItemNotFoundError:
        raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        logger.error(f"Error deleting item {item_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete item") from e


@router.get("/spin", response_model=SpinResponse)
async def spin_wheel(
    type: Optional[str] = Query(None, regex="^(game|movie)$", description="Filter by media type"),
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter by"),
    include_archived: bool = Query(False, description="Include archived items"),
    status: Optional[str] = Query(
        None, 
        regex="^(active|done|archived)$", 
        description="Filter by status"
    ),
    service: MediaItemService = Depends(get_media_service),
) -> SpinResponse:
    """Spin the wheel to get a random item."""
    try:
        spin_request = SpinRequest(
            type=type,
            tags=tags,
            include_archived=include_archived,
            status=status,
        )
        
        result = service.spin_wheel(spin_request)
        logger.info(f"Spin wheel completed with {result.total_pool_size} items in pool")
        return result
    except Exception as e:
        logger.error(f"Error spinning wheel: {e}")
        raise HTTPException(status_code=500, detail="Failed to spin wheel") from e


@router.get("/statistics")
async def get_statistics(
    service: MediaItemService = Depends(get_media_service),
) -> dict:
    """Get media library statistics."""
    try:
        stats = service.get_statistics()
        logger.info("Retrieved media library statistics")
        return stats
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics") from e
