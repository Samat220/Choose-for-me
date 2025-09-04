#!/usr/bin/env python3
"""Fix database schema migration script."""

import json
import logging
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_database():
    """Migrate database from old schema to new schema."""
    conn = sqlite3.connect("media_picker.db")
    cursor = conn.cursor()

    try:
        # Check if we need to migrate
        cursor.execute("PRAGMA table_info(media_items)")
        columns = [row[1] for row in cursor.fetchall()]

        logger.info(f"Existing columns: {columns}")

        if "tags_json" in columns:
            logger.info("Database already migrated, no action needed")
            return

        if "tags" not in columns:
            logger.error("Neither 'tags' nor 'tags_json' column found")
            return

        # Add new column
        logger.info("Adding tags_json column...")
        cursor.execute("ALTER TABLE media_items ADD COLUMN tags_json TEXT")

        # Migrate data from tags to tags_json
        logger.info("Migrating tags data...")
        cursor.execute("SELECT id, tags FROM media_items WHERE tags IS NOT NULL")
        rows = cursor.fetchall()

        for row_id, tags_text in rows:
            try:
                # Parse existing JSON or create empty list
                if tags_text:
                    try:
                        tags_list = json.loads(tags_text)
                        if not isinstance(tags_list, list):
                            tags_list = []
                    except json.JSONDecodeError:
                        # If it's not JSON, treat as comma-separated
                        tags_list = [tag.strip() for tag in tags_text.split(",") if tag.strip()]
                else:
                    tags_list = []

                # Update with JSON data
                cursor.execute(
                    "UPDATE media_items SET tags_json = ? WHERE id = ?",
                    (json.dumps(tags_list), row_id),
                )
                logger.info(f"Migrated tags for item {row_id}: {tags_list}")

            except Exception as e:
                logger.error(f"Error migrating tags for item {row_id}: {e}")

        # Add missing columns if needed
        if "is_deleted" not in columns:
            logger.info("Adding is_deleted column...")
            cursor.execute("ALTER TABLE media_items ADD COLUMN is_deleted INTEGER DEFAULT 0")

        conn.commit()
        logger.info("Database migration completed successfully")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate_database()
