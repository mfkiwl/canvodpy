"""Structlog-based logging for canvod-grids package."""

import structlog


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a structlog logger instance.

    Parameters
    ----------
    name : str, optional
        Logger name, typically __name__ of the module.
        If None, uses "canvod.grids".

    Returns
    -------
    structlog.stdlib.BoundLogger
        Configured structlog logger.

    Examples
    --------
    >>> log = get_logger(__name__)
    >>> log.info("cell_assignment_started", grid_name="equal_area")
    """
    if name is None:
        name = "canvod.grids"
    return structlog.get_logger(name)
