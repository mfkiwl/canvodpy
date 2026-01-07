# Missing TUW-GEO Template Components

## Workspace Root - MISSING

### Critical Files
- [ ] LICENSE (choose: MIT, Unlicense, Apache 2.0, None)
- [ ] README.md (workspace overview)
- [ ] CONTRIBUTING.md (contribution guidelines)
- [ ] .pre-commit-config.yaml (pre-commit hooks)

### GitHub Workflows
- [ ] .github/workflows/code_quality.yml (linting, formatting, types)
- [ ] .github/workflows/test_coverage.yml (pytest + coverage)
- [ ] .github/workflows/test_platforms.yml (multi-platform testing)

### Root Justfile Enhancements
- [ ] Add `testall` command (test multiple Python versions)
- [ ] Add `bump` command (version bumping)
- [ ] Add `tag` command (git tagging)
- [ ] Add `init` command (git init helper)
- [ ] Add `docs` command (myst serve)
- [ ] Add `dist` command (uv build)
- [ ] Add color formatting

## Per-Package (All 7 Packages) - MISSING

### Each package needs:
- [ ] README.md (package-specific)
- [ ] Justfile (package-level commands)
- [ ] tests/test_meta.py (basic test structure)
- [ ] docs/index.ipynb (documentation notebook)
- [ ] myst.yml (MyST documentation config)

## What We HAVE ✅

### Workspace Root
- ✅ pyproject.toml (workspace config)
- ✅ .gitignore
- ✅ Justfile (basic version)
- ✅ .python-version
- ✅ canvodpy.code-workspace (VSCode)
- ✅ .github/actions/setup/action.yml

### Per-Package
- ✅ pyproject.toml (with uv_build + namespace config)
- ✅ src/canvod/{subpackage}/__init__.py

## License Options (from cookiecutter)

1. **MIT** - Permissive, most common
2. **Unlicense** - Public domain
3. **Apache License 2.0** - Permissive with patent grant
4. **None** - No license (all rights reserved)

## Total Missing Items

- **Root**: 7 files
- **Per-package**: 5 files × 7 packages = 35 files
- **Total**: 42 files to add
