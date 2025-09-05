"""Tests for media schemas"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from src.media_picker.schemas.media import (
    MediaItemCreate,
    MediaItemUpdate,
    MediaItemResponse,
    MediaItemFilter,
    SpinRequest,
    SpinResponse,
    MediaType,
    MediaStatus
)


class TestMediaItemCreate:
    """Test MediaItemCreate schema"""

    def test_minimal_creation(self):
        """Test creating with minimal required fields"""
        data = MediaItemCreate(
            type="game",
            title="Test Game"
        )
        assert data.type == "game"
        assert data.title == "Test Game"
        assert data.platform is None
        assert data.cover_url is None
        assert data.tags == []

    def test_full_creation(self):
        """Test creating with all fields"""
        data = MediaItemCreate(
            type="movie",
            title="Test Movie",
            platform="Netflix",
            coverUrl="https://example.com/cover.jpg",
            tags=["action", "thriller"]
        )
        assert data.type == "movie"
        assert data.title == "Test Movie"
        assert data.platform == "Netflix"
        assert data.cover_url == "https://example.com/cover.jpg"
        assert data.tags == ["action", "thriller"]

    def test_invalid_type(self):
        """Test validation fails for invalid type"""
        with pytest.raises(ValidationError):
            MediaItemCreate(
                type="invalid",
                title="Test",
                platform="PC",
                coverUrl="https://example.com/cover.jpg"
            )

    def test_invalid_status(self):
        """Test validation fails for invalid status"""
        with pytest.raises(ValidationError):
            MediaItemCreate(
                type="game",
                title="Test Game",
                platform="PC",
                coverUrl="https://example.com/cover.jpg",
                status="invalid"
            )

    def test_empty_title(self):
        """Test validation fails for empty title"""
        with pytest.raises(ValidationError):
            MediaItemCreate(
                type="game",
                title="",
                platform="PC",
                coverUrl="https://example.com/cover.jpg"
            )

    def test_tags_normalization(self):
        """Test that tags are normalized"""
        data = MediaItemCreate(
            type="game",
            title="Test Game",
            platform="PC",
            coverUrl="https://example.com/cover.jpg",
            tags=["Action", "RPG", "action", ""]
        )
        # Tags should be lowercased and deduplicated
        assert "action" in data.tags
        assert "rpg" in data.tags
        assert len([t for t in data.tags if t == "action"]) == 1


class TestMediaItemUpdate:
    """Test MediaItemUpdate schema"""

    def test_partial_update(self):
        """Test updating with partial fields"""
        data = MediaItemUpdate(title="Updated Title")
        assert data.title == "Updated Title"
        assert data.type is None
        assert data.platform is None

    def test_status_update(self):
        """Test updating status"""
        data = MediaItemUpdate(status="done")
        assert data.status == "done"

    def test_tags_update(self):
        """Test updating tags"""
        data = MediaItemUpdate(tags=["new", "tags"])
        assert data.tags == ["new", "tags"]

    def test_invalid_status_update(self):
        """Test validation fails for invalid status in update"""
        with pytest.raises(ValidationError):
            MediaItemUpdate(status="invalid")


class TestMediaItemResponse:
    """Test MediaItemResponse schema"""

    def test_response_creation(self):
        """Test creating response schema"""
        import time
        now_timestamp = int(time.time())
        now_datetime = datetime.now()
        data = MediaItemResponse(
            id="test-id",
            type="game",
            title="Test Game",
            platform="PC",
            coverUrl="https://example.com/cover.jpg",
            tags=["action"],
            status="active",
            addedAt=now_timestamp,
            created_at=now_datetime,
            updated_at=now_datetime
        )
        assert data.id == "test-id"
        assert data.type == "game"
        assert data.title == "Test Game"
        assert isinstance(data.added_at, int)


class TestMediaItemFilter:
    """Test MediaItemFilter schema"""

    def test_empty_filter(self):
        """Test creating empty filter"""
        filter_data = MediaItemFilter()
        assert filter_data.type is None
        assert filter_data.tags is None
        assert filter_data.include_archived is False
        assert filter_data.status is None

    def test_type_filter(self):
        """Test filtering by type"""
        filter_data = MediaItemFilter(type="game")
        assert filter_data.type == "game"

    def test_tags_filter(self):
        """Test filtering by tags"""
        filter_data = MediaItemFilter(tags="action,rpg")
        assert filter_data.tags == "action,rpg"

    def test_status_filter(self):
        """Test filtering by status"""
        filter_data = MediaItemFilter(status="active")
        assert filter_data.status == "active"

    def test_pagination(self):
        """Test pagination parameters"""
        filter_data = MediaItemFilter(limit=10, offset=20)
        assert filter_data.limit == 10
        assert filter_data.offset == 20

    def test_search_filter(self):
        """Test search parameter"""
        filter_data = MediaItemFilter(search="test query")
        assert filter_data.search == "test query"


class TestSpinRequest:
    """Test SpinRequest schema"""

    def test_empty_spin_request(self):
        """Test creating empty spin request"""
        request = SpinRequest()
        assert request.type is None
        assert request.tags is None
        assert request.include_archived is False
        assert request.status is None

    def test_filtered_spin_request(self):
        """Test creating filtered spin request"""
        request = SpinRequest(
            type="game",
            tags="action,rpg",
            include_archived=True,
            status="active"
        )
        assert request.type == "game"
        assert request.tags == "action,rpg"
        assert request.include_archived is True
        assert request.status == "active"


class TestSpinResponse:
    """Test SpinResponse schema"""

    def test_spin_response_with_winner(self):
        """Test spin response with winner"""
        import time
        now_timestamp = int(time.time())
        now_datetime = datetime.now()
        winner = MediaItemResponse(
            id="test-id",
            type="game",
            title="Test Game",
            platform="PC",
            coverUrl="https://example.com/cover.jpg",
            tags=["action"],
            status="active",
            addedAt=now_timestamp,
            created_at=now_datetime,
            updated_at=now_datetime
        )
        pool = [winner]
        
        response = SpinResponse(
            winner=winner,
            pool=pool,
            total_pool_size=1
        )
        
        assert response.winner == winner
        assert response.pool == pool
        assert response.total_pool_size == 1

    def test_spin_response_no_winner(self):
        """Test spin response with no winner"""
        response = SpinResponse(
            winner=None,
            pool=[],
            total_pool_size=0
        )
        
        assert response.winner is None
        assert response.pool == []
        assert response.total_pool_size == 0


class TestMediaConstants:
    """Test media type and status constants"""

    def test_media_type_constants(self):
        """Test MediaType constants"""
        assert MediaType.GAME == "game"
        assert MediaType.MOVIE == "movie"

    def test_media_status_constants(self):
        """Test MediaStatus constants"""
        assert MediaStatus.ACTIVE == "active"
        assert MediaStatus.DONE == "done"
        assert MediaStatus.ARCHIVED == "archived"
