# RINEX Validation Error - FIXED ✅

**Error:** `Missing required data variables: {'S', 'D', 'C', 'L'}`

**Status:** ✅ **FIXED**

---

## 🐛 The Problem

### Error Message
```
ValueError: Missing required data variables: {'S', 'D', 'C', 'L'}
```

### Root Cause
**Validation was using wrong default for `keep_rnx_data_vars`**

1. Diagnostic script sets `keep_vars=['SNR']` from `canvodpy.globals.KEEP_RNX_VARS`
2. Processor calls `first_rnx.to_ds(write_global_attrs=True)` **without** passing `keep_vars`
3. `to_ds()` uses default `keep_rnx_data_vars=KEEP_RNX_VARS` from `canvod.readers.gnss_specs.constants`
4. Constants default is `["C", "L", "D", "S"]` (Code, Phase, Doppler, Signal)
5. Validation expects all 4 variables but RINEX only has SNR data
6. **ValueError raised!**

---

## 🔍 The Issue

### Two Different KEEP_RNX_VARS

**1. In `canvodpy/globals.py` (User setting)**
```python
KEEP_RNX_VARS: list[str] = [
    'SNR',
    # 'Pseudorange',
    # 'Phase',
    # 'Doppler',
]
```

**2. In `canvod.readers.gnss_specs.constants.py` (Default)**
```python
KEEP_RNX_VARS: list[str] = [
    "C",  # Code
    "L",  # Phase
    "D",  # Doppler
    "S",  # Signal strength
]
```

### Where `to_ds()` Was Called

| Line | Context | Purpose | Needs Data? |
|------|---------|---------|-------------|
| 116 | `preprocess_with_hermite_aux()` | Process RINEX data | ✅ YES |
| 441 | `_preprocess_aux_data_with_hermite()` | Detect sampling interval | ❌ NO |
| 1357 | Multi-receiver processing | Get receiver position | ❌ NO |
| 1529 | Multi-receiver processing | Get receiver position | ❌ NO |
| 2186 | Multi-receiver processing | Get receiver position | ❌ NO |

---

## ✅ The Fix

### Strategy
- **For data processing:** Pass actual `keep_vars` parameter
- **For metadata only:** Pass empty list `keep_rnx_data_vars=[]`

### Why Empty List Works
```python
# In validate_data_variables():
missing_vars = set([]) - set(self.dataset.data_vars)  # = set()
if missing_vars:  # = if False:
    raise ValueError(...)  # NOT raised ✅
```

Empty list = no required variables = no validation errors!

---

## 📝 Changes Made

**File:** `canvodpy/src/canvodpy/orchestrator/processor.py`

### 1. Line 116 - Pass actual keep_vars
```python
# Before
ds = rnx.to_ds(write_global_attrs=True)

# After
ds = rnx.to_ds(keep_rnx_data_vars=keep_vars, write_global_attrs=True)
```

### 2. Line 441 - Use empty list (metadata only)
```python
# Before
first_ds = first_rnx.to_ds(write_global_attrs=True)

# After
first_ds = first_rnx.to_ds(keep_rnx_data_vars=[], write_global_attrs=True)
```

### 3. Lines 1357 & 2186 - Use empty list (metadata only)
```python
# Before
first_ds = first_rnx.to_ds(write_global_attrs=True)

# After
first_ds = first_rnx.to_ds(keep_rnx_data_vars=[], write_global_attrs=True)
```

### 4. Line 1529 - Use empty list (metadata only)
```python
# Before
first_ds = first_rnx.to_ds(write_global_attrs=True)

# After
first_ds = first_rnx.to_ds(keep_rnx_data_vars=[], write_global_attrs=True)
```

---

## ✅ Test Results

### Before Fix
```
❌ ValueError: Missing required data variables: {'S', 'D', 'C', 'L'}
```

### After Fix
```
✅ 2026-01-28 17:41:06 - Successfully loaded 'ephemerides': {'epoch': 289, 'sid': 3658}
✅ 2026-01-28 17:41:06 - Successfully loaded 'clock': {'epoch': 2880, 'sid': 3658}
✅ Processing starts successfully!
```

---

## 🎯 Key Insights

### 1. Parameter Defaults Can Be Dangerous
When a method has a default parameter that comes from a different module/config, it can cause subtle bugs when different parts of the codebase have different expectations.

### 2. Metadata vs Data Processing
When reading files for metadata only (sampling rate, receiver position), we don't need data variables at all:
- Pass `keep_rnx_data_vars=[]`
- Skip validation
- Faster processing

### 3. Validation Should Match Intent
If you're only using metadata, don't validate data variables. The validation should match what you actually need.

---

## 🚀 Next Error

After fixing validation, new error appeared:
```
CoordinateValidationError: conflicting sizes for dimension 'sid': 
length 3658 on the data but length 205 on coordinate 'sid'
```

**This is a different issue** - dimension mismatch between:
- Auxiliary data (3658 sids - global padded)
- RINEX data (205 sids - actual observations)

---

## 📊 Summary

| Issue | Status |
|-------|--------|
| **Validation error** | ✅ Fixed |
| **Line 116** | ✅ Uses keep_vars |
| **Line 441** | ✅ Uses [] |
| **Line 1357** | ✅ Uses [] |
| **Line 1529** | ✅ Uses [] |
| **Line 2186** | ✅ Uses [] |
| **Aux data loads** | ✅ Working |
| **RINEX reads** | ✅ Working |

---

## 💡 Lesson Learned

**Always pass explicit parameters instead of relying on defaults when:**
1. Defaults come from different modules
2. Different parts of codebase have different configs
3. The intent varies by use case (data vs metadata)

**Solution patterns:**
```python
# For data processing - use actual requirements
ds = rnx.to_ds(keep_rnx_data_vars=keep_vars)

# For metadata only - skip validation
ds = rnx.to_ds(keep_rnx_data_vars=[])
```

---

**The RINEX validation error is completely resolved!** ✅
