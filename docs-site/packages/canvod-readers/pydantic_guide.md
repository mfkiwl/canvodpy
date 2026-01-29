# Pydantic Guide

This page provides a comprehensive guide to Pydantic usage in canvod-readers. We'll cover why Pydantic is essential, how it's used throughout the codebase, and best practices for working with Pydantic models.

## Why Pydantic?

### The Problem: Fragile Parsing

Traditional RINEX parsing code is error-prone:

```python
# ❌ Traditional approach - fragile and error-prone
def parse_header_old(lines):
    version = float(lines[0][:9])  # What if it's not a number?
    file_type = lines[0][20]        # What if line is too short?

    # Silent failures
    if version < 3:
        print("Warning: old version")  # Just a warning?

    # No validation
    obs_types = lines[5].split()  # What if missing?

    return {
        'version': version,
        'type': file_type,
        'obs_types': obs_types
    }
```

**Problems**:
1. ❌ No type checking
2. ❌ Silent failures
3. ❌ No validation
4. ❌ Runtime errors discovered late
5. ❌ Hard to test
6. ❌ No IDE support

### The Solution: Pydantic Models

```python
# ✅ Pydantic approach - robust and validated
from pydantic import BaseModel, field_validator

class Rnxv3ObsHeader(BaseModel):
    rinex_version: float
    rinex_type: str
    obs_types: dict[str, list[str]]

    @field_validator('rinex_version')
    def check_version(cls, v):
        if not (3.0 <= v < 4.0):
            raise ValueError(f"Expected RINEX v3, got {v}")
        return v

    @field_validator('rinex_type')
    def check_type(cls, v):
        if v != 'O':
            raise ValueError(f"Expected observation file, got {v}")
        return v
```

**Benefits**:
1. ✅ Automatic type checking
2. ✅ Explicit validation rules
3. ✅ Clear error messages
4. ✅ Errors caught immediately
5. ✅ Easy to test
6. ✅ Full IDE autocomplete

## Core Pydantic Concepts

### 1. BaseModel Basics

Every Pydantic model inherits from `BaseModel`:

```python
from pydantic import BaseModel

class Observation(BaseModel):
    """Type-safe observation model."""

    value: float
    lli: int | None = None
    ssi: int | None = None
```

**What you get automatically**:
- `__init__()` with type checking
- `model_validate()` for validation
- `model_dump()` for serialization
- `__repr__()` for debugging
- `__eq__()` for comparison

### 2. Type Annotations

Pydantic uses Python type hints:

```python
from datetime import datetime
from pathlib import Path

class Rnxv3Obs(BaseModel):
    # Required fields
    fpath: Path

    # Optional fields with defaults
    header: Rnxv3ObsHeader | None = None
    timestamp: datetime | None = None

    # Collections
    satellites: list[Satellite] = []
    obs_types: dict[str, list[str]] = {}

    # Union types (Python 3.10+)
    interval: int | float = 30.0
```

### 3. Automatic Validation

Validation happens automatically on initialization:

```python
# ✅ Valid
obs = Observation(value=45.2, lli=0, ssi=7)

# ❌ Invalid type
obs = Observation(value="not a number")
# ValidationError: Input should be a valid number

# ❌ Out of range (custom validator)
obs = Observation(value=45.2, lli=10)
# ValidationError: LLI must be 0-9
```

### 4. Field Validators

Custom validation logic:

```python
from pydantic import field_validator, Field

class Satellite(BaseModel):
    sv: str = Field(..., description="Satellite vehicle ID")

    @field_validator('sv')
    @classmethod
    def check_sv_format(cls, v: str) -> str:
        """Validate satellite vehicle ID format."""
        if len(v) != 3:
            raise ValueError(f"SV must be 3 chars, got {len(v)}")

        system = v[0]
        if system not in 'GRECJIS':
            raise ValueError(f"Invalid system: {system}")

        prn = v[1:]
        if not prn.isdigit():
            raise ValueError(f"PRN must be numeric: {prn}")

        return v
```

### 5. Model Validators

Validate multiple fields together:

```python
from pydantic import model_validator

class Rnxv3ObsHeaderFileVars(BaseModel):
    sampling_interval: Quantity
    rnx_file_dump_interval: Quantity
    epoch_records_indeces: list[int]

    @model_validator(mode='after')
    def check_intervals(self):
        """Validate epoch intervals consistency."""
        total_time = (
            len(self.epoch_records_indeces) *
            self.sampling_interval.m_as(ureg.seconds)
        )
        expected_time = self.rnx_file_dump_interval.m_as(ureg.seconds)

        if total_time != expected_time:
            raise MissingEpochError(
                f"Total sampling time ({total_time}s) != "
                f"dump interval ({expected_time}s). "
                f"Missing epochs detected."
            )

        return self
```

**Note**: In Pydantic v2.12+, `mode='after'` validators should be **instance methods** (using `self`), not class methods (using `cls, values`).

### 6. Configuration

Control model behavior with `model_config`:

```python
from pydantic import ConfigDict

class Rnxv3Obs(BaseModel):
    """Immutable reader with arbitrary types."""

    model_config = ConfigDict(
        frozen=True,              # Immutable after creation
        arbitrary_types_allowed=True,  # Allow non-Pydantic types
        validate_assignment=True, # Validate on attribute assignment
        str_strip_whitespace=True,  # Strip whitespace from strings
    )

    fpath: Path  # Path is "arbitrary type"
```

## Real-World Examples

### Example 1: Header Parsing

Complete header model with validation:

```python
from pydantic import BaseModel, field_validator
from datetime import datetime

class Rnxv3ObsHeader(BaseModel):
    """RINEX v3 observation header.

    Automatically validates all fields according to
    RINEX v3.04 specification.
    """

    # Version and type (required)
    rinex_version: float
    rinex_type: str
    sat_system: str | None = None

    # Program info
    pgm: str | None = None
    run_by: str | None = None
    date: str | None = None

    # Station info
    marker_name: str | None = None
    marker_number: str | None = None

    # Observation types (required)
    obs_types: dict[str, list[str]]

    # Time info
    time_of_first_obs: datetime | None = None
    interval: float | None = None

    @field_validator('rinex_version')
    @classmethod
    def check_version(cls, v: float) -> float:
        """Ensure RINEX v3.x."""
        if not (3.0 <= v < 4.0):
            raise ValueError(
                f"Expected RINEX v3.xx, got {v}. "
                f"Use Rnxv2Obs for v2 or Rnxv4Obs for v4."
            )
        return v

    @field_validator('rinex_type')
    @classmethod
    def check_type(cls, v: str) -> str:
        """Ensure observation file."""
        if v != 'O':
            raise ValueError(
                f"Expected observation file (type='O'), got '{v}'. "
                f"This reader only handles observation files."
            )
        return v

    @field_validator('obs_types')
    @classmethod
    def check_obs_types(cls, v: dict[str, list[str]]) -> dict:
        """Validate observation type structure."""
        if not v:
            raise ValueError("No observation types defined in header")

        valid_obs_chars = {'C', 'L', 'D', 'S'}
        for system, obs_list in v.items():
            if system not in 'GRECJIS':
                raise ValueError(f"Invalid GNSS system: {system}")

            for obs in obs_list:
                if len(obs) != 3:
                    raise ValueError(
                        f"Observation code must be 3 chars: {obs}"
                    )
                if obs[0] not in valid_obs_chars:
                    raise ValueError(
                        f"Invalid observation type '{obs[0]}' in {obs}. "
                        f"Must be one of: {valid_obs_chars}"
                    )

        return v
```

**Usage**:

```python
# ✅ Valid header
header = Rnxv3ObsHeader(
    rinex_version=3.04,
    rinex_type='O',
    obs_types={'G': ['C1C', 'L1C', 'S1C']}
)

# ❌ Invalid version
header = Rnxv3ObsHeader(
    rinex_version=2.11,  # Wrong version
    rinex_type='O',
    obs_types={'G': ['C1', 'L1']}
)
# ValidationError: Expected RINEX v3.xx, got 2.11

# ❌ Invalid observation type
header = Rnxv3ObsHeader(
    rinex_version=3.04,
    rinex_type='O',
    obs_types={'G': ['X1Y']}  # Invalid type
)
# ValidationError: Invalid observation type 'X' in X1Y
```

### Example 2: Nested Models

Models can contain other models:

```python
class Observation(BaseModel):
    """Single observation value."""
    value: float
    lli: int | None = None
    ssi: int | None = None

    @field_validator('lli', 'ssi')
    @classmethod
    def check_flags(cls, v: int | None) -> int | None:
        """Validate flag range."""
        if v is not None and not (0 <= v <= 9):
            raise ValueError(f"Flag must be 0-9 or None, got {v}")
        return v


class Satellite(BaseModel):
    """Satellite with observations."""
    sv: str
    observations: dict[str, Observation] = {}

    def add_observation(self, obs_code: str, obs: Observation) -> None:
        """Add observation with validation."""
        self.observations[obs_code] = obs


class Rnxv3ObsEpochRecord(BaseModel):
    """Complete epoch record."""
    timestamp: datetime
    epoch_flag: int
    num_satellites: int
    satellites: list[Satellite] = []

    @field_validator('epoch_flag')
    @classmethod
    def check_epoch_flag(cls, v: int) -> int:
        """Validate epoch flag."""
        if not (0 <= v <= 6):
            raise ValueError(f"Epoch flag must be 0-6, got {v}")
        return v

    @model_validator(mode='after')
    def check_satellite_count(self):
        """Validate satellite count matches."""
        actual = len(self.satellites)
        expected = self.num_satellites

        if actual != expected:
            raise ValueError(
                f"Expected {expected} satellites, got {actual}"
            )

        return self
```

**Usage**:

```python
# Build nested structure
obs1 = Observation(value=45.2, lli=0, ssi=7)
obs2 = Observation(value=42.8, lli=None, ssi=6)

sat = Satellite(sv="G01")
sat.add_observation("S1C", obs1)
sat.add_observation("S2W", obs2)

epoch = Rnxv3ObsEpochRecord(
    timestamp=datetime(2024, 1, 1, 0, 0, 0),
    epoch_flag=0,
    num_satellites=1,
    satellites=[sat]
)
```

### Example 3: Custom Types with Pydantic

Integrate non-Pydantic types:

```python
from pathlib import Path
from pydantic import BaseModel, ConfigDict, field_serializer
import pint

ureg = pint.UnitRegistry()

class Rnxv3Obs(BaseModel):
    """Reader with Path and pint.Quantity support."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,  # Allow Path, pint.Quantity
    )

    fpath: Path
    sampling_interval: pint.Quantity

    @field_serializer('sampling_interval')
    def serialize_quantity(self, v: pint.Quantity) -> str:
        """Convert Quantity to string for serialization."""
        return f"{v.magnitude} {v.units}"


# ✅ Works with arbitrary types
reader = Rnxv3Obs(
    fpath=Path("/data/station.24o"),
    sampling_interval=30.0 * ureg.seconds
)

# Serialization
print(reader.model_dump())
# {'fpath': PosixPath('/data/station.24o'),
#  'sampling_interval': '30.0 second'}
```

## Advanced Patterns

### Pattern 1: Computed Fields

```python
from pydantic import computed_field

class Rnxv3Obs(BaseModel):
    fpath: Path
    _cached_hash: str | None = None

    @computed_field
    @property
    def file_hash(self) -> str:
        """Compute SHA256 hash (cached)."""
        if self._cached_hash is None:
            h = hashlib.sha256()
            with open(self.fpath, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            self._cached_hash = h.hexdigest()[:16]
        return self._cached_hash
```

### Pattern 2: Factory Methods

```python
class Rnxv3ObsHeader(BaseModel):
    rinex_version: float
    obs_types: dict[str, list[str]]
    # ... other fields

    @classmethod
    def from_lines(cls, lines: list[str]) -> 'Rnxv3ObsHeader':
        """Factory method to parse from RINEX lines."""
        data = {}

        for line in lines:
            label = line[60:80].strip()

            if label == "RINEX VERSION / TYPE":
                data['rinex_version'] = float(line[0:9])
                data['rinex_type'] = line[20]

            elif label == "SYS / # / OBS TYPES":
                system = line[0]
                num_obs = int(line[3:6])
                obs_types = line[7:60].split()

                if 'obs_types' not in data:
                    data['obs_types'] = {}
                data['obs_types'][system] = obs_types

            # ... parse other fields

        return cls(**data)  # Validates automatically


# Usage
with open("station.24o", 'r') as f:
    header_lines = []
    for line in f:
        header_lines.append(line)
        if "END OF HEADER" in line:
            break

header = Rnxv3ObsHeader.from_lines(header_lines)
```

### Pattern 3: Pre/Post Processing

```python
from pydantic import field_serializer, field_validator

class Rnxv3ObsHeader(BaseModel):
    marker_name: str

    @field_validator('marker_name', mode='before')
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """Preprocessing: Clean whitespace."""
        return v.strip() if isinstance(v, str) else v

    @field_validator('marker_name')
    @classmethod
    def validate_marker_name(cls, v: str) -> str:
        """Validation: Check format."""
        if not v:
            raise ValueError("Marker name cannot be empty")
        if len(v) > 60:
            raise ValueError(f"Marker name too long: {len(v)} chars")
        return v
```

## Error Handling

### ValidationError Structure

```python
from pydantic import ValidationError

try:
    header = Rnxv3ObsHeader(
        rinex_version=2.11,  # Wrong version
        rinex_type='N',      # Wrong type
        obs_types={}         # Empty
    )
except ValidationError as e:
    print(e.errors())
    # [
    #     {
    #         'loc': ('rinex_version',),
    #         'msg': 'Expected RINEX v3.xx, got 2.11',
    #         'type': 'value_error'
    #     },
    #     {
    #         'loc': ('rinex_type',),
    #         'msg': "Expected observation file (type='O'), got 'N'",
    #         'type': 'value_error'
    #     },
    #     {
    #         'loc': ('obs_types',),
    #         'msg': 'No observation types defined in header',
    #         'type': 'value_error'
    #     }
    # ]
```

### Custom Exceptions

```python
from canvod.readers.gnss_specs.exceptions import CorruptedFileError

class Rnxv3ObsHeader(BaseModel):
    rinex_version: float

    @field_validator('rinex_version')
    @classmethod
    def check_version(cls, v: float) -> float:
        if not (3.0 <= v < 4.0):
            # Raise custom exception instead of ValidationError
            raise CorruptedFileError(
                f"Invalid RINEX version {v}. "
                f"File may be corrupted or not a RINEX v3 file."
            )
        return v
```

### Handling Validation Errors

```python
from pydantic import ValidationError

def safe_parse_header(lines: list[str]) -> Rnxv3ObsHeader | None:
    """Safely parse header with error handling."""
    try:
        return Rnxv3ObsHeader.from_lines(lines)
    except ValidationError as e:
        print(f"Header validation failed:")
        for error in e.errors():
            field = '.'.join(str(loc) for loc in error['loc'])
            print(f"  {field}: {error['msg']}")
        return None
    except CorruptedFileError as e:
        print(f"Corrupted file: {e}")
        return None
```

## Best Practices

### 1. Use Type Hints Everywhere

```python
# ✅ Good: Full type hints
class Observation(BaseModel):
    value: float
    lli: int | None = None
    ssi: int | None = None

# ❌ Bad: Missing type hints
class Observation(BaseModel):
    value = 0.0  # Type inferred incorrectly
    lli = None   # Type is Any
```

### 2. Provide Clear Error Messages

```python
# ✅ Good: Informative error
@field_validator('rinex_version')
@classmethod
def check_version(cls, v: float) -> float:
    if not (3.0 <= v < 4.0):
        raise ValueError(
            f"Expected RINEX v3.xx, got {v}. "
            f"Use Rnxv2Obs for v2 files or Rnxv4Obs for v4 files."
        )
    return v

# ❌ Bad: Generic error
@field_validator('rinex_version')
@classmethod
def check_version(cls, v: float) -> float:
    if not (3.0 <= v < 4.0):
        raise ValueError("Invalid version")
    return v
```

### 3. Use Factory Methods for Complex Parsing

```python
# ✅ Good: Factory method
@classmethod
def from_lines(cls, lines: list[str]) -> 'Rnxv3ObsHeader':
    """Parse from RINEX header lines."""
    data = cls._parse_lines(lines)
    return cls(**data)  # Automatic validation

# ❌ Bad: Manual construction
def parse_header(lines):
    header = Rnxv3ObsHeader()
    header.rinex_version = float(lines[0][:9])  # Bypasses validation
    # ...
```

### 4. Validate Early

```python
# ✅ Good: Validate on initialization
class Rnxv3Obs(BaseModel):
    fpath: Path
    header: Rnxv3ObsHeader

    @model_validator(mode='after')
    def parse_header(self):
        """Parse and validate header immediately."""
        with open(self.fpath, 'r') as f:
            lines = self._read_header(f)
        self.header = Rnxv3ObsHeader.from_lines(lines)
        return self

# ❌ Bad: Lazy validation
class Rnxv3Obs:
    def __init__(self, fpath):
        self.fpath = fpath
        self._header = None  # Parsed later

    @property
    def header(self):
        if self._header is None:
            self._header = self._parse_header()  # Error discovered late
        return self._header
```

### 5. Use Immutability

```python
# ✅ Good: Frozen model
class Rnxv3Obs(BaseModel):
    model_config = ConfigDict(frozen=True)
    fpath: Path
    header: Rnxv3ObsHeader

# ❌ Bad: Mutable model
class Rnxv3Obs(BaseModel):
    fpath: Path
    header: Rnxv3ObsHeader

reader = Rnxv3Obs(...)
reader.fpath = other_path  # Unexpected mutation
```

## Debugging Pydantic Models

### 1. Use `model_dump()`

```python
header = Rnxv3ObsHeader(...)
print(header.model_dump())
# Outputs all fields as dict
```

### 2. Use `model_dump_json()`

```python
print(header.model_dump_json(indent=2))
# Pretty-printed JSON
```

### 3. Inspect Schema

```python
print(Rnxv3ObsHeader.model_json_schema())
# Get JSON Schema representation
```

## Performance Considerations

### Validation Cost

Pydantic validation has minimal overhead:

```python
# Benchmark: Parse 2880 epoch records
# Traditional: 0.45s
# Pydantic: 0.52s (+15%)
# Benefit: Type safety, validation, clear errors
```

### Optimization Tips

1. **Use `mode='before'` validators** for preprocessing
2. **Cache computed properties** with `@cached_property`
3. **Use `model_config(extra='forbid')`** to reject unknown fields fast
4. **Profile with `cProfile`** to find bottlenecks

## Summary

Pydantic in canvod-readers provides:

1. ✅ **Type Safety**: Catch type errors at parse time
2. ✅ **Validation**: Ensure data meets RINEX specification
3. ✅ **Clear Errors**: Informative validation messages
4. ✅ **IDE Support**: Full autocomplete and type checking
5. ✅ **Testability**: Easy to mock and test
6. ✅ **Documentation**: Self-documenting models

Next: Learn how to [test Pydantic models](testing.md) effectively.
