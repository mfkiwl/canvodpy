# Build Backend & Namespace Package Decisions

## Final Configuration

### Build Backend: `setuptools`
**Why not uv_build or hatchling?**
- `uv_build`: Doesn't handle PEP 420 namespace packages well
- `hatchling`: Complex config needed for namespace packages
- **`setuptools`**: Best support for PEP 420 implicit namespace packages

**Configuration:**
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]
namespaces = false  # Using PEP 420 implicit
```

### Namespace Packages: PEP 420 Implicit

**OLD Python 2 Style (REMOVED):**
```python
# src/canvod/__init__.py
__path__ = __import__('pkgutil').extend_path(__path__, __name__)
```

**MODERN Python 3.3+ Style (PEP 420):**
```
src/
  canvod/              # NO __init__.py file!
    readers/
      __init__.py     # Regular package
```

**Benefits:**
- ✅ Simpler - no special code needed
- ✅ Standard Python 3.3+
- ✅ Works across all packages automatically
- ✅ Better tool support

## What We Have Now

### Structure:
```
packages/
  canvod-readers/
    src/
      canvod/                    # NO __init__.py (namespace)
        readers/
          __init__.py           # Regular package
```

### Imports That Work:
```python
from canvod.readers import Rnxv3Obs
from canvod.aux import AuxData
from canvod.grids import HemiGrid
import canvodpy
```

### All Tools Working:
```bash
uv sync                          # ✅ Works
just check                       # ✅ Works  
python -c "import canvod.readers"  # ✅ Works
```

## Deviation from TUW-GEO Template

**TUW-GEO uses:** `uv_build`
**We use:** `setuptools`

**Reason:** TUW-GEO template creates regular packages (`my_package`), not namespace packages (`canvod.readers`). For namespace packages, setuptools has the best support.

**Other TUW-GEO standards we DO follow:**
- ✅ Ruff with ALL rules
- ✅ ty type checker
- ✅ Python 3.13
- ✅ Modern dev tooling
- ✅ Workspace structure
