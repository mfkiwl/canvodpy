---
title: canVODpy
description: An Open Python Ecosystem for GNSS-Transmissometry Canopy VOD Retrievals
---

<div class="hero" markdown>

# canVODpy

**An Open Python Ecosystem for GNSS-Transmissometry Canopy VOD Retrievals**

canVODpy aims to be the central community-driven software suite for deriving and
analyzing canopy Vegetation Optical Depth (VOD) from GNSS signal-to-noise ratio observations.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18636775.svg)](https://doi.org/10.5281/zenodo.18636775)
[![PyPI](https://img.shields.io/pypi/v/canvodpy)](https://pypi.org/project/canvodpy/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

[Get started](guides/getting-started.md){ .md-button .md-button--primary }
[View on GitHub](https://github.com/nfb2021/canvodpy){ .md-button }

</div>

---

## Processing Pipeline

```mermaid
flowchart TD
    subgraph INPUT["Data Acquisition"]
        RINEX["RINEX v3.04 Observation Files (SNR, Pseudorange, Phase)"]
        SP3["SP3 Precise Ephemerides (satellite orbits)"]
        CLK["CLK Precise Clock Corrections"]
    end

    subgraph DOWNLOAD["Auxiliary Data Retrieval"]
        FTP["FTP Download (ESA primary, NASA CDDIS fallback)"]
        CACHE["Local File Cache (SP3/CLK per DOY)"]
    end

    subgraph PREPROCESS["Auxiliary Preprocessing"]
        PARSE_SP3["Parse SP3 (ECEF satellite positions + velocities)"]
        PARSE_CLK["Parse CLK (satellite clock offsets)"]
        HERMITE["Hermite Spline Interpolation (cubic, velocity-aware)"]
        LINEAR["Piecewise Linear Interpolation (clock corrections)"]
        MERGE_AUX["Merge Interpolated Auxiliary Data (Zarr cache)"]
    end

    subgraph PARALLEL["Parallel RINEX Processing (ProcessPoolExecutor)"]
        READ["Read RINEX (per hourly file)"]
        SID["Signal ID Mapping (sv|band|code)"]
        SLICE["Slice Auxiliary to Observation Epochs (nearest-neighbour)"]
        SCS["Spherical Coordinate Transformation (ECEF to r, theta, phi)"]
    end

    subgraph STORAGE["Versioned Storage"]
        ICECHUNK["Icechunk Repository (append per epoch, commit per file)"]
        META["Metadata Tracking (RINEX hash, snapshot ID, epoch range)"]
    end

    subgraph GRIDDING["Hemispheric Grid Assignment"]
        GRID["Grid Construction (equal-area, HEALPix, geodesic, ...)"]
        KDTREE["KDTree Cell Assignment (O(n log m) spatial query)"]
    end

    subgraph VOD["VOD Retrieval"]
        PAIR["Canopy-Reference Dataset Pairing"]
        TAU["Zeroth-Order Tau-Omega Inversion"]
        FORMULA["DELTA_SNR = SNR_canopy - SNR_ref transmissivity = 10^(DELTA_SNR/10) VOD = -ln(transmissivity) * cos(theta)"]
    end

    subgraph OUTPUT["Output"]
        VOD_DS["VOD Dataset (per sid, epoch, cell)"]
        VIZ["Hemispheric Visualization (polar projection)"]
    end

    SP3 --> FTP
    CLK --> FTP
    FTP --> CACHE
    CACHE --> PARSE_SP3
    CACHE --> PARSE_CLK
    PARSE_SP3 --> HERMITE
    PARSE_CLK --> LINEAR
    HERMITE --> MERGE_AUX
    LINEAR --> MERGE_AUX

    RINEX --> READ
    READ --> SID
    MERGE_AUX --> SLICE
    SID --> SLICE
    SLICE --> SCS
    SCS --> ICECHUNK
    ICECHUNK --> META

    ICECHUNK --> GRID
    GRID --> KDTREE
    KDTREE --> PAIR
    PAIR --> TAU
    TAU --> FORMULA
    FORMULA --> VOD_DS
    VOD_DS --> VIZ
```

## Packages

| Package | Description |
|---------|-------------|
| **canvod-readers** | RINEX v3.04 observation file parsing with validation |
| **canvod-auxiliary** | SP3 ephemeris and CLK clock correction processing |
| **canvod-grids** | Hemispheric grid implementations (HEALPix, equal-area) |
| **canvod-vod** | VOD estimation using the tau-omega model |
| **canvod-store** | Versioned storage via Icechunk |
| **canvod-viz** | 2D and 3D hemispheric visualization |
| **canvod-utils** | Configuration management and CLI |
| **canvodpy** | Umbrella package providing unified access |

## Quick Start

```bash
pip install canvodpy
```

### Level 1 — Convenience (two lines)

```python
from canvodpy import process_date, calculate_vod

data = process_date("Rosalia", "2025001")
vod  = calculate_vod("Rosalia", "canopy_01", "reference_01", "2025001")
```

### Level 2 — Fluent workflow (deferred execution)

```python
import canvodpy

result = (canvodpy.workflow("Rosalia")
    .read("2025001")
    .preprocess()
    .grid("equal_area", angular_resolution=5.0)
    .vod("canopy_01", "reference_01")
    .result())
```

### Level 3 — VODWorkflow (eager, with logging)

```python
from canvodpy import VODWorkflow

wf  = VODWorkflow(site="Rosalia", grid="equal_area")
vod = wf.calculate_vod("canopy_01", "reference_01", "2025001")
```

### Level 4 — Functional (stateless, Airflow-ready)

```python
from canvodpy import read_rinex, create_grid, assign_grid_cells

ds   = read_rinex(path, reader="rinex3")
grid = create_grid(grid_type="equal_area", angular_resolution=5.0)
ds   = assign_grid_cells(ds, grid)
```

## Technology

| | |
|---|---|
| Python 3.13+ | uv + uv_build |
| xarray + NumPy | Icechunk / Zarr |
| ruff + ty | pytest |
| Zensical | just |

## Publications

Bader, N. F. (2026). *canVODpy: An Open Python Ecosystem for GNSS-Transmissometry Canopy VOD Retrievals* (v0.1.0-beta.2).
Zenodo. [https://doi.org/10.5281/zenodo.18636775](https://doi.org/10.5281/zenodo.18636775)

## Affiliation

Climate and Environmental Remote Sensing Research Unit (CLIMERS),
Department of Geodesy and Geoinformation,
TU Wien (Vienna University of Technology).

[https://www.tuwien.at/en/mg/geo/climers](https://www.tuwien.at/en/mg/geo/climers)
