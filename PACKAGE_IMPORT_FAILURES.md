# 🚨 ROOT CAUSE: Package Import Failures

## Problem Summary

Tests fail NOT because of umbrella cleanup, but because **packages have broken imports within their own code**.

---

## ✅ What We Fixed

### 1. Created Missing Namespace Package Files

All packages now have `src/canvod/__init__.py`:

```bash
✅ canvod-aux/src/canvod/__init__.py
✅ canvod-grids/src/canvod/__init__.py
✅ canvod-readers/src/canvod/__init__.py
✅ canvod-store/src/canvod/__init__.py
✅ canvod-viz/src/canvod/__init__.py
✅ canvod-vod/src/canvod/__init__.py
```

**Content:**
```python
"""canvod namespace package"""
__path__ = __import__('pkgutil').extend_path(__path__, __name__)
```

**Result:** Namespace packages now work correctly!

---

## ❌ What's Still Broken

### Real Error: Broken Imports in Package Code

When trying to import `canvod.aux`:

```python
❌ canvod.aux failed: cannot import name 'AGGREGATE_GLONASS_FDMA' 
   from 'canvod.readers.gnss_specs.constants'
```

**Location:** `packages/canvod-readers/src/canvod/readers/rinex/v3_04.py`

**What it tries to import:**
```python
from canvod.readers.gnss_specs.constants import (
    AGGREGATE_GLONASS_FDMA,  # ❌ Doesn't exist!
    ...
)
```

**What constants.py says:**
```python
# Comment in constants.py:
# - AGGREGATE_GLONASS_FDMA → processing.aggregate_glonass_fdma
```

**Problem:** The constant was moved/renamed but imports weren't updated!

---

## 🔍 How to Find All Broken Imports

### Step 1: Try to Import Each Package

```bash
cd /Users/work/Developer/GNSS/canvodpy

# Test each package
for pkg in aux readers grids store viz vod utils; do
  echo "Testing canvod.$pkg..."
  ~/.local/bin/uv run python -c "import canvod.$pkg; print('✅')" 2>&1 || echo "❌ FAILED"
done
```

### Step 2: Find the Actual Errors

```bash
# Get detailed error for each broken package
~/.local/bin/uv run python -c "
try:
    import canvod.aux
except Exception as e:
    print(f'canvod.aux: {e}')

try:
    import canvod.readers
except Exception as e:
    print(f'canvod.readers: {e}')
    
# ... etc for each package
"
```

---

## 🔧 Known Broken Imports

### 1. canvod-readers

**File:** `packages/canvod-readers/src/canvod/readers/rinex/v3_04.py`

**Broken import:**
```python
from canvod.readers.gnss_specs.constants import (
    AGGREGATE_GLONASS_FDMA,  # ❌ Missing
    ...
)
```

**Fix:** Either:
- A) Define `AGGREGATE_GLONASS_FDMA` in constants.py
- B) Import from new location: `from canvod.readers.processing import aggregate_glonass_fdma`
- C) Remove if not needed

### 2. Likely More in Other Packages

Need to test each package individually to find all broken imports.

---

## 🎯 Action Plan

### Phase 1: Inventory Broken Imports (15 min)

```bash
#!/bin/bash
cd /Users/work/Developer/GNSS/canvodpy

echo "=== Testing All Package Imports ===" > BROKEN_IMPORTS.txt
echo "" >> BROKEN_IMPORTS.txt

for pkg in aux readers grids store viz vod utils; do
  echo "Testing canvod.$pkg..." >> BROKEN_IMPORTS.txt
  
  error=$(~/.local/bin/uv run python -c "import canvod.$pkg" 2>&1)
  
  if [ $? -eq 0 ]; then
    echo "✅ canvod.$pkg works" >> BROKEN_IMPORTS.txt
  else
    echo "❌ canvod.$pkg BROKEN" >> BROKEN_IMPORTS.txt
    echo "$error" >> BROKEN_IMPORTS.txt
  fi
  
  echo "" >> BROKEN_IMPORTS.txt
done

cat BROKEN_IMPORTS.txt
```

### Phase 2: Fix Each Broken Import (varies)

For each error found:

1. **Identify what's missing** (e.g., `AGGREGATE_GLONASS_FDMA`)
2. **Find where it should come from** (search codebase)
3. **Update the import** or **add the missing definition**
4. **Test the fix**

### Phase 3: Verify Tests Pass (5 min)

```bash
# After fixes, test each package
cd packages/canvod-aux
~/.local/bin/uv run pytest

cd ../canvod-readers
~/.local/bin/uv run pytest

# ... etc
```

---

## 📊 Current Status

### Namespace Packages
✅ All packages have proper `canvod/__init__.py`  
✅ Namespace mechanism works correctly  
✅ Packages are installed in workspace

### Package Imports
❌ canvod.aux - Broken (depends on canvod.readers)  
❌ canvod.readers - Broken (AGGREGATE_GLONASS_FDMA missing)  
⚠️ canvod.grids - Unknown  
⚠️ canvod.store - Unknown  
⚠️ canvod.viz - Unknown  
⚠️ canvod.vod - Unknown  
⚠️ canvod.utils - Unknown  

### Test Status
❌ Cannot run tests until imports are fixed  
❌ Orchestrator cannot import packages  
❌ API cannot import packages

---

## 🔍 Verification Commands

### Check Namespace Packages Work
```bash
~/.local/bin/uv run python -c "
import sys
sys.path.insert(0, 'packages/canvod-aux/src')
import canvod
print('Namespace paths:', canvod.__path__)
"
```

**Expected:** List of all package src/canvod directories ✅

### Check Individual Package
```bash
~/.local/bin/uv run python -c "import canvod.readers"
```

**Expected:** Clean import with no errors

### Check Specific Import
```bash
~/.local/bin/uv run python -c "
from canvod.readers.gnss_specs.constants import AGGREGATE_GLONASS_FDMA
print('Found:', AGGREGATE_GLONASS_FDMA)
"
```

**Expected:** Either the constant value or ImportError if truly missing

---

## 💡 Why This Happened

### Likely Sequence of Events

1. ✅ Originally developed constants in constants.py
2. ⚠️ Decided to reorganize code
3. ⚠️ Moved some constants (e.g., AGGREGATE_GLONASS_FDMA)
4. ⚠️ Left comments in constants.py about where they went
5. ❌ **Forgot to update imports in consuming code**
6. ❌ Tests weren't run after refactoring
7. 🚨 **Now everything is broken**

This is separate from the umbrella cleanup issue!

---

## ✅ Next Steps

1. **Run the inventory script** to find ALL broken imports
2. **Fix each broken import** systematically
3. **Test each package** individually
4. **Then** fix orchestrator imports (separate issue)

---

## 📝 Summary

**Not a namespace package issue** ✅ (fixed)  
**Not a test import issue** ✅ (tests import correctly)  
**IS a broken package code issue** ❌ (need to fix)

**The packages themselves have broken imports that need fixing before anything else can work.**
