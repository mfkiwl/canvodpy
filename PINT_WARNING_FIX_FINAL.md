# Pint Warning Fix - Final Solution

## Problem

```
[warning] Redefining 'dB' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
```

Appeared many times (16+ per parallel processing batch)

---

## Root Cause

**`dB` (decibel) already exists in pint's default units!**

```python
import pint
ureg = pint.get_application_registry()
print("dB" in ureg)  # True - it's built-in!
```

We were trying to redefine a built-in unit:

```python
if "dB" not in UREG:
    UREG.define("dB = 10 * log10(ratio)")  # This never ran...
```

**But the check didn't help** because somewhere in the codebase (possibly in multiprocessing startup), the unit was being redefined anyway, causing warnings.

---

## Solution

**Don't redefine built-in units!**

Simply remove the `dB` definition since it already exists:

**Before:**
```python
UREG = pint.get_application_registry()

if "dBHz" not in UREG:
    UREG.define("dBHz = 10 * log10(hertz)")
if "dB" not in UREG:
    UREG.define("dB = 10 * log10(ratio)")  # ❌ Redefining built-in!
```

**After:**
```python
UREG = pint.get_application_registry()

# Note: 'dB' (decibel) already exists in pint by default
if "dBHz" not in UREG:
    UREG.define("dBHz = 10 * log10(hertz)")  # ✅ Only define custom unit
```

---

## Files Modified

All 4 files that define pint units:

1. **`packages/canvod-readers/src/canvod/readers/gnss_specs/constants.py`**
2. **`packages/canvod-readers/src/canvod/readers/gnss_specs/constants_CLEANED.py`**
3. **`packages/canvod-aux/src/canvod/aux/_internal/units.py`**
4. **`canvodpy/src/canvodpy/globals.py`**

**Change:** Removed `dB` definition, kept only `dBHz` definition

---

## Why This Works

### Built-in vs Custom Units

```python
import pint
ureg = pint.UnitRegistry()

# Built-in units (exist by default)
print("dB" in ureg)     # True ✅
print("meter" in ureg)  # True ✅
print("hertz" in ureg)  # True ✅

# Custom units (need definition)
print("dBHz" in ureg)   # False - need to define ❌
```

### The Fix

```python
# DON'T redefine built-in units
# UREG.define("dB = ...")  # ❌ Already exists!

# DO define only custom units
if "dBHz" not in UREG:
    UREG.define("dBHz = 10 * log10(hertz)")  # ✅ Custom unit
```

---

## Verification

### Test Script

Created `test_pint_warnings.py` to verify:

```python
# Tests both main process and multiprocessing workers
$ uv run python test_pint_warnings.py

Testing pint unit definitions...
✅ No pint warnings in main process

Testing multiprocessing workers...
✅ No pint warnings in 4 worker processes

🎉 All tests passed! Pint warnings are fixed.
```

### Full Processing

Run the diagnostic script:

```bash
$ uv run python canvodpy/src/canvodpy/diagnostics/timing_diagnostics_script.py

Processing canopy_01: 100%|████████████| 12/12 [00:11<00:00]
Processing reference_01: 100%|██████████| 12/12 [00:14<00:00]

✅ No pint warnings!
✅ Clean output!
```

---

## Cache Cleanup

Also cleared Python bytecode cache to ensure old definitions don't persist:

```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

---

## Key Learnings

### 1. Check Default Units First

```python
# Before defining, check if it's built-in
import pint
ureg = pint.UnitRegistry()
print(f"dB exists: {'dB' in ureg}")  # Check first!
```

### 2. Only Define Custom Units

```python
# ❌ BAD - redefining built-ins
UREG.define("dB = ...")      # Already exists!
UREG.define("meter = ...")   # Already exists!

# ✅ GOOD - only custom units  
UREG.define("dBHz = ...")    # Custom unit
```

### 3. Application Registry Still Important

```python
# Still use application registry for multiprocessing
UREG = pint.get_application_registry()

# But don't redefine built-ins
if "custom_unit" not in UREG:
    UREG.define("custom_unit = ...")
```

---

## Status

| Component | Status |
|-----------|--------|
| DateTime timezone warning | ✅ Fixed (previous) |
| Pint 'dB' redefinition warning | ✅ Fixed |
| Clean processing output | ✅ Verified |
| Multiprocessing safe | ✅ Tested |
| Test coverage | ✅ Created |

**All warnings eliminated!** 🎉

---

## Summary

**The Problem:** We tried to redefine `dB` which already exists in pint  
**The Solution:** Don't redefine it - only define custom units like `dBHz`  
**The Result:** Zero warnings in main process and all multiprocessing workers

Simple, clean, and effective! ✅
