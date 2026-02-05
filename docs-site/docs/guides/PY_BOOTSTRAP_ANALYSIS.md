# py-bootstrap Template Analysis

Analysis of [npikall/py-bootstrap](https://github.com/npikall/py-bootstrap)
for potential features to integrate into canvodpy monorepo.

**Date:** 2026-02-04

## 📋 Template Overview

Modern Python project template using Copier (not Cookiecutter), focusing on
2026 best practices. Key philosophy: "Python Developer Tooling Handbook"
compliant.

## ✅ Already Have (Good Match)

| Feature | Theirs | Ours | Status |
|---------|--------|------|--------|
| uv | ✅ | ✅ | ✅ Match |
| just | ✅ | ✅ | ✅ Match |
| ruff | ✅ | ✅ | ✅ Match |
| ty (type checking) | ✅ | ✅ | ✅ Match |
| pytest | ✅ | ✅ | ✅ Match |
| GitHub Actions | ✅ | ✅ | ✅ Match |
| Pre-commit hooks | ✅ | ✅ | ✅ Match |
| Code quality CI | ✅ | ✅ | ✅ Match |
| Testing CI | ✅ | ✅ | ✅ Match |

## 🆕 Features We Don't Have

### 1. **Git Changelog** (⭐ HIGH VALUE)

**What:** Auto-generates CHANGELOG.md from git commits using conventional
commits (Angular style).

**Tool:** [git-changelog](https://pawamoy.github.io/git-changelog/)

**Their Justfile command:**
```just
changelog VERSION="auto":
    uvx git-changelog -Tio CHANGELOG.md -B="{{VERSION}}" -c angular
```

**Their workflow:** Manual changelogs are error-prone. They:
1. Write commits with conventional format (`feat:`, `fix:`, `docs:`, etc.)
2. Run `just changelog` before release
3. Git-changelog parses commits → beautiful CHANGELOG.md
4. Commit changelog → bump version → tag

**Pros:**
- ✅ No manual changelog maintenance
- ✅ Enforces conventional commits (good for monorepo)
- ✅ Auto-links to GitHub issues/PRs
- ✅ Groups by type (Features, Bug Fixes, Breaking Changes)
- ✅ Easy to integrate with uv tool: `uvx git-changelog`

**Cons:**
- ⚠️ Requires team discipline (conventional commit messages)
- ⚠️ Monorepo complexity (might need per-package changelogs?)

**Recommendation:** ⭐⭐⭐⭐⭐ **HIGHLY RECOMMENDED**
- Start with root CHANGELOG.md for whole monorepo
- Later: Could generate per-package changelogs with path filters

---

### 2. **Version Bumping Workflow** (⭐ HIGH VALUE)

**What:** Integrated `just` commands for version management

**Their Justfile commands:**
```just
# Bump version, lock, commit, tag
bump VERSION:
    uv version {{ VERSION }}  # NEW! uv has built-in version command
    uv lock
    git add pyproject.toml uv.lock
    git commit -m "chore: bumped version to {{VERSION}}"
    git tag -a "v{{VERSION}}"

# Complete release workflow
release VERSION: test
    @just changelog "v{{VERSION}}"
    git add CHANGELOG.md
    git commit -m "chore: updated Changelog"
    @just bump "{{VERSION}}"
    @echo "Success! Run 'git push && git push --tags' now."
```

**Key insight:** `uv version major|minor|patch` is NEW (uv 0.9+)!
We're not using this yet.

**Workflow:**
```bash
just release 0.2.0  # Runs tests → updates changelog → bumps version → tags
git push && git push --tags  # Manual push (safety)
```

**Pros:**
- ✅ DRY: One command for entire release
- ✅ Safety: Tests run first
- ✅ Consistency: Same steps every time
- ✅ uv version built-in (no external tools)

**Cons:**
- ⚠️ Monorepo needs per-package versioning (canvodpy uses this)
- ⚠️ Would need adaptation for workspace packages

**Recommendation:** ⭐⭐⭐⭐ **RECOMMENDED with adaptations**
- Add `just bump-package PKG VERSION` for individual packages
- Keep root package bumps separate from sub-packages

---

### 3. **GoReleaser Integration** (⭐ MEDIUM VALUE)

**What:** Automated GitHub Releases with assets

**Tool:** [GoReleaser](https://goreleaser.com) (despite name, works for Python)

**Their setup:**
1. `.goreleaser.yaml` config (builds wheel + sdist via uv)
2. GitHub workflow triggers on `v*` tags
3. GoReleaser builds, creates GitHub release, uploads assets

**Their `.goreleaser.yaml`:**
```yaml
version: 2
builds:
  - id: wheel
    builder: uv
    buildmode: wheel
  - id: sdist
    builder: uv
    buildmode: sdist
changelog:
  sort: asc
  filters:
    exclude:
      - "^docs:"
      - "^test:"
```

**Their release workflow:**
```yaml
on:
  push:
    tags:
      - "v*"
jobs:
  release:
    - uses: goreleaser/goreleaser-action@v6
```

**Pros:**
- ✅ Auto-creates GitHub releases on tag push
- ✅ Uploads wheel + sdist as release assets
- ✅ Pulls changelog from git-changelog
- ✅ Consistent release notes

**Cons:**
- ⚠️ Another tool to learn (Go binary)
- ⚠️ Monorepo complexity (7 packages = 7 releases?)
- ⚠️ Might be overkill if not publishing to PyPI often

**Recommendation:** ⭐⭐⭐ **OPTIONAL** (consider later)
- Good for when you're ready to publish to PyPI
- For now, manual releases might be simpler
- Revisit when package is more stable

---

### 4. **Release Notes Workflow** (⭐ HIGH VALUE)

**What:** GitHub release workflow without GoReleaser (simpler alternative)

**Their workflow:**
```yaml
on:
  push:
    tags:
      - "v*"
steps:
  - Install git-changelog
  - git-changelog --release-notes > release-notes.md
  - gh release create ${{ github.ref_name }} \
      --notes-file release-notes.md \
      --draft
```

**Workflow:**
1. Tag with `v1.2.3` and push
2. Workflow auto-creates GitHub draft release
3. Release notes pulled from commits since last tag
4. Manual review → publish

**Pros:**
- ✅ Simpler than GoReleaser
- ✅ No extra binaries needed (just git-changelog)
- ✅ Draft mode = safety
- ✅ Works great with git-changelog

**Cons:**
- ⚠️ Manual asset uploads (wheel/sdist)
- ⚠️ Still need to adapt for monorepo

**Recommendation:** ⭐⭐⭐⭐⭐ **HIGHLY RECOMMENDED**
- Much simpler than GoReleaser for scientific packages
- Good middle ground between manual and fully automated
- Pair with git-changelog for best results

---

### 5. **Recipe Groups in Justfile** (⭐ LOW VALUE)

**What:** Organized `just --list` output with `[group("name")]` annotation

**Example:**
```just
[group("test")]
test:
    pytest

[group("chore")]
changelog:
    git-changelog
```

**Output:**
```
Available recipes:
[test]
    test   # Run tests
[chore]
    changelog   # Generate changelog
```

**Pros:**
- ✅ Better UX for `just --list`
- ✅ Groups related commands

**Cons:**
- ⚠️ Cosmetic improvement only
- ⚠️ Requires just 1.20+ (we have 1.46)

**Recommendation:** ⭐⭐ **NICE TO HAVE**
- Easy to add (`[group("name")]` before recipes)
- Low priority, good for cleanup later

---

### 6. **Alternative: Prek vs Pre-commit** (⭐ LOW VALUE)

**What:** [Prek](https://prek.j178.dev) - faster pre-commit alternative written
in Rust

**Trade-offs:**
- Prek: Faster, Rust-based, newer, less mature
- Pre-commit: Slower, Python-based, mature, huge ecosystem

**Recommendation:** ⚠️ **STICK WITH PRE-COMMIT**
- Pre-commit is mature and works well
- Prek is interesting but switching has no clear benefit
- Not worth migration effort

---

## 🎯 Recommended Implementation Plan

### Phase 1: High-Value Quick Wins ✅

**1. Git Changelog Setup**
```bash
# Add to pyproject.toml [tool.uv] or [project.optional-dependencies]
# None needed - use uvx!

# Add to Justfile
changelog VERSION="auto":
    uvx git-changelog -Tio CHANGELOG.md -B="{{VERSION}}" -c angular
```

**Files to create:**
- None! Just add Justfile recipe

**Configuration needed:**
- Optional: `.git-changelog.toml` for monorepo path filters
- Convention: Team must use conventional commits

**2. Version Bump Workflow**
```bash
# Add to Justfile
bump VERSION:
    uv version {{ VERSION }}
    uv lock
    git add pyproject.toml uv.lock
    git commit -m "chore: bumped version to {{VERSION}}"
    git tag -a "v{{VERSION}}" -m "Release v{{VERSION}}"

bump-package PKG VERSION:
    cd {{PKG}} && uv version {{VERSION}}
    uv lock
    git add {{PKG}}/pyproject.toml uv.lock
    git commit -m "chore({{PKG}}): bumped to {{VERSION}}"
    git tag -a "{{PKG}}-v{{VERSION}}" -m "{{PKG}} v{{VERSION}}"

release VERSION: test
    @just changelog "v{{VERSION}}"
    git add CHANGELOG.md
    git commit -m "chore: updated Changelog"
    @just bump "{{VERSION}}"
    @echo "✅ Success! Run 'git push && git push --tags' now."
```

**3. GitHub Release Workflow**
```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags:
      - "v*"
permissions:
  contents: write
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0  # Need full history for changelog

      - uses: astral-sh/setup-uv@v7

      - name: Generate release notes
        run: |
          uvx git-changelog --release-notes > release-notes.md

      - name: Create GitHub release
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          gh release create ${{ github.ref_name }} \
            --repo ${{ github.repository }} \
            --title "canvodpy ${{ github.ref_name }}" \
            --notes-file release-notes.md \
            --draft
```

### Phase 2: Optional Enhancements 🔮

**GoReleaser** - Only if publishing to PyPI regularly
**Recipe groups** - Nice UX improvement for `just --list`
**Prek** - No compelling reason to switch

---

## 📝 Conventional Commits Primer

Required for git-changelog to work properly.

**Format:** `<type>(<scope>): <description>`

**Types:**
- `feat:` New feature (→ "Features" in changelog)
- `fix:` Bug fix (→ "Bug Fixes")
- `docs:` Documentation only
- `refactor:` Code restructure (no behavior change)
- `test:` Add/modify tests
- `chore:` Build/tools (dependencies, config)
- `perf:` Performance improvements
- `ci:` CI/CD changes

**Examples:**
```bash
git commit -m "feat(vod): add tau-omega calculator"
git commit -m "fix(readers): handle empty RINEX files"
git commit -m "docs: update installation instructions"
git commit -m "chore: bump version to 0.2.0"
git commit -m "feat(viz)!: redesign 3D plotting API"  # ! = breaking
```

**Monorepo scopes:**
- `(readers)`, `(vod)`, `(grids)`, `(store)`, `(viz)`, `(aux)`, `(utils)`
- Or omit scope for changes affecting multiple packages

---

## 🚦 Decision Matrix

| Feature | Value | Effort | Priority | Adopt? |
|---------|-------|--------|----------|--------|
| git-changelog | ⭐⭐⭐⭐⭐ | Low | 🔴 HIGH | ✅ YES |
| Version bumping | ⭐⭐⭐⭐ | Low | 🔴 HIGH | ✅ YES |
| Release workflow | ⭐⭐⭐⭐⭐ | Low | 🔴 HIGH | ✅ YES |
| GoReleaser | ⭐⭐⭐ | Medium | 🟢 LOW | ⏸️ LATER |
| Recipe groups | ⭐⭐ | Low | 🟢 LOW | ⏸️ LATER |
| Prek | ⭐ | Medium | 🟢 LOW | ❌ NO |

---

## 🎓 Key Learnings

1. **Conventional commits are the foundation**
   - Makes git-changelog work
   - Makes monorepo history readable
   - Industry standard in 2026

2. **uv has version management built-in**
   - `uv version major|minor|patch`
   - `uv version 1.2.3`
   - No need for bump2version, etc.

3. **git-changelog pairs perfectly with GitHub releases**
   - One source of truth (git commits)
   - No manual CHANGELOG.md maintenance
   - Release notes auto-generated

4. **Monorepo adds complexity**
   - Need per-package versioning
   - Need path filters for changelogs
   - Consider package-specific tags (`canvod-v1.0.0`)

---

## 📚 Resources

- **git-changelog:** https://pawamoy.github.io/git-changelog/
- **Conventional Commits:** https://www.conventionalcommits.org/
- **GoReleaser:** https://goreleaser.com
- **Python Tooling Handbook:** https://pydevtools.com/handbook/
- **py-bootstrap repo:** https://github.com/npikall/py-bootstrap
