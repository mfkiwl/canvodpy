# Metadata Management

## Overview

The metadata system provides:

1. **Software attribution** - Version, URL, authorship
2. **User metadata** - Researcher information for outputs
3. **Centralized versioning** - Single source of truth

## Software Metadata

### Location

```python
from canvod.utils._meta import SOFTWARE_ATTRS, __version__
```

### Contents

```python
SOFTWARE_ATTRS = {
    "software": "canvodpy",
    "software_url": "https://github.com/nfb2021/canvodpy",
    "version": "0.1.0"
}

__version__ = "0.1.0"
```

### Usage

```python
import xarray as xr
from canvod.utils._meta import SOFTWARE_ATTRS

# Create dataset
ds = xr.Dataset(...)

# Add software metadata
ds.attrs.update(SOFTWARE_ATTRS)

# Result:
# ds.attrs = {
#     "software": "canvodpy",
#     "software_url": "https://github.com/nfb2021/canvodpy",
#     "version": "0.1.0",
#     ...
# }
```

## User Metadata

### Configuration

User metadata is configured in `config/processing.yaml`:

```yaml
metadata:
  author: Nicolas F. Bader
  email: nicolas.bader@tuwien.ac.at
  institution: TU Wien
  department: Department of Geodesy and Geoinformation  # Optional
  research_group: Climate and Environment Remote Sensing  # Optional
  website: https://www.tuwien.at/en/mg/geo/climers  # Optional
```

### Loading

```python
from canvod.utils.config import load_config

config = load_config()
metadata = config.processing.metadata

print(metadata.author)        # "Nicolas F. Bader"
print(metadata.email)         # "nicolas.bader@tuwien.ac.at"
print(metadata.institution)   # "TU Wien"
```

### Converting to Attributes

```python
# Convert to dictionary for xarray attrs
attrs_dict = metadata.to_attrs_dict()

# Result:
# {
#     "author": "Nicolas F. Bader",
#     "author_email": "nicolas.bader@tuwien.ac.at",
#     "institution": "TU Wien",
#     "department": "Department of Geodesy and Geoinformation",
#     "research_group": "Climate and Environment Remote Sensing",
#     "website": "https://www.tuwien.at/en/mg/geo/climers"
# }
```

## Complete Metadata Workflow

### 1. Configure User Metadata

```bash
canvodpy config edit processing
```

```yaml
metadata:
  author: Your Name
  email: your.email@institution.edu
  institution: Your Institution
```

### 2. Load in Code

```python
from canvod.utils.config import load_config
from canvod.utils._meta import SOFTWARE_ATTRS

config = load_config()
```

### 3. Add to Output

```python
import xarray as xr

# Create dataset
ds = xr.Dataset(
    data_vars={"vod": (["epoch", "sid"], vod_values)},
    coords={"epoch": epochs, "sid": sids}
)

# Add all metadata
ds.attrs.update(config.processing.metadata.to_attrs_dict())
ds.attrs.update(SOFTWARE_ATTRS)

# Save
ds.to_netcdf("output.nc")
```

### 4. Result

NetCDF file attributes:
```
:author = "Nicolas F. Bader" ;
:author_email = "nicolas.bader@tuwien.ac.at" ;
:institution = "TU Wien" ;
:department = "Department of Geodesy and Geoinformation" ;
:research_group = "Climate and Environment Remote Sensing" ;
:website = "https://www.tuwien.at/en/mg/geo/climers" ;
:software = "canvodpy" ;
:software_url = "https://github.com/nfb2021/canvodpy" ;
:version = "0.1.0" ;
:creation_date = "2026-01-23T15:30:00Z" ;
```

## Version Management

### Updating Version

```python
# packages/canvod-utils/src/canvod/utils/_meta.py

__version__ = "0.2.0"  # Update here

SOFTWARE_ATTRS = {
    "software": "canvodpy",
    "software_url": "https://github.com/nfb2021/canvodpy",
    "version": __version__  # Automatically uses new version
}
```

### Version in Package

```python
# In any package
from canvod.utils import __version__

print(f"canvodpy version: {__version__}")
```

### Version in Scripts

```bash
# Get version programmatically
python -c "from canvod.utils import __version__; print(__version__)"
```

## Metadata Best Practices

### 1. Always Include Both

```python
# ✅ Good - includes both user and software metadata
ds.attrs.update(config.processing.metadata.to_attrs_dict())
ds.attrs.update(SOFTWARE_ATTRS)

# ❌ Bad - missing user metadata
ds.attrs.update(SOFTWARE_ATTRS)

# ❌ Bad - missing software metadata
ds.attrs.update(config.processing.metadata.to_attrs_dict())
```

### 2. Add Creation Date

```python
from datetime import datetime, timezone

ds.attrs.update(config.processing.metadata.to_attrs_dict())
ds.attrs.update(SOFTWARE_ATTRS)
ds.attrs["creation_date"] = datetime.now(timezone.utc).isoformat()
```

### 3. Add Processing Info

```python
ds.attrs.update(config.processing.metadata.to_attrs_dict())
ds.attrs.update(SOFTWARE_ATTRS)
ds.attrs["processing_date"] = datetime.now(timezone.utc).isoformat()
ds.attrs["time_aggregation"] = config.processing.processing.time_aggregation_seconds
ds.attrs["agency"] = config.processing.aux_data.agency
ds.attrs["product_type"] = config.processing.aux_data.product_type
```

### 4. Validate Email Format

```python
from canvod.utils.config.models import MetadataConfig

# Pydantic validates email format automatically
try:
    metadata = MetadataConfig(
        author="John Doe",
        email="invalid-email",  # ❌ Will raise ValidationError
        institution="University"
    )
except ValueError as e:
    print(f"Invalid email: {e}")
```

## Metadata Templates

### Minimal Template

```python
from canvod.utils.config import load_config
from canvod.utils._meta import SOFTWARE_ATTRS

config = load_config()

def add_metadata(ds: xr.Dataset) -> xr.Dataset:
    """Add standard metadata to dataset."""
    ds.attrs.update(config.processing.metadata.to_attrs_dict())
    ds.attrs.update(SOFTWARE_ATTRS)
    return ds
```

### Extended Template

```python
from datetime import datetime, timezone
from canvod.utils.config import load_config
from canvod.utils._meta import SOFTWARE_ATTRS

config = load_config()

def add_full_metadata(
    ds: xr.Dataset,
    processing_info: dict | None = None
) -> xr.Dataset:
    """Add complete metadata including processing details."""
    
    # User metadata
    ds.attrs.update(config.processing.metadata.to_attrs_dict())
    
    # Software metadata
    ds.attrs.update(SOFTWARE_ATTRS)
    
    # Timestamps
    ds.attrs["creation_date"] = datetime.now(timezone.utc).isoformat()
    
    # Processing info
    if processing_info:
        ds.attrs.update(processing_info)
    else:
        ds.attrs["time_aggregation"] = config.processing.processing.time_aggregation_seconds
        ds.attrs["agency"] = config.processing.aux_data.agency
        ds.attrs["product_type"] = config.processing.aux_data.product_type
    
    return ds
```

## CF Conventions

For CF-compliant NetCDF files:

```python
ds.attrs.update({
    # User metadata
    **config.processing.metadata.to_attrs_dict(),
    
    # Software metadata
    **SOFTWARE_ATTRS,
    
    # CF conventions
    "Conventions": "CF-1.8",
    "title": "GNSS Vegetation Optical Depth",
    "summary": "VOD derived from GNSS signal attenuation",
    "keywords": "GNSS, VOD, vegetation, remote sensing",
    "source": "GNSS receivers",
    "processing_level": "3",
    "date_created": datetime.now(timezone.utc).isoformat(),
    
    # Spatial coverage (if applicable)
    "geospatial_lat_min": lat_min,
    "geospatial_lat_max": lat_max,
    "geospatial_lon_min": lon_min,
    "geospatial_lon_max": lon_max,
})
```

## Troubleshooting

### Missing Author Information

```python
# Check if metadata is configured
config = load_config()

if config.processing.metadata.author == "Unknown":
    print("⚠️  Metadata not configured!")
    print("Run: canvodpy config edit processing")
```

### Invalid Email

```yaml
# ❌ Invalid
metadata:
  email: not-an-email

# ✅ Valid
metadata:
  email: user@example.com
```

### Version Mismatch

```python
# Check versions match
from canvod.utils import __version__
from canvod.utils._meta import SOFTWARE_ATTRS

assert SOFTWARE_ATTRS["version"] == __version__
```
