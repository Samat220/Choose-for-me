"""Exception handlers for the API."""

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from ..core.exceptions import (
    DatabaseError,
    ItemNotFoundError,
    MediaPickerError,
    ServiceError,
)
from ..core.logging import get_logger

logger = get_logger("api.handlers")


async def media_picker_exception_handler(request: Request, exc: MediaPickerError) -> JSONResponse:
    """Handle custom Media Picker exceptions."""
    logger.warning(f"Media Picker error: {exc.message}", extra={"details": exc.details})

    # Map exception types to HTTP status codes
    status_code_map = {
        ItemNotFoundError: 404,
        ValidationError: 422,
        DatabaseError: 500,
        ServiceError: 500,
    }

    status_code = status_code_map.get(type(exc), 500)

    return JSONResponse(
        status_code=status_code,
        content={
            "error": exc.message,
            "type": exc.__class__.__name__,
            "details": exc.details,
        },
    )


async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    logger.warning(f"Validation error: {exc}")

    # Format Pydantic errors for API response
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": " -> ".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation failed",
            "type": "ValidationError",
            "details": {"errors": errors},
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    logger.exception("Unexpected error occurred")

    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "type": "InternalServerError", "details": {}},
    )
