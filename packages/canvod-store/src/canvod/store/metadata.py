from datetime import datetime
import json
from typing import Optional

import numpy as np
import polars as pl
import zarr
from zarr.dtype import VariableLengthUTF8

from canvodpy.logging.context import get_logger


class MetadataManager:
    """
    Manages metadata table operations for Icechunk groups.

    Handles all metadata table CRUD operations, backups, restoration,
    and deduplication logic in a separate, focused class.
    """

    def __init__(self, logger=None):
        self._logger = logger or get_logger()

    #TODO future refactor of MyIcechunkStore
