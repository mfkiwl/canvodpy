# Verified API Design - Based on Actual Implementation

## Current Processing Pipeline (from diagnostics script)

```python
# What actually happens now:
site = GnssResearchSite(site_name="Rosalia")
orchestrator = PipelineOrchestrator(site=site, dry_run=False)

for date_key, datasets, receiver_times in orchestrator.process_by_date(
    keep_vars=KEEP_RNX_VARS, start_from=start_from, end_at=end_at
):
    # datasets = {
    #     'canopy_01': xr.Dataset,    # Has: epoch, sid, C1C, L1C, phi, theta, r
    #     'canopy_02': xr.Dataset,
    #     'reference_01': xr.Dataset,
    # }
    
    # Each Dataset contains:
    # - RINEX observations (SNR, phase, pseudorange)
    # - Spherical coordinates (phi, theta, r) 
    # - Already augmented with satellite positions
    # - Stored in Icechunk
```

## Actual Processing Steps (from RinexDataProcessor)

1. **Download auxiliary data** (ephemeris, clocks) - ONCE per day
2. **Preprocess with Hermite splines** → save to temp Zarr - ONCE per day  
3. **For each receiver:**
   - Read RINEX files (parallel)
   - Extract receiver position from first file
   - Match with preprocessed aux data
   - Compute spherical coordinates (θ, φ, r)
   - Append to Icechunk store
   - Return combined daily dataset

## The Gap: RINEX → VOD

**Current workflow STOPS at processed RINEX observations.**

VOD calculation needs:
1. Load processed observations from store
2. Create hemisphere grid
3. Assign observations to grid cells
4. Aggregate multiple obs per cell (mean/median)
5. Calculate VOD (canopy vs reference)

## Proposed Modular API

### Level 1: Raw Processing (What orchestrator does)

```python
from canvodpy.processing import (
    download_auxiliary_data,
    preprocess_ephemeris,
    process_rinex_file,
    compute_spherical_coords,
)

# Step 1: Get auxiliary data
aux_data = download_auxiliary_data(date="2025001", agency="COD")

# Step 2: Preprocess with Hermite interpolation
aux_preprocessed = preprocess_ephemeris(aux_data, sampling_rate=30)

# Step 3: Process RINEX
observations = process_rinex_file(
    "data/canopy.rnx",
    aux_data=aux_preprocessed,
    keep_vars=["C1C", "L1C", "S1C"],
)

# Step 4: Compute spherical coordinates
observations = compute_spherical_coords(
    observations,
    receiver_position=(x, y, z),  # ECEF
)
```

### Level 2: Grid Processing (Missing from current code)

```python
from canvodpy.grids import (
    create_hemisphere_grid,
    assign_to_grid,
    aggregate_cells,
)

# Step 5: Create grid
grid = create_hemisphere_grid(
    resolution=5.0,
    grid_type="equal_area",
)

# Step 6: Assign observations to grid cells
canopy_gridded = assign_to_grid(
    canopy_observations,
    grid,
    method="nearest",  # or "interpolate"
)

reference_gridded = assign_to_grid(
    reference_observations,
    grid,
    method="nearest",
)

# Step 7: Aggregate multiple observations per cell
canopy_agg = aggregate_cells(
    canopy_gridded,
    statistic="mean",  # or "median", "max"
)

reference_agg = aggregate_cells(
    reference_gridded,
    statistic="mean",
)
```

### Level 3: VOD Calculation (Missing from current code)

```python
from canvodpy.vod import calculate_vod

# Step 8: Calculate VOD
vod = calculate_vod(
    canopy=canopy_agg,
    reference=reference_agg,
    grid=grid,
    method="tau_omega",  # or "direct_snr"
)

# vod is xr.Dataset with:
# - cell_id (grid cells)
# - vod (vegetation optical depth)
# - tau, omega (model parameters)
# - n_obs_canopy, n_obs_reference (counts)
```

## Factory Pattern Integration

```python
# Register custom components
from canvodpy import ReaderFactory, GridFactory, VODCalculatorFactory

# Built-in components (already registered)
ReaderFactory.register("rinex_v3", Rnxv3Obs)
GridFactory.register("equal_area", EqualAreaGrid)
VODCalculatorFactory.register("tau_omega", TauOmegaVOD)

# User adds their own
class MyCustomGrid:
    def assign_points(self, theta, phi):
        # Custom grid assignment logic
        ...

GridFactory.register("my_grid", MyCustomGrid)

# Now use it
grid = create_hemisphere_grid(resolution=5.0, grid_type="my_grid")
```

## Functional API (Airflow-Compatible)

```python
# Each function is standalone (perfect for Airflow tasks)
from canvodpy import (
    process_rinex,           # RINEX → xr.Dataset with coords
    create_grid,             # Grid object
    assign_to_grid,          # Dataset → Gridded Dataset
    aggregate_cells,         # Gridded → Aggregated
    calculate_vod,           # Canopy + Reference → VOD
)

# Airflow DAG
@task
def process_rinex_task(file_path: str):
    return process_rinex(file_path, date="2025001")

@task
def create_grid_task():
    return create_grid(resolution=5.0, grid_type="equal_area")

@task
def assign_task(obs, grid):
    return assign_to_grid(obs, grid, method="nearest")

@task  
def aggregate_task(gridded):
    return aggregate_cells(gridded, statistic="mean")

@task
def calculate_vod_task(canopy_agg, ref_agg, grid):
    return calculate_vod(canopy_agg, ref_agg, grid, method="tau_omega")
```

## Pipeline Wrapper (Convenience)

```python
from canvodpy import VODPipeline

# High-level wrapper
pipeline = VODPipeline(
    reader="rinex_v3",
    grid="equal_area",
    vod_calculator="tau_omega",
)

# Processes everything
vod = pipeline.process(
    canopy_file="data/canopy.rnx",
    reference_file="data/reference.rnx",
    date="2025001",
    resolution=5.0,
)
```

## Key Architecture Decisions

1. **Functional API** - Pure functions, composable, Airflow-ready
2. **Factory Pattern** - Users can register custom components
3. **Protocol-based** - Type-safe interfaces (RinexReader, Grid, VODCalculator)
4. **Pipeline wrapper** - Optional convenience for simple scripts
5. **Explicit steps** - Every transformation visible

## What's Missing in Current Code

1. **Grid assignment functions** - Assign obs to grid cells
2. **Aggregation functions** - Combine multiple obs per cell
3. **VOD calculation** - Tau-omega model implementation
4. **Factory classes** - Component registration system
5. **Protocols** - Type interfaces for custom components

## Implementation Priority

### Phase 1: Complete the pipeline (what's missing)
```python
# canvodpy/grids/operations.py
def assign_observations_to_grid(obs: xr.Dataset, grid: GridData) -> xr.Dataset:
    """Assign observations to nearest grid cell."""
    ...

def aggregate_gridded_observations(gridded: xr.Dataset, statistic: str) -> xr.Dataset:
    """Aggregate multiple observations per cell."""
    ...
```

### Phase 2: VOD calculation
```python
# canvodpy/vod/calculators.py
class TauOmegaVOD:
    def calculate(self, canopy: xr.Dataset, reference: xr.Dataset) -> xr.Dataset:
        """Calculate VOD using tau-omega model."""
        ...
```

### Phase 3: Factory pattern
```python
# canvodpy/factories.py
class ReaderFactory:
    _readers = {}
    
    @classmethod
    def register(cls, name: str, reader_class):
        cls._readers[name] = reader_class
    
    @classmethod
    def create(cls, name: str, **kwargs):
        return cls._readers[name](**kwargs)
```

### Phase 4: Functional API
```python
# canvodpy/api.py
def process_rinex(file_path, date, reader_type="rinex_v3", **kwargs):
    reader = ReaderFactory.create(reader_type)
    return reader.process(file_path, date, **kwargs)

def create_grid(resolution, grid_type="equal_area", **kwargs):
    grid_class = GridFactory.create(grid_type)
    return grid_class(resolution=resolution, **kwargs)

def calculate_vod(canopy, reference, method="tau_omega", **kwargs):
    calculator = VODCalculatorFactory.create(method)
    return calculator.calculate(canopy, reference, **kwargs)
```

### Phase 5: Pipeline wrapper
```python
# canvodpy/pipeline.py
class VODPipeline:
    def __init__(self, reader="rinex_v3", grid="equal_area", vod_calculator="tau_omega"):
        self.reader = reader
        self.grid = grid
        self.calculator = vod_calculator
    
    def process(self, canopy_file, reference_file, date, resolution):
        # Calls functional API internally
        canopy = process_rinex(canopy_file, date, reader_type=self.reader)
        reference = process_rinex(reference_file, date, reader_type=self.reader)
        grid = create_grid(resolution, grid_type=self.grid)
        canopy_gridded = assign_to_grid(canopy, grid)
        reference_gridded = assign_to_grid(reference, grid)
        return calculate_vod(canopy_gridded, reference_gridded, method=self.calculator)
```

## Questions for User

1. **Grid assignment**: Already exists in `canvod.grids.operations.add_cell_ids_to_ds_fast()`?
2. **Aggregation**: Already exists or needs implementation?
3. **VOD calculation**: Where is tau-omega model currently implemented?
4. **Should we expose the full orchestrator** or just the functional pieces?
5. **Icechunk storage**: Do users need to interact with stores directly or hide it?
