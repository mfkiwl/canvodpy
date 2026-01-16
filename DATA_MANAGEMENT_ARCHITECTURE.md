# Data Management Architecture

## Overview

Two separate Git repositories as submodules for different purposes:

```
canvodpy/                           # Main repository
├── test-data/                      # Submodule 1: Testing with falsified data
│   ├── valid/                      #   ├─ Baseline files
│   ├── corrupted/                  #   ├─ Intentionally broken
│   └── edge_cases/                 #   └─ Boundary conditions
│
└── examples/                       # Submodule 2: Demos with real data
    ├── rosalia/                    #   ├─ Forest site data
    ├── tuwien/                     #   ├─ Urban site data
    └── site_metadata.json          #   └─ Site information
```

---

## Purpose Separation

### 🧪 Test Data (`test-data/`)

**Purpose**: Validation testing with falsified/corrupted files

**Usage**:
- pytest fixtures via `conftest.py`
- Error handling tests
- Validation logic verification
- Boundary condition testing

**Content**:
- Corrupted RINEX files (truncated headers, invalid epochs)
- Corrupted auxiliary files (bad coordinates, clock jumps)
- Edge cases (minimal files, sparse observations)

**Access**:
```python
def test_corrupted_header(test_data_dir):
    corrupted = test_data_dir / "corrupted/rinex/truncated_header.rnx"
    with pytest.raises(HeaderParseError):
        obs = Rnxv3Obs(fpath=corrupted)
```

### 📚 Examples (`examples/`)

**Purpose**: Documentation and demos with clean real-world data

**Usage**:
- Interactive notebooks (marimo)
- Documentation examples
- Tutorial walkthroughs
- API demonstrations

**Content**:
- Complete real observation datasets
- Auxiliary files (SP3, CLK)
- Site metadata and coordinates
- Processed outputs

**Access**:
```python
def demo_pipeline(examples_dir):
    rinex = examples_dir / "rosalia/2023/001/rinex/canopy_20230010000.rnx"
    obs = Rnxv3Obs(fpath=rinex)
    # ... demo code
```

---

## Repository Details

### Test Data Repository

**Name**: `canvodpy-test-data`  
**URL**: `https://github.com/your-org/canvodpy-test-data`  
**Size**: Small (~100MB)  
**Update Frequency**: As new error cases discovered  
**Git LFS**: Optional (most files small)

**Structure**:
```
test-data/
├── README.md                       # File manifest
├── valid/
│   ├── rinex/
│   │   └── baseline.rnx            # Known-good reference
│   └── aux/
│       ├── baseline.SP3
│       └── baseline.CLK
├── corrupted/
│   ├── rinex/
│   │   ├── truncated_header.rnx    # Missing END OF HEADER
│   │   ├── invalid_epochs.rnx      # Non-monotonic times
│   │   ├── bad_satellites.rnx      # Invalid SV IDs
│   │   └── corrupt_observations.rnx # Malformed data
│   └── aux/
│       ├── bad_coordinates.SP3     # Positions > Earth radius
│       └── discontinuous.CLK       # Clock jumps
└── edge_cases/
    ├── minimal.rnx                 # 1 epoch, 1 SV
    ├── sparse_observations.rnx     # Large gaps
    └── multi_gnss.rnx              # All constellations
```

### Examples Repository

**Name**: `canvodpy-examples`  
**URL**: `https://github.com/your-org/canvodpy-examples`  
**Size**: Large (~1-2GB with LFS)  
**Update Frequency**: As new sites added  
**Git LFS**: Required (large RINEX files)

**Structure**:
```
examples/
├── README.md                       # Site documentation
├── site_metadata.json              # All site info
├── rosalia/                        # Austrian forest site
│   ├── site_info.md
│   └── 2023/
│       └── 001/                    # DOY 001
│           ├── rinex/
│           │   ├── canopy_20230010000.rnx      # 50MB
│           │   └── reference_20230010000.rnx   # 50MB
│           ├── aux/
│           │   ├── COD0MGXFIN_*.SP3            # 10MB
│           │   └── COD0MGXFIN_*.CLK            # 5MB
│           └── outputs/
│               └── augmented_*.nc              # 100MB
└── tuwien/                         # Urban campus site
    └── 2024/
        └── 150/
            └── rinex/
                └── tuwien_20241500000.rnx
```

---

## Setup Instructions

### For Developers (First Time)

```bash
# Clone with all submodules
git clone --recurse-submodules https://github.com/your-org/canvodpy.git
cd canvodpy

# Or clone then initialize
git clone https://github.com/your-org/canvodpy.git
cd canvodpy
git submodule update --init --recursive

# If using Git LFS
cd test-data && git lfs pull
cd ../examples && git lfs pull
```

### For Users (Selective)

```bash
# Clone main repo
git clone https://github.com/your-org/canvodpy.git
cd canvodpy

# Option 1: Only for running tests
git submodule update --init test-data

# Option 2: Only for running demos
git submodule update --init examples

# Option 3: Both
git submodule update --init test-data examples
```

---

## Integration with Code

### conftest.py (Root)

```python
# Submodule paths
TEST_DATA_ROOT = Path(__file__).parent / "test-data"
EXAMPLES_ROOT = Path(__file__).parent / "examples"

# Test data fixtures
@pytest.fixture
def test_data_dir() -> Path:
    if not TEST_DATA_ROOT.exists():
        pytest.skip("Test data submodule not initialized")
    return TEST_DATA_ROOT

# Example data fixtures
@pytest.fixture
def examples_dir() -> Path:
    if not EXAMPLES_ROOT.exists():
        pytest.skip("Examples submodule not initialized")
    return EXAMPLES_ROOT
```

### Notebooks

```python
# In complete_pipeline.py
from pathlib import Path

# Default to examples submodule
EXAMPLES_DIR = Path(__file__).parent.parent.parent.parent / "examples"

# Or allow user to configure
rinex_dir_input = mo.ui.text(
    value=str(EXAMPLES_DIR / "rosalia/2023/001/rinex"),
    label="RINEX Data Directory:",
)
```

### Tests

```python
# Using test-data
def test_corrupted_file(test_data_dir):
    corrupted = test_data_dir / "corrupted/rinex/truncated_header.rnx"
    with pytest.raises(HeaderParseError):
        obs = Rnxv3Obs(fpath=corrupted)

# Using examples
@pytest.mark.requires_examples
def test_integration_rosalia(examples_dir):
    rinex = examples_dir / "rosalia/2023/001/rinex/canopy_20230010000.rnx"
    obs = Rnxv3Obs(fpath=rinex)
    assert len(obs.to_ds().epoch) > 0
```

---

## Workflow

### Adding Test Data

```bash
cd test-data

# Create corrupted file
cp valid/rinex/baseline.rnx corrupted/rinex/new_error.rnx
# ... corrupt it

# Update manifest
vim README.md

# Commit
git add corrupted/rinex/new_error.rnx README.md
git commit -m "Add new_error test case"
git push

# Update main repo reference
cd ..
git add test-data
git commit -m "Update test-data with new error case"
git push
```

### Adding Example Data

```bash
cd examples

# Add new site
mkdir -p new_site/2024/200/{rinex,aux}
cp /path/to/data/* new_site/2024/200/rinex/

# Update metadata
vim site_metadata.json

# Commit (Git LFS handles large files)
git add new_site/ site_metadata.json
git commit -m "Add new_site example data"
git push

# Update main repo reference
cd ..
git add examples
git commit -m "Update examples with new_site"
git push
```

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: true      # Clone submodules
          lfs: true             # Pull LFS files
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          pip install uv
          uv sync
      
      - name: Run tests
        run: uv run pytest
```

---

## Benefits

### ✅ Separation of Concerns
- Test data separate from demo data
- Each has clear purpose
- Independent versioning

### ✅ Size Management
- Main repo stays small
- Large files in LFS
- Optional cloning (selective submodules)

### ✅ Independent Development
- Test data evolves with test suite
- Example data added as sites added
- No coupling between them

### ✅ Easy Maintenance
- Clear ownership per repo
- Focused PRs
- Simple to update

---

## Summary

**Two submodules, two purposes:**

| Aspect | test-data | examples |
|--------|-----------|----------|
| Purpose | Testing | Documentation |
| Content | Falsified files | Real data |
| Size | Small (~100MB) | Large (~2GB) |
| LFS | Optional | Required |
| Users | Developers | Everyone |
| Update | With tests | With sites |

**Simple commands:**

```bash
# Setup
git clone --recurse-submodules <repo>

# Update
git submodule update --remote

# Use in tests
pytest  # Uses test-data/

# Use in demos
marimo edit docs/notebooks/complete_pipeline.py  # Uses examples/
```

**Clean, organized, purposeful!**
