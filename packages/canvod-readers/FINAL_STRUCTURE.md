# ✅ Final Package Structure

**Date**: January 9, 2026  
**Module Name**: `canvod.readers.gnss_specs`

---

## 📁 Final Structure

```
src/canvod/readers/
├── __init__.py                  # Main package interface
├── base.py                      # Abstract base classes (GNSSReader, RinexReader)
│
├── gnss_specs/                  # 🎯 GNSS specifications & characteristics
│   ├── __init__.py              # "GNSS specifications and core characteristics"
│   ├── constants.py             # 74 lines - Unit registry, physical constants
│   ├── exceptions.py            # 49 lines - GNSS-specific exceptions
│   ├── metadata.py              # 229 lines - CF-compliant metadata definitions
│   ├── models.py                # 369 lines - Pydantic validation models
│   ├── signals.py               # 117 lines - Signal mapping & band properties
│   └── utils.py                 # 61 lines - Utility functions
│
└── rinex/                       # RINEX format readers
    ├── __init__.py
    └── v3_04.py                 # 1,450 lines - RINEX v3.04 reader
```

**Total**: 2,368 lines of core code

---

## 📦 Import Examples

### High-Level API (User-facing)
```python
from canvod.readers import Rnxv3Reader

reader = Rnxv3Reader()
dataset = reader.read("file.24o")
```

### GNSS Specifications (Developer-facing)
```python
from canvod.readers.gnss_specs import constants, exceptions, models
from canvod.readers.gnss_specs.signals import SignalIDMapper

# Use GNSS constants
ureg = constants.UREG
frequency = 1575.42 * ureg.MHz

# Use signal mapper
mapper = SignalIDMapper()
signal_id = mapper.create_signal_id("G01", "G01|S1C")
```

---

## 🎯 Module Purpose: `gnss_specs`

**Name Rationale**: 
- "specs" = specifications
- Contains GNSS signal specifications, band definitions, metadata specifications
- Clear, professional, concise

**Contains**:
1. **Physical specifications**: Frequencies, bandwidths, wavelengths
2. **Signal specifications**: Band mappings, signal IDs, overlapping groups
3. **Data specifications**: Metadata schemas, coordinate definitions
4. **Format specifications**: RINEX parsing rules, data types
5. **Validation specifications**: Pydantic models for data validation

---

## ✅ Verification

All syntax valid:
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

All imports updated:
```python
# Old: from canvod.readers._shared import (...)
# New: from canvod.readers.gnss_specs import (...)
```

---

## 🚀 Next Step

**Implement complete signal mapping in `gnss_specs/signals.py`**

Current status: Has wrong imports from gnssvodpy
Target: ~200 lines with complete GNSS band specifications

Ready to proceed with signal mapping implementation?
