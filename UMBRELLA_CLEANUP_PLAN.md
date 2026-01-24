# Umbrella Package Cleanup Plan

## 🎯 Decision: **Packages are canonical, exclusively**

**Action:** Delete all implementation logic from umbrella, keep ONLY orchestration/API/logging.

---

## 🗑️ WHAT TO DELETE (10,900 lines)

### Delete Immediately - Complete Directories

```bash
cd /Users/work/Developer/GNSS/canvodpy/canvodpy/src/canvodpy

# Delete implementation logic (these are in packages)
rm -rf aux_data/                    # 3,068 lines → Use canvod.aux
rm -rf rinexreader/                 # 2,005 lines → Use canvod.readers
rm -rf signal_frequency_mapping/    # 1,517 lines → Use canvod.readers.gnss_specs
rm -rf data_handler/                # 1,299 lines → Use canvod.readers
rm -rf validation_models/           #   614 lines → Use canvod.utils or packages
rm -rf position/                    #   421 lines → Use canvod.grids
rm -rf utils/                       #   382 lines → Use canvod.utils
rm -rf error_handling/              #    42 lines → Use canvod.utils

# Total deleted: ~9,350 lines
```

---

## ⚠️ WHAT TO REVIEW

### orchestrator/ (3,236 lines) - NEEDS AUDIT

**Action:** Review each file to determine if it's:
- ✅ **Pure orchestration** (coordinates packages) → Keep
- ❌ **Implementation logic** (algorithms) → Delete or move to package

```bash
cd orchestrator/
ls -la
# Files:
# - interpolator.py
# - matcher.py  
# - pipeline.py
# - processor.py
```

**Questions to ask for each file:**
1. Does it implement algorithms? → Move to appropriate package
2. Does it coordinate packages? → Keep in umbrella
3. Does it have business logic? → Move to appropriate package

### workflows/ (341 lines) - NEEDS AUDIT

Similar review - is this orchestration or implementation?

---

## ✅ WHAT TO KEEP

### Core Umbrella Files (Keep & Update)

```bash
# Keep these files:
__init__.py           # Update imports to use packages
api.py                # Update imports to use packages  
logging/              # Logging setup (OK as-is)
config/               # Config loader (OK as-is)

# Review & possibly simplify:
globals.py            # Should use canvod.utils.config instead?
settings.py           # Should use canvod.utils.config instead?
research_sites_config.py  # Move to canvod.utils.config?
```

---

## 🔄 UPDATE STRATEGY

### Step 1: Create Backup

```bash
cd /Users/work/Developer/GNSS/canvodpy
cp -r canvodpy canvodpy.backup
echo "✅ Backup created"
```

### Step 2: Delete Implementation Directories

```bash
cd canvodpy/src/canvodpy

# Delete directories with implementation logic
rm -rf aux_data
rm -rf rinexreader
rm -rf signal_frequency_mapping
rm -rf data_handler
rm -rf validation_models
rm -rf position
rm -rf utils
rm -rf error_handling

echo "✅ Deleted 9,350 lines of implementation logic"
```

### Step 3: Update __init__.py to Import from Packages

```python
# canvodpy/__init__.py

"""
canVODpy - GNSS Vegetation Optical Depth Analysis

High-level API that orchestrates canvod-* packages.
All implementation logic is in the packages.
"""

# Import from packages (canonical versions)
from canvod.readers import Rnxv3Obs
from canvod.readers.gnss_specs import SIGNAL_MAPPING, GNSS_BANDS

from canvod.aux import (
    augment_with_ephemeris,
    augment_with_clock,
    EphemerisContainer,
    ClockContainer,
)

from canvod.grids import (
    HemiGrid,
    create_healpix_grid,
    to_spherical,  # Replaces position/
)

from canvod.vod import calculate_vod

from canvod.store import IcechunkStore

from canvod.viz import plot_vod_map

from canvod.utils import (
    # Replaces utils/
    date_to_doy,
    validate_rinex_path,
)
from canvod.utils.config import load_config

# Local modules (orchestration only)
from canvodpy.logging import setup_logging

# API will be updated after orchestrator review
# from canvodpy.api import VODPipeline, run_analysis

__version__ = "0.1.0"

__all__ = [
    # Readers
    "Rnxv3Obs",
    "SIGNAL_MAPPING",
    "GNSS_BANDS",
    # Aux
    "augment_with_ephemeris",
    "augment_with_clock",
    "EphemerisContainer",
    "ClockContainer",
    # Grids
    "HemiGrid",
    "create_healpix_grid",
    "to_spherical",
    # VOD
    "calculate_vod",
    # Store
    "IcechunkStore",
    # Viz
    "plot_vod_map",
    # Utils
    "date_to_doy",
    "validate_rinex_path",
    "load_config",
    # Logging
    "setup_logging",
    # API (after review)
    # "VODPipeline",
    # "run_analysis",
]
```

### Step 4: Update api.py to Import from Packages

```python
# canvodpy/api.py

"""
High-level API for common VOD analysis workflows.

This module ONLY coordinates packages - no implementations.
"""

from pathlib import Path
from typing import Optional

from canvod.readers import Rnxv3Obs
from canvod.aux import augment_with_ephemeris, augment_with_clock
from canvod.grids import HemiGrid
from canvod.vod import calculate_vod
from canvod.store import IcechunkStore
from canvod.utils.config import load_config

from canvodpy.logging import setup_logging


class VODPipeline:
    """
    High-level pipeline for VOD analysis.
    
    Coordinates packages - contains NO algorithm implementations.
    All logic is in canvod.* packages.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize pipeline with configuration."""
        self.config = load_config(config_path) if config_path else None
        
        if self.config:
            setup_logging(self.config.get('log_level', 'INFO'))
        
        # Components from packages
        self.reader = Rnxv3Obs()
        self.grid = None  # Initialized on demand
        self.store = None  # Initialized on demand
    
    def process_rinex(
        self,
        rinex_path: Path,
        output_path: Optional[Path] = None
    ):
        """
        Process RINEX file through complete VOD pipeline.
        
        Orchestration only - delegates to packages.
        """
        # Read (from canvod.readers)
        obs_data = self.reader.read(rinex_path)
        
        # Augment (from canvod.aux)
        augmented = augment_with_ephemeris(obs_data, self.config)
        augmented = augment_with_clock(augmented, self.config)
        
        # Calculate VOD (from canvod.vod)
        vod_result = calculate_vod(augmented)
        
        # Store (from canvod.store)
        if output_path:
            if not self.store:
                self.store = IcechunkStore(output_path)
            self.store.save(vod_result)
        
        return vod_result


def run_vod_analysis(
    rinex_path: Path,
    config_path: Optional[Path] = None,
    output_path: Optional[Path] = None
):
    """
    Convenience function for one-shot VOD analysis.
    
    Args:
        rinex_path: Path to RINEX observation file
        config_path: Optional path to configuration file
        output_path: Optional path for output storage
    
    Returns:
        VOD analysis results
    """
    pipeline = VODPipeline(config_path)
    return pipeline.process_rinex(rinex_path, output_path)
```

### Step 5: Review orchestrator/ - Determine What to Keep

Create audit file for each module in orchestrator/:

```bash
# For each file in orchestrator/, ask:
cd canvodpy/src/canvodpy/orchestrator

for file in *.py; do
    echo "=== $file ==="
    echo "Question: Does this coordinate packages OR implement algorithms?"
    echo "Lines: $(wc -l < $file)"
    echo ""
done
```

### Step 6: Update pyproject.toml Dependencies

```toml
# canvodpy/pyproject.toml

[project]
dependencies = [
    # All packages are dependencies
    "canvod-readers>=0.1.0",
    "canvod-aux>=0.1.0",
    "canvod-grids>=0.1.0",
    "canvod-vod>=0.1.0",
    "canvod-store>=0.1.0",
    "canvod-viz>=0.1.0",
    "canvod-utils>=0.1.0",
]

[tool.uv.workspace]
members = ["packages/*"]

[tool.uv.sources]
# Use workspace versions
canvod-readers = { workspace = true }
canvod-aux = { workspace = true }
canvod-grids = { workspace = true }
canvod-vod = { workspace = true }
canvod-store = { workspace = true }
canvod-viz = { workspace = true }
canvod-utils = { workspace = true }
```

---

## 🧪 TESTING STRATEGY

### After Each Deletion

```bash
# Test that packages still work independently
cd packages/canvod-readers
uv run pytest

cd ../canvod-aux
uv run pytest

# etc.
```

### After All Updates

```bash
# Test umbrella imports
cd canvodpy
uv run python -c "
from canvodpy import Rnxv3Obs, augment_with_ephemeris, HemiGrid
print('✅ All imports work')
"

# Test API
uv run python -c "
from canvodpy import VODPipeline
pipeline = VODPipeline()
print('✅ API works')
"
```

---

## 📊 BEFORE/AFTER

### Before (Current - WRONG)
```
canvodpy/src/canvodpy/
├── aux_data/           3,068 lines ❌
├── rinexreader/        2,005 lines ❌
├── signal_mapping/     1,517 lines ❌
├── data_handler/       1,299 lines ❌
├── validation_models/    614 lines ❌
├── position/             421 lines ❌
├── utils/                382 lines ❌
├── orchestrator/       3,236 lines ⚠️
├── workflows/            341 lines ⚠️
├── api.py                523 lines ⚠️
├── logging/               93 lines ✅
└── config/                11 lines ✅

Total: 14,106 lines
```

### After (Goal - RIGHT)
```
canvodpy/src/canvodpy/
├── __init__.py         ~150 lines ✅ (imports from packages)
├── api.py              ~200 lines ✅ (coordination only)
├── orchestrator/       ~500 lines ✅ (pure coordination)
├── logging/             ~93 lines ✅ (cross-package concern)
└── config/              ~11 lines ✅ (delegates to canvod-utils)

Total: ~950 lines
```

**Reduction: 14,106 → ~950 lines (93% reduction!)**

---

## ✅ SUCCESS CRITERIA

### 1. Packages Work Independently

```bash
pip install canvod-readers
python -c "from canvod.readers import Rnxv3Obs; print('✅')"

pip install canvod-aux  
python -c "from canvod.aux import augment_with_ephemeris; print('✅')"
```

### 2. Umbrella Only Coordinates

```bash
# All imports should come from packages
grep -r "from canvod\." canvodpy/src/canvodpy/*.py
# Should see ONLY imports, no implementations

# No duplicate implementations
find canvodpy/src/canvodpy -name "augmentation.py"
# Should return nothing
```

### 3. Dependency Graph Clean

```bash
python scripts/analyze_dependencies.py --format report
# Should show:
# - canvodpy depends on ALL packages
# - Packages depend on NOTHING from canvodpy
```

---

## 🚀 EXECUTION STEPS

Execute in this order:

### TODAY:
1. ✅ Create backup
2. ✅ Delete implementation directories
3. ✅ Update __init__.py with package imports
4. ✅ Test basic imports work

### NEXT:
5. ⚠️ Audit orchestrator/ (which files are pure coordination?)
6. ⚠️ Update api.py (use package imports)
7. ⚠️ Review globals.py, settings.py (move to canvod-utils?)
8. ⚠️ Update pyproject.toml dependencies

### VERIFY:
9. ✅ Test all packages independently
10. ✅ Test umbrella API
11. ✅ Run dependency analysis
12. ✅ Update documentation

---

## 🎯 IMMEDIATE COMMAND SEQUENCE

```bash
#!/bin/bash
# Execute this to clean umbrella package

cd /Users/work/Developer/GNSS/canvodpy

# 1. Backup
echo "Creating backup..."
cp -r canvodpy canvodpy.backup.$(date +%Y%m%d_%H%M%S)

# 2. Delete implementation directories
echo "Deleting implementation logic..."
cd canvodpy/src/canvodpy
rm -rf aux_data
rm -rf rinexreader
rm -rf signal_frequency_mapping
rm -rf data_handler
rm -rf validation_models
rm -rf position
rm -rf utils
rm -rf error_handling

echo "✅ Deleted ~9,350 lines of duplicate code"

# 3. Count remaining lines
echo ""
echo "Remaining lines in umbrella:"
find . -name "*.py" -type f | xargs wc -l | tail -1

# 4. List what's left
echo ""
echo "Remaining structure:"
find . -type d -maxdepth 1 | tail -n +2 | sort

echo ""
echo "✅ Cleanup phase 1 complete!"
echo "⚠️  Next: Review orchestrator/ and workflows/"
```

---

**Ready to execute? This will reduce umbrella from 14,106 lines to ~4,750 lines immediately, with further reduction after orchestrator review.**
