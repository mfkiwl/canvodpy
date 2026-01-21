# Your Existing Submodule Structure

## ✅ Already Configured

You have two submodules already set up and working:

```
canvodpy/
├── demo/                                    # canvodpy-demo submodule
│   └── data/
│       ├── 00_aux_files/
│       │   ├── 01_SP3/
│       │   └── 02_CLK/
│       └── 01_Rosalia/
│           ├── 01_reference/01_GNSS/01_raw/
│           │   ├── 25001/  # 2025 day 001 (96 files, 15-min RINEX)
│           │   └── 25002/  # 2025 day 002
│           └── 02_canopy/01_GNSS/01_raw/
│               ├── 25001/
│               └── 25002/
│
└── packages/canvod-readers/tests/test_data/ # canvodpy-test-data submodule
    └── valid/
        ├── aux/00_aux_files/
        │   ├── 01_SP3/
        │   └── 02_CLK/
        └── rinex_v3_04/01_Rosalia/
            ├── 01_reference/01_GNSS/01_raw/
            └── 02_canopy/01_GNSS/01_raw/
```

---

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

## Data Discovery

### Demo Data (Real Files Found!)

**Location**: `demo/data/01_Rosalia/01_reference/01_GNSS/01_raw/25001/`

**Files**: 96 RINEX observation files (`.25o` extension)
- Format: `rref001a00.25o`, `rref001a15.25o`, ... `rref001x45.25o`
- Pattern: 15-minute files covering 24 hours
- Year: 2025 (`.25o` extension)
- Day: 001 (DOY)
- Site: Rosalia reference receiver

**Example filenames**:
```
rref001a00.25o  # 00:00-00:15
rref001a15.25o  # 00:15-00:30
rref001a30.25o  # 00:30-00:45
rref001a45.25o  # 00:45-01:00
rref001b00.25o  # 01:00-01:15
...
rref001x45.25o  # 23:45-00:00
```

**Same structure** for:
- `demo/data/01_Rosalia/01_reference/01_GNSS/01_raw/25002/` (day 002)
- `demo/data/01_Rosalia/02_canopy/01_GNSS/01_raw/25001/` (canopy receiver)
- `demo/data/01_Rosalia/02_canopy/01_GNSS/01_raw/25002/`

### Test Data Structure

**Location**: `packages/canvod-readers/tests/test_data/valid/`

**Structure mirrors demo but currently empty** (ready for population)
- `valid/rinex_v3_04/01_Rosalia/01_reference/01_GNSS/01_raw/`
- `valid/rinex_v3_04/01_Rosalia/02_canopy/01_GNSS/01_raw/`
- `valid/aux/00_aux_files/01_SP3/`
- `valid/aux/00_aux_files/02_CLK/`

**Ready for**:
- `corrupted/` directory (falsified files)
- `edge_cases/` directory (boundary conditions)

---

## Updated conftest.py (✅ Done!)

### Test Data Fixtures

```python
# Root paths
TEST_DATA_ROOT = Path(__file__).parent / "packages/canvod-readers/tests/test_data"
DEMO_ROOT = Path(__file__).parent / "demo"

# Test data fixtures (for pytest)
@pytest.fixture
def rosalia_reference_test_rinex(valid_rinex_dir: Path) -> Path:
    """Rosalia reference RINEX from test_data (any *.25o, *.rnx, *.RNX)."""
    rinex_dir = valid_rinex_dir / "01_reference/01_GNSS/01_raw"
    files = list(rinex_dir.rglob("*.[0-9][0-9]o")) + list(rinex_dir.glob("*.rnx"))
    return files[0]

@pytest.fixture
def rosalia_canopy_test_rinex(valid_rinex_dir: Path) -> Path:
    """Rosalia canopy RINEX from test_data."""
    rinex_dir = valid_rinex_dir / "02_canopy/01_GNSS/01_raw"
    files = list(rinex_dir.rglob("*.[0-9][0-9]o")) + list(rinex_dir.glob("*.rnx"))
    return files[0]
```

### Demo Data Fixtures

```python
# Demo data fixtures (for examples/notebooks)
@pytest.fixture
def demo_rosalia_reference(demo_rosalia_dir: Path) -> Path:
    """Demo Rosalia reference RINEX (first file from 25001 or 25002)."""
    rinex_dir = demo_rosalia_dir / "01_reference/01_GNSS/01_raw"
    files = list(rinex_dir.rglob("*.[0-9][0-9]o"))  # Finds *.25o files
    return files[0]

@pytest.fixture
def demo_rosalia_reference_day(demo_rosalia_dir: Path) -> Path:
    """Full day directory: demo/data/01_Rosalia/01_reference/.../25001/"""
    return demo_rosalia_dir / "01_reference/01_GNSS/01_raw/25001"
```

---

## Usage Examples

### In Tests (using test_data)

```python
def test_read_rinex(rosalia_reference_test_rinex):
    from canvod.readers import Rnxv3Obs
    
    obs = Rnxv3Obs(fpath=rosalia_reference_test_rinex)
    ds = obs.to_ds()
    assert len(ds.epoch) > 0
```

### In Notebooks (using demo)

```python
from pathlib import Path

def _(demo_data_dir):
    # Path to demo data
    rinex_dir = demo_data_dir / "01_Rosalia/01_reference/01_GNSS/01_raw/25001"
    
    # Load first RINEX file
    rinex_files = sorted(rinex_dir.glob("*.25o"))
    obs = Rnxv3Obs(fpath=rinex_files[0])
    
    # Or load all files for the day
    datasets = []
    for rinex_file in rinex_files:
        obs = Rnxv3Obs(fpath=rinex_file)
        datasets.append(obs.to_ds())
```

### Complete Pipeline Demo

```python
# In complete_pipeline.py notebook
from pathlib import Path

# Default to demo submodule
DEMO_DIR = Path(__file__).parent.parent.parent.parent / "demo/data"

default_rinex_dir = DEMO_DIR / "01_Rosalia/01_reference/01_GNSS/01_raw/25001"
default_aux_dir = DEMO_DIR / "00_aux_files"
```

---

## Recommended Next Steps

### 1. Populate test_data with Falsified Files

```bash
cd packages/canvod-readers/tests/test_data

# Add corrupted directory
mkdir -p corrupted/rinex corrupted/aux

# Create corrupted files (examples):
# - truncated_header.25o (missing END OF HEADER)
# - invalid_epochs.25o (non-monotonic times)
# - bad_satellites.25o (invalid SV IDs)

# Add edge cases
mkdir -p edge_cases

# Commit to test-data repo
git add corrupted/ edge_cases/
git commit -m "Add corrupted and edge case test files"
git push

# Update main repo reference
cd /Users/work/Developer/GNSS/canvodpy
git add packages/canvod-readers/tests/test_data
git commit -m "Update test-data submodule"
```

### 2. Add Auxiliary Files to Demo

```bash
cd demo/data/00_aux_files

# Download or copy SP3 and CLK files for 2025-001 and 2025-002
# to match the RINEX data you have

# Commit to demo repo
git add 01_SP3/ 02_CLK/
git commit -m "Add auxiliary files for 2025-001 and 2025-002"
git push

# Update main repo reference
cd /Users/work/Developer/GNSS/canvodpy
git add demo
git commit -m "Update demo submodule with aux files"
```

### 3. Update Notebook Defaults

Already prepared - just verify paths point to demo:

```python
# In canvodpy/docs/notebooks/complete_pipeline.py
DEMO_DIR = Path(__file__).parent.parent.parent.parent / "demo/data"
default_rinex_dir = DEMO_DIR / "01_Rosalia/01_reference/01_GNSS/01_raw/25001"
```

---

## Verification

```bash
# Check submodules initialized
git submodule status
# Should show:
#  <hash> demo (HEAD)
#  <hash> packages/canvod-readers/tests/test_data (HEAD)

# List demo RINEX files
ls demo/data/01_Rosalia/01_reference/01_GNSS/01_raw/25001/*.25o | wc -l
# Should show: 96

# Check test_data structure
ls -la packages/canvod-readers/tests/test_data/valid/
# Should show: aux/, rinex_v3_04/

# Run tests with demo data
pytest -v -k "demo"
```

---

## File Naming Convention

### RINEX Short Name Format

Your files follow RINEX v3 short name convention:

```
rref001a00.25o
└┬┘└┬┘└┬┘└┬┘└┬─┬┘
 │  │  │  │  │ └─ Extension: o (observation)
 │  │  │  │  └─── Year: 25 (2025)
 │  │  │  └────── Session: 00 (00:00-00:15)
 │  │  └───────── Hour code: a (hour 00)
 │  └──────────── DOY: 001 (day of year)
 └─────────────── Station: rref (Rosalia reference)
```

**Hour codes**: a=00, b=01, c=02, ... x=23  
**Sessions**: 00=:00-:15, 15=:15-:30, 30=:30-:45, 45=:45-:00

---

## Summary

✅ **Both submodules configured and working**  
✅ **Demo has real Rosalia data (2025-001, 2025-002)**  
✅ **Test data structure ready for falsified files**  
✅ **conftest.py updated with proper fixtures**  
✅ **96 RINEX files per day per receiver**  

**Next**: Add auxiliary files to demo and corrupted files to test_data!
