"""Exception handling and custom exceptions."""

from typing import Any, Dict, Optional


class MediaPickerError(Exception):
    """Base exception for Media Picker application."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(MediaPickerError):
    """Raised when data validation fails."""

    pass


class DatabaseError(MediaPickerError):
    """Raised when database operations fail."""

    pass


class ItemNotFoundError(MediaPickerError):
    """Raised when a requested item is not found."""

    def __init__(self, item_id: str) -> None:
        super().__init__(f"Item with ID '{item_id}' not found", {"item_id": item_id})
        self.item_id = item_id


class ConfigurationError(MediaPickerError):
    """Raised when configuration is invalid."""

    pass


class ServiceError(MediaPickerError):
    """Raised when a service operation fails."""

    pass
