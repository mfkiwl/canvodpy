# 🎯 canvodpy High-Level API Design

**Status:** Gap Analysis & Architecture Proposal  
**Date:** 2025-01-21  
**Purpose:** Design the public-facing API for canvodpy

---

## 📊 Current Status: What Exists vs What's Missing

### ✅ What We Have (Low-Level Components)

| Package | Status | Lines | Description |
|---------|--------|-------|-------------|
| **canvod-readers** | ✅ Complete | 2,900+ | RINEX parsing, validation |
| **canvod-aux** | ✅ Complete | 2,500+ | Ephemeris, clocks, preprocessing |
| **canvod-grids** | ✅ Complete | 360+ | Hemisphere grid structures |
| **canvod-viz** | ✅ Complete | 1,370+ | 2D/3D visualization |

**Total:** ~7,130 lines of production code + comprehensive tests

---

### ❌ What's Missing (High-Level Components)

From `gnssvodpy`, we need these public-facing components:

#### 1. **canvod-store** (Data Storage Layer)
**Source:** `gnssvodpy/icechunk_manager/`

Components needed:
- `MyIcechunkStore` - Icechunk wrapper with versioning
- `GnssResearchSite` - Site manager (receivers, stores)
- Store creation helpers (`create_rinex_store`, `create_vod_store`)
- Metadata management
- Group operations

**Critical for:** Persistent data storage, versioning, collaboration

#### 2. **canvod-vod** (VOD Calculations)
**Source:** `gnssvodpy/vod/`

Components needed:
- `VODCalculator` - Main VOD algorithm
- `TauOmegaZerothOrder` - Tau-omega model
- Signal attenuation computation
- Quality metrics

**Critical for:** Actual vegetation optical depth calculations

#### 3. **canvodpy (Umbrella)** - High-Level Public API
**Source:** `gnssvodpy/processor/`, `gnssvodpy/globals.py`

Components needed:
- `Site` - User-facing site management
- `Pipeline` - Processing orchestration
- `Config` - Configuration management
- Convenience functions for common workflows

**Critical for:** User experience, clean API

---

## 🏗️ Proposed Architecture

### Package Dependencies (Bottom-Up)

```
Level 0: canvod-readers (RINEX parsing)
         ├─ georinex, xarray, pandas
         └─ No internal dependencies

Level 1: canvod-aux (Auxiliary data)
         ├─ canvod-readers
         ├─ scipy, numpy, ftplib
         └─ SP3, CLK file processing

Level 2: canvod-grids (Grid structures)
         ├─ numpy
         └─ No internal dependencies

Level 3a: canvod-vod (VOD calculations)
          ├─ canvod-readers
          ├─ canvod-aux
          ├─ numpy, xarray
          └─ Signal processing algorithms

Level 3b: canvod-store (Storage)
          ├─ canvod-readers
          ├─ canvod-grids
          ├─ icechunk, zarr, xarray
          └─ Persistence layer

Level 4: canvod-viz (Visualization)
         ├─ canvod-grids
         ├─ matplotlib, plotly
         └─ Plotting and rendering

Level 5: canvodpy (Umbrella + High-Level API)
         ├─ All above packages
         ├─ canvod-store (primary dependency)
         ├─ canvod-vod (primary dependency)
         └─ Pipeline orchestration
```

---

## 🎯 High-Level API Design (canvodpy)

### User-Facing API (What Researchers Need)

```python
# ============================================================================
# Simple Case: Process one day of data
# ============================================================================

from canvodpy import Site, Pipeline

# Initialize site
site = Site("Rosalia")  # Loads from ~/.canvod/sites.toml

# Process one day
pipeline = Pipeline(site)
results = pipeline.process_date("2025001")

# results = {
#     'canopy_01': xr.Dataset,
#     'canopy_02': xr.Dataset,
#     'reference_01': xr.Dataset,
#     'reference_02': xr.Dataset,
# }

# Calculate VOD
vod_results = pipeline.calculate_vod(
    canopy='canopy_01',
    reference='reference_01',
    date="2025001"
)

# Visualize
from canvodpy import visualize

fig = visualize.hemisphere_2d(vod_results['vod'], title="VOD Distribution")
fig.savefig("vod_2025001.png")


# ============================================================================
# Batch Processing: Multiple days
# ============================================================================

# Process date range
for date_key, datasets in pipeline.process_date_range("2025001", "2025007"):
    print(f"Processed {date_key}: {len(datasets)} receivers")
    
    # Auto-store to Icechunk
    site.store_rinex(date_key, datasets)


# ============================================================================
# Advanced: Custom configuration
# ============================================================================

# Custom site (programmatic)
site = Site.from_config({
    'name': 'MySite',
    'receivers': {
        'canopy_01': {'type': 'canopy', 'directory': '/path/to/data'},
        'reference_01': {'type': 'reference', 'directory': '/path/to/ref'},
    },
    'rinex_store': '/path/to/rinex_store',
    'vod_store': '/path/to/vod_store',
})

# Custom pipeline
pipeline = Pipeline(
    site=site,
    aux_agency='COD',        # CODE analysis center
    aux_product='rapid',     # Rapid products
    keep_vars=['C1C', 'L1C', 'S1C'],  # Only GPS L1
    n_workers=8,
)


# ============================================================================
# Data Management
# ============================================================================

# Access stored data
rinex_data = site.load_rinex('canopy_01', date_range=("2025001", "2025007"))
vod_data = site.load_vod('canopy_01_vs_reference_01', date="2025001")

# Store metadata
site.store_vod(
    analysis_name='canopy_01_vs_reference_01',
    vod_dataset=vod_results,
    metadata={'processing_version': '0.1.0', 'notes': 'Test run'}
)

# List available data
print(site.list_rinex_dates())
print(site.list_vod_analyses())


# ============================================================================
# Analysis Workflows
# ============================================================================

from canvodpy import analysis

# Time series analysis
ts = analysis.time_series(
    site=site,
    analysis='canopy_01_vs_reference_01',
    start_date="2024001",
    end_date="2024365"
)

# Seasonal patterns
seasonal = analysis.seasonal_decomposition(ts, period=365)

# Comparison across receivers
comparison = analysis.compare_receivers(
    site=site,
    date="2025001",
    receivers=['canopy_01', 'canopy_02']
)
```

---

## 📦 Detailed Design: Missing Packages

### 1. canvod-store (Priority: CRITICAL)

**Purpose:** Icechunk-based storage with versioning

**Public API:**
```python
from canvod.store import (
    IcechunkStore,           # Low-level store wrapper
    create_rinex_store,      # Factory for RINEX store
    create_vod_store,        # Factory for VOD store
    StoreMetadata,           # Metadata management
)

# Low-level usage
store = create_rinex_store("/path/to/store")
store.write_group("canopy_01", dataset)
ds = store.read_group("canopy_01", time_range=("2025-01-01", "2025-01-07"))
```

**Key Features:**
- Icechunk integration
- Versioned snapshots
- Metadata tracking
- Time-based queries
- Group management

**Implementation (~500 lines):**
```
src/canvod/store/
├── __init__.py
├── base.py              # IcechunkStore wrapper
├── rinex.py             # RINEX-specific store
├── vod.py               # VOD-specific store
├── metadata.py          # Metadata management
└── utils.py             # Helpers
```

---

### 2. canvod-vod (Priority: CRITICAL)

**Purpose:** VOD calculation algorithms

**Public API:**
```python
from canvod.vod import (
    VODCalculator,           # Main calculator
    TauOmegaModel,          # Tau-omega model
    calculate_vod,          # Convenience function
)

# Simple usage
vod = calculate_vod(
    canopy_data=canopy_ds,
    reference_data=reference_ds,
    grid=hemigrid,
)

# Advanced usage
calculator = VODCalculator(model=TauOmegaModel())
vod = calculator.compute(
    canopy_signal=canopy_ds['S1C'],
    reference_signal=reference_ds['S1C'],
    canopy_phase=canopy_ds['L1C'],
    reference_phase=reference_ds['L1C'],
)
```

**Key Features:**
- Signal attenuation calculation
- Phase difference computation
- Quality filtering
- Grid aggregation

**Implementation (~400 lines):**
```
src/canvod/vod/
├── __init__.py
├── calculator.py        # VODCalculator
├── models.py            # Tau-omega models
├── signal.py            # Signal processing
└── quality.py           # Quality metrics
```

---

### 3. canvodpy (Umbrella) (Priority: HIGH)

**Purpose:** High-level user-facing API

**Public API:**
```python
from canvodpy import (
    Site,                 # Site management
    Pipeline,             # Processing orchestration
    Config,               # Configuration
    visualize,            # Visualization helpers
    analysis,             # Analysis workflows
)

# Convenience imports (re-exported from subpackages)
from canvodpy import (
    # From canvod-readers
    read_rinex,
    
    # From canvod-aux
    get_ephemerides,
    get_clocks,
    
    # From canvod-grids
    create_hemigrid,
    
    # From canvod-vod
    calculate_vod,
    
    # From canvod-viz
    plot_hemisphere_2d,
    plot_hemisphere_3d,
)
```

**Key Features:**
- Site configuration management
- Pipeline orchestration
- Batch processing
- Progress tracking
- Error handling
- Logging

**Implementation (~800 lines):**
```
canvodpy/src/canvod/
├── __init__.py          # Main imports
├── site.py              # Site class
├── pipeline.py          # Pipeline class
├── config.py            # Configuration
├── processor/
│   ├── orchestrator.py  # Processing orchestration
│   └── batch.py         # Batch operations
├── analysis/
│   ├── timeseries.py
│   └── comparison.py
└── cli.py               # Command-line interface (optional)
```

---

## 🔧 Configuration System

### Site Configuration (~/.canvod/sites.toml)

```toml
# Default site
default_site = "Rosalia"

# Site definitions
[sites.Rosalia]
name = "Rosalia"
location = "Austria"
description = "Rosalia field site for VOD research"

# Receiver configuration
[sites.Rosalia.receivers.canopy_01]
type = "canopy"
directory = "/data/Rosalia/canopy_01/01_GNSS/01_raw"
description = "Canopy receiver 1"
active = true

[sites.Rosalia.receivers.canopy_02]
type = "canopy"
directory = "/data/Rosalia/canopy_02/01_GNSS/01_raw"
active = true

[sites.Rosalia.receivers.reference_01]
type = "reference"
directory = "/data/Rosalia/reference_01/01_GNSS/01_raw"
active = true

[sites.Rosalia.receivers.reference_02]
type = "reference"
directory = "/data/Rosalia/reference_02/01_GNSS/01_raw"
active = true

# VOD analysis pairs
[sites.Rosalia.vod_analyses]
canopy_01_vs_reference_01 = { canopy = "canopy_01", reference = "reference_01" }
canopy_02_vs_reference_02 = { canopy = "canopy_02", reference = "reference_02" }

# Storage paths
[sites.Rosalia.storage]
rinex_store = "/data/Rosalia/stores/rinex_store"
vod_store = "/data/Rosalia/stores/vod_store"

# Processing defaults
[sites.Rosalia.processing]
aux_agency = "COD"
aux_product = "rapid"
n_workers = 12
keep_vars = ["C1C", "L1C", "S1C", "C2W", "L2W", "S2W"]
```

### Global Configuration (~/.canvod/config.toml)

```toml
# Global settings
[global]
log_level = "INFO"
cache_dir = "~/.canvod/cache"
temp_dir = "/tmp/canvod"

# FTP settings for auxiliary data
[aux]
default_agency = "COD"
default_product = "rapid"
ftp_server = "gdc.cddis.eosdis.nasa.gov"
user_email = "your.email@example.com"

# Processing defaults
[processing]
n_workers = 12
enable_parallel = true
chunk_size = 1000

# Visualization defaults
[viz]
default_dpi = 300
default_colormap = "viridis"
```

---

## 🎯 Implementation Priority

### Phase 1: Storage Layer (Week 1)
**Package:** canvod-store  
**Lines:** ~500  
**Status:** CRITICAL - Blocks everything else

Create Icechunk integration:
- IcechunkStore base class
- RINEX-specific store
- VOD-specific store
- Metadata management

### Phase 2: VOD Calculations (Week 1-2)
**Package:** canvod-vod  
**Lines:** ~400  
**Status:** CRITICAL - Core algorithm

Implement VOD algorithms:
- VODCalculator
- Tau-omega models
- Signal processing
- Quality metrics

### Phase 3: Configuration System (Week 2)
**Package:** canvodpy (config module)  
**Lines:** ~200  
**Status:** HIGH - User experience

Create config management:
- TOML-based configuration
- Site definitions
- Settings management
- Environment variable support

### Phase 4: High-Level API (Week 2-3)
**Package:** canvodpy (main API)  
**Lines:** ~600  
**Status:** HIGH - Public interface

Build user-facing API:
- Site class
- Pipeline class
- Convenience functions
- Error handling

### Phase 5: Pipeline Orchestration (Week 3)
**Package:** canvodpy (processor module)  
**Lines:** ~400  
**Status:** MEDIUM - Automation

Implement batch processing:
- Date-based iteration
- Parallel processing
- Progress tracking
- Error recovery

---

## 📊 Estimated Effort

| Component | Lines | Tests | Docs | Total Effort |
|-----------|-------|-------|------|--------------|
| canvod-store | 500 | 300 | 200 | 2-3 days |
| canvod-vod | 400 | 250 | 150 | 2 days |
| Config system | 200 | 100 | 100 | 1 day |
| High-level API | 600 | 350 | 300 | 2-3 days |
| Orchestration | 400 | 200 | 150 | 1-2 days |
| **TOTAL** | **2,100** | **1,200** | **900** | **8-11 days** |

---

## 🎯 Migration Strategy from gnssvodpy

### Approach: Extract & Modernize

1. **Extract core logic** from gnssvodpy
2. **Modernize architecture** (clean dependencies, type hints)
3. **Add comprehensive tests** (pytest, coverage)
4. **Create clean API** (Pythonic, intuitive)
5. **Document thoroughly** (MyST, examples)

### Key Improvements Over gnssvodpy

**gnssvodpy:**
- Monolithic structure
- Mixed concerns
- Limited tests
- Private use only

**canvodpy:**
- ✅ Modular packages
- ✅ Clean separation
- ✅ Comprehensive tests
- ✅ Public-ready API
- ✅ Modern tooling (uv, ruff)
- ✅ Interactive demos (marimo)

---

## 🚀 Next Steps

### Immediate Actions

1. **Create canvod-store package** (2-3 days)
   - Extract from gnssvodpy/icechunk_manager/
   - Modernize Icechunk integration
   - Add comprehensive tests

2. **Create canvod-vod package** (2 days)
   - Extract from gnssvodpy/vod/
   - Clean up algorithms
   - Add quality metrics

3. **Design configuration system** (1 day)
   - TOML-based site definitions
   - Environment variables
   - Validation

4. **Build high-level API** (2-3 days)
   - Site class
   - Pipeline class
   - Convenience functions

5. **Create orchestration layer** (1-2 days)
   - Batch processing
   - Progress tracking
   - Error handling

### Timeline: 8-11 Days Total

---

## 📝 Success Criteria

✅ Users can install: `pip install canvodpy`  
✅ Simple workflow: 5 lines of code to process data  
✅ Clean API: Intuitive, discoverable, documented  
✅ Production-ready: Tests, error handling, logging  
✅ Community-ready: Examples, tutorials, demos  

---

**Status:** Design Complete - Ready for Implementation  
**Next:** Begin with canvod-store package extraction
