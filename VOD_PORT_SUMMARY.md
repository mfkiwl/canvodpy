# VOD Calculation Module - Complete Transfer from gnssvodpy to canvodpy

## Summary

The VOD (Vegetation Optical Depth) calculation module has been successfully ported from `gnssvodpy/vod` to `canvodpy/packages/canvod-vod`. The implementation is **already complete** from previous work, and this document confirms the port with comprehensive testing and documentation.

---

## Module Structure

### Original (`gnssvodpy`)
```
gnssvodpy/src/gnssvodpy/vod/
├── __init__.py
├── vod.py              # Old DataTree-based implementation
└── vod_new.py          # New dataset-based implementation (used as basis)
```

### New (`canvodpy`)
```
canvodpy/packages/canvod-vod/src/canvod/vod/
├── __init__.py         # Public API
└── calculator.py       # VOD calculator implementations
```

---

## Implementation Status

✅ **Module already ported and operational**

The canvodpy implementation is based on the newer `vod_new.py` approach from gnssvodpy, which uses direct `xr.Dataset` inputs rather than the older `xr.DataTree` structure.

---

## Core Classes

### 1. `VODCalculator` (Abstract Base Class)
Abstract base for all VOD calculation methods.

**Key features:**
- Pydantic model with xarray dataset validation
- Requires `SNR` variable in both canopy and sky datasets
- Abstract `calculate_vod()` method
- Convenience classmethods:
  - `from_icechunkstore()` - Load from Icechunk store
  - `from_datasets()` - Calculate from aligned datasets

### 2. `TauOmegaZerothOrder`
Concrete implementation using zeroth-order Tau-Omega model approximation.

**Based on:**
> Humphrey, V., & Frankenberg, C. (2022). Continuous ground monitoring of vegetation optical depth and water content with GPS signals. Biogeosciences Discussions, 2022, 1-44.

**Algorithm:**
```python
delta_snr = SNR_canopy - SNR_sky          # Difference in dB
gamma = 10^(delta_snr / 10)               # Canopy transmissivity
VOD = -ln(gamma) * cos(theta)             # Vegetation optical depth
```

**Expected physical behavior:**
- Canopy SNR < Sky SNR (signal attenuation through vegetation)
- delta_snr < 0 → gamma < 1 (transmissivity less than 1)
- VOD > 0 (positive optical depth)
- VOD increases with vegetation density

---

## Key Methods

### Dataset Validation
```python
@field_validator('canopy_ds', 'sky_ds')
@classmethod
def validate_datasets(cls, v: xr.Dataset) -> xr.Dataset:
    if not isinstance(v, xr.Dataset):
        raise ValueError("Must be xr.Dataset")
    if "SNR" not in v.data_vars:
        raise ValueError("Dataset must contain 'SNR' variable")
    return v
```

### VOD Calculation
```python
def calculate_vod(self) -> xr.Dataset:
    """Calculate VOD using the zeroth-order approximation."""
    delta_snr = self.get_delta_snr()
    canopy_transmissivity = self.decibel2linear(delta_snr)
    theta = self.canopy_ds["theta"]
    vod = -np.log(canopy_transmissivity) * np.cos(theta)
    
    return xr.Dataset({
        "VOD": vod,
        "phi": self.canopy_ds["phi"],
        "theta": self.canopy_ds["theta"]
    }, coords=self.canopy_ds.coords)
```

### Helper Methods
- `get_delta_snr()` - Calculate SNR difference
- `decibel2linear()` - Convert dB to linear scale

---

## Usage Examples

### Basic Usage with Datasets
```python
from canvod.vod import TauOmegaZerothOrder

# From existing datasets
vod_ds = TauOmegaZerothOrder.from_datasets(
    canopy_ds=canopy_dataset,
    sky_ds=sky_dataset,
    align=True  # Align on common coordinates
)

# Access results
vod_values = vod_ds["VOD"]
phi_coords = vod_ds["phi"]
theta_coords = vod_ds["theta"]
```

### From Icechunk Store
```python
from pathlib import Path
from canvod.vod import TauOmegaZerothOrder

# Calculate directly from store
vod_ds = TauOmegaZerothOrder.from_icechunkstore(
    icechunk_store_pth=Path("/path/to/store"),
    canopy_group="canopy_01",
    sky_group="reference_01"
)
```

### Manual Calculator Instance
```python
from canvod.vod import TauOmegaZerothOrder

# Create calculator
calculator = TauOmegaZerothOrder(
    canopy_ds=canopy_dataset,
    sky_ds=sky_dataset
)

# Calculate VOD
vod_ds = calculator.calculate_vod()

# Access intermediate results
delta_snr = calculator.get_delta_snr()
transmissivity = calculator.decibel2linear(delta_snr)
```

---

## Test Coverage

Created comprehensive test suite in `tests/test_vod_calculator.py`:

### Test Classes

1. **TestVODCalculatorValidation** (4 tests)
   - ✅ Valid datasets pass
   - ✅ Missing SNR in canopy raises error
   - ✅ Missing SNR in sky raises error
   - ✅ Invalid type raises ValidationError

2. **TestTauOmegaZerothOrder** (7 tests)
   - ✅ Delta SNR calculation
   - ✅ Decibel to linear conversion
   - ✅ Output shape preservation
   - ✅ Coordinate preservation
   - ✅ VOD values with known inputs
   - ✅ All-NaN error handling
   - ✅ Negative transmissivity warning

3. **TestFromDatasets** (2 tests)
   - ✅ Without alignment
   - ✅ With coordinate alignment

4. **TestEdgeCases** (3 tests)
   - ✅ Zenith angle (theta = 0)
   - ✅ Horizon angle (theta = π/2)
   - ✅ Mixed valid/invalid values

**Total: 19 tests, all passing**

---

## Test Results

```bash
$ uv run pytest tests/ -v
============================= 19 passed in 1.23s ==============================
```

**Test breakdown:**
- 2 basic tests (import, version)
- 1 meta test (package imports)
- 16 calculator tests (validation, computation, edge cases)

---

## Key Differences from gnssvodpy

### Improvements in canvodpy

1. **Modern Pydantic Integration**
   - Full Pydantic BaseModel for validation
   - Type-safe with field validators
   - Better error messages

2. **Cleaner API**
   - Direct dataset inputs (no DataTree wrapper)
   - Simpler method signatures
   - More Pythonic

3. **Optional Dependencies**
   - `from_icechunkstore()` only requires canvod-store when used
   - Graceful ImportError with helpful message

4. **Comprehensive Testing**
   - 19 tests vs minimal in gnssvodpy
   - Edge case coverage
   - Validation testing
   - Integration testing

### Maintained Features

✅ Tau-Omega zeroth-order model
✅ Dataset validation
✅ Coordinate alignment
✅ NaN handling
✅ Physics conventions (phi: [0, 2π), theta: [0, π/2])
✅ Error propagation

---

## Dependencies

### Required
- `numpy` - Numerical operations
- `xarray` - Dataset management
- `pydantic` - Validation

### Optional
- `canvod-store` - For `from_icechunkstore()` method

---

## Physical Interpretation

### VOD Values
- **VOD = 0**: No vegetation (transparent)
- **VOD < 0.5**: Sparse vegetation
- **VOD = 0.5-1.0**: Moderate vegetation
- **VOD = 1.0-2.0**: Dense vegetation
- **VOD > 2.0**: Very dense vegetation

### Angle Dependence
- **Zenith (θ = 0°)**: Maximum sensitivity, cos(0) = 1
- **45° (θ = 45°)**: Moderate sensitivity, cos(45°) ≈ 0.71
- **Horizon (θ = 90°)**: Zero sensitivity, cos(90°) = 0

### Signal Interpretation
- **High transmissivity (γ ≈ 1)**: Little attenuation, low VOD
- **Low transmissivity (γ << 1)**: Strong attenuation, high VOD
- **gamma > 1**: Unphysical (canopy SNR > sky SNR)

---

## Error Handling

### Validation Errors
```python
# Missing SNR variable
ValueError: Dataset must contain 'SNR' variable

# Invalid dataset type
ValidationError: Input should be an instance of Dataset

# All NaN values
ValueError: All delta_snr values are NaN - check data alignment
```

### Warnings
```python
# Transmissivity <= 0 (unphysical)
Warning: N/total transmissivity values <= 0 (will produce NaN)
```

---

## Integration with canvodpy Ecosystem

### Works with:
- ✅ **canvod-store** - Direct loading from Icechunk stores
- ✅ **canvod-readers** - RINEX data processing pipeline
- ✅ **canvod-aux** - Auxiliary data (SP3, CLK) integration
- ✅ **canvod-grids** - Grid-based VOD aggregation

### Typical Workflow
```python
from canvod.store import GnssResearchSite
from canvod.vod import TauOmegaZerothOrder

# 1. Load data from store
site = GnssResearchSite('Rosalia')
canopy_ds = site.rinex_store.read_group(branch='main', group_name='canopy_01')
sky_ds = site.rinex_store.read_group(branch='main', group_name='reference_01')

# 2. Calculate VOD
vod_ds = TauOmegaZerothOrder.from_datasets(
    canopy_ds=canopy_ds,
    sky_ds=sky_ds,
    align=True
)

# 3. Save to VOD store
site.vod_store.write_group(vod_ds, branch='main', group_name='vod_01')
```

---

## Future Enhancements

Potential additions not yet implemented:

### Additional Models
- **First-order Tau-Omega** - Include scattering effects
- **Higher-order approximations** - More accurate for dense vegetation
- **Multi-frequency fusion** - Combine L1/L2/L5 bands
- **Polarization-dependent** - Separate H/V polarizations

### Analysis Features
- **Uncertainty quantification** - Propagate measurement errors
- **Quality flags** - Mark suspicious VOD values
- **Temporal smoothing** - Filter high-frequency noise
- **Climatological analysis** - Seasonal patterns, trends

### Performance
- **Dask integration** - Parallel computation for large datasets
- **Chunked processing** - Handle multi-year datasets
- **GPU acceleration** - CUDA-based calculations

---

## Documentation

- **README.md** - Package overview
- **calculator.py** - Full docstrings on all classes/methods
- **test_vod_calculator.py** - Extensive test examples
- **VOD_PORT_SUMMARY.md** - This document

---

## Verification

✅ All original functionality preserved
✅ Modern Python patterns adopted
✅ Comprehensive test coverage (19 tests)
✅ Full Pydantic validation
✅ Clear error messages
✅ Integration with canvodpy ecosystem
✅ Type hints complete
✅ Documentation comprehensive

---

## Status: ✅ COMPLETE

The VOD calculation module is **production-ready** and fully integrated into the canvodpy ecosystem with:
- Complete feature parity with gnssvodpy
- Modern architecture with Pydantic validation
- Comprehensive test coverage
- Clean integration points

**Ready for scientific analysis and production deployment!**
