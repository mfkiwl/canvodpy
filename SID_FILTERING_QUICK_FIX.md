# SID Filtering Fix - Quick Summary

## The Problem - Two Errors

### Error 1: Too Many SIDs in Aux Data
```
CoordinateValidationError: conflicting sizes for dimension 'sid': 
length 321 on the data but length 3658 on coordinate 'sid'
```

### Error 2: Missing SIDs in Aux Data
```
KeyError: "not all values found in index 'sid'"
```

---

## The Root Cause

**Three different SID sets:**

1. **Configured SIDs** (`sids.yaml`): 321 SIDs you want to process
2. **RINEX observations**: Satellites actually observed (~185 SIDs)
3. **Aux data** (ephemeris): Satellites with ephemeris (~315 SIDs)

**The mismatch:**
- Not all observed satellites have ephemeris
- Not all satellites with ephemeris were observed
- Simple selection fails: `aux.sel(sid=rinex.sid)` ❌

---

## The Solution - Inner Join

**File:** `canvodpy/src/canvodpy/orchestrator/processor.py`

```python
# Find satellites in BOTH datasets
rinex_sids = set(ds.sid.values)
aux_sids = set(aux_slice.sid.values)
common_sids = sorted(rinex_sids.intersection(aux_sids))

# Filter BOTH to common SIDs
ds = ds.sel(sid=common_sids)
aux_slice = aux_slice.sel(sid=common_sids)

# Now they match! ✅
```

---

## What This Does

**Example:**
- RINEX has: 185 observed satellites
- Aux has: 315 satellites with ephemeris
- Common: 180 satellites (in BOTH)

**Result:**
- 5 observations dropped (no ephemeris)
- 135 ephemeris entries unused (not observed)
- 180 satellites processed successfully ✅

---

## Log Output

You'll see this in logs:

```
INFO: SID filtering: RINEX had 185, aux had 315, using 180 common
```

This tells you exactly what was filtered.

---

## Why Inner Join?

| Approach | Behavior | Result |
|----------|----------|--------|
| Left join | `aux.sel(sid=rinex.sid)` | ❌ Error if RINEX has SIDs not in aux |
| Right join | `rinex.sel(sid=aux.sid)` | ❌ Error if aux has SIDs not in RINEX |
| **Inner join** | Find intersection first | ✅ Always works! |

---

## Testing

The fix handles all scenarios:

1. ✅ **Perfect overlap** - RINEX=100, aux=100, common=100
2. ✅ **Missing ephemeris** - RINEX=100, aux=95, common=95
3. ✅ **Extra ephemeris** - RINEX=100, aux=300, common=100
4. ✅ **Partial overlap** - RINEX=185, aux=315, common=180

---

## Files Modified

**Single file, ~15 lines added:**

- `canvodpy/src/canvodpy/orchestrator/processor.py`
  - Lines 120-138: Inner join logic with logging

---

## Result

Processing now works correctly regardless of which satellites were observed vs which have ephemeris data! 🎉
