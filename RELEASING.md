# Release Process for canvodpy

**Last Updated:** 2026-02-04  
**Audience:** Maintainers

## Overview

This document describes how to create and publish releases for canvodpy.

## Prerequisites

- All CI checks passing
- Main branch is stable
- You have push access to the repository
- All changes are committed and pushed

## Release Types

### Patch Release (0.1.X)
- Bug fixes only
- No new features
- Backward compatible
- Example: `0.1.0` → `0.1.1`

### Minor Release (0.X.0)
- New features
- Backward compatible
- May include bug fixes
- Example: `0.1.0` → `0.2.0`

### Major Release (X.0.0)
- Breaking changes
- API changes
- Requires migration guide
- Example: `0.9.0` → `1.0.0`

## Step-by-Step Release Process

### 1. Prepare the Release

```bash
# Ensure you're on main and up to date
git checkout main
git pull origin main

# Ensure all tests pass
just test

# Run code quality checks
just check
```

### 2. Create the Release

Use the `just release` command with the new version:

```bash
# For a minor release (new features)
just release 0.2.0

# For a patch release (bug fixes)
just release 0.1.1

# For a major release (breaking changes)
just release 1.0.0
```

**What this does:**
1. ✅ Runs all tests
2. 📝 Generates CHANGELOG.md from commits
3. 🔄 Bumps version in all packages
4. 🏷️ Creates git tag `vX.Y.Z`
5. 💾 Commits changes

**Output example:**
```
✅ Release v0.2.0 created!

Next steps:
  1. Review the commits and tag
  2. Push with: git push && git push --tags
  3. GitHub Actions will create the release draft
```

### 3. Review the Changes

Before pushing, review what was created:

```bash
# Check the last commits
git log --oneline -5

# Check the tag
git tag | tail -1

# Review CHANGELOG
cat CHANGELOG.md | head -50

# Check version files
uv version --short
```

### 4. Push to GitHub

If everything looks good:

```bash
# Push commits
git push origin main

# Push tags
git push origin --tags
```

### 5. GitHub Actions Creates Draft Release

The `.github/workflows/release.yml` workflow will:
1. Detect the new tag (`v*.*.*`)
2. Generate release notes from commits
3. Create a **draft release** on GitHub

**Timeline:** ~1-2 minutes

### 6. Review and Publish Release

1. Go to: https://github.com/nfb2021/canvodpy/releases
2. Find the draft release
3. Review:
   - ✅ Release notes are accurate
   - ✅ Version number is correct
   - ✅ No sensitive information
4. Edit if needed (add migration notes, etc.)
5. **Publish release** 🚀

### 7. (Future) PyPI Publishing

Once PyPI publishing is set up:
1. Publishing the GitHub release will trigger PyPI upload
2. Users can install: `pip install canvodpy==X.Y.Z`

## Release Checklist

Before creating a release:

- [ ] All tests passing locally and in CI
- [ ] CHANGELOG reflects all changes
- [ ] Version number follows SemVer
- [ ] Breaking changes documented (if any)
- [ ] Migration guide written (if breaking changes)
- [ ] Documentation updated
- [ ] No uncommitted changes

After pushing tag:

- [ ] GitHub Actions workflow completed
- [ ] Draft release created
- [ ] Release notes are accurate
- [ ] Release published
- [ ] Announcement posted (if major release)

## Troubleshooting

### Issue: `just release` fails with "tests failed"

**Solution:** Fix failing tests first
```bash
just test  # See which tests fail
# Fix the tests
just test  # Verify all pass
```

### Issue: Version bump failed

**Solution:** Check version format
```bash
# Valid formats:
just release 0.2.0     # ✅ Explicit version
just release minor     # ✅ Increment type (cz bump)
just release patch     # ✅ Increment type

# Invalid:
just release v0.2.0    # ❌ Don't include 'v' prefix
just release 0.2       # ❌ Must be X.Y.Z format
```

### Issue: Tag already exists

**Solution:** Delete and recreate (if not pushed yet)
```bash
# Delete local tag
git tag -d v0.2.0

# If already pushed (use with caution!)
git push origin :refs/tags/v0.2.0

# Recreate
just release 0.2.0
```

### Issue: GitHub workflow didn't trigger

**Solution:** Check workflow status
1. Go to: https://github.com/nfb2021/canvodpy/actions
2. Look for "Release" workflow
3. Check for errors
4. Ensure tag matches pattern `v*.*.*`

### Issue: Need to update release after publishing

**Solution:** You can edit published releases
1. Go to the release page
2. Click "Edit release"
3. Update notes
4. Save changes

## Manual Release (Fallback)

If automation fails, create release manually:

1. **Generate changelog:**
   ```bash
   just changelog v0.2.0
   ```

2. **Create GitHub release:**
   - Go to: https://github.com/nfb2021/canvodpy/releases/new
   - Select tag: `v0.2.0`
   - Title: `canvodpy v0.2.0`
   - Copy relevant section from CHANGELOG.md
   - Publish

## Post-Release Tasks

After a successful release:

1. **Announce (for major/minor releases):**
   - Create GitHub discussion
   - Post on team channels
   - Update documentation site

2. **Monitor:**
   - Watch for issues related to new release
   - Check CI for downstream effects

3. **Archive (optional):**
   - Create Zenodo snapshot for DOI
   - Update citation information

## Beta/RC Releases

For pre-releases (testing before stable):

```bash
# Create pre-release version
just release 0.2.0-beta.1
git push && git push --tags
```

Then manually mark as "pre-release" in GitHub UI.

## Semantic Versioning Quick Reference

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Bug fixes only | PATCH | 0.1.0 → 0.1.1 |
| New features (compatible) | MINOR | 0.1.0 → 0.2.0 |
| Breaking changes | MAJOR | 0.9.0 → 1.0.0 |

## See Also

- [VERSIONING.md](./VERSIONING.md) - Versioning strategy
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Contribution guidelines
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
