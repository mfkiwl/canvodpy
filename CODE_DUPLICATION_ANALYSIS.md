# Code Duplication Analysis Report

**Date:** 2026-01-25  
**Project:** canvodpy  
**Analysis:** Complete codebase scan for duplicated code

---

## 🔍 Executive Summary

Found **multiple instances of code duplication** that should be cleaned up:

1. **Unused `_shared` directory** in canvod-readers (1 file, 205 lines)
2. **YYYYDOY class duplicated** in 3 locations (total: ~793 lines)
3. **gpsweekday function duplicated** in 2 locations
4. **Configuration duplication** (.env vs processing.yaml)
5. **Old gnssvodpy imports** still present in canvod-store

---

## 📋 Detailed Findings

### 1. Unused `_shared` Directory ⚠️

**Location:** `packages/canvod-readers/src/canvod/readers/_shared/`

**Files:**
- `signals.py` (205 lines)

**Status:** ❌ **NOT USED ANYWHERE**

**Evidence:**
```bash
# No imports found
$ grep -r "from.*_shared.*import" packages/
# (empty result)
```

**File Header:**
```python
"""GNSS signal and frequency mapping.

Simplified version for initial migration.
Full migration of bands.py (338 lines) + gnss_specs.py (993 lines) + signal_mapping.py (186 lines)
pending in Phase 2 expansion.

TODO: Migrate complete signal mapping system from gnssvodpy/signal_frequency_mapping/
"""
```

**Analysis:**
- This is a **leftover from initial migration**
- The full implementation exists at `packages/canvod-readers/src/canvod/readers/gnss_specs/signals.py` (292 lines)
- The _shared version is outdated and incomplete
- **Safe to delete**

---

### 2. YYYYDOY Class Duplication ⚠️⚠️⚠️

**Found in 3 locations:**

| Location | Lines | MD5 Hash | Status |
|----------|-------|----------|--------|
| `canvod-utils/src/canvod/utils/tools/date_utils.py` | 386 | `91e258b774ad92de20e52968c98923ff` | ✅ **CANONICAL** |
| `canvod-readers/src/canvod/readers/utils/date_utils.py` | 241 | `3a4b7af7d3b7a215397f6414e6a678f5` | ❌ **DUPLICATE** |
| `canvod-aux/src/canvod/aux/_internal/date_utils.py` | 166 | `ccd56d24330d022008b15f2ed9885801` | ❌ **DUPLICATE** |

**Current Import Status:**
```python
# CORRECT imports (15 found):
from canvod.utils.tools import YYYYDOY  # ✅ Using canonical version

# PROBLEMATIC imports:
# In canvod-readers/src/canvod/readers/utils/__init__.py:
from .date_utils import YYYYDOY  # ❌ Local import, should use canvod.utils

# In canvod-store (2 old imports):
from gnssvodpy.utils.date_time import YYYYDOY  # ❌ OLD gnssvodpy import!
```

**Evidence of Usage:**
```bash
# Most packages correctly import from canvod.utils:
$ grep -r "from canvod.utils.tools import YYYYDOY" packages/
packages/canvod-readers/src/canvod/readers/matching/models.py
packages/canvod-readers/src/canvod/readers/matching/dir_matcher.py
packages/canvod-readers/src/canvod/readers/__init__.py
packages/canvod-aux/src/canvod/aux/core/base.py
packages/canvod-aux/src/canvod/aux/pipeline.py
# ... 15 total
```

**Problems:**
1. **canvod-readers** still exports its own YYYYDOY via `__init__.py`
2. **canvod-aux** still has duplicate implementation
3. **canvod-store** still imports from OLD gnssvodpy!

**Impact:**
- Wasted ~407 lines of duplicated code
- Maintenance burden (changes must be made in 3 places)
- Confusion about which version to use
- Risk of divergence between implementations

---

### 3. gpsweekday Function Duplication ⚠️

**Found in 2 locations:**

| Location | Status |
|----------|--------|
| `canvod-utils/src/canvod/utils/tools/date_utils.py` | ✅ **CANONICAL** |
| `canvod-aux/src/canvod/aux/_internal/date_utils.py` | ❌ **DUPLICATE** |

**Analysis:**
- Same function duplicated in canvod-aux
- Should import from canvod-utils instead
- Part of the same date_utils.py duplication issue

---

### 4. Configuration Duplication ⚠️⚠️

**Two Configuration Systems:**

#### System 1: .env (via settings.py)
**File:** `canvodpy/src/canvodpy/settings.py`

**Loads from:**
```python
# From .env file
CDDIS_MAIL=your.email@example.com
GNSS_ROOT_DIR=/path/to/data
```

**Code:**
```python
from dotenv import load_dotenv
_env_path = Path(__file__).parent.parent.parent / '.env'
if _env_path.exists():
    load_dotenv(_env_path)

class AppSettings:
    def __init__(self):
        self.cddis_mail = os.getenv('CDDIS_MAIL')
        self.gnss_root_dir = os.getenv('GNSS_ROOT_DIR')
```

**Used by:**
- `canvodpy.settings.get_settings()`
- `canvod.aux.pipeline` (for FTP authentication)

---

#### System 2: processing.yaml (via config loader)
**File:** `canvodpy/config/processing.yaml`

**Contains:**
```yaml
credentials:
  cddis_mail: your.email@example.com
  gnss_root_dir: /path/to/your/gnss/data

aux_data:
  agency: COD
  product_type: final

processing:
  time_aggregation_seconds: 15
  n_max_threads: 20
  keep_rnx_vars:
    - SNR
  aggregate_glonass_fdma: true

compression:
  zlib: true
  complevel: 5

icechunk:
  compression_level: 5
  compression_algorithm: zstd
  # ... more settings
```

**Loader:** `canvod-utils/src/canvod/utils/config/loader.py`

**Status:** ❓ **NOT INTEGRATED with settings.py**

---

#### Analysis: Configuration Duplication

**Overlap:**
| Setting | .env (settings.py) | processing.yaml | Status |
|---------|-------------------|-----------------|--------|
| `cddis_mail` | ✅ | ✅ | ⚠️ **DUPLICATE** |
| `gnss_root_dir` | ✅ | ✅ | ⚠️ **DUPLICATE** |
| `agency` | ❌ | ✅ | ℹ️ Only in yaml |
| `product_type` | ❌ | ✅ | ℹ️ Only in yaml |
| `keep_rnx_vars` | ❌ | ✅ | ℹ️ Only in yaml |
| ... more | ❌ | ✅ | ℹ️ Only in yaml |

**Current State:**
- **settings.py loads ONLY from .env** (via python-dotenv)
- **processing.yaml is NOT loaded by settings.py**
- **Both have cddis_mail and gnss_root_dir fields**
- **User must maintain BOTH files** for consistency

**Problem:**
- Duplication of credential fields
- No integration between systems
- User confusion: "Do I use .env or processing.yaml?"
- Risk of inconsistency if values differ

---

#### Question: Is .env Still Needed?

**Short Answer:** 🤔 **Potentially NO**, but needs careful migration

**Reasons to Keep .env:**
1. **Standard practice** - .env is Python ecosystem standard
2. **Environment-specific** - Different for dev/staging/prod
3. **Security** - Excluded from git by default
4. **Simple** - Easy to understand

**Reasons to Remove .env:**
1. **Duplication** - Same fields in processing.yaml
2. **Confusion** - Two config files for same data
3. **Already have processing.yaml** - More comprehensive
4. **Config loader exists** - Can handle credentials

**Recommendation:**

**Option 1: Keep .env (Simple)**
- Keep settings.py + .env as-is
- Remove `cddis_mail` and `gnss_root_dir` from processing.yaml
- Document: "Credentials in .env, other settings in processing.yaml"

**Option 2: Migrate to processing.yaml Only (Clean)**
- Modify settings.py to load from processing.yaml instead of .env
- Remove .env support
- Single source of truth: processing.yaml
- Document: "All settings in processing.yaml"

**Option 3: Hybrid (Current - Confusing)**
- Keep both systems
- Document which takes precedence
- **Not recommended** - maintains duplication

**My Recommendation:** **Option 1 (Keep .env)**
- Less disruptive
- Follows Python best practices
- Clean separation: credentials (.env) vs settings (processing.yaml)
- Remove duplicate fields from processing.yaml

---

### 5. Old gnssvodpy Imports ⚠️

**Found in canvod-store:**

```python
# packages/canvod-store/src/canvod/store/reader.py
from gnssvodpy.utils.date_time import YYYYDOY  # ❌ OLD IMPORT

# packages/canvod-store/src/canvod/store/manager.py
from gnssvodpy.utils.date_time import YYYYDOY  # ❌ OLD IMPORT
```

**Problem:**
- Still importing from OLD gnssvodpy package
- Should import from `canvod.utils.tools`
- Migration incomplete

---

## 📊 Impact Summary

| Issue | Lines Wasted | Maintenance Impact | Risk |
|-------|--------------|-------------------|------|
| Unused `_shared` | 205 | Low (not used) | None |
| YYYYDOY duplication | ~407 | High (3 copies) | Medium |
| gpsweekday duplication | ~50 | Medium (2 copies) | Low |
| Config duplication | N/A | Medium (confusion) | Medium |
| Old imports | N/A | Low (2 files) | Low |
| **TOTAL** | **~662** | **High** | **Medium** |

---

## 🎯 Recommendations

### Priority 1: Critical (Do First)

**1. Fix Old gnssvodpy Imports in canvod-store**
```python
# BEFORE
from gnssvodpy.utils.date_time import YYYYDOY

# AFTER
from canvod.utils.tools import YYYYDOY
```
**Impact:** High - prevents failures if gnssvodpy not installed

---

### Priority 2: High (Should Do)

**2. Remove YYYYDOY Duplicates**

**Step 1:** Delete duplicate implementations
- ❌ Delete `packages/canvod-readers/src/canvod/readers/utils/date_utils.py`
- ❌ Delete `packages/canvod-aux/src/canvod/aux/_internal/date_utils.py`

**Step 2:** Fix canvod-readers __init__.py
```python
# BEFORE (in packages/canvod-readers/src/canvod/readers/utils/__init__.py)
from .date_utils import YYYYDOY  # ❌ Local import

# AFTER
from canvod.utils.tools import YYYYDOY  # ✅ Import from canonical location
```

**Step 3:** Update dependencies
- Add `canvod-utils` to `canvod-readers` dependencies (if not already)
- Add `canvod-utils` to `canvod-aux` dependencies (if not already)

**Impact:** Saves ~407 lines, removes maintenance burden

---

**3. Resolve Configuration Duplication**

**Recommended: Keep .env, Clean processing.yaml**

**Step 1:** Remove duplicate fields from processing.yaml
```yaml
# REMOVE these from processing.yaml (keep in .env only):
credentials:
  cddis_mail: ...       # ❌ Remove
  gnss_root_dir: ...    # ❌ Remove

# KEEP these in processing.yaml:
aux_data:
  agency: COD
  product_type: final

processing:
  time_aggregation_seconds: 15
  # ... etc
```

**Step 2:** Document clearly
```python
# settings.py docstring:
"""
Credentials Configuration:
- CDDIS_MAIL: Set in .env file
- GNSS_ROOT_DIR: Set in .env file

Other Settings:
- Processing parameters: Set in config/processing.yaml
- See canvod.utils.config for loading processing.yaml
"""
```

**Impact:** Eliminates confusion, single source per setting

---

### Priority 3: Medium (Nice to Have)

**4. Delete Unused `_shared` Directory**
```bash
rm -rf packages/canvod-readers/src/canvod/readers/_shared
```
**Impact:** Removes 205 lines of dead code

---

## 📝 Implementation Plan

### Phase 1: Critical Fixes (30 minutes)

```bash
# 1. Fix old imports in canvod-store
# Edit packages/canvod-store/src/canvod/store/reader.py
# Edit packages/canvod-store/src/canvod/store/manager.py
# Change: from gnssvodpy.utils.date_time import YYYYDOY
# To:     from canvod.utils.tools import YYYYDOY

# 2. Test imports
uv run python -c "from canvod.store import GnssResearchSite"
```

---

### Phase 2: Remove Duplicates (1 hour)

```bash
# 1. Delete duplicate date_utils files
rm packages/canvod-readers/src/canvod/readers/utils/date_utils.py
rm packages/canvod-aux/src/canvod/aux/_internal/date_utils.py

# 2. Update canvod-readers utils __init__.py
# Change local import to: from canvod.utils.tools import YYYYDOY

# 3. Remove _shared directory
rm -rf packages/canvod-readers/src/canvod/readers/_shared

# 4. Run tests
uv run pytest packages/canvod-readers/tests/
uv run pytest packages/canvod-aux/tests/
```

---

### Phase 3: Configuration Cleanup (30 minutes)

```bash
# 1. Edit canvodpy/config/processing.yaml
# Remove credentials.cddis_mail
# Remove credentials.gnss_root_dir

# 2. Update documentation
# Document: "Credentials in .env, other settings in processing.yaml"

# 3. Create .env.example
cat > .env.example << 'EOF'
# NASA CDDIS FTP Authentication (optional)
CDDIS_MAIL=your.email@example.com

# GNSS Data Root Directory
GNSS_ROOT_DIR=/path/to/your/gnss/data
EOF
```

---

## ✅ Success Criteria

After cleanup:

- [ ] No YYYYDOY duplication (only in canvod-utils)
- [ ] No gpsweekday duplication (only in canvod-utils)
- [ ] No old gnssvodpy imports
- [ ] No unused `_shared` directory
- [ ] No configuration field duplication
- [ ] All tests passing
- [ ] Clear documentation on config files

---

## 🔍 Verification Commands

```bash
# Check for YYYYDOY duplication
grep -r "class YYYYDOY" packages/*/src --include="*.py" | wc -l
# Should show: 1 (only in canvod-utils)

# Check for old imports
grep -r "from gnssvodpy" packages/ --include="*.py"
# Should show: empty

# Check for _shared
find packages/ -type d -name "_shared"
# Should show: empty

# Run tests
uv run pytest
```

---

## 📌 Summary

**Found:**
- 5 categories of code duplication
- ~662 lines of duplicated code
- Configuration confusion (2 systems)
- 2 old gnssvodpy imports

**Impact:**
- High maintenance burden
- User confusion
- Risk of divergence

**Solution:**
- 3-phase cleanup plan
- ~2 hours total work
- Clear separation of concerns
- Single source of truth per setting

**Recommendation:** Implement all phases for clean, maintainable codebase.
