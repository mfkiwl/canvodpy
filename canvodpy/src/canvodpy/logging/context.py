import contextvars
from pathlib import Path

from canvodpy.logging.logging_config import LOGGER, get_file_logger

# ContextVar to store the active logger
CURRENT_LOGGER = contextvars.ContextVar("CURRENT_LOGGER", default=LOGGER)


def get_logger():
    """Return the logger bound to the current context (defaults to base LOGGER)."""
    return CURRENT_LOGGER.get()


def set_file_context(fname: Path):
    """
    Set the current logger context to a file-specific logger.
    Returns a token for later reset.
    """
    flog = get_file_logger(fname)
    return CURRENT_LOGGER.set(flog)


def reset_context(token):
    """Reset CURRENT_LOGGER to its previous value."""
    CURRENT_LOGGER.reset(token)
