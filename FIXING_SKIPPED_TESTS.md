# Fixing Skipped Tests - Missing Test Data

## Problem

36 tests are skipped because the test_data submodule is empty:

```
Test file not found: /Users/work/Developer/GNSS/canvodpy/packages/canvod-readers/tests/test_data/01_Rosalia/02_canopy/01_GNSS/01_raw/25001/ract001a00.25o
```

**Current state**:
- ✅ test_data submodule structure exists
- ❌ No actual RINEX files in test_data
- ✅ demo submodule has real files

---

## Solution: Populate Test Data

### Option 1: Copy from Demo (Quick Fix)

```bash
cd /Users/work/Developer/GNSS/canvodpy

# Copy a few files from demo to test_data for testing
# This creates minimal test fixtures

# Copy reference receiver files (day 25001)
mkdir -p packages/canvod-readers/tests/test_data/valid/rinex_v3_04/01_Rosalia/01_reference/01_GNSS/01_raw/25001
cp demo/data/01_Rosalia/01_reference/01_GNSS/01_raw/25001/rref001a00.25o \
   packages/canvod-readers/tests/test_data/valid/rinex_v3_04/01_Rosalia/01_reference/01_GNSS/01_raw/25001/

# Copy canopy receiver files (day 25001)
mkdir -p packages/canvod-readers/tests/test_data/valid/rinex_v3_04/01_Rosalia/02_canopy/01_GNSS/01_raw/25001
cp demo/data/01_Rosalia/02_canopy/01_GNSS/01_raw/25001/ract001a00.25o \
   packages/canvod-readers/tests/test_data/valid/rinex_v3_04/01_Rosalia/02_canopy/01_GNSS/01_raw/25001/

# Copy auxiliary files if needed
cp -r demo/data/00_aux_files/* \
   packages/canvod-readers/tests/test_data/valid/aux/00_aux_files/ 2>/dev/null || true

# Commit to test_data submodule
cd packages/canvod-readers/tests/test_data
git add .
git commit -m "Add minimal test fixtures from demo data"
git push

# Update main repo reference
cd /Users/work/Developer/GNSS/canvodpy
git add packages/canvod-readers/tests/test_data
git commit -m "Update test-data with minimal fixtures"
```

### Option 2: Create Symbolic Links (Development)

For development, symlink demo data into test_data (don't commit these):

```bash
cd packages/canvod-readers/tests/test_data/valid

# Create symlinks to demo data
ln -sf ../../../../../../demo/data/01_Rosalia rinex_v3_04/
ln -sf ../../../../../../demo/data/00_aux_files aux/
```

**Warning**: Don't commit symlinks to the test_data repository!

### Option 3: Proper Test Fixtures (Recommended Long-term)

Create minimal, purpose-built test files:

1. **Extract minimal RINEX**: Single-epoch files for fast tests
2. **Create corrupted versions**: For error handling tests
3. **Document test cases**: Each file tests specific functionality

```bash
cd packages/canvod-readers/tests/test_data

# Create minimal test file (first epoch only)
# This requires Python to extract first epoch
python3 << 'EOF'
from pathlib import Path

# Read first 100 lines of demo file (header + first epoch)
demo_file = Path("../../../../../../demo/data/01_Rosalia/02_canopy/01_GNSS/01_raw/25001/ract001a00.25o")
output_file = Path("valid/rinex_v3_04/01_Rosalia/02_canopy/01_GNSS/01_raw/25001/ract001a00.25o")
output_file.parent.mkdir(parents=True, exist_ok=True)

with open(demo_file) as f:
    lines = f.readlines()[:100]

with open(output_file, 'w') as f:
    f.writelines(lines)

print(f"Created minimal test file: {output_file}")
EOF
```

---

## Verification

After populating test_data, run tests again:

```bash
cd /Users/work/Developer/GNSS/canvodpy
uv run pytest packages/canvod-readers/tests/ -v

# Should see:
# - Previously skipped tests now running
# - 106 tests passed (or more)
# - 0 skipped (or fewer)
```

---

## Current Test Status

```
✅ 70 passed   - Tests with hardcoded data or no data needed
⏭️  36 skipped  - Tests requiring RINEX files (ract001a00.25o)
⚠️  8 warnings  - Deprecation warnings (not critical)
```

**After fix should see**:
```
✅ 106 passed
⏭️  0-2 skipped (only network-dependent tests)
```

---

## Quick Fix Commands

```bash
# Navigate to project root
cd /Users/work/Developer/GNSS/canvodpy

# Copy one canopy file for tests
mkdir -p packages/canvod-readers/tests/test_data/valid/rinex_v3_04/01_Rosalia/02_canopy/01_GNSS/01_raw/25001
cp demo/data/01_Rosalia/02_canopy/01_GNSS/01_raw/25001/ract001a00.25o \
   packages/canvod-readers/tests/test_data/valid/rinex_v3_04/01_Rosalia/02_canopy/01_GNSS/01_raw/25001/

# Verify
ls -lh packages/canvod-readers/tests/test_data/valid/rinex_v3_04/01_Rosalia/02_canopy/01_GNSS/01_raw/25001/

# Run tests
uv run pytest packages/canvod-readers/tests/test_rinex_v3.py -v
```

---

## Notes

**For test_data submodule**:
- Keep files minimal (single epoch when possible)
- Add corrupted versions for error tests
- Document each test file's purpose
- Don't duplicate entire demo dataset

**For demo submodule**:
- Keep full real-world data
- Use for documentation/examples
- Don't modify for testing purposes

This keeps test data fast and focused, while demo data remains complete and realistic.
