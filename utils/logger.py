"""Logging configuration for the application."""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(name: str, log_level: Optional[int] = None) -> logging.Logger:
    """Configure and return a logger instance.

    Args:
        name: The name of the logger, typically the module name
        log_level: Optional custom log level. Defaults to INFO if not provided

    Returns:
        A configured Logger instance with both file and console handlers
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level if log_level is not None else logging.INFO)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    try:
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True, parents=True)

        # File handler with detailed format
        file_handler = logging.FileHandler(log_dir / "app.log")
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

        # Console handler with simpler format
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)

    except Exception as e:
        # Fallback to console-only logging if file setup fails
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        logger.error(f"Failed to set up file logging: {str(e)}")

    return logger
