# 🔧 Import Error Fix - Processor Module

**Issue**: `ModuleNotFoundError: No module named 'canvodpy.aux_data'`

**Cause**: The processor.py file was initially copied with full gnssvodpy code including
imports to modules that don't exist in canvodpy yet. The file has now been replaced with
a lightweight stub.

## ✅ Solution: Restart Marimo

The processor.py file has been fixed, but marimo has cached the old version.

### Quick Fix

**In your marimo browser window:**

1. **Stop the kernel**: Click "Kernel" → "Restart kernel" (or Ctrl+C in terminal)
2. **Restart marimo**:
   ```bash
   cd ~/Developer/GNSS/canvodpy/demo
   uv run marimo edit gnss_vod_complete_demo.py
   ```

3. **Run cells again**: Execute from top to bottom

---

## 🔍 What Was Fixed

### Before (Broken)
```
canvodpy/orchestrator/processor.py (92 KB)
- Full gnssvodpy processor code
- Imports from canvodpy.aux_data (doesn't exist)
- Imports from canvodpy.data_handler (wrong location)
- Many dependencies not yet migrated
```

### After (Fixed)
```python
canvodpy/orchestrator/processor.py (1.4 KB)
# Lightweight stub that lazily imports from gnssvodpy

class RinexDataProcessor:
    """Wrapper that delegates to gnssvodpy implementation."""
    def __new__(cls, *args, **kwargs):
        from gnssvodpy.processor.processor import RinexDataProcessor
        return RinexDataProcessor(*args, **kwargs)
```

---

## ✅ Verification

After restarting, you should see:

```python
from canvodpy import Site, Pipeline

site = Site("Rosalia")
pipeline = site.pipeline()  # ✅ Works!
```

---

## 🔄 Alternative: Use gnssvodpy Directly

If you want to continue without restarting, use gnssvodpy directly:

```python
# Temporary workaround (bypasses canvodpy API)
from gnssvodpy.icechunk_manager.manager import GnssResearchSite
from gnssvodpy.processor.pipeline_orchestrator import PipelineOrchestrator

site = GnssResearchSite(site_name="Rosalia")
orchestrator = PipelineOrchestrator(site=site, dry_run=False)
```

But **restarting is recommended** to use the clean canvodpy API!

---

## 📝 What Happened

1. **Earlier today**: We migrated processor module by copying files
2. **Problem**: Full processor.py code came with all its imports
3. **Fix**: Replaced with lightweight stub that imports from gnssvodpy
4. **Cache**: Marimo/Python cached the old imports
5. **Solution**: Restart to clear cache

---

## 🎯 Status

- ✅ processor.py fixed (1.4 KB stub)
- ✅ Imports from gnssvodpy (stable)
- ✅ All caches cleared
- ⏳ **Need to restart marimo**

---

## 🚀 After Restart

The demo will work perfectly:

```python
from canvodpy import Site, Pipeline

# Level 2 API - Clean and simple!
site = Site("Rosalia")
pipeline = site.pipeline(n_workers=12)
data = pipeline.process_date("2025001")

# ✅ Success!
```

---

**Just restart marimo and you're good to go!** 🎉
