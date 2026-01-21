# Auxiliary Data Preprocessing - sv → sid Conversion

## Problem
SP3 and CLK files use satellite vehicle (sv) dimension, but RINEX uses Signal ID (sid) dimension. Interpolation must happen on sid dimension to match RINEX structure.

## Solution
Use `preprocess_aux_for_interpolation()` to convert sv → sid **BEFORE** interpolation.

## Complete Workflow

```python
from canvod.aux import (
    Sp3File,
    ClkFile,
    Sp3Config,
    ClockConfig,
    Sp3InterpolationStrategy,
    ClockInterpolationStrategy,
    preprocess_aux_for_interpolation,  # ← NEW!
    compute_spherical_coordinates,
    add_spherical_coords_to_dataset,
)

# 1. Load raw auxiliary data (sv dimension)
sp3_data = Sp3File.from_url(date, "CODE", "final").to_dataset()
clk_data = ClkFile.from_url(date, "CODE", "final").to_dataset()

print(sp3_data.dims)  # {'epoch': 96, 'sv': 32}
print(clk_data.dims)  # {'epoch': 288, 'sv': 32}

# 2. ✅ Convert sv → sid BEFORE interpolation
sp3_sid = preprocess_aux_for_interpolation(sp3_data)
clk_sid = preprocess_aux_for_interpolation(clk_data)

print(sp3_sid.dims)  # {'epoch': 96, 'sid': 384}  (~12 sids per sv)
print(clk_sid.dims)  # {'epoch': 288, 'sid': 384}

# 3. Interpolate (now works because sid dimension exists)
sp3_config = Sp3Config(use_velocities=True)
sp3_interpolator = Sp3InterpolationStrategy(config=sp3_config)
sp3_interp = sp3_interpolator.interpolate(sp3_sid, target_epochs)  # ✅ Works!

clk_config = ClockConfig(window_size=9, jump_threshold=1e-6)
clk_interpolator = ClockInterpolationStrategy(config=clk_config)
clk_interp = clk_interpolator.interpolate(clk_sid, target_epochs)  # ✅ Works!

# 4. Compute spherical coordinates
sat_x, sat_y, sat_z = sp3_interp['X'], sp3_interp['Y'], sp3_interp['Z']
r, theta, phi = compute_spherical_coordinates(sat_x, sat_y, sat_z, receiver_position)
augmented_ds = add_spherical_coords_to_dataset(rinex_ds, r, theta, phi)
```

## Why This Works

### Before (❌ BROKEN)
```python
sp3_data = Sp3File(...).to_dataset()  # {'epoch': 96, 'sv': 32}
sp3_interp = interpolator.interpolate(sp3_data, target_epochs)
# ❌ KeyError: 'sid' - interpolator expects sid dimension!
```

### After (✅ FIXED)
```python
sp3_data = Sp3File(...).to_dataset()  # {'epoch': 96, 'sv': 32}
sp3_sid = preprocess_aux_for_interpolation(sp3_data)  # {'epoch': 96, 'sid': 384}
sp3_interp = interpolator.interpolate(sp3_sid, target_epochs)  # ✅ Works!
```

## Under the Hood

`preprocess_aux_for_interpolation()` expands each satellite to all its signal IDs:

```python
# GPS satellite G01 transmits on multiple bands/codes:
"G01" → [
    "G01|L1|C",  # L1 C/A
    "G01|L1|P",  # L1 P(Y)
    "G01|L1|W",  # L1 Z-tracking
    "G01|L2|C",  # L2 C/A
    "G01|L2|L",  # L2 L2C(L)
    ...
    "G01|X1|X",  # X1 auxiliary
]

# Values are replicated across all sids for the same satellite
sp3_data['X'].sel(sv='G01') = 1234.5  # Single value
sp3_sid['X'].sel(sid='G01|L1|C') = 1234.5  # Same value
sp3_sid['X'].sel(sid='G01|L2|W') = 1234.5  # Same value
sp3_sid['X'].sel(sid='G01|X1|X') = 1234.5  # Same value
```

## Dependencies

canvod-aux now depends on canvod-readers for GNSS constellation knowledge:

```python
from canvod.readers.gnss_specs.constellations import GPS, GALILEO, GLONASS, ...
from canvod.readers.gnss_specs.signals import SignalIDMapper
from canvod.readers.gnss_specs.constants import AGGREGATE_GLONASS_FDMA
```

## Production Flow (gnssvodpy)

The gnssvodpy production pipeline does this in `_preprocess_aux_data_with_hermite()`:

```python
# 1. Get raw aux data
ephem_ds = aux_pipeline.get("ephemerides")  # sv dimension
clock_ds = aux_pipeline.get("clock")        # sv dimension

# 2. ✅ Convert sv → sid BEFORE interpolation
from gnssvodpy.icechunk_manager.preprocessing import IcechunkPreprocessor
ephem_ds = IcechunkPreprocessor.prep_aux_ds(ephem_ds)  # sid dimension
clock_ds = IcechunkPreprocessor.prep_aux_ds(clock_ds)  # sid dimension

# 3. Interpolate with Hermite splines
sp3_interp = sp3_interpolator.interpolate(ephem_ds, target_epochs)
clk_interp = clk_interpolator.interpolate(clock_ds, target_epochs)

# 4. Merge and write to Zarr
aux_processed = xr.merge([sp3_interp, clk_interp])
aux_processed.to_zarr(output_path)
```

We're following the same pattern in canvodpy!

## Testing

```bash
cd packages/canvod-aux
uv pip install -e ".[dev]"

# Test the preprocessing
python -c "
from canvod.aux import preprocess_aux_for_interpolation, Sp3File
from datetime import date

sp3_data = Sp3File.from_url(date(2024, 1, 1), 'CODE', 'final').to_dataset()
print('Before:', sp3_data.dims)

sp3_sid = preprocess_aux_for_interpolation(sp3_data)
print('After:', sp3_sid.dims)
print('Success!')
"
```

## Next Steps

1. Update demo notebook `03_augment_data.py` to use preprocessing
2. Verify interpolation works end-to-end
3. Compare results with gnssvodpy for scientific accuracy
