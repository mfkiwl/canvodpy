"""GNSS data format readers.

This package provides readers for various GNSS data formats, all implementing
a common interface for seamless integration with processing pipelines.

Supported formats:
- RINEX v3.04 (GNSS observations)
- More formats coming soon...

Quick Start
-----------
```python
from canvod.readers import Rnxv3Obs

# Read RINEX v3 file
reader = Rnxv3Obs(fpath="station.24o")
dataset = reader.to_ds()
```

Or use the factory for automatic format detection:
```python
from canvod.readers import ReaderFactory

# Auto-detects format
reader = ReaderFactory.create("station.24o")
dataset = reader.to_ds()
```

Directory Matching:
```python
from canvod.readers import DataDirMatcher

# Find dates with RINEX files in both receivers
matcher = DataDirMatcher(root=Path("/data/01_Rosalia"))
for matched_dirs in matcher:
    print(matched_dirs.yyyydoy)
    # Load RINEX files from matched_dirs.canopy_data_dir
```
"""

from canvod.readers.base import (
    DatasetStructureValidator,
    GNSSDataReader,
    # Backwards compatibility aliases
    GNSSReader,
    ReaderFactory,
    RinexReader,
)
from canvod.readers.matching import (
    DataDirMatcher,
    MatchedDirs,
    PairDataDirMatcher,
    PairMatchedDirs,
)
from canvod.readers.rinex.v3_04 import Rnxv3Obs
from canvod.readers.utils import YYYYDOY

__version__ = "0.1.0"

__all__ = [
    # Abstract interfaces
    "GNSSDataReader",
    "DatasetStructureValidator",
    "ReaderFactory",
    # Backwards compatibility aliases
    "GNSSReader",
    "RinexReader",
    # Concrete implementations
    "Rnxv3Obs",
    # Directory matching
    "DataDirMatcher",
    "PairDataDirMatcher",
    "MatchedDirs",
    "PairMatchedDirs",
    # Utilities
    "YYYYDOY",
]
