# Icechunk Store Location and Status

## Store Locations

The diagnostic script creates and uses Icechunk stores in the following locations:

### Configuration Source

**File:** `canvodpy/src/canvodpy/research_sites_config.py`

The store paths are configured per research site and come from:
1. Environment variable `GNSS_ROOT_DIR` (set in `.env` file)
2. Site-specific subdirectories

**Current Configuration (from `.env`):**
```bash
GNSS_ROOT_DIR=/Users/work/Developer/GNSS/canvodpy-test-data/valid/
```

### Store Paths

**RINEX Store (Level 1 - Raw Observations):**
```
/Users/work/Developer/GNSS/canvodpy-test-data/valid/01_Rosalia/03_Rinex_Testing
```

**VOD Store (Level 2 - Analysis Products):**
```
/Users/work/Developer/GNSS/canvodpy-test-data/valid/01_Rosalia/04_VOD_Testing
```

---

## Store Structure

### RINEX Store Contents

```
03_Rinex_Testing/
├── config.yaml          # Icechunk configuration
├── chunks/              # Data chunks (130 files)
├── manifests/           # Chunk manifests (136 files)
├── refs/                # Branch references
│   └── heads/           # Branch heads
├── snapshots/           # Version snapshots (15 snapshots)
└── transactions/        # Transaction logs (14 transactions)
```

**Receivers stored:**
- `canopy_01` - Canopy receiver data
- `reference_01` - Reference receiver data

**Data stored:**
- 72 metadata rows per receiver
- Time range: `2025-01-01 00:00:00` to `2025-01-01 02:59:55`
- Dimensions: 
  - `epoch`: 180 time steps
  - `sid`: 3658 satellite identifiers
- Variables: `SNR`, `epoch`, `sid`, `phi`, `theta`, `r`, `band`, `code`, `system`, `sv`, `freq_center`, `freq_min`, `freq_max`

### VOD Store Contents

```
04_VOD_Testing/
├── config.yaml          # Icechunk configuration
├── refs/                # Branch references
│   └── heads/           # Branch heads
└── snapshots/           # Version snapshots (empty - no data yet)
```

**Status:** Empty - VOD analysis has not been run yet

---

## How Stores Are Initialized

### In `timing_diagnostics_script.py`

```python
from canvod.store import GnssResearchSite

# Initialize site - creates/opens both stores
site = GnssResearchSite(site_name="Rosalia")

# Stores are now available:
site.rinex_store  # MyIcechunkStore instance
site.vod_store    # MyIcechunkStore instance
```

### In `GnssResearchSite.__init__()`

**File:** `packages/canvod-store/src/canvod/store/manager.py`

```python
def __init__(self, site_name: str) -> None:
    self.site_config = RESEARCH_SITES[site_name]
    
    # Initialize stores from config paths
    self.rinex_store = create_rinex_store(
        self.site_config["rinex_store_path"]
    )
    self.vod_store = create_vod_store(
        self.site_config["vod_store_path"]
    )
```

### Store Creation Functions

**File:** `packages/canvod-store/src/canvod/store/store.py`

```python
def create_rinex_store(storage_path: Path) -> MyIcechunkStore:
    """Create RINEX Icechunk store."""
    return MyIcechunkStore(
        store_path=storage_path,
        store_type="rinex_store",
        compression_level=5,
        compression_algorithm="zstd",
    )

def create_vod_store(storage_path: Path) -> MyIcechunkStore:
    """Create VOD Icechunk store."""
    return MyIcechunkStore(
        store_path=storage_path,
        store_type="vod_store",
        compression_level=5,
        compression_algorithm="zstd",
    )
```

---

## Store Architecture

### Two-Level Storage System

**Level 1: RINEX Store**
- Stores raw/standardized GNSS observations
- One group per receiver (e.g., `canopy_01`, `reference_01`)
- Each group contains:
  - Time series data arrays
  - Metadata table with file tracking
  - Satellite identifiers (SIDs)
  - Observation variables (SNR, phase, etc.)

**Level 2: VOD Store**
- Stores VOD analysis products
- One group per receiver pair (e.g., `canopy_01_vs_reference_01`)
- Each group contains:
  - VOD time series
  - Quality metrics
  - Analysis metadata

### Icechunk Features

**Versioning:**
- Each write creates a new snapshot
- Snapshots are immutable versions
- Can read from any past snapshot
- Enables time-travel debugging

**Metadata Tracking:**
- Each receiver group has a `metadata/table`
- Tracks ingested RINEX files:
  - File hash
  - Time range (start/end)
  - Snapshot ID
  - Action (insert/append/overwrite/skip)
  - Write strategy
  - Dataset attributes

**Storage Strategy:**
- Compression: zstd level 5
- Chunking:
  - `epoch`: 34560 (two days of 5s data)
  - `sid`: -1 (no chunking along satellite dimension)
- Inline threshold: 512 bytes

---

## Checking Store Status

### Command Line

```bash
# List store contents
ls -lh /Users/work/Developer/GNSS/canvodpy-test-data/valid/01_Rosalia/03_Rinex_Testing/

# Count snapshots (versions)
ls /Users/work/Developer/GNSS/canvodpy-test-data/valid/01_Rosalia/03_Rinex_Testing/snapshots/ | wc -l

# Check store size
du -sh /Users/work/Developer/GNSS/canvodpy-test-data/valid/01_Rosalia/03_Rinex_Testing/
```

### Python

```python
from canvod.store import GnssResearchSite
import zarr

site = GnssResearchSite('Rosalia')

# Open RINEX store
with site.rinex_store.readonly_session('main') as session:
    zroot = zarr.open_group(session.store, mode='r')
    
    # List receivers
    print(f"Receivers: {list(zroot.keys())}")
    
    # Check canopy_01 data
    canopy = zroot['canopy_01']
    print(f"Arrays: {list(canopy.keys())}")
    print(f"SNR shape: {canopy['SNR'].shape}")
    print(f"Epoch range: {canopy['epoch'][:].min()} to {canopy['epoch'][:].max()}")
```

---

## Current Store Status

### RINEX Store ✅ Active

**Receivers:**
- ✅ canopy_01 (72 files ingested)
- ✅ reference_01 (72 files ingested)

**Data Range:**
- Start: 2025-01-01 00:00:00
- End: 2025-01-01 02:59:55
- Duration: ~3 hours

**Dimensions:**
- Time steps: 180
- Satellites: 3658

**Versions:**
- Snapshots: 15
- Transactions: 14
- Chunks: 130
- Manifests: 136

### VOD Store ⚠️ Empty

**Status:** Initialized but no data written yet

**Why:** The diagnostic script only processes RINEX data (Level 1). VOD analysis (Level 2) would be a separate step.

---

## Changing Store Location

To use a different location for stores:

### Option 1: Edit `.env` file

```bash
# Edit .env
GNSS_ROOT_DIR=/path/to/your/data/directory/
```

The stores will be created at:
- RINEX: `/path/to/your/data/directory/01_Rosalia/03_Rinex_Testing`
- VOD: `/path/to/your/data/directory/01_Rosalia/04_VOD_Testing`

### Option 2: Edit `research_sites_config.py`

```python
RESEARCH_SITES: dict[str, dict[str, Any]] = {
    "Rosalia": {
        "rinex_store_path": Path("/custom/path/to/rinex_store"),
        "vod_store_path": Path("/custom/path/to/vod_store"),
        ...
    }
}
```

---

## Store Management

### View Store Info

```python
from canvod.store import GnssResearchSite

site = GnssResearchSite('Rosalia')

# RINEX store info
print(f"RINEX store: {site.rinex_store.store_path}")
print(f"Type: {site.rinex_store.store_type}")

# VOD store info
print(f"VOD store: {site.vod_store.store_path}")
print(f"Type: {site.vod_store.store_type}")
```

### Check Metadata

```python
# Load metadata for a receiver
with site.rinex_store.readonly_session('main') as session:
    import polars as pl
    df = site.rinex_store.load_metadata(session.store, 'canopy_01')
    print(df)
```

### List Snapshots

```bash
ls -lt /Users/work/Developer/GNSS/canvodpy-test-data/valid/01_Rosalia/03_Rinex_Testing/snapshots/
```

---

## Key Takeaways

1. **Stores are created automatically** when `GnssResearchSite` is initialized
2. **Location is configurable** via `.env` or `research_sites_config.py`
3. **RINEX store is actively used** by the diagnostic script
4. **VOD store is initialized** but empty (VOD analysis not yet run)
5. **Data is versioned** with Icechunk snapshots
6. **Metadata tracks** all ingested files

The diagnostic script successfully creates and populates the RINEX store with processed GNSS observations! 🎉
