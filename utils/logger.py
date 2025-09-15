# utils/logger.py
import logging
import sys

def get_logger(name: str):
    """
    Returns a logger instance with a standard format.
    Logs both to console and can be extended for file logging.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:  # Prevent duplicate handlers
        logger.setLevel(logging.INFO)

        # Console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)

        # Log format
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger
