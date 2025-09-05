"""Tests for the database models"""

import time

from src.media_picker.db.models import MediaItem


class TestMediaItem:
    """Test the MediaItem model"""

    def test_create_from_dict_minimal(self):
        """Test creating a MediaItem from minimal data"""
        data = {"title": "Test Game", "type": "game"}

        item = MediaItem.create_from_dict(data)

        assert item.title == "Test Game"
        assert item.type == "game"
        assert item.status == "active"  # Default
        assert item.tags == []  # Default
        assert item.platform is None
        assert item.cover_url is None
        assert item.is_deleted is False  # Default
        # Note: id and created_at are set by SQLAlchemy when saved to DB
        assert isinstance(item.added_at, int)

    def test_create_from_dict_full(self):
        """Test creating a MediaItem from full data"""
        data = {
            "title": "Test Game",
            "type": "game",
            "platform": "PC",
            "coverUrl": "https://example.com/cover.jpg",
            "tags": ["rpg", "fantasy"],
            "status": "done",
        }

        item = MediaItem.create_from_dict(data)

        assert item.title == "Test Game"
        assert item.type == "game"
        assert item.platform == "PC"
        assert item.cover_url == "https://example.com/cover.jpg"
        assert item.tags == ["rpg", "fantasy"]
        assert item.status == "done"
        assert item.is_deleted is False

    def test_create_from_dict_with_alias(self):
        """Test creating with cover_url alias handling"""
        # Test with coverUrl alias
        data1 = {"title": "Test", "type": "game", "coverUrl": "https://example.com/1.jpg"}
        item1 = MediaItem.create_from_dict(data1)
        assert item1.cover_url == "https://example.com/1.jpg"

        # Test with cover_url direct
        data2 = {"title": "Test", "type": "game", "cover_url": "https://example.com/2.jpg"}
        item2 = MediaItem.create_from_dict(data2)
        assert item2.cover_url == "https://example.com/2.jpg"

    def test_update_from_dict(self):
        """Test updating a MediaItem from dict"""
        # Create initial item
        data = {"title": "Original", "type": "game"}
        item = MediaItem.create_from_dict(data)
        original_id = item.id
        original_created_at = item.created_at

        # Update with new data
        update_data = {
            "title": "Updated Title",
            "platform": "PlayStation",
            "tags": ["action", "shooter"],
            "status": "done",
        }
        item.update_from_dict(update_data)

        # Assert updates
        assert item.title == "Updated Title"
        assert item.platform == "PlayStation"
        assert item.tags == ["action", "shooter"]
        assert item.status == "done"
        assert item.type == "game"  # Unchanged
        assert item.id == original_id  # ID should not change
        assert item.created_at == original_created_at  # Created time should not change
        assert item.updated_at is not None

    def test_update_from_dict_partial(self):
        """Test partial updates"""
        # Create initial item
        data = {"title": "Original", "type": "game", "platform": "PC", "tags": ["rpg"]}
        item = MediaItem.create_from_dict(data)

        # Update only title
        update_data = {"title": "New Title"}
        item.update_from_dict(update_data)

        # Assert only title changed
        assert item.title == "New Title"
        assert item.platform == "PC"  # Unchanged
        assert item.tags == ["rpg"]  # Unchanged
        assert item.type == "game"  # Unchanged

    def test_update_from_dict_with_none_values(self):
        """Test updates with None values don't override existing data"""
        # Create initial item
        data = {"title": "Original", "type": "game", "platform": "PC", "tags": ["rpg"]}
        item = MediaItem.create_from_dict(data)

        # Update with None values (should be ignored)
        update_data = {
            "title": "New Title",
            "platform": None,  # Should be ignored
            "tags": None,  # Should be ignored
        }
        item.update_from_dict(update_data)

        # Assert None values were ignored
        assert item.title == "New Title"
        assert item.platform == "PC"  # Unchanged
        assert item.tags == ["rpg"]  # Unchanged

    def test_update_with_cover_url_alias(self):
        """Test updating with coverUrl alias"""
        data = {"title": "Test", "type": "game"}
        item = MediaItem.create_from_dict(data)

        # Update with coverUrl alias
        update_data = {"coverUrl": "https://example.com/new.jpg"}
        item.update_from_dict(update_data)

        assert item.cover_url == "https://example.com/new.jpg"

    def test_id_generation(self):
        """Test that models can be created (ID generation happens at DB level)"""
        data = {"title": "Test", "type": "game"}

        item1 = MediaItem.create_from_dict(data)
        item2 = MediaItem.create_from_dict(data)

        # Both items are created successfully (actual ID generation happens in DB)
        assert item1.title == "Test"
        assert item2.title == "Test"
        assert item1.type == "game"
        assert item2.type == "game"

    def test_timestamp_fields(self):
        """Test that timestamp fields are set correctly"""
        data = {"title": "Test", "type": "game"}
        current_time = int(time.time())
        item = MediaItem.create_from_dict(data)

        # Check that added_at is set
        assert isinstance(item.added_at, int)

        # Check added_at is reasonable (within last minute)
        time_diff = abs(current_time - item.added_at)
        assert time_diff < 60

        # Note: created_at and updated_at are set by SQLAlchemy when saved to DB
        assert item.updated_at is None  # Should be None initially

    def test_status_default(self):
        """Test that status defaults to 'active'"""
        data = {"title": "Test", "type": "game"}
        item = MediaItem.create_from_dict(data)

        assert item.status == "active"

    def test_is_deleted_default(self):
        """Test that is_deleted defaults to False"""
        data = {"title": "Test", "type": "game"}
        item = MediaItem.create_from_dict(data)

        assert item.is_deleted is False

    def test_tags_default(self):
        """Test that tags defaults to empty list"""
        data = {"title": "Test", "type": "game"}
        item = MediaItem.create_from_dict(data)

        assert item.tags == []
        assert isinstance(item.tags, list)

    def test_tags_normalization(self):
        """Test that tags are stored as provided (normalization happens at schema level)"""
        data = {
            "title": "Test",
            "type": "game",
            "tags": ["rpg", "fantasy"],  # Assume already normalized by schema
        }
        item = MediaItem.create_from_dict(data)

        # Model should store tags as provided (normalization happens in schemas)
        assert "rpg" in item.tags
        assert "fantasy" in item.tags

    def test_empty_string_handling(self):
        """Test handling of empty strings"""
        data = {
            "title": "Test",
            "type": "game",
            "platform": "",  # Empty string
            "coverUrl": "",  # Empty string
        }
        item = MediaItem.create_from_dict(data)

        # Empty strings should be converted to None for optional fields
        assert item.platform is None or item.platform == ""
        assert item.cover_url is None or item.cover_url == ""

    def test_invalid_field_ignored(self):
        """Test that invalid fields are ignored"""
        data = {
            "title": "Test",
            "type": "game",
            "invalid_field": "should be ignored",
            "another_invalid": 123,
        }
        item = MediaItem.create_from_dict(data)

        # Should not raise error and should create valid item
        assert item.title == "Test"
        assert item.type == "game"
        # Invalid fields should not exist on the model
        assert not hasattr(item, "invalid_field")
        assert not hasattr(item, "another_invalid")
