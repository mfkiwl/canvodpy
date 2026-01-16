"""
Logging utilities for canvod-aux package.

Canonical source: This file is the authoritative version.
See /DUPLICATION_TRACKER.md for copy locations.

Provides lightweight logging with optional file-based context.
"""
import contextvars
import logging
from pathlib import Path
from typing import Optional

# ContextVar to store the active logger
CURRENT_LOGGER = contextvars.ContextVar("CURRENT_LOGGER", default=None)

# Default logger configuration
_BASE_LOGGER: Optional[logging.Logger] = None


def _configure_base_logger() -> logging.Logger:
    """Configure and return the base logger for canvod-aux."""
    logger = logging.getLogger("canvod.aux")
    
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get the logger for the current context.
    
    Parameters
    ----------
    name : str, optional
        Logger name. If None, uses context-bound logger or base logger.
        
    Returns
    -------
    logging.Logger
        Logger instance
    """
    global _BASE_LOGGER
    
    # Return context logger if set
    context_logger = CURRENT_LOGGER.get()
    if context_logger is not None:
        return context_logger
    
    # Return named logger if requested
    if name is not None:
        return logging.getLogger(f"canvod.aux.{name}")
    
    # Return or create base logger
    if _BASE_LOGGER is None:
        _BASE_LOGGER = _configure_base_logger()
    
    return _BASE_LOGGER


def set_file_context(filename: str | Path) -> contextvars.Token:
    """
    Set logging context to include file information.
    
    Parameters
    ----------
    filename : str or Path
        File being processed
        
    Returns
    -------
    contextvars.Token
        Token for later reset
        
    Examples
    --------
    >>> token = set_file_context("data.sp3")
    >>> logger = get_logger()
    >>> logger.info("Processing file")
    >>> reset_context(token)
    """
    if isinstance(filename, Path):
        filename = filename.name
    
    # Create file-specific logger
    file_logger = logging.getLogger(f"canvod.aux.{filename}")
    
    # Inherit configuration from base logger
    base_logger = get_logger()
    if not file_logger.handlers and base_logger.handlers:
        for handler in base_logger.handlers:
            file_logger.addHandler(handler)
        file_logger.setLevel(base_logger.level)
    
    return CURRENT_LOGGER.set(file_logger)


def reset_context(token: contextvars.Token) -> None:
    """
    Reset logging context to previous state.
    
    Parameters
    ----------
    token : contextvars.Token
        Token returned by set_file_context()
    """
    CURRENT_LOGGER.reset(token)
