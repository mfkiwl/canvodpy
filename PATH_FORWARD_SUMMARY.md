# 🎯 canvodpy: Path Forward - High-Level API

**Date:** 2025-01-21  
**Status:** Design Complete, Ready for Implementation

---

## 🔍 The Core Problem

We've built excellent **low-level components** (readers, aux, grids, viz) totaling ~7,130 lines with comprehensive tests.

But we're **missing the high-level API** that researchers actually need:

```python
# ❌ This doesn't exist yet in canvodpy:
from canvodpy import Site, Pipeline

site = Site("Rosalia")
pipeline = Pipeline(site)
results = pipeline.process_date("2025001")
vod = pipeline.calculate_vod("canopy_01", "reference_01", "2025001")
```

**Why?** Because canvodpy is missing:
1. **Storage layer** (canvod-store) - No data persistence
2. **VOD calculations** (canvod-vod) - No actual VOD algorithm
3. **Site management** (canvodpy) - No configuration system
4. **Pipeline orchestration** (canvodpy) - No workflow automation

---

## 📊 What We Have vs What We Need

### ✅ Foundation (Complete - 75% of codebase)

| Package | Status | Purpose |
|---------|--------|---------|
| canvod-readers | ✅ 2,900 lines | Parse RINEX files |
| canvod-aux | ✅ 2,500 lines | Get ephemeris/clocks |
| canvod-grids | ✅ 360 lines | Hemisphere grids |
| canvod-viz | ✅ 1,370 lines | Visualize results |

**What these do:** Low-level data manipulation

---

### ❌ Missing Public API (25% of codebase - but critical!)

| Package | Priority | Purpose |
|---------|----------|---------|
| **canvod-store** | 🔴 CRITICAL | Store/retrieve data (Icechunk) |
| **canvod-vod** | 🔴 CRITICAL | Calculate VOD from signals |
| **canvodpy (umbrella)** | 🟡 HIGH | User-facing API |

**What these do:** Make everything usable for researchers

---

## 🏗️ The Missing Pieces

### 1. canvod-store (~500 lines)

**Purpose:** Persistent data storage with versioning

```python
from canvod.store import create_rinex_store, create_vod_store

# Store processed RINEX data
rinex_store = create_rinex_store("/path/to/store")
rinex_store.write_group("canopy_01", dataset)

# Store VOD results
vod_store = create_vod_store("/path/to/vod_store")
vod_store.write_group("canopy_01_vs_ref_01", vod_dataset)
```

**Extracted from:** `gnssvodpy/icechunk_manager/`

---

### 2. canvod-vod (~400 lines)

**Purpose:** Calculate vegetation optical depth

```python
from canvod.vod import calculate_vod

# The core algorithm
vod = calculate_vod(
    canopy_signal=canopy_ds,
    reference_signal=reference_ds,
    grid=hemigrid
)
```

**Extracted from:** `gnssvodpy/vod/`

---

### 3. canvodpy - Site Management (~200 lines)

**Purpose:** Manage research sites and configuration

```python
from canvodpy import Site

# Loads from ~/.canvod/sites.toml
site = Site("Rosalia")

# Access receivers
print(site.receivers)  # {'canopy_01': {...}, 'reference_01': {...}}

# Access stores
site.rinex_store  # Icechunk store for RINEX
site.vod_store    # Icechunk store for VOD
```

**Extracted from:** `gnssvodpy/research_sites_config.py`, `gnssvodpy/icechunk_manager/manager.py`

---

### 4. canvodpy - Pipeline (~600 lines)

**Purpose:** Orchestrate processing workflows

```python
from canvodpy import Pipeline

pipeline = Pipeline(site)

# Process single date
results = pipeline.process_date("2025001")
# Returns: {'canopy_01': xr.Dataset, 'reference_01': xr.Dataset, ...}

# Process range
for date_key, datasets in pipeline.process_date_range("2025001", "2025007"):
    print(f"Processed {date_key}")
    
# Calculate VOD
vod = pipeline.calculate_vod(
    canopy='canopy_01',
    reference='reference_01',
    date="2025001"
)
```

**Extracted from:** `gnssvodpy/processor/pipeline_orchestrator.py`

---

## 🎯 The User Experience We're Building

### Simple Case (5 lines)

```python
from canvodpy import Site, Pipeline

site = Site("Rosalia")
pipeline = Pipeline(site)
results = pipeline.process_date("2025001")
vod = pipeline.calculate_vod("canopy_01", "reference_01", "2025001")
```

### Batch Processing

```python
for date_key, datasets in pipeline.process_date_range("2025001", "2025007"):
    # Auto-stored to Icechunk
    print(f"✓ Processed {date_key}")
```

### Custom Configuration

```python
site = Site.from_config({
    'name': 'MySite',
    'receivers': {...},
    'rinex_store': '/path/to/store',
})

pipeline = Pipeline(
    site=site,
    aux_agency='COD',
    keep_vars=['C1C', 'L1C', 'S1C'],
)
```

---

## 📅 Implementation Timeline

### Week 1: Storage & VOD (CRITICAL)

**Days 1-3:** canvod-store
- Extract Icechunk wrapper
- Create RINEX/VOD store classes
- Add metadata management
- Write tests (~500 lines + 300 tests)

**Days 3-5:** canvod-vod
- Extract VOD calculator
- Extract tau-omega model
- Add quality metrics
- Write tests (~400 lines + 250 tests)

### Week 2: Configuration & API (HIGH)

**Days 5-6:** Configuration system
- TOML-based site definitions
- Settings management
- Environment variables
- (~200 lines + 100 tests)

**Days 6-7:** Site management
- Site class
- Store integration
- Receiver management
- (~200 lines + 150 tests)

**Days 7-9:** Pipeline orchestration
- Pipeline class
- Batch processing
- Progress tracking
- (~600 lines + 350 tests)

### Week 3: Integration & Polish

**Days 9-10:** Supporting infrastructure
- Logging system
- Utilities
- Data matching

**Days 10-11:** Integration
- End-to-end testing
- Demo notebooks
- Documentation

---

## 🎯 Success Criteria

After implementation, users should be able to:

✅ Install: `pip install canvodpy`  
✅ Configure: Edit `~/.canvod/sites.toml`  
✅ Process: 5-line script processes data  
✅ Calculate: VOD from RINEX in one call  
✅ Visualize: Publication-ready plots  
✅ Batch: Process weeks/months automatically  
✅ Store: Version-controlled results  

---

## 📊 Why This Matters

**Current state:**
- canvodpy has excellent components
- But no way for users to actually use them
- Can't process real data end-to-end
- Can't calculate actual VOD values

**After implementation:**
- Complete public API
- Production-ready workflows
- Community can use independently
- Ready for publication

---

## 🚀 Next Action

**Start with canvod-store** (most critical):

```bash
cd ~/Developer/GNSS/canvodpy/packages
mkdir -p canvod-store/src/canvod/store
mkdir -p canvod-store/tests

# Copy cookiecutter template structure
cp -r canvod-readers/pyproject.toml canvod-store/
cp -r canvod-readers/Justfile canvod-store/

# Extract from gnssvodpy
# Focus on: MyIcechunkStore, create_*_store functions
```

**Timeline:** 11 days to complete public API  
**Effort:** ~2,350 lines + 1,200 tests + 900 docs  
**Result:** Production-ready canvodpy

---

## 📚 Reference Documents

1. **HIGH_LEVEL_API_DESIGN.md** - Detailed API design
2. **GNSSVODPY_VS_CANVODPY_COMPARISON.md** - Component mapping
3. **CANVODPY_MIGRATION_GUIDE.md** - Original migration plan

---

**Status:** Design Complete ✅  
**Recommendation:** Begin canvod-store implementation immediately  
**This is the last major piece** to make canvodpy production-ready! 🎉
