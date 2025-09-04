import contextlib
import os
import pathlib
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from src.media_picker.api.dependencies import get_db
from src.media_picker.db.database import Base


# Create a temporary database for testing
@pytest.fixture
def db_session():
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp()
    database_url = f"sqlite:///{db_path}"

    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    db = TestingSessionLocal()
    yield db

    # Clean up
    db.close()
    os.close(db_fd)
    with contextlib.suppress(PermissionError, FileNotFoundError):
        # On Windows, file might still be in use, ignore cleanup errors
        pathlib.Path(db_path).unlink()
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"


def test_get_empty_items(client, db_session):
    """Test getting items when database is empty"""
    response = client.get("/api/items")
    assert response.status_code == 200
    assert response.json() == []


def test_add_item(client, db_session):
    """Test adding a new item"""
    item_data = {
        "type": "game",
        "title": "Test Game",
        "platform": "PC",
        "coverUrl": "https://example.com/cover.jpg",
        "tags": ["RPG", "Action"],
    }

    response = client.post("/api/items", json=item_data)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Test Game"
    assert data["type"] == "game"
    assert data["platform"] == "PC"
    assert data["tags"] == ["rpg", "action"]  # tags are lowercased
    assert "id" in data


def test_add_item_invalid_type(client, db_session):
    """Test adding item with invalid type"""
    item_data = {
        "type": "invalid",
        "title": "Test Game",
    }

    response = client.post("/api/items", json=item_data)
    assert response.status_code == 422


def test_add_item_empty_title(client, db_session):
    """Test adding item with empty title"""
    item_data = {
        "type": "game",
        "title": "",
    }

    response = client.post("/api/items", json=item_data)
    assert response.status_code == 422


def test_update_item(client, db_session):
    """Test updating an existing item"""
    # First add an item
    item_data = {"type": "game", "title": "Test Game", "platform": "PC"}

    response = client.post("/api/items", json=item_data)
    item_id = response.json()["id"]

    # Update the item
    update_data = {"title": "Updated Game", "status": "done"}

    response = client.patch(f"/api/items/{item_id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Updated Game"
    assert data["status"] == "done"


def test_delete_item(client, db_session):
    """Test deleting an item"""
    # First add an item
    item_data = {"type": "game", "title": "Test Game"}

    response = client.post("/api/items", json=item_data)
    item_id = response.json()["id"]

    # Delete the item
    response = client.delete(f"/api/items?id={item_id}")
    assert response.status_code == 204  # No Content is correct for DELETE

    # Verify it's deleted
    response = client.get("/api/items")
    assert response.json() == []


def test_spin_empty_pool(client, db_session):
    """Test spinning when no items exist"""
    response = client.get("/api/spin")
    assert response.status_code == 200

    data = response.json()
    assert data["winner"] is None
    assert data["pool"] == []


def test_spin_with_items(client, db_session):
    """Test spinning when items exist"""
    # Add some items
    items = [
        {"type": "game", "title": "Game 1", "platform": "PC"},
        {"type": "game", "title": "Game 2", "platform": "PlayStation"},
        {"type": "movie", "title": "Movie 1", "platform": "Netflix"},
    ]

    for item_data in items:
        client.post("/api/items", json=item_data)

    response = client.get("/api/spin")
    assert response.status_code == 200

    data = response.json()
    assert data["winner"] is not None
    assert len(data["pool"]) == 3
    assert data["winner"] in data["pool"]


def test_filter_by_type(client, db_session):
    """Test filtering items by type"""
    # Add items of different types
    items = [{"type": "game", "title": "Game 1"}, {"type": "movie", "title": "Movie 1"}]

    for item_data in items:
        client.post("/api/items", json=item_data)

    # Filter by games
    response = client.get("/api/items?type=game")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["type"] == "game"
    assert data[0]["title"] == "Game 1"


def test_filter_by_tags(client, db_session):
    """Test filtering items by tags"""
    # Add items with different tags
    items = [
        {"type": "game", "title": "RPG Game", "tags": ["RPG", "Fantasy"]},
        {"type": "game", "title": "Action Game", "tags": ["Action", "Shooter"]},
        {"type": "game", "title": "RPG Action Game", "tags": ["RPG", "Action"]},
    ]

    for item_data in items:
        client.post("/api/items", json=item_data)

    # Filter by RPG tag
    response = client.get("/api/items?tags=RPG")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2  # Should return RPG Game and RPG Action Game

    # Filter by multiple tags
    response = client.get("/api/items?tags=RPG,Action")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1  # Should return only RPG Action Game
    assert data[0]["title"] == "RPG Action Game"
