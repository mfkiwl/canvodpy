# canvod-utils Documentation

```{toctree}
:maxdepth: 2
:caption: Contents

configuration
cli
metadata
api_reference
```

## Overview

`canvod-utils` provides configuration management and utility functions for the canVODpy framework:

- **Configuration system** - YAML-based settings with Pydantic validation
- **CLI tools** - Command-line interface for managing config
- **Metadata** - Software version and attribution information
- **Validation** - Type-safe configuration with helpful error messages

## Quick Start

### Initialize Configuration

```bash
# Create config templates
canvodpy config init

# Edit your settings
canvodpy config edit processing

# Validate configuration
canvodpy config validate
```

### Load Configuration in Code

```python
from canvod.utils.config import load_config

# Load configuration
config = load_config()

# Access values
print(config.processing.metadata.author)
print(config.gnss_root_dir)
print(config.processing.aux_data.agency)
```

### Access Software Metadata

```python
from canvod.utils._meta import SOFTWARE_ATTRS

# Add to xarray dataset
ds.attrs.update(SOFTWARE_ATTRS)
```

## Key Features

- **Type-safe** - Full Pydantic validation with IDE autocomplete
- **User-friendly** - YAML configuration files, not code
- **Validated** - Email format, paths, ranges all checked
- **Git-safe** - User configs gitignored automatically
- **API-ready** - Configuration serializable for services
- **CLI tools** - Easy management via `canvodpy config` commands

## Configuration Structure

```yaml
# config/processing.yaml
metadata:
  author: Nicolas F. Bader
  email: nicolas.bader@tuwien.ac.at
  institution: TU Wien

credentials:
  cddis_mail: your.email@example.com
  gnss_root_dir: /path/to/gnss/data

aux_data:
  agency: COD
  product_type: final

processing:
  time_aggregation_seconds: 15
  n_max_threads: 20
  aggregate_glonass_fdma: true

storage:
  stores_root_dir: /path/to/stores
  rinex_store_strategy: skip
  vod_store_strategy: overwrite
```

## Next Steps

- [Configuration System](configuration.md) - Learn about config structure
- [CLI Tools](cli.md) - Use command-line tools
- [Metadata Management](metadata.md) - Manage software metadata
- [API Reference](api_reference.md) - Complete API documentation
