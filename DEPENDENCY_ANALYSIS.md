# 🚨 CRITICAL: Complete Dependency Analysis

**Status:** ⚠️ **INCOMPLETE** - Packages still depend on gnssvodpy!

---

## 📊 Current State

### gnssvodpy Import Count by Location

| Location | Imports | Status |
|----------|---------|--------|
| **packages/canvod-store** | 24 | ❌ Most critical |
| **packages/canvod-aux** | 15 | ❌ Critical |
| **packages/canvod-readers** | 2 | ⚠️ Minor |
| **demo/** files | 18 | ⚠️ Need updating |
| **TOTAL** | **59** | ❌ **NOT INDEPENDENT** |

---

## 🎯 What Needs To Happen

### Critical Issues

1. **canvod-store imports from gnssvodpy** ❌
   - `from gnssvodpy.globals import ...`
   - `from gnssvodpy.signal_frequency_mapping import ...`
   - `from gnssvodpy.logging import ...`
   - `from gnssvodpy.utils import ...`
   - `from gnssvodpy.research_sites_config import ...`

2. **canvod-aux imports from gnssvodpy** ❌
   - `from gnssvodpy.globals import ...`
   - `from gnssvodpy.settings import ...`
   - `from gnssvodpy.data_handler import ...`
   - `from gnssvodpy.utils import ...`

3. **canvod-readers imports from gnssvodpy** ⚠️
   - Minor docstring references

4. **Demo files use gnssvodpy API** ⚠️
   - Should use canvodpy API instead

---

## 🏗️ Architecture Problem

### Current (Broken!)

```
canvod-store/
  └─ from gnssvodpy.globals import ... ❌
      └─ CIRCULAR! Should not depend on application

canvod-aux/
  └─ from gnssvodpy.settings import ... ❌
      └─ CIRCULAR! Should not depend on application

canvodpy/
  └─ from canvod.store import ... ✅
  └─ from canvod.aux import ... ✅
```

**Problem:** Packages (libraries) importing from gnssvodpy/canvodpy (applications)!

### Correct Architecture

```
canvod-* packages (libraries - self-contained)
  ├─ canvod-store (Icechunk storage)
  ├─ canvod-aux (Auxiliary data)
  ├─ canvod-readers (RINEX reading)
  ├─ canvod-grids (Hemisphere grids)
  ├─ canvod-viz (Visualization)
  └─ canvod-vod (VOD calculations)
    ↓ NO IMPORTS FROM CANVODPY OR GNSSVODPY
External packages only
  └─ xarray, numpy, scipy, etc.
```

Then:

```
canvodpy (application/umbrella)
  ├─ from canvod.store import ... ✅
  ├─ from canvod.aux import ... ✅
  ├─ from canvod.readers import ... ✅
  └─ Contains application logic ✅
```

**Packages must be self-contained libraries!**

---

## 🔧 Solution Strategy

### Option 1: Move Shared Code to Packages (Recommended)

**Move these from canvodpy/gnssvodpy into packages:**

1. **Create canvod-core** for shared utilities:
   - `globals.py` → `canvod.core.constants`
   - `settings.py` → `canvod.core.settings`
   - `research_sites_config.py` → `canvod.core.config`
   - `utils/` → `canvod.core.utils`
   - `logging/` → `canvod.core.logging`

2. **Update package imports:**
   ```python
   # Before (broken):
   from gnssvodpy.globals import UREG
   
   # After (correct):
   from canvod.core import UREG
   ```

3. **Update canvodpy:**
   ```python
   # canvodpy also uses canvod-core
   from canvod.core import UREG, get_settings
   ```

### Option 2: Duplicate Shared Code (Quick Fix)

Copy necessary files into each package that needs them:
- Copy `globals.py` → Each package
- Copy `settings.py` → Each package
- etc.

**Downside:** Code duplication, harder to maintain

### Option 3: Parameters Instead of Imports

Instead of:
```python
from gnssvodpy.globals import AGENCY
agency = AGENCY
```

Do:
```python
def process(agency: str = "COD"):
    # Use parameter
```

**Downside:** More verbose API

---

## 📋 Detailed Breakdown

### canvod-store needs:

From gnssvodpy:
- `globals` (AGGREGATE_GLONASS_FDMA, KEEP_SIDS, etc.)
- `signal_frequency_mapping` (SignalIDMapper, GPS, GLONASS, etc.)
- `logging.context` (get_logger)
- `utils.tools` (get_version_from_pyproject)
- `utils.date_time` (YYYYDOY)
- `research_sites_config` (RESEARCH_SITES)

**Solution:** Create `canvod-core` with these shared utilities

### canvod-aux needs:

From gnssvodpy:
- `globals` (AGENCY, CLK_FILE_PATH, SP3_FILE_PATH, FTP_SERVER, etc.)
- `settings` (get_settings)
- `data_handler` (MatchedDirs - type hints only)
- `utils.date_time` (YYYYDOY)

**Solution:** 
- Move to `canvod-core` OR
- Accept as parameters OR
- Use TYPE_CHECKING for type hints only

### canvod-readers needs:

From gnssvodpy:
- Docstring references only (can just update docs)

**Solution:** Update docstrings

---

## 🎯 Recommended Action Plan

### Phase 1: Create canvod-core (Shared Foundation)

```bash
cd packages
mkdir -p canvod-core/src/canvod/core

# Copy shared modules
cp -r ../canvodpy/src/canvodpy/globals.py canvod-core/src/canvod/core/constants.py
cp -r ../canvodpy/src/canvodpy/settings.py canvod-core/src/canvod/core/settings.py
cp -r ../canvodpy/src/canvodpy/research_sites_config.py canvod-core/src/canvod/core/config.py
cp -r ../canvodpy/src/canvodpy/utils canvod-core/src/canvod/core/utils
cp -r ../canvodpy/src/canvodpy/logging canvod-core/src/canvod/core/logging
cp -r ../canvodpy/src/canvodpy/signal_frequency_mapping canvod-core/src/canvod/core/signals
```

### Phase 2: Update Package Imports

```bash
# In canvod-store, canvod-aux, canvod-readers:
sed -i '' 's/from gnssvodpy\.globals/from canvod.core.constants/g' **/*.py
sed -i '' 's/from gnssvodpy\.settings/from canvod.core.settings/g' **/*.py
sed -i '' 's/from gnssvodpy\.logging/from canvod.core.logging/g' **/*.py
sed -i '' 's/from gnssvodpy\.utils/from canvod.core.utils/g' **/*.py
sed -i '' 's/from gnssvodpy\.signal_frequency_mapping/from canvod.core.signals/g' **/*.py
sed -i '' 's/from gnssvodpy\.research_sites_config/from canvod.core.config/g' **/*.py
```

### Phase 3: Update canvodpy

```python
# canvodpy also imports from canvod.core
from canvod.core import UREG, get_settings
from canvod.core.config import RESEARCH_SITES
```

### Phase 4: Update Demos

```python
# Old (broken):
from gnssvodpy.icechunk_manager.manager import GnssResearchSite

# New (correct):
from canvodpy import Site  # Use high-level API
```

---

## ⚠️ Why This Matters

**Current state violates Sollbruchstellen principle:**

- Packages should be **independent libraries**
- Packages should NOT import from applications
- **Library → Application is wrong direction!**

**Correct dependency flow:**

```
Application (canvodpy)
  ↓ imports from
Packages (canvod-*)
  ↓ imports from  
Core (canvod-core - shared utilities)
  ↓ imports from
External (numpy, xarray, etc.)
```

---

## 🚦 Next Steps

**Immediate:**
1. Create `canvod-core` package
2. Move shared code (globals, settings, utils, logging)
3. Update all package imports
4. Update canvodpy imports
5. Update demo files
6. Verify: `grep -r "from gnssvodpy" . | wc -l` → should be 0

**Result:** True independence with proper architecture!

---

## 📊 Success Criteria

- [ ] canvod-core created with shared utilities
- [ ] canvod-store: 0 gnssvodpy imports
- [ ] canvod-aux: 0 gnssvodpy imports  
- [ ] canvod-readers: 0 gnssvodpy imports
- [ ] canvodpy: imports from canvod.core
- [ ] demos: use canvodpy API
- [ ] Total gnssvodpy imports: **0**
- [ ] Architecture: correct dependency flow

---

**Current Status:** ⚠️ Architecture violation - needs comprehensive fix!
