"""
Tests for internal logger utilities.

Tests logging context management and logger configuration.
"""

import logging
from pathlib import Path

from canvod.auxiliary._internal import get_logger, reset_context, set_file_context


def test_get_logger_returns_logger():
    """Test that get_logger returns a Logger instance."""
    logger = get_logger()
    assert isinstance(logger, logging.Logger)


def test_get_logger_named():
    """Test that get_logger with name returns named logger."""
    logger = get_logger("test_module")
    assert isinstance(logger, logging.Logger)
    assert "test_module" in logger.name


def test_get_logger_default_is_cached():
    """Test that default logger is cached."""
    logger1 = get_logger()
    logger2 = get_logger()
    assert logger1 is logger2


def test_set_file_context():
    """Test setting file context for logging."""
    token = set_file_context("test_file.sp3")

    # Get logger should return file-specific logger
    logger = get_logger()
    assert "test_file.sp3" in logger.name

    # Cleanup
    reset_context(token)


def test_reset_context():
    """Test resetting logging context."""
    # Get original logger
    original_logger = get_logger()

    # Set file context
    token = set_file_context("test_file.sp3")
    file_logger = get_logger()

    # Verify it changed
    assert file_logger is not original_logger

    # Reset context
    reset_context(token)

    # Should return to original behavior
    reset_logger = get_logger()
    assert reset_logger is original_logger


def test_set_file_context_with_path():
    """Test setting file context with Path object."""
    path = Path("/data/test_file.sp3")
    token = set_file_context(path)

    logger = get_logger()
    assert "test_file.sp3" in logger.name

    reset_context(token)


def test_logger_has_handlers():
    """Test that logger has configured handlers."""
    logger = get_logger()

    # Should have at least one handler (console)
    assert len(logger.handlers) > 0


def test_nested_file_contexts():
    """Test nested file context management."""
    # First context
    token1 = set_file_context("file1.sp3")
    logger1 = get_logger()
    assert "file1.sp3" in logger1.name

    # Second context (nested)
    token2 = set_file_context("file2.clk")
    logger2 = get_logger()
    assert "file2.clk" in logger2.name

    # Reset second context
    reset_context(token2)
    logger_after_2 = get_logger()
    assert "file1.sp3" in logger_after_2.name

    # Reset first context
    reset_context(token1)
