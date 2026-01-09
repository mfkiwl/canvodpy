# Testing Guide for canvod-readers

## Prerequisites

### Install Dependencies

```bash
cd ~/Developer/GNSS/canvodpy/packages/canvod-readers

# Option 1: Using uv (recommended)
uv sync

# Option 2: Using pip
pip install -e ".[dev]"
```

### Required Dependencies
All dependencies from `pyproject.toml`:
- georinex>=1.16.0
- matplotlib>=3.7.0
- natsort>=8.4.0
- numpy>=1.24.0
- pandas>=2.0.0
- pint>=0.23
- pydantic>=2.5.0
- pytz>=2023.3
- requests>=2.31.0
- xarray>=2023.12.0

### Development Dependencies
- pytest>=8.0
- pytest-cov>=5.0
- ruff>=0.14
- ty>=0.0.9

---

## Test Structure

```
tests/
├── conftest.py                      # Pytest configuration & fixtures
├── test_meta.py                     # Package structure tests (8 tests)
├── test_gnss_core.py               # Core modules tests (28 tests)  
├── test_signal_mapping.py          # Signal mapping tests (NEW - 60+ tests)
├── test_rinex_v3.py                # RINEX v3 tests (23 tests)
├── test_rinex_integration.py       # Integration tests (NEW - 25+ tests)
└── test_data/                      # Test RINEX files
    └── 01_Rosalia/.../*.25o
```

---

## Running Tests

### Quick Verification (Fast Tests Only)

```bash
# Run all fast tests (excludes slow & network tests)
pytest -v -m "not slow"

# Expected output:
# ✅ test_meta.py::... (8 tests)
# ✅ test_gnss_core.py::... (28 tests)
# ✅ test_signal_mapping.py::... (60+ tests)
# ✅ test_rinex_v3.py::... (23 tests)
# ✅ test_rinex_integration.py::... (20+ tests)
```

### Full Test Suite

```bash
# Run all tests including slow ones
pytest -v

# With coverage report
pytest --cov=canvod.readers --cov-report=html --cov-report=term
```

### Specific Test Categories

```bash
# 1. Package structure tests
pytest tests/test_meta.py -v

# 2. Core GNSS specifications
pytest tests/test_gnss_core.py -v

# 3. Signal mapping system
pytest tests/test_signal_mapping.py -v

# 4. RINEX reading
pytest tests/test_rinex_v3.py -v

# 5. Integration tests
pytest tests/test_rinex_integration.py -v
```

### By Test Class

```bash
# Signal mapper only
pytest tests/test_signal_mapping.py::TestSignalIDMapper -v

# Constellation classes only
pytest tests/test_signal_mapping.py::TestConstellations -v

# RINEX integration only
pytest tests/test_rinex_integration.py::TestRINEXIntegration -v
```

### Individual Tests

```bash
# Single test
pytest tests/test_signal_mapping.py::TestSignalIDMapper::test_create_signal_id_gps -v
```

---

## Test Coverage

### Expected Test Counts

| Test File | Tests | Purpose |
|-----------|-------|---------|
| test_meta.py | 8 | Package structure & imports |
| test_gnss_core.py | 28 | Core modules (constants, exceptions, etc.) |
| **test_signal_mapping.py** | **60+** | **Signal mapping system** |
| test_rinex_v3.py | 23 | RINEX v3 functionality |
| **test_rinex_integration.py** | **25+** | **Integration tests** |
| **TOTAL** | **~144** | **Complete test suite** |

### Test Categories

#### 1. Signal Mapping Tests (test_signal_mapping.py)

**TestSignalIDMapper** (18 tests):
- Initialization
- System band coverage
- Signal ID creation (GPS, Galileo, GLONASS, BeiDou)
- Auxiliary observation handling (X1)
- Signal ID parsing
- Band frequency retrieval
- Band bandwidth retrieval
- Overlapping group identification
- Auxiliary detection

**TestBands** (8 tests):
- Initialization
- BAND_PROPERTIES structure
- SYSTEM_BANDS structure
- OVERLAPPING_GROUPS structure
- All systems present
- GLONASS FDMA aggregation

**TestConstellations** (12 tests):
- GPS initialization & static SVs
- Galileo initialization
- GLONASS initialization & FDMA equations
- BeiDou initialization
- IRNSS initialization
- QZSS initialization
- SBAS initialization
- Frequency lookup tables

**TestIntegration** (3 tests):
- Signal mapper in RINEX context
- Overlapping group filtering
- Frequency consistency

**TestWikipediaCache** (3 tests):
- Cache initialization
- GPS fetch (slow, network)
- Galileo fetch (slow, network)

#### 2. RINEX Integration Tests (test_rinex_integration.py)

**TestRINEXIntegration** (14 tests):
- Header parsing with signal mapping
- Rnxv3Obs initialization
- Signal ID creation from RINEX
- Dataset creation with signal mapping
- Band frequencies in dataset
- Band coordinate validation
- System coordinate matching
- Overlapping group filtering
- Multiple data variables
- Epoch iteration
- File hash generation
- Global attributes
- Full file processing (slow)

**TestSignalMappingEdgeCases** (7 tests):
- Unknown system handling
- Malformed observation codes
- Empty signal IDs
- Nonexistent bands
- Error handling

---

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Error: No module named 'xarray'
# Solution: Install dependencies
uv sync
# or
pip install -e ".[dev]"
```

#### 2. Test Data Not Found
```bash
# Error: Test file not found: .../*.25o
# Solution: Ensure test data is in correct location
ls tests/test_data/01_Rosalia/02_canopy/01_GNSS/01_raw/25001/
```

#### 3. Slow Tests Timeout
```bash
# Skip slow tests
pytest -m "not slow" -v
```

#### 4. Network Tests Fail
```bash
# Wikipedia cache tests require network
# They're marked with @pytest.mark.skipif by default
# To run them, remove the skip decorator
```

---

## Test Markers

### Available Markers

```python
@pytest.mark.slow          # Long-running tests
@pytest.mark.integration   # Integration tests
```

### Using Markers

```bash
# Skip slow tests
pytest -m "not slow"

# Run only slow tests
pytest -m "slow"

# Run only integration tests
pytest -m "integration"

# Skip slow AND integration
pytest -m "not slow and not integration"
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.13'
    
    - name: Install dependencies
      run: |
        cd packages/canvod-readers
        pip install -e ".[dev]"
    
    - name: Run tests
      run: |
        cd packages/canvod-readers
        pytest -v -m "not slow" --cov=canvod.readers --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

---

## Development Workflow

### 1. Make Changes
```bash
# Edit code in src/canvod/readers/
vim src/canvod/readers/gnss_specs/signals.py
```

### 2. Run Relevant Tests
```bash
# Test your changes
pytest tests/test_signal_mapping.py -v
```

### 3. Run Full Suite
```bash
# Before committing
pytest -v -m "not slow"
```

### 4. Check Coverage
```bash
# Ensure >85% coverage
pytest --cov=canvod.readers --cov-report=term-missing
```

### 5. Format Code
```bash
# Use ruff
ruff check src/
ruff format src/
```

---

## Performance Benchmarking

### Timing Tests

```bash
# Time test execution
pytest --durations=10

# Profile slow tests
pytest --profile
```

### Memory Usage

```bash
# Monitor memory with pytest-memray (if installed)
pytest --memray
```

---

## Test Data Management

### RINEX Test Files

Located in `tests/test_data/01_Rosalia/.../*.25o`

**Current files:**
- ~15-minute RINEX observation files
- Size: ~1.5MB each
- Format: RINEX v3.04

**Adding new test files:**
1. Place in `tests/test_data/`
2. Update fixtures in `conftest.py`
3. Reference in tests

---

## Expected Results

### After Full Migration

```bash
$ pytest -v

tests/test_meta.py::TestPackageStructure::... PASSED
tests/test_meta.py::TestPackageMetadata::... PASSED
tests/test_gnss_core.py::TestExceptions::... PASSED
tests/test_gnss_core.py::TestConstants::... PASSED
tests/test_gnss_core.py::TestModels::... PASSED
tests/test_gnss_core.py::TestSignalMapper::... PASSED
tests/test_gnss_core.py::TestUtils::... PASSED
tests/test_gnss_core.py::TestMetadata::... PASSED
tests/test_signal_mapping.py::TestSignalIDMapper::... PASSED
tests/test_signal_mapping.py::TestBands::... PASSED
tests/test_signal_mapping.py::TestConstellations::... PASSED
tests/test_signal_mapping.py::TestIntegration::... PASSED
tests/test_rinex_v3.py::TestRnxv3Header::... PASSED
tests/test_rinex_v3.py::TestRnxv3Obs::... PASSED
tests/test_rinex_v3.py::TestSignalMapping::... PASSED
tests/test_rinex_integration.py::TestRINEXIntegration::... PASSED
tests/test_rinex_integration.py::TestSignalMappingEdgeCases::... PASSED

====================== 144 passed in 25.34s ======================
```

### Coverage Target

**Minimum**: 85%  
**Target**: 90%+

```
Name                                     Stmts   Miss  Cover
------------------------------------------------------------
src/canvod/readers/__init__.py              15      0   100%
src/canvod/readers/base.py                  45      2    96%
src/canvod/readers/gnss_specs/...          450     35    92%
src/canvod/readers/rinex/v3_04.py          580     65    89%
------------------------------------------------------------
TOTAL                                     1090     102    91%
```

---

## Getting Help

### Test Failures

1. Check error message carefully
2. Run single failing test: `pytest tests/test_file.py::test_name -v`
3. Add print statements if needed
4. Check test data exists
5. Verify dependencies installed

### Questions

- Check documentation in `tests/README.md`
- Review test examples in existing tests
- Ask in project discussions

---

**Last Updated**: January 9, 2026  
**Test Suite Version**: Complete with signal mapping  
**Status**: ✅ Ready for testing
