# Config Loader Fix - Monorepo Root Detection

## Problem

Even after fixing the CLI to use monorepo root, `ConfigLoader` was still using `Path.cwd() / "config"`, causing errors when running from subdirectories:

```bash
$ cd packages/canvod-readers
$ uv run canvodpy config show

⚠️  Warning: /Users/work/Developer/GNSS/canvodpy/packages/canvod-readers/config/processing.yaml not found
❌ Required configuration file missing: /Users/work/Developer/GNSS/canvodpy/packages/canvod-readers/config/sites.yaml
```

**Root cause:** `ConfigLoader` and CLI were using different default logic for finding the config directory.

---

## Solution

### Added `find_monorepo_root()` to ConfigLoader

**File:** `packages/canvod-utils/src/canvod/utils/config/loader.py`

```python
def find_monorepo_root() -> Path:
    """Find the monorepo root by looking for .git directory."""
    current = Path.cwd().resolve()
    
    # Walk up directory tree looking for .git
    for parent in [current] + list(current.parents):
        if (parent / ".git").exists():
            return parent
    
    # Fallback: calculate from __file__
    try:
        loader_file = Path(__file__).resolve()
        monorepo_root = loader_file.parent.parent.parent.parent.parent.parent.parent
        if (monorepo_root / ".git").exists():
            return monorepo_root
    except Exception:
        pass
    
    raise RuntimeError("Cannot find monorepo root")
```

### Updated ConfigLoader.__init__

**Before:**
```python
def __init__(self, config_dir: Path | None = None) -> None:
    self.config_dir = Path(config_dir or Path.cwd() / "config")
```

**After:**
```python
def __init__(self, config_dir: Path | None = None) -> None:
    if config_dir is None:
        try:
            monorepo_root = find_monorepo_root()
            config_dir = monorepo_root / "config"
        except RuntimeError:
            config_dir = Path.cwd() / "config"  # Fallback
    
    self.config_dir = Path(config_dir)
```

---

## Verification ✅

Created test script that verifies config loading from 5 different directories:

```bash
$ uv run python test_config_from_anywhere.py

======================================================================
Testing config loader from multiple directories
======================================================================

📁 Testing from: .
   ✅ SUCCESS

📁 Testing from: canvodpy
   ✅ SUCCESS

📁 Testing from: packages/canvod-readers
   ✅ SUCCESS

📁 Testing from: packages/canvod-readers/tests
   ✅ SUCCESS

📁 Testing from: packages/canvod-utils/src/canvod/utils/config
   ✅ SUCCESS

======================================================================
✅ SUCCESS: All 5 directories passed!
======================================================================
```

---

## Consistency Achieved

Both CLI and ConfigLoader now use the **same logic** for finding the config directory:

### CLI (cli.py)
```python
try:
    MONOREPO_ROOT = find_monorepo_root()
    DEFAULT_CONFIG_DIR = MONOREPO_ROOT / "config"
except RuntimeError:
    DEFAULT_CONFIG_DIR = Path.cwd() / "config"
```

### ConfigLoader (loader.py)
```python
if config_dir is None:
    try:
        monorepo_root = find_monorepo_root()
        config_dir = monorepo_root / "config"
    except RuntimeError:
        config_dir = Path.cwd() / "config"
```

**Result:** Identical behavior from any directory! 🎉

---

## Files Modified

1. **`packages/canvod-utils/src/canvod/utils/config/loader.py`**
   - Added `find_monorepo_root()` function
   - Updated `ConfigLoader.__init__()` to use monorepo root
   - Updated `load_config()` docstring

---

## Status

| Component | Status |
|-----------|--------|
| CLI config directory | ✅ Fixed (previous) |
| ConfigLoader config directory | ✅ Fixed (this fix) |
| Works from monorepo root | ✅ Verified |
| Works from canvodpy/ | ✅ Verified |
| Works from packages/canvod-readers/ | ✅ Verified |
| Works from deep nested dirs | ✅ Verified |
| CLI and ConfigLoader consistent | ✅ Verified |

**Configuration system now fully consistent! 🎉**
