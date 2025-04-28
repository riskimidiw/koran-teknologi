"""Logger implementation"""

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
        A configured Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level if log_level is not None else logging.INFO)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True, parents=True)

    # Create handlers
    c_handler = logging.StreamHandler(sys.stdout)
    f_handler = logging.FileHandler(log_dir / "app.log")

    # Set levels
    c_handler.setLevel(logger.level)
    f_handler.setLevel(logger.level)

    # Create formatters and add them to handlers
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    c_format = logging.Formatter(log_format)
    f_format = logging.Formatter(log_format)
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger
