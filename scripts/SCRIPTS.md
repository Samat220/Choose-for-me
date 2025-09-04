# Scripts Directory

This directory contains utility scripts for database migration, maintenance, and development tasks.

## Available Scripts

### migration.py
Legacy migration script for moving from old JSON format to SQLite database.

**Usage:**
```bash
python scripts/migration.py migrate <json_file>   # Migrate from JSON file
python scripts/migration.py export <output_file>  # Export to JSON file
python scripts/migration.py init                  # Initialize empty database
```

### migrate_to_new_structure.py
Modern migration script for transitioning to the new modular architecture.

**Usage:**
```bash
python scripts/migrate_to_new_structure.py migrate <json_file>
python scripts/migrate_to_new_structure.py export <output_file>
python scripts/migrate_to_new_structure.py validate
python scripts/migrate_to_new_structure.py init
```

### fix_database_schema.py
Database schema migration script for updating database structure.

**Usage:**
```bash
python scripts/fix_database_schema.py
```

### run_checks.py
Code quality check script that runs ruff linting and formatting.

**Usage:**
```bash
python scripts/run_checks.py
```

## Notes

- Always backup your database before running migration scripts
- The new modular architecture uses `data/media_picker.db` as the default database location
- Legacy files are stored in the `legacy/` directory and should not be used in production
