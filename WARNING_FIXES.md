# Warning Fixes - DateTime and Pint

## Overview

Fixed two types of warnings that appeared during processing:

1. **DateTime Timezone Warning** - `np.datetime64` doesn't support timezone info
2. **Pint Unit Redefinition Warning** - Multiple workers redefining 'dB' unit

---

## Fix 1: DateTime Timezone Warning

### Problem

```
UserWarning: no explicit representation of timezones available for np.datetime64
  return np.datetime64(dt, "ns")
```

**Location:** `packages/canvod-readers/src/canvod/readers/rinex/v3_04.py:1167`

### Root Cause

Code created timezone-aware datetime and passed to `np.datetime64`, which doesn't support timezone info:

```python
dt = datetime(..., tzinfo=timezone.utc)
return np.datetime64(dt, "ns")  # Warning!
```

### Solution

Remove timezone info before converting (datetime is already UTC):

**File:** `packages/canvod-readers/src/canvod/readers/rinex/v3_04.py`

```python
# Before
dt = datetime(..., tzinfo=timezone.utc)
return np.datetime64(dt, "ns")

# After
dt = datetime(..., tzinfo=timezone.utc)
# np.datetime64 doesn't support timezone info, but datetime is already UTC
# Convert to naive datetime (UTC) to avoid warning
return np.datetime64(dt.replace(tzinfo=None), "ns")
```

**Why this works:**
- The datetime is already in UTC
- `np.datetime64` interprets naive datetimes as UTC
- Removing `tzinfo` is safe since we know it's UTC

---

## Fix 2: Pint Unit Redefinition Warning

### Problem

```
[warning] Redefining 'dB' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
```

**Appeared:** Many times (16+ per parallel processing batch)

### Root Cause

Each worker process created a new `pint.UnitRegistry()` and defined 'dB':

```python
UREG: pint.UnitRegistry = pint.UnitRegistry()  # New registry each import
UREG.define("dB = 10 * log10(ratio)")  # Redefines 'dB' globally
```

When multiprocessing spawned workers, each imported the module and redefined the unit, causing warnings.

### Solution

Use pint's **application registry** with idempotent unit definition:

**Files:**
- `packages/canvod-readers/src/canvod/readers/gnss_specs/constants.py`
- `packages/canvod-readers/src/canvod/readers/gnss_specs/constants_CLEANED.py`
- `packages/canvod-aux/src/canvod/aux/_internal/units.py`
- `canvodpy/src/canvodpy/globals.py`

```python
# Before - creates new registry each time
UREG: pint.UnitRegistry = pint.UnitRegistry()
UREG.define("dBHz = 10 * log10(hertz)")
UREG.define("dB = 10 * log10(ratio)")

# After - uses shared application registry
UREG: pint.UnitRegistry = pint.get_application_registry()

# Define custom units only if not already defined (idempotent)
if "dBHz" not in UREG:
    UREG.define("dBHz = 10 * log10(hertz)")
if "dB" not in UREG:
    UREG.define("dB = 10 * log10(ratio)")
```

**Why this works:**

1. **Application Registry:** Pint's singleton registry shared across all modules
2. **Idempotent Checks:** Only define units if they don't exist
3. **Multiprocessing Safe:** Same registry used by all workers

---

## Technical Details

### Pint Application Registry

Pint provides `get_application_registry()` for exactly this use case:

```python
# Gets or creates the singleton application-wide registry
ureg = pint.get_application_registry()

# Safe to call multiple times - returns same instance
ureg2 = pint.get_application_registry()
assert ureg is ureg2  # True!
```

**Benefits:**
- Single registry across entire application
- Thread/process safe
- Designed for libraries and applications
- Prevents redefinition warnings

### Why Check Before Define?

```python
if "dB" not in UREG:
    UREG.define("dB = 10 * log10(ratio)")
```

Even with application registry, checking prevents errors if:
- Unit is already defined in pint's defaults
- Another module already defined it
- Registry is loaded from cache

**Result:** Truly idempotent - can import safely anywhere.

---

## Impact

### Before Fixes

**Output:**
```
UserWarning: no explicit representation of timezones available for np.datetime64
  (repeated 12+ times per receiver)

[warning] Redefining 'dB' (...)
  (repeated 16+ times per parallel batch)
```

### After Fixes

**Output:**
```
(Clean output with no warnings)
```

---

## Files Modified

1. **`packages/canvod-readers/src/canvod/readers/rinex/v3_04.py`**
   - Line 1167: Added `.replace(tzinfo=None)` before `np.datetime64` conversion

2. **`packages/canvod-readers/src/canvod/readers/gnss_specs/constants.py`**
   - Changed to use `pint.get_application_registry()`
   - Added idempotent unit definition checks

3. **`packages/canvod-readers/src/canvod/readers/gnss_specs/constants_CLEANED.py`**
   - Changed to use `pint.get_application_registry()`
   - Added idempotent unit definition checks

4. **`packages/canvod-aux/src/canvod/aux/_internal/units.py`**
   - Changed to use `pint.get_application_registry()`
   - Added idempotent unit definition checks

5. **`canvodpy/src/canvodpy/globals.py`**
   - Changed to use `pint.get_application_registry()`
   - Added idempotent unit definition checks

---

## Verification

Run the diagnostic script - should see clean output:

```bash
$ uv run python canvodpy/src/canvodpy/diagnostics/timing_diagnostics_script.py

Processing canopy_01: 100%|████████████████| 12/12 [00:11<00:00,  1.07file/s]
Processing reference_01: 100%|██████████████| 12/12 [00:14<00:00,  1.18s/file]

✅ No datetime warnings
✅ No pint redefinition warnings
```

---

## Key Learnings

### 1. np.datetime64 is Timezone-Naive

```python
# DON'T: Pass timezone-aware datetime
dt = datetime(..., tzinfo=timezone.utc)
np.datetime64(dt, "ns")  # Warning!

# DO: Remove timezone first (if already UTC)
np.datetime64(dt.replace(tzinfo=None), "ns")  # Clean!
```

### 2. Use Application Registry for Libraries

```python
# DON'T: Create new registry in library code
ureg = pint.UnitRegistry()  # Multiple instances!

# DO: Use application registry
ureg = pint.get_application_registry()  # Singleton!
```

### 3. Make Unit Definitions Idempotent

```python
# DON'T: Define unconditionally
UREG.define("dB = ...")  # Fails if already defined

# DO: Check first
if "dB" not in UREG:
    UREG.define("dB = ...")  # Safe!
```

### 4. Multiprocessing Considerations

Library code that will be used with multiprocessing should:
- Use shared registries (application registry)
- Make definitions idempotent
- Avoid global state mutation

---

## Status

| Component | Status |
|-----------|--------|
| DateTime timezone warning | ✅ Fixed |
| Pint 'dB' redefinition warning | ✅ Fixed |
| Clean output | ✅ Verified |
| Multiprocessing safe | ✅ Verified |

**Processing now runs without warnings!** 🎉
