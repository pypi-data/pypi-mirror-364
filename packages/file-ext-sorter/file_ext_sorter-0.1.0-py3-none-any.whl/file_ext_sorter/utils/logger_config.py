"""
Logging configuration.

Intended to be called at the start of the application to initialize logging behavior.
"""

from __future__ import annotations  # Enables lazy type evaluation (Python <3.10)

import logging
from logging.handlers import RotatingFileHandler
import sys
from pathlib import Path

from colorama import Fore, Style


LOG_FILE_PATH = Path("logs/app.log").resolve()
LOG_FILE_MAX_BYTES = 1_000_000  # ~1MB
LOG_FILE_BACKUP_COUNT = 3


def configure_logging(debug: bool = False, level: int = logging.INFO) -> None:
    """
    Configure root logger to log to file and optionally to console if debug is enabled.

    Rotating log file handler: rotates after 1MB, keeps 3 backups
    """
    # Decide final logging level
    level = logging.DEBUG if debug else level

    # Reset any existing handlers
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    # Common log format
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    # File handler
    LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        LOG_FILE_PATH,
        maxBytes=LOG_FILE_MAX_BYTES,
        backupCount=LOG_FILE_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    # Console handler if debug is True
    if debug:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root.addHandler(console_handler)

    # Silence noisy libraries
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_console_logger() -> logging.Logger:
    """Return a logger configured for colored console output."""

    class ConsoleFormatter(logging.Formatter):
        """Custom formatter for console output with colored and prefixed log messages."""

        def format(self, record: logging.LogRecord) -> str:
            """Format the log record with appropriate color and symbol based on log level."""
            if record.levelno == logging.WARNING:
                msg = f"{Fore.YELLOW}⚠️  Warning: {record.getMessage()}{Style.RESET_ALL}"
            elif record.levelno == logging.ERROR or record.levelno == logging.CRITICAL:
                msg = f"{Fore.RED}❌ Error: {record.getMessage()}{Style.RESET_ALL}"
            else:
                msg = record.getMessage()
            return msg

    logger = logging.getLogger("console")
    logger.setLevel(logging.INFO)  # Always enabled
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(ConsoleFormatter())
        logger.addHandler(handler)

    return logger
