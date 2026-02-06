---
title: canvod-auxiliary Documentation
description: Complete guide to using canvod-auxiliary for GNSS auxiliary data processing
---

# canvod-auxiliary Documentation

Welcome to the complete documentation for **canvod-auxiliary**, the auxiliary data augmentation package for GNSS VOD analysis.

## What is canvod-auxiliary?

`canvod-auxiliary` is a **Python package** for handling auxiliary GNSS data files including:

- **SP3 Ephemerides** - Satellite orbit positions and velocities
- **CLK Corrections** - Satellite clock corrections
- **Interpolation** - Temporal alignment with RINEX observations
- **Augmentation** - Enrich RINEX datasets with computed values

Part of the [canVODpy ecosystem](https://github.com/nfb2021/canvodpy).

## Who Should Use This?

This package is for:

- **GNSS Researchers** needing precise satellite positions and clock corrections
- **VOD Analysts** augmenting RINEX data with auxiliary information
- **Developers** building GNSS processing pipelines
- **Scientists** working with multi-GNSS observations

**No GNSS expertise assumed!** We explain everything from the ground up.

## Quick Navigation

### 🚀 Getting Started

**New to canvod-auxiliary?** Start here:

1. **[Installation →](installation.md)** - Install the package
2. **[Quick Start →](quickstart.md)** - Your first 5 minutes
3. **[Architecture →](architecture.md)** - Understand the design

### 📖 Core Documentation

**Deep dives into key topics:**

- **[SP3 Files →](sp3-files.md)** - Satellite ephemeris handling
- **[CLK Files →](clk-files.md)** - Clock correction processing
- **[Interpolation →](interpolation.md)** - Temporal alignment strategies
- **[Pipeline →](pipeline.md)** - Automated workflows
- **[Augmentation →](augmentation.md)** - Dataset enrichment

### 🔧 Reference

**Detailed API documentation:**

- **[API Reference →](api-reference.md)** - Complete API docs
- **[Internal Utilities →](internal-utilities.md)** - UREG, YYYYDOY, logging

### 💡 Examples

**Practical code examples:**

- **[Basic Usage →](examples/basic.md)** - Simple file operations
- **[Custom Interpolation →](examples/interpolation.md)** - Advanced strategies
- **[Pipeline Workflows →](examples/pipeline.md)** - Complete workflows

## Key Features

### ✨ SP3 File Support

```python
from canvod.aux import Sp3File

# Load and parse
sp3 = Sp3File.from_file("orbit.SP3")
data = sp3.data  # xarray Dataset with X, Y, Z, Vx, Vy, Vz

# Interpolate to new epochs
strategy = sp3.get_interpolation_strategy()
interpolated = strategy.interpolate(data, target_epochs)
```

**Features:**
- Cubic Hermite interpolation using velocities
- Linear fallback when velocities unavailable
- Automatic download from ESA/NASA CDDIS
- Thread-safe file handling

### ✨ Clock Corrections

```python
from canvod.aux import ClkFile

# Load clock file
clk = ClkFile.from_file("clock.CLK")
data = clk.data  # xarray Dataset with clock offsets

# Jump-aware interpolation
strategy = clk.get_interpolation_strategy()
interpolated = strategy.interpolate(data, target_epochs)
```

**Features:**
- Jump detection and segment-based interpolation
- Configurable jump thresholds
- Parallel processing per satellite
- Handles discontinuities gracefully

### ✨ Flexible Pipeline

```python
from canvod.aux import AuxDataPipeline

# Create pipeline
pipeline = AuxDataPipeline(
    agency="COD",
    product_type="final",
    aux_file_path="cache/"
)

# Get data (downloads if needed)
augmented = pipeline.get_or_create_aux_data(
    yyyydoy="2024015",
    target_epochs=epochs
)
```

**Features:**
- Automatic file discovery and caching
- Multi-threaded downloads
- Configurable FTP servers and agencies
- Thread-safe operations

### ✨ Augmentation Framework

```python
from canvod.aux import AuxDataAugmenter, SphericalCoordinateAugmentation

# Configure augmentation
augmenter = AuxDataAugmenter(
    pipeline=pipeline,
    steps=[SphericalCoordinateAugmentation()]
)

# Enrich dataset
enriched = augmenter.augment(rinex_dataset, context)
```

**Features:**
- Pluggable augmentation steps
- Spherical coordinate calculation
- Clock correction application
- Extensible via ABC pattern

## Installation

### From PyPI (Recommended)

```bash
pip install canvod-auxiliary
```

### Development Install

```bash
git clone https://github.com/nfb2021/canvodpy.git
cd canvodpy/packages/canvod-auxiliary
uv pip install -e .
```

See **[Installation Guide →](installation.md)** for detailed instructions.

## Quick Start

### 1. Basic SP3 Usage

```python
from pathlib import Path
from canvod.aux import Sp3File

# Load file
sp3 = Sp3File.from_file(Path("COD0MGXFIN_20240150000_01D_05M_ORB.SP3"))

# Access data
print(sp3.data)
# <xarray.Dataset>
# Dimensions:  (epoch: 289, sid: 190)
# Coordinates:
#   * epoch    (epoch) datetime64[ns] 2024-01-15T00:00:00 ...
#   * sid      (sid) object 'G01|L1|C' 'G01|L2|W' ...
# Data variables:
#     X        (epoch, sid) float64 ...
#     Y        (epoch, sid) float64 ...
#     Z        (epoch, sid) float64 ...
#     Vx       (epoch, sid) float64 ...
#     Vy       (epoch, sid) float64 ...
#     Vz       (epoch, sid) float64 ...
```

### 2. Interpolation

```python
import numpy as np
from canvod.aux import Sp3InterpolationStrategy, Sp3Config

# Configure strategy
config = Sp3Config(use_velocities=True)
strategy = Sp3InterpolationStrategy(config=config)

# Define target epochs (30-second intervals)
target_epochs = np.arange(
    np.datetime64('2024-01-15T00:00:00'),
    np.datetime64('2024-01-15T23:59:30'),
    np.timedelta64(30, 's')
)

# Interpolate
interpolated = strategy.interpolate(sp3.data, target_epochs)
```

### 3. Pipeline Workflow

```python
from canvod.aux import AuxDataPipeline
from pathlib import Path

# Create pipeline
pipeline = AuxDataPipeline(
    agency="COD",
    product_type="final",
    ftp_server="ftp://gssc.esa.int/gnss",
    aux_file_path=Path("aux_data")
)

# Process specific date
result = pipeline.get_or_create_aux_data(
    yyyydoy="2024015",
    target_epochs=my_epochs
)
```

See **[Quick Start Guide →](quickstart.md)** for more examples.

## Architecture Overview

### Package Structure

```
canvod.aux
├── _internal          # Internal utilities (UREG, YYYYDOY, logger)
├── reader             # AuxFile ABC base class
├── container          # FTP downloader, data containers
├── interpolation      # Interpolation strategies
├── sp3                # SP3 ephemeris handler
├── clk                # CLK corrections handler
├── pipeline           # AuxDataPipeline orchestration
└── augmentation       # Augmentation framework
```

### Design Patterns

**ABC Pattern:**
- `AuxFile` - Base class for all auxiliary files
- `Interpolator` - Base class for interpolation strategies
- `AugmentationStep` - Base class for augmentation operations

**Lazy Loading:**
- Data only loaded when accessed via `.data` property
- Reduces memory footprint for large files

**Strategy Pattern:**
- Different interpolation strategies for different file types
- Configurable behavior via config classes

See **[Architecture Guide →](architecture.md)** for complete details.

## Core Concepts

### 1. Auxiliary Files

**Definition:** GNSS products providing satellite state information beyond raw observations.

**Types supported:**
- **SP3** - Precise satellite orbits (positions + velocities)
- **CLK** - Satellite clock corrections
- **IONEX** - Ionospheric corrections (future)

### 2. Interpolation

**Why needed:** Auxiliary files have different temporal sampling than RINEX observations.

**Strategies:**
- **Hermite** - Cubic interpolation using velocities (SP3)
- **Linear** - Piecewise linear (fallback)
- **Jump-aware** - Segment-based for discontinuities (CLK)

### 3. Augmentation

**Purpose:** Enrich RINEX datasets with computed values from auxiliary data.

**Steps:**
- Compute spherical coordinates (φ, θ, r)
- Apply clock corrections
- Add auxiliary variables to dataset

## Integration with canVODpy

`canvod-auxiliary` is part of the canVODpy ecosystem:

```
canvod-readers → canvod-auxiliary → canvod-grids → canvod-vod
                     ↓
              canvod-store
                     ↓
               canvod-viz
```

**Workflow:**
1. **canvod-readers** - Read RINEX observations
2. **canvod-auxiliary** - Augment with auxiliary data ← **You are here**
3. **canvod-grids** - Map to hemisphere grids
4. **canvod-vod** - Calculate VOD
5. **canvod-store** - Store results
6. **canvod-viz** - Visualize outputs

## Best Practices

### 1. Use Pipeline for Production

```python
# ✅ Good - Handles caching, threading, errors
pipeline = AuxDataPipeline(...)
data = pipeline.get_or_create_aux_data(...)

# ❌ Avoid - Manual file management
sp3 = Sp3File.from_file(...)  # For simple scripts only
```

### 2. Configure FTP Properly

```python
# ✅ Good - Optional NASA CDDIS fallback
pipeline = AuxDataPipeline(
    ftp_server="ftp://gssc.esa.int/gnss",
    user_email="your@email.com"  # Enables NASA CDDIS
)

# ❌ Avoid - No fallback
pipeline = AuxDataPipeline(ftp_server="ftp://gssc.esa.int/gnss")
```

### 3. Use Appropriate Interpolation

```python
# ✅ Good - Use velocities when available
config = Sp3Config(use_velocities=True)

# ✅ Good - Set fallback method
config = Sp3Config(
    use_velocities=True,
    fallback_method='cubic'
)
```

### 4. Handle Errors Gracefully

```python
try:
    data = pipeline.get_or_create_aux_data(yyyydoy, epochs)
except FileNotFoundError:
    # File not available for this date
    logger.warning(f"No aux data for {yyyydoy}")
    # Use fallback or skip
```

## Getting Help

### Documentation
- **This site** - Complete package documentation
- **API Reference** - Detailed function/class docs
- **Examples** - Practical code samples

### Community
- **GitHub Issues** - Report bugs, request features
- **Discussions** - Ask questions, share ideas
- **Pull Requests** - Contribute code

### Resources
- [GitHub Repository](https://github.com/nfb2021/canvodpy)
- [canVODpy Main Docs](https://canvodpy.readthedocs.io)
- [TU Wien GEO](https://www.tuwien.ac.at/mg/geo)

## Next Steps

**Ready to get started?**

1. 📦 **[Install canvod-auxiliary →](installation.md)**
2. 🚀 **[Quick Start Tutorial →](quickstart.md)**
3. 📖 **[Read Architecture Guide →](architecture.md)**

**Or explore:**

- 📘 [SP3 Files Guide](sp3-files.md)
- 📗 [CLK Files Guide](clk-files.md)
- 📙 [Interpolation Guide](interpolation.md)
- 📕 [Pipeline Guide](pipeline.md)

---

*This documentation covers version 0.1.0. Last updated: January 2025.*
