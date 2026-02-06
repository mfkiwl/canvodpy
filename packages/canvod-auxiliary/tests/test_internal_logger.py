"""
Tests for internal logger utilities.

Tests structlog-based logger configuration.
"""

from canvod.auxiliary._internal import get_logger


def test_get_logger_returns_structlog_logger():
    """Test that get_logger returns a structlog logger instance."""
    logger = get_logger()
    # Should be a structlog logger (BoundLoggerLazyProxy or similar)
    assert hasattr(logger, "bind")
    assert hasattr(logger, "info")
    assert hasattr(logger, "debug")


def test_get_logger_named():
    """Test that get_logger with name returns named logger."""
    logger = get_logger("test_module")
    # Should be a structlog logger with logging methods
    assert hasattr(logger, "bind")
    assert hasattr(logger, "info")


def test_get_logger_default_name():
    """Test that default logger works."""
    logger = get_logger()
    # Should be a valid logger instance
    assert hasattr(logger, "bind")
    assert hasattr(logger, "info")


def test_logger_binding():
    """Test that logger can bind context."""
    logger = get_logger()

    # Bind context
    bound_logger = logger.bind(file="test_file.sp3", component="auxiliary")

    # Should return a logger with bind method
    assert hasattr(bound_logger, "bind")
    assert hasattr(bound_logger, "info")
    # Bound logger is a different instance
    assert bound_logger is not logger


def test_logger_supports_structured_logging():
    """Test that logger supports structured logging."""
    logger = get_logger()

    # Should be able to log with structured data
    # This shouldn't raise an exception
    logger.info("test_event", key="value", count=123)
    logger.debug("debug_event", data={"nested": "value"})
    logger.warning("warning_event", status="failed")


def test_nested_bindings():
    """Test nested context binding."""
    logger = get_logger()

    # First binding
    logger1 = logger.bind(file="file1.sp3")
    assert hasattr(logger1, "bind")

    # Second binding (nested)
    logger2 = logger1.bind(operation="interpolation")
    assert hasattr(logger2, "bind")

    # Each binding creates a new instance
    assert logger1 is not logger
    assert logger2 is not logger1
