# canvod-aux Test Suite

Comprehensive test suite for the canvod-aux package.

## Test Structure

```
tests/
├── conftest.py                      # Pytest configuration
├── test_meta.py                     # Package structure and imports
├── test_internal_units.py           # Unit registry tests
├── test_internal_date_utils.py      # Date/time utilities tests
├── test_internal_logger.py          # Logger tests
├── test_interpolation.py            # Interpolation strategy tests
└── test_container.py                # Container and downloader tests
```

## Running Tests

### Install Development Dependencies

```bash
cd /Users/work/Developer/GNSS/canvodpy/packages/canvod-aux
uv pip install -e ".[dev]"
```

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_meta.py
pytest tests/test_internal_units.py
```

### Run Specific Test Class or Function

```bash
pytest tests/test_internal_date_utils.py::TestYYYDOY
pytest tests/test_internal_date_utils.py::TestYYYDOY::test_from_date
```

### Run with Coverage

```bash
pytest --cov=canvod.aux --cov-report=html
```

### Run Only Fast Tests (Skip Slow/Network Tests)

```bash
pytest -m "not slow and not network"
```

## Test Categories

### Unit Tests (Fast)
- `test_meta.py` - Import validation (< 1s)
- `test_internal_units.py` - UREG functionality (< 1s)
- `test_internal_date_utils.py` - YYYYDOY and GPS week (< 1s)
- `test_internal_logger.py` - Logger configuration (< 1s)
- `test_interpolation.py` - Interpolation configs (< 1s)
- `test_container.py` - Data structures (< 1s)

### Integration Tests (Slower)
Currently none - will be added when full file reading/processing tests are implemented.

### Network Tests (Skipped by Default)
Tests that require network access are marked with `@pytest.mark.network` and skipped by default.

## Test Coverage Goals

- **Internal Utilities:** 100% coverage
- **Public API:** 90%+ coverage
- **File Handlers:** 80%+ coverage (requires test data files)
- **Pipeline:** 70%+ coverage (complex dependencies)

## Current Coverage

After Step 8:
- ✅ Internal utilities: Full coverage
- ✅ Interpolation configs: Full coverage
- ✅ Import validation: Full coverage
- ⏳ File handlers: Pending (requires test data)
- ⏳ Pipeline: Pending (requires mocks)

## Adding New Tests

### Template for New Test File

```python
\"\"\"
Tests for <module_name>.

Brief description of what is being tested.
\"\"\"
import pytest
from canvod.aux import <YourClass>


class Test<YourClass>:
    \"\"\"Tests for <YourClass>.\"\"\"
    
    def test_basic_functionality(self):
        \"\"\"Test basic usage.\"\"\"
        obj = <YourClass>()
        assert obj is not None
```

### Test Naming Conventions

- Test files: `test_<module>.py`
- Test classes: `Test<ClassName>`
- Test functions: `test_<what_is_being_tested>`

### Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.slow
def test_large_file_processing():
    ...

@pytest.mark.network
def test_ftp_download():
    ...

@pytest.mark.integration
def test_full_pipeline():
    ...
```

## Continuous Integration

When CI is set up, tests will run on:
- Every push to main branch
- Every pull request
- Nightly for integration tests

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError: No module named 'canvod'`:

```bash
# Install package in development mode
uv pip install -e .
```

### Missing Dependencies

```bash
# Install all dev dependencies
uv pip install -e ".[dev]"
```

### Test Discovery Issues

Make sure:
- Test files start with `test_`
- Test functions start with `test_`
- Test classes start with `Test`

## Future Tests

Planned test additions:
1. File reading tests (requires sample SP3/CLK files)
2. Pipeline integration tests
3. Augmentation workflow tests
4. Error handling tests
5. Performance benchmarks
