"""Metadata table helpers for Icechunk-backed stores."""

from datetime import datetime
import json
from typing import Any

import numpy as np
import polars as pl
import zarr
from zarr.dtype import VariableLengthUTF8

from canvodpy.logging.context import get_logger


class MetadataManager:
    """Manage metadata table CRUD, backups, and deduplication for groups.

    Parameters
    ----------
    logger : Any, optional
        Logger-like object to use. Defaults to the configured context logger.
    """

    def __init__(self, logger: Any | None = None) -> None:
        self._logger = logger or get_logger()

    # TODO: Future refactor of MyIcechunkStore.
