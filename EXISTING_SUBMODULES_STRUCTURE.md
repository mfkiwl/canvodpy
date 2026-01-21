# Existing Submodules Structure

## ✅ Already Configured!

Your submodules are already set up at:

```
canvodpy/
├── demo/                                    # Submodule: canvodpy-demo
│   └── data/
│       ├── 00_aux_files/
│       │   ├── 01_SP3/
│       │   └── 02_CLK/
│       └── 01_Rosalia/
│           ├── 01_reference/01_GNSS/01_raw/
│           └── 02_canopy/01_GNSS/01_raw/
│
└── packages/canvod-readers/tests/test_data/ # Submodule: canvodpy-test-data
    └── valid/
        ├── aux/
        │   └── 00_aux_files/
        │       ├── 01_SP3/
        │       └── 02_CLK/
        └── rinex_v3_04/
            └── 01_Rosalia/
                ├── 01_reference/
                └── 02_canopy/
```

## Git Configuration

From `.gitmodules`:

```ini
[submodule "demo"]
    path = demo
    url = https://github.com/nfb2021/canvodpy-demo.git

[submodule "packages/canvod-readers/tests/test_data"]
    path = packages/canvod-readers/tests/test_data
    url = https://github.com/nfb2021/canvodpy-test-data.git
```

---

## Usage Mapping

### 1. Test Data (for pytest)
**Location**: `packages/canvod-readers/tests/test_data/`  
**Repository**: `canvodpy-test-data`  
**Purpose**: Validation testing

**Structure**:
```
test_data/
└── valid/
    ├── aux/00_aux_files/
    │   ├── 01_SP3/
    │   └── 02_CLK/
    └── rinex_v3_04/01_Rosalia/
        ├── 01_reference/
        └── 02_canopy/
```

**Next Steps**:
- Add `corrupted/` directory for falsified files
- Add `edge_cases/` directory for boundary conditions

### 2. Demo Data (for examples/notebooks)
**Location**: `demo/`  
**Repository**: `canvodpy-demo`  
**Purpose**: Documentation and demos

**Structure**:
```
demo/data/
├── 00_aux_files/
│   ├── 01_SP3/
│   └── 02_CLK/
└── 01_Rosalia/
    ├── 01_reference/01_GNSS/01_raw/
    └── 02_canopy/01_GNSS/01_raw/
```

---

## Updated Configuration

### conftest.py (Root)

```python
"""Pytest configuration for canvodpy workspace."""

from pathlib import Path
import pytest


# Existing submodule paths
TEST_DATA_ROOT = Path(__file__).parent / "packages/canvod-readers/tests/test_data"
DEMO_DATA_ROOT = Path(__file__).parent / "demo"


# ============================================================================
# Test Data Fixtures (for validation testing)
# ============================================================================

@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Root directory for test data (canvodpy-test-data submodule)."""
    if not TEST_DATA_ROOT.exists():
        pytest.skip("Test data submodule not initialized")
    return TEST_DATA_ROOT


@pytest.fixture(scope="session")
def valid_test_data_dir(test_data_dir: Path) -> Path:
    """Valid test data directory."""
    return test_data_dir / "valid"


@pytest.fixture(scope="session")
def valid_rinex_dir(valid_test_data_dir: Path) -> Path:
    """Valid RINEX test files."""
    return valid_test_data_dir / "rinex_v3_04/01_Rosalia"


@pytest.fixture(scope="session")
def valid_aux_dir(valid_test_data_dir: Path) -> Path:
    """Valid auxiliary test files."""
    return valid_test_data_dir / "aux/00_aux_files"


@pytest.fixture
def rosalia_reference_rinex(valid_rinex_dir: Path) -> Path:
    """Rosalia reference RINEX file."""
    rinex_dir = valid_rinex_dir / "01_reference"
    files = list(rinex_dir.glob("*.rnx")) + list(rinex_dir.glob("*.RNX"))
    if not files:
        pytest.skip(f"No RINEX files in {rinex_dir}")
    return files[0]


@pytest.fixture
def rosalia_canopy_rinex(valid_rinex_dir: Path) -> Path:
    """Rosalia canopy RINEX file."""
    rinex_dir = valid_rinex_dir / "02_canopy"
    files = list(rinex_dir.glob("*.rnx")) + list(rinex_dir.glob("*.RNX"))
    if not files:
        pytest.skip(f"No RINEX files in {rinex_dir}")
    return files[0]


@pytest.fixture
def sample_sp3_file(valid_aux_dir: Path) -> Path:
    """Sample SP3 file."""
    sp3_dir = valid_aux_dir / "01_SP3"
    files = list(sp3_dir.glob("*.SP3")) + list(sp3_dir.glob("*.sp3"))
    if not files:
        pytest.skip(f"No SP3 files in {sp3_dir}")
    return files[0]


@pytest.fixture
def sample_clk_file(valid_aux_dir: Path) -> Path:
    """Sample CLK file."""
    clk_dir = valid_aux_dir / "02_CLK"
    files = list(clk_dir.glob("*.CLK")) + list(clk_dir.glob("*.clk"))
    if not files:
        pytest.skip(f"No CLK files in {clk_dir}")
    return files[0]


# ============================================================================
# Demo Data Fixtures (for examples/documentation)
# ============================================================================

@pytest.fixture(scope="session")
def demo_data_dir() -> Path:
    """Root directory for demo data (canvodpy-demo submodule)."""
    if not DEMO_DATA_ROOT.exists():
        pytest.skip("Demo data submodule not initialized")
    return DEMO_DATA_ROOT


@pytest.fixture(scope="session")
def demo_rosalia_dir(demo_data_dir: Path) -> Path:
    """Rosalia demo data directory."""
    return demo_data_dir / "data/01_Rosalia"


@pytest.fixture(scope="session")
def demo_aux_dir(demo_data_dir: Path) -> Path:
    """Demo auxiliary files directory."""
    return demo_data_dir / "data/00_aux_files"


@pytest.fixture
def demo_rosalia_reference(demo_rosalia_dir: Path) -> Path:
    """Demo Rosalia reference RINEX."""
    rinex_dir = demo_rosalia_dir / "01_reference/01_GNSS/01_raw"
    files = list(rinex_dir.rglob("*.rnx")) + list(rinex_dir.rglob("*.RNX"))
    if not files:
        pytest.skip(f"No RINEX files in {rinex_dir}")
    return files[0]


@pytest.fixture
def demo_rosalia_canopy(demo_rosalia_dir: Path) -> Path:
    """Demo Rosalia canopy RINEX."""
    rinex_dir = demo_rosalia_dir / "02_canopy/01_GNSS/01_raw"
    files = list(rinex_dir.rglob("*.rnx")) + list(rinex_dir.rglob("*.RNX"))
    if not files:
        pytest.skip(f"No RINEX files in {rinex_dir}")
    return files[0]


# Marks for selective testing
requires_test_data = pytest.mark.skipif(
    not TEST_DATA_ROOT.exists(),
    reason="Test data submodule not initialized"
)

requires_demo_data = pytest.mark.skipif(
    not DEMO_DATA_ROOT.exists(),
    reason="Demo data submodule not initialized"
)
```

---

## Updating Notebook

Update `canvodpy/docs/notebooks/complete_pipeline.py`:

```python
# Default to demo submodule
DEMO_DIR = Path(__file__).parent.parent.parent.parent / "demo/data"
default_rinex_dir = DEMO_DIR / "01_Rosalia/01_reference/01_GNSS/01_raw"
default_aux_dir = DEMO_DIR / "00_aux_files"
```

---

## Recommended Additions

### To test_data repository

Add these directories to support full test coverage:

```bash
cd packages/canvod-readers/tests/test_data

# Create corrupted data directory
mkdir -p corrupted/{rinex,aux}

# Create edge cases directory
mkdir -p edge_cases

# Commit
git add .
git commit -m "Add structure for corrupted and edge case tests"
git push
```

### To demo repository

Already well-structured! Consider adding:

```bash
cd demo

# Add site metadata
cat > data/site_metadata.json << 'EOF'
{
  "rosalia": {
    "name": "Rosalia Forest Site",
    "location": {"lat": 47.73, "lon": 16.30, "elevation": 350.0},
    "receivers": {
      "reference": {"position_ecef": {"x": 4194354.123, "y": 1162180.456, "z": 4647290.789}},
      "canopy": {"position_ecef": {"x": 4194304.678, "y": 1162205.267, "z": 4647245.201}}
    }
  }
}
EOF

# Commit
git add data/site_metadata.json
git commit -m "Add site metadata"
git push
```

---

## Verification

```bash
# Check submodules status
git submodule status

# Should show:
# <hash> demo (HEAD)
# <hash> packages/canvod-readers/tests/test_data (HEAD)

# Update submodules
git submodule update --remote

# Initialize if needed
git submodule update --init --recursive
```

---

## Summary

✅ **Already have**: Both submodules configured  
✅ **Good structure**: Rosalia data with reference/canopy  
✅ **Clear separation**: test_data for testing, demo for examples

**Next actions**:
1. Update `conftest.py` with new fixture paths
2. Update notebook to use `demo/data/` 
3. Add `corrupted/` and `edge_cases/` to test_data
4. Add site metadata to demo
