# 🎯 ACTION PLAN: Eliminating ALL gnssvodpy Dependencies

**Current Status:** 59 gnssvodpy imports across monorepo  
**Target:** 0 gnssvodpy imports  
**Challenge:** Packages importing from application (architecture violation)

---

## 📊 Current Dependency Count

| Location | Imports | Priority |
|----------|---------|----------|
| canvod-store | 24 | 🔴 **CRITICAL** |
| canvod-aux | 15 | 🔴 **CRITICAL** |
| demo files | 18 | 🟡 **UPDATE NEEDED** |
| canvod-readers | 2 | 🟢 **MINOR** |
| **TOTAL** | **59** | ❌ **NOT INDEPENDENT** |

---

## 🎯 Three Approaches (Choose One)

### Option A: Create canvod-core (Proper Architecture) ⭐ RECOMMENDED

**What:** Create a shared foundation package for common utilities

**Pros:**
- ✅ Proper architecture (libraries don't depend on applications)
- ✅ Single source of truth for shared code
- ✅ Clean dependency flow
- ✅ Maintainable long-term

**Cons:**
- ⚠️ Requires creating new package
- ⚠️ ~2 hours of work
- ⚠️ Need to update all imports

**Steps:**
1. Create `packages/canvod-core`
2. Move shared code from canvodpy/gnssvodpy
3. Update all package imports
4. Update canvodpy imports
5. Update demos

**Estimated time:** 2-3 hours

---

### Option B: Copy Code into Each Package (Quick & Dirty)

**What:** Duplicate necessary utilities in each package

**Pros:**
- ✅ Quick to implement
- ✅ Packages become truly independent
- ✅ No new package needed

**Cons:**
- ❌ Code duplication
- ❌ Harder to maintain
- ❌ Inconsistencies may develop

**Steps:**
1. Copy `globals.py` into each package that needs it
2. Copy `settings.py` into each package that needs it
3. Copy other utilities as needed
4. Update imports within each package

**Estimated time:** 1 hour

---

### Option C: Use Parameters Instead of Imports (Functional)

**What:** Pass configuration as function parameters

**Pros:**
- ✅ No shared state
- ✅ Explicit dependencies
- ✅ Testable

**Cons:**
- ❌ Verbose API
- ❌ Breaking changes to existing code
- ❌ Doesn't solve all cases (e.g., logging)

**Example:**
```python
# Before:
from gnssvodpy.globals import AGENCY
def download_sp3():
    agency = AGENCY
    
# After:
def download_sp3(agency: str = "COD"):
    # Use parameter
```

**Estimated time:** 3-4 hours (many API changes)

---

## 🏗️ Detailed Plan for Option A (Recommended)

### Phase 1: Create canvod-core Package

```bash
cd /Users/work/Developer/GNSS/canvodpy/packages

# 1. Create structure
mkdir -p canvod-core/src/canvod/core/{constants,config,logging,utils,signals}

# 2. Copy shared modules
cp ../../gnssvodpy/src/gnssvodpy/globals.py \
   canvod-core/src/canvod/core/constants.py

cp ../../gnssvodpy/src/gnssvodpy/settings.py \
   canvod-core/src/canvod/core/settings.py

cp ../../gnssvodpy/src/gnssvodpy/research_sites_config.py \
   canvod-core/src/canvod/core/config.py

cp -r ../../gnssvodpy/src/gnssvodpy/logging \
   canvod-core/src/canvod/core/

cp -r ../../gnssvodpy/src/gnssvodpy/utils \
   canvod-core/src/canvod/core/

cp -r ../../gnssvodpy/src/gnssvodpy/signal_frequency_mapping \
   canvod-core/src/canvod/core/signals

# 3. Create pyproject.toml
cat > canvod-core/pyproject.toml << 'EOF'
[project]
name = "canvod-core"
version = "0.1.0"
description = "Core utilities for CANVOD GNSS analysis"
requires-python = ">=3.10"
dependencies = [
    "numpy",
    "pandas",
    "pydantic",
    "pint",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
EOF

# 4. Create __init__.py
cat > canvod-core/src/canvod/core/__init__.py << 'EOF'
"""Core utilities for CANVOD packages."""

from canvod.core.constants import *
from canvod.core.settings import get_settings
from canvod.core.config import RESEARCH_SITES

__all__ = ['get_settings', 'RESEARCH_SITES']
EOF
```

### Phase 2: Update Package Imports

```bash
cd /Users/work/Developer/GNSS/canvodpy/packages

# canvod-store
cd canvod-store/src/canvod/store
find . -name "*.py" -exec sed -i '' \
  's/from gnssvodpy\.globals/from canvod.core.constants/g' {} +
find . -name "*.py" -exec sed -i '' \
  's/from gnssvodpy\.signal_frequency_mapping/from canvod.core.signals/g' {} +
find . -name "*.py" -exec sed -i '' \
  's/from gnssvodpy\.logging/from canvod.core.logging/g' {} +
find . -name "*.py" -exec sed -i '' \
  's/from gnssvodpy\.utils/from canvod.core.utils/g' {} +
find . -name "*.py" -exec sed -i '' \
  's/from gnssvodpy\.research_sites_config/from canvod.core.config/g' {} +

# canvod-aux
cd ../../canvod-aux/src/canvod/aux
find . -name "*.py" -exec sed -i '' \
  's/from gnssvodpy\.globals/from canvod.core.constants/g' {} +
find . -name "*.py" -exec sed -i '' \
  's/from gnssvodpy\.settings/from canvod.core.settings/g' {} +
find . -name "*.py" -exec sed -i '' \
  's/from gnssvodpy\.utils/from canvod.core.utils/g' {} +

# canvod-readers
cd ../../canvod-readers/src/canvod/readers
# Just update docstrings (no actual imports)
find . -name "*.py" -exec sed -i '' \
  's/Migrated from gnssvodpy/Migrated to canvod/g' {} +
```

### Phase 3: Update canvodpy

```python
# canvodpy also uses canvod-core
# Update canvodpy/src/canvodpy/__init__.py to import from canvod.core
```

### Phase 4: Update Demos

```bash
cd /Users/work/Developer/GNSS/canvodpy/demo

# Update all demo files to use canvodpy API instead of gnssvodpy
# Replace gnssvodpy imports with canvodpy imports
find . -name "*.py" -exec sed -i '' \
  's/from gnssvodpy\.icechunk_manager\.manager import GnssResearchSite/from canvodpy import Site/g' {} +
find . -name "*.py" -exec sed -i '' \
  's/from gnssvodpy\.processor\.pipeline_orchestrator import PipelineOrchestrator/from canvodpy import Pipeline/g' {} +
find . -name "*.py" -exec sed -i '' \
  's/from gnssvodpy\.globals import KEEP_RNX_VARS/from canvod.core import KEEP_RNX_VARS/g' {} +
```

### Phase 5: Update Workspace

```toml
# pyproject.toml (workspace root)
[tool.uv.workspace]
members = [
    "canvodpy",
    "packages/canvod-readers",
    "packages/canvod-aux",
    "packages/canvod-grids",
    "packages/canvod-viz",
    "packages/canvod-store",
    "packages/canvod-vod",
    "packages/canvod-core",  # NEW!
]
```

### Phase 6: Verify

```bash
cd /Users/work/Developer/GNSS/canvodpy
grep -r "from gnssvodpy" --include="*.py" . | grep -v __pycache__

# Should output: (empty)
# Target: 0 imports
```

---

## 🚦 Decision Matrix

| Criteria | Option A (canvod-core) | Option B (duplicate) | Option C (parameters) |
|----------|------------------------|----------------------|-----------------------|
| **Proper architecture** | ✅ Yes | ⚠️ Partial | ✅ Yes |
| **Maintainability** | ✅ High | ❌ Low | ⚠️ Medium |
| **Implementation time** | ⚠️ 2-3 hours | ✅ 1 hour | ❌ 3-4 hours |
| **Future-proof** | ✅ Yes | ❌ No | ✅ Yes |
| **Clean code** | ✅ Yes | ❌ Duplicated | ✅ Yes |
| **Breaking changes** | ⚠️ Moderate | ⚠️ Moderate | ❌ Many |

---

## 🎯 Recommended: Option A

**Why?**
1. Proper architecture (Sollbruchstellen principle)
2. Single source of truth
3. Maintainable long-term
4. Only ~2 hours of work
5. Professional solution

**When to choose others:**
- **Option B:** If you need something working in 1 hour
- **Option C:** If you want functional purity (but takes longer)

---

## 📋 Quick Start Commands

**If you choose Option A:**

```bash
cd /Users/work/Developer/GNSS/canvodpy

# See detailed commands in Phase 1-6 above
# Or run this automated script:

# Create canvod-core package
mkdir -p packages/canvod-core/src/canvod/core
# ... follow Phase 1 steps
```

**If you choose Option B:**

```bash
# Copy globals.py into each package
cp canvodpy/src/canvodpy/globals.py packages/canvod-store/src/canvod/store/
cp canvodpy/src/canvodpy/globals.py packages/canvod-aux/src/canvod/aux/
# ... etc
```

---

## ✅ Success Criteria

After completion:
- [ ] `grep -r "from gnssvodpy" --include="*.py" . | wc -l` returns **0**
- [ ] All packages build successfully
- [ ] All tests pass
- [ ] Demo runs without gnssvodpy
- [ ] Architecture diagram updated
- [ ] Documentation updated

---

## 🎬 What Should We Do Now?

**I recommend Option A** (canvod-core). 

Shall I proceed with:
1. Creating the canvod-core package structure?
2. Moving shared code into it?
3. Updating all imports?

Or would you prefer a different approach?
