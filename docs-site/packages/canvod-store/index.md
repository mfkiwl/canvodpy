# canvod-store Documentation


## Overview

`canvod-store` manages IceChunk-based storage for GNSS VOD analysis data, providing:

- **Storage strategies** - Skip, overwrite, or append modes
- **IceChunk integration** - Modern cloud-native storage format
- **Preprocessing** - Dataset preparation for storage
- **Reader utilities** - Load and query stored data

## Quick Example

```python
from canvod.store import IcechunkStore

# Initialize store
store = IcechunkStore(
    store_path="/path/to/store",
    strategy="append"
)

# Write dataset
store.write(dataset)

# Read dataset
ds = store.read(time_range=("2024-01-01", "2024-01-31"))
```

## Key Features

- **Compression** - Configurable compression algorithms
- **Chunking** - Optimized chunk strategies for time-series data
- **Versioning** - Built-in version control via IceChunk
- **Cloud-ready** - S3-compatible storage backends

## Next Steps

- [Storage Strategies](storage_strategies.md) - Learn about different storage modes
- [IceChunk Integration](icechunk.md) - Understand the storage format
- [API Reference](api_reference.md) - Complete API documentation
