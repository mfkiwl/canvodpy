# Deleted Utils Functions - Usage Analysis

**Date:** January 24, 2026  
**Purpose:** Determine what needs to go into canvod-utils/tools/

---

## 📊 Usage Summary

| Function | Uses | Used By | Priority | Destination |
|----------|------|---------|----------|-------------|
| **get_version_from_pyproject** | 17 | canvod-store (14), canvod-readers (3) | 🔴 **CRITICAL** | canvod-utils/tools/version.py |
| **YYYYDOY** | 75 | canvod-aux (37), canvod-readers (29), canvod-store (6) | 🔴 **CRITICAL** | canvod-utils/tools/date_utils.py |
| **YYDOY** | 75 | (same as YYYYDOY) | 🔴 **CRITICAL** | canvod-utils/tools/date_utils.py |
| **gpsweekday** | 10 | canvod-aux (7), canvod-readers (3) | 🟡 **HIGH** | canvod-utils/tools/date_utils.py |
| **get_gps_week_from_filename** | 7 | canvod-aux (7) | 🟡 **HIGH** | canvod-utils/tools/date_utils.py |
| **isfloat** | 4 | canvod-readers (4) | 🟢 **MEDIUM** | canvod-utils/tools/validation.py |
| **rinex_file_hash** | 3 | canvod-readers (3) | 🟢 **MEDIUM** | canvod-utils/tools/hashing.py |
| **TqdmUpTo** | 0 | NONE | ⚪ **SKIP** | Don't migrate |
| **cls_timer** | 0 | NONE | ⚪ **SKIP** | Don't migrate |
| **enforce_keyword_only_methods** | 0 | NONE | ⚪ **SKIP** | Don't migrate |
| **check_dir_exists** | 0 | NONE | ⚪ **SKIP** | Don't migrate |
| **extract_file** | 0 | NONE | ⚪ **SKIP** | Don't migrate |

---

## 🔴 CRITICAL (Must Implement)

### 1. get_version_from_pyproject() - 17 uses

**Used by:**
- canvod-store/store.py (5 uses) - Commit messages
- canvod-store/reader.py (5 uses) - Commit messages
- canvod-store/manager.py (2 uses) - Commit messages
- canvod-store/grid_adapters/complete_grid_vod_workflow.py (2 uses) - Metadata
- canvod-readers/rinex/v3_04.py (2 uses) - Metadata
- canvod-readers/gnss_specs/utils.py (1 use) - Metadata

**Purpose:** Get package version for metadata and commit messages

**Implementation:** `canvod-utils/tools/version.py`

---

### 2. YYYYDOY + YYDOY - 75 uses total

**Used by:**
- canvod-aux (37 uses)
  - _internal/date_utils.py (14)
  - augmentation.py (4)
  - pipeline.py (3)
  - products/models.py (4)
  - clock/reader.py (2)
  - ephemeris/reader.py (2)
  - container.py (1)
  - core/base.py (2)
  - _internal/__init__.py (2)
  
- canvod-readers (29 uses)
  - utils/date_utils.py (16)
  - matching/models.py (8)
  - matching/dir_matcher.py (7)
  - __init__.py (2)
  - utils/__init__.py (2)
  
- canvod-store (6 uses)
  - manager.py (3)
  - reader.py (3)

**Purpose:** Date handling for GNSS data (year + day-of-year format)

**Current:** DUPLICATED in canvod-aux and canvod-readers

**Implementation:** `canvod-utils/tools/date_utils.py`

**Action:** De-duplicate by moving to utils and updating all imports

---

## 🟡 HIGH (Should Implement)

### 3. gpsweekday() - 10 uses

**Used by:**
- canvod-aux/_internal/date_utils.py (5 uses)
- canvod-readers/utils/date_utils.py (3 uses)
- canvod-aux/_internal/__init__.py (2 uses)

**Purpose:** Convert date to GPS week number and day of week

**Implementation:** `canvod-utils/tools/date_utils.py`

---

### 4. get_gps_week_from_filename() - 7 uses

**Used by:**
- canvod-aux (7 uses)
  - clock/reader.py (2)
  - ephemeris/reader.py (2)
  - _internal/__init__.py (2)
  - _internal/date_utils.py (1)

**Purpose:** Extract GPS week from GNSS product filenames

**Implementation:** `canvod-utils/tools/date_utils.py`

---

## 🟢 MEDIUM (Nice to Have)

### 5. isfloat() - 4 uses

**Used by:**
- canvod-readers/gnss_specs/utils.py (4 uses)

**Purpose:** Check if value can be converted to float

**Implementation:** `canvod-utils/tools/validation.py`

---

### 6. rinex_file_hash() - 3 uses

**Used by:**
- canvod-readers/gnss_specs/utils.py (3 uses)

**Purpose:** Generate hash of RINEX file

**Implementation:** `canvod-utils/tools/hashing.py`

---

## ⚪ SKIP (Not Used)

The following functions are **NOT used anywhere** and should **NOT be migrated**:

1. **TqdmUpTo** - Custom tqdm class (0 uses)
2. **cls_timer** - Decorator for timing methods (0 uses)
3. **enforce_keyword_only_methods** - Force keyword-only args (0 uses)
4. **check_dir_exists** - Directory creation utility (0 uses)
5. **extract_file** - File extraction utility (0 uses)

These were probably replaced by better alternatives or are no longer needed.

---

## 📁 Proposed Structure

```
packages/canvod-utils/src/canvod/utils/
├── config/              # ✅ Already exists
├── _meta/              # ✅ Already exists
└── tools/              # ❌ NEW - Create this
    ├── __init__.py
    ├── version.py      # get_version_from_pyproject()
    ├── date_utils.py   # YYYYDOY, YYDOY, gpsweekday(), get_gps_week_from_filename()
    ├── validation.py   # isfloat()
    └── hashing.py      # rinex_file_hash()
```

---

## 🔧 Implementation Priority

### Phase 1: Critical (Blocking Issues)
1. ✅ Create canvod-utils/tools/ structure
2. ✅ Implement `version.py` (get_version_from_pyproject)
3. ✅ Implement `date_utils.py` (YYYYDOY, YYDOY, gpsweekday, get_gps_week_from_filename)
4. ✅ Update all imports in canvod-store (broken)
5. ✅ Update all imports in canvod-aux (currently uses duplicated YYYYDOY)
6. ✅ Update all imports in canvod-readers (currently uses duplicated YYYYDOY)
7. ✅ Remove duplicated YYYYDOY from canvod-aux and canvod-readers

### Phase 2: Nice to Have
8. ⚠️ Implement `validation.py` (isfloat) - if time permits
9. ⚠️ Implement `hashing.py` (rinex_file_hash) - if time permits

### Phase 3: Skip
10. ❌ Don't migrate unused functions

---

## 📊 Import Update Count

**After implementation, need to update imports in:**

- canvod-store: 17 imports
- canvod-aux: 44 imports  
- canvod-readers: 32 imports

**Total: ~93 import statements to update**

---

## ✅ Success Criteria

When done:

```bash
# All packages should import from canvod.utils.tools
from canvod.utils.tools import get_version_from_pyproject
from canvod.utils.tools import YYYYDOY, YYDOY
from canvod.utils.tools import gpsweekday, get_gps_week_from_filename

# No more duplicates
grep -r "class YYYYDOY" packages/canvod-aux/src     # Should return nothing
grep -r "class YYYYDOY" packages/canvod-readers/src # Should return nothing

# No more broken imports
grep -r "from canvodpy.utils" packages/*/src        # Should return nothing

# All packages import successfully
uv run python -c "import canvod.store; print('✅')"
```
