# Constants.py Cleanup - Migration Guide

## Summary

Moved user-configurable settings from `canvod/readers/gnss_specs/constants.py` to the configuration system.

## What Changed

### ✅ Kept in constants.py (True Constants)
- `UREG` - Unit registry
- `SPEEDOFLIGHT` - Physical constant
- `EPOCH_RECORD_INDICATOR` - RINEX format constant
- `FREQ_UNIT` - Unit definition
- `SEPTENTRIO_SAMPLING_INTERVALS` - Hardware capabilities
- `IGS_RNX_DUMP_INTERVALS` - Data availability

### 🔄 Moved to Configuration

| Old Location | New Location | Access |
|--------------|--------------|--------|
| `KEEP_RNX_VARS` | `config/processing.yaml` → `processing.keep_rnx_vars` | `config.processing.processing.keep_rnx_vars` |
| `COMPRESSION` | `config/processing.yaml` → `compression` | `config.processing.compression.zlib`, `.complevel` |
| `TIME_AGGR` | `config/processing.yaml` → `processing.time_aggregation_seconds` | `config.processing.processing.time_aggregation_seconds` |
| `AGGREGATE_GLONASS_FDMA` | `config/processing.yaml` → `processing.aggregate_glonass_fdma` | `config.processing.processing.aggregate_glonass_fdma` |
| `AUTHOR` | `config/processing.yaml` → `metadata.author` | `config.processing.metadata.author` |
| `EMAIL` | `config/processing.yaml` → `metadata.email` | `config.processing.metadata.email` |
| `INSTITUTION` | `config/processing.yaml` → `metadata.institution` | `config.processing.metadata.institution` |
| `DEPARTMENT` | `config/processing.yaml` → `metadata.department` | `config.processing.metadata.department` |
| `RESEARCH_GROUP` | `config/processing.yaml` → `metadata.research_group` | `config.processing.metadata.research_group` |
| `WEBSITE` | `config/processing.yaml` → `metadata.website` | `config.processing.metadata.website` |
| `SOFTWARE` | `canvod.utils._meta.SOFTWARE_ATTRS` | `from canvod.utils._meta import SOFTWARE_ATTRS` |

## Code Migration Examples

### Before (Old Way)
```python
from canvod.readers.gnss_specs.constants import (
    AUTHOR,
    EMAIL,
    KEEP_RNX_VARS,
    COMPRESSION,
    TIME_AGGR,
)

# Using constants
print(f"Author: {AUTHOR}")
vars_to_keep = KEEP_RNX_VARS
compression_level = COMPRESSION["complevel"]
time_window = TIME_AGGR.to(UREG.second).magnitude
```

### After (New Way)
```python
from canvod.utils.config import load_config
from canvod.utils._meta import SOFTWARE_ATTRS

# Load configuration
config = load_config()

# Using config
print(f"Author: {config.processing.metadata.author}")
vars_to_keep = config.processing.processing.keep_rnx_vars
compression_level = config.processing.compression.complevel
time_window = config.processing.processing.time_aggregation_seconds

# Software metadata
software_info = SOFTWARE_ATTRS
print(software_info["software"])  # "canvodpy v0.1.0"
```

### Writing Metadata to Output Files

**Before:**
```python
from canvod.readers.gnss_specs.constants import (
    AUTHOR, EMAIL, INSTITUTION, DEPARTMENT, SOFTWARE
)

ds.attrs["author"] = AUTHOR
ds.attrs["email"] = EMAIL
ds.attrs["institution"] = INSTITUTION
ds.attrs["department"] = DEPARTMENT
ds.attrs["software"] = SOFTWARE
```

**After:**
```python
from canvod.utils.config import load_config
from canvod.utils._meta import SOFTWARE_ATTRS

config = load_config()

# User metadata from config
ds.attrs.update(config.processing.metadata.to_attrs_dict())

# Software metadata (automatic versioning)
ds.attrs.update(SOFTWARE_ATTRS)
```

## Steps to Migrate Your Code

1. **Replace constants.py:**
   ```bash
   cd packages/canvod-readers/src/canvod/readers/gnss_specs/
   cp constants_CLEANED.py constants.py
   ```

2. **Update imports throughout your code:**
   ```python
   # Remove these imports
   from canvod.readers.gnss_specs.constants import (
       AUTHOR, EMAIL, KEEP_RNX_VARS, COMPRESSION, TIME_AGGR, AGGREGATE_GLONASS_FDMA
   )
   
   # Add these imports
   from canvod.utils.config import load_config
   from canvod.utils._meta import SOFTWARE_ATTRS
   
   # Load config once at module/function start
   config = load_config()
   ```

3. **Update your config file:**
   ```bash
   canvodpy config edit processing
   ```
   
   Add your metadata:
   ```yaml
   metadata:
     author: Nicolas F. Bader
     email: nicolas.bader@tuwien.ac.at
     institution: TU Wien
     department: Department of Geodesy and Geoinformation
     research_group: Climate and Environment Remote Sensing
     website: https://www.tuwien.at/en/mg/geo/climers
   ```

4. **Search and replace in your codebase:**
   ```bash
   # Find files that need updating
   grep -r "from canvod.readers.gnss_specs.constants import.*AUTHOR" packages/
   grep -r "from canvod.readers.gnss_specs.constants import.*EMAIL" packages/
   grep -r "from canvod.readers.gnss_specs.constants import.*KEEP_RNX_VARS" packages/
   ```

## Benefits

✅ **User-friendly:** Settings in YAML, not buried in source code  
✅ **Validation:** Pydantic validates all values (email format, paths, etc.)  
✅ **Separation:** Constants vs configuration clearly separated  
✅ **Version tracking:** Software version automatically included  
✅ **No git conflicts:** User settings gitignored  
✅ **API-ready:** Configuration serializable for future services  

## Verification

After migration, verify your config:
```bash
canvodpy config validate
canvodpy config show
```

Test in Python:
```python
from canvod.utils.config import load_config
from canvod.utils._meta import SOFTWARE_ATTRS

config = load_config()
print("Metadata:", config.processing.metadata.to_attrs_dict())
print("Software:", SOFTWARE_ATTRS)
print("Keep vars:", config.processing.processing.keep_rnx_vars)
print("Compression:", config.processing.compression.complevel)
```
