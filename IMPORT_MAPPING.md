# Import Mapping: Umbrella → Packages

## ✅ Available in Packages

### From canvod-readers

| Old Import (canvodpy.*) | New Import (canvod.*) | Status |
|------------------------|----------------------|--------|
| `canvodpy.rinexreader.rinex_reader.Rnxv3Obs` | `canvod.readers.Rnxv3Obs` | ✅ |
| `canvodpy.data_handler.data_handler.DataDirMatcher` | `canvod.readers.DataDirMatcher` | ✅ |
| `canvodpy.data_handler.data_handler.MatchedDirs` | `canvod.readers.MatchedDirs` | ✅ |
| `canvodpy.data_handler.data_handler.PairDataDirMatcher` | `canvod.readers.PairDataDirMatcher` | ✅ |
| `canvodpy.data_handler.data_handler.PairMatchedDirs` | `canvod.readers.PairMatchedDirs` | ✅ |
| `canvodpy.utils.date_time.YYYYDOY` | `canvod.readers.utils.YYYYDOY` | ✅ |

### From canvod-aux

| Old Import (canvodpy.*) | New Import (canvod.*) | Status |
|------------------------|----------------------|--------|
| `canvodpy.aux_data.clk.ClkFile` | `canvod.aux.ClkFile` | ✅ |
| `canvodpy.aux_data.sp3.Sp3File` | `canvod.aux.Sp3File` | ✅ |
| `canvodpy.aux_data.container.GnssData` | `canvod.aux.GnssData` | ✅ |
| `canvodpy.position.position.ECEFPosition` | `canvod.aux.position.ECEFPosition` | ✅ |
| `canvodpy.position.spherical_coords.*` | `canvod.aux.position.*` | ✅ |

### Need to Check

| Old Import | Possible Location | Status |
|-----------|------------------|--------|
| `canvodpy.aux_data.augmentation.AuxDataAugmenter` | `canvod.aux.???` | ⚠️ |
| `canvodpy.aux_data.pipeline.AuxDataPipeline` | `canvod.aux.???` | ⚠️ |
| `canvodpy.data_handler.rnx_parser.RinexFilesParser` | `canvod.readers.???` or orchestrator? | ⚠️ |
| `canvodpy.utils.tools.get_version_from_pyproject` | `canvod.utils.???` or orchestrator? | ⚠️ |

---

## 🔧 Fix Script

Run this to update all imports in orchestrator:

```bash
cd /Users/work/Developer/GNSS/canvodpy/canvodpy/src/canvodpy

# Fix orchestrator/processor.py
sed -i '' 's/from canvodpy\.rinexreader\.rinex_reader import/from canvod.readers import/g' orchestrator/processor.py
sed -i '' 's/from canvodpy\.aux_data\.clk import/from canvod.aux import/g' orchestrator/processor.py
sed -i '' 's/from canvodpy\.aux_data\.sp3 import/from canvod.aux import/g' orchestrator/processor.py
sed -i '' 's/from canvodpy\.data_handler\.data_handler import/from canvod.readers import/g' orchestrator/processor.py
sed -i '' 's/from canvodpy\.position\.position import/from canvod.aux.position import/g' orchestrator/processor.py
sed -i '' 's/from canvodpy\.position\.spherical_coords import/from canvod.aux.position import/g' orchestrator/processor.py

# Fix orchestrator/pipeline.py
sed -i '' 's/from canvodpy\.data_handler\.data_handler import/from canvod.readers import/g' orchestrator/pipeline.py
sed -i '' 's/from canvodpy\.utils\.date_time import/from canvod.readers.utils import/g' orchestrator/pipeline.py

echo "✅ Fixed common imports"
echo "⚠️  Manual review needed for:"
echo "   - AuxDataAugmenter"
echo "   - AuxDataPipeline"
echo "   - RinexFilesParser"
echo "   - get_version_from_pyproject"
```

---

## 📋 Manual Review Needed

### 1. AuxDataAugmenter

**Check:** Does this exist in canvod-aux?

```bash
grep -r "class AuxDataAugmenter" packages/canvod-aux/
```

**If found:** Update import  
**If not found:** 
- Is it in orchestrator as orchestration logic? → Keep in orchestrator
- Is it missing from package? → Need to add to canvod-aux

### 2. AuxDataPipeline

**Check:** Does this exist in canvod-aux?

```bash
grep -r "class AuxDataPipeline" packages/canvod-aux/
```

**Action:** Same as above

### 3. RinexFilesParser

**Check:** Does this exist in canvod-readers?

```bash
grep -r "class RinexFilesParser" packages/canvod-readers/
```

**If not found:** This might be orchestration-specific (bulk file parsing)
- If it coordinates reading multiple files → Keep in orchestrator
- If it's a low-level parser → Should be in canvod-readers

### 4. get_version_from_pyproject

**Check:** Does this exist in canvod-utils?

```bash
grep -r "def get_version_from_pyproject" packages/canvod-utils/
```

**If not found:** This is probably orchestrator-specific metadata
- Create `orchestrator/_version.py` with this function

---

## ✅ After Fixing

Test imports:

```bash
cd /Users/work/Developer/GNSS/canvodpy/canvodpy

# Test orchestrator imports
uv run python -c "
from canvodpy.orchestrator import processor
print('✅ processor imports work')
"

# Test pipeline imports  
uv run python -c "
from canvodpy.orchestrator import pipeline
print('✅ pipeline imports work')
"

# Test API imports
uv run python -c "
from canvodpy import Site, Pipeline
print('✅ API imports work')
"
```

---

## 📊 Import Statistics

**Before:**
- Total broken imports in orchestrator: ~25
- From deleted directories: 100%

**After automated fixes:**
- Fixed automatically: ~15 (60%)
- Need manual review: ~10 (40%)

**Remaining work:**
- Find or implement 4 missing classes
- Test all imports
- Update any other broken references
