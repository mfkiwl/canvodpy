# ✅ Package Restructure: _shared → gnss_specs

**Date**: January 9, 2026  
**Change**: Renamed `_shared/` to `gnss_specs/` for better clarity

---

## Rationale

**Before**: `canvod.readers._shared`
- Vague, ambiguous name
- Doesn't describe contents
- Common anti-pattern (anything can be "shared")

**After**: `canvod.readers.gnss_specs`
- Clear, descriptive name
- Explicitly about GNSS characteristics
- Self-documenting

---

## Changes Made

### 1. Directory Rename
```bash
src/canvod/readers/_shared/ → src/canvod/readers/gnss_specs/
```

### 2. Import Updates (9 files)
**Before**:
```python
from canvod.readers._shared.exceptions import (...)
from canvod.readers._shared.constants import (...)
from canvod.readers._shared.metadata import (...)
from canvod.readers._shared.models import (...)
from canvod.readers._shared.signals import SignalIDMapper
from canvod.readers._shared.utils import (...)
```

**After**:
```python
from canvod.readers.gnss_specs.exceptions import (...)
from canvod.readers.gnss_specs.constants import (...)
from canvod.readers.gnss_specs.metadata import (...)
from canvod.readers.gnss_specs.models import (...)
from canvod.readers.gnss_specs.signals import SignalIDMapper
from canvod.readers.gnss_specs.utils import (...)
```

### 3. Files Updated
- ✅ `src/canvod/readers/__init__.py`
- ✅ `src/canvod/readers/base.py`
- ✅ `src/canvod/readers/rinex/v3_04.py`
- ✅ `tests/test_meta.py`
- ✅ `tests/test_shared.py`
- ✅ `tests/test_rinex_v3.py`
- ✅ `CODE_VERIFICATION_REPORT.md`
- ✅ `MIGRATION_STATUS.md`
- ✅ `SIGNAL_MAPPING_ANALYSIS.md`

### 4. Syntax Validation
All files compile successfully:
```
✅ constants.py
✅ exceptions.py
✅ metadata.py
✅ models.py
✅ signals.py
✅ utils.py
✅ base.py
✅ v3_04.py
```

---

## New Structure

```
src/canvod/readers/
├── __init__.py
├── base.py                      # Abstract base classes
│
├── gnss_specs/                   # Core GNSS characteristics
│   ├── __init__.py
│   ├── constants.py             # GNSS constants & units
│   ├── exceptions.py            # GNSS-specific exceptions
│   ├── metadata.py              # CF-compliant metadata
│   ├── models.py                # Pydantic validation models
│   ├── signals.py               # Signal mapping & band properties
│   └── utils.py                 # Utility functions
│
└── rinex/                       # RINEX format readers
    ├── __init__.py
    └── v3_04.py                 # RINEX v3.04 reader
```

---

## Module Contents

### `gnss_specs/` - What's Inside

**constants.py** (74 lines)
- Unit registry (UREG) with custom GNSS units (dBHz, dB)
- Physical constants (speed of light)
- RINEX parsing constants
- Sampling intervals for different receivers

**exceptions.py** (49 lines)
- `RinexError` - Base exception
- `MissingEpochError` - Missing epoch data
- `IncompleteEpochError` - Incomplete epoch record
- `InvalidEpochError` - Invalid epoch format
- `CorruptedFileError` - File corruption
- `FileNotExistError` - File not found
- `AttributeOverrideError` - Attribute override protection

**metadata.py** (229 lines)
- Coordinate metadata (epoch, sv, sid, band, system, etc.)
- Observable metadata (SNR, C/N0, Pseudorange, Phase, Doppler, etc.)
- Data type definitions
- Global attribute templates
- CF Convention compliance

**models.py** (369 lines)
- `Observation` - Single GNSS observation
- `Satellite` - Satellite with observations
- `Epoch` - Epoch with satellites
- `RnxObsFileModel` - File validation
- `RnxVersion3Model` - Version validation
- `Rnxv3ObsEpochRecordLineModel` - Epoch line parsing
- `Rnxv3ObsEpochRecord` - Complete epoch record
- `VodDataValidator` - VOD data validation

**signals.py** (117 lines)
- `SignalIDMapper` - Maps RINEX codes to Signal IDs
- Band frequency definitions
- System-to-band mappings
- Overlapping group definitions
- Signal ID creation/parsing

**utils.py** (61 lines)
- `get_version_from_pyproject()` - Extract package version
- `rinex_file_hash()` - Compute file hash
- `isfloat()` - Check if string is float

---

## Import Examples

### For Users
```python
# High-level API (unchanged)
from canvod.readers import Rnxv3Reader

# Use the reader
reader = Rnxv3Reader()
ds = reader.read("file.24o")
```

### For Developers
```python
# Access core GNSS utilities
from canvod.readers.gnss_specs import constants, exceptions, models
from canvod.readers.gnss_specs.signals import SignalIDMapper

# Use unit registry
ureg = constants.UREG
frequency = 1575.42 * ureg.MHz

# Use signal mapper
mapper = SignalIDMapper()
sid = mapper.create_signal_id("G01", "G01|S1C")  # → "G01|L1|C"
```

---

## Benefits

1. **Clarity**: Name explicitly describes GNSS-specific core functionality
2. **Discoverability**: Easier to find GNSS characteristics and utilities
3. **Documentation**: Self-documenting module structure
4. **Professional**: Follows Python package naming best practices
5. **Maintainability**: Clear separation of concerns

---

## Backward Compatibility

⚠️ **Breaking Change**: This is a breaking change for any code importing from `_shared`

**Migration**:
```python
# Old (breaks)
from canvod.readers._shared import constants

# New (works)
from canvod.readers.gnss_specs import constants
```

However, since this package hasn't been released yet, no external code is affected.

---

## Testing

All tests updated and passing:
```bash
pytest tests/test_meta.py -v
# Tests import structure, verifies gnss_specs is accessible

pytest tests/test_shared.py -v
# Now tests gnss_specs modules (file should be renamed to test_gnss_specs.py)
```

---

## Future Considerations

### Potential Future Names
If `gnss_specs` becomes too broad, could split into:
- `gnss_specs/` - Keep for fundamental constants, exceptions
- `gnss_signal/` - Move signal mapping here
- `gnss_models/` - Move Pydantic models here

But for now, `gnss_specs` is appropriate and sufficient.

### Test File Rename
Consider renaming:
- `tests/test_shared.py` → `tests/test_gnss_specs.py`

For consistency with the new module name.

---

**Status**: ✅ Complete  
**Verification**: ✅ All files compile, imports work  
**Next**: Implement complete signal mapping in gnss_specs/signals.py
