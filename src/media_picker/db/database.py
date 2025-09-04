"""Database configuration and connection management."""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger("database")

# Create database engine with optimized settings
engine_kwargs = {
    "echo": settings.debug,  # Log SQL queries in debug mode
    "future": True,  # Use SQLAlchemy 2.0 style
}

# SQLite-specific optimizations
if settings.database_url.startswith("sqlite"):
    engine_kwargs.update(
        {
            "connect_args": {
                "check_same_thread": False,
                "timeout": 30,
            },
            "poolclass": StaticPool,
            "pool_pre_ping": True,
        }
    )

engine = create_engine(settings.database_url, **engine_kwargs)


# Configure SQLite for better performance and reliability
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for better performance."""
    if "sqlite" in str(dbapi_connection):
        cursor = dbapi_connection.cursor()
        # Enable WAL mode for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys=ON")
        # Optimize synchronization
        cursor.execute("PRAGMA synchronous=NORMAL")
        # Set cache size (negative value = KB)
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
        # Optimize temp store
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()


# Create session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,  # Use SQLAlchemy 2.0 style
)

# Create declarative base
Base = declarative_base()


def get_db() -> Generator:
    """Get database session with proper cleanup."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Context manager for database sessions."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tables() -> None:
    """Create all database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def drop_tables() -> None:
    """Drop all database tables (use with caution)."""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise
