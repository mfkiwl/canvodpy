# DatasetMatcher Migration Plan

## Current State

### gnssvodpy has TWO matching components:

**1. File-Level Matching** (`data_handler.py`)
- `DataDirMatcher` - Finds common directories with RINEX files
- `PairDataDirMatcher` - Matches receiver pairs across dates
- `MatchedDirs` - Container for matched directory paths

**2. Dataset-Level Matching** (`processor/matcher.py`)
- `DatasetMatcher` - Temporally aligns loaded datasets
- Uses interpolation strategies
- Matches aux data to RINEX epochs

---

## Migration Strategy

### 1. File-Level Matching → canvod-readers

**Where**: `packages/canvod-readers/src/canvod/readers/matching/`

**Why**: 
- Identifies RINEX files before reading
- First step in the pipeline
- Logically part of data discovery

**Files to create**:
```
canvod-readers/src/canvod/readers/matching/
├── __init__.py
├── dir_matcher.py       # DataDirMatcher, PairDataDirMatcher
└── models.py            # MatchedDirs, PairMatchedDirs
```

**Updates needed**:
- Remove dependency on `gnssvodpy.validation_models`
- Use `canvod.readers.gnss_specs` for date utilities
- Add proper validation with Pydantic

---

### 2. Dataset-Level Matching → WHERE?

**Options**:

**Option A: canvod-aux** ✅ RECOMMENDED
- Uses `create_interpolator_from_attrs` from aux
- Matches aux datasets to RINEX
- Natural fit with auxiliary data pipeline

**Option B: canvodpy core**
- Cross-cutting concern
- Used by both readers and aux
- But adds complexity to core package

**Option C: canvod-readers**
- Could argue it "matches datasets for reading"
- But it operates POST-reading
- Doesn't really fit readers' scope

**Recommendation**: **canvod-aux**

**Where**: `packages/canvod-aux/src/canvod/aux/matching/`

**Files to create**:
```
canvod-aux/src/canvod/aux/matching/
├── __init__.py
└── dataset_matcher.py   # DatasetMatcher
```

**Updates needed**:
- Update imports: `from canvod.aux.interpolation import ...`
- Keep dependency on interpolation (already in canvod-aux)
- Add better error messages

---

## Implementation Steps

### Step 1: Migrate File Matchers to canvod-readers

```python
# canvod-readers/src/canvod/readers/matching/models.py
from dataclasses import dataclass
from pathlib import Path
from canvod.readers.gnss_specs import YYYYDOY  # Or create in readers

@dataclass(frozen=True)
class MatchedDirs:
    """Matched directory paths for canopy and reference receivers."""
    canopy_data_dir: Path
    reference_data_dir: Path  # renamed from sky_data_dir
    yyyydoy: YYYYDOY

@dataclass
class PairMatchedDirs:
    """Matched directories for a receiver pair on a specific date."""
    yyyydoy: YYYYDOY
    pair_name: str
    canopy_receiver: str
    reference_receiver: str
    canopy_data_dir: Path
    reference_data_dir: Path
```

```python
# canvod-readers/src/canvod/readers/matching/dir_matcher.py
from pathlib import Path
from typing import Iterator
from natsort import natsorted
from .models import MatchedDirs, PairMatchedDirs

class DataDirMatcher:
    """
    Match RINEX data directories for canopy and reference receivers.
    
    Scans directory structure to find dates with RINEX files in both
    canopy and reference receiver directories.
    
    Parameters
    ----------
    root : Path
        Root directory containing receiver subdirectories
    reference_pattern : Path
        Path pattern for reference receiver (e.g., "01_reference/01_GNSS/01_raw")
    canopy_pattern : Path
        Path pattern for canopy receiver (e.g., "02_canopy/01_GNSS/01_raw")
    """
    
    def __init__(
        self,
        root: Path,
        reference_pattern: Path = Path("01_reference/01_GNSS/01_raw"),
        canopy_pattern: Path = Path("02_canopy/01_GNSS/01_raw"),
    ):
        self.root = Path(root)
        self.reference_dir = self.root / reference_pattern
        self.canopy_dir = self.root / canopy_pattern
        
        # Validate directories exist
        if not self.root.exists():
            raise FileNotFoundError(f"Root directory not found: {self.root}")
        if not self.reference_dir.exists():
            raise FileNotFoundError(f"Reference directory not found: {self.reference_dir}")
        if not self.canopy_dir.exists():
            raise FileNotFoundError(f"Canopy directory not found: {self.canopy_dir}")
    
    def __iter__(self) -> Iterator[MatchedDirs]:
        """Iterate over matched directory pairs with RINEX files."""
        for date_dir in self.get_common_dates():
            yield MatchedDirs(
                canopy_data_dir=self.canopy_dir / date_dir,
                reference_data_dir=self.reference_dir / date_dir,
                yyyydoy=YYYYDOY.from_yydoy_str(date_dir),
            )
    
    def get_common_dates(self) -> list[str]:
        """Get dates with RINEX files in both receivers."""
        ref_dates = self._get_dates_with_rinex(self.reference_dir)
        can_dates = self._get_dates_with_rinex(self.canopy_dir)
        
        common = ref_dates & can_dates
        common.discard("00000")  # Remove placeholder
        
        return natsorted(list(common))
    
    def _get_dates_with_rinex(self, base_dir: Path) -> set[str]:
        """Find all date directories with RINEX files."""
        dates = set()
        for date_dir in base_dir.iterdir():
            if date_dir.is_dir() and self._has_rinex_files(date_dir):
                dates.add(date_dir.name)
        return dates
    
    def _has_rinex_files(self, directory: Path) -> bool:
        """Check if directory contains RINEX files (*.??o)."""
        return any(directory.glob("*.[0-9][0-9]o"))
```

### Step 2: Migrate DatasetMatcher to canvod-aux

```python
# canvod-aux/src/canvod/aux/matching/__init__.py
from .dataset_matcher import DatasetMatcher

__all__ = ["DatasetMatcher"]
```

```python
# canvod-aux/src/canvod/aux/matching/dataset_matcher.py
import warnings
import xarray as xr
from canvod.aux.interpolation import create_interpolator_from_attrs

class DatasetMatcher:
    """
    Match auxiliary datasets to a reference RINEX dataset temporally.
    
    Handles:
    1. Temporal alignment via interpolation
    2. Different sampling rates
    3. Specialized interpolation strategies
    
    Examples
    --------
    >>> matcher = DatasetMatcher()
    >>> matched = matcher.match_datasets(
    ...     rinex_ds,
    ...     ephemerides=sp3_data,
    ...     clock=clk_data
    ... )
    >>> matched['ephemerides']  # Aligned to RINEX epochs
    """
    
    def match_datasets(
        self,
        reference_ds: xr.Dataset,
        **aux_datasets: xr.Dataset
    ) -> dict[str, xr.Dataset]:
        """
        Match auxiliary datasets to reference dataset epochs.
        
        Parameters
        ----------
        reference_ds : xr.Dataset
            Primary dataset (usually RINEX observations)
        **aux_datasets : dict[str, xr.Dataset]
            Named auxiliary datasets to align
            
        Returns
        -------
        dict[str, xr.Dataset]
            Aligned auxiliary datasets
        """
        self._validate_inputs(reference_ds, aux_datasets)
        
        ref_interval = self._get_temporal_interval(reference_ds)
        matched = self._match_temporal_resolution(
            reference_ds, ref_interval, aux_datasets
        )
        
        return matched
    
    # ... rest of implementation from gnssvodpy
```

### Step 3: Update Imports

**In demo notebooks**:
```python
# OLD
from gnssvodpy.processor.matcher import DatasetMatcher
from gnssvodpy.data_handler.data_handler import MatchedDirs

# NEW
from canvod.aux.matching import DatasetMatcher
from canvod.readers.matching import MatchedDirs, DataDirMatcher
```

**In canvod-aux augmentation**:
```python
# canvod-aux/src/canvod/aux/augmentation.py

# OLD
from gnssvodpy.processor.matcher import DatasetMatcher

# NEW  
from canvod.aux.matching import DatasetMatcher
```

---

## Package Dependencies

After migration:

```
canvod-readers
  ├── No new dependencies
  └── Provides: DataDirMatcher, PairDataDirMatcher, MatchedDirs

canvod-aux
  ├── Uses canvod-readers (for YYYYDOY if needed)
  └── Provides: DatasetMatcher
```

---

## Testing Strategy

### File Matchers (canvod-readers)
```python
def test_data_dir_matcher(demo_root):
    """Test directory matching."""
    matcher = DataDirMatcher(root=demo_root)
    
    matched_list = list(matcher)
    assert len(matched_list) == 2  # DOY 001, 002
    
    first = matched_list[0]
    assert first.yyyydoy.to_str() == "2025001"
    assert first.canopy_data_dir.exists()
    assert first.reference_data_dir.exists()
```

### Dataset Matcher (canvod-aux)
```python
def test_dataset_matcher(rinex_ds, sp3_data, clk_data):
    """Test dataset temporal matching."""
    matcher = DatasetMatcher()
    
    matched = matcher.match_datasets(
        rinex_ds,
        ephemerides=sp3_data,
        clock=clk_data
    )
    
    # Check aligned to same epochs
    assert len(matched['ephemerides'].epoch) == len(rinex_ds.epoch)
    assert len(matched['clock'].epoch) == len(rinex_ds.epoch)
```

---

## Benefits

✅ **Clear separation of concerns**
- File identification → canvod-readers
- Dataset matching → canvod-aux

✅ **No circular dependencies**
- readers → aux (only for YYYYDOY if needed)
- aux doesn't depend on readers for core functionality

✅ **Logical organization**
- File discovery with readers
- Dataset alignment with auxiliary data

✅ **Better naming**
- `DataDirMatcher` clearly indicates directory matching
- `DatasetMatcher` clearly indicates dataset matching

---

## Timeline

1. **Phase 1**: Migrate DataDirMatcher to canvod-readers (1-2 hours)
2. **Phase 2**: Migrate DatasetMatcher to canvod-aux (30 mins)
3. **Phase 3**: Update demo notebooks (30 mins)
4. **Phase 4**: Test and validate (1 hour)

**Total**: ~3-4 hours

---

## Questions for Clarification

1. Should `MatchedDirs.sky_data_dir` be renamed to `reference_data_dir` for consistency?
2. Should `PairDataDirMatcher` also be migrated, or is it Rosalia-specific?
3. Should YYYYDOY stay in gnss_specs or move to a shared location?

---

## Next Steps

Ready to proceed? I can:
1. Create the file matcher in canvod-readers
2. Migrate dataset matcher to canvod-aux
3. Update all imports in demo notebooks
4. Add tests

Let me know which package structure you prefer!
