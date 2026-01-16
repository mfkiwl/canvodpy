# Submodules Setup Checklist

## ✅ Complete Setup Guide

Follow these steps to set up both data submodules.

---

## Phase 1: Create Test Data Repository

- [ ] **Create GitHub repository**: `canvodpy-test-data`
- [ ] **Initialize locally**:
  ```bash
  mkdir canvodpy-test-data && cd canvodpy-test-data
  git init
  ```
- [ ] **Create directory structure**:
  ```bash
  mkdir -p valid/{rinex,aux}
  mkdir -p corrupted/{rinex,aux}
  mkdir -p edge_cases
  ```
- [ ] **Add README**: Copy from `TEST_DATA_README.md`
- [ ] **Setup Git LFS** (optional):
  ```bash
  git lfs install
  # Add .gitattributes
  ```
- [ ] **Initial commit and push**:
  ```bash
  git add .
  git commit -m "Initial test data structure"
  git remote add origin https://github.com/your-org/canvodpy-test-data.git
  git push -u origin main
  ```

---

## Phase 2: Create Examples Repository

- [ ] **Create GitHub repository**: `canvodpy-examples`
- [ ] **Initialize locally**:
  ```bash
  mkdir canvodpy-examples && cd canvodpy-examples
  git init
  ```
- [ ] **Create directory structure**:
  ```bash
  mkdir -p rosalia/2023/001/{rinex,aux,outputs}
  mkdir -p tuwien/2024/150/{rinex,aux}
  ```
- [ ] **Add README**: Copy from `EXAMPLES_README.md`
- [ ] **Create site_metadata.json**
- [ ] **Setup Git LFS** (required):
  ```bash
  git lfs install
  # Add .gitattributes for *.rnx, *.SP3, *.CLK, *.nc
  ```
- [ ] **Initial commit and push**:
  ```bash
  git add .
  git commit -m "Initial examples structure"
  git remote add origin https://github.com/your-org/canvodpy-examples.git
  git push -u origin main
  ```

---

## Phase 3: Add Submodules to Main Repo

- [ ] **Add test-data submodule**:
  ```bash
  cd /Users/work/Developer/GNSS/canvodpy
  git submodule add https://github.com/your-org/canvodpy-test-data.git test-data
  ```
- [ ] **Add examples submodule**:
  ```bash
  git submodule add https://github.com/your-org/canvodpy-examples.git examples
  ```
- [ ] **Commit submodule references**:
  ```bash
  git add .gitmodules test-data examples
  git commit -m "Add test-data and examples submodules"
  git push
  ```

---

## Phase 4: Populate Test Data

- [ ] **Add valid baseline files**:
  ```bash
  cd test-data/valid/rinex
  # Copy known-good RINEX file
  # Copy known-good SP3 file
  # Copy known-good CLK file
  ```
- [ ] **Create corrupted files**:
  ```bash
  cd ../../corrupted/rinex
  # Create truncated_header.rnx
  # Create invalid_epochs.rnx
  # Create bad_satellites.rnx
  # ... (see TEST_DATA_README.md for full list)
  ```
- [ ] **Create edge case files**:
  ```bash
  cd ../../edge_cases
  # Create minimal.rnx
  # Create sparse_observations.rnx
  # ... (see TEST_DATA_README.md for full list)
  ```
- [ ] **Update README manifest**
- [ ] **Commit and push**:
  ```bash
  git add .
  git commit -m "Add initial test data files"
  git push
  ```
- [ ] **Update main repo reference**:
  ```bash
  cd /Users/work/Developer/GNSS/canvodpy
  git add test-data
  git commit -m "Update test-data submodule"
  git push
  ```

---

## Phase 5: Populate Example Data

- [ ] **Add Rosalia site data**:
  ```bash
  cd examples/rosalia/2023/001/rinex
  # Copy canopy_20230010000.rnx
  # Copy reference_20230010000.rnx
  ```
- [ ] **Add Rosalia auxiliary data**:
  ```bash
  cd ../aux
  # Copy COD0MGXFIN_20230010000_01D_05M_ORB.SP3
  # Copy COD0MGXFIN_20230010000_01D_30S_CLK.CLK
  ```
- [ ] **Update site_metadata.json** with Rosalia coordinates
- [ ] **Create rosalia/site_info.md**
- [ ] **Commit and push** (Git LFS handles large files):
  ```bash
  git add .
  git commit -m "Add Rosalia site example data"
  git push
  ```
- [ ] **Update main repo reference**:
  ```bash
  cd /Users/work/Developer/GNSS/canvodpy
  git add examples
  git commit -m "Update examples submodule"
  git push
  ```

---

## Phase 6: Update Configuration

- [ ] **conftest.py already configured** (✅ Done)
- [ ] **Update notebook defaults**:
  ```python
  # In complete_pipeline.py
  EXAMPLES_DIR = Path(__file__).parent.parent.parent.parent / "examples"
  default_rinex_dir = EXAMPLES_DIR / "rosalia/2023/001/rinex"
  ```
- [ ] **Commit changes**:
  ```bash
  git add canvodpy/docs/notebooks/complete_pipeline.py
  git commit -m "Update notebook to use examples submodule"
  git push
  ```

---

## Phase 7: Write Tests

- [ ] **Create test using corrupted data**:
  ```python
  # tests/test_readers_validation.py
  def test_truncated_header(test_data_dir):
      corrupted = test_data_dir / "corrupted/rinex/truncated_header.rnx"
      with pytest.raises(HeaderParseError):
          obs = Rnxv3Obs(fpath=corrupted)
  ```
- [ ] **Create integration test using examples**:
  ```python
  # tests/test_integration.py
  @pytest.mark.requires_examples
  def test_rosalia_pipeline(examples_dir):
      rinex = examples_dir / "rosalia/2023/001/rinex/canopy_20230010000.rnx"
      obs = Rnxv3Obs(fpath=rinex)
      assert len(obs.to_ds().epoch) > 0
  ```
- [ ] **Run tests**:
  ```bash
  cd /Users/work/Developer/GNSS/canvodpy
  pytest
  ```

---

## Phase 8: Update CI/CD

- [ ] **Update GitHub Actions**:
  ```yaml
  - uses: actions/checkout@v4
    with:
      submodules: true  # Clone submodules
      lfs: true         # Pull LFS files
  ```
- [ ] **Test CI pipeline**:
  ```bash
  git add .github/workflows/tests.yml
  git commit -m "Update CI to use submodules"
  git push
  # Check GitHub Actions
  ```

---

## Phase 9: Documentation

- [ ] **Update main README.md** to mention submodules
- [ ] **Add to CONTRIBUTING.md**:
  ```markdown
  ## Working with Test Data
  See test-data/README.md
  
  ## Working with Examples
  See examples/README.md
  ```
- [ ] **Commit documentation**:
  ```bash
  git add README.md CONTRIBUTING.md
  git commit -m "Document submodules in main README"
  git push
  ```

---

## Phase 10: Verification

- [ ] **Clone fresh copy**:
  ```bash
  cd /tmp
  git clone --recurse-submodules https://github.com/your-org/canvodpy.git
  cd canvodpy
  ```
- [ ] **Verify submodules initialized**:
  ```bash
  ls test-data/  # Should show valid/, corrupted/, edge_cases/
  ls examples/   # Should show rosalia/, site_metadata.json
  ```
- [ ] **Run tests**:
  ```bash
  uv sync
  uv run pytest
  ```
- [ ] **Run demo notebook**:
  ```bash
  cd canvodpy
  uv run marimo edit docs/notebooks/complete_pipeline.py
  ```

---

## Quick Reference

### For New Contributors

```bash
# Clone with submodules
git clone --recurse-submodules https://github.com/your-org/canvodpy.git

# Or after cloning
git submodule update --init --recursive

# Install Git LFS and pull files
git lfs install
cd test-data && git lfs pull
cd ../examples && git lfs pull
```

### Daily Development

```bash
# Update submodules
git submodule update --remote

# After making changes in submodule
cd test-data  # or examples
git add .
git commit -m "Update data"
git push
cd ..
git add test-data  # or examples
git commit -m "Update submodule reference"
```

---

## Status Tracking

Use this checklist to track your progress:

- [ ] Phase 1: Test data repo created ✅
- [ ] Phase 2: Examples repo created ✅
- [ ] Phase 3: Submodules added to main ✅
- [ ] Phase 4: Test data populated ⏳
- [ ] Phase 5: Example data populated ⏳
- [ ] Phase 6: Configuration updated ✅
- [ ] Phase 7: Tests written ⏳
- [ ] Phase 8: CI/CD updated ⏳
- [ ] Phase 9: Documentation updated ⏳
- [ ] Phase 10: Verification complete ⏳

---

## Getting Help

- **Submodule issues**: See `SUBMODULES_SETUP_GUIDE.md`
- **Data format**: See `TEST_DATA_README.md` or `EXAMPLES_README.md`
- **Architecture**: See `DATA_MANAGEMENT_ARCHITECTURE.md`
