# canvod-readers Migration Plan

## Current Analysis

### Source Files (gnssvodpy)
```
rinexreader/
├── rinex_reader.py         (1730 lines) - Main RINEX v3 reader
├── metadata.py             (275 lines)  - Dataset metadata
└── __init__.py             (empty)

data_handler/
├── rnx_parser.py           (902 lines)  - RINEX parsing logic  
├── data_handler.py         (397 lines)  - Data handling
└── __init__.py             (empty)

signal_frequency_mapping/
├── signal_mapping.py       - GNSS signal/frequency mapping
├── bands.py                - Band definitions
├── gnss_systems.py         - GNSS system definitions
└── satellite CSVs          - Satellite data

Total: ~3,300 lines + dependencies
```

### External Dependencies
```
georinex      - RINEX file parsing
numpy         - Numerical operations
pint          - Physical units
pydantic      - Data validation
pytz          - Timezone handling
xarray        - Labeled arrays
```

### Internal Dependencies (to migrate/adapt)
```
error_handling/           → Move to readers (custom exceptions)
globals.py                → Move constants to readers
logging/                  → Optional (or use standard logging)
validation_models/        → Move Pydantic models to readers
utils/tools.py            → Move utilities to readers
signal_frequency_mapping/ → Core part of readers
```

### Dependencies to Remove (for now)
```
icechunk_manager/         → belongs in canvod-store (future)
```

---

## Migration Strategy

### Phase 1: Foundation (Self-contained modules)
**Goal**: Set up basic structure with no internal dependencies

1. ✅ Package structure already exists
2. Create basic modules:
   - `metadata.py` - Dataset metadata definitions
   - `exceptions.py` - RINEX-specific exceptions
   - `constants.py` - RINEX constants and globals
   - `models.py` - Pydantic validation models

### Phase 2: Signal Mapping (Independent)
**Goal**: GNSS signal/frequency mapping

3. Migrate signal_frequency_mapping:
   - `signal_mapping.py`
   - `bands.py`
   - `gnss_systems.py`
   - Satellite CSV files

### Phase 3: Utilities
**Goal**: Helper functions

4. Create `utils.py`:
   - `rinex_file_hash()`
   - `get_version_from_pyproject()`
   - Date/time utilities
   - File management helpers

### Phase 4: Core Reader
**Goal**: Main RINEX reading functionality

5. Migrate `rinex_reader.py`:
   - `Rnxv3Header` class
   - `Rnxv3Obs` class (main reader)
   - Update all imports to use canvod.readers
   - Remove icechunk_manager dependencies (add TODO)

### Phase 5: Parser
**Goal**: RINEX parsing logic

6. Migrate `rnx_parser.py`:
   - Parser classes
   - Update imports

### Phase 6: Data Handler
**Goal**: Data handling utilities

7. Migrate `data_handler.py`:
   - Data manipulation classes
   - Update imports

### Phase 7: Polish
**Goal**: Complete, tested package

8. Create proper `__init__.py`:
   - Export main classes
   - Public API definition

9. Add dependencies to `pyproject.toml`

10. Write/migrate tests

11. Update documentation

---

## Dependency Resolution

### Simple Migrations (Copy + Update imports)
```python
# OLD
from gnssvodpy.rinexreader.metadata import CN0_METADATA

# NEW
from canvod.readers.metadata import CN0_METADATA
```

### Create New Modules
```python
# constants.py - Extract from globals.py
EPOCH_RECORD_INDICATOR = ">"
KEEP_RNX_VARS = ["time", "sv", ...]
COMPRESSION = {"zlib": True, "complevel": 9}
UREG = pint.UnitRegistry()
AGGREGATE_GLONASS_FDMA = True

# exceptions.py - Extract from error_handling
class IncompleteEpochError(Exception): ...
class InvalidEpochError(Exception): ...
class MissingEpochError(Exception): ...
```

### Remove/Defer Dependencies
```python
# REMOVE (belongs in canvod-store)
from gnssvodpy.icechunk_manager.preprocessing import IcechunkPreprocessor

# REPLACE WITH
# TODO: Move to canvod-store when available
# from canvod.store import IcechunkPreprocessor
```

### Logging Strategy
```python
# OLD
from gnssvodpy.logging.context import get_logger

# NEW (use standard logging)
import logging
logger = logging.getLogger(__name__)
```

---

## File Mapping

### Old → New Structure
```
gnssvodpy/rinexreader/               → canvod-readers/src/canvod/readers/
├── rinex_reader.py                  → rinex_v3.py
├── metadata.py                      → metadata.py
└── __init__.py                      → __init__.py

gnssvodpy/data_handler/              → canvod-readers/src/canvod/readers/
├── rnx_parser.py                    → parser.py
└── data_handler.py                  → data_handler.py

gnssvodpy/signal_frequency_mapping/  → canvod-readers/src/canvod/readers/signals/
├── signal_mapping.py                → mapping.py
├── bands.py                         → bands.py
├── gnss_systems.py                  → systems.py
└── *.csv                            → data/*.csv

NEW FILES (extract from old codebase):
├── constants.py                     ← from gnssvodpy/globals.py
├── exceptions.py                    ← from gnssvodpy/error_handling/
├── models.py                        ← from gnssvodpy/validation_models/
└── utils.py                         ← from gnssvodpy/utils/
```

---

## API Design

### Public API (`canvod.readers.__init__.py`)
```python
"""GNSS data format readers."""

from canvod.readers.rinex_v3 import Rnxv3Obs, Rnxv3Header
from canvod.readers.parser import RinexParser
from canvod.readers.exceptions import (
    IncompleteEpochError,
    InvalidEpochError,
    MissingEpochError,
)

__all__ = [
    "Rnxv3Obs",
    "Rnxv3Header",
    "RinexParser",
    "IncompleteEpochError",
    "InvalidEpochError",
    "MissingEpochError",
]

__version__ = "0.1.0"
```

### Usage Example
```python
from canvod.readers import Rnxv3Obs

# Read RINEX file
reader = Rnxv3Obs(filepath="/path/to/file.rnx")
data = reader.to_xarray()
```

---

## Testing Strategy

### Unit Tests
```
tests/
├── test_rinex_v3.py         - Main reader tests
├── test_parser.py           - Parser tests
├── test_signals.py          - Signal mapping tests
├── test_models.py           - Pydantic model validation
├── test_exceptions.py       - Exception handling
└── fixtures/                - Test data
    └── sample.rnx           - Sample RINEX file
```

### Integration Tests
- Read actual RINEX files
- Validate output format
- Check metadata completeness

---

## Dependencies to Add

### Runtime Dependencies
```toml
[project]
dependencies = [
    "georinex>=1.16.0",
    "numpy>=1.24.0",
    "pint>=0.23",
    "pydantic>=2.5.0",
    "pytz>=2023.3",
    "xarray>=2023.12.0",
]
```

### Development Dependencies
```toml
[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "ruff>=0.14",
    "ty>=0.0.9",
]
```

---

## Execution Plan

### Step-by-step Checklist

- [ ] **Step 1**: Create foundation modules
  - [ ] `constants.py`
  - [ ] `exceptions.py`
  - [ ] `models.py`
  - [ ] `metadata.py`

- [ ] **Step 2**: Migrate signal mapping
  - [ ] Create `signals/` directory
  - [ ] Migrate mapping.py
  - [ ] Migrate bands.py
  - [ ] Migrate systems.py
  - [ ] Copy CSV data files

- [ ] **Step 3**: Create utilities
  - [ ] `utils.py` with helper functions

- [ ] **Step 4**: Migrate core reader
  - [ ] `rinex_v3.py` (from rinex_reader.py)
  - [ ] Update all imports
  - [ ] Remove/defer store dependencies

- [ ] **Step 5**: Migrate parser
  - [ ] `parser.py` (from rnx_parser.py)

- [ ] **Step 6**: Migrate data handler
  - [ ] `data_handler.py`

- [ ] **Step 7**: Polish package
  - [ ] Create proper `__init__.py`
  - [ ] Add dependencies to pyproject.toml
  - [ ] Write tests
  - [ ] Update README

- [ ] **Step 8**: Verify & Test
  - [ ] Run tests
  - [ ] Check imports work
  - [ ] Build package
  - [ ] Test installation

---

## Notes

### Things to Keep
- All Pydantic models (excellent validation)
- Error handling structure
- Metadata definitions
- Signal mapping logic

### Things to Simplify
- Logging (use standard library)
- Remove icechunk dependencies (add to canvod-store later)
- Simplify file paths (relative to package)

### Things to Improve
- Add type hints where missing
- Improve docstrings
- Add examples in docstrings
- Better error messages

---

## Timeline Estimate

- **Phase 1** (Foundation): 1-2 hours
- **Phase 2** (Signal Mapping): 30 min
- **Phase 3** (Utilities): 30 min
- **Phase 4** (Core Reader): 2-3 hours
- **Phase 5** (Parser): 1 hour
- **Phase 6** (Data Handler): 1 hour
- **Phase 7** (Polish): 1-2 hours

**Total**: ~8-10 hours of focused work

---

## Success Criteria

✅ Package builds successfully
✅ All imports work correctly
✅ Can read RINEX files
✅ Tests pass
✅ No external gnssvodpy dependencies
✅ Proper namespace package structure
✅ Documentation complete
