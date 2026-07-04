"""
utils/logger.py

A single, reusable logging setup for the whole ML pipeline. Every file
should get its logger the same way instead of configuring logging
separately in each module:

    from utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Something happened")
"""

import logging


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a logger with consistent formatting across the project."""
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if get_logger() is called more than once
    # for the same module (e.g. during testing or re-imports).
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.propagate = False

    return logger