# Testing Audit & Strategy Plan for canvodpy (2026)

**Date:** 2026-02-03  
**Purpose:** Comprehensive testing strategy for modern Python scientific package

---

## 📊 Current State: Test Audit

### Existing Test Structure

**Total:** 32 test files across 8 packages

```
canvod-aux       : 12 files  ⭐ Best coverage
canvod-grids     :  2 files  ⚠️  Needs expansion
canvod-readers   :  5 files  ✅ Good
canvod-store     :  1 file   🚨 Minimal
canvod-utils     :  3 files  ✅ Good  
canvod-viz       :  3 files  ✅ Good (just fixed!)
canvod-vod       :  3 files  ⚠️  Needs expansion
canvodpy-umbrella:  3 files  ✅ Good
```

### Test Categories Present

#### ✅ **Unit Tests** (Present)
- `test_internal_*.py` - Internal utilities
- `test_*_calculator.py` - Core algorithms
- `test_signal_mapping.py` - Logic tests
- Component isolation and mocking

#### ✅ **Integration Tests** (Present)
- `test_integration*.py` - Cross-package workflows
- `test_rinex_integration.py` - File reading + processing
- `test_viz/test_integration.py` - End-to-end visualization

#### ✅ **Meta/Smoke Tests** (Present)
- `test_*_meta.py` - Import checks, version checks
- Package structure validation
- Quick sanity checks

#### ⚠️ **Configuration Tests** (Present but Limited)
- `test_configuration.py` - Settings management
- `test_config.py` - Config loading
- **Missing:** Environment variation tests

---

## 🚨 Critical Gaps (2026 Standards)

### 1. **Property-Based Testing** ❌ Missing
Modern Python uses **Hypothesis** for generative testing.

**What we need:**
```python
# Example: Grid creation property tests
from hypothesis import given
from hypothesis.strategies import floats, integers

@given(
    angular_resolution=floats(min_value=1.0, max_value=90.0),
    cutoff_theta=floats(min_value=0.0, max_value=np.pi/2)
)
def test_grid_creation_properties(angular_resolution, cutoff_theta):
    """Grid should always have positive cell count."""
    grid = create_hemigrid(angular_resolution, "equal_area", cutoff_theta)
    assert grid.ncells > 0
    assert grid.ncells < 10000  # Reasonable upper bound
```

**Packages needing this:**
- `canvod-grids` - Grid generation invariants
- `canvod-vod` - VOD calculation properties
- `canvod-aux` - Interpolation behavior

---

### 2. **Performance/Benchmark Tests** ❌ Missing
Scientific code needs **performance regression detection**.

**What we need:**
```python
# Using pytest-benchmark
def test_large_grid_performance(benchmark):
    """Equal-area grid with 1000 cells should create in <100ms."""
    result = benchmark(create_hemigrid, 
                      angular_resolution=2, 
                      grid_type='equal_area')
    assert result.ncells > 900

# Memory profiling
@pytest.mark.memory
def test_vod_processing_memory():
    """VOD processing shouldn't exceed 500MB for typical dataset."""
    # Use memory_profiler or tracemalloc
    pass
```

**Packages needing this:**
- `canvod-grids` - Grid creation speed
- `canvod-vod` - VOD calculation throughput
- `canvod-viz` - Rendering performance
- `canvod-store` - I/O performance

---

### 3. **Parametric/Data-Driven Tests** ⚠️ Limited
Use **pytest.mark.parametrize** extensively.

**Current:** Some use, but not systematic  
**Need:** Comprehensive parameter sweeps

```python
@pytest.mark.parametrize("grid_type,min_cells", [
    ("equal_area", 100),
    ("htm", 50),
    ("geodesic", 80),
])
@pytest.mark.parametrize("resolution", [2, 4, 8, 16])
def test_grid_coverage(grid_type, resolution, min_cells):
    """All grid types should provide adequate coverage."""
    grid = create_hemigrid(resolution, grid_type)
    assert grid.ncells >= min_cells
```

---

### 4. **Regression Tests** ❌ Missing
Lock in known-good outputs.

**What we need:**
- **Golden file tests** for VOD calculations
- **Snapshot testing** for visualizations
- **Numerical regression** for grid algorithms

```python
def test_vod_regression_golden_output(snapshot):
    """VOD calculation should match golden reference."""
    vod_output = calculate_vod(test_input)
    # pytest-snapshot or pytest-regtest
    snapshot.assert_match(vod_output.to_dict(), "vod_golden.json")
```

---

### 5. **Fixtures & Test Data Management** ⚠️ Needs Organization

**Current issues:**
- Test data scattered (some in submodules, some inline)
- No centralized fixture library
- Duplication across packages

**What we need:**
```
canvodpy/
  tests/
    fixtures/           # Shared fixtures
      grids.py          # Grid fixtures for all packages
      rinex_data.py     # Sample RINEX data
      aux_data.py       # Ephemeris/clock data
    conftest.py         # Root conftest with shared fixtures
```

---

### 6. **Error & Edge Case Testing** ⚠️ Incomplete

**Present:**
- `test_viz/test_integration.py::TestDataEdgeCases` ✅
- Some invalid input tests

**Missing:**
- Systematic boundary value testing
- Error message validation
- Exception type checking
- Recovery/fallback behavior

```python
def test_grid_invalid_resolution():
    """Should raise clear error for invalid resolution."""
    with pytest.raises(ValueError, match="resolution must be positive"):
        create_hemigrid(angular_resolution=-5, grid_type='equal_area')
```

---

### 7. **Doctests** ❌ Missing
Documentation examples should be tested!

```python
def create_hemigrid(angular_resolution: float, grid_type: str) -> GridData:
    """
    Create a hemisphere grid.
    
    Examples
    --------
    >>> grid = create_hemigrid(4, 'equal_area')
    >>> grid.ncells > 0
    True
    >>> grid.grid_type
    'equal_area'
    """
```

**Run with:** `pytest --doctest-modules`

---

### 8. **Contract/Type Testing** ⚠️ Basic
Modern Python uses **mypy + pytest-mypy-plugins**.

**Current:** Type hints present, but not tested  
**Need:** Runtime type validation + static checking

```python
# pytest-mypy-plugins config
@pytest.mark.mypy_testing
def test_grid_type_signatures():
    """Type signatures should be correct."""
    # Validates that type hints match runtime behavior
```

---

### 9. **Coverage Gaps**

**Current coverage by package** (estimated from audit):
```
canvod-aux:     ~60%  ⚠️  Missing: download retry logic, error handling
canvod-grids:   ~40%  🚨 Missing: geodesic, HEALPix, fibonacci grids
canvod-readers: ~50%  ⚠️  Missing: corrupted file handling
canvod-store:   ~10%  🚨 Missing: almost everything!
canvod-utils:   ~70%  ✅ Good
canvod-viz:     ~66%  ✅ Good (just improved)
canvod-vod:     ~45%  ⚠️  Missing: edge cases, validation
```

**Target:** 80% line coverage, 90% branch coverage for scientific code

---

### 10. **CI/CD Integration** ❌ Not Visible
Need GitHub Actions workflows for:
- ✅ Test matrix (Python 3.11, 3.12, 3.13)
- ✅ OS matrix (Linux, macOS, Windows?)
- ✅ Dependency updates (Dependabot)
- ❌ Performance tracking
- ❌ Coverage reporting (Codecov/Coveralls)
- ❌ Documentation builds

---

## 📋 Recommended Testing Strategy (2026)

### Tier 1: Critical Path (Immediate)

#### A. **Core Algorithm Tests**
**Priority: HIGHEST**

1. **Grid Operations** (`canvod-grids`)
   - [ ] Property tests for all grid types
   - [ ] Boundary value tests (resolution limits)
   - [ ] Grid storage/loading round-trip tests
   - [ ] Solid angle conservation tests
   - [ ] Cell adjacency tests

2. **VOD Calculation** (`canvod-vod`)
   - [ ] Golden file regression tests
   - [ ] Edge case tests (NaN handling, sparse data)
   - [ ] Numerical stability tests
   - [ ] Performance benchmarks

3. **Store Operations** (`canvod-store`) 🚨 **URGENT**
   - [ ] Basic CRUD operations
   - [ ] Concurrency tests
   - [ ] Data integrity tests
   - [ ] Rollback/recovery tests

#### B. **Integration Workflows**
- [ ] RINEX → Aux → VOD → Grid → Store (end-to-end)
- [ ] Multi-site processing
- [ ] Large dataset handling
- [ ] Error propagation across pipeline

### Tier 2: Robustness (High Priority)

#### C. **Error Handling & Validation**
- [ ] Input validation tests (all public APIs)
- [ ] Network failure simulation (aux downloads)
- [ ] Corrupted file handling
- [ ] Out-of-memory scenarios
- [ ] Disk full scenarios

#### D. **Property-Based Testing**
- [ ] Install Hypothesis: `uv add --group dev hypothesis`
- [ ] Write property tests for:
  - Grid invariants
  - VOD calculation properties
  - Interpolation behavior
  - Coordinate transformations

### Tier 3: Quality & Performance (Medium Priority)

#### E. **Performance Tests**
- [ ] Install pytest-benchmark: `uv add --group dev pytest-benchmark`
- [ ] Benchmark critical paths:
  - Grid creation
  - VOD calculation
  - Data aggregation
  - Visualization rendering

#### F. **Regression Tests**
- [ ] Install pytest-regtest: `uv add --group dev pytest-regtest`
- [ ] Create golden files for:
  - VOD outputs
  - Grid structures
  - Aux data processing

#### G. **Doctests**
- [ ] Add docstring examples to all public APIs
- [ ] Enable doctest in pytest config
- [ ] Run `pytest --doctest-modules`

### Tier 4: Infrastructure (Lower Priority)

#### H. **Test Organization**
- [ ] Create `tests/fixtures/` for shared fixtures
- [ ] Consolidate test data management
- [ ] Document testing patterns in `CONTRIBUTING.md`

#### I. **CI/CD**
- [ ] Create `.github/workflows/tests.yml`
- [ ] Matrix testing (Python versions, OS)
- [ ] Coverage reporting
- [ ] Performance tracking

#### J. **Documentation**
- [ ] Test coverage badges in README
- [ ] Testing guide for contributors
- [ ] Examples using actual test data

---

## 🛠️ Tools to Add (Modern 2026 Stack)

### Testing Frameworks
```toml
[dependency-groups]
dev = [
    # Existing
    "pytest>=9.0.1",
    "pytest-cov>=7.0.0",
    "pytest-mock>=3.12.0",
    
    # ADD THESE:
    "hypothesis>=6.100",           # Property-based testing
    "pytest-benchmark>=4.0",       # Performance testing
    "pytest-regtest>=2.1",         # Regression testing
    "pytest-xdist>=3.5",           # Parallel test execution
    "pytest-timeout>=2.2",         # Timeout protection
    "pytest-randomly>=3.15",       # Random test order
    "pytest-mypy-plugins>=3.1",    # Type testing
    "pytest-snapshot>=0.9",        # Snapshot testing
]
```

### Coverage & Reporting
```toml
dev = [
    "coverage[toml]>=7.4",         # Coverage tracking
    "pytest-html>=4.1",            # HTML reports
    "pytest-json-report>=1.5",     # JSON reports
]
```

### Quality Assurance
```toml
dev = [
    "mypy>=1.10",                  # Type checking
    "ruff>=0.14.5",                # Linting (already have)
    "interrogate>=1.7",            # Docstring coverage
]
```

---

## 📈 Success Metrics

**Phase 1 (Month 1):**
- ✅ 80% line coverage on `canvod-grids`
- ✅ 80% line coverage on `canvod-vod`
- ✅ 50% line coverage on `canvod-store` (from 10%)
- ✅ Property tests for core algorithms
- ✅ Golden file tests for VOD

**Phase 2 (Month 2):**
- ✅ 85% overall line coverage
- ✅ Performance benchmarks established
- ✅ CI/CD pipeline operational
- ✅ Doctest coverage >50%

**Phase 3 (Month 3):**
- ✅ 90% branch coverage
- ✅ Full error handling test suite
- ✅ Performance regression tracking
- ✅ Complete integration test matrix

---

## 🎯 Quick Wins (Start Here)

### This Week
1. **Fix `canvod-store` tests** - Only 1 test file! Add:
   - Basic read/write tests
   - Grid storage round-trip test
   - VOD dataset storage test

2. **Add property tests to `canvod-grids`**
   - Install Hypothesis
   - Test grid creation properties
   - Test solid angle conservation

3. **Create shared fixture library**
   - Move common fixtures to root `conftest.py`
   - Reduce duplication

### Next Week
4. **Add performance benchmarks**
   - Grid creation
   - VOD calculation
   - Establish baseline

5. **Golden file tests for VOD**
   - Create reference outputs
   - Add regression tests

6. **Complete edge case coverage**
   - NaN handling
   - Empty datasets
   - Boundary values

---

## 📚 Resources

**Modern Python Testing (2026):**
- **Hypothesis**: https://hypothesis.readthedocs.io/
- **pytest-benchmark**: https://pytest-benchmark.readthedocs.io/
- **Real Python Testing Guide**: https://realpython.com/pytest-python-testing/

**Scientific Python Testing:**
- **SciPy Testing**: https://docs.scipy.org/doc/scipy/dev/contributor/development_workflow.html#testing
- **NumPy Testing**: https://numpy.org/devdocs/reference/testing.html

**CI/CD:**
- **GitHub Actions for Python**: https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python

---

## 🤝 Implementation Priority

**Critical (Do First):**
1. 🚨 `canvod-store` - Expand from 1 to ~10 test files
2. 🚨 Property-based tests for grids
3. 🚨 Golden file regression for VOD

**High (Do Next):**
4. Performance benchmarks
5. Shared fixture library
6. Error handling tests

**Medium (Then):**
7. Doctests
8. CI/CD pipeline
9. Coverage reporting

**Low (Eventually):**
10. Test documentation
11. Advanced fixtures
12. Integration with external tools

---

**Next Steps:** Choose one item from "Critical" and start implementing!
