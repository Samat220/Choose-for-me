"""Tests for the database repository layer"""
import contextlib
import os
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.media_picker.db.database import Base
from src.media_picker.db.repository import MediaItemRepository
from src.media_picker.db.models import MediaItem
from src.media_picker.schemas.media import MediaItemCreate, MediaItemUpdate, MediaItemFilter


class TestMediaItemRepository:
    """Test the MediaItemRepository class"""

    @pytest.fixture
    def db_session(self):
        """Create a test database session"""
        # Create a temporary file for the test database
        db_fd, db_path = tempfile.mkstemp()
        database_url = f"sqlite:///{db_path}"

        engine = create_engine(database_url, connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        Base.metadata.create_all(bind=engine)

        session = TestingSessionLocal()
        yield session

        # Clean up
        session.close()
        os.close(db_fd)
        with contextlib.suppress(PermissionError, FileNotFoundError):
            os.unlink(db_path)

    @pytest.fixture
    def repository(self, db_session):
        """Create a MediaItemRepository instance with test database"""
        return MediaItemRepository(db_session)

    def test_create_item(self, repository, db_session):
        """Test creating a new media item"""
        # Setup
        item_data = MediaItemCreate(
            title="Test Game",
            type="game",
            platform="PC",
            coverUrl="https://example.com/cover.jpg",
            tags=["rpg", "fantasy"]
        )

        # Execute
        result = repository.create(item_data.model_dump(by_alias=True))

        # Assert
        assert result is not None
        assert result.title == "Test Game"
        assert result.type == "game"
        assert result.platform == "PC"
        assert result.cover_url == "https://example.com/cover.jpg"
        assert result.tags == ["rpg", "fantasy"]
        assert result.status == "active"  # Default status
        assert result.id is not None

    def test_get_all_no_filters(self, repository, db_session):
        """Test getting all items without filters"""
        # Setup - create test items
        items_data = [
            {"title": "Game 1", "type": "game", "platform": "PC", "coverUrl": "https://example.com/1.jpg", "tags": ["rpg"]},
            {"title": "Movie 1", "type": "movie", "platform": "Netflix", "coverUrl": "https://example.com/2.jpg", "tags": ["action"]},
        ]
        for item_data in items_data:
            repository.create(item_data)
        
        # Create an archived item separately
        archived_item = repository.create({"title": "Archived Game", "type": "game", "platform": "PC", "coverUrl": "https://example.com/3.jpg"})
        archived_item.status = "archived"
        db_session.commit()

        # Execute
        result = repository.get_all()

        # Assert - get_all() returns all non-deleted items regardless of status
        assert len(result) == 3  # All items including archived
        titles = [item.title for item in result]
        assert "Game 1" in titles
        assert "Movie 1" in titles
        assert "Archived Game" in titles

    def test_get_filtered_include_archived(self, repository, db_session):
        """Test getting filtered items including archived"""
        # Setup
        items_data = [
            {"title": "Active Game", "type": "game", "platform": "PC", "coverUrl": "https://example.com/1.jpg"},
        ]
        for item_data in items_data:
            repository.create(item_data)
            
        # Create an archived item
        archived_item = repository.create({"title": "Archived Game", "type": "game", "platform": "PC", "coverUrl": "https://example.com/2.jpg"})
        archived_item.status = "archived"
        db_session.commit()

        # Execute
        filter_params = MediaItemFilter(include_archived=True)
        result = repository.get_filtered(filter_params)

        # Assert
        assert len(result) == 2
        titles = [item.title for item in result]
        assert "Active Game" in titles
        assert "Archived Game" in titles

    def test_get_filtered_type_filter(self, repository, db_session):
        """Test filtering items by type"""
        # Setup
        items_data = [
            {"title": "Game 1", "type": "game", "platform": "PC", "coverUrl": "https://example.com/1.jpg"},
            {"title": "Movie 1", "type": "movie", "platform": "Netflix", "coverUrl": "https://example.com/2.jpg"},
            {"title": "Game 2", "type": "game", "platform": "PlayStation", "coverUrl": "https://example.com/3.jpg"},
        ]
        for item_data in items_data:
            repository.create(item_data)

        # Execute
        filter_params = MediaItemFilter(type="game")
        result = repository.get_filtered(filter_params)

        # Assert
        assert len(result) == 2
        for item in result:
            assert item.type == "game"

    def test_get_filtered_tags_filter_single(self, repository, db_session):
        """Test filtering items by single tag"""
        # Setup
        items_data = [
            {"title": "RPG Game", "type": "game", "platform": "PC", "coverUrl": "https://example.com/1.jpg", "tags": ["rpg", "fantasy"]},
            {"title": "Action Game", "type": "game", "platform": "PC", "coverUrl": "https://example.com/2.jpg", "tags": ["action", "shooter"]},
            {"title": "RPG Movie", "type": "movie", "platform": "Netflix", "coverUrl": "https://example.com/3.jpg", "tags": ["rpg", "drama"]},
        ]
        for item_data in items_data:
            repository.create(item_data)

        # Execute
        filter_params = MediaItemFilter(tags="rpg")
        result = repository.get_filtered(filter_params)

        # Assert
        assert len(result) == 2
        titles = [item.title for item in result]
        assert "RPG Game" in titles
        assert "RPG Movie" in titles

    def test_get_filtered_tags_filter_multiple_and(self, repository, db_session):
        """Test filtering items by multiple tags (AND logic)"""
        # Setup
        items_data = [
            {"title": "RPG Fantasy Game", "type": "game", "platform": "PC", "coverUrl": "https://example.com/1.jpg", "tags": ["rpg", "fantasy"]},
            {"title": "RPG Action Game", "type": "game", "platform": "PC", "coverUrl": "https://example.com/2.jpg", "tags": ["rpg", "action"]},
            {"title": "Fantasy Adventure", "type": "game", "platform": "PC", "coverUrl": "https://example.com/3.jpg", "tags": ["fantasy", "adventure"]},
        ]
        for item_data in items_data:
            repository.create(item_data)

        # Execute - should return only items that have BOTH rpg AND fantasy tags
        filter_params = MediaItemFilter(tags="rpg,fantasy")
        result = repository.get_filtered(filter_params)

        # Assert
        assert len(result) == 1
        assert result[0].title == "RPG Fantasy Game"

    def test_get_filtered_combined_filters(self, repository, db_session):
        """Test combining type and tags filters"""
        # Setup
        items_data = [
            {"title": "RPG Game", "type": "game", "platform": "PC", "coverUrl": "https://example.com/1.jpg", "tags": ["rpg"]},
            {"title": "RPG Movie", "type": "movie", "platform": "Netflix", "coverUrl": "https://example.com/2.jpg", "tags": ["rpg"]},
            {"title": "Action Game", "type": "game", "platform": "PC", "coverUrl": "https://example.com/3.jpg", "tags": ["action"]},
        ]
        for item_data in items_data:
            repository.create(item_data)

        # Execute
        filter_params = MediaItemFilter(type="game", tags="rpg")
        result = repository.get_filtered(filter_params)

        # Assert
        assert len(result) == 1
        assert result[0].title == "RPG Game"
        assert result[0].type == "game"

    def test_update_item(self, repository, db_session):
        """Test updating an existing item"""
        # Setup - create an item first
        item_data = {"title": "Original Title", "type": "game", "platform": "PC", "coverUrl": "https://example.com/1.jpg"}
        created_item = repository.create(item_data)

        # Execute
        update_data = MediaItemUpdate(
            title="Updated Title",
            platform="PlayStation",
            status="done",
            tags=["updated", "tag"]
        )
        result = repository.update(created_item.id, update_data.model_dump(exclude_unset=True, by_alias=True))

        # Assert
        assert result is not None
        assert result.title == "Updated Title"
        assert result.platform == "PlayStation"
        assert result.status == "done"
        assert result.tags == ["updated", "tag"]
        assert result.type == "game"  # Unchanged field
        assert result.id == created_item.id

    def test_update_nonexistent_item(self, repository, db_session):
        """Test updating a non-existent item"""
        # Execute and expect exception
        update_data = MediaItemUpdate(title="Won't work")
        
        from src.media_picker.core.exceptions import ItemNotFoundError
        with pytest.raises(ItemNotFoundError):
            repository.update("nonexistent-id", update_data.model_dump(exclude_unset=True))

    def test_update_partial_fields(self, repository, db_session):
        """Test updating only some fields"""
        # Setup
        item_data = {
            "title": "Original Title",
            "type": "game",
            "platform": "PC",
            "tags": ["original"],
            "coverUrl": "https://example.com/1.jpg"
        }
        created_item = repository.create(item_data)

        # Execute - only update title
        update_data = MediaItemUpdate(title="New Title")
        result = repository.update(created_item.id, update_data.model_dump(exclude_unset=True))

        # Assert
        assert result.title == "New Title"
        assert result.platform == "PC"  # Unchanged
        assert result.tags == ["original"]  # Unchanged

    def test_delete_item(self, repository, db_session):
        """Test deleting an existing item (soft delete)"""
        # Setup
        item_data = {"title": "To Delete", "type": "game", "platform": "PC", "coverUrl": "https://example.com/1.jpg"}
        created_item = repository.create(item_data)

        # Execute
        result = repository.delete(created_item.id)

        # Assert
        assert result is True
        
        # Verify item is soft deleted (not in get_all)
        all_items = repository.get_all()
        assert len(all_items) == 0
        
        # But still exists in database with is_deleted=True
        deleted_item = db_session.query(MediaItem).filter(MediaItem.id == created_item.id).first()
        assert deleted_item is not None
        assert deleted_item.is_deleted is True

    def test_delete_nonexistent_item(self, repository, db_session):
        """Test deleting a non-existent item"""
        # Execute and expect exception
        from src.media_picker.core.exceptions import ItemNotFoundError
        with pytest.raises(ItemNotFoundError):
            repository.delete("nonexistent-id")

    def test_get_by_id(self, repository, db_session):
        """Test getting an item by ID"""
        # Setup
        item_data = {"title": "Find Me", "type": "game", "platform": "PC", "coverUrl": "https://example.com/1.jpg"}
        created_item = repository.create(item_data)

        # Execute
        result = repository.get_by_id(created_item.id)

        # Assert
        assert result is not None
        assert result.id == created_item.id
        assert result.title == "Find Me"

    def test_get_by_id_nonexistent(self, repository, db_session):
        """Test getting a non-existent item by ID"""
        # Execute
        result = repository.get_by_id("nonexistent-id")

        # Assert
        assert result is None

    def test_get_by_id_soft_deleted(self, repository, db_session):
        """Test getting a soft deleted item by ID returns None"""
        # Setup
        item_data = {"title": "Deleted Item", "type": "game", "platform": "PC", "coverUrl": "https://example.com/1.jpg"}
        created_item = repository.create(item_data)
        repository.delete(created_item.id)

        # Execute
        result = repository.get_by_id(created_item.id)

        # Assert
        assert result is None

    def test_empty_tags_handling(self, repository, db_session):
        """Test that empty tags are handled correctly"""
        # Setup
        item_data = {"title": "No Tags Game", "type": "game", "platform": "PC", "coverUrl": "https://example.com/1.jpg", "tags": []}
        created_item = repository.create(item_data)

        # Assert
        assert created_item.tags == []

        # Test filtering with no tags
        filter_params = MediaItemFilter()
        result = repository.get_filtered(filter_params)
        assert len(result) == 1

    def test_get_by_status(self, repository, db_session):
        """Test getting items by status"""
        # Setup
        items_data = [
            {"title": "Active Game", "type": "game", "platform": "PC", "coverUrl": "https://example.com/1.jpg"},
            {"title": "Done Game", "type": "game", "platform": "PC", "coverUrl": "https://example.com/2.jpg"},
        ]
        active_item = repository.create(items_data[0])
        done_item = repository.create(items_data[1])
        done_item.status = "done"
        db_session.commit()

        # Execute
        result = repository.get_by_status("done")

        # Assert
        assert len(result) == 1
        assert result[0].title == "Done Game"
        assert result[0].status == "done"

    def test_get_by_type(self, repository, db_session):
        """Test getting items by type"""
        # Setup
        items_data = [
            {"title": "Test Game", "type": "game", "platform": "PC", "coverUrl": "https://example.com/1.jpg"},
            {"title": "Test Movie", "type": "movie", "platform": "Netflix", "coverUrl": "https://example.com/2.jpg"},
        ]
        for item_data in items_data:
            repository.create(item_data)

        # Execute
        result = repository.get_by_type("movie")

        # Assert
        assert len(result) == 1
        assert result[0].title == "Test Movie"
        assert result[0].type == "movie"

    def test_count_total(self, repository, db_session):
        """Test counting total items"""
        # Setup
        items_data = [
            {"title": "Game 1", "type": "game", "platform": "PC", "coverUrl": "https://example.com/1.jpg"},
            {"title": "Game 2", "type": "game", "platform": "PC", "coverUrl": "https://example.com/2.jpg"},
        ]
        for item_data in items_data:
            repository.create(item_data)

        # Execute
        result = repository.count_total()

        # Assert
        assert result == 2

    def test_count_by_status(self, repository, db_session):
        """Test counting items by status"""
        # Setup
        items_data = [
            {"title": "Active Game", "type": "game", "platform": "PC", "coverUrl": "https://example.com/1.jpg"},
            {"title": "Done Game", "type": "game", "platform": "PC", "coverUrl": "https://example.com/2.jpg"},
        ]
        active_item = repository.create(items_data[0])
        done_item = repository.create(items_data[1])
        done_item.status = "done"
        db_session.commit()

        # Execute
        result = repository.count_by_status("done")

        # Assert
        assert result == 1

    def test_hard_delete(self, repository, db_session):
        """Test permanently deleting an item"""
        # Setup
        item_data = {"title": "To Hard Delete", "type": "game", "platform": "PC", "coverUrl": "https://example.com/1.jpg"}
        created_item = repository.create(item_data)

        # Execute
        result = repository.hard_delete(created_item.id)

        # Assert
        assert result is True
        
        # Verify item is completely removed from database
        deleted_item = db_session.query(MediaItem).filter(MediaItem.id == created_item.id).first()
        assert deleted_item is None

    def test_search_functionality(self, repository, db_session):
        """Test search functionality in filtering"""
        # Setup
        items_data = [
            {"title": "The Witcher 3", "type": "game", "platform": "PC", "coverUrl": "https://example.com/1.jpg"},
            {"title": "Witcher Netflix Series", "type": "movie", "platform": "Netflix", "coverUrl": "https://example.com/2.jpg"},
            {"title": "Cyberpunk 2077", "type": "game", "platform": "PC", "coverUrl": "https://example.com/3.jpg"},
        ]
        for item_data in items_data:
            repository.create(item_data)

        # Execute
        filter_params = MediaItemFilter(search="witcher")
        result = repository.get_filtered(filter_params)

        # Assert
        assert len(result) == 2
        titles = [item.title for item in result]
        assert "The Witcher 3" in titles
        assert "Witcher Netflix Series" in titles

    def test_pagination(self, repository, db_session):
        """Test pagination functionality"""
        # Setup - create 5 items
        for i in range(5):
            item_data = {"title": f"Game {i+1}", "type": "game", "platform": "PC", "coverUrl": f"https://example.com/{i+1}.jpg"}
            repository.create(item_data)

        # Execute - get page 2 with limit 2
        filter_params = MediaItemFilter(limit=2, offset=2)
        result = repository.get_filtered(filter_params)

        # Assert
        assert len(result) == 2
        # Items should be ordered by added_at desc, so we get items 3 and 4 (0-indexed: 2,1)
        assert result[0].title in ["Game 3", "Game 2", "Game 1"]  # Could be any depending on timing
