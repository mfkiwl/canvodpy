"""Metadata table helpers for Icechunk-backed stores."""

from typing import Any

from canvodpy.logging.context import get_logger


class MetadataManager:
    """Manage metadata table CRUD, backups, and deduplication for groups.

    Parameters
    ----------
    logger : Any, optional
        Logger-like object to use. Defaults to the configured context logger.
    """

    def __init__(self, logger: Any | None = None) -> None:
        """Initialize the metadata manager.

        Parameters
        ----------
        logger : Any | None, optional
            Logger-like object to use.
        """
        self._logger = logger or get_logger()

    # TODO: Future refactor of MyIcechunkStore.
