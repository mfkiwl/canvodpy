# canVODpy

<!-- Build & Quality -->
[![Platform Tests](https://github.com/nfb2021/canvodpy/actions/workflows/test_platforms.yml/badge.svg)](https://github.com/nfb2021/canvodpy/actions/workflows/test_platforms.yml)
[![Code Coverage](https://github.com/nfb2021/canvodpy/actions/workflows/test_coverage.yml/badge.svg)](https://github.com/nfb2021/canvodpy/actions/workflows/test_coverage.yml)
[![Code Quality](https://github.com/nfb2021/canvodpy/actions/workflows/code_quality.yml/badge.svg)](https://github.com/nfb2021/canvodpy/actions/workflows/code_quality.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

<!-- Python & Platforms -->
[![Python Version](https://img.shields.io/badge/python-3.13%20|%203.14-blue.svg)](https://www.python.org/)
[![Platforms](https://img.shields.io/badge/platform-Linux%20|%20macOS%20|%20Windows-lightgrey)](https://github.com/nfb2021/canvodpy/actions/workflows/test_platforms.yml)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

<!-- Modern Stack -->
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-E92063?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![MyST Markdown](https://img.shields.io/badge/MyST-Markdown-orange?logo=markdown&logoColor=white)](https://mystmd.org/)
[![Zarr](https://img.shields.io/badge/Zarr-v3-00A3E0?logo=databricks&logoColor=white)](https://zarr.dev/)

<!-- Standards & Best Practices -->
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196?logo=conventionalcommits&logoColor=white)](https://conventionalcommits.org)
[![FAIR Principles](https://img.shields.io/badge/FAIR-Principles-00A3E0)](https://www.go-fair.org/fair-principles/)
[![OIDC Publishing](https://img.shields.io/badge/OIDC-Trusted_Publisher-4285F4?logo=openid&logoColor=white)](https://docs.pypi.org/trusted-publishers/)

<!-- Project & License -->
[![CLIMERS @ TU Wien](https://img.shields.io/badge/CLIMERS_@_GEO_TU_WIEN-Project-gray?style=flat&labelColor=%23006699&color=gray&link=https%3A%2F%2Fwww.tuwien.at%2Fen%2Fmg%2Fgeo%2Fclimers)](https://www.tuwien.at/en/mg/geo/climers)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

GNSS Vegetation Optical Depth (VOD) analysis package - Modern monorepo architecture.

> [!IMPORTANT]
> This project uses `uv` for package management and `Just` for task automation.
> - Install `uv`: [uv documentation](https://docs.astral.sh/uv/getting-started/installation/)
> - Install `Just`: [Just documentation](https://github.com/casey/just)

## Overview

canVODpy is a modular ecosystem for GNSS-T-based vegetation optical depth analysis, organized as a monorepo with independent packages:

- **canvod-readers** - RINEX and GNSS data format readers
- **canvod-auxiliary** - Auxiliary data handling
- **canvod-grids** - HEALPix and hemispheric grid operations
- **canvod-vod** - Vegetation Optical Depth calculations
- **canvod-store** - Icechunk and Zarr storage backends
- **canvod-viz** - Visualization and plotting utilities
- **canvodpy** - Umbrella package providing unified access

## Installation

```bash
# Install from PyPI (when published)
uv pip install canvodpy

# Or install specific components
uv pip install canvod-readers canvod-grids
```

## Development Setup

### Prerequisites

This project requires two tools that need to be installed separately:

1. **uv** - Fast Python package manager
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # Or via package manager
   brew install uv  # macOS
   ```

2. **just** - Command runner (like make, but better)
   ```bash
   # macOS/Linux
   curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash
   
   # Or via package manager
   brew install just      # macOS
   cargo install just     # Rust
   apt install just       # Ubuntu 23.04+
   ```

### Setup Steps

```bash
# Clone repository
git clone https://github.com/nfb2021/canvodpy.git
cd canvodpy

# Verify required tools are installed
just check-dev-tools  # Checks uv, just, python3

# Install Python dependencies
uv sync

# Install pre-commit hooks
just hooks

# Run tests
just test

# Check code quality
just check
```

### Available Commands

See all available commands:
```bash
just --list
```

Common commands:
- `just check` - Lint, format, and type-check
- `just test` - Run all tests
- `just test-coverage` - Run tests with coverage report
- `just changelog` - Generate CHANGELOG from commits
- `just release <VERSION>` - Create a new release

## Documentation

- **[docs/guides/HOW_RELEASE_WORKS.md](docs/guides/HOW_RELEASE_WORKS.md)** - Complete guide to the release system
- **[docs/guides/PYPI_SETUP.md](docs/guides/PYPI_SETUP.md)** - PyPI publishing setup
- **[VERSIONING.md](VERSIONING.md)** - Versioning strategy
- **[RELEASING.md](RELEASING.md)** - Release process
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- `just clean` - Clean build artifacts
- `just docs` - Preview documentation

## Usage

```python
# Import from namespace packages
from canvod.readers import Rnxv3Obs
from canvod.grids import HemiGrid
from canvod.vod import calculate_vod

# Or use umbrella package
import canvodpy
```

## Project Structure

```
canvodpy/                    # Monorepo root
├── packages/                # Independent packages
│   ├── canvod-readers/
│   ├── canvod-auxiliary/
│   ├── canvod-grids/
│   ├── canvod-vod/
│   ├── canvod-store/
│   └── canvod-viz/
├── canvodpy/               # Umbrella package
├── .github/                # CI/CD workflows
├── docs/                   # Documentation
└── pyproject.toml          # Workspace configuration
```

## Available Commands

```bash
just                # List all commands
just check          # Lint + format + type check
just test           # Run all tests
just sync           # Install/update dependencies
just clean          # Remove build artifacts
just hooks          # Install pre-commit hooks
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

Licensed under the Apache License, Version 2.0. See the [LICENSE file](https://github.com/nfb2021/canvodpy/blob/main/LICENSE) for details.

## Author & Affiliation

**Author:** Nicolas François Bader (nicolas.bader@geo.tuwien.ac.at)

Developed at the **Climate and Environmental Remote Sensing Research Unit (CLIMERS)**
Department of Geodesy and Geoinformation
TU Wien (Vienna University of Technology)
[https://www.tuwien.at/en/mg/geo/climers](https://www.tuwien.at/en/mg/geo/climers)
