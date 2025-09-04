"""Logging configuration and utilities."""

import logging
import sys


def setup_logging(log_level: str = "INFO", debug: bool = False) -> logging.Logger:
    """Setup application logging with proper configuration."""
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
        force=True,
    )

    # Create application logger
    logger = logging.getLogger("media_picker")
    logger.setLevel(getattr(logging, log_level))

    # Add structured logging for different environments
    if debug:
        # More verbose logging in debug mode
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        )
    else:
        # Production logging format
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Update handler formatter
    for handler in logging.getLogger().handlers:
        handler.setFormatter(formatter)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(f"media_picker.{name}")


# Initialize default logger
logger = setup_logging()
