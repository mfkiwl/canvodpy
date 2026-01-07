# canVODpy

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Static Badge](https://img.shields.io/badge/TU_Wien_GEO-Project-gray?style=flat&labelColor=%23006699&color=gray&link=https%3A%2F%2Fwww.tuwien.at%2Fen%2Fmg%2Fgeo)](https://www.tuwien.at/mg/geo)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

GNSS Vegetation Optical Depth (VOD) analysis package - Modern monorepo architecture.

> [!IMPORTANT]
> This project uses `uv` for package management and `Just` for task automation.
> - Install `uv`: [uv documentation](https://docs.astral.sh/uv/getting-started/installation/)
> - Install `Just`: [Just documentation](https://github.com/casey/just)

## Overview

canVODpy is a modular ecosystem for GNSS-based vegetation optical depth analysis, organized as a monorepo with independent packages:

- **canvod-readers** - RINEX and GNSS data format readers
- **canvod-aux** - Auxiliary data handling
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

```bash
# Clone repository
git clone https://github.com/nfb2021/canvodpy.git
cd canvodpy

# Install dependencies
uv sync

# Install pre-commit hooks
just hooks

# Run tests
just test

# Check code quality
just check
```

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
│   ├── canvod-aux/
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

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

## Affiliation

Developed at TU Wien, Department of Geodesy and Geoinformation (GEO).
