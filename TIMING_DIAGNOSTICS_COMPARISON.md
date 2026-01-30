# Timing Diagnostics Script - Comprehensive Comparison

## Overview

Comparing:
- **Original:** `/Users/work/Developer/GNSS/gnssvodpy/src/gnssvodpy/processor/timing_diagnostics_script.py`
- **New:** `/Users/work/Developer/GNSS/canvodpy/canvodpy/src/canvodpy/diagnostics/timing_diagnostics_script.py`

---

## Critical Differences Found

### ❌ 1. TimingLogger Class - MISSING in canvodpy

**Original (gnssvodpy):**
```python
class TimingLogger:
    """CSV logger for timing data with append support."""
    
    def __init__(self, filename=None, expected_receivers=None):
        if filename is None:
            from gnssvodpy.globals import LOG_DIR
            filename = LOG_DIR / "timing_log.csv"
        # ... rest of implementation
    
    def log(self, day, start_time, end_time, receiver_times, total_time):
        """Log a day's processing times."""
        # Writes CSV with timing data
```

**New (canvodpy):**
```python
# MISSING - No TimingLogger class at all!
```

**Impact:** ❌ **Critical** - No CSV logging of timing data for visualization/analysis

---

### ❌ 2. Timing Data Capture - INCOMPLETE in canvodpy

**Original (gnssvodpy):**
```python
for date_key, datasets, receiver_times in orchestrator.process_by_date(...):
    day_start_time = datetime.now()  # ← Capture start
    
    try:
        # ... processing ...
        day_end_time = datetime.now()  # ← Capture end
        
        # LOG TO CSV with actual receiver times
        timing_log.log(
            day=date_key,
            start_time=day_start_time,
            end_time=day_end_time,
            receiver_times=receiver_times,
            total_time=total_time
        )
```

**New (canvodpy):**
```python
for date_key, datasets, receiver_times in orchestrator.process_by_date(...):
    # ❌ No day_start_time capture
    
    try:
        # ... processing ...
        # ❌ No day_end_time capture
        # ❌ No CSV logging at all!
```

**Impact:** ❌ **Critical** - Cannot track timing data over multiple days

---

### ⚠️ 3. RINEX_STORE_STRATEGY Reporting - MISSING in canvodpy

**Original (gnssvodpy):**
```python
from gnssvodpy.globals import KEEP_RNX_VARS, RINEX_STORE_STRATEGY

def diagnose_processing(...):
    print("=" * 80)
    print("TIMING DIAGNOSTIC WITH GENERALIZED PIPELINE")
    print("=" * 80)
    print(f"Start time: {datetime.now()}")
    print(f"RINEX_STORE_STRATEGY: {RINEX_STORE_STRATEGY}")  # ← Reports strategy
```

**New (canvodpy):**
```python
from canvodpy.globals import KEEP_RNX_VARS
# ❌ RINEX_STORE_STRATEGY not imported

def diagnose_processing(...):
    print("=" * 80)
    print("CANVODPY DIAGNOSTIC PROCESSING")
    print("=" * 80)
    print(f"Start time: {datetime.now()}")
    print(f"KEEP_RNX_VARS: {KEEP_RNX_VARS}")
    # ❌ No RINEX_STORE_STRATEGY printed
```

**Impact:** ⚠️ **Minor** - Less diagnostic information, but doesn't affect processing

---

### ⚠️ 4. Expected Receivers Registration - MISSING in canvodpy

**Original (gnssvodpy):**
```python
site = GnssResearchSite(site_name="Rosalia")
# Get all configured receivers
all_receivers = sorted(site.active_receivers.keys())
timing_log = TimingLogger(expected_receivers=all_receivers)  # ← Pre-register
```

**New (canvodpy):**
```python
site = GnssResearchSite(site_name="Rosalia")
orchestrator = PipelineOrchestrator(site=site, dry_run=False)
# ❌ No receiver pre-registration
```

**Impact:** ⚠️ **Minor** - Only relevant for TimingLogger (which is missing)

---

## Similarities (✅ Correct)

### ✅ 1. Main Processing Loop

**Both implementations are identical:**
```python
for date_key, datasets, receiver_times in orchestrator.process_by_date(
        keep_vars=KEEP_RNX_VARS, start_from=start_from, end_at=end_at):
    
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
        
        # Calculate total
        total_time = sum(receiver_times.values())
        
        # Summary
        print(f"\n{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}")
        for receiver_name, ds in datasets.items():
            print(f"{receiver_name}: {dict(ds.sizes)} ({receiver_times[receiver_name]:.2f}s)")
        print(f"Total time: {total_time:.2f}s")
```

✅ **Identical logic** - Processing works the same way

---

### ✅ 2. Error Handling

**Both implementations:**
```python
try:
    # ... processing ...
except Exception as e:
    print(f"\n✗ Failed {date_key}: {e}")
    import traceback
    traceback.print_exc()
```

✅ **Identical** - Same error handling

---

### ✅ 3. Counters and State

**Both implementations:**
```python
counter = 0
garbage_collect = 0
days_since_rechunk = 0

# In loop:
finally:
    counter += 1
    garbage_collect += 1
    # ... rechunk logic (commented out in both) ...
```

✅ **Identical** - Same state management

---

### ✅ 4. Garbage Collection

**Both implementations:**
```python
if garbage_collect % 5 == 0:
    print("\n💤 Pausing for 60s before garbage collection...")
    time.sleep(60)
    print("\n🗑️  Running garbage collection...")
    gc.collect()
    print("✓ Garbage collection done")
```

✅ **Identical** - Same GC strategy

---

### ✅ 5. Commented-Out Rechunking Logic

**Both have rechunking commented out in the same way**

✅ **Identical** - Same structure (though disabled)

---

## Import Comparison

### Original (gnssvodpy)
```python
import csv  # ← Used by TimingLogger
from datetime import datetime
import gc
from pathlib import Path  # ← Used by TimingLogger
import time

from gnssvodpy.globals import KEEP_RNX_VARS, RINEX_STORE_STRATEGY
from gnssvodpy.icechunk_manager.manager import GnssResearchSite
from gnssvodpy.processor.pipeline_orchestrator import PipelineOrchestrator
```

### New (canvodpy)
```python
# ruff: noqa: DTZ005, ERA001, PLC0415, BLE001
import gc
import time
from datetime import datetime

from canvod.store import GnssResearchSite

from canvodpy.globals import KEEP_RNX_VARS  # ← Missing RINEX_STORE_STRATEGY
from canvodpy.orchestrator import PipelineOrchestrator

# ❌ Missing: csv, Path
# ❌ Missing: RINEX_STORE_STRATEGY
```

---

## Function Signature Comparison

### Original (gnssvodpy)
```python
def diagnose_processing(start_from: str | None = None,
                        end_at: str | None = None):
    """Run diagnostic timing with generalized pipeline."""
```

### New (canvodpy)
```python
def diagnose_processing(
    start_from: str | None = None,
    end_at: str | None = None,
) -> None:  # ← Added return type hint
    """Run diagnostic processing with canvodpy pipeline.
    
    This is the analogon to gnssvodpy's timing_diagnostics_script.py.
    Use this to verify that the new implementation produces the same results.
    """
```

✅ **Functionally identical** - Return type hint is an improvement

---

## __main__ Block Comparison

### Original (gnssvodpy)
```python
if __name__ == "__main__":
    # Process everything
    diagnose_processing()

    # Start from a specific date
    # diagnose_processing(start_from="2024183")  #July 1, 2024

    # diagnose_processing(start_from="2025299", end_at="2025300")  #Oct 26, 2025

    # Process a specific range
    # diagnose_processing(start_from="2025278", end_at="2025280")
```

### New (canvodpy)
```python
if __name__ == "__main__":
    # Process everything
    diagnose_processing()

    # Start from a specific date
    # diagnose_processing(start_from="2024183")  # July 1, 2024

    # Process a specific range
    # diagnose_processing(start_from="2025278", end_at="2025280")

    # Process specific test range (Oct 26, 2025)
    # diagnose_processing(start_from="2025299", end_at="2025300")

    # ... additional commented-out code ...
```

✅ **Essentially identical** - Same examples, just formatted differently

---

## Summary of Differences

| Feature | gnssvodpy | canvodpy | Impact |
|---------|-----------|----------|--------|
| **TimingLogger class** | ✅ Full CSV logging | ❌ Missing | **CRITICAL** |
| **day_start_time capture** | ✅ Captured | ❌ Missing | **CRITICAL** |
| **day_end_time capture** | ✅ Captured | ❌ Missing | **CRITICAL** |
| **CSV timing log** | ✅ Written | ❌ Missing | **CRITICAL** |
| **RINEX_STORE_STRATEGY print** | ✅ Printed | ❌ Missing | Minor |
| **Expected receivers** | ✅ Pre-registered | ❌ Missing | Minor |
| **Import csv** | ✅ Imported | ❌ Missing | Minor |
| **Import Path** | ✅ Imported | ❌ Missing | Minor |
| **Core processing logic** | ✅ | ✅ | **IDENTICAL** |
| **Error handling** | ✅ | ✅ | **IDENTICAL** |
| **GC strategy** | ✅ | ✅ | **IDENTICAL** |
| **State management** | ✅ | ✅ | **IDENTICAL** |

---

## Core Processing Logic Analysis

### ✅ Data Flow is IDENTICAL

Both scripts follow the exact same flow:

1. **Initialize**
   ```python
   site = GnssResearchSite(site_name="Rosalia")
   orchestrator = PipelineOrchestrator(site=site, dry_run=False)
   ```

2. **Main Loop**
   ```python
   for date_key, datasets, receiver_times in orchestrator.process_by_date(
           keep_vars=KEEP_RNX_VARS, start_from=start_from, end_at=end_at):
   ```

3. **Process Each Receiver**
   ```python
   for receiver_name, ds in datasets.items():
       print(f"  Dataset shape: {dict(ds.sizes)}")
       print(f"  Processing time: {receiver_times[receiver_name]:.2f}s")
   ```

4. **Calculate Totals**
   ```python
   total_time = sum(receiver_times.values())
   ```

5. **Print Summary**
   ```python
   for receiver_name, ds in datasets.items():
       print(f"{receiver_name}: {dict(ds.sizes)} ({receiver_times[receiver_name]:.2f}s)")
   print(f"Total time: {total_time:.2f}s")
   ```

**Conclusion:** ✅ **Processing logic is identical** - Both will produce the same data processing results

---

## What's Missing in canvodpy

### 1. TimingLogger Class (Critical)

The entire `TimingLogger` class needs to be added:
- CSV file management
- Structured logging with fixed fieldnames
- Append support
- All expected receivers pre-registered

### 2. Timing Capture (Critical)

Need to add:
```python
day_start_time = datetime.now()  # Before processing
# ... processing ...
day_end_time = datetime.now()  # After processing
```

### 3. CSV Logging Call (Critical)

Need to add:
```python
timing_log.log(
    day=date_key,
    start_time=day_start_time,
    end_time=day_end_time,
    receiver_times=receiver_times,
    total_time=total_time
)
```

### 4. RINEX_STORE_STRATEGY (Minor)

Need to import and print:
```python
from canvodpy.globals import RINEX_STORE_STRATEGY
# ... then print it ...
print(f"RINEX_STORE_STRATEGY: {RINEX_STORE_STRATEGY}")
```

---

## Verification: Do They Produce Identical Results?

### ✅ Processing Results: YES

Both scripts:
1. Use identical `PipelineOrchestrator.process_by_date()` method
2. Process same variables (`KEEP_RNX_VARS`)
3. Apply same logic to `datasets` and `receiver_times`
4. Calculate totals identically
5. Handle errors identically

**The actual data processing will produce IDENTICAL results.**

### ❌ Diagnostic Output: NO

The original provides:
- CSV timing logs for analysis
- RINEX_STORE_STRATEGY reporting
- Structured timing data

The new version:
- Only prints to console
- No persistent timing data
- Less diagnostic info

**The diagnostic/logging capabilities are NOT equivalent.**

---

## Recommendation

**To make canvodpy fully equivalent to gnssvodpy, you MUST:**

1. ✅ **Add TimingLogger class** - Copy from gnssvodpy with path adjustments
2. ✅ **Add timing capture** - Add day_start_time and day_end_time
3. ✅ **Add CSV logging** - Call timing_log.log() in the try block
4. ⚠️ **Add RINEX_STORE_STRATEGY reporting** - Import and print (optional but recommended)

**Without these additions:**
- ✅ Processing results will be identical
- ❌ Diagnostic capabilities will be incomplete
- ❌ No persistent timing data for analysis/visualization

---

## Action Items

### Required (Critical)
- [ ] Port `TimingLogger` class to canvodpy
- [ ] Add `day_start_time` and `day_end_time` capture
- [ ] Add `timing_log.log()` call
- [ ] Add necessary imports (`csv`, `Path`)

### Recommended (Minor)
- [ ] Add `RINEX_STORE_STRATEGY` import and print
- [ ] Add `all_receivers = sorted(site.active_receivers.keys())`
- [ ] Update title from "CANVODPY DIAGNOSTIC" to match original

### Once Fixed
- [ ] Verify CSV output matches format
- [ ] Verify timing data is correctly logged
- [ ] Compare CSV files from both versions

---

## Conclusion

**Core Processing:** ✅ **IDENTICAL** - Both produce same results  
**Diagnostic Features:** ❌ **INCOMPLETE** - Missing timing logger

The new canvodpy version correctly implements the processing logic but is missing the diagnostic/logging infrastructure that makes the script useful for timing analysis and performance tracking.
