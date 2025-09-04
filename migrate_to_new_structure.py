"""Migration script for transitioning to the new modular architecture."""

import json
import sys
from pathlib import Path

from src.media_picker.core.config import settings
from src.media_picker.core.logging import get_logger, setup_logging
from src.media_picker.db.database import create_tables, get_db_context
from src.media_picker.services.media_service import MediaItemService

# Setup logging
setup_logging(settings.log_level, settings.debug)
logger = get_logger("migration")


def migrate_from_json(json_file_path: str) -> None:
    """Migrate data from old JSON format to new database structure."""
    json_path = Path(json_file_path)

    if not json_path.exists():
        logger.error(f"JSON file not found: {json_file_path}")
        return

    try:
        with json_path.open() as f:
            old_items = json.load(f)

        logger.info(f"Found {len(old_items)} items in JSON file")

        # Create database tables
        create_tables()

        # Migrate each item
        migrated_count = 0
        with get_db_context() as db:
            service = MediaItemService(db)

            for item_data in old_items:
                try:
                    # Convert old format to new schema
                    from src.media_picker.schemas.media import MediaItemCreate

                    # Map old field names to new ones
                    converted_data = {
                        "type": item_data.get("type"),
                        "title": item_data.get("title"),
                        "platform": item_data.get("platform"),
                        "cover_url": item_data.get("coverUrl"),
                        "tags": item_data.get("tags", []),
                    }

                    # Create and validate the item
                    create_item = MediaItemCreate(**converted_data)
                    service.create_item(create_item)
                    migrated_count += 1

                except Exception as e:
                    logger.warning(
                        f"Failed to migrate item {item_data.get('title', 'Unknown')}: {e}"
                    )
                    continue

        logger.info(f"Successfully migrated {migrated_count} items to new database structure")

    except Exception as e:
        logger.error(f"Error during migration: {e}")
        raise


def export_to_json(output_file_path: str) -> None:
    """Export current database to JSON format."""
    output_path = Path(output_file_path)

    try:
        with get_db_context() as db:
            service = MediaItemService(db)
            items = service.get_all_items()

        # Convert to exportable format
        export_data = []
        for item in items:
            export_data.append(item.model_dump(by_alias=True))

        with output_path.open("w") as f:
            json.dump(export_data, f, indent=2, default=str)

        logger.info(f"Successfully exported {len(items)} items to {output_file_path}")

    except Exception as e:
        logger.error(f"Error during export: {e}")
        raise


def validate_database() -> None:
    """Validate the database structure and data integrity."""
    try:
        with get_db_context() as db:
            service = MediaItemService(db)

            # Get statistics
            stats = service.get_statistics()
            logger.info("Database validation results:")
            logger.info(f"  Total items: {stats['total']}")
            logger.info(f"  Active: {stats['active']}")
            logger.info(f"  Done: {stats['done']}")
            logger.info(f"  Archived: {stats['archived']}")
            logger.info(f"  Games: {stats['games']}")
            logger.info(f"  Movies: {stats['movies']}")

            # Validate a few items
            if stats["total"] > 0:
                items = service.get_all_items()
                if items:
                    sample_item = items[0]
                    logger.info(f"Sample item: {sample_item.title} ({sample_item.type})")

        logger.info("Database validation completed successfully")

    except Exception as e:
        logger.error(f"Error during validation: {e}")
        raise


def main():
    """Main migration script entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python migrate_to_new_structure.py migrate <json_file>")
        print("  python migrate_to_new_structure.py export <output_file>")
        print("  python migrate_to_new_structure.py validate")
        print("  python migrate_to_new_structure.py init")
        sys.exit(1)

    command = sys.argv[1]

    if command == "init":
        logger.info("Initializing database structure...")
        create_tables()
        logger.info("Database initialization completed")

    elif command == "migrate":
        if len(sys.argv) < 3:
            logger.error("Please provide JSON file path")
            sys.exit(1)
        json_file = sys.argv[2]
        logger.info(f"Starting migration from {json_file}...")
        migrate_from_json(json_file)

    elif command == "export":
        if len(sys.argv) < 3:
            logger.error("Please provide output file path")
            sys.exit(1)
        output_file = sys.argv[2]
        logger.info(f"Starting export to {output_file}...")
        export_to_json(output_file)

    elif command == "validate":
        logger.info("Starting database validation...")
        validate_database()

    else:
        logger.error(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
