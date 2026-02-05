# canvod-auxiliary

**Auxiliary data augmentation for GNSS VOD analysis**

Part of the [canVODpy](https://github.com/nfb2021/canvodpy) ecosystem.

## Overview

`canvod-auxiliary` provides tools for downloading, parsing, and interpolating auxiliary GNSS data files including:

- **SP3 ephemerides** - Satellite orbit positions and velocities
- **CLK corrections** - Satellite clock corrections
- **Interpolation strategies** - Hermite and linear interpolation for temporal alignment
- **Augmentation framework** - Pluggable system for enriching RINEX datasets

## Features

✨ **SP3 File Handling**
- Download from ESA or NASA CDDIS servers
- Parse SP3 format (positions + velocities)
- Cubic Hermite interpolation using velocities
- Fallback to linear interpolation

✨ **Clock Corrections**
- CLK file download and parsing
- Jump-aware interpolation
- Segment-based processing

✨ **Flexible Pipeline**
- Automatic file discovery and caching
- Thread-safe downloading
- Configurable FTP servers and agencies

✨ **Augmentation System**
- Spherical coordinate calculation (φ, θ, r)
- Clock correction application
- Extensible via ABC pattern

## Installation

```bash
# From PyPI (when published)
pip install canvod-auxiliary

# Development install
cd canvodpy/packages/canvod-auxiliary
uv pip install -e .
```

## Quick Start

### Basic SP3 Usage

```python
from pathlib import Path
from canvod.aux import Sp3File

# Load SP3 ephemeris file
sp3 = Sp3File.from_file(Path("COD0MGXFIN_20240150000_01D_05M_ORB.SP3"))

# Access data as xarray Dataset
data = sp3.data
print(data)  # Coordinates: epoch, sid | Variables: X, Y, Z, Vx, Vy, Vz

# Get interpolation strategy
strategy = sp3.get_interpolation_strategy()
print(strategy.config)  # Sp3Config(use_velocities=True)
```

### Pipeline Usage

```python
from canvod.aux import AuxDataPipeline
from pathlib import Path

# Create pipeline
pipeline = AuxDataPipeline(
    agency="COD",
    product_type="final",
    ftp_server="ftp://gssc.esa.int/gnss",
    aux_file_path=Path("aux_data")
)

# Get augmented data for specific date
augmented_ds = pipeline.get_or_create_aux_data(
    yyyydoy="2024015",
    target_epochs=my_rinex_epochs
)
```

### Custom Interpolation

```python
from canvod.aux import Sp3Config, Sp3InterpolationStrategy
import numpy as np

# Configure interpolation
config = Sp3Config(use_velocities=True, fallback_method='cubic')
strategy = Sp3InterpolationStrategy(config=config)

# Interpolate to new epochs
target_epochs = np.array([...])  # Your target timestamps
interpolated = strategy.interpolate(sp3_dataset, target_epochs)
```

## Documentation

📚 **[Full Documentation →](docs/index.md)**

- [Installation Guide](docs/installation.md)
- [Quick Start Tutorial](docs/quickstart.md)
- [API Reference](docs/api-reference.md)
- [Architecture Overview](docs/architecture.md)

## Package Structure

```
canvod-auxiliary/
├── src/canvod/aux/
│   ├── __init__.py              # Public API
│   ├── _internal/               # Internal utilities
│   │   ├── units.py             # UREG unit registry
│   │   ├── date_utils.py        # YYYYDOY, GPS week utils
│   │   └── logger.py            # Logging utilities
│   ├── reader.py                # AuxFile ABC
│   ├── container.py             # FTP downloader
│   ├── interpolation.py         # Interpolation strategies
│   ├── sp3.py                   # SP3 handler
│   ├── clk.py                   # CLK handler
│   ├── pipeline.py              # AuxDataPipeline
│   └── augmentation.py          # Augmentation framework
├── tests/                       # 65 tests, 100% core coverage
├── docs/                        # MyST documentation
└── pyproject.toml
```

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/nfb2021/canvodpy.git
cd canvodpy/packages/canvod-auxiliary

# Install dependencies
uv sync

# Install pre-commit hooks
pre-commit install
```

### Commands

```bash
# Run tests
pytest

# With coverage
pytest --cov=canvod.aux --cov-report=html

# Lint and format
ruff check .
ruff format .

# Type check
ty check src/
```

### Project Tasks (Just)

If you have [Just](https://github.com/casey/just) installed:

```bash
just test          # Run tests
just check         # Lint + format check
just fix           # Auto-fix linting issues
just docs          # Build documentation
```

## Dependencies

**Core:**
- scipy ≥1.15.0
- numpy ≥1.24.0
- xarray ≥2023.12.0
- pydantic ≥2.5.0
- pint ≥0.23

**Network:**
- requests ≥2.31.0
- python-dotenv ≥1.0.1
- retrying ≥1.3.4
- beautifulsoup4 ≥4.12.0
- lxml ≥5.3.0

**Development:**
- pytest ≥8.0
- pytest-cov ≥5.0
- ruff ≥0.14
- ty ≥0.0.9

## Contributing

Contributions welcome! Please see the [main repository](https://github.com/nfb2021/canvodpy) for contribution guidelines.

## License

Apache License 2.0 - See LICENSE file

## Related Packages

Part of the canVODpy ecosystem:

- **[canvod-readers](../canvod-readers/)** - RINEX data readers
- **[canvod-grids](../canvod-grids/)** - Hemisphere grids
- **[canvod-vod](../canvod-vod/)** - VOD calculations
- **[canvod-store](../canvod-store/)** - Icechunk storage
- **[canvod-viz](../canvod-viz/)** - Visualization
- **[canvodpy](../../canvodpy/)** - Umbrella package

## Citation

If you use canvod-auxiliary in your research, please cite:

```bibtex
@software{canvodpy2025,
  author = {Bader, Nicolas F.},
  title = {canVODpy: GNSS Vegetation Optical Depth Analysis},
  year = {2025},
  publisher = {TU Wien},
  url = {https://github.com/nfb2021/canvodpy}
}
```

## Author & Affiliation

**Nicolas François Bader**
Climate and Environmental Remote Sensing Research Unit (CLIMERS)
Department of Geodesy and Geoinformation
TU Wien (Vienna University of Technology)
Email: nicolas.bader@geo.tuwien.ac.at
[https://www.tuwien.at/en/mg/geo/climers](https://www.tuwien.at/en/mg/geo/climers)
