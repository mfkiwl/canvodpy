# New Simple API Design for Canvodpy
## For 95% of Users: Scientists Writing Plain Python Scripts

---

## Goal
Make VOD calculation **simple, explicit, and understandable** for scientists who:
- Write plain Python scripts locally
- Want to see every step clearly
- Need to inspect/modify data between steps
- Don't know/need Airflow, marimo, or web APIs

---

## Proposed API

### Import (Simple and Clear)
```python
from canvodpy import (
    Site,              # Represents a research site
    load_observations, # Load GNSS observations for a date
    create_grid,       # Create hemisphere grid
    calculate_vod,     # Calculate VOD from observations + grid
    save_vod,          # Save VOD results
    plot_hemisphere,   # Quick visualization (optional)
)
```

### Basic Workflow (5 Steps - Clear & Explicit)
```python
# =================================================================
# STEP 1: Setup site
# =================================================================
site = Site("Rosalia")
print(f"Site: {site.name}")
print(f"Receivers: {list(site.receivers.keys())}")

# =================================================================
# STEP 2: Load observations for one date
# =================================================================
observations = load_observations(
    site=site,
    date="2025001",  # YYYYDOY format
    min_elevation=5.0,  # degrees - filter low elevations
    max_gap=300,        # seconds - max gap in observation arcs
)
print(f"Loaded {len(observations)} observations")

# =================================================================
# STEP 3: Create hemisphere grid
# =================================================================
grid = create_grid(
    resolution=5.0,       # degrees - cell size
    method="equal_area",  # or "regular"
)
print(f"Grid has {grid.ncells} cells")

# =================================================================
# STEP 4: Calculate VOD
# =================================================================
vod = calculate_vod(
    observations=observations,
    grid=grid,
    canopy_receiver="canopy_01",
    reference_receiver="reference_01",
    aggregation="mean",  # how to combine multiple obs per cell
)
print(f"VOD mean: {vod.vod.mean():.3f} dB")

# =================================================================
# STEP 5: Save results
# =================================================================
save_vod(vod, "output/rosalia_2025001.zarr")
print("✓ Results saved!")

# =================================================================
# OPTIONAL: Quick visualization
# =================================================================
fig = plot_hemisphere(vod)
fig.write_html("rosalia_2025001.html")
```

---

## Multiple Dates (Just a Loop!)
```python
from canvodpy import Site, load_observations, create_grid, calculate_vod, save_vod
from pathlib import Path

# Configuration
SITE = "Rosalia"
DATES = ["2025001", "2025002", "2025003"]
OUTPUT = Path("output/batch")
OUTPUT.mkdir(exist_ok=True)

# Setup (once)
site = Site(SITE)
grid = create_grid(resolution=5.0)

# Process each date
for date in DATES:
    print(f"\nProcessing {date}...")
    
    try:
        # Load → Calculate → Save
        obs = load_observations(site, date, min_elevation=5)
        vod = calculate_vod(obs, grid, "canopy_01", "reference_01")
        save_vod(vod, OUTPUT / f"{date}.zarr")
        
        print(f"  ✓ Mean VOD: {vod.vod.mean():.3f} dB")
        
    except Exception as e:
        print(f"  ✗ Failed: {e}")

print("\n✓ All dates processed!")
```

---

## Multiple Sites (Nested Loops!)
```python
from canvodpy import Site, load_observations, create_grid, calculate_vod, save_vod
from pathlib import Path

# Configuration
SITES = ["Rosalia", "Tonasket", "Pullman"]
DATES = ["2025001", "2025002"]
OUTPUT = Path("output/multi_site")

# Shared grid
grid = create_grid(resolution=5.0)

# Process all sites × dates
for site_name in SITES:
    print(f"\n{'='*60}")
    print(f"Site: {site_name}")
    print(f"{'='*60}")
    
    site = Site(site_name)
    site_output = OUTPUT / site_name
    site_output.mkdir(parents=True, exist_ok=True)
    
    for date in DATES:
        print(f"  {date}...", end=" ")
        try:
            obs = load_observations(site, date, min_elevation=5)
            vod = calculate_vod(obs, grid, "canopy_01", "reference_01")
            save_vod(vod, site_output / f"{date}.zarr")
            print(f"✓ {vod.vod.mean():.3f} dB")
        except Exception as e:
            print(f"✗ {e}")

print("\n✓ All sites processed!")
```

---

## Implementation Details

### Module: `canvodpy/simple_api.py`

```python
"""Simple, explicit API for VOD calculation.

Designed for scientists writing plain Python scripts locally.
Every step is clear and inspectable.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
import pandas as pd
import xarray as xr

if TYPE_CHECKING:
    from pathlib import Path
    from canvod.grids import GridData

# Re-export Site from existing API
from canvodpy.api import Site

def load_observations(
    site: Site,
    date: str,
    *,
    min_elevation: float = 5.0,
    max_gap: int = 300,
    keep_variables: list[str] | None = None,
) -> pd.DataFrame:
    """Load GNSS observations for one date.
    
    This function:
    1. Loads RINEX files for all active receivers
    2. Processes observations (filtering, augmentation)
    3. Converts to hemisphere coordinates (theta, phi)
    4. Returns combined DataFrame ready for grid assignment
    
    Parameters
    ----------
    site : Site
        Research site with receiver configuration
    date : str
        Date in YYYYDOY format (e.g., "2025001" = Jan 1, 2025)
    min_elevation : float, default 5.0
        Minimum satellite elevation angle in degrees.
        Observations below this are filtered out.
    max_gap : int, default 300
        Maximum gap in seconds before splitting observation arcs.
    keep_variables : list[str] | None
        RINEX variables to keep (default: SNR, phase, pseudorange)
        
    Returns
    -------
    pd.DataFrame
        Combined observations from all receivers with columns:
        - receiver_id : str - Receiver name (e.g., "canopy_01")
        - timestamp : datetime - Observation time (UTC)
        - sat_id : str - Satellite ID (e.g., "G01", "R08")
        - theta : float - Zenith angle in radians [0, π/2]
        - phi : float - Azimuth in radians [0, 2π)
        - snr : float - Signal-to-noise ratio in dB-Hz
        - elevation : float - Satellite elevation in radians
        - azimuth : float - Satellite azimuth in radians
        
    Examples
    --------
    Load one day:
    
    >>> site = Site("Rosalia")
    >>> obs = load_observations(site, "2025001")
    >>> len(obs)
    45231
    >>> obs['receiver_id'].unique()
    array(['canopy_01', 'canopy_02', 'reference_01'])
    
    With custom filtering:
    
    >>> obs = load_observations(
    ...     site,
    ...     "2025001",
    ...     min_elevation=10.0,  # Stricter elevation cutoff
    ...     max_gap=600,          # Longer arcs allowed
    ... )
    
    Inspect data:
    
    >>> print(f"Receivers: {obs['receiver_id'].nunique()}")
    >>> print(f"Satellites: {obs['sat_id'].nunique()}")
    >>> print(f"Time range: {obs['timestamp'].min()} to {obs['timestamp'].max()}")
    >>> print(f"Mean SNR: {obs['snr'].mean():.1f} dB-Hz")
    
    Notes
    -----
    - RINEX files are downloaded automatically if not cached locally
    - Satellite ephemeris and clock corrections are applied automatically
    - Multipath and ionospheric corrections are NOT applied (raw SNR)
    - Processing typically takes 30-60 seconds per date
    
    See Also
    --------
    create_grid : Create hemisphere grid for VOD calculation
    calculate_vod : Calculate VOD from observations and grid
    """
    # Implementation wraps existing pipeline
    pass


def create_grid(
    resolution: float = 5.0,
    method: str = "equal_area",
) -> GridData:
    """Create hemisphere grid for binning observations.
    
    Parameters
    ----------
    resolution : float, default 5.0
        Angular resolution in degrees. Determines grid cell size.
        Typical values: 2-10 degrees (smaller = more cells, finer detail)
    method : str, default "equal_area"
        Grid generation method:
        - "equal_area": Cells have equal solid angle (recommended)
        - "regular": Regular lat-lon grid (simpler, unequal areas)
        
    Returns
    -------
    GridData
        Grid object containing:
        - ncells : int - Number of cells
        - theta : array - Zenith angles of cell centers [0, π/2]
        - phi : array - Azimuth angles of cell centers [0, 2π)
        - solid_angle : array - Solid angle of each cell (steradians)
        - vertices : arrays - Cell boundary vertices
        
    Examples
    --------
    Standard grid:
    
    >>> grid = create_grid(resolution=5.0)
    >>> grid.ncells
    324
    
    Higher resolution:
    
    >>> fine_grid = create_grid(resolution=2.0)
    >>> fine_grid.ncells
    2025
    
    Regular lat-lon grid:
    
    >>> reg_grid = create_grid(resolution=5.0, method="regular")
    >>> reg_grid.ncells
    360
    
    Inspect grid:
    
    >>> print(f"Cells: {grid.ncells}")
    >>> print(f"Mean solid angle: {grid.solid_angle.mean():.6f} sr")
    >>> print(f"Theta range: [{grid.theta.min():.2f}, {grid.theta.max():.2f}] rad")
    
    Notes
    -----
    - Equal-area grids are recommended for accurate VOD calculation
    - Grids are cached and reused across processing runs
    - Resolution must divide 360 evenly for equal-area grids
    - Processing time: < 1 second for typical resolutions
    
    See Also
    --------
    load_observations : Load observations to assign to grid
    calculate_vod : Calculate VOD using grid
    """
    pass


def calculate_vod(
    observations: pd.DataFrame,
    grid: GridData,
    canopy_receiver: str,
    reference_receiver: str,
    *,
    aggregation: str = "mean",
) -> xr.Dataset:
    """Calculate VOD from observations and grid.
    
    This function:
    1. Assigns observations to grid cells (nearest neighbor)
    2. Aggregates multiple observations per cell
    3. Separates canopy and reference observations
    4. Calculates VOD using the tau-omega model
    5. Returns xarray Dataset with results
    
    Parameters
    ----------
    observations : pd.DataFrame
        Combined observations from all receivers (from load_observations)
    grid : GridData
        Hemisphere grid (from create_grid)
    canopy_receiver : str
        Name of canopy receiver (e.g., "canopy_01")
    reference_receiver : str
        Name of reference receiver (e.g., "reference_01")
    aggregation : str, default "mean"
        Method for combining multiple observations per cell:
        - "mean": Average SNR (recommended)
        - "median": Median SNR (robust to outliers)
        - "max": Maximum SNR per cell
        
    Returns
    -------
    xr.Dataset
        VOD results with variables:
        - vod : array - Vegetation optical depth in dB
        - tau : array - Optical depth (τ)
        - omega : array - Single scattering albedo (ω)
        - cell_id : coord - Grid cell identifier
        - theta : coord - Zenith angle of cell center
        - phi : coord - Azimuth angle of cell center
        - n_obs_canopy : int - Number of canopy observations per cell
        - n_obs_reference : int - Number of reference observations per cell
        
    Examples
    --------
    Basic usage:
    
    >>> site = Site("Rosalia")
    >>> obs = load_observations(site, "2025001")
    >>> grid = create_grid(resolution=5.0)
    >>> vod = calculate_vod(obs, grid, "canopy_01", "reference_01")
    >>> vod.vod.mean()
    0.42
    
    With median aggregation:
    
    >>> vod = calculate_vod(
    ...     obs, grid,
    ...     "canopy_01", "reference_01",
    ...     aggregation="median"
    ... )
    
    Inspect results:
    
    >>> print(f"Mean VOD: {vod.vod.mean():.3f} dB")
    >>> print(f"VOD range: [{vod.vod.min():.3f}, {vod.vod.max():.3f}] dB")
    >>> print(f"Cells with data: {vod.vod.notnull().sum()}")
    >>> print(f"Total observations: {vod.n_obs_canopy.sum()}")
    
    Access specific cells:
    
    >>> vod.sel(cell_id=42)
    >>> vod.where(vod.vod > 0.5)  # High VOD cells
    
    Notes
    -----
    - Cells with < 10 observations are marked as NaN
    - VOD is calculated as difference in SNR between reference and canopy
    - Negative VOD values may occur due to measurement noise
    - Processing time: 10-30 seconds depending on observation count
    
    See Also
    --------
    load_observations : Load observations for VOD calculation
    save_vod : Save VOD results to file
    plot_hemisphere : Visualize VOD on hemisphere
    """
    pass


def save_vod(
    vod: xr.Dataset,
    path: str | Path,
) -> None:
    """Save VOD results to Zarr format.
    
    Parameters
    ----------
    vod : xr.Dataset
        VOD results from calculate_vod()
    path : str or Path
        Output path (should end in .zarr)
        
    Examples
    --------
    >>> vod = calculate_vod(obs, grid, "canopy_01", "reference_01")
    >>> save_vod(vod, "output/rosalia_2025001.zarr")
    
    Load back later:
    
    >>> import xarray as xr
    >>> vod = xr.open_zarr("output/rosalia_2025001.zarr")
    
    Notes
    -----
    - Zarr format allows efficient partial loading of large datasets
    - Metadata (site, date, receivers) is preserved automatically
    """
    pass


def plot_hemisphere(
    vod: xr.Dataset,
    variable: str = "vod",
) -> "plotly.graph_objects.Figure":
    """Create quick hemisphere visualization of VOD.
    
    Parameters
    ----------
    vod : xr.Dataset
        VOD results
    variable : str, default "vod"
        Variable to plot ("vod", "tau", "omega", "n_obs_canopy")
        
    Returns
    -------
    plotly.graph_objects.Figure
        Interactive plot
        
    Examples
    --------
    >>> fig = plot_hemisphere(vod)
    >>> fig.write_html("vod_map.html")
    >>> fig.show()  # In Jupyter
    """
    pass
```

---

## New `__init__.py`

```python
"""canvodpy: Simple GNSS VOD Analysis

Quick Start
-----------
>>> from canvodpy import Site, load_observations, create_grid, calculate_vod
>>> 
>>> site = Site("Rosalia")
>>> obs = load_observations(site, "2025001")
>>> grid = create_grid(resolution=5.0)
>>> vod = calculate_vod(obs, grid, "canopy_01", "reference_01")
"""

# Simple API (95% of users)
from canvodpy.simple_api import (
    Site,
    load_observations,
    create_grid,
    calculate_vod,
    save_vod,
    plot_hemisphere,
)

# Advanced: Re-export subpackages
from canvodpy.api import Pipeline  # For advanced workflows

__version__ = "0.2.0"

__all__ = [
    # Simple API (recommended)
    "Site",
    "load_observations",
    "create_grid",
    "calculate_vod",
    "save_vod",
    "plot_hemisphere",
    # Advanced
    "Pipeline",
    # Version
    "__version__",
]
```

---

## Implementation Plan

### Phase 1: Core Functions (Priority)
1. ✅ `Site` - Already exists, just re-export
2. 🔨 `load_observations()` - Wrap existing pipeline.process_date()
3. 🔨 `create_grid()` - Wrap canvod.grids.create_hemigrid()
4. 🔨 `calculate_vod()` - Wrap existing VOD calculation
5. 🔨 `save_vod()` - Wrap existing store.save()

### Phase 2: Examples
1. `examples/basic_workflow.py` - Single date
2. `examples/batch_processing.py` - Multiple dates
3. `examples/multi_site.py` - Multiple sites
4. `examples/custom_analysis.py` - Advanced customization

### Phase 3: Documentation
1. Update README with new simple API
2. Add "Quick Start" guide
3. Add "Cookbook" with common patterns
4. Update package docstring

### Phase 4: Visualization (Optional)
1. `plot_hemisphere()` - Quick 2D plot
2. `plot_timeseries()` - VOD over time
3. `plot_coverage()` - Observation coverage map

---

## Benefits

✅ **Explicit** - Every step is clear and visible
✅ **Simple** - Just 5 functions for 95% of use cases
✅ **Understandable** - Scientists can read and modify easily
✅ **Inspectable** - Can print/plot data at any step
✅ **Debuggable** - Easy to find where things break
✅ **Composable** - Functions work independently
✅ **No frameworks** - Just plain Python loops
✅ **Good defaults** - Works out of the box
✅ **Rich docs** - Examples in every docstring
✅ **Type hints** - IDE autocomplete helps users

---

## Questions for User

1. **Function names**: `load_observations()` or `load_data()`?
2. **Grid method**: Should we expose "equal_area" vs "regular" or hide it?
3. **Aggregation**: Default to "mean" or make it required?
4. **Error handling**: Return None on error or raise exceptions?
5. **Progress bars**: Show progress during long operations?
6. **Caching**: Auto-cache RINEX files or require explicit download?

---

## Next Steps

**Ready to implement?**

I can start with Phase 1 (core functions) and create working examples.
This will give you a clean, simple API that 95% of users will love!
