# Migration Guide: timing_diagnostics_script.py

**Old Location:** `/Users/work/Developer/GNSS/gnssvodpy/src/gnssvodpy/processor/timing_diagnostics_script.py`  
**New Location:** `/Users/work/Developer/GNSS/canvodpy/canvodpy/src/canvodpy/diagnostics/timing_diagnostics.py`

---

## Import Changes

### Old (gnssvodpy)
```python
from gnssvodpy.globals import KEEP_RNX_VARS, RINEX_STORE_STRATEGY
from gnssvodpy.icechunk_manager.manager import GnssResearchSite
from gnssvodpy.processor.pipeline_orchestrator import PipelineOrchestrator
```

### New (canvodpy)
```python
from canvodpy.globals import KEEP_RNX_VARS
from canvod.store import GnssResearchSite
from canvodpy.orchestrator import PipelineOrchestrator
```

### Changes Summary
| Old Import | New Import | Notes |
|------------|------------|-------|
| `gnssvodpy.globals.KEEP_RNX_VARS` | `canvodpy.globals.KEEP_RNX_VARS` | ✅ Same |
| `gnssvodpy.globals.RINEX_STORE_STRATEGY` | *(removed)* | Not in new version |
| `gnssvodpy.icechunk_manager.manager.GnssResearchSite` | `canvod.store.GnssResearchSite` | ✅ Migrated |
| `gnssvodpy.processor.pipeline_orchestrator.PipelineOrchestrator` | `canvodpy.orchestrator.PipelineOrchestrator` | ✅ Migrated |

---

## Code Changes

### TimingLogger Class

**Status:** Removed in analogon (user doesn't need timing/logging for comparison)

**If you need it:**
```python
# Copy the TimingLogger class from the old script
# Change: from gnssvodpy.globals import LOG_DIR
# To:     from pathlib import Path
#         LOG_DIR = Path("logs")  # Or configure as needed
```

### Main Function: diagnose_processing()

**Core logic preserved:** ✅ Same processing flow

**Changes:**
1. **Removed:** `RINEX_STORE_STRATEGY` print (doesn't exist in new version)
2. **Removed:** TimingLogger instantiation and logging calls
3. **Simplified:** Comments and structure (logic identical)

---

## Running the Scripts

### Old Script (gnssvodpy)
```bash
cd /Users/work/Developer/GNSS/gnssvodpy

# Activate gnssvodpy environment
conda activate gnssvodpy  # or your env name

# Run
python src/gnssvodpy/processor/timing_diagnostics_script.py
```

### New Script (canvodpy)
```bash
cd /Users/work/Developer/GNSS/canvodpy

# Run with uv
uv run python canvodpy/src/canvodpy/diagnostics/timing_diagnostics.py

# Or activate environment first
source .venv/bin/activate  # or conda activate canvodpy
python canvodpy/src/canvodpy/diagnostics/timing_diagnostics.py
```

---

## Comparing Results

### What to Compare

**1. Dataset Shapes**
```python
# Old output
canopy_01: {'epoch': 180, 'sid': 205}

# New output (should be IDENTICAL)
canopy_01: {'epoch': 180, 'sid': 205}
```

**2. Processing Success**
```python
# Both should process the same dates
✓ Successfully processed 2025001
✓ Successfully processed 2025002
# ...
```

**3. Data Content**
```python
# Extract datasets and compare
from canvod.store import IcechunkDataReader

reader = IcechunkDataReader(site_name="Rosalia")
ds_old = ...  # From gnssvodpy run
ds_new = ...  # From canvodpy run

# Compare
xr.testing.assert_identical(ds_old, ds_new)
```

### Expected Differences

**None!** The new implementation should produce **identical results**.

If you find differences:
- ✗ Dataset shapes differ → Bug in migration
- ✗ Processing fails on different dates → Bug in migration
- ✗ Data values differ → Bug in migration

---

## Usage Examples

### Process Everything
```python
from canvodpy.diagnostics.timing_diagnostics import diagnose_processing

diagnose_processing()
```

### Process Specific Date Range
```python
# Single day
diagnose_processing(start_from="2025001", end_at="2025001")

# One week
diagnose_processing(start_from="2025001", end_at="2025007")

# Start from specific date
diagnose_processing(start_from="2024183")  # July 1, 2024
```

---

## API Compatibility

### PipelineOrchestrator

**Old API:**
```python
orchestrator = PipelineOrchestrator(site=site, dry_run=False)

for date_key, datasets, receiver_times in orchestrator.process_by_date(
        keep_vars=KEEP_RNX_VARS, start_from=start_from, end_at=end_at):
    # Process datasets
    pass
```

**New API:**
```python
orchestrator = PipelineOrchestrator(site=site, dry_run=False)

for date_key, datasets, receiver_times in orchestrator.process_by_date(
        keep_vars=KEEP_RNX_VARS, start_from=start_from, end_at=end_at):
    # Process datasets
    pass
```

**Status:** ✅ **IDENTICAL** - No API changes required!

---

## Verification Checklist

Use this checklist to verify the migration:

- [ ] **Run old script** - Record outputs
- [ ] **Run new script** - Record outputs
- [ ] **Compare dataset shapes** - Should be identical
- [ ] **Compare processing dates** - Should process same dates
- [ ] **Compare data values** - Should be identical
- [ ] **Check error handling** - Should fail on same dates
- [ ] **Verify performance** - Should be comparable (±10%)

---

## Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'canvod.store'`

**Solution:**
```bash
cd /Users/work/Developer/GNSS/canvodpy
uv sync  # Ensure all packages installed
```

### Different Results

**Problem:** Datasets have different shapes or values

**Diagnosis:**
1. Check which step produces different results
2. Compare intermediate outputs
3. Verify YYYYDOY API compatibility (should be 100%)
4. Check auxiliary file loading

**Common Causes:**
- Missing import updates
- YYYYDOY API incompatibility (should be fixed)
- Configuration differences

### Missing Variables

**Problem:** `RINEX_STORE_STRATEGY` not found

**Solution:** This variable doesn't exist in canvodpy. Remove references to it.

---

## Removed Features

### From Old Script

**1. RINEX_STORE_STRATEGY**
- Not used in new architecture
- Remove references

**2. TimingLogger (optional)**
- Removed from analogon for simplicity
- Copy from old script if needed

**3. Rechunking Logic (commented out)**
- Already commented in old script
- Not included in analogon
- Add back if needed

---

## File Structure

```
gnssvodpy/                                    canvodpy/
└── src/gnssvodpy/processor/                 └── src/canvodpy/diagnostics/
    └── timing_diagnostics_script.py             └── timing_diagnostics.py
```

---

## Next Steps

### 1. Test the New Script
```bash
cd /Users/work/Developer/GNSS/canvodpy
uv run python canvodpy/src/canvodpy/diagnostics/timing_diagnostics.py
```

### 2. Compare with Old Script
```bash
# Run old script
cd /Users/work/Developer/GNSS/gnssvodpy
python src/gnssvodpy/processor/timing_diagnostics_script.py

# Compare outputs manually
```

### 3. Verify Identical Results
- Dataset shapes should match
- Processing should succeed on same dates
- Data values should be identical

### 4. Report Issues
If you find discrepancies:
1. Note which dates/receivers differ
2. Compare intermediate outputs
3. Check import migration was complete
4. Verify API compatibility

---

## Summary

| Aspect | Status |
|--------|--------|
| Import migration | ✅ Complete |
| Core logic preserved | ✅ Identical |
| API compatibility | ✅ 100% |
| TimingLogger | ⚠️ Removed (optional) |
| Ready for testing | ✅ Yes |

**File:** `canvodpy/src/canvodpy/diagnostics/timing_diagnostics.py`  
**Purpose:** Verify canvodpy produces identical results to gnssvodpy  
**Usage:** Run and compare outputs with old script
