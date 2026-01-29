# Testing Guide

This page explains the test structure, coverage, and best practices for testing canvod-readers.

## Test Structure

```
tests/
├── test_gnss_specs_base.py      # Core modules (exceptions, constants, models, utils)
├── test_signal_mapping.py        # Signal ID mapping and constellations
├── test_rinex_v3.py              # RINEX v3.04 parser unit tests
├── test_rinex_integration.py     # Full file processing tests
├── test_meta.py                  # Package metadata tests
└── data/                         # Test RINEX files
    ├── BRUX00BEL_R_20240010000_01D_30S_MO.24o
    └── ... (more test files)
```

## Running Tests

### Quick Test

```bash
# Run all tests
just test

# Or with pytest directly
uv run pytest tests/ -v
```

### With Coverage

```bash
# Generate coverage report
just test-cov

# View HTML report
open htmlcov/index.html
```

### Specific Tests

```bash
# Test specific file
pytest tests/test_rinex_v3.py -v

# Test specific class
pytest tests/test_rinex_v3.py::TestRnxv3ObsHeader -v

# Test specific method
pytest tests/test_rinex_v3.py::TestRnxv3ObsHeader::test_header_parsing -v
```

## Test Categories

### 1. Unit Tests - Pydantic Models

Test individual Pydantic models for validation:

```python
# tests/test_rinex_v3.py
from canvod.readers.gnss_specs.models import Observation
from pydantic import ValidationError
import pytest

class TestObservation:
    """Test Observation model."""

    def test_valid_observation(self):
        """Test valid observation creation."""
        obs = Observation(value=45.2, lli=0, ssi=7)

        assert obs.value == 45.2
        assert obs.lli == 0
        assert obs.ssi == 7

    def test_missing_optional_fields(self):
        """Test observation with optional fields missing."""
        obs = Observation(value=42.8)

        assert obs.value == 42.8
        assert obs.lli is None
        assert obs.ssi is None

    def test_invalid_lli(self):
        """Test LLI validation."""
        with pytest.raises(ValidationError) as exc_info:
            Observation(value=45.2, lli=10)  # Invalid: must be 0-9

        errors = exc_info.value.errors()
        assert 'lli' in str(errors[0]['loc'])
        assert 'must be 0-9' in errors[0]['msg'].lower()

    def test_invalid_ssi(self):
        """Test SSI validation."""
        with pytest.raises(ValidationError):
            Observation(value=45.2, ssi=-1)  # Invalid: must be 0-9
```

### 2. Unit Tests - Signal Mapping

Test Signal ID creation and constellation mappings:

```python
# tests/test_signal_mapping.py
from canvod.readers.gnss_specs.signals import SignalIDMapper

class TestSignalIDMapper:
    """Test Signal ID mapping."""

    def test_create_gps_signal_id(self):
        """Test GPS signal ID creation."""
        mapper = SignalIDMapper()

        sid = mapper.create_signal_id("G01", "G01|S1C")
        assert sid == "G01|L1|C"

        sid = mapper.create_signal_id("G01", "G01|S2W")
        assert sid == "G01|L2|W"

    def test_create_galileo_signal_id(self):
        """Test Galileo signal ID creation."""
        mapper = SignalIDMapper()

        sid = mapper.create_signal_id("E05", "E05|C1C")
        assert sid == "E05|E1|C"

        sid = mapper.create_signal_id("E05", "E05|C5Q")
        assert sid == "E05|E5a|Q"

    def test_auxiliary_observation(self):
        """Test X1 auxiliary observation."""
        mapper = SignalIDMapper()

        sid = mapper.create_signal_id("G01", "G01|X1")
        assert sid == "G01|X1|X"

        is_aux = mapper.is_auxiliary_observation(sid)
        assert is_aux is True

    def test_get_band_frequency(self):
        """Test frequency retrieval."""
        mapper = SignalIDMapper()

        freq = mapper.get_band_frequency("L1")
        assert freq == 1575.42

        freq = mapper.get_band_frequency("E5a")
        assert freq == 1176.45
```

### 3. Integration Tests - Full File Processing

Test complete RINEX file parsing:

```python
# tests/test_rinex_integration.py
from pathlib import Path
from canvod.readers import Rnxv3Obs
import xarray as xr

class TestRINEXIntegration:
    """Integration tests for complete file processing."""

    def test_full_file_processing(self):
        """Test processing complete RINEX file."""
        # Path to test data
        test_file = Path("tests/data/BRUX00BEL_R_20240010000_01D_30S_MO.24o")

        # Create reader
        obs = Rnxv3Obs(fpath=test_file)

        # Convert to Dataset
        ds = obs.to_ds(keep_rnx_data_vars=["SNR"])

        # Validate structure
        assert isinstance(ds, xr.Dataset)
        assert "epoch" in ds.dims
        assert "sid" in ds.dims
        assert ds.sizes["epoch"] > 0
        assert ds.sizes["sid"] > 0

        # Validate coordinates
        assert "sv" in ds.coords
        assert "system" in ds.coords
        assert "band" in ds.coords
        assert "code" in ds.coords
        assert "freq_center" in ds.coords

        # Validate data
        assert "SNR" in ds.data_vars
        assert ds.SNR.dims == ("epoch", "sid")

        # Check no all-NaN data
        import numpy as np
        assert not np.all(np.isnan(ds.SNR.values))

    def test_multi_system_filtering(self):
        """Test filtering by GNSS system."""
        test_file = Path("tests/data/BRUX00BEL_R_20240010000_01D_30S_MO.24o")
        obs = Rnxv3Obs(fpath=test_file)
        ds = obs.to_ds()

        # Filter GPS only
        gps = ds.where(ds.system == 'G', drop=True)
        assert all(gps.system.values == 'G')

        # Filter Galileo only
        galileo = ds.where(ds.system == 'E', drop=True)
        assert all(galileo.system.values == 'E')

    def test_band_filtering(self):
        """Test filtering by frequency band."""
        test_file = Path("tests/data/BRUX00BEL_R_20240010000_01D_30S_MO.24o")
        obs = Rnxv3Obs(fpath=test_file)
        ds = obs.to_ds()

        # Filter L1 band
        l1 = ds.where(ds.band == 'L1', drop=True)
        assert all(l1.band.values == 'L1')

        # Check frequencies are in L1 range
        assert all((l1.freq_center > 1550) & (l1.freq_center < 1600))
```

### 4. Validation Tests

Test `DatasetStructureValidator`:

```python
# tests/test_rinex_v3.py
from canvod.readers.base import DatasetStructureValidator
import xarray as xr
import numpy as np
import pytest

class TestDatasetValidation:
    """Test Dataset structure validation."""

    def test_valid_dataset(self):
        """Test validation passes for valid dataset."""
        ds = xr.Dataset(
            data_vars={
                "SNR": (("epoch", "sid"), np.random.rand(10, 5)),
                "Phase": (("epoch", "sid"), np.random.rand(10, 5)),
            },
            coords={
                "epoch": ("epoch", pd.date_range("2024-01-01", periods=10, freq="30s")),
                "sid": ("sid", ["G01|L1|C", "G01|L2|P", "E05|E1|C", "E05|E5a|Q", "R12|G1|C"]),
                "sv": ("sid", ["G01", "G01", "E05", "E05", "R12"]),
                "system": ("sid", ["G", "G", "E", "E", "R"]),
                "band": ("sid", ["L1", "L2", "E1", "E5a", "G1"]),
                "code": ("sid", ["C", "P", "C", "Q", "C"]),
                "freq_center": ("sid", np.array([1575.42, 1227.60, 1575.42, 1176.45, 1602.0])),
                "freq_min": ("sid", np.array([1560.0, 1212.0, 1560.0, 1166.0, 1598.0])),
                "freq_max": ("sid", np.array([1590.0, 1243.0, 1590.0, 1186.0, 1606.0])),
            },
            attrs={
                "Created": "2024-01-01T00:00:00",
                "Software": "canvod-readers 0.1.0",
                "Institution": "TU Wien",
                "RINEX File Hash": "abc123",
            }
        )

        validator = DatasetStructureValidator(dataset=ds)
        validator.validate_all()  # Should not raise

    def test_missing_dimension(self):
        """Test validation fails for missing dimension."""
        ds = xr.Dataset(
            data_vars={"SNR": (("time", "sid"), np.random.rand(10, 5))},
            coords={"time": range(10), "sid": range(5)}
        )

        validator = DatasetStructureValidator(dataset=ds)
        with pytest.raises(ValueError, match="Missing required dimensions"):
            validator.validate_dimensions()

    def test_wrong_dtype(self):
        """Test validation fails for wrong dtype."""
        ds = xr.Dataset(
            coords={
                "epoch": ("epoch", pd.date_range("2024-01-01", periods=10)),
                "sid": ("sid", ["G01|L1|C"]),
                "freq_center": ("sid", np.array([1575.42], dtype=np.float32)),  # Wrong: should be float64
            }
        )

        validator = DatasetStructureValidator(dataset=ds)
        with pytest.raises(ValueError, match="Wrong dtype"):
            validator.validate_coordinates()
```

## Test Fixtures

Create reusable test data:

```python
# tests/conftest.py
import pytest
from pathlib import Path
import xarray as xr
import numpy as np
import pandas as pd

@pytest.fixture
def test_rinex_file():
    """Path to test RINEX file."""
    return Path("tests/data/BRUX00BEL_R_20240010000_01D_30S_MO.24o")

@pytest.fixture
def sample_dataset():
    """Create sample xarray Dataset for testing."""
    return xr.Dataset(
        data_vars={
            "SNR": (("epoch", "sid"), np.random.rand(100, 20)),
        },
        coords={
            "epoch": ("epoch", pd.date_range("2024-01-01", periods=100, freq="30s")),
            "sid": ("sid", [f"G{i:02d}|L1|C" for i in range(1, 21)]),
            "sv": ("sid", [f"G{i:02d}" for i in range(1, 21)]),
            "system": ("sid", ["G"] * 20),
            "band": ("sid", ["L1"] * 20),
            "code": ("sid", ["C"] * 20),
            "freq_center": ("sid", np.full(20, 1575.42)),
            "freq_min": ("sid", np.full(20, 1560.0)),
            "freq_max": ("sid", np.full(20, 1590.0)),
        }
    )

@pytest.fixture
def signal_mapper():
    """Create SignalIDMapper instance."""
    from canvod.readers.gnss_specs.signals import SignalIDMapper
    return SignalIDMapper()
```

**Usage**:

```python
def test_with_fixtures(test_rinex_file, signal_mapper):
    """Test using fixtures."""
    from canvod.readers import Rnxv3Obs

    obs = Rnxv3Obs(fpath=test_rinex_file)
    ds = obs.to_ds()

    # Use signal_mapper fixture
    sid = signal_mapper.create_signal_id("G01", "G01|S1C")
    assert sid in ds.sid.values
```

## Coverage Report

Current test coverage (as of documentation):

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
src/canvod/readers/__init__.py             12      0   100%
src/canvod/readers/base.py                142      8    94%
src/canvod/readers/gnss_specs/
    __init__.py                             8      0   100%
    constants.py                           25      0   100%
    exceptions.py                          20      0   100%
    models.py                             215     12    94%
    signals.py                             87      5    94%
    utils.py                               18      0   100%
src/canvod/readers/rinex/
    __init__.py                             4      0   100%
    v3_04.py                              487     34    93%
-----------------------------------------------------------
TOTAL                                    1018     59    94%
```

**Target**: 95%+ coverage

## Best Practices

### 1. Test One Thing at a Time

```python
# ✅ Good: Focused test
def test_observation_value():
    """Test observation value validation."""
    obs = Observation(value=45.2)
    assert obs.value == 45.2

# ❌ Bad: Tests multiple things
def test_observation():
    """Test observation."""
    obs = Observation(value=45.2, lli=0, ssi=7)
    assert obs.value == 45.2
    assert obs.lli == 0
    assert obs.ssi == 7
    assert obs.model_dump() == {...}
```

### 2. Use Descriptive Names

```python
# ✅ Good: Clear what's being tested
def test_lli_must_be_between_0_and_9():
    """Test LLI validation rejects values outside 0-9."""

# ❌ Bad: Vague
def test_lli():
    """Test LLI."""
```

### 3. Test Both Success and Failure

```python
def test_satellite_creation_success():
    """Test valid satellite creation."""
    sat = Satellite(sv="G01")
    assert sat.sv == "G01"

def test_satellite_creation_invalid_system():
    """Test satellite creation fails for invalid system."""
    with pytest.raises(ValidationError):
        Satellite(sv="X01")  # Invalid system

def test_satellite_creation_invalid_length():
    """Test satellite creation fails for wrong length."""
    with pytest.raises(ValidationError):
        Satellite(sv="G1")  # Too short
```

### 4. Use Parametrize for Similar Tests

```python
@pytest.mark.parametrize("sv,obs_code,expected", [
    ("G01", "G01|S1C", "G01|L1|C"),
    ("G01", "G01|S2W", "G01|L2|W"),
    ("E05", "E05|C1C", "E05|E1|C"),
    ("R12", "R12|C1C", "R12|G1|C"),
])
def test_signal_id_creation(sv, obs_code, expected):
    """Test signal ID creation for various systems."""
    mapper = SignalIDMapper()
    sid = mapper.create_signal_id(sv, obs_code)
    assert sid == expected
```

### 5. Mock External Dependencies

```python
from unittest.mock import patch, mock_open

def test_file_hash_computation():
    """Test file hash computation."""
    mock_data = b"test content"

    with patch("builtins.open", mock_open(read_data=mock_data)):
        from canvod.readers.gnss_specs.utils import rinex_file_hash

        hash_result = rinex_file_hash(Path("fake.24o"))
        assert len(hash_result) == 16
```

## Continuous Integration

GitHub Actions workflow:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3

      - name: Set up Python
        run: uv python install ${{ matrix.python-version }}

      - name: Install dependencies
        run: uv sync

      - name: Run tests
        run: uv run pytest tests/ -v --cov

      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

## Writing New Tests

### Step 1: Identify What to Test

Ask:
- What's the happy path?
- What can go wrong?
- What are edge cases?

### Step 2: Write Test Skeleton

```python
class TestNewFeature:
    """Test new feature."""

    def test_success_case(self):
        """Test successful execution."""
        pass

    def test_failure_case_1(self):
        """Test failure scenario 1."""
        pass

    def test_edge_case(self):
        """Test edge case."""
        pass
```

### Step 3: Implement Tests

```python
def test_success_case(self):
    """Test successful execution."""
    # Arrange
    input_data = {...}

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected
```

### Step 4: Run and Refine

```bash
pytest tests/test_new_feature.py -v
```

## Summary

Testing in canvod-readers ensures:

1. ✅ **Correctness**: Pydantic models validate properly
2. ✅ **Robustness**: Edge cases are handled
3. ✅ **Compatibility**: Datasets meet structure requirements
4. ✅ **Maintainability**: Tests document expected behavior
5. ✅ **Confidence**: Changes don't break existing functionality

**Current Status**: 104 tests passing, 94% coverage

Next: Learn how to [add new readers](extending_readers.md) to the package.
