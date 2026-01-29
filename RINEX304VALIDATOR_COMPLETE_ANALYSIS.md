# RINEX304Validator - Complete Analysis

## Git History Findings

### ✅ Confirmed: validators.py NEVER existed

```bash
$ git log --all --full-history -- "**/gnss_specs/validators.py"
# (empty result)
```

### Class mention history:

```bash
$ git log -S "RINEX304Validator" --source --all --oneline
9b547fb  started resolving import issues       # Added analysis doc
2484fd6  added canvodpy-aux package...         # First mention (Jan 16, 2026)
```

### What commit 2484fd6 added:

**Location:** Inside `validate_rinex_304_compliance()` method (lazy import)

```python
def validate_rinex_304_compliance(
    self,
    ds: xr.Dataset = None,
    strict: bool = False,
    print_report: bool = True
) -> dict[str, list[str]]:
    """Run enhanced RINEX 3.04 specification validation."""
    from canvod.readers.gnss_specs.validators import RINEX304Validator  # ← Never existed!
    
    # Prepare header dict
    header_dict = {
        'obs_codes_per_system': self.header.obs_codes_per_system,
    }
    
    # Add GLONASS-specific headers
    if hasattr(self.header, 'glonass_slot_frq'):
        header_dict['GLONASS SLOT / FRQ #'] = self.header.glonass_slot_frq
    
    if hasattr(self.header, 'glonass_cod_phs_bis'):
        header_dict['GLONASS COD/PHS/BIS'] = self.header.glonass_cod_phs_bis
    
    if hasattr(self.header, 'phase_shift'):
        header_dict['SYS / PHASE SHIFT'] = self.header.phase_shift
    
    # Call non-existent validator
    results = RINEX304Validator.validate_all(
        ds=ds,
        header_dict=header_dict,
        strict=strict
    )
    
    if print_report:
        RINEX304Validator.print_validation_report(results)
    
    return results
```

**This was STUB/ASPIRATIONAL CODE** - method signature defined, implementation left as TODO.

---

## Intent Analysis

### What validation should do:

From the docstring:
```
Validates:
1. System-specific observation codes
2. GLONASS mandatory fields (slot/frequency, biases)
3. Phase shift records (RINEX 3.01+)
4. Observation value ranges
```

### Expected API:

```python
results = RINEX304Validator.validate_all(
    ds=xr.Dataset,          # Dataset to validate
    header_dict=dict,       # RINEX headers
    strict=bool             # Raise errors or just report?
) -> dict[str, list[str]]   # Validation results by category

RINEX304Validator.print_validation_report(results)
```

### Expected output structure:

```python
{
    "observation_codes": [...],    # Invalid observation codes
    "glonass_fields": [...],       # Missing GLONASS headers
    "phase_shifts": [...],         # Phase shift issues
    "value_ranges": [...],         # Out-of-range values
}
```

---

## Current Validator Architecture

### Yes, validators ARE in models.py now!

**Location:** `packages/canvod-readers/src/canvod/readers/gnss_specs/models.py`

```python
class VodDataValidator(BaseModel):
    """Validates VOD (Vegetation Optical Depth) data structure."""
    
    vod_data: xr.Dataset
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    @field_validator("vod_data", mode="before")
    def validate_vod_data(cls, value: xr.Dataset) -> xr.Dataset:
        """Validate VOD dataset structure."""
        # Validation logic
        return value
```

**Pattern:** Pydantic BaseModel with field validators

### Also in base.py:

**Location:** `packages/canvod-readers/src/canvod/readers/base.py`

```python
class DatasetStructureValidator(BaseModel):
    """Validates xarray.Dataset structure for pipeline compatibility."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    dataset: xr.Dataset
    
    def validate_dimensions(self) -> None:
        """Validate required dimensions exist."""
        required_dims = {"epoch", "sid"}
        missing_dims = required_dims - set(self.dataset.dims)
        if missing_dims:
            raise ValueError(f"Missing dimensions: {missing_dims}")
    
    def validate_coordinates(self) -> None:
        """Validate required coordinates."""
        # ...
    
    def validate_data_variables(self, required_vars: list[str] | None = None) -> None:
        """Validate data variables."""
        # ...
    
    def validate_all(self, required_vars: list[str] | None = None) -> None:
        """Run all validations."""
        self.validate_dimensions()
        self.validate_coordinates()
        self.validate_data_variables(required_vars)
        self.validate_attributes()
```

**Pattern:** Pydantic BaseModel with method-based validation

---

## Why It Broke

### Before Ruff refactoring:

```python
def validate_rinex_304_compliance(self, ...):
    from canvod.readers.gnss_specs.validators import RINEX304Validator  # Lazy import
    # Only fails IF method is called
```

**Status:** Hidden failure - no tests call this method, so import never executed

### After Ruff refactoring:

```python
# Top of file (line 65)
from canvod.readers.gnss_specs.validators import RINEX304Validator  # Eager import

def validate_rinex_304_compliance(self, ...):
    # Import moved to top
    results = RINEX304Validator.validate_all(...)
```

**Status:** Loud failure - import executes on module load, everything breaks

**Ruff's rule:** Move imports to module top (PEP 8, better style)  
**Result:** Exposed the stub code that was silently failing

---

## Available Resources

### validation_constants.py

**Contains all RINEX 3.04 specification data:**

```python
# GNSS Systems
GNSS_SYSTEMS = {"G", "R", "E", "C", "J", "S", "I"}
SYSTEM_NAMES = {"G": "GPS", "R": "GLONASS", ...}

# Band specifications with valid codes
GPS_BANDS = {
    "1": {
        "name": "L1",
        "frequency": 1575.42,  # MHz
        "bandwidth": 30.69,
        "codes": {"C", "S", "L", "X", "P", "W", "Y", "M", "N"},
    },
    "2": {"name": "L2", ...},
    "5": {"name": "L5", ...},
}

GALILEO_BANDS = {...}
GLONASS_BANDS = {...}
BEIDOU_BANDS = {...}
# etc.
```

**This provides everything needed for validation:**
- Valid observation codes per system
- Frequency ranges
- Band specifications

---

## Solution: Add RINEX304Validator to models.py

### Recommended Implementation

**File:** `packages/canvod-readers/src/canvod/readers/gnss_specs/models.py`

```python
class RINEX304Validator(BaseModel):
    """Validates RINEX 3.04 specification compliance.
    
    Validates:
    - System-specific observation codes
    - GLONASS mandatory fields (slot/frequency, biases)
    - Phase shift records (RINEX 3.01+)
    - Observation value ranges
    """
    
    dataset: xr.Dataset
    header_dict: dict[str, Any]
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    @staticmethod
    def validate_all(
        ds: xr.Dataset,
        header_dict: dict[str, Any],
        strict: bool = False
    ) -> dict[str, list[str]]:
        """Validate dataset against RINEX 3.04 specification.
        
        Parameters
        ----------
        ds : xr.Dataset
            Dataset to validate
        header_dict : dict
            RINEX header information including:
            - obs_codes_per_system
            - GLONASS SLOT / FRQ #
            - GLONASS COD/PHS/BIS
            - SYS / PHASE SHIFT
        strict : bool, default False
            If True, raise ValueError on validation failures
        
        Returns
        -------
        dict[str, list[str]]
            Validation results by category:
            - observation_codes: Invalid obs codes
            - glonass_fields: Missing GLONASS fields
            - phase_shifts: Phase shift issues
            - value_ranges: Out-of-range values
        """
        from .validation_constants import (
            GNSS_SYSTEMS,
            GPS_BANDS,
            GALILEO_BANDS,
            GLONASS_BANDS,
            BEIDOU_BANDS,
            QZSS_BANDS,
            SBAS_BANDS,
            IRNSS_BANDS,
        )
        
        results = {
            "observation_codes": [],
            "glonass_fields": [],
            "phase_shifts": [],
            "value_ranges": [],
        }
        
        # 1. Validate observation codes per system
        obs_codes = header_dict.get('obs_codes_per_system', {})
        for system, codes in obs_codes.items():
            if system not in GNSS_SYSTEMS:
                results["observation_codes"].append(
                    f"Unknown system: {system}"
                )
                continue
            
            # Get valid codes for this system
            # TODO: Implement validation logic using band specs
            pass
        
        # 2. Validate GLONASS mandatory fields
        if 'R' in obs_codes:
            if 'GLONASS SLOT / FRQ #' not in header_dict:
                results["glonass_fields"].append(
                    "Missing required header: GLONASS SLOT / FRQ #"
                )
            if 'GLONASS COD/PHS/BIS' not in header_dict:
                results["glonass_fields"].append(
                    "Missing required header: GLONASS COD/PHS/BIS"
                )
        
        # 3. Validate phase shifts
        phase_shifts = header_dict.get('SYS / PHASE SHIFT', {})
        # TODO: Validate phase shift records
        
        # 4. Validate observation value ranges
        # TODO: Check that observation values are within spec ranges
        
        # Raise errors in strict mode
        if strict:
            all_issues = sum([v for v in results.values()], [])
            if all_issues:
                raise ValueError(
                    f"RINEX 3.04 validation failed with {len(all_issues)} issues"
                )
        
        return results
    
    @staticmethod
    def print_validation_report(results: dict[str, list[str]]) -> None:
        """Print formatted validation report.
        
        Parameters
        ----------
        results : dict[str, list[str]]
            Validation results from validate_all()
        """
        has_issues = any(results.values())
        
        if not has_issues:
            print("✓ RINEX 3.04 validation passed - no issues found")
            return
        
        print("RINEX 3.04 Validation Report")
        print("=" * 60)
        
        for category, issues in results.items():
            if issues:
                print(f"\n{category.replace('_', ' ').title()}:")
                for issue in issues:
                    print(f"  - {issue}")
        
        print("\n" + "=" * 60)
        total_issues = sum(len(v) for v in results.values())
        print(f"Total issues: {total_issues}")
```

### Then update v3_04.py import:

**Line 65:**
```python
# OLD (broken):
from canvod.readers.gnss_specs.validators import RINEX304Validator

# NEW (working):
from canvod.readers.gnss_specs.models import RINEX304Validator
```

---

## Alternative: Quick Stub Fix

If you don't want to implement validation now:

**Option 1:** Comment out and stub

```python
# Line 65 - Comment out
# from canvod.readers.gnss_specs.validators import RINEX304Validator

def validate_rinex_304_compliance(
    self,
    ds: xr.Dataset | None = None,
    strict: bool = False,
    print_report: bool = True,
) -> dict[str, list[str]]:
    """Run enhanced RINEX 3.04 specification validation.
    
    NOTE: Currently returns empty results (validation not implemented).
    TODO: Implement RINEX304Validator in models.py
    """
    if ds is None:
        ds = self.to_ds(write_global_attrs=False)
    
    results = {
        "observation_codes": [],
        "glonass_fields": [],
        "phase_shifts": [],
        "value_ranges": [],
    }
    
    if print_report:
        print("RINEX 3.04 validation not yet implemented")
    
    return results
```

---

## Recommendation

**Short-term:** Use stub fix to unblock development  
**Medium-term:** Implement RINEX304Validator in models.py following the pattern above  
**Long-term:** Add comprehensive tests for validation logic

The validator belongs in `models.py` alongside `VodDataValidator` since both validate data structures.
