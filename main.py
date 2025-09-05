"""Main application entry point with modern architecture."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError as PydanticValidationError

from src.media_picker.api.exception_handlers import (
    custom_validation_exception_handler,
    general_exception_handler,
    media_picker_exception_handler,
    validation_exception_handler,
)
from src.media_picker.api.media import router as media_router
from src.media_picker.core.config import settings
from src.media_picker.core.exceptions import MediaPickerError, ValidationError as CustomValidationError
from src.media_picker.core.logging import get_logger
from src.media_picker.db.database import create_tables

# Configure logging
settings.configure_logging()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting up Media Picker application")
    try:
        # Ensure data directory exists before creating database
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        create_tables()
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Media Picker application")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        description="A modern web app for organizing games and movies with a spinning wheel picker",
        version=settings.version,
        lifespan=lifespan,
        debug=settings.debug,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["*"],
    )

    # Register exception handlers
    app.add_exception_handler(MediaPickerError, media_picker_exception_handler)
    app.add_exception_handler(CustomValidationError, custom_validation_exception_handler)
    app.add_exception_handler(PydanticValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # Include API routers
    app.include_router(media_router)

    # Mount static files
    if settings.static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")

    # Setup templates
    templates = None
    if settings.templates_dir.exists():
        templates = Jinja2Templates(directory=str(settings.templates_dir))

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        """Serve the main application page."""
        if templates:
            return templates.TemplateResponse("index.html", {"request": request})

        # Simple fallback
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Media Picker</title>
        </head>
        <body>
            <h1>Media Picker API</h1>
            <p>Welcome to the Media Picker application!</p>
            <p><a href="/docs">API Documentation</a></p>
        </body>
        </html>
        """)

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": settings.version,
            "debug": settings.debug,
        }

    logger.info(f"FastAPI application created with debug={settings.debug}")
    return app


# Create the application instance
app = create_app()


def main():
    """Entry point for running the application."""
    import uvicorn

    logger.info(f"Starting server on {settings.host}:{settings.port}")
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
