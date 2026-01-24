# Deleted Utils Functions - Complete Usage Analysis

**Date:** January 24, 2026  
**Purpose:** Determine what needs to go into canvod-utils/tools/

---

## 📊 Complete Usage Summary

| Function | Uses | Priority | Action |
|----------|------|----------|--------|
| **YYYYDOY** | 148 | 🔴 CRITICAL | ✅ CREATED in canvod-utils/tools/date_utils.py |
| **get_version_from_pyproject** | 28 | 🔴 CRITICAL | ✅ CREATED in canvod-utils/tools/version.py |
| **gpsweekday** | 20 | 🔴 CRITICAL | ✅ CREATED in canvod-utils/tools/date_utils.py |
| **get_gps_week_from_filename** | 13 | 🟡 HIGH | ✅ CREATED in canvod-utils/tools/date_utils.py |
| **isfloat** | 13 | 🟡 HIGH | ❌ TODO: Create in validation.py |
| **rinex_file_hash** | 6 | 🟢 MEDIUM | ❌ TODO: Create in hashing.py |
| **TqdmUpTo** | 0 | ⚪ SKIP | ❌ Not needed |
| **cls_timer** | 0 | ⚪ SKIP | ❌ Not needed |
| **enforce_keyword_only_methods** | 0 | ⚪ SKIP | ❌ Not needed |
| **check_dir_exists** | 0 | ⚪ SKIP | ❌ Not needed |
| **extract_file** | 0 | ⚪ SKIP | ❌ Not needed |

---

## 🔴 CRITICAL Functions (Already Created)

### 1. YYYYDOY - 148 uses ✅

**Used by:**
- canvod-aux/tests (33 uses)
- canvod-utils/tools (22 uses) - our new file
- canvod-readers/utils (18 uses)
- canvod-aux/_internal (16 uses)
- canvod-readers/matching (15 uses)
- orchestrator (12 uses)
- canvod-store (6 uses)
- Multiple other files

**Status:** ✅ Created in `canvod-utils/tools/date_utils.py`

**Currently duplicated in:**
- packages/canvod-aux/src/canvod/aux/_internal/date_utils.py
- packages/canvod-readers/src/canvod/readers/utils/date_utils.py

**Next step:** Remove duplicates after updating all imports

---

### 2. get_version_from_pyproject - 28 uses ✅

**Used by:**
- orchestrator/processor.py (7 uses)
- canvod-store/store.py (5 uses)
- canvod-store/reader.py (5 uses)
- canvod-store/manager.py (2 uses)
- canvod-store/grid_adapters (2 uses)
- canvod-readers/rinex/v3_04.py (2 uses)
- canvod-readers/gnss_specs/utils.py (1 use)
- canvod-readers/tests (2 uses)
- canvod-utils/tools/version.py (2 uses) - our new file

**Status:** ✅ Created in `canvod-utils/tools/version.py`

**Purpose:** Get package version for commit messages and metadata

---

### 3. gpsweekday - 20 uses ✅

**Used by:**
- canvod-aux/tests (7 uses)
- canvod-aux/_internal/date_utils.py (5 uses)
- canvod-utils/tools/date_utils.py (3 uses) - our new file
- canvod-readers/utils/date_utils.py (3 uses)
- canvod-aux/_internal/__init__.py (2 uses)

**Status:** ✅ Created in `canvod-utils/tools/date_utils.py`

**Purpose:** Convert date to GPS week number and day of week

---

## 🟡 HIGH Priority Functions (TODO)

### 4. get_gps_week_from_filename - 13 uses ✅

**Used by:**
- canvod-aux/tests (4 uses)
- canvod-utils/tools/date_utils.py (2 uses) - our new file
- canvod-aux/ephemeris/reader.py (2 uses)
- canvod-aux/clock/reader.py (2 uses)
- canvod-aux/_internal/__init__.py (2 uses)
- canvod-aux/_internal/date_utils.py (1 use)

**Status:** ✅ Created in `canvod-utils/tools/date_utils.py`

**Purpose:** Extract GPS week from GNSS product filenames

---

### 5. isfloat - 13 uses ❌

**Used by:**
- canvod-readers/tests/test_gnss_specs_base.py (9 uses)
- canvod-readers/src/canvod/readers/gnss_specs/utils.py (4 uses)

**Status:** ❌ TODO - Need to create

**Purpose:** Check if value can be converted to float

**Implementation needed:** `canvod-utils/tools/validation.py`

---

## 🟢 MEDIUM Priority Functions (TODO)

### 6. rinex_file_hash - 6 uses ❌

**Used by:**
- canvod-readers/tests/test_gnss_specs_base.py (3 uses)
- canvod-readers/src/canvod/readers/gnss_specs/utils.py (3 uses)

**Status:** ❌ TODO - Need to create

**Purpose:** Generate hash of RINEX file

**Implementation needed:** `canvod-utils/tools/hashing.py`

---

## ⚪ SKIP (Not Used Anywhere)

The following functions have **ZERO uses** and should **NOT be migrated**:

1. **TqdmUpTo** (0 uses)
2. **cls_timer** (0 uses)
3. **enforce_keyword_only_methods** (0 uses)
4. **check_dir_exists** (0 uses)
5. **extract_file** (0 uses)

---

## 📁 Current Structure

```
packages/canvod-utils/src/canvod/utils/
├── config/              # ✅ Exists - YAML config system
├── _meta.py            # ✅ Exists - Package metadata
├── __init__.py         # ✅ Exists
└── tools/              # ✅ Created
    ├── __init__.py     # ❌ TODO
    ├── version.py      # ✅ Created - get_version_from_pyproject()
    ├── date_utils.py   # ✅ Created - YYYYDOY, gpsweekday, get_gps_week_from_filename()
    ├── validation.py   # ❌ TODO - isfloat()
    └── hashing.py      # ❌ TODO - rinex_file_hash()
```

---

## 🔧 Next Steps

### Phase 1: Complete canvod-utils/tools/ (Priority)

1. ✅ DONE: version.py
2. ✅ DONE: date_utils.py
3. ❌ TODO: Create tools/__init__.py with exports
4. ❌ TODO: Create validation.py (isfloat)
5. ❌ TODO: Create hashing.py (rinex_file_hash)

### Phase 2: Update All Imports (~150+ locations)

6. ❌ TODO: Update imports in canvod-store (28 imports)
7. ❌ TODO: Update imports in canvod-aux (50+ imports)
8. ❌ TODO: Update imports in canvod-readers (40+ imports)
9. ❌ TODO: Update imports in orchestrator (12 imports)
10. ❌ TODO: Update imports in tests (20+ imports)

### Phase 3: Remove Duplicates

11. ❌ TODO: Remove canvod-aux/_internal/date_utils.py (YYYYDOY duplicate)
12. ❌ TODO: Remove canvod-readers/utils/date_utils.py (YYYYDOY duplicate)
13. ❌ TODO: Update any remaining imports

---

## ✅ Success Criteria

When complete:

```bash
# All packages import from canvod.utils.tools
from canvod.utils.tools import get_version_from_pyproject
from canvod.utils.tools import YYYYDOY, YYDOY, gpsweekday
from canvod.utils.tools import isfloat, rinex_file_hash

# No duplicates exist
! grep -r "class YYYYDOY" packages/canvod-aux/src
! grep -r "class YYYYDOY" packages/canvod-readers/src

# No broken imports
! grep -r "from canvodpy.utils" packages/*/src

# All packages import successfully
uv run python -c "import canvod.store; print('✅')"
uv run python -c "import canvod.aux; print('✅')"
uv run python -c "import canvod.readers; print('✅')"
```

---

## 📊 Import Update Summary

**Estimated import updates needed:** ~150-200 lines across all packages

This is manageable with systematic search-and-replace operations.
