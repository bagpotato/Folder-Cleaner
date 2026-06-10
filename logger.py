"""
Lightweight action log. Wraps the stdlib ``logging`` module and writes to
both the console and a configurable file.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}


def configure_logger(name: str, file_path: str | Path, level: str = "INFO") -> logging.Logger:
    """Configure and return a logger that writes to console and file."""
    logger = logging.getLogger(name)
    logger.setLevel(_LEVELS.get(level.upper(), logging.INFO))
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    logger.addHandler(console)

    try:
        log_path = Path(file_path).expanduser().resolve()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError as exc:
        logger.warning("Could not open log file (%s): %s", file_path, exc)

    return logger
