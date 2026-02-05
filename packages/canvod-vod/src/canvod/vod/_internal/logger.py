"""Structlog-based logging for canvod-vod package."""

import structlog


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a structlog logger instance.

    Parameters
    ----------
    name : str, optional
        Logger name, typically __name__ of the module.
        If None, uses "canvod.vod".

    Returns
    -------
    structlog.stdlib.BoundLogger
        Configured structlog logger.

    Examples
    --------
    >>> log = get_logger(__name__)
    >>> log.info("vod_calculation_started", canopy_epochs=2880)
    """
    if name is None:
        name = "canvod.vod"
    return structlog.get_logger(name)
