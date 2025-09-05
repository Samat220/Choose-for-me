"""Tests for core exceptions"""

from src.media_picker.core.exceptions import ItemNotFoundError, ServiceError, ValidationError


class TestItemNotFoundError:
    """Test ItemNotFoundError"""

    def test_item_not_found_error_with_id(self):
        """Test ItemNotFoundError with item ID"""
        error = ItemNotFoundError("test-id-123")
        assert str(error) == "Item with ID 'test-id-123' not found"
        assert error.item_id == "test-id-123"
        assert error.details["item_id"] == "test-id-123"

    def test_item_not_found_error_inheritance(self):
        """Test that ItemNotFoundError inherits from MediaPickerError"""
        error = ItemNotFoundError("test")
        assert isinstance(error, Exception)
        assert hasattr(error, "message")
        assert hasattr(error, "details")


class TestServiceError:
    """Test ServiceError"""

    def test_service_error_creation(self):
        """Test ServiceError creation"""
        error = ServiceError("Database connection failed")
        assert str(error) == "Database connection failed"
        assert isinstance(error, Exception)

    def test_service_error_empty_message(self):
        """Test ServiceError with empty message"""
        error = ServiceError("")
        assert str(error) == ""


class TestValidationError:
    """Test ValidationError"""

    def test_validation_error_creation(self):
        """Test ValidationError creation"""
        error = ValidationError("Invalid field value")
        assert str(error) == "Invalid field value"
        assert isinstance(error, Exception)

    def test_validation_error_with_field_name(self):
        """Test ValidationError with field context"""
        error = ValidationError("Title cannot be empty")
        assert str(error) == "Title cannot be empty"
