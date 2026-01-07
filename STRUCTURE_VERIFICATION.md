# canVODpy Structure Verification Report
Generated: 2026-01-07

## ✅ What We Have (Correct)

### Workspace Root
- ✅ pyproject.toml (workspace config, Python 3.13, TUW-GEO ruff)
- ✅ Justfile (root commands)
- ✅ .python-version (3.13)
- ✅ .gitignore (comprehensive)
- ✅ .github/actions/setup/action.yml
- ✅ canvodpy.code-workspace
- ✅ uv.lock
- ✅ docs/ directory

### Package Structure
- ✅ 6 packages in packages/
- ✅ 1 umbrella in canvodpy/
- ✅ Each has pyproject.toml (uv_build backend)
- ✅ Each has src/{package}/__init__.py
- ✅ Correct naming: canvod-readers → canvod_readers

### Git Configuration
- ✅ Git user: Nicolas Bader <nicolas.bader@geo.tuwien.ac.at>
- ✅ Initial commit pushed

## ❌ What's Missing (Per TUW-GEO Cookiecutter)

### Workspace Root Missing
- ❌ README.md
- ❌ CONTRIBUTING.md
- ❌ LICENSE
- ❌ .pre-commit-config.yaml
- ❌ .github/workflows/code_quality.yml
- ❌ .github/workflows/test_coverage.yml
- ❌ .github/workflows/test_platforms.yml

### Per-Package Missing (All 7 packages)
- ❌ Justfile
- ❌ tests/ directory
- ❌ tests/test_meta.py
- ❌ docs/ directory
- ❌ docs/index.ipynb
- ❌ myst.yml
- ❌ README.md
- ❌ CONTRIBUTING.md (or symlink to root)
- ❌ LICENSE (or symlink to root)

### Per-Package pyproject.toml Issues
- ⚠️  Missing proper metadata (authors, description, classifiers)
- ⚠️  Missing [dependency-groups] dev dependencies
- ⚠️  Missing [tool.pytest.ini_options]
- ⚠️  Missing [tool.coverage.run]

## 📋 Comparison to Cookiecutter Template

### TUW-GEO Template Has:
```
canvod-template/
├── .github/
│   ├── actions/setup/action.yml     ✅ We have
│   └── workflows/
│       ├── code_quality.yml         ❌ Missing
│       ├── test_coverage.yml        ❌ Missing
│       └── test_platforms.yml       ❌ Missing
├── .gitignore                       ✅ We have
├── .pre-commit-config.yaml          ❌ Missing
├── .python-version                  ✅ We have (but template doesn't)
├── CONTRIBUTING.md                  ❌ Missing
├── Justfile                         ✅ We have
├── LICENSE                          ❌ Missing
├── README.md                        ❌ Missing
├── docs/
│   └── index.ipynb                  ❌ Missing
├── myst.yml                         ❌ Missing
├── pyproject.toml                   ✅ We have
├── src/{package}/
│   └── __init__.py                  ✅ We have
└── tests/
    └── test_meta.py                 ❌ Missing
```

## 🎯 Comparison to Migration Plan

### Planned Structure (from CANVODPY_MIGRATION_GUIDE.md):
```
canvodpy/
├── .github/
│   ├── workflows/
│   │   ├── code_quality.yml         ❌ Not created yet
│   │   ├── test_coverage.yml        ❌ Not created yet
│   │   ├── readers.yml              ❌ Not created yet (per-package)
│   │   ├── aux.yml                  ❌ Not created yet
│   │   └── ... (one per package)
│   └── actions/setup/               ✅ Created
├── packages/
│   ├── canvod-readers/              ✅ Created (minimal)
│   │   ├── src/canvod/readers/      ⚠️  Should be namespace package
│   │   ├── tests/                   ❌ Not created
│   │   ├── docs/                    ❌ Not created
│   │   ├── pyproject.toml           ✅ Created (needs expansion)
│   │   ├── Justfile                 ❌ Not created
│   │   └── README.md                ❌ Not created
│   └── ... (same for all packages)
├── canvodpy/ (umbrella)
│   ├── src/canvod/                  ⚠️  Currently src/canvodpy/
│   ├── pyproject.toml               ✅ Created
│   └── tests/                       ❌ Not created
├── docs/                            ✅ Created (empty)
├── pyproject.toml                   ✅ Created
├── Justfile                         ✅ Created
└── README.md                        ❌ Not created
```

## ⚠️  Critical Issues

### Issue 1: Namespace Packages
**Current:** `packages/canvod-readers/src/canvod_readers/`
**Should be:** `packages/canvod-readers/src/canvod/readers/`

**Why?** For proper namespace packaging:
```python
# Should work:
from canvod.readers import Rnxv3Obs
from canvod.aux import AuxData
from canvod.grids import HemiGrid

# NOT:
from canvod_readers import Rnxv3Obs  # Wrong!
```

### Issue 2: Umbrella Package Location
**Current:** `canvodpy/src/canvodpy/`
**Should be:** `canvodpy/src/canvod/`

The umbrella should also use the `canvod` namespace.

### Issue 3: Package pyproject.toml Too Minimal
Each package needs full TUW-GEO metadata:
- authors, description, classifiers
- [dependency-groups] dev
- [tool.pytest.ini_options]
- [tool.coverage.run]

## 📝 Next Steps Priority

### High Priority (Before Moving Code)
1. Fix namespace package structure (canvod.readers, not canvod_readers)
2. Add per-package Justfiles
3. Add per-package tests/ directories
4. Expand per-package pyproject.toml files

### Medium Priority
5. Add GitHub Actions workflows
6. Add .pre-commit-config.yaml
7. Add README.md files (root + per package)
8. Add LICENSE

### Low Priority (Can be added later)
9. Add myst.yml and docs/index.ipynb
10. Add CONTRIBUTING.md
11. Add test_meta.py files

## 🔍 Tooling Verification

### Installed Tools (via uv sync)
- ✅ pytest 9.0.2
- ✅ pytest-cov 7.0.0
- ✅ pytest-mock 3.15.1
- ✅ ruff 0.14.10
- ✅ ty 0.0.9
- ✅ mystmd 1.7.1
- ✅ ipykernel 7.1.0

### Available Commands
```bash
just check          # ✅ Works (lint + format + type)
just test           # ⚠️  Will fail (no tests yet)
just check-package  # ✅ Works (per-package)
just test-package   # ⚠️  Will fail (no tests yet)
just sync           # ✅ Works
just clean          # ✅ Works
just hooks          # ⚠️  Will fail (no .pre-commit-config.yaml)
just docs           # ⚠️  Will fail (no myst.yml)
```

## ✅ Final Assessment

**Current State:** 40% complete
- ✅ Core structure correct
- ✅ Workspace configured
- ✅ Tooling installed
- ⚠️  Namespace packages wrong
- ❌ Per-package setup incomplete
- ❌ CI/CD not configured
- ❌ Documentation not set up

**Recommendation:** 
1. Fix namespace package structure FIRST
2. Then proceed with canvod-readers migration
