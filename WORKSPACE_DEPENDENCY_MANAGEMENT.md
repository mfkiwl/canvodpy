# Workspace Dependency Management

## How UV Syncs Workspace Dependencies

### ✅ Your Current Setup

Your monorepo is configured correctly with:

1. **Root workspace configuration** (`/pyproject.toml`):
```toml
[tool.uv.workspace]
members = ["packages/*", "canvodpy"]
```

2. **Umbrella package references** (`/canvodpy/pyproject.toml`):
```toml
[project]
dependencies = [
    "canvod-readers",
    "canvod-aux",
    # ... other deps
]

[tool.uv.sources]
canvod-readers = { workspace = true }
canvod-aux = { workspace = true }
```

This setup ensures:
- ✅ Umbrella automatically pulls in sub-package dependencies
- ✅ Local changes are immediately reflected
- ✅ No version conflicts between packages
- ✅ Single unified `uv.lock` at root

---

## How It Works

### 1. Dependency Resolution

When you run `uv sync` from **anywhere** in the monorepo:

```bash
cd /Users/work/Developer/GNSS/canvodpy
uv sync
```

UV will:
1. Read root `pyproject.toml` workspace configuration
2. Find all `members = ["packages/*", "canvodpy"]`
3. Resolve each package's dependencies
4. Create unified `uv.lock` with ALL dependencies
5. Install everything in editable mode

### 2. Transitive Dependencies

```
canvodpy (umbrella)
├─ canvod-readers (workspace = true)
│  ├─ xarray>=2023.12.0      ← Pulled into umbrella
│  ├─ numpy>=1.24.0          ← Pulled into umbrella
│  └─ pint>=0.23             ← Pulled into umbrella
└─ canvod-aux (workspace = true)
   ├─ scipy>=1.15.0          ← Pulled into umbrella
   ├─ xarray>=2023.12.0      ← Shared with readers
   └─ numpy>=1.24.0          ← Shared with readers
```

UV automatically:
- Merges all dependencies
- Resolves version conflicts
- Ensures compatibility

### 3. Editable Installs

With `workspace = true`, packages are installed as **editable**:

```python
# Changes in /packages/canvod-readers/src/canvod/readers/
# are IMMEDIATELY available when you import:
from canvod.readers import Rnxv3Obs  # Uses latest code
```

No need to reinstall after code changes!

---

## Common Commands

### Sync Everything (Recommended)

```bash
# From repository root
cd /Users/work/Developer/GNSS/canvodpy
uv sync

# This syncs ALL workspace members and their dependencies
```

### Sync with Dev Dependencies

```bash
# Include dev dependencies (pytest, ruff, etc.)
uv sync --all-extras

# Or specifically for umbrella
cd canvodpy
uv sync --group dev
```

### Sync with Legacy Dependencies

```bash
# Include legacy gnssvodpy (temporary)
cd canvodpy
uv sync --group legacy
```

### Update Dependencies

```bash
# Update all packages to latest compatible versions
uv sync --upgrade

# Update specific package
uv sync --upgrade-package numpy
```

### Add New Dependency

```bash
# To a sub-package
cd packages/canvod-readers
uv add scipy>=1.15.0

# To umbrella
cd canvodpy
uv add polars>=1.0.0

# Both will update root uv.lock
```

---

## Verification Commands

### Check What's Installed

```bash
# Show all packages in environment
uv pip list

# Check specific package
uv pip show canvod-readers

# Verify it's editable (should show path)
```

### Verify Workspace Setup

```bash
# From root - should show all members
uv tree

# Check lock file status
ls -lh uv.lock  # Should exist at root
```

### Test Imports

```bash
# Test umbrella can import sub-packages
cd canvodpy
uv run python -c "from canvod.readers import Rnxv3Obs; print('✅')"
uv run python -c "from canvod.aux import Sp3File; print('✅')"
```

---

## Troubleshooting

### Issue: Sub-package not found

**Symptom:**
```python
ModuleNotFoundError: No module named 'canvod.readers'
```

**Solution:**
```bash
# Re-sync from root
cd /Users/work/Developer/GNSS/canvodpy
uv sync

# Verify workspace configuration
grep -A5 "\[tool.uv.workspace\]" pyproject.toml

# Check sources are configured
grep -A5 "\[tool.uv.sources\]" canvodpy/pyproject.toml
```

### Issue: Using old code after changes

**Symptom:** Code changes not reflected when importing

**Solution:**
```bash
# Verify editable install
uv pip show canvod-readers | grep Location
# Should show: /path/to/packages/canvod-readers/src

# If not editable, reinstall
cd /Users/work/Developer/GNSS/canvodpy
uv sync --reinstall
```

### Issue: Version conflicts

**Symptom:**
```
Conflicts detected between package versions
```

**Solution:**
```bash
# Check conflicting versions
uv tree | grep -i "conflict"

# Update constraints in affected packages
# E.g., if numpy conflict between 1.24.0 and 2.0.0:
# Update all packages to use numpy>=2.0.0

# Then re-sync
uv sync --reinstall
```

### Issue: Lock file out of sync

**Symptom:**
```
Warning: uv.lock is out of date
```

**Solution:**
```bash
# Regenerate lock file
cd /Users/work/Developer/GNSS/canvodpy
rm uv.lock
uv sync
```

---

## Best Practices

### 1. Always Sync from Root

```bash
# ✅ Good
cd /Users/work/Developer/GNSS/canvodpy
uv sync

# ⚠️ Works but prefer root
cd canvodpy
uv sync
```

### 2. Keep Dependencies Aligned

When adding deps to sub-packages, use compatible versions:

```toml
# ✅ Good - compatible ranges
canvod-readers: numpy>=1.24.0
canvod-aux:     numpy>=1.24.0

# ❌ Bad - conflicting constraints  
canvod-readers: numpy>=2.0.0
canvod-aux:     numpy<2.0.0
```

### 3. Use Workspace Sources

```toml
# ✅ Always use workspace = true
[tool.uv.sources]
canvod-readers = { workspace = true }

# ❌ Don't use paths or versions
canvod-readers = { path = "../packages/canvod-readers" }  # Wrong
canvod-readers = ">=0.1.0"  # Wrong
```

### 4. Single Lock File

- Keep `uv.lock` at repository root only
- Don't create lock files in sub-packages
- Commit `uv.lock` to version control

---

## Adding New Packages

When you create a new package (e.g., `canvod-vod`):

### 1. Create Package Structure

```bash
cd packages
mkdir -p canvod-vod/src/canvod/vod
cd canvod-vod
```

### 2. Create pyproject.toml

```toml
[project]
name = "canvod-vod"
version = "0.1.0"
dependencies = [
    "xarray>=2023.12.0",
    "numpy>=1.24.0",
]

[build-system]
requires = ["uv_build>=0.9.17,<0.10.0"]
build-backend = "uv_build"
```

### 3. Update Umbrella

```bash
cd ../../canvodpy
uv add canvod-vod --workspace
```

This automatically:
- Adds to `dependencies`
- Adds to `tool.uv.sources` with `workspace = true`
- Updates root `uv.lock`

### 4. Verify

```bash
cd /Users/work/Developer/GNSS/canvodpy
uv sync
uv run python -c "import canvod.vod; print('✅')"
```

---

## Migration Workflow

As you migrate code from `gnssvodpy` to sub-packages:

### Before Each Migration

```bash
# Start with clean sync
cd /Users/work/Developer/GNSS/canvodpy
uv sync
```

### After Adding Code

```bash
# No reinstall needed! Changes are immediate
# Just test:
cd canvodpy
uv run python -c "from canvod.vod import new_function"
```

### When Removing Legacy Dep

```bash
# Remove gnssvodpy dependency
cd canvodpy
uv remove gnssvodpy  # Or remove from legacy group

# Sync
cd ..
uv sync
```

---

## GitHub Actions / CI

Your CI should use:

```yaml
- name: Install dependencies
  run: |
    pip install uv
    uv sync --all-extras
```

This ensures:
- All workspace members installed
- All dependencies synced
- Tests run with correct versions

---

## Summary

### ✅ What You Have Now

1. **Workspace configured** at root
2. **Umbrella declares** sub-package dependencies
3. **Sources point** to workspace members
4. **Single lock file** manages everything

### 🔄 How to Sync

```bash
# Simple command from root:
cd /Users/work/Developer/GNSS/canvodpy
uv sync

# That's it! All packages synced automatically.
```

### 📦 Dependencies Flow

```
Root uv.lock
    ↓
canvodpy (umbrella)
    ↓ (workspace = true)
┌───┴────┐
↓        ↓
readers  aux
↓        ↓
deps     deps → Merged into single environment
```

### 🎯 Key Benefit

**One sync, everything works:**
- Sub-packages installed editable
- All dependencies resolved
- No version conflicts
- Immediate code updates
