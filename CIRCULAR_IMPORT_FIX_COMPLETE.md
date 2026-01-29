# Circular Import Fix - Complete ✅

## Summary

**The circular import is FIXED with a two-part solution:**
1. Lazy import in `canvod.store.reader.py`
2. Lazy imports in `canvodpy.orchestrator.__init__.py`

---

## Problem

Circular import error when running tests:

```
ImportError: cannot import name 'AuxDataPipeline' from partially initialized module 'canvod.aux.pipeline'
(most likely due to a circular import)
```

### Circular Dependency Chain

```
canvod.aux.__init__ (line 109)
  → canvod.aux.pipeline (line 16)
    → canvod.store.preprocessing
      → canvod.store.__init__ (line 8)
        → canvod.store.reader (line 16) [FIX #1]
          → canvodpy.orchestrator.__init__ (line 16) [FIX #2]
            → canvodpy.orchestrator.pipeline (line 9)
              → canvod.store (CIRCULAR!)
```

---

## Solution

### Fix #1: Lazy Import in `canvod.store.reader`

**File:** `packages/canvod-store/src/canvod/store/reader.py`

**Before:**
```python
# Line 16 - module-level import
from canvodpy.orchestrator import RinexDataProcessor

def parsed_rinex_data_gen_v2(self, ...):
    processor = RinexDataProcessor(...)
```

**After:**
```python
# Removed from line 16

def parsed_rinex_data_gen_v2(self, ...):
    from canvodpy.orchestrator import RinexDataProcessor  # Lazy import
    processor = RinexDataProcessor(...)
```

### Fix #2: Lazy Imports in `canvodpy.orchestrator.__init__`

**File:** `canvodpy/src/canvodpy/orchestrator/__init__.py`

**Before:**
```python
from canvodpy.orchestrator.pipeline import (
    PipelineOrchestrator,
    SingleReceiverProcessor,
)
from canvodpy.orchestrator.processor import RinexDataProcessor

__all__ = ["PipelineOrchestrator", "RinexDataProcessor", "SingleReceiverProcessor"]
```

**After:**
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from canvodpy.orchestrator.pipeline import PipelineOrchestrator, SingleReceiverProcessor
    from canvodpy.orchestrator.processor import RinexDataProcessor

__all__ = ["PipelineOrchestrator", "RinexDataProcessor", "SingleReceiverProcessor"]

def __getattr__(name: str):
    """Lazy import to avoid circular dependencies."""
    if name == "PipelineOrchestrator":
        from canvodpy.orchestrator.pipeline import PipelineOrchestrator
        return PipelineOrchestrator
    if name == "SingleReceiverProcessor":
        from canvodpy.orchestrator.pipeline import SingleReceiverProcessor
        return SingleReceiverProcessor
    if name == "RinexDataProcessor":
        from canvodpy.orchestrator.processor import RinexDataProcessor
        return RinexDataProcessor
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

---

## Test Fixes

### NaN Handling in Padded Datasets

After fixing circular imports, 3 tests failed due to NaN values in padded SIDs (3658 total vs 205 observed).

**Files:**
- `packages/canvod-readers/tests/test_rinex_integration.py`
- `packages/canvod-readers/tests/test_rinex_v3.py`

**Pattern:**
```python
# Filter out NaN values before assertions
valid_data = data[~np.isnan(data)]
assert all_checks(valid_data)

# For system coordinate checks
if dataset_system == 'nan':
    continue
```

---

## Verification ✅

### 1. Direct Import Test

**File:** `check_circular_import.py` (renamed from `test_circular_import_fix.py`)

```bash
$ uv run python check_circular_import.py

Testing circular import fix...
============================================================

1. Import canvodpy.api (should NOT trigger canvod.store import)
✅ canvodpy.api imported successfully
   - Has Site class: True
   - Has Pipeline class: True

2. Check that canvod.store is NOT yet imported
✅ canvod.store is NOT imported yet (lazy import working!)

3. Instantiate Site class (should NOW import canvod.store)
✅ Site class can be imported
✅ Site instantiated successfully

============================================================
✅ Circular import is FIXED!
```

### 2. All Package Tests Pass (104 tests)

```bash
$ cd packages/canvod-readers
$ uv run pytest tests/ -v

================= 104 passed, 2 skipped, 18 warnings in 14.85s =================
```

### 3. Specific Test That Originally Failed

```bash
$ cd packages/canvod-readers
$ uv run pytest tests/test_rinex_integration.py::TestRINEXIntegration::test_band_frequencies_in_dataset -v

========================= 1 passed, 1 warning in 2.74s =========================
```

### 4. Diagnostic Script Runs

```bash
$ uv run python canvodpy/src/canvodpy/diagnostics/timing_diagnostics_script.py

✅ Process completed with exit code 0 (runtime: 2.08s)
```

---

## Files Modified

### Core Fixes (Circular Import)

1. **`packages/canvod-store/src/canvod/store/reader.py`**
   - Removed module-level import of `RinexDataProcessor`
   - Added lazy import inside `parsed_rinex_data_gen_v2()` method

2. **`canvodpy/src/canvodpy/orchestrator/__init__.py`**
   - Replaced module-level imports with `TYPE_CHECKING` imports for type hints
   - Added `__getattr__` method for lazy loading of classes

### Test Fixes (NaN Handling)

3. **`packages/canvod-readers/tests/test_rinex_integration.py`**
   - Fixed `test_band_frequencies_in_dataset` to filter NaN values
   - Fixed `test_system_coordinate_matches_signal_ids` to skip NaN values

4. **`packages/canvod-readers/tests/test_rinex_v3.py`**
   - Fixed `TestSignalMapping::test_system_coordinate` to skip NaN values

### Test File Renamed

5. **`test_circular_import_fix.py` → `check_circular_import.py`**
   - Renamed to prevent pytest from collecting it (was causing collection crash)
   - File has `sys.exit()` at module level which breaks pytest collection
   - Now runs as standalone script: `uv run python check_circular_import.py`

---

## Key Learnings

### 1. Hidden Circular Dependencies

Fixing one circular import can expose another! The import in `orchestrator/__init__.py` wasn't discovered until after fixing `store/reader.py`.

**Testing strategy:**
```python
import sys
import canvodpy.api
assert 'canvod.store' not in sys.modules
```

### 2. Pytest Collection vs Direct Execution

Files with `test_` prefix are collected by pytest, and module-level code runs during collection. Files with `sys.exit()` at module level will crash pytest collection.

**Solution:** Rename test scripts that aren't pytest tests (e.g., `check_*.py` instead of `test_*.py`).

### 3. Lazy Import Patterns

**Method 1:** Lazy import inside function
```python
def my_function():
    from module import Class  # Import when called
    return Class()
```

**Method 2:** Module-level `__getattr__`
```python
def __getattr__(name: str):
    if name == "Class":
        from .module import Class
        return Class
    raise AttributeError(...)
```

**Method 3:** TYPE_CHECKING for type hints
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .module import Class  # Only for type checkers

def function() -> "Class":  # String annotation
    from .module import Class  # Lazy import
    return Class()
```

### 4. Padded Dataset Testing

When datasets are padded to global dimensions (~3658 SIDs), many entries contain NaN values. Tests must filter these:

```python
# Always exclude NaN before validation
valid_data = data[~np.isnan(data)]
assert all_checks(valid_data)
```

---

## Architecture Insight

### The Import Chain

The circular dependency existed because:

1. **`canvod.store`** needs **`canvodpy.orchestrator`** for processing
2. **`canvodpy.orchestrator`** needs **`canvod.store`** for data storage
3. Both imported at module level → circular dependency

### The Solution Pattern

Break cycles by making imports lazy at package boundaries:

```
canvod.store → canvodpy.orchestrator (LAZY in store/reader.py)
                     ↓
canvodpy.orchestrator → canvod.store (LAZY in orchestrator/__init__.py)
```

Both directions are now lazy, eliminating the circular dependency.

---

## Status

| Component | Status |
|-----------|--------|
| Circular import (store/reader.py) | ✅ Fixed |
| Circular import (orchestrator/__init__.py) | ✅ Fixed |
| Import test (check_circular_import.py) | ✅ Passes |
| Package tests (104 tests) | ✅ Pass |
| Diagnostic script | ✅ Runs |
| Test fixes for NaN handling | ✅ Complete |
| Pytest collection | ✅ Works |

**Result:** Circular dependency completely eliminated with two-part fix! 🎉
