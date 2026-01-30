# Configuration Path Fix

## Problem

Two configuration issues discovered:

1. **Wrong .env file location:** `research_sites_config.py` was looking for `.env` in `canvodpy/` instead of monorepo root
2. **CLI crash:** `canvodpy config show` crashed with `AttributeError: 'PosixPath' object has no attribute 'isidentifier'`

### Symptoms

**Issue 1 - Wrong Paths:**
```python
# Paths incorrectly pointing to wrong location
base_dir = PosixPath('/Users/work/Developer/GNSS/canvodpy/packages/canvod-readers/data/01_Rosalia')
```

**Issue 2 - CLI Crash:**
```bash
$ canvodpy config show
AttributeError: 'PosixPath' object has no attribute 'isidentifier'
```

---

## Root Cause

### Issue 1: Incorrect _ENV_DIR Calculation

**File:** `canvodpy/src/canvodpy/research_sites_config.py`

```python
# BEFORE - Wrong number of .parent calls
_ENV_DIR = Path(__file__).parent.parent.parent  # Points to canvodpy/

# File structure:
# canvodpy/src/canvodpy/research_sites_config.py
# .parent = canvodpy/src/canvodpy/
# .parent.parent = canvodpy/src/
# .parent.parent.parent = canvodpy/  ❌ Wrong! Looking for .env here

# But .env is actually at:
# . (monorepo root)  ✅ Should look here
```

**Also:** Default fallback used `Path.cwd() / "data"` which changes based on where script is run from.

### Issue 2: Incorrect typer.Option Usage

**File:** `packages/canvod-utils/src/canvod/utils/config/cli.py`

```python
# BEFORE - Passing Path object as first arg to typer.Option
CONFIG_DIR_OPTION = typer.Option(
    DEFAULT_CONFIG_DIR,  # ❌ Path object passed here
    "--config-dir",
    "-c",
    help="Configuration directory",
)
```

When using `Annotated[Type, typer.Option(...)]`, the Option shouldn't contain the default value as first positional arg - it should be in the function signature only.

---

## Solution

### Fix #1: Correct .env File Path

**File:** `canvodpy/src/canvodpy/research_sites_config.py`

**Before:**
```python
_ENV_DIR = Path(__file__).parent.parent.parent
_GNSS_ROOT_DIR = Path(os.getenv("GNSS_ROOT_DIR", Path.cwd() / "data"))
```

**After:**
```python
_ENV_DIR = Path(__file__).parent.parent.parent.parent  # One more .parent!
_GNSS_ROOT_DIR = Path(os.getenv("GNSS_ROOT_DIR", _ENV_DIR / "data"))
```

**Changes:**
1. Added one more `.parent` to reach monorepo root
2. Changed fallback from `Path.cwd() / "data"` to `_ENV_DIR / "data"` (consistent regardless of where run from)

### Fix #2: Correct typer.Option Usage

**File:** `packages/canvod-utils/src/canvod/utils/config/cli.py`

**Before:**
```python
CONFIG_DIR_OPTION = typer.Option(
    DEFAULT_CONFIG_DIR,  # ❌ Path object as first arg
    "--config-dir",
    "-c",
    help="Configuration directory",
)
```

**After:**
```python
CONFIG_DIR_OPTION = typer.Option(
    "--config-dir",  # ✅ Option name first
    "-c",
    help="Configuration directory",
)
```

**The default value is now only in the function signature:**
```python
def init(
    config_dir: Annotated[Path, CONFIG_DIR_OPTION] = DEFAULT_CONFIG_DIR,  # Default here
```

---

## Verification ✅

### 1. Configuration Paths Test

```bash
$ uv run python check_config_paths.py

============================================================
Configuration Path Test
============================================================

base_dir: /Users/work/Developer/GNSS/canvodpy-test-data/valid/01_Rosalia
rinex_store_path: /Users/work/Developer/GNSS/canvodpy-test-data/valid/01_Rosalia/03_Rinex_Testing
vod_store_path: /Users/work/Developer/GNSS/canvodpy-test-data/valid/01_Rosalia/04_VOD_Testing

✅ SUCCESS: Paths correctly point to test data!
============================================================
```

### 2. CLI Works

```bash
$ uv run canvodpy config show

Current Configuration

Processing Configuration:
┌──────────────────┬─────────────────────────────┐
│ Credentials      │ Configured via .env file    │
│ Agency           │ COD                         │
│ Product Type     │ final                       │
│ Max Threads      │ 20                          │
└──────────────────┴─────────────────────────────┘

Research Sites:
  rosalia:
    Base: /Users/work/Developer/GNSS/canvodpy-test-data/valid/
    Receivers: 2
      - reference_01 (reference)
      - canopy_01 (canopy)
```

### 3. Diagnostic Script Runs

```bash
$ uv run python canvodpy/src/canvodpy/diagnostics/timing_diagnostics_script.py

✅ Process completed with exit code 0 (runtime: 10.81s)
```

---

## Files Modified

1. **`canvodpy/src/canvodpy/research_sites_config.py`**
   - Fixed `_ENV_DIR` calculation (added one more `.parent`)
   - Changed default `_GNSS_ROOT_DIR` from `Path.cwd()` to `_ENV_DIR` based

2. **`packages/canvod-utils/src/canvod/utils/config/cli.py`**
   - Removed `DEFAULT_CONFIG_DIR` from `CONFIG_DIR_OPTION` definition
   - Default value now only in function signature

---

## Key Learnings

### 1. Path Calculation in Modules

When calculating paths relative to `__file__`, count carefully:

```python
# Always verify with actual file structure
# packages/canvodpy/src/canvodpy/module.py
# .parent → packages/canvodpy/src/canvodpy/
# .parent.parent → packages/canvodpy/src/
# .parent.parent.parent → packages/canvodpy/
# .parent.parent.parent.parent → packages/ (monorepo root)
```

### 2. Avoid Path.cwd() for Module-level Defaults

**Bad:**
```python
DEFAULT_PATH = Path.cwd() / "data"  # Changes based on where script is run!
```

**Good:**
```python
_MODULE_DIR = Path(__file__).parent
DEFAULT_PATH = _MODULE_DIR / "data"  # Always relative to module
```

### 3. typer.Option with Annotated

When using `Annotated[Type, typer.Option(...)]`, the Option should only contain metadata, not the default value:

**Pattern:**
```python
MY_OPTION = typer.Option(
    "--option-name",      # Option name
    "-o",                 # Short name
    help="Description",   # Help text
    # NO default value here!
)

def command(
    param: Annotated[Type, MY_OPTION] = default_value,  # Default here
):
    pass
```

### 4. Test Configuration from Multiple Locations

Configuration issues often only appear when running from different directories. Test from:
- Project root
- Package directories  
- Arbitrary locations

---

## Status

| Component | Status |
|-----------|--------|
| .env file loading | ✅ Fixed |
| Configuration paths | ✅ Correct |
| CLI (`canvodpy config show`) | ✅ Works |
| Diagnostic script | ✅ Runs |
| Path consistency | ✅ Independent of cwd |

**Result:** Configuration system now works correctly from any location! 🎉
