# canvod-utils/tools/ Creation Complete

**Date:** January 24, 2026  
**Status:** ✅ COMPLETE

---

## ✅ What Was Created

### New Directory Structure

```
packages/canvod-utils/src/canvod/utils/
├── config/              # ✅ Already existed
├── _meta.py            # ✅ Already existed
├── __init__.py         # ✅ Updated to mention tools
└── tools/              # ✅ NEWLY CREATED
    ├── __init__.py     # ✅ Created - exports all utilities
    ├── version.py      # ✅ Created - get_version_from_pyproject()
    ├── date_utils.py   # ✅ Created - YYYYDOY, YYDOY, gpsweekday, etc.
    ├── validation.py   # ✅ Created - isfloat()
    └── hashing.py      # ✅ Created - rinex_file_hash()
```

---

## 📦 Functions Implemented

### ✅ version.py
- **get_version_from_pyproject()** - Get package version from pyproject.toml

### ✅ date_utils.py
- **YYYYDOY** - Year + day-of-year date class (most important, 148 uses!)
- **YYDOY** - Two-digit year + DOY class
- **gpsweekday()** - Convert date to GPS week and day
- **get_gps_week_from_filename()** - Extract GPS week from filenames

### ✅ validation.py
- **isfloat()** - Check if value can convert to float

### ✅ hashing.py
- **rinex_file_hash()** - Compute SHA256 hash of RINEX files

---

## 🧪 Testing Results

All imports work correctly:

```python
✅ get_version_from_pyproject
✅ YYYYDOY, YYDOY
✅ gpsweekday, get_gps_week_from_filename
✅ isfloat
✅ rinex_file_hash

# Functionality tests passed
isfloat("3.14"): True
isfloat("hello"): False
YYYYDOY.from_str("2025024"): 2025024
```

---

## 📊 Usage Statistics

| Function | Current Uses | Where |
|----------|--------------|-------|
| YYYYDOY | 148 | canvod-aux, canvod-readers, canvod-store, orchestrator |
| get_version_from_pyproject | 28 | canvod-store, orchestrator, canvod-readers |
| gpsweekday | 20 | canvod-aux, canvod-readers |
| get_gps_week_from_filename | 13 | canvod-aux |
| isfloat | 13 | canvod-readers |
| rinex_file_hash | 6 | canvod-readers |

**Total impact: ~228 uses across the codebase**

---

## 🔧 Dependencies Added

Updated `canvod-utils/pyproject.toml`:

```toml
dependencies = [
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "pyyaml>=6.0",
    "typer>=0.9",
    "rich>=13.0",
    "email-validator>=2.0",
    "tomli>=2.0; python_version < '3.11'",  # ✅ Added for version.py
]
```

---

## 🎯 Next Steps (Ready to Execute)

### Phase 1: Update All Imports

Now that canvod-utils/tools exists, we need to update ~228 import statements:

**Priority order:**
1. **canvod-store** (28 imports) - Currently broken
2. **orchestrator** (12 imports) - Currently broken
3. **canvod-aux** (~60 imports) - Using duplicated YYYYDOY
4. **canvod-readers** (~50 imports) - Using duplicated YYYYDOY

### Phase 2: Remove Duplicates

After all imports are updated:

```bash
# Remove duplicate YYYYDOY implementations
rm packages/canvod-aux/src/canvod/aux/_internal/date_utils.py
rm packages/canvod-readers/src/canvod/readers/utils/date_utils.py
```

Update any remaining imports in those packages.

### Phase 3: Verification

```bash
# Test all packages import successfully
uv run python -c "import canvod.store; print('✅')"
uv run python -c "import canvod.aux; print('✅')"
uv run python -c "import canvod.readers; print('✅')"
uv run python -c "from canvodpy import Pipeline; print('✅')"

# Verify no broken imports remain
! grep -r "from canvodpy.utils" packages/*/src
! grep -r "from canvodpy.data_handler" packages/*/src

# Verify no duplicates remain
! grep -r "class YYYYDOY" packages/canvod-aux/src
! grep -r "class YYYYDOY" packages/canvod-readers/src
```

---

## 📚 Usage Examples

### For Package Developers

```python
# Import utilities from canvod.utils.tools
from canvod.utils.tools import (
    get_version_from_pyproject,
    YYYYDOY,
    gpsweekday,
    isfloat,
    rinex_file_hash,
)

# Get package version
version = get_version_from_pyproject()

# Work with GNSS dates
date = YYYYDOY.from_str("2025024")
dt = date.to_datetime()
week, day = gpsweekday(dt)

# Validate input
if isfloat(user_input):
    value = float(user_input)

# Hash RINEX files
from pathlib import Path
hash_val = rinex_file_hash(Path("data.rnx"))
```

---

## 🎉 Success Metrics

✅ All 6 critical/high-priority functions implemented  
✅ All imports tested and working  
✅ Proper documentation with docstrings  
✅ Type hints included  
✅ Examples in docstrings  
✅ Dependencies updated  
✅ Zero breaking changes (old code still works)  

**Ready for Phase 2: Update all imports across the codebase**

---

## 🗂️ Files Created/Modified

**Created:**
- `packages/canvod-utils/src/canvod/utils/tools/__init__.py`
- `packages/canvod-utils/src/canvod/utils/tools/version.py`
- `packages/canvod-utils/src/canvod/utils/tools/date_utils.py`
- `packages/canvod-utils/src/canvod/utils/tools/validation.py`
- `packages/canvod-utils/src/canvod/utils/tools/hashing.py`

**Modified:**
- `packages/canvod-utils/src/canvod/utils/__init__.py` (updated exports)
- `packages/canvod-utils/pyproject.toml` (added tomli dependency)

**Documentation:**
- `UTILS_MIGRATION_COMPLETE_ANALYSIS.md`
- `CANVOD_UTILS_TOOLS_CREATED.md` (this file)
