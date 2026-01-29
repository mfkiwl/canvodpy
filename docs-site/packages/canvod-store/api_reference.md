# API Reference

## Store Management

### IcechunkStore

> See the unified API reference: [API Reference](../../docs/api/)


### Storage Strategies

```python
from canvod.store import StorageStrategy

# Available strategies
StorageStrategy.SKIP
StorageStrategy.OVERWRITE
StorageStrategy.APPEND
```

## Preprocessing

### IcechunkPreprocessor

> See the unified API reference: [API Reference](../../docs/api/)


Key methods:
- `prep_aux_ds()` - Complete preprocessing pipeline
- `map_aux_sv_to_sid()` - Convert satellite vehicle to signal ID dimension
- `pad_to_global_sid()` - Pad to all possible signals
- `normalize_sid_dtype()` - Ensure object dtype for sid coordinate
- `strip_fillvalue()` - Remove _FillValue attributes

## Reader Interface

### IcechunkReader

> See the unified API reference: [API Reference](../../docs/api/)


## Configuration

### Store Configuration

```python
from canvod.utils.config import load_config

config = load_config()

# Access storage config
storage_config = config.processing.storage
store_path = storage_config.get_rinex_store_path("rosalia")
strategy = storage_config.rinex_store_strategy
```

## Usage Examples

### Complete Workflow

```python
from canvod.store import IcechunkStore
from canvod.store.preprocessing import IcechunkPreprocessor
from canvod.utils.config import load_config

# Load configuration
config = load_config()

# Get store path
store_path = config.processing.storage.get_rinex_store_path("rosalia")

# Initialize store
store = IcechunkStore(
    store_path=store_path,
    strategy=config.processing.storage.rinex_store_strategy
)

# Preprocess dataset
preprocessed = IcechunkPreprocessor.prep_aux_ds(
    raw_dataset,
    aggregate_glonass_fdma=config.processing.processing.aggregate_glonass_fdma
)

# Write to store
store.write(preprocessed)

# Read back
reader = IcechunkReader(store_path)
ds = reader.read(time_range=("2024-01-01", "2024-01-31"))
```

### Advanced Configuration

```python
from icechunk import IcechunkStore
import zarr

# Custom compression
compressor = zarr.Blosc(
    cname=config.processing.icechunk.compression_algorithm,
    clevel=config.processing.icechunk.compression_level,
    shuffle=2
)

# Custom encoding
encoding = {
    "vod": {
        "compressor": compressor,
        "chunks": (
            config.processing.icechunk.chunk_strategies.vod_store.epoch,
            None  # Auto-chunk sid dimension
        )
    }
}

# Write with custom settings
ds.to_zarr(store, encoding=encoding)
```

## Type Hints

```python
from typing import Literal, Optional
from pathlib import Path
import xarray as xr

StrategyType = Literal["skip", "overwrite", "append"]

def write_to_store(
    dataset: xr.Dataset,
    store_path: Path,
    strategy: StrategyType = "skip",
    time_range: Optional[tuple[str, str]] = None
) -> None:
    """Write dataset to IceChunk store."""
    ...
```

## Error Handling

```python
from canvod.store.exceptions import (
    StoreNotFoundError,
    StoreCorruptedError,
    VersionNotFoundError
)

try:
    store = IcechunkStore(store_path)
    store.write(dataset)
except StoreNotFoundError:
    print("Store does not exist - creating new store")
    store = IcechunkStore.create(store_path)
except StoreCorruptedError as e:
    print(f"Store corrupted: {e}")
    store.repair()
except VersionNotFoundError:
    print("Version not found - using latest")
    store = IcechunkStore(store_path, version="latest")
```
