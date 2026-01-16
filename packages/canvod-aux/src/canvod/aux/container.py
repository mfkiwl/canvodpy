"""Container classes for GNSS data."""

from pathlib import Path

import pandas as pd
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
import xarray as xr


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class GnssData:
    """Container for GNSS data that may include both xarray Dataset and pandas DataFrame."""

    dataset: xr.Dataset
    dataframe: pd.DataFrame | None = None


@dataclass
class FileMetadata:
    """Metadata required for GNSS auxiliary files."""

    date: str  # Format: YYYYDOY
    agency: str  # e.g., 'COD', 'IGS'
    product_type: str  # 'final', 'rapid', 'ultrarapid'
    local_dir: Path
    ftp_server: str
