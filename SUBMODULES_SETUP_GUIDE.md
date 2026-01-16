# Git Submodules Setup Guide

This guide explains how to set up and manage two separate data repositories as submodules.

## Overview

**Two independent data repositories:**

1. **test-data** → For pytest with falsified/corrupted files
2. **examples** → For demos/docs with clean real data

```
canvodpy/
├── test-data/      # Submodule 1: Testing with corrupted data
└── examples/       # Submodule 2: Demos with real data
```

---

## Initial Setup (Repository Maintainers)

### Step 1: Create Test Data Repository

```bash
# Create repository
cd ~/Developer
mkdir canvodpy-test-data
cd canvodpy-test-data
git init

# Create structure
mkdir -p valid/{rinex,aux}
mkdir -p corrupted/{rinex,aux}
mkdir -p edge_cases

# Copy the test data README
cp /path/to/canvodpy/TEST_DATA_README.md README.md

# Setup Git LFS (optional, for large files)
git lfs install
cat > .gitattributes << 'EOF'
*.rnx filter=lfs diff=lfs merge=lfs -text
*.RNX filter=lfs diff=lfs merge=lfs -text
*.SP3 filter=lfs diff=lfs merge=lfs -text
*.CLK filter=lfs diff=lfs merge=lfs -text
EOF

# Initial commit
git add .
git commit -m "Initial test data repository structure"

# Create GitHub repo and push
gh repo create your-org/canvodpy-test-data --public
git remote add origin https://github.com/your-org/canvodpy-test-data.git
git push -u origin main
```

### Step 2: Create Examples Repository

```bash
# Create repository
cd ~/Developer
mkdir canvodpy-examples
cd canvodpy-examples
git init

# Create structure
mkdir -p rosalia/2023/001/{rinex,aux,outputs}
mkdir -p tuwien/2024/150/{rinex,aux}

# Copy the examples README
cp /path/to/canvodpy/EXAMPLES_README.md README.md

# Create site metadata
cat > site_metadata.json << 'EOF'
{
  "sites": {
    "rosalia": {
      "name": "Rosalia Forest Site",
      "country": "Austria",
      "location": {
        "lat": 47.73,
        "lon": 16.30,
        "elevation": 350.0
      },
      "receivers": {
        "canopy": {
          "type": "canopy",
          "position_ecef": {
            "x": 4194304.678,
            "y": 1162205.267,
            "z": 4647245.201
          }
        },
        "reference": {
          "type": "reference",
          "position_ecef": {
            "x": 4194354.123,
            "y": 1162180.456,
            "z": 4647290.789
          }
        }
      }
    }
  }
}
EOF

# Setup Git LFS
git lfs install
cat > .gitattributes << 'EOF'
*.rnx filter=lfs diff=lfs merge=lfs -text
*.RNX filter=lfs diff=lfs merge=lfs -text
*.SP3 filter=lfs diff=lfs merge=lfs -text
*.CLK filter=lfs diff=lfs merge=lfs -text
*.nc filter=lfs diff=lfs merge=lfs -text
EOF

# Initial commit
git add .
git commit -m "Initial examples repository structure"

# Create GitHub repo and push
gh repo create your-org/canvodpy-examples --public
git remote add origin https://github.com/your-org/canvodpy-examples.git
git push -u origin main
```

### Step 3: Add as Submodules to Main Repo

```bash
cd /Users/work/Developer/GNSS/canvodpy

# Add test-data submodule
git submodule add https://github.com/your-org/canvodpy-test-data.git test-data

# Add examples submodule
git submodule add https://github.com/your-org/canvodpy-examples.git examples

# Commit submodule references
git add .gitmodules test-data examples
git commit -m "Add test-data and examples submodules"
git push
```

---

## User Setup (Cloning Repository)

### Option 1: Clone with Submodules

```bash
# Clone everything at once
git clone --recurse-submodules https://github.com/your-org/canvodpy.git
cd canvodpy

# Verify submodules
ls test-data/  # Should show valid/, corrupted/, edge_cases/
ls examples/   # Should show rosalia/, tuwien/, site_metadata.json
```

### Option 2: Clone Then Initialize Submodules

```bash
# Clone main repo
git clone https://github.com/your-org/canvodpy.git
cd canvodpy

# Initialize submodules
git submodule init
git submodule update

# Or combined:
git submodule update --init --recursive
```

### Option 3: Selective Submodule Initialization

```bash
# Clone main repo
git clone https://github.com/your-org/canvodpy.git
cd canvodpy

# Only initialize what you need
git submodule update --init test-data     # For running tests
# or
git submodule update --init examples      # For running demos
```

---

## Daily Usage

### Running Tests (Requires test-data)

```bash
cd /Users/work/Developer/GNSS/canvodpy

# Ensure test-data is up to date
git submodule update --remote test-data

# Run tests
pytest

# Tests will use fixtures from conftest.py
# which point to test-data/ submodule
```

### Running Demos (Requires examples)

```bash
cd /Users/work/Developer/GNSS/canvodpy

# Ensure examples are up to date
git submodule update --remote examples

# Run notebook
cd canvodpy
uv run marimo edit docs/notebooks/complete_pipeline.py

# In notebook, point to examples data:
# EXAMPLES = Path("/path/to/canvodpy/examples")
```

### Updating Submodules

```bash
# Update both submodules to latest
git submodule update --remote

# Update specific submodule
git submodule update --remote test-data
git submodule update --remote examples

# Commit updated references
git add test-data examples
git commit -m "Update submodules to latest"
```

---

## Contributing Data

### Adding Test Data (test-data submodule)

```bash
# Work in test-data submodule
cd test-data

# Create corrupted file
cp valid/rinex/sample.rnx corrupted/rinex/truncated.rnx
# ... corrupt the file

# Commit
git add corrupted/rinex/truncated.rnx
git commit -m "Add truncated RINEX test case"
git push

# Update reference in main repo
cd ..
git add test-data
git commit -m "Update test-data with new corrupted file"
```

### Adding Example Data (examples submodule)

```bash
# Work in examples submodule
cd examples

# Add new site data
mkdir -p new_site/2024/100/{rinex,aux}
# ... add files

# Update metadata
# Edit site_metadata.json

# Commit
git add new_site/ site_metadata.json
git commit -m "Add new_site example data for 2024-100"
git push

# Update reference in main repo
cd ..
git add examples
git commit -m "Update examples with new_site data"
```

---

## Configuration Files

### Update conftest.py

Already configured to use `test-data/` submodule:

```python
TEST_DATA_ROOT = Path(__file__).parent / "test-data"

@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    if not TEST_DATA_ROOT.exists():
        pytest.skip("Test data submodule not initialized")
    return TEST_DATA_ROOT
```

### Update notebook defaults

```python
# In complete_pipeline.py
from pathlib import Path

# Default to examples submodule
EXAMPLES_DIR = Path(__file__).parent.parent.parent.parent / "examples"
default_rinex_dir = EXAMPLES_DIR / "rosalia/2023/001/rinex"
```

---

## Git LFS Setup (If Using Large Files)

### Install Git LFS

```bash
# macOS
brew install git-lfs

# Linux
sudo apt install git-lfs

# Windows
# Download from: https://git-lfs.github.com/

# Initialize
git lfs install
```

### Pull LFS Files

```bash
cd test-data
git lfs pull

cd ../examples
git lfs pull
```

---

## Troubleshooting

### Submodule not initialized

**Error**: `Test data submodule not initialized`

**Solution**:
```bash
cd /Users/work/Developer/GNSS/canvodpy
git submodule update --init test-data
```

### Submodule detached HEAD

**Symptom**: Submodule in detached HEAD state

**Solution**:
```bash
cd test-data  # or examples
git checkout main
git pull
cd ..
git add test-data  # or examples
git commit -m "Update submodule to latest main"
```

### Submodule URL changed

**Solution**:
```bash
# Update .gitmodules with new URL
vim .gitmodules

# Sync configuration
git submodule sync

# Update submodule
git submodule update --init --recursive
```

### Large files not downloading

**Solution**:
```bash
# Install Git LFS if not already
git lfs install

# Pull LFS files
cd test-data  # or examples
git lfs pull
```

---

## CI/CD Configuration

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
          submodules: recursive  # ← Include submodules
          lfs: true              # ← Pull LFS files
      
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

## Best Practices

### For test-data:
- ✅ Keep files small (< 10MB if possible)
- ✅ One error per corrupted file
- ✅ Document expected errors in README
- ✅ Create corresponding test cases

### For examples:
- ✅ Use real observational data
- ✅ Include complete metadata
- ✅ Organize by site and date
- ✅ Provide site documentation

### For both:
- ✅ Use Git LFS for files > 1MB
- ✅ Update READMEs with file manifests
- ✅ Version control is important
- ✅ Keep submodules synced

---

## Summary

```bash
# Setup (once)
git submodule add <url> test-data
git submodule add <url> examples

# Clone (users)
git clone --recurse-submodules <repo>

# Update (daily)
git submodule update --remote

# Contribute
cd test-data  # or examples
# ... make changes
git push
cd ..
git add test-data  # or examples
git commit -m "Update submodule"
```

**Two repos, clear purposes, easy management!**
