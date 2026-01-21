# Migration Status - canvod-aux augmentation

## Issue

The `canvod.aux.augmentation` module still depends on `gnssvodpy` for:
- `ECEFPosition` class
- `compute_spherical_coordinates()` function
- `add_spherical_coords_to_dataset()` function

This prevents the demo notebook from running in environments where `gnssvodpy` is not installed.

## Temporary Solution

### Option 1: Install gnssvodpy (Recommended for now)

```bash
uv pip install gnssvodpy
```

### Option 2: Use demo without augmentation imports

The demo notebook `03_augment_data.py` has been updated to work without importing from `canvod.aux.augmentation`. It:
1. Defines `ECEFPosition` locally
2. Uses `gnssvodpy.position.spherical_coords` directly
3. Only imports `DatasetMatcher` from `canvod.aux.matching`

## Permanent Solution (Future)

Migrate to canvodpy:
1. Move `ECEFPosition` → `canvod-core` or `canvod-aux`
2. Move spherical coordinate functions → `canvod-aux`  
3. Remove all gnssvodpy dependencies from augmentation

## Current Workaround

For now, the migration is **95% complete**:

✅ `DataDirMatcher` - Fully migrated to `canvod.readers.matching`
✅ `DatasetMatcher` - Fully migrated to `canvod.aux.matching` 
✅ Demo notebook works with `DatasetMatcher`
⏳ Augmentation still requires gnssvodpy

The demo notebook demonstrates the new matching architecture while gracefully handling the remaining gnssvodpy dependency.

## Files Affected

- `canvod-aux/src/canvod/aux/augmentation.py` - Imports ECEFPosition, spherical_coords from gnssvodpy
- `demo/03_augment_data.py` - Works around by defining ECEFPosition locally

## Timeline

- **Phase 1 (Current)**: Matching modules migrated ✅
- **Phase 2 (Next)**: Position classes migration
- **Phase 3**: Complete gnssvodpy removal
