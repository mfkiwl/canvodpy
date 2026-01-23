# API Reference

## Configuration Loading

### load_config()

```{eval-rst}
.. autofunction:: canvod.utils.config.load_config
```

**Usage:**
```python
from canvod.utils.config import load_config

config = load_config()
```

## Configuration Models

### CanvodConfig

```{eval-rst}
.. autoclass:: canvod.utils.config.models.CanvodConfig
   :members:
   :undoc-members:
   :show-inheritance:
```

### ProcessingConfig

```{eval-rst}
.. autoclass:: canvod.utils.config.models.ProcessingConfig
   :members:
   :undoc-members:
   :show-inheritance:
```

### MetadataConfig

```{eval-rst}
.. autoclass:: canvod.utils.config.models.MetadataConfig
   :members:
   :undoc-members:
   :show-inheritance:
```

**Methods:**
```python
def to_attrs_dict() -> dict[str, str]:
    """Convert to dictionary for xarray attributes."""
```

### CredentialsConfig

```{eval-rst}
.. autoclass:: canvod.utils.config.models.CredentialsConfig
   :members:
   :undoc-members:
   :show-inheritance:
```

### AuxDataConfig

```{eval-rst}
.. autoclass:: canvod.utils.config.models.AuxDataConfig
   :members:
   :undoc-members:
   :show-inheritance:
```

**Methods:**
```python
def get_ftp_servers(cddis_mail: str | None) -> list[tuple[str, str | None]]:
    """Get FTP servers based on credentials."""
```

### ProcessingParams

```{eval-rst}
.. autoclass:: canvod.utils.config.models.ProcessingParams
   :members:
   :undoc-members:
   :show-inheritance:
```

### CompressionConfig

```{eval-rst}
.. autoclass:: canvod.utils.config.models.CompressionConfig
   :members:
   :undoc-members:
   :show-inheritance:
```

### IcechunkConfig

```{eval-rst}
.. autoclass:: canvod.utils.config.models.IcechunkConfig
   :members:
   :undoc-members:
   :show-inheritance:
```

### StorageConfig

```{eval-rst}
.. autoclass:: canvod.utils.config.models.StorageConfig
   :members:
   :undoc-members:
   :show-inheritance:
```

**Methods:**
```python
def get_rinex_store_path(site_name: str) -> Path:
    """Get RINEX store path for a site."""

def get_vod_store_path(site_name: str) -> Path:
    """Get VOD store path for a site."""
```

### SitesConfig

```{eval-rst}
.. autoclass:: canvod.utils.config.models.SitesConfig
   :members:
   :undoc-members:
   :show-inheritance:
```

### SidsConfig

```{eval-rst}
.. autoclass:: canvod.utils.config.models.SidsConfig
   :members:
   :undoc-members:
   :show-inheritance:
```

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
