"""GNSS data format readers.

This package provides readers for various GNSS data formats, all implementing
a common interface for seamless integration with processing pipelines.

Supported formats:
- RINEX v3.04 (GNSS observations)
- More formats coming soon...

Quick Start
-----------
```python
from canvod.readers import Rnxv3Reader

# Read RINEX v3 file
reader = Rnxv3Reader()
dataset = reader.read("station.24o")
```

Or use the abstract base for type hints:
```python
from canvod.readers import GNSSReader

def process_data(reader: GNSSReader, filepath: Path):
    # Works with any GNSS reader
    dataset = reader.read(filepath)
```
"""

from canvod.readers.base import GNSSReader, RinexReader
from canvod.readers.rinex import Rnxv3Reader

__version__ = "0.1.0"

__all__ = [
    # Abstract interfaces
    "GNSSReader",
    "RinexReader",
    # Concrete implementations
    "Rnxv3Reader",
]
