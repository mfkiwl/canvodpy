# API Reference

## Configuration Loading

### load_config()

> See the unified API reference: [API Reference](../../docs/api/)


**Usage:**
```python
from canvod.utils.config import load_config

config = load_config()
```

## Configuration Models

### CanvodConfig

> See the unified API reference: [API Reference](../../docs/api/)


### ProcessingConfig

> See the unified API reference: [API Reference](../../docs/api/)


### MetadataConfig

> See the unified API reference: [API Reference](../../docs/api/)


**Methods:**
```python
def to_attrs_dict() -> dict[str, str]:
    """Convert to dictionary for xarray attributes."""
```

### CredentialsConfig

> See the unified API reference: [API Reference](../../docs/api/)


### AuxDataConfig

> See the unified API reference: [API Reference](../../docs/api/)


**Methods:**
```python
def get_ftp_servers(cddis_mail: str | None) -> list[tuple[str, str | None]]:
    """Get FTP servers based on credentials."""
```

### ProcessingParams

> See the unified API reference: [API Reference](../../docs/api/)


### CompressionConfig

> See the unified API reference: [API Reference](../../docs/api/)


### IcechunkConfig

> See the unified API reference: [API Reference](../../docs/api/)


### StorageConfig

> See the unified API reference: [API Reference](../../docs/api/)


**Methods:**
```python
def get_rinex_store_path(site_name: str) -> Path:
    """Get RINEX store path for a site."""

def get_vod_store_path(site_name: str) -> Path:
    """Get VOD store path for a site."""
```

### SitesConfig

> See the unified API reference: [API Reference](../../docs/api/)


### SidsConfig

> See the unified API reference: [API Reference](../../docs/api/)


**Methods:**
```python
def get_sids() -> list[str]:
    """Get effective list of signal IDs based on mode."""
```

## Metadata

### SOFTWARE_ATTRS

```python
from canvod.utils._meta import SOFTWARE_ATTRS

SOFTWARE_ATTRS: dict[str, str] = {
    "software": "canvodpy",
    "software_url": "https://github.com/nfb2021/canvodpy",
    "version": "0.1.0"
}
```

### __version__

```python
from canvod.utils import __version__

__version__: str = "0.1.0"
```

## CLI

### Commands

All CLI commands are accessed via:

```bash
canvodpy config <command>
```

Available commands:
- `init` - Initialize configuration files
- `validate` - Validate configuration
- `show` - Display configuration
- `edit` - Edit configuration file

See [CLI Tools](cli.md) for detailed documentation.

## Type Hints

```python
from typing import Literal
from pathlib import Path
from pydantic import EmailStr

# Strategy types
StrategyType = Literal["skip", "overwrite", "append"]

# Product types
ProductType = Literal["final", "rapid", "ultra-rapid"]

# Compression algorithms
CompressionAlgorithm = Literal["zstd", "lz4", "gzip"]

# Signal ID modes
SidMode = Literal["all", "preset", "custom"]
```

## Usage Examples

### Complete Workflow

```python
from canvod.utils.config import load_config
from canvod.utils._meta import SOFTWARE_ATTRS
import xarray as xr

# Load configuration
config = load_config()

# Access values
gnss_root = config.gnss_root_dir
agency = config.processing.aux_data.agency
rinex_store = config.processing.storage.get_rinex_store_path("rosalia")

# Get FTP servers
servers = config.processing.aux_data.get_ftp_servers(config.cddis_mail)

# Add metadata to dataset
ds = xr.Dataset(...)
ds.attrs.update(config.processing.metadata.to_attrs_dict())
ds.attrs.update(SOFTWARE_ATTRS)
```

### Configuration Validation

```python
from canvod.utils.config.models import MetadataConfig
from pydantic import ValidationError

try:
    metadata = MetadataConfig(
        author="John Doe",
        email="invalid-email",  # Will raise ValidationError
        institution="University"
    )
except ValidationError as e:
    print(f"Validation errors: {e}")
```

### Programmatic Configuration

```python
from canvod.utils.config.models import (
    CanvodConfig,
    ProcessingConfig,
    MetadataConfig,
    CredentialsConfig
)

config = CanvodConfig(
    processing=ProcessingConfig(
        metadata=MetadataConfig(
            author="John Doe",
            email="john@example.com",
            institution="University"
        ),
        credentials=CredentialsConfig(
            gnss_root_dir="/path/to/data",
            cddis_mail=None
        ),
        # ... other settings
    ),
    sites=...,
    sids=...
)

# Validate
config.model_validate(config)

# Serialize
config_dict = config.model_dump()
config_json = config.model_dump_json(indent=2)
```

## Error Handling

```python
from canvod.utils.config import load_config
from pydantic import ValidationError

try:
    config = load_config()
except FileNotFoundError:
    print("Configuration file not found")
    print("Run: canvodpy config init")
except ValidationError as e:
    print(f"Configuration validation failed:")
    for error in e.errors():
        print(f"  - {error['loc'][0]}: {error['msg']}")
except Exception as e:
    print(f"Unexpected error: {e}")
```
