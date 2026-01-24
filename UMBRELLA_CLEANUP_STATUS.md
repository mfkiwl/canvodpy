# ✅ Umbrella Cleanup Status Report

**Date:** January 24, 2026  
**Action Taken:** Deleted duplicate implementation directories

---

## 📊 BEFORE vs AFTER

### Before Cleanup
```
Total: 14,106 lines

Implementation (duplicates):
├── aux_data/                 3,068 lines
├── rinexreader/              2,005 lines
├── signal_frequency_mapping/ 1,517 lines
├── data_handler/             1,299 lines
├── validation_models/          614 lines
├── position/                   421 lines
├── utils/                      382 lines
└── error_handling/              42 lines
Subtotal: 9,348 lines (deleted ✅)

Orchestration:
├── orchestrator/             3,236 lines
└── workflows/                  341 lines
Subtotal: 3,577 lines (kept ⚠️)

API/Config:
├── api.py                      523 lines
├── globals.py                  196 lines
├── settings.py                 156 lines
├── __init__.py                 122 lines
├── logging/                     93 lines
├── research_sites_config.py     79 lines
├── config/                      11 lines
└── diagnostics/                  1 line
Subtotal: 1,181 lines (kept ⚠️)
```

### After Cleanup
```
Total: 4,758 lines (66% reduction ✅)

Remaining structure:
├── orchestrator/             3,236 lines ⚠️ BROKEN IMPORTS
├── workflows/                  341 lines ⚠️ Needs review
├── api.py                      523 lines ⚠️ Needs import updates
├── globals.py                  196 lines
├── settings.py                 156 lines
├── __init__.py                 122 lines
├── logging/                     93 lines ✅
├── research_sites_config.py     79 lines
├── config/                      11 lines ✅
└── diagnostics/                  1 line ✅
```

---

## 🚨 CRITICAL: Broken Imports Detected

### orchestrator/processor.py (2,384 lines)

**Broken imports found:**
```python
# These modules were deleted!
from canvodpy.aux_data.augmentation import AuxDataAugmenter
from canvodpy.aux_data.clk import ClkFile
from canvodpy.aux_data.pipeline import AuxDataPipeline
from canvodpy.aux_data.sp3 import Sp3File
from canvodpy.data_handler.data_handler import DataDirMatcher, MatchedDirs
from canvodpy.data_handler.rnx_parser import RinexFilesParser
from canvodpy.position.position import ECEFPosition
from canvodpy.position.spherical_coords import ...
from canvodpy.rinexreader.rinex_reader import Rnxv3Obs
from canvodpy.utils.tools import get_version_from_pyproject
```

**Impact:** processor.py is completely broken right now!

### orchestrator/pipeline.py (356 lines)

**Broken imports:**
```python
from canvodpy.data_handler.data_handler import PairDataDirMatcher, PairMatchedDirs
from canvodpy.utils.date_time import YYYYDOY
```

### Other Files

**api.py** - Likely has broken imports too  
**workflows/** - Needs checking

---

## 🔧 REQUIRED FIXES

### Fix 1: Update orchestrator/processor.py Imports

**Replace broken imports with package imports:**

```python
# OLD (broken):
from canvodpy.aux_data.augmentation import AuxDataAugmenter
from canvodpy.aux_data.clk import ClkFile
from canvodpy.aux_data.pipeline import AuxDataPipeline
from canvodpy.aux_data.sp3 import Sp3File

# NEW (correct):
from canvod.aux import AuxDataAugmenter
from canvod.aux.clock import ClkFile  # Check actual location
from canvod.aux import AuxDataPipeline
from canvod.aux.ephemeris import Sp3File  # Check actual location
```

```python
# OLD (broken):
from canvodpy.data_handler.data_handler import DataDirMatcher, MatchedDirs
from canvodpy.data_handler.rnx_parser import RinexFilesParser

# NEW (correct):
# These might be orchestration-specific
# If so, they should stay in orchestrator/
# OR move to canvod-utils if they're reusable
```

```python
# OLD (broken):
from canvodpy.position.position import ECEFPosition
from canvodpy.position.spherical_coords import to_spherical

# NEW (correct):
from canvod.grids import ECEFPosition  # Check if this exists
from canvod.grids import to_spherical
```

```python
# OLD (broken):
from canvodpy.rinexreader.rinex_reader import Rnxv3Obs

# NEW (correct):
from canvod.readers import Rnxv3Obs
```

```python
# OLD (broken):
from canvodpy.utils.tools import get_version_from_pyproject

# NEW (correct):
from canvod.utils import get_version_from_pyproject
# OR if it's orchestrator-specific, keep it local
```

---

### Fix 2: Check What Belongs Where

Some of the imports in orchestrator might be **orchestration logic** that should stay:

**Questions to answer:**

1. **DataDirMatcher, MatchedDirs** - Is this orchestration-specific file matching?
   - If YES → Keep in orchestrator/ (create orchestrator/file_matcher.py)
   - If NO → Move to canvod-utils

2. **RinexFilesParser** - Is this just parsing logic?
   - If YES → Should be in canvod-readers
   - If NO → Keep in orchestrator if it's about coordinating parsing

3. **YYYYDOY date utilities** - Are these general utilities?
   - If YES → Move to canvod-utils
   - If NO → Keep in orchestrator if workflow-specific

---

## 🎯 ACTION PLAN

### Phase 1: Identify What's Actually in Packages (NOW)

Check what's available in packages:

```bash
# What's in canvod-aux?
ls -la packages/canvod-aux/src/canvod/aux/

# What's in canvod-readers?  
ls -la packages/canvod-readers/src/canvod/readers/

# What's in canvod-grids?
ls -la packages/canvod-grids/src/canvod/grids/

# What's in canvod-utils?
ls -la packages/canvod-utils/src/canvod/utils/
```

### Phase 2: Create Import Mapping (NOW)

Create a file `IMPORT_MAPPING.md`:

```markdown
# Import Mapping: Old → New

## aux_data
- AuxDataAugmenter → canvod.aux.???
- ClkFile → canvod.aux.clock.???
- AuxDataPipeline → canvod.aux.???
- Sp3File → canvod.aux.ephemeris.???

## data_handler
- DataDirMatcher → orchestrator/file_matcher.py OR canvod.utils?
- MatchedDirs → orchestrator/file_matcher.py OR canvod.utils?
- RinexFilesParser → canvod.readers.??? OR orchestrator?

## position
- ECEFPosition → canvod.grids.??? OR canvod.aux.position?
- to_spherical → canvod.grids.???

## rinexreader
- Rnxv3Obs → canvod.readers.Rnxv3Obs ✅

## utils
- get_version_from_pyproject → canvod.utils.??? OR keep local?
- YYYYDOY → canvod.utils.??? OR orchestrator?
```

### Phase 3: Update Imports Systematically

For each broken import in orchestrator/:

1. **Check if it exists in packages** → Use package version
2. **Check if it's orchestration-specific** → Keep/move to orchestrator/
3. **Check if it's missing** → Need to implement in appropriate package

### Phase 4: Test

```bash
# Try to import orchestrator
cd canvodpy
uv run python -c "from canvodpy.orchestrator import processor"
# This should work after fixes
```

---

## 📋 IMMEDIATE NEXT STEPS

### Step 1: Inventory Package Contents (5 min)

```bash
# Run this to see what's available:
cd /Users/work/Developer/GNSS/canvodpy

echo "=== canvod-aux contents ===" && \
ls -R packages/canvod-aux/src/canvod/aux/ | grep "\.py$" && \
echo "" && \
echo "=== canvod-readers contents ===" && \
ls -R packages/canvod-readers/src/canvod/readers/ | grep "\.py$" && \
echo "" && \
echo "=== canvod-grids contents ===" && \
ls -R packages/canvod-grids/src/canvod/grids/ | grep "\.py$" && \
echo "" && \
echo "=== canvod-utils contents ===" && \
ls -R packages/canvod-utils/src/canvod/utils/ | grep "\.py$"
```

### Step 2: Create Import Mapping (10 min)

Document where each broken import should come from

### Step 3: Update orchestrator/processor.py (30 min)

Fix all imports systematically

### Step 4: Update orchestrator/pipeline.py (15 min)

Fix remaining imports

### Step 5: Test Imports (5 min)

```bash
uv run python -c "from canvodpy.orchestrator import processor"
```

---

## ✅ What's GOOD

1. ✅ **Deleted 9,348 lines of duplicate code**
2. ✅ **No more confusion about canonical versions**
3. ✅ **Reduced umbrella from 14,106 → 4,758 lines (66% reduction)**
4. ✅ **Logging, config, diagnostics are clean**

---

## ⚠️ What's BROKEN

1. ❌ **orchestrator/processor.py has ~20 broken imports**
2. ❌ **orchestrator/pipeline.py has ~5 broken imports**
3. ❌ **api.py probably has broken imports**
4. ❌ **workflows/ needs checking**
5. ❌ **Cannot import orchestrator right now**

---

## 🎯 SUCCESS CRITERIA

When done:

```bash
# These should all work:
uv run python -c "from canvodpy.orchestrator import processor; print('✅')"
uv run python -c "from canvodpy import Site, Pipeline; print('✅')"
uv run python -c "from canvodpy.api import process_date; print('✅')"

# No references to deleted modules:
grep -r "canvodpy.aux_data" canvodpy/src/
grep -r "canvodpy.rinexreader" canvodpy/src/
grep -r "canvodpy.data_handler" canvodpy/src/
# Should return nothing
```

---

## 📊 Current Stats

```
Umbrella package: 4,758 lines (down from 14,106)
├── Clean: 1,181 lines (api, config, logging) ✅
├── Orchestrator: 3,577 lines (needs import fixes) ⚠️

Reduction: 66% ✅
Broken imports: ~25 ❌
Next step: Fix imports → Use packages
```

---

**Status:** Good progress! Duplicates deleted, but orchestrator needs import updates to use packages.
