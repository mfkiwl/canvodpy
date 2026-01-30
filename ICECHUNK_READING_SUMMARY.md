# Icechunk Store Reading - Quick Fix Summary

## ✅ **FIXED: NotImplementedError When Reading Store**

---

## The Problem

**Error when reading datasets:**
```python
ds = mystore.read_group(branch='main', group_name='canopy_01')

NotImplementedError: Can not use auto rechunking with object dtype.
We are unable to estimate the size in bytes of object data
```

**Warning (harmless):**
```
UnstableSpecificationWarning: The data type (FixedLengthUTF32) does not have a Zarr V3 specification.
```

---

## The Fix

**File:** `packages/canvod-store/src/canvod/store/store.py`

**Changed line ~387 from:**
```python
chunks = 'auto'  # ❌ Fails with string coordinates
```

**To:**
```python
chunks = ICECHUNK_CHUNK_STRATEGIES.get(self.store_type, {
    "epoch": 34560,  # Chunk time dimension (2 days)
    "sid": -1        # Don't chunk satellites (load all)
})
```

---

## Why It Works

**Before:**
- `chunks='auto'` → dask tries to auto-chunk ALL arrays
- String coordinates (band, code, system, sv) have object dtype
- Dask can't estimate size of object data
- Result: Error! ❌

**After:**
- Explicit chunks for dimensions only: `{"epoch": 34560, "sid": -1}`
- Numeric arrays inherit chunking from dimensions
- String coordinates loaded fully (no chunking)
- Result: Works! ✅

---

## Verification

```python
from canvod.store import GnssResearchSite

site = GnssResearchSite('Rosalia')
ds = site.rinex_store.read_group(branch='main', group_name='canopy_01')

print(f'✅ Shape: {dict(ds.sizes)}')
print(f'✅ Variables: {list(ds.data_vars)}')
```

**Output:**
```
✅ Shape: {'epoch': 2160, 'sid': 321}
✅ Variables: ['r', 'SNR', 'phi', 'theta']
```

---

## About the Warning

**The FixedLengthUTF32 warning is harmless:**
- ⚠️ Zarr V3 string spec is still being finalized
- ✅ Data works correctly
- ⚠️ Format might change in future zarr versions
- ✅ No action needed

**To suppress (optional):**
```python
import warnings
warnings.filterwarnings('ignore', category=UnstableSpecificationWarning)
```

---

## Files Changed

1. `packages/canvod-store/src/canvod/store/store.py` - Fixed chunking

---

## Documentation

- **`ICECHUNK_CHUNKING_FIX.md`** - Complete technical details

---

**Datasets can now be read successfully!** ✅
