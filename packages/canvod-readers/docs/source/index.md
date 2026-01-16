# canvod-readers Documentation

**GNSS Data Format Readers for Vegetation Optical Depth Research**

```{toctree}
:maxdepth: 2
:caption: Contents

overview
architecture
rinex_reader
pydantic_guide
testing
extending_readers
api_reference
```

## Quick Links

::::{grid} 2
:gutter: 3

:::{grid-item-card} 🚀 Quick Start
:link: overview
:link-type: doc

Get started with reading RINEX files in minutes
:::

:::{grid-item-card} 🏗️ Architecture
:link: architecture
:link-type: doc

Understand the ABC pattern and design principles
:::

:::{grid-item-card} 📖 RINEX Reader
:link: rinex_reader
:link-type: doc

Deep dive into the RINEX v3.04 reader implementation
:::

:::{grid-item-card} 🔧 Extending
:link: extending_readers
:link-type: doc

Add support for new data formats
:::

::::

## What is canvod-readers?

`canvod-readers` is a Python package for reading and parsing GNSS (Global Navigation Satellite System) data files into standardized `xarray.Dataset` structures. It's the first component in the canVODpy ecosystem for analyzing vegetation optical depth (VOD) from GNSS signal-to-noise ratio (SNR) data.

### Key Features

- **📡 RINEX v3.04 Support**: Complete implementation of RINEX v3 observation file format
- **🎯 Signal ID System**: Unique identifiers for each GNSS signal (format: `SV|BAND|CODE`)
- **📊 xarray Integration**: Native conversion to xarray Datasets for downstream analysis
- **✅ Automatic Validation**: Built-in header parsing and epoch completeness checking
- **💾 Memory Efficient**: Lazy iteration through large observation files
- **🔍 Flexible Filtering**: Filter by GNSS system, frequency band, or code type
- **🧩 Extensible**: Abstract base class pattern for adding new formats

### The canVODpy Ecosystem

```{mermaid}
graph LR
    A[RINEX Files] --> B[canvod-readers]
    B --> C[canvod-vod]
    C --> D[canvod-store]
    D --> E[canvod-grids]
    
    style B fill:#e1f5ff
```

**canvod-readers** sits at the foundation of the canVODpy pipeline:

1. **canvod-readers** (this package): Parse RINEX → xarray.Dataset
2. **canvod-vod**: Calculate vegetation optical depth from SNR
3. **canvod-store**: Store data in Icechunk format
4. **canvod-grids**: Project data onto hemisphere grids

## Installation

::::{tab-set}

:::{tab-item} uv (Recommended)
```bash
uv pip install canvod-readers
```
:::

:::{tab-item} pip
```bash
pip install canvod-readers
```
:::

:::{tab-item} Development
```bash
git clone https://github.com/nfb2021/canvodpy.git
cd canvodpy/packages/canvod-readers
uv sync
```
:::

::::

## Quick Example

```python
from pathlib import Path
from canvod.readers import Rnxv3Obs

# Load RINEX observation file
reader = Rnxv3Obs(fpath=Path("station_data.24o"))

# Convert to xarray Dataset
ds = reader.to_ds(keep_rnx_data_vars=["SNR", "Phase"])

# Inspect structure
print(ds)
# <xarray.Dataset>
# Dimensions:      (epoch: 2880, sid: 156)
# Coordinates:
#   * epoch        (epoch) datetime64[ns] 2024-01-01T00:00:00 ...
#   * sid          (sid) object 'G01|L1|C' 'G01|L2|P' ...
#     sv           (sid) object 'G01' 'G01' 'G02' ...
#     system       (sid) object 'G' 'G' 'G' ...
#     band         (sid) object 'L1' 'L2' 'L1' ...
#     code         (sid) object 'C' 'P' 'C' ...
#     freq_center  (sid) float64 1.575e+03 1.228e+03 ...
# Data variables:
#     SNR          (epoch, sid) float32 ...
#     Phase        (epoch, sid) float64 ...

# Filter GPS L1 C/A signals
gps_l1_ca = ds.where(
    (ds.system == 'G') & 
    (ds.band == 'L1') & 
    (ds.code == 'C'),
    drop=True
)
```

## Core Concepts

### Signal IDs

Every GNSS observation is assigned a unique **Signal ID** in the format:

```
SV|BAND|CODE
```

**Examples:**
- `G01|L1|C` - GPS satellite 1, L1 band, C/A code
- `E05|E5a|Q` - Galileo satellite 5, E5a band, Q channel
- `R12|G1|C` - GLONASS satellite 12, G1 band, C code

This standardization enables consistent filtering and analysis across all GNSS constellations.

### Dataset Structure

All readers produce xarray Datasets with this standardized structure:

**Dimensions:**
- `epoch`: Time of observation (datetime64[ns])
- `sid`: Signal ID (object/string)

**Coordinates:**
- `sv`: Space vehicle identifier (e.g., "G01", "E05")
- `system`: GNSS system code ('G', 'R', 'E', 'C', 'J', 'I', 'S')
- `band`: Frequency band (e.g., "L1", "E5a", "B2b")
- `code`: Observation code (e.g., "C", "P", "Q")
- `freq_center`: Center frequency (MHz)
- `freq_min`, `freq_max`: Band edges (MHz)

**Data Variables:**
- `SNR`: Signal-to-Noise Ratio (dB)
- `Phase`: Carrier phase (cycles)
- `Pseudorange`: Code pseudorange (meters)
- `Doppler`: Doppler shift (Hz)

This structure ensures compatibility with downstream canVOD processing.

## License

Apache License 2.0 - See LICENSE file for details.

## Citation

If you use canvod-readers in your research, please cite:

```bibtex
@software{canvodpy2025,
  author = {Nicolás Fabián Beber},
  title = {canVODpy: GNSS-based Vegetation Optical Depth Analysis},
  year = {2025},
  publisher = {TU Wien},
  url = {https://github.com/nfb2021/canvodpy}
}
```

## Support

- 📧 Email: [your.email@tuwien.ac.at]
- 🐛 Issues: [GitHub Issues](https://github.com/nfb2021/canvodpy/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/nfb2021/canvodpy/discussions)
