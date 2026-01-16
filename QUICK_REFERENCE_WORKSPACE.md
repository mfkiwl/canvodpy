# Quick Reference: Workspace Dependencies

## ⚡ TL;DR

```bash
# Sync all packages and dependencies
cd /Users/work/Developer/GNSS/canvodpy
uv sync

# That's it! Everything is synced automatically.
```

---

## 🔧 What Was Configured

### 1. Umbrella Package (`canvodpy/pyproject.toml`)

```toml
[project]
dependencies = [
    "canvod-readers",  # ← Sub-package
    "canvod-aux",      # ← Sub-package
    # ... other deps
]

[tool.uv.sources]
canvod-readers = { workspace = true }  # ← Points to local package
canvod-aux = { workspace = true }      # ← Points to local package
```

### 2. Root Workspace (`pyproject.toml`)

```toml
[tool.uv.workspace]
members = ["packages/*", "canvodpy"]  # ← All packages included
```

---

## 📦 How Dependencies Flow

```
uv sync (at root)
    ↓
Reads: canvodpy/pyproject.toml
    ↓
Finds: canvod-readers, canvod-aux (workspace = true)
    ↓
Resolves: All transitive dependencies
    ↓
Installs: Everything as editable
    ↓
Result: Single unified environment
```

---

## ✅ Benefits

1. **Automatic Transitive Dependencies**
   - Umbrella pulls in ALL sub-package deps
   - No manual tracking needed

2. **Instant Updates**
   - Code changes immediately available
   - No reinstall required

3. **Version Conflict Resolution**
   - Single lock file manages all versions
   - UV resolves conflicts automatically

4. **Editable Installs**
   - Development happens in place
   - Import changes immediately

---

## 🎯 Common Tasks

### Sync Everything
```bash
cd /Users/work/Developer/GNSS/canvodpy
uv sync
```

### Run Pipeline Demo
```bash
cd canvodpy
uv run marimo edit docs/notebooks/complete_pipeline.py
```

### Test Imports
```bash
uv run python -c "from canvod.readers import Rnxv3Obs"
uv run python -c "from canvod.aux import Sp3File"
```

### Add New Dependency to Sub-Package
```bash
cd packages/canvod-readers
uv add new-package>=1.0.0
cd ../..
uv sync  # Updates umbrella automatically
```

### Add New Sub-Package
```bash
# 1. Create package
mkdir -p packages/canvod-vod/src/canvod/vod

# 2. Add to umbrella
cd canvodpy
uv add canvod-vod --workspace

# 3. Sync
cd ..
uv sync
```

---

## 🔍 Verification

```bash
# Run verification script
cd /Users/work/Developer/GNSS/canvodpy
bash verify_workspace.sh

# Or manually check:
uv pip list | grep canvod
uv pip show canvod-readers  # Should show editable location
```

---

## 📚 Full Documentation

- **Detailed Guide**: `WORKSPACE_DEPENDENCY_MANAGEMENT.md`
- **Pipeline Demo**: `canvodpy/docs/notebooks/complete_pipeline.py`
- **Testing Guide**: `QUICK_START_TESTING.md`

---

## 🆘 Troubleshooting

### Import Error
```bash
uv sync --reinstall
```

### Lock File Out of Sync
```bash
rm uv.lock && uv sync
```

### Editable Install Not Working
```bash
uv pip show canvod-readers | grep Editable
# Should show: Yes
```

---

## 🎓 Key Concepts

**Workspace**: Monorepo with multiple packages sharing deps  
**workspace = true**: Install package from local directory  
**Editable**: Changes to code immediately available  
**uv.lock**: Single source of truth for all versions
