import os
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from app.core.config import settings


def setup_logging() -> None:
    """Configure logging for the application."""

    # Create log directory if it doesn't exist
    log_dir = settings.LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)

    # Get log level
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Create log file path
    log_file = log_dir / settings.LOG_FILENAME

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Create file handler
    file_handler = TimedRotatingFileHandler(
        filename=str(log_file),
        when="midnight",
        interval=1,
        backupCount=7,  # Keep 7 days of logs
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Set log level for external libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
