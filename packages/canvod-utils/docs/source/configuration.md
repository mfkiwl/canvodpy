# Configuration System

## Overview

The canvod-utils configuration system provides:

1. **YAML-based configuration** - Human-readable settings
2. **Pydantic validation** - Type-safe with helpful errors
3. **Hierarchical structure** - Organized by domain
4. **Default values** - Sensible package defaults
5. **User overrides** - Custom settings in `config/`

## Configuration Files

### Structure

```
canvodpy/
├── config/                              # User configuration
│   ├── processing.yaml                 # YOUR settings (gitignored)
│   ├── sites.yaml                      # YOUR research sites
│   ├── sids.yaml                       # YOUR signal selection
│   ├── processing.yaml.example         # Template
│   ├── sites.yaml.example              # Template
│   └── sids.yaml.example               # Template
│
└── packages/canvod-utils/
    └── src/canvod/utils/config/
        └── defaults/                    # Package defaults
            ├── processing.yaml
            ├── sites.yaml
            └── sids.yaml
```

### Priority

```
Package defaults < User config
```

User config overrides package defaults for any specified values.

## Configuration Schema

### Processing Configuration

```yaml
# config/processing.yaml

# Metadata (written to output files)
metadata:
  author: Nicolas François Bader
  email: nicolas.bader@tuwien.ac.at
  institution: TU Wien
  department: Department of Geodesy and Geoinformation  # Optional
  research_group: Climate and Environment Remote Sensing  # Optional
  website: https://www.tuwien.at/en/mg/geo/climers  # Optional

# Credentials & paths
credentials:
  cddis_mail: your.email@example.com  # Optional (enables NASA CDDIS)
  gnss_root_dir: /path/to/gnss/data   # Required

# Auxiliary data settings
aux_data:
  agency: COD              # COD, GFZ, IGS, ESA, etc.
  product_type: final      # final, rapid, ultra-rapid

# Processing parameters
processing:
  time_aggregation_seconds: 15     # 1-300
  n_max_threads: 20                # 1-100
  keep_rnx_vars: [SNR]             # Variables to keep
  aggregate_glonass_fdma: true     # Aggregate GLONASS FDMA bands

# Compression settings
compression:
  zlib: true
  complevel: 5  # 0-9

# IceChunk storage settings
icechunk:
  compression_level: 5                    # 1-9
  compression_algorithm: zstd             # zstd, lz4, gzip
  inline_threshold: 512                   # bytes
  get_concurrency: 1                      # parallel reads
  chunk_strategies:
    rinex_store:
      epoch: 34560   # ~24h @ 2.5s sampling
      sid: -1        # All signals
    vod_store:
      epoch: 34560
      sid: -1

# Storage strategies
storage:
  stores_root_dir: /path/to/stores
  rinex_store_strategy: skip      # skip, overwrite, append
  rinex_store_expire_days: 2
  vod_store_strategy: overwrite
```

### Sites Configuration

```yaml
# config/sites.yaml

sites:
  rosalia:
    base_dir: /path/to/rosalia
    receivers:
      reference_01:
        type: reference
        directory: 01_reference
      canopy_01:
        type: canopy
        directory: 02_canopy
    vod_analyses:
      canopy_01_vs_reference_01:
        canopy_receiver: canopy_01
        reference_receiver: reference_01

  tuw:
    base_dir: /path/to/tuw
    receivers:
      rooftop:
        type: reference
        directory: rooftop
```

### Signal ID Configuration

```yaml
# config/sids.yaml

mode: all  # all, preset, custom

# For mode: preset
preset: GPS_L1  # GPS_L1, GPS_L1L2, MULTI_FREQ

# For mode: custom
custom_sids:
  - G01|L1|C
  - G02|L1|C
  - E01|E1|C
```

## Using Configuration

### Load Configuration

```python
from canvod.utils.config import load_config

# Load all configuration
config = load_config()

# Access nested values
author = config.processing.metadata.author
agency = config.processing.aux_data.agency
store_path = config.processing.storage.stores_root_dir
```

### Access Shortcuts

```python
# Direct access to commonly used values
gnss_root = config.gnss_root_dir  # Shortcut
cddis_mail = config.cddis_mail     # Shortcut

# Equivalent to:
gnss_root = config.processing.credentials.gnss_root_dir
cddis_mail = config.processing.credentials.cddis_mail
```

### Get FTP Servers

```python
# Auto-detect FTP servers based on credentials
servers = config.processing.aux_data.get_ftp_servers(config.cddis_mail)

# If cddis_mail is set:
# [("ftp://gdc.cddis.eosdis.nasa.gov", email),
#  ("ftp://gssc.esa.int/gnss", None)]

# If cddis_mail is None:
# [("ftp://gssc.esa.int/gnss", None)]
```

### Get Store Paths

```python
# Get store paths for a site
rinex_store = config.processing.storage.get_rinex_store_path("rosalia")
# → /path/to/stores/rosalia/rinex

vod_store = config.processing.storage.get_vod_store_path("rosalia")
# → /path/to/stores/rosalia/vod
```

### Get Signal IDs

```python
# Get effective list of SIDs based on mode
sids = config.sids.get_sids()

# Returns:
# - All SIDs if mode="all"
# - Preset SIDs if mode="preset"
# - Custom SIDs if mode="custom"
```

## Validation

### Email Validation

```python
from canvod.utils.config.models import MetadataConfig

# Valid
metadata = MetadataConfig(
    author="John Doe",
    email="john@example.com",  # ✅ Valid email
    institution="University"
)

# Invalid
metadata = MetadataConfig(
    author="John Doe",
    email="not-an-email",  # ❌ Validation error
    institution="University"
)
```

### Path Validation

```python
from canvod.utils.config.models import CredentialsConfig

# Valid - path exists
creds = CredentialsConfig(
    gnss_root_dir="/existing/path",  # ✅ Path exists
    cddis_mail=None
)

# Invalid - path doesn't exist
creds = CredentialsConfig(
    gnss_root_dir="/nonexistent/path",  # ❌ Validation error
    cddis_mail=None
)
```

### Range Validation

```python
from canvod.utils.config.models import ProcessingParams

# Valid
params = ProcessingParams(
    time_aggregation_seconds=15,  # ✅ 1-300
    n_max_threads=20,              # ✅ 1-100
    keep_rnx_vars=["SNR"],
    aggregate_glonass_fdma=True
)

# Invalid
params = ProcessingParams(
    time_aggregation_seconds=500,  # ❌ Out of range
    n_max_threads=200,             # ❌ Out of range
    keep_rnx_vars=["SNR"],
    aggregate_glonass_fdma=True
)
```

## Error Handling

### Friendly Error Messages

```python
try:
    config = load_config()
except ValueError as e:
    print(f"Configuration error: {e}")
```

**Example errors:**

```
❌ Validation failed:
   - email: value is not a valid email address
   - gnss_root_dir: Path does not exist: /bad/path
   - time_aggregation_seconds: ensure this value is less than or equal to 300
```

### Typo Detection

```python
# config/processing.yaml with typo
metadta:  # ❌ Typo: should be "metadata"
  author: John
```

**Error:**
```
❌ Extra fields not permitted: metadta
   Did you mean: metadata?
```

## Advanced Usage

### Programmatic Configuration

```python
from canvod.utils.config.models import (
    CanvodConfig,
    ProcessingConfig,
    MetadataConfig
)

# Create configuration programmatically
config = CanvodConfig(
    processing=ProcessingConfig(
        metadata=MetadataConfig(
            author="John Doe",
            email="john@example.com",
            institution="University"
        ),
        # ... other settings
    ),
    sites=...,
    sids=...
)
```

### Serialization

```python
# To dictionary
config_dict = config.model_dump()

# To JSON
config_json = config.model_dump_json(indent=2)

# From dictionary
config = CanvodConfig(**config_dict)

# From JSON
import json
config = CanvodConfig(**json.loads(config_json))
```

### Partial Updates

```python
# Load existing config
config = load_config()

# Update specific value
config.processing.processing.n_max_threads = 40

# Validate
config.model_validate(config)
```

## Best Practices

### 1. Never Commit User Config

```gitignore
# .gitignore
config/processing.yaml
config/sites.yaml
config/sids.yaml
```

### 2. Always Provide Examples

```yaml
# config/processing.yaml.example
metadata:
  author: Your Name
  email: your.email@example.com
```

### 3. Use Type Hints

```python
from canvod.utils.config import CanvodConfig

def process_data(config: CanvodConfig) -> None:
    # IDE autocomplete works!
    author = config.processing.metadata.author
```

### 4. Validate Early

```python
# At application startup
config = load_config()  # Fails fast if invalid

# Then use throughout
process_data(config)
store_results(config)
```

## Troubleshooting

### Config Not Found

```bash
❌ Warning: config/processing.yaml not found, using defaults
   Run: canvodpy config init
```

**Solution:**
```bash
canvodpy config init
canvodpy config edit processing
```

### Validation Errors

```bash
❌ Validation failed:
   - gnss_root_dir: Path does not exist
```

**Solution:**
```bash
# Create the directory
mkdir -p /path/to/gnss/data

# Or update config to existing path
canvodpy config edit processing
```

### Permission Errors

```bash
❌ Could not create stores directory
```

**Solution:**
```bash
# Create manually with correct permissions
mkdir -p /path/to/stores
chmod 755 /path/to/stores
```
