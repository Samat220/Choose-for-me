#!/usr/bin/env python3
"""Debug script to test API functionality."""

from fastapi.testclient import TestClient

from main import app


def main():
    client = TestClient(app)

    # First, let's see all items without any filter
    print("=== All items ===")
    response = client.get("/api/items")
    print(f"Status: {response.status_code}")
    items = response.json()
    print(f"Items count: {len(items)}")
    for item in items:
        print(f"  - {item}")

    # Test creating an item
    print("\n=== Creating a test game ===")
    test_item = {"type": "game", "title": "Debug Test Game", "platform": "PC"}
    response = client.post("/api/items", json=test_item)
    print(f"Create Status: {response.status_code}")
    if response.status_code == 201:
        created_item = response.json()
        print(f"Created Item ID: {created_item['id']}")
        print(f"Created Item: {created_item}")
    else:
        print(f"Error: {response.json()}")

    # Now check all items again
    print("\n=== All items after creation ===")
    response = client.get("/api/items")
    print(f"Status: {response.status_code}")
    items = response.json()
    print(f"Total items: {len(items)}")
    for item in items:
        print(f"  - {item}")

    # Test filtering by game type
    print("\n=== Filtered by game type ===")
    response = client.get("/api/items?type=game")
    print(f"Status: {response.status_code}")
    game_items = response.json()
    print(f"Game items: {len(game_items)}")
    for item in game_items:
        print(f"  - {item}")


if __name__ == "__main__":
    main()
