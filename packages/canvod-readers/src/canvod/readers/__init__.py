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

Or use the abstract base for type hints:
```python
from canvod.readers import GNSSDataReader

def process_data(reader: GNSSDataReader):
    # Works with any GNSS reader
    dataset = reader.to_ds()
```
"""

from canvod.readers.base import (
    GNSSDataReader,
    DatasetStructureValidator,
    ReaderFactory,
    # Backwards compatibility aliases
    GNSSReader,
    RinexReader,
)
from canvod.readers.rinex.v3_04 import Rnxv3Obs

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
]
