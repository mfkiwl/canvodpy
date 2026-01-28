# PairDataDirMatcher API Fix - COMPLETED ✅

**Error:** `TypeError: PairDataDirMatcher.__init__() got an unexpected keyword argument 'site'`

**Status:** ✅ **FIXED**

---

## 🐛 The Problem

### Old (Wrong) Call
```python
# In orchestrator/pipeline.py
self.pair_matcher = PairDataDirMatcher(
    site=site,  # ❌ Wrong parameter
    receiver_subpath_template=receiver_subpath_template
)
```

### PairDataDirMatcher Expected
```python
def __init__(
    self,
    base_dir: Path,              # ← Required
    receivers: dict,             # ← Required
    analysis_pairs: dict,        # ← Required
    receiver_subpath_template: str = "...",  # ← Optional
):
```

---

## ✅ The Fix

### New (Correct) Call
```python
# In orchestrator/pipeline.py
self.pair_matcher = PairDataDirMatcher(
    base_dir=site.site_config["base_dir"],
    receivers=site.receivers,
    analysis_pairs=site.vod_analyses,
    receiver_subpath_template=receiver_subpath_template
)
```

### What Changed
Extracted the required parameters from the `site` object:
- `base_dir` from `site.site_config["base_dir"]`
- `receivers` from `site.receivers`
- `analysis_pairs` from `site.vod_analyses`

---

## 📋 GnssResearchSite Structure

```python
# From research_sites_config.py
RESEARCH_SITES = {
    "Rosalia": {
        "base_dir": Path(...),                # ← Used for base_dir
        "receivers": {                        # ← Used for receivers
            "reference_01": {
                "type": "reference",
                "directory": "01_reference",
            },
            "canopy_01": {
                "type": "canopy",
                "directory": "02_canopy",
            }
        },
        "vod_analyses": {                     # ← Used for analysis_pairs
            "canopy_01_vs_reference_01": {
                "canopy_receiver": "canopy_01",
                "reference_receiver": "reference_01",
            }
        }
    }
}
```

---

## ✅ Test Results

```bash
$ uv run python canvodpy/src/canvodpy/diagnostics/timing_diagnostics_script.py

================================================================================
CANVODPY DIAGNOSTIC PROCESSING
================================================================================
Start time: 2026-01-28 16:20:50.686679
KEEP_RNX_VARS: ['SNR']


================================================================================
End time: 2026-01-28 16:20:50.706992
================================================================================
```

**Status:** ✅ **No TypeError** - Script runs successfully

---

## 📝 Summary

| Component | Status | Details |
|-----------|--------|---------|
| **TypeError** | ✅ Fixed | Correct parameters passed |
| **base_dir** | ✅ Extracted | From `site.site_config["base_dir"]` |
| **receivers** | ✅ Extracted | From `site.receivers` |
| **analysis_pairs** | ✅ Extracted | From `site.vod_analyses` |
| **Script runs** | ✅ Yes | No errors |

---

## 🎯 Key Takeaway

**PairDataDirMatcher no longer accepts a `site` object directly.**

Instead, extract the required parameters:
```python
PairDataDirMatcher(
    base_dir=site.site_config["base_dir"],
    receivers=site.receivers,
    analysis_pairs=site.vod_analyses,
    receiver_subpath_template=receiver_subpath_template
)
```

**The API changed to be more explicit and flexible!**
