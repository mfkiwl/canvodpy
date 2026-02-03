# Grid Storage and Loading

This guide explains how to store and load grids in canvodpy using Icechunk stores.

## Overview

Grids can be stored to the Icechunk store and loaded later for reuse. This ensures consistency across processing runs and avoids recreating grids each time.

## Quick Start

### 1. Store a Grid

```python
from canvod.grids import create_hemigrid, store_grid

# Create grid
grid = create_hemigrid(angular_resolution=4, grid_type='equal_area')

# Store to Icechunk
snapshot_id = store_grid(grid, store, 'equal_area_4deg')
```

### 2. Load a Grid

```python
from canvod.grids import load_grid

# Load from Icechunk
grid = load_grid(store, 'equal_area_4deg')
```

### 3. Use for Processing

```python
from canvod.grids import add_cell_ids_to_ds_fast
import xarray as xr

# Load VOD data
with store.readonly_session() as session:
    vod_ds = xr.open_zarr(session.store, group='reference_01_canopy_01')

# Add cell assignments using loaded grid
vod_ds = add_cell_ids_to_ds_fast(vod_ds, grid, 'equal_area_4deg')

# Now vod_ds has cell_id_equal_area_4deg variable
```

## Complete Workflow Example

```python
from pathlib import Path
from canvod.grids import (
    create_hemigrid, store_grid, load_grid, add_cell_ids_to_ds_fast
)
import xarray as xr

# Setup
store_path = Path("/path/to/your/icechunk/store")
store = MyIcechunkStore(store_path)

# Step 1: Create and store multiple grids
grid_configs = [
    {"type": "equal_area", "resolution": 2},
    {"type": "equal_area", "resolution": 4},
    {"type": "htm", "resolution": 4},
]

for config in grid_configs:
    grid = create_hemigrid(
        angular_resolution=config["resolution"],
        grid_type=config["type"],
    )
    grid_name = f"{config['type']}_{int(config['resolution'])}deg"
    store_grid(grid, store, grid_name)

# Step 2: Load VOD data
with store.readonly_session() as session:
    vod_ds = xr.open_zarr(
        session.store,
        group="reference_01_canopy_01",
        consolidated=False,
    )

# Step 3: Load grids and add cell assignments
for config in grid_configs:
    grid_name = f"{config['type']}_{int(config['resolution'])}deg"
    grid = load_grid(store, grid_name)
    vod_ds = add_cell_ids_to_ds_fast(vod_ds, grid, grid_name)

# Step 4: Aggregate per cell
import polars as pl
import numpy as np

grid = load_grid(store, "equal_area_2deg")
cell_ids = vod_ds["cell_id_equal_area_2deg"].values.ravel()
vod_values = vod_ds["VOD"].values.ravel()

valid = np.isfinite(cell_ids) & np.isfinite(vod_values)
df = pl.DataFrame({
    "cell_id": cell_ids[valid].astype(int),
    "vod": vod_values[valid]
})

stats = df.group_by("cell_id").agg(pl.col("vod").mean().alias("vod_mean"))
```

## Store Structure

After storing grids, your Icechunk store will have this structure:

```
store/
├── reference_01_canopy_01/          # VOD data groups
│   ├── VOD                          # Original VOD variable
│   ├── cell_id_equal_area_2deg      # Cell assignments
│   ├── cell_id_equal_area_4deg
│   └── cell_id_htm_4deg
├── grids/
│   ├── equal_area_2deg/             # Grid definitions (xarray)
│   │   ├── cell_phi
│   │   ├── cell_theta
│   │   ├── vertices_phi
│   │   ├── vertices_theta
│   │   ├── n_vertices
│   │   └── solid_angle
│   ├── equal_area_4deg/
│   └── htm_4deg/
```

## API Reference

### `store_grid(grid, store, grid_name)`

Store a grid to Icechunk store.

**Parameters:**
- `grid`: GridData instance
- `store`: Icechunk store instance
- `grid_name`: Grid identifier (e.g., 'equal_area_4deg')

**Returns:** Snapshot ID (str)

### `load_grid(store, grid_name)`

Load a grid from Icechunk store.

**Parameters:**
- `store`: Icechunk store instance
- `grid_name`: Grid identifier

**Returns:** GridData instance

### `grid_to_dataset(grid)`

Convert grid to xarray Dataset (used internally by `store_grid`).

**Parameters:**
- `grid`: GridData instance

**Returns:** xarray.Dataset with grid structure

## Benefits

1. **Consistency**: Same grid used across multiple datasets
2. **Performance**: No need to recreate grids each run
3. **Persistence**: Grid definitions saved with your data
4. **Reproducibility**: Exact grid structure preserved

## Implementation Details

Grids are stored as xarray Datasets containing:
- `cell_phi`, `cell_theta`: Cell centers
- `vertices_phi`, `vertices_theta`: Vertex positions (NaN-padded)
- `n_vertices`: Number of vertices per cell
- `solid_angle`: Solid angle per cell
- Attributes: `grid_type`, `angular_resolution`, `cutoff_theta`

The `load_grid()` function reconstructs the GridData object from this
stored information.
