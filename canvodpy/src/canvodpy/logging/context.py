"""Context-local logging helpers."""

import contextvars
from pathlib import Path
from typing import Any

from canvodpy.logging.logging_config import LOGGER, get_file_logger

# ContextVar to store the active logger
CURRENT_LOGGER = contextvars.ContextVar("CURRENT_LOGGER", default=LOGGER)


def get_logger() -> Any:
    """Return the logger bound to the current context."""
    return CURRENT_LOGGER.get()


def set_file_context(fname: Path) -> contextvars.Token:
    """
    Set the current logger context to a file-specific logger.

    Parameters
    ----------
    fname : Path
        File path to bind into the logging context.

    Returns
    -------
    contextvars.Token
        Token used to restore the previous context.
    """
    flog = get_file_logger(fname)
    return CURRENT_LOGGER.set(flog)


def reset_context(token: contextvars.Token) -> None:
    """Reset CURRENT_LOGGER to its previous value."""
    CURRENT_LOGGER.reset(token)
