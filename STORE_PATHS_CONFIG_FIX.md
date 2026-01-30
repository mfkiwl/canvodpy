# Store Paths Fix - Use Configuration System

## Problem

Store paths were hardcoded in `research_sites_config.py` instead of using the `processing.yaml` configuration:

**Before (Hardcoded):**
```python
# research_sites_config.py
RESEARCH_SITES = {
    "Rosalia": {
        "rinex_store_path": _GNSS_ROOT_DIR / "01_Rosalia" / "03_Rinex_Testing",
        "vod_store_path": _GNSS_ROOT_DIR / "01_Rosalia" / "04_VOD_Testing",
        ...
    }
}
```

**Configuration (Ignored):**
```yaml
# config/processing.yaml
storage:
  stores_root_dir: /Volumes/SanDisk/GNSS
  rinex_store_strategy: skip
  vod_store_strategy: overwrite
```

**Result:** Stores were created at hardcoded paths, not at the configured `stores_root_dir`.

---

## Solution

Updated `GnssResearchSite` to load store paths from the configuration system:

### 1. Updated `GnssResearchSite.__init__()`

**File:** `packages/canvod-store/src/canvod/store/manager.py`

```python
def __init__(self, site_name: str) -> None:
    ...
    # Load store paths from processing config (not from research_sites_config)
    from canvod.utils.config import load_config
    config = load_config()
    
    rinex_store_path = config.processing.storage.get_rinex_store_path(site_name)
    vod_store_path = config.processing.storage.get_vod_store_path(site_name)
    
    # Initialize stores using paths from processing.yaml
    self.rinex_store = create_rinex_store(rinex_store_path)
    self.vod_store = create_vod_store(vod_store_path)
    
    self._logger.info(
        f"Initialized GNSS research site: {site_name}",
        rinex_store=str(rinex_store_path),
        vod_store=str(vod_store_path),
    )
```

### 2. Updated `from_rinex_store_path()` classmethod

```python
@classmethod
def from_rinex_store_path(cls, rinex_store_path: Path) -> GnssResearchSite:
    # Load config to get store paths
    from canvod.utils.config import load_config
    config = load_config()
    
    # Try to match against each site's expected rinex store path
    for site_name in RESEARCH_SITES.keys():
        expected_path = config.processing.storage.get_rinex_store_path(site_name)
        if expected_path == rinex_store_path:
            return cls(site_name)
    
    raise ValueError(f"No research site found for RINEX store path: {rinex_store_path}")
```

### 3. Cleaned up `research_sites_config.py`

**File:** `canvodpy/src/canvodpy/research_sites_config.py`

```python
RESEARCH_SITES: dict[str, dict[str, Any]] = {
    "Rosalia": {
        "base_dir": _GNSS_ROOT_DIR / "01_Rosalia",
        # Store paths now come from processing.yaml (storage.stores_root_dir)
        # They are: {stores_root_dir}/{site_name}/rinex/
        #           {stores_root_dir}/{site_name}/vod/
        "receivers": {
            ...
        }
    }
}
```

---

## How It Works Now

### Configuration Flow

**1. Define `stores_root_dir` in `config/processing.yaml`:**
```yaml
storage:
  stores_root_dir: /Volumes/SanDisk/GNSS
```

**2. Configuration model computes paths:**

**File:** `packages/canvod-utils/src/canvod/utils/config/models.py`

```python
class StorageConfig(BaseModel):
    stores_root_dir: Path = Field(...)
    
    def get_rinex_store_path(self, site_name: str) -> Path:
        """Get RINEX store path for a site."""
        return self.stores_root_dir / site_name / "rinex"
    
    def get_vod_store_path(self, site_name: str) -> Path:
        """Get VOD store path for a site."""
        return self.stores_root_dir / site_name / "vod"
```

**3. `GnssResearchSite` uses these paths:**
```python
site = GnssResearchSite("Rosalia")
# Stores created at:
#   /Volumes/SanDisk/GNSS/Rosalia/rinex/
#   /Volumes/SanDisk/GNSS/Rosalia/vod/
```

---

## Path Structure

**Old structure (hardcoded):**
```
$GNSS_ROOT_DIR/
└── 01_Rosalia/
    ├── 03_Rinex_Testing/  ← RINEX store
    └── 04_VOD_Testing/    ← VOD store
```

**New structure (from config):**
```
$stores_root_dir/
└── Rosalia/
    ├── rinex/  ← RINEX store
    └── vod/    ← VOD store
```

**Benefits:**
- ✅ Cleaner paths (no numbered prefixes)
- ✅ Consistent naming
- ✅ Easily configurable
- ✅ Can place stores anywhere

---

## Configuration Example

**Edit `config/processing.yaml`:**

```yaml
storage:
  # All stores will be under this directory
  stores_root_dir: /Volumes/SanDisk/GNSS
  
  # Store strategies
  rinex_store_strategy: skip
  rinex_store_expire_days: 2
  vod_store_strategy: overwrite
```

**Result:**
```
/Volumes/SanDisk/GNSS/
├── Rosalia/
│   ├── rinex/   ← RINEX observations
│   └── vod/     ← VOD products
├── AnotherSite/
│   ├── rinex/
│   └── vod/
└── ...
```

---

## Verification

**Test the new paths:**

```python
from canvod.store import GnssResearchSite
from canvod.utils.config import load_config

# Check configuration
config = load_config()
print(f"Root: {config.processing.storage.stores_root_dir}")
print(f"RINEX: {config.processing.storage.get_rinex_store_path('Rosalia')}")
print(f"VOD: {config.processing.storage.get_vod_store_path('Rosalia')}")

# Create site
site = GnssResearchSite('Rosalia')
print(f"\nActual RINEX: {site.rinex_store.store_path}")
print(f"Actual VOD: {site.vod_store.store_path}")
```

**Output:**
```
Root: /Volumes/SanDisk/GNSS
RINEX: /Volumes/SanDisk/GNSS/Rosalia/rinex
VOD: /Volumes/SanDisk/GNSS/Rosalia/vod

Actual RINEX: /Volumes/SanDisk/GNSS/Rosalia/rinex
Actual VOD: /Volumes/SanDisk/GNSS/Rosalia/vod
```

✅ Paths match configuration!

---

## Migration Guide

If you have existing stores at old paths, you can:

### Option 1: Update Configuration

Point to existing store location:

```yaml
storage:
  stores_root_dir: /Users/work/Developer/GNSS/canvodpy-test-data/valid/01_Rosalia
```

Paths will be:
- RINEX: `.../01_Rosalia/Rosalia/rinex` ⚠️ (nested)

### Option 2: Move Stores

Move existing stores to new structure:

```bash
# Define new root
NEW_ROOT="/Volumes/SanDisk/GNSS"

# Create new structure
mkdir -p "$NEW_ROOT/Rosalia/rinex"
mkdir -p "$NEW_ROOT/Rosalia/vod"

# Move stores
mv /path/to/old/03_Rinex_Testing/* "$NEW_ROOT/Rosalia/rinex/"
mv /path/to/old/04_VOD_Testing/* "$NEW_ROOT/Rosalia/vod/"
```

### Option 3: Start Fresh

The easiest approach - let new data write to new location:

```yaml
storage:
  stores_root_dir: /Volumes/SanDisk/GNSS
```

Old stores remain untouched, new data uses clean structure.

---

## Files Modified

1. **`packages/canvod-store/src/canvod/store/manager.py`**
   - Updated `__init__()` to load paths from config
   - Updated `from_rinex_store_path()` to use config

2. **`canvodpy/src/canvodpy/research_sites_config.py`**
   - Removed hardcoded `rinex_store_path` and `vod_store_path`
   - Added comment explaining paths come from config

---

## Benefits

### ✅ Single Source of Truth
All paths configured in `processing.yaml`, not scattered across files.

### ✅ Easy to Change
Update one line in YAML, affects all code:
```yaml
stores_root_dir: /new/location/  # Done!
```

### ✅ Cleaner Structure
```
stores_root_dir/
└── SiteName/
    ├── rinex/
    └── vod/
```

### ✅ Flexible Deployment
Different deployments can use different `stores_root_dir`:
- Development: Local SSD
- Testing: Test directory
- Production: Network storage

---

## Key Takeaways

1. **Configuration system is authoritative** - Store paths come from `processing.yaml`
2. **`StorageConfig` methods compute paths** - Consistent path generation
3. **`research_sites_config.py` only defines site metadata** - Receivers, analyses, not paths
4. **Easy to configure per environment** - Just edit one YAML file

**Store paths now follow the configuration-driven architecture!** 🎉
