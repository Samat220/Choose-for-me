"""
Migration utility to move from the old in-memory storage to SQLite database.
This script helps migrate data if you have any existing data in the old format.
"""

import json
import time
import uuid

from database import MediaItem, SessionLocal, create_tables


def migrate_from_json_file(json_file_path: str):
    """
    Migrate data from a JSON file to the database.
    Expected JSON format: list of items with keys matching the old format.
    """
    create_tables()

    try:
        with open(json_file_path) as f:
            old_items = json.load(f)
    except FileNotFoundError:
        print(f"File {json_file_path} not found. Starting with empty database.")
        return
    except json.JSONDecodeError:
        print(f"Invalid JSON in {json_file_path}. Starting with empty database.")
        return

    db = SessionLocal()

    try:
        for item in old_items:
            # Convert old format to new format
            new_item = MediaItem(
                id=item.get("id", uuid.uuid4().hex),
                type=item.get("type", "game"),
                title=item.get("title", "Unknown"),
                platform=item.get("platform"),
                cover_url=item.get("coverUrl"),
                tags=json.dumps(item.get("tags", [])),
                status=item.get("status", "active"),
                added_at=item.get("addedAt", int(time.time())),
            )

            # Check if item already exists
            existing = db.query(MediaItem).filter(MediaItem.id == new_item.id).first()
            if not existing:
                db.add(new_item)

        db.commit()
        print(f"Successfully migrated {len(old_items)} items to database.")

    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
    finally:
        db.close()


def export_to_json(output_file_path: str):
    """
    Export current database to JSON file for backup.
    """
    db = SessionLocal()

    try:
        items = db.query(MediaItem).all()
        export_data = [item.to_dict() for item in items]

        with open(output_file_path, "w") as f:
            json.dump(export_data, f, indent=2)

        print(f"Successfully exported {len(items)} items to {output_file_path}")

    except Exception as e:
        print(f"Error during export: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python migration.py migrate <json_file>   # Migrate from JSON file")
        print("  python migration.py export <output_file>  # Export to JSON file")
        print("  python migration.py init                  # Initialize empty database")
        sys.exit(1)

    command = sys.argv[1]

    if command == "migrate" and len(sys.argv) == 3:
        migrate_from_json_file(sys.argv[2])
    elif command == "export" and len(sys.argv) == 3:
        export_to_json(sys.argv[2])
    elif command == "init":
        create_tables()
        print("Database initialized successfully.")
    else:
        print("Invalid command or missing arguments.")
        sys.exit(1)
