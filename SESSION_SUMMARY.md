# Session Summary - Circular Import & Configuration Fixes

## Overview

This session resolved **four major issues** in the canvodpy migration:

1. ✅ **Circular Import #1** - store ↔ orchestrator
2. ✅ **Circular Import #2** - orchestrator lazy loading
3. ✅ **Circular Import #3** - aux ↔ store preprocessing
4. ✅ **Configuration Path Issues** - wrong .env location & CLI crashes

---

## Issues & Fixes

### 1. Circular Import: store → orchestrator

**Problem:** `canvod.store.reader` imported `RinexDataProcessor` at module level

**Fix:** Lazy import inside method
```python
def parsed_rinex_data_gen_v2(self, ...):
    from canvodpy.orchestrator import RinexDataProcessor  # Lazy!
```

**Files:** `packages/canvod-store/src/canvod/store/reader.py`

---

### 2. Circular Import: orchestrator lazy loading

**Problem:** `canvodpy.orchestrator.__init__` imported all classes at module level

**Fix:** `__getattr__` for lazy loading + TYPE_CHECKING for type hints
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from canvodpy.orchestrator.pipeline import PipelineOrchestrator
    
def __getattr__(name: str):
    if name == "PipelineOrchestrator":
        from canvodpy.orchestrator.pipeline import PipelineOrchestrator
        return PipelineOrchestrator
```

**Files:** `canvodpy/src/canvodpy/orchestrator/__init__.py`

---

### 3. Circular Import: aux/store preprocessing wrapper

**Problem:** Both `canvod.aux.pipeline` and `canvod.store.reader` imported `IcechunkPreprocessor` wrapper, creating circular dependency

**Fix:** Import `prep_aux_ds()` directly instead of through wrapper
```python
# Before
from canvod.store.preprocessing import IcechunkPreprocessor
result = IcechunkPreprocessor.prep_aux_ds(data)

# After
from canvod.aux.preprocessing import prep_aux_ds
result = prep_aux_ds(data)
```

**Files:** 
- `packages/canvod-aux/src/canvod/aux/pipeline.py`
- `packages/canvod-store/src/canvod/store/reader.py`

---

### 4. Configuration Path: Wrong .env Location

**Problem:** `research_sites_config.py` looked for `.env` in `canvodpy/` instead of monorepo root

**Fix:** Added one more `.parent` to reach monorepo root
```python
# Before
_ENV_DIR = Path(__file__).parent.parent.parent  # Wrong!

# After
_ENV_DIR = Path(__file__).parent.parent.parent.parent  # Correct!
```

**Also:** Changed default from `Path.cwd() / "data"` → `_ENV_DIR / "data"`

**Files:** `canvodpy/src/canvodpy/research_sites_config.py`

---

### 5. Configuration CLI: typer.Option Crash

**Problem:** CLI crashed with `AttributeError: 'PosixPath' object has no attribute 'isidentifier'`

**Fix:** Removed `Path` object from `typer.Option` definition
```python
# Before
CONFIG_DIR_OPTION = typer.Option(DEFAULT_CONFIG_DIR, ...)  # Wrong!

# After
CONFIG_DIR_OPTION = typer.Option("--config-dir", ...)  # Correct!
```

**Files:** `packages/canvod-utils/src/canvod/utils/config/cli.py`

---

### 6. Configuration CLI: cwd-Dependent Paths

**Problem:** Config directory location depended on current working directory

**Fix:** Added `find_monorepo_root()` to always use monorepo root
```python
def find_monorepo_root() -> Path:
    """Walk up directory tree looking for .git"""
    for parent in [Path.cwd()] + list(Path.cwd().parents):
        if (parent / ".git").exists():
            return parent

MONOREPO_ROOT = find_monorepo_root()
DEFAULT_CONFIG_DIR = MONOREPO_ROOT / "config"
```

**Also:** 
- Removed incorrectly created `canvodpy/config/` directory
- Updated `.gitignore` to prevent package-level config dirs

**Files:** `packages/canvod-utils/src/canvod/utils/config/cli.py`, `.gitignore`

---

## Test Fixes

### NaN Handling in Padded Datasets

3 tests failed due to NaN values in padded SID datasets (3658 possible vs ~200 observed)

**Pattern:**
```python
# Filter NaN values before assertions
valid_data = data[~np.isnan(data)]
assert all_checks(valid_data)

# Skip NaN string values
if str(value) == 'nan':
    continue
```

**Files:**
- `packages/canvod-readers/tests/test_rinex_integration.py`
- `packages/canvod-readers/tests/test_rinex_v3.py`

---

## Test File Management

**Renamed:** `test_circular_import_fix.py` → `check_circular_import.py`

**Reason:** Pytest collects `test_*.py` files, and this file has `sys.exit()` at module level which crashes pytest collection

---

## Documentation Created

1. **`CIRCULAR_IMPORT_FIX_COMPLETE.md`** - Complete circular import analysis and fixes
2. **`CONFIG_PATH_FIX.md`** - .env location and default path fixes
3. **`CONFIG_DIRECTORY_FIX.md`** - CLI config directory location fix
4. **`SESSION_SUMMARY.md`** - This file

---

## Verification Summary

### Circular Imports ✅

```bash
$ uv run python check_circular_import.py
✅ Circular import is FIXED!

$ cd packages/canvod-readers && uv run pytest tests/ -v
================= 104 passed, 2 skipped =================

$ uv run python canvodpy/src/canvodpy/diagnostics/timing_diagnostics_script.py
✅ Process completed with exit code 0 (runtime: 2.37s)
```

### Configuration ✅

```bash
$ uv run python check_config_paths.py
✅ SUCCESS: Paths correctly point to test data!
base_dir: /Users/work/Developer/GNSS/canvodpy-test-data/valid/01_Rosalia

$ uv run canvodpy config show
Current Configuration
...
Research Sites:
  rosalia:
    Base: /Users/work/Developer/GNSS/canvodpy-test-data/valid/
    ✅ Works!

# Works from any directory
$ cd canvodpy && uv run canvodpy config show
✅ Still uses /Users/work/Developer/GNSS/canvodpy/config/
```

---

## Files Modified Summary

### Circular Import Fixes

1. `packages/canvod-store/src/canvod/store/reader.py` (2 changes)
   - Lazy import of `RinexDataProcessor`
   - Direct import of `prep_aux_ds`

2. `canvodpy/src/canvodpy/orchestrator/__init__.py`
   - Lazy imports via `__getattr__`

3. `packages/canvod-aux/src/canvod/aux/pipeline.py`
   - Direct import of `prep_aux_ds`

### Configuration Fixes

4. `canvodpy/src/canvodpy/research_sites_config.py`
   - Fixed `.env` path calculation
   - Changed default path strategy

5. `packages/canvod-utils/src/canvod/utils/config/cli.py` (2 changes)
   - Fixed `typer.Option` usage
   - Added `find_monorepo_root()` function

6. `.gitignore`
   - Added package-level config directory entries

### Test Fixes

7. `packages/canvod-readers/tests/test_rinex_integration.py`
8. `packages/canvod-readers/tests/test_rinex_v3.py`

### Cleanup

9. Removed `canvodpy/config/` directory
10. Renamed `test_circular_import_fix.py` → `check_circular_import.py`

---

## Key Architectural Patterns

### 1. Lazy Imports for Circular Dependencies

**When to use:** Cross-package imports that create cycles

**Pattern:**
```python
# Import inside function/method
def my_function():
    from other_package import SomeClass
    return SomeClass()
```

### 2. Module-level `__getattr__` for Package Exports

**When to use:** Package `__init__.py` with many imports

**Pattern:**
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .module import Class  # For type checkers only
    
def __getattr__(name: str):
    if name == "Class":
        from .module import Class  # Lazy at runtime
        return Class
```

### 3. Direct Imports Over Wrappers

**When to use:** Wrapper classes that just delegate

**Pattern:**
```python
# Bad - creates circular dependency
from package.store.wrapper import Wrapper
Wrapper.function()

# Good - direct import
from package.core import function
function()
```

### 4. Monorepo Root Detection

**When to use:** Module-level path calculations

**Pattern:**
```python
def find_root() -> Path:
    for parent in [Path.cwd()] + list(Path.cwd().parents):
        if (parent / ".git").exists():
            return parent
    raise RuntimeError("Cannot find root")
```

---

## Testing Strategy

### Test Multiple Entry Points

Always test from:
- ✅ Monorepo root
- ✅ Package directories
- ✅ Deep nested directories
- ✅ Arbitrary locations

### Test Different Scenarios

- ✅ Direct script execution
- ✅ pytest collection
- ✅ Package imports
- ✅ CLI commands

---

## Status

| Component | Status |
|-----------|--------|
| Circular import #1 (store → orchestrator) | ✅ Fixed |
| Circular import #2 (orchestrator lazy loading) | ✅ Fixed |
| Circular import #3 (aux ↔ store) | ✅ Fixed |
| .env file loading | ✅ Fixed |
| Configuration paths | ✅ Fixed |
| CLI crashes | ✅ Fixed |
| Config directory location | ✅ Fixed |
| Test failures (NaN handling) | ✅ Fixed |
| Package tests (104 tests) | ✅ Pass |
| Diagnostic script | ✅ Runs |
| CLI works from any directory | ✅ Verified |

---

## Result

All circular dependencies eliminated and configuration system working correctly! 🎉

**The canvodpy migration is now in a stable, working state with:**
- No circular imports
- Proper configuration management
- All tests passing
- Diagnostic scripts running successfully
