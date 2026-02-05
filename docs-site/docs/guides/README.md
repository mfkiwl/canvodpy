# Release & Publishing Guides

This directory contains comprehensive guides for the release infrastructure and PyPI publishing setup.

## Contents

### Core Documentation

- **[HOW_RELEASE_WORKS.md](HOW_RELEASE_WORKS.md)** - Deep dive into the complete release system
  - Conventional commits system
  - Git changelog generation
  - Version management with commitizen
  - GitHub releases automation
  - PyPI publishing with OIDC
  - Troubleshooting guide

- **[PYPI_SETUP.md](PYPI_SETUP.md)** - Step-by-step PyPI configuration
  - TestPyPI setup (practice first!)
  - Real PyPI setup
  - OIDC trusted publishing configuration
  - GitHub environments
  - Testing procedures

### Background

- **[PY_BOOTSTRAP_ANALYSIS.md](PY_BOOTSTRAP_ANALYSIS.md)** - Analysis of modern Python templates
  - Comparison with py-bootstrap template
  - Features we adopted
  - Decision rationale

## Quick Start

### For Contributors

**Read:** `HOW_RELEASE_WORKS.md` to understand how everything works

**Key concepts:**
- Conventional commits (required!)
- How `just release` automates everything
- How OIDC secures PyPI uploads

### For Maintainers

**Read:** `PYPI_SETUP.md` when ready to publish to PyPI

**Steps:**
1. Set up TestPyPI first (safe practice)
2. Test with beta release
3. Set up real PyPI
4. First production release

## Also See

- [VERSIONING.md](../../VERSIONING.md) - Versioning strategy (unified SemVer)
- [RELEASING.md](../../RELEASING.md) - Release process checklist
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - How to contribute with conventional commits
