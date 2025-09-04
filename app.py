import json
import logging
import random
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

# Import our custom modules
from database import MediaItem, create_tables, get_db
from models import MediaItemCreate, MediaItemResponse, MediaItemUpdate, SpinResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Create database tables on startup


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    create_tables()
    logger.info("Database tables created successfully")
    yield
    # Shutdown


# Create FastAPI app
app = FastAPI(
    title="Media Picker API",
    description="A modern web app for organizing games and movies with a spinning wheel picker",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS - More restrictive in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9000", "http://127.0.0.1:9000"],  # Restrict to localhost
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)


# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422, content={"error": "Validation failed", "details": exc.errors()}
    )


@app.exception_handler(Exception)
async def general_exception_handler(_request: Request, exc: Exception):
    logger.exception("Unexpected error occurred: %s", exc)
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


def uid():
    """Generate a unique identifier"""
    return uuid.uuid4().hex


# API Routes
@app.get("/api/items", response_model=list[MediaItemResponse])
async def get_items(
    type: str | None = Query(None, pattern="^(game|movie)$"),
    tags: str | None = Query(None),
    include_archived: bool = Query(False),
    status: str | None = Query(None, pattern="^(active|done|archived)$"),
    db: Session = Depends(get_db),
):
    """Get filtered list of media items"""
    try:
        query = db.query(MediaItem)

        # Apply filters
        if type:
            query = query.filter(MediaItem.type == type)

        if status:
            query = query.filter(MediaItem.status == status)
        elif not include_archived:
            query = query.filter(MediaItem.status != "archived")

        items = query.order_by(MediaItem.added_at.desc()).all()

        # Filter by tags if provided
        if tags:
            tag_set = {t.strip().lower() for t in tags.split(",") if t.strip()}
            if tag_set:
                items = [
                    item
                    for item in items
                    if tag_set.issubset({t.lower() for t in json.loads(item.tags or "[]")})
                ]

        return [MediaItemResponse.from_orm(item) for item in items]

    except Exception as e:
        logger.exception("Error fetching items")
        raise HTTPException(status_code=500, detail="Failed to fetch items") from e


@app.post("/api/items", response_model=MediaItemResponse)
async def add_item(item: MediaItemCreate, db: Session = Depends(get_db)):
    """Add a new media item"""
    try:
        new_item = MediaItem(
            id=uid(),
            type=item.type,
            title=item.title,
            platform=item.platform,
            cover_url=item.coverUrl,
            tags=json.dumps(item.tags),
            status="active",
            added_at=int(time.time()),
        )

        db.add(new_item)
        db.commit()
        db.refresh(new_item)

        logger.info(f"Added new item: {item.title}")
        return MediaItemResponse.from_orm(new_item)

    except Exception as e:
        logger.exception("Error adding item")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to add item") from e


@app.delete("/api/items")
async def delete_item(id: str = Query(...), db: Session = Depends(get_db)):
    """Delete a media item"""
    try:
        item = db.query(MediaItem).filter(MediaItem.id == id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        db.delete(item)
        db.commit()

        logger.info(f"Deleted item: {item.title}")
        return {"status": "deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error deleting item")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete item") from e


@app.patch("/api/items/{item_id}", response_model=MediaItemResponse)
async def update_item(item_id: str, update_data: MediaItemUpdate, db: Session = Depends(get_db)):
    """Update a media item"""
    try:
        item = db.query(MediaItem).filter(MediaItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if field == "coverUrl":
                item.cover_url = value
            elif field == "tags":
                item.tags = json.dumps(value)
            else:
                setattr(item, field, value)

        db.commit()
        db.refresh(item)

        logger.info(f"Updated item: {item.title}")
        return MediaItemResponse.from_orm(item)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error updating item")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update item") from e


@app.get("/api/spin", response_model=SpinResponse)
async def spin(
    type: str | None = Query(None, pattern="^(game|movie)$"),
    tags: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """Spin the wheel to get a random item"""
    try:
        query = db.query(MediaItem).filter(MediaItem.status == "active")

        if type:
            query = query.filter(MediaItem.type == type)

        items = query.all()

        # Filter by tags if provided
        if tags:
            tag_set = {t.strip().lower() for t in tags.split(",") if t.strip()}
            if tag_set:
                items = [
                    item
                    for item in items
                    if tag_set.issubset({t.lower() for t in json.loads(item.tags or "[]")})
                ]

        if not items:
            return SpinResponse(winner=None, pool=[])

        winner = random.choice(items)
        pool = [MediaItemResponse.from_orm(item) for item in items]

        logger.info(f"Spin result: {winner.title}")
        return SpinResponse(winner=MediaItemResponse.from_orm(winner), pool=pool)

    except Exception as e:
        logger.exception("Error during spin")
        raise HTTPException(status_code=500, detail="Failed to spin") from e


# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": int(time.time())}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=9000, reload=True)
