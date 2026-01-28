# Session Summary - Diagnostic Script Fixes

**Date:** 2026-01-28  
**Duration:** ~45 minutes  
**Status:** ✅ **Major Progress - 2 Critical Errors Fixed**

---

## 🎯 Starting Point

**User ran timing_diagnostics_script.py** and encountered multiple errors preventing execution.

**Initial Error:**
```
TypeError: PairDataDirMatcher.__init__() got an unexpected keyword argument 'site'
```

---

## ✅ Errors Fixed (3 Total)

### 1. PairDataDirMatcher API Error ✅

**Error:** `TypeError: PairDataDirMatcher.__init__() got an unexpected keyword argument 'site'`

**Problem:** Orchestrator was calling `PairDataDirMatcher(site=site, ...)` but the class expected explicit parameters.

**Fix:** Extract parameters from site object:
```python
# Before
PairDataDirMatcher(site=site, receiver_subpath_template=...)

# After
PairDataDirMatcher(
    base_dir=site.site_config["base_dir"],
    receivers=site.receivers,
    analysis_pairs=site.vod_analyses,
    receiver_subpath_template=...
)
```

**File:** `canvodpy/src/canvodpy/orchestrator/pipeline.py` (line 45)

---

### 2. Wikipedia Fetch Error ✅

**Error:** `[Errno 2] No such file or directory: b'<!DOCTYPE html>...Galileo satellites - Wikipedia...'`

**Problem:** GALILEO, BEIDOU, and IRNSS constellation classes were trying to fetch satellite lists from Wikipedia at runtime, which was:
- Failing with HTML errors
- Slow and unreliable
- Network-dependent

**Fix:** Added static satellite lists:
```python
# GALILEO
use_wiki=False,
static_svs=[f"E{x:02d}" for x in range(1, 37)],  # E01-E36

# BEIDOU
use_wiki=False,
static_svs=[f"C{x:02d}" for x in range(1, 64)],  # C01-C63

# IRNSS
use_wiki=False,
static_svs=[f"I{x:02d}" for x in range(1, 15)],  # I01-I14
```

**File:** `packages/canvod-readers/src/canvod/readers/gnss_specs/constellations.py`

**Result:** Auxiliary data now loads successfully!
```
✅ Successfully loaded 'ephemerides': {'epoch': 289, 'sid': 3658}
✅ Successfully loaded 'clock': {'epoch': 2880, 'sid': 3658}
```

---

### 3. RINEX Validation Error ✅

**Error:** `ValueError: Missing required data variables: {'S', 'D', 'C', 'L'}`

**Problem:** `to_ds()` method was using wrong default for `keep_rnx_data_vars`:
- Diagnostic script wants `['SNR']` (from canvodpy.globals)
- Default was `['C', 'L', 'D', 'S']` (from canvod.readers constants)
- Validation failed because RINEX file only has SNR data

**Fix:** Pass explicit `keep_rnx_data_vars` parameter:
- **For data processing:** Pass actual `keep_vars`
- **For metadata only:** Pass empty list `[]`

```python
# Data processing (line 116)
ds = rnx.to_ds(keep_rnx_data_vars=keep_vars, write_global_attrs=True)

# Metadata only (lines 441, 1357, 1529, 2186)
ds = rnx.to_ds(keep_rnx_data_vars=[], write_global_attrs=True)
```

**Files:** `canvodpy/src/canvodpy/orchestrator/processor.py` (5 locations)

---

## 📊 Progress Summary

| Issue | Before | After | Impact |
|-------|--------|-------|--------|
| **API Error** | ❌ Script crashes | ✅ Orchestrator initializes | Critical |
| **Wikipedia Fetch** | ❌ HTML parsing error | ✅ Aux data loads | Critical |
| **Validation Error** | ❌ Missing variables | ✅ RINEX reads | Critical |
| **Processing** | ❌ Doesn't start | ⚠️ Starts but has dimension error | Major |

---

## 🚧 Current Status

**Diagnostic script now:**
1. ✅ Initializes orchestrator correctly
2. ✅ Loads auxiliary data (ephemerides, clock)
3. ✅ Reads RINEX files
4. ✅ Starts processing pipeline
5. ⚠️ **Encounters dimension mismatch error**

---

## 🔄 Next Error to Fix

**Current Error:**
```
CoordinateValidationError: conflicting sizes for dimension 'sid': 
length 3658 on the data but length 205 on coordinate 'sid'
```

**Analysis:**
- **Auxiliary data:** 3658 sids (global padded list with all possible signals)
- **RINEX data:** 205 sids (only observed signals in this file)
- **Problem:** Trying to combine datasets with different sid dimensions

**Location:** 
```python
add_spherical_coords_to_dataset()
  ↓ creates DataArrays with mismatched sid coordinates
```

**This is a design issue:** Need to align sid dimensions before combining datasets.

**Possible solutions:**
1. Pad RINEX data to match aux data (3658 sids)
2. Slice aux data to match RINEX data (205 sids)
3. Use xarray's alignment capabilities

---

## 📝 Documentation Created

1. **PAIRDATADIRMATCHER_API_FIXED.md** (131 lines)
   - API change explanation
   - Before/after code
   - Parameter extraction from site object

2. **WIKIPEDIA_FETCH_ERROR_FIXED.md** (294 lines)
   - Root cause analysis
   - Static vs dynamic satellite lists
   - All constellation fixes

3. **RINEX_VALIDATION_ERROR_FIXED.md** (204 lines)
   - Validation logic explanation
   - Metadata vs data processing patterns
   - All 5 code locations fixed

---

## 🎯 Key Learnings

### 1. API Breaking Changes
When refactoring classes, ensure all call sites are updated. The PairDataDirMatcher API changed from accepting a site object to explicit parameters.

### 2. External Dependencies Are Risky
Wikipedia fetching for satellite lists was:
- Unreliable (network, HTML changes)
- Slow (HTTP requests)
- Unnecessary (satellite lists are relatively static)

**Solution:** Use static lists for scientific software.

### 3. Parameter Defaults Matter
Having multiple `KEEP_RNX_VARS` in different modules created confusion. Always pass explicit parameters when:
- Defaults vary by module/config
- Intent varies by use case
- Validation requirements differ

### 4. Separation of Concerns
Reading files for:
- **Metadata** (sampling rate, position) → No data validation needed
- **Data processing** → Full validation required

---

## 💪 Strengths of Migration

Despite these errors, the migration shows:

1. **Better modularity** - Errors are isolated and fixable
2. **Clear separation** - Aux, readers, store are independent
3. **Type safety** - Pydantic validation catches issues early
4. **Better logging** - Easy to trace where errors occur
5. **Modern patterns** - ABC, static typing, validators

---

## 🚀 Next Steps

1. **Fix dimension mismatch** - Align sid coordinates
2. **Test full pipeline** - Process complete day
3. **Compare with gnssvodpy** - Verify identical results
4. **Performance testing** - Check timing vs old implementation

---

## 📈 Migration Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Package structure** | ✅ Complete | 6 packages + umbrella |
| **Aux data loading** | ✅ Working | Static satellite lists |
| **RINEX reading** | ✅ Working | Validation fixed |
| **Orchestration** | ⚠️ In progress | Dimension mismatch |
| **VOD calculation** | ⏳ Not tested | Waiting for pipeline |
| **Store integration** | ⏳ Not tested | Waiting for pipeline |

---

## ✅ Session Achievements

- **3 critical errors fixed**
- **Pipeline now starts processing**
- **Auxiliary data loads successfully**
- **Clear path forward identified**
- **Comprehensive documentation created**

**The diagnostic script went from "instant crash" to "processing with one remaining error"!** 🎉

---

**Next session should focus on the dimension alignment issue to complete the processing pipeline.**
