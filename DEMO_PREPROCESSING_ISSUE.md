# Demo Notebook Issue - Missing Preprocessing Step

## Problem

The demo tries to use `DatasetMatcher` directly on raw SP3/CLK data:

```python
matched = matcher.match_datasets(
    daily_rinex,
    ephemerides=sp3_data,  # ❌ Raw SP3 has dims: (epoch, sv)
    clock=clk_data          # ❌ Raw CLK has dims: (epoch, sv)
)
```

But `DatasetMatcher` expects datasets with RINEX structure:
- **Required dimensions**: (epoch, sid)  
- **Raw aux data has**: (epoch, sv)

## The Missing Step: Aux Data Preprocessing

The gnssvodpy pipeline does this in `_preprocess_aux_data_with_hermite()`:

1. **Read first RINEX** to detect sampling rate
2. **Generate 24-hour epoch grid** aligned with RINEX sampling
3. **Interpolate ephemerides** using Hermite splines with velocities
4. **Interpolate clock** using piecewise linear
5. **Expand to (epoch, sid)** dimensions matching RINEX
6. **Write to Zarr** for efficient slicing

## Solution for Demo

The demo has two options:

### Option 1: Manual Preprocessing (Simple for Demo)

```python
# After loading SP3/CLK, preprocess to match RINEX structure

# 1. Select aux data for RINEX epochs
aux_epochs = daily_rinex.epoch.values
sp3_interp = sp3_data.interp(epoch=aux_epochs, method='linear')
clk_interp = clk_data.interp(epoch=aux_epochs, method='linear')

# 2. Broadcast from (epoch, sv) to (epoch, sid) 
# Map sv to sid based on RINEX sids
rinex_svs = daily_rinex.sv.values
rinex_sids = daily_rinex.sid.values

# Create mapping sv -> sid list
sv_to_sids = {}
for sid in rinex_sids:
    sv = sid[:3]  # e.g., "G01" from "G01C1C"
    if sv not in sv_to_sids:
        sv_to_sids[sv] = []
    sv_to_sids[sv].append(sid)

# Expand sp3/clk from sv dimension to sid dimension
# For each SV, replicate data across all its SIDs
sp3_expanded = []
clk_expanded = []

for sv in rinex_svs:
    if sv in sv_to_sids:
        sids = sv_to_sids[sv]
        sv_data_sp3 = sp3_interp.sel(sv=sv)
        sv_data_clk = clk_interp.sel(sv=sv)
        
        for sid in sids:
            sp3_expanded.append(sv_data_sp3.assign_coords(sid=sid))
            clk_expanded.append(sv_data_clk.assign_coords(sid=sid))

sp3_matched = xr.concat(sp3_expanded, dim='sid')
clk_matched = xr.concat(clk_expanded, dim='sid')

# Now they have (epoch, sid) dimensions!
```

### Option 2: Use Interpolation Pipeline (More Accurate)

```python
from canvod.aux.interpolation import (
    Sp3InterpolationStrategy,
    ClockInterpolationStrategy,
    Sp3Config,
    ClockConfig
)

# 1. Interpolate ephemerides using Hermite splines
sp3_config = Sp3Config(use_velocities=True, fallback_method='linear')
sp3_interp_strategy = Sp3InterpolationStrategy(config=sp3_config)
sp3_interp = sp3_interp_strategy.interpolate(sp3_data, daily_rinex.epoch.values)

# 2. Interpolate clock using piecewise linear
clk_config = ClockConfig(window_size=9, jump_threshold=1e-6)
clk_interp_strategy = ClockInterpolationStrategy(config=clk_config)
clk_interp = clk_interp_strategy.interpolate(clk_data, daily_rinex.epoch.values)

# 3. Expand to sid dimension (same as Option 1)
# ... broadcast sv -> sid mapping
```

## What DatasetMatcher Actually Does

`DatasetMatcher` expects **already-preprocessed** aux datasets:
- Interpolated to RINEX epoch grid
- Expanded to (epoch, sid) dimensions
- Ready for direct coordinate computation

The matcher just does **epoch/sid alignment**, not interpolation!

## Recommended Fix for Demo

Add a preprocessing section:

```markdown
## 5. Preprocess Auxiliary Data

Match auxiliary data structure to RINEX dimensions.
```

```python
# Simple interpolation to RINEX epochs
aux_epochs = daily_rinex.epoch.values
sp3_prep = sp3_data.interp(epoch=aux_epochs, method='linear')
clk_prep = clk_data.interp(epoch=aux_epochs, method='linear')

# Expand sv -> sid (replicate SV data for each signal)
# [Implementation of sv->sid expansion]

# NOW ready for DatasetMatcher
matched = matcher.match_datasets(daily_rinex, ephemerides=sp3_prep, clock=clk_prep)
```

## Alternative: Skip DatasetMatcher Entirely

For the demo, you could bypass matching and compute coordinates directly:

```python
# Skip the matcher - compute directly from preprocessed aux
from canvod.aux.position import compute_spherical_coordinates, add_spherical_coords_to_dataset

# Get satellite positions (interpolated to RINEX epochs)
sat_x = sp3_prep['X'].values
sat_y = sp3_prep['Y'].values  
sat_z = sp3_prep['Z'].values

# Compute spherical coordinates
r, theta, phi = compute_spherical_coordinates(sat_x, sat_y, sat_z, receiver_position)

# Add to dataset
augmented_ds = add_spherical_coords_to_dataset(daily_rinex, r, theta, phi)
```

This is simpler for a demo and shows the core functionality!
