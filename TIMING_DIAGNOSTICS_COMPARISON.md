# Timing Diagnostics Script - Side-by-Side Comparison

**Purpose:** Verify canvodpy produces identical results to gnssvodpy

---

## File Locations

| Original | New |
|----------|-----|
| `/Users/work/Developer/GNSS/gnssvodpy/src/gnssvodpy/processor/timing_diagnostics_script.py` | `/Users/work/Developer/GNSS/canvodpy/canvodpy/src/canvodpy/diagnostics/timing_diagnostics_script.py` |

---

## Import Mapping

### gnssvodpy (Original)
```python
from gnssvodpy.globals import KEEP_RNX_VARS, RINEX_STORE_STRATEGY
from gnssvodpy.icechunk_manager.manager import GnssResearchSite
from gnssvodpy.processor.pipeline_orchestrator import PipelineOrchestrator
```

### canvodpy (New)
```python
from canvodpy.globals import KEEP_RNX_VARS
from canvod.store import GnssResearchSite
from canvodpy.orchestrator import PipelineOrchestrator
```

### Changes Summary

| Item | Old Path | New Path | Status |
|------|----------|----------|--------|
| `KEEP_RNX_VARS` | `gnssvodpy.globals` | `canvodpy.globals` | ✅ Migrated |
| `RINEX_STORE_STRATEGY` | `gnssvodpy.globals` | *(removed)* | ⚠️ Not in new version |
| `GnssResearchSite` | `gnssvodpy.icechunk_manager.manager` | `canvod.store` | ✅ Migrated |
| `PipelineOrchestrator` | `gnssvodpy.processor.pipeline_orchestrator` | `canvodpy.orchestrator` | ✅ Migrated |

---

## Code Structure Comparison

### Removed in canvodpy Version

1. **TimingLogger class** - Not needed for basic comparison
2. **RINEX_STORE_STRATEGY reference** - Doesn't exist in new architecture
3. **CSV logging** - Simplified for verification
4. **LOG_DIR reference** - Not needed

### Preserved in canvodpy Version

1. ✅ **diagnose_processing() function** - Identical logic
2. ✅ **Processing loop** - Same structure
3. ✅ **Date filtering** - Same start_from/end_at parameters
4. ✅ **Garbage collection** - Same 60s pause + gc.collect() every 5 days
5. ✅ **Rechunking placeholder** - Same commented-out structure
6. ✅ **Exception handling** - Same try/except pattern
7. ✅ **Print statements** - Same diagnostic output format

---

## Line-by-Line Function Comparison

### Function Signature

**Both versions:**
```python
def diagnose_processing(start_from: str | None = None,
                        end_at: str | None = None):
```

**Status:** ✅ Identical

---

### Initialization Block

**gnssvodpy:**
```python
site = GnssResearchSite(site_name="Rosalia")
all_receivers = sorted(site.active_receivers.keys())
timing_log = TimingLogger(expected_receivers=all_receivers)
orchestrator = PipelineOrchestrator(site=site, dry_run=False)
```

**canvodpy:**
```python
site = GnssResearchSite(site_name="Rosalia")
orchestrator = PipelineOrchestrator(site=site, dry_run=False)
```

**Changes:** Removed TimingLogger (not needed for comparison)

---

### Main Processing Loop

**Both versions:**
```python
for date_key, datasets, receiver_times in orchestrator.process_by_date(
        keep_vars=KEEP_RNX_VARS, start_from=start_from, end_at=end_at):
    
    day_start_time = datetime.now()
    
    print(f"\n{'='*80}")
    print(f"Processing {date_key}")
    print(f"{'='*80}\n")
    
    try:
        # Track timing per receiver
        for receiver_name, ds in datasets.items():
            print(f"\n{'─'*80}")
            print(f"{receiver_name.upper()} PROCESSING")
            print(f"{'─'*80}")
            print(f"  Dataset shape: {dict(ds.sizes)}")
            print(f"  Processing time: {receiver_times[receiver_name]:.2f}s")
        
        day_end_time = datetime.now()
        total_time = sum(receiver_times.values())
        
        # Summary
        print(f"\n{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}")
        for receiver_name, ds in datasets.items():
            print(f"{receiver_name}: {dict(ds.sizes)} ({receiver_times[receiver_name]:.2f}s)")
        print(f"Total time: {total_time:.2f}s")
        print(f"\n✓ Successfully processed {date_key}")
```

**Status:** ✅ Identical (only difference: canvodpy doesn't log to CSV)

---

### Garbage Collection

**Both versions:**
```python
if garbage_collect % 5 == 0:
    print(f"\n💤 Pausing for 60s before garbage collection...")
    time.sleep(60)
    print(f"\n🗑️  Running garbage collection...")
    gc.collect()
    print(f"✓ Garbage collection done")
```

**Status:** ✅ Identical

---

## Expected Output Format

### gnssvodpy Output
```
================================================================================
TIMING DIAGNOSTIC WITH GENERALIZED PIPELINE
================================================================================
Start time: 2026-01-25 14:55:00.000000
RINEX_STORE_STRATEGY: single_group
Starting from: 2025001

================================================================================
Processing 2025001
================================================================================

────────────────────────────────────────────────────────────────────────────────
CANOPY_01 PROCESSING
────────────────────────────────────────────────────────────────────────────────
  Dataset shape: {'epoch': 180, 'sid': 205}
  Processing time: 15.23s

────────────────────────────────────────────────────────────────────────────────
REFERENCE_01 PROCESSING
────────────────────────────────────────────────────────────────────────────────
  Dataset shape: {'epoch': 180, 'sid': 205}
  Processing time: 14.87s

================================================================================
SUMMARY
================================================================================
canopy_01: {'epoch': 180, 'sid': 205} (15.23s)
reference_01: {'epoch': 180, 'sid': 205} (14.87s)
Total time: 30.10s

✓ Successfully processed 2025001
📊 Logged timing for 2025001
   File: /path/to/timing_log.csv
```

### canvodpy Output
```
================================================================================
CANVODPY DIAGNOSTIC PROCESSING
================================================================================
Start time: 2026-01-25 14:55:00.000000
KEEP_RNX_VARS: ['SNR']
Starting from: 2025001

================================================================================
Processing 2025001
================================================================================

────────────────────────────────────────────────────────────────────────────────
CANOPY_01 PROCESSING
────────────────────────────────────────────────────────────────────────────────
  Dataset shape: {'epoch': 180, 'sid': 205}
  Processing time: 15.23s

────────────────────────────────────────────────────────────────────────────────
REFERENCE_01 PROCESSING
────────────────────────────────────────────────────────────────────────────────
  Dataset shape: {'epoch': 180, 'sid': 205}
  Processing time: 14.87s

================================================================================
SUMMARY
================================================================================
canopy_01: {'epoch': 180, 'sid': 205} (15.23s)
reference_01: {'epoch': 180, 'sid': 205} (14.87s)
Total time: 30.10s

✓ Successfully processed 2025001
```

### Differences in Output

| Item | gnssvodpy | canvodpy | Match? |
|------|-----------|----------|--------|
| Title | "TIMING DIAGNOSTIC WITH GENERALIZED PIPELINE" | "CANVODPY DIAGNOSTIC PROCESSING" | Different (cosmetic) |
| RINEX_STORE_STRATEGY line | Shows strategy | Not shown | Different (doesn't exist) |
| CSV logging line | Shows "📊 Logged timing" | Not shown | Different (not implemented) |
| Dataset shapes | `{'epoch': 180, 'sid': 205}` | `{'epoch': 180, 'sid': 205}` | ✅ MUST MATCH |
| Processing times | ~15s per receiver | ~15s per receiver | Should be similar |
| Receivers processed | canopy_01, reference_01 | canopy_01, reference_01 | ✅ MUST MATCH |

---

## Running the Scripts

### Run gnssvodpy Version

```bash
cd /Users/work/Developer/GNSS/gnssvodpy

# Run full processing
python src/gnssvodpy/processor/timing_diagnostics_script.py

# Or process specific range
python -c "
from gnssvodpy.processor.timing_diagnostics_script import diagnose_processing
diagnose_processing(start_from='2025001', end_at='2025007')
"
```

### Run canvodpy Version

```bash
cd /Users/work/Developer/GNSS/canvodpy

# Run full processing
uv run python canvodpy/src/canvodpy/diagnostics/timing_diagnostics_script.py

# Or process specific range
uv run python -c "
from canvodpy.diagnostics import diagnose_processing
diagnose_processing(start_from='2025001', end_at='2025007')
"
```

---

## Verification Checklist

### Must Match Exactly

- [ ] **Dataset shapes** - `{'epoch': N, 'sid': M}` must be identical
- [ ] **Receiver names** - Same receivers processed (e.g., canopy_01, reference_01)
- [ ] **Processing dates** - Same dates succeed/fail
- [ ] **Number of receivers** - Same count per day
- [ ] **Error messages** - Fail on same dates with similar errors

### May Differ (Acceptable)

- ⚠️ **Processing times** - Can vary ±10% due to system load
- ⚠️ **Timestamps** - Different run times
- ⚠️ **Title text** - Cosmetic difference
- ⚠️ **CSV logging** - Only gnssvodpy logs to CSV

### Unacceptable Differences

- ✗ **Dataset shapes differ** - Bug in migration
- ✗ **Different receivers** - Bug in migration
- ✗ **Different dates processed** - Bug in migration
- ✗ **Data values differ** - Bug in migration

---

## Debugging Differences

If you find differences in results:

### Step 1: Identify the Difference
```python
# Run both scripts on same date range
# Compare outputs line by line
```

### Step 2: Check Dataset Details
```python
from canvod.store import IcechunkDataReader

# Old data
reader_old = IcechunkDataReader(site_name="Rosalia", store_path="gnssvodpy_store")
ds_old = reader_old.read_receiver(receiver="canopy_01", date="2025001")

# New data
reader_new = IcechunkDataReader(site_name="Rosalia")
ds_new = reader_new.read_receiver(receiver="canopy_01", date="2025001")

# Compare
import xarray as xr
xr.testing.assert_identical(ds_old, ds_new)
```

### Step 3: Check Processing Steps
- Verify YYYYDOY API compatibility (should be 100%)
- Check auxiliary file loading
- Compare RINEX parsing
- Verify coordinate transformations

---

## Quick Test

Run this to test a single day:

```bash
cd /Users/work/Developer/GNSS/canvodpy

uv run python -c "
from canvodpy.diagnostics import diagnose_processing
diagnose_processing(start_from='2025001', end_at='2025001')
"
```

**Expected:** Should complete successfully and show dataset shapes.

---

## Summary

| Aspect | Status |
|--------|--------|
| File created | ✅ `canvodpy/src/canvodpy/diagnostics/timing_diagnostics_script.py` |
| Imports updated | ✅ All imports migrated |
| Core logic preserved | ✅ Processing loop identical |
| API compatibility | ✅ PipelineOrchestrator API unchanged |
| Garbage collection | ✅ Identical logic |
| TimingLogger | ⚠️ Removed (not needed for comparison) |
| CSV logging | ⚠️ Removed (not needed for comparison) |
| Ready for testing | ✅ Yes |

**Next Step:** Run both scripts on same data and compare dataset shapes.
