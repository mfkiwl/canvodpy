# Versioning Strategy for canvodpy

**Last Updated:** 2026-02-04  
**Status:** Active

## Overview

canvodpy uses **unified semantic versioning** across all packages in the monorepo. This means all packages share the same version number and are released together.

## Rationale

### Why Unified Versioning?

1. **FAIR Principles & Open Science**
   - Single version number for reproducibility
   - Clear citation in scientific papers
   - Unambiguous environment recreation

2. **User Experience**
   - Simple to understand: "I use canvodpy 0.2.0"
   - Not: "I use canvod-readers 1.0.0, canvod-vod 0.3.0, ..."
   - Easy installation: `pip install canvodpy==0.2.0`

3. **Compatibility Guarantees**
   - All packages tested together
   - No version mismatch issues
   - Clear compatibility contracts

### Monorepo with Sollbruchstellen (Breaking Points)

The monorepo structure provides **modularity at development time** while maintaining **coherence at release time**:

- **Development:** Independent package development and testing
- **Release:** Coordinated releases with unified version
- **Installation:** Users can install individual packages if needed
  - `pip install canvod-readers==0.2.0` (same version as full release)

## Semantic Versioning

We follow [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH
```

### Version Increments

**MAJOR (X.0.0)** - Breaking changes
- API changes that break backward compatibility
- Removal of deprecated features
- Major architecture changes

Examples:
- Changing function signatures
- Removing public APIs
- Renaming packages

**MINOR (0.X.0)** - New features
- New functionality (backward compatible)
- New modules or classes
- Significant enhancements

Examples:
- Adding new VOD calculation methods
- New grid types
- New data readers

**PATCH (0.0.X)** - Bug fixes
- Bug fixes (backward compatible)
- Documentation updates
- Performance improvements (no API changes)

Examples:
- Fixing calculation errors
- Correcting docstrings
- Optimizing algorithms

### Pre-release Versions

For development and testing:

```
0.2.0-alpha.1  # Early testing
0.2.0-beta.1   # Feature complete, testing
0.2.0-rc.1     # Release candidate
```

## Version Management Workflow

### 1. During Development

Commit with conventional commits:
```bash
git commit -m "feat(vod): add tau-omega calculator"
git commit -m "fix(readers): handle empty RINEX files"
```

### 2. Creating a Release

Use the `just release` command:

```bash
# For a minor release (new features)
just release 0.2.0

# For a patch release (bug fixes)
just release 0.1.1

# For a major release (breaking changes)
just release 1.0.0
```

This command:
1. Runs all tests
2. Generates changelog from commits
3. Bumps version in all packages
4. Creates git tag
5. Prompts you to push

### 3. Manual Version Bump (Advanced)

```bash
# Bump by increment
just bump minor  # 0.1.0 -> 0.2.0
just bump patch  # 0.1.0 -> 0.1.1
just bump major  # 0.1.0 -> 1.0.0

# Bump to specific version
just bump 0.2.0
```

## Version Files

All package versions are synchronized via `commitizen`:

```toml
[tool.commitizen]
version = "0.1.0"
version_files = [
    "canvodpy/pyproject.toml:version",
    "packages/canvod-readers/pyproject.toml:version",
    "packages/canvod-auxiliary/pyproject.toml:version",
    "packages/canvod-grids/pyproject.toml:version",
    "packages/canvod-vod/pyproject.toml:version",
    "packages/canvod-store/pyproject.toml:version",
    "packages/canvod-viz/pyproject.toml:version",
    "packages/canvod-utils/pyproject.toml:version",
]
```

## Git Tags

Tags follow the format: `vMAJOR.MINOR.PATCH`

Examples:
- `v0.1.0` - First minor release
- `v0.1.1` - Patch release
- `v1.0.0` - First stable release
- `v0.2.0-beta.1` - Beta release

## Breaking Changes Policy

### Signaling Breaking Changes

1. **In Commit Messages:**
   ```bash
   git commit -m "feat(viz)!: redesign 3D plotting API"
   # The ! indicates a breaking change
   ```

2. **In CHANGELOG:**
   - Clearly marked under "Breaking Changes" section
   - Migration guide provided

3. **In Version Number:**
   - MAJOR version bump (e.g., 0.9.0 → 1.0.0)

### Deprecation Policy

Before removing features:

1. **Deprecation Warning (Version N)**
   - Add deprecation warning in code
   - Document in CHANGELOG
   - Keep feature functional

2. **Deprecation Notice (Version N+1)**
   - Louder warnings
   - Migration guide in docs

3. **Removal (Version N+2)**
   - Remove deprecated feature
   - MAJOR version bump

Example timeline:
- v0.8.0: Feature X deprecated (warning added)
- v0.9.0: Feature X marked for removal (louder warning)
- v1.0.0: Feature X removed (breaking change, major bump)

## Citation in Scientific Papers

### Recommended Citation Format

```bibtex
@software{canvodpy2026,
  author = {Bader, Nicolas and Contributors},
  title = {canvodpy: GNSS Vegetation Optical Depth Analysis},
  version = {0.2.0},
  year = {2026},
  url = {https://github.com/nfb2021/canvodpy},
  doi = {10.5281/zenodo.XXXXXXX}
}
```

### In-text Citation

> "Analysis was performed using canvodpy v0.2.0 (Bader et al., 2026)."

## Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG reviewed
- [ ] Version number follows SemVer
- [ ] Breaking changes documented
- [ ] Migration guide (if breaking changes)
- [ ] Git tag created
- [ ] GitHub release created
- [ ] PyPI release published (when ready)
- [ ] Zenodo DOI minted (for citations)

## Questions & Answers

**Q: Why not independent versioning per package?**  
A: Scientific reproducibility requires a single version number. "I used canvodpy 0.2.0" is clearer than tracking 7 different package versions.

**Q: Can I install just one package?**  
A: Yes! `pip install canvod-readers==0.2.0` works, but the version matches the full release.

**Q: What if only one package changes?**  
A: The entire monorepo gets a version bump (usually PATCH). This is intentional for consistency.

**Q: When do we bump to 1.0.0?**  
A: When the API is stable, well-tested, and we're ready to commit to backward compatibility.

## See Also

- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [RELEASING.md](./RELEASING.md) - Release process details
