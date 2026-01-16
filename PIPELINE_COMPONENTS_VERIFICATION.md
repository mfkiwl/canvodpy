# Pipeline Components Verification

## Status: ✅ All Core Components Present

### 1. Data Reading (canvod-readers) ✅
**Location:** `/packages/canvod-readers/src/canvod/readers/`

**Components:**
- `rinex/v3_04.py` - RINEX v3.04 parser
- `Rnxv3Obs` class - Main observation reader
- GNSS specs and signal mapping

**Usage:**
```python
from canvod.readers import Rnxv3Obs

obs = Rnxv3Obs(fpath="example.rnx")
ds = obs.to_ds()  # Returns xarray.Dataset
```

---

### 2. Auxiliary Data (canvod-aux) ✅
**Location:** `/packages/canvod-aux/src/canvod/aux/`

**Components:**

#### a) Data Downloading
- `core/downloader.py` - FTP downloader with ESA/NASA fallback
- `products/registry.py` - 39 products across 17 agencies
- Automatic server selection and failover

#### b) File Readers
- `ephemeris/reader.py` - SP3File class for satellite positions
- `clock/reader.py` - ClkFile class for clock corrections
- Both support `from_datetime_date()` and `from_file()` methods

#### c) Interpolation
- `interpolation.py` - Hermite cubic spline for SP3
- Segment-based linear interpolation for CLK
- Velocity computation from positions

#### d) Augmentation Framework
- `augmentation.py` - Pluggable augmentation system
- `AugmentationStep` ABC for custom steps
- `SphericalCoordinateAugmentation` - Computes φ, θ, r
- `ClockCorrectionAugmentation` - Applies clock corrections

**Usage:**
```python
# Download auxiliary data
from canvod.aux.ephemeris.reader import Sp3File
from canvod.aux.clock.reader import ClkFile

sp3 = Sp3File.from_datetime_date(
    date=datetime.date(2023, 9, 11),
    agency="COD",
    product_type="final",
    ftp_server="ftp://ftp.aiub.unibe.ch",
    local_dir=Path("/data/aux"),
)

# Access data (lazy loaded)
ephemeris_ds = sp3.data

# Augment RINEX
from canvod.aux.augmentation import AuxDataAugmenter, AugmentationContext
from gnssvodpy.position.position import ECEFPosition

context = AugmentationContext(
    receiver_position=ECEFPosition(x=..., y=..., z=...),
    matched_datasets={'ephemeris': sp3.data, 'clock': clk.data}
)

augmenter = AuxDataAugmenter()
augmented_ds = augmenter.augment(rinex_ds, context)
```

---

### 3. Complete Pipeline Demo ✅
**Location:** `/canvodpy/docs/notebooks/complete_pipeline.py`

**Features:**
- Interactive marimo notebook
- Demonstrates full workflow:
  1. Configure directories
  2. Read RINEX files
  3. Download auxiliary data (SP3 + CLK)
  4. Augment with satellite positions
  5. Visualize results
  6. Save to NetCDF

**Run:**
```bash
cd canvodpy
uv run marimo edit docs/notebooks/complete_pipeline.py
```

---

## Integration Points

### From gnssvodpy (Legacy) → canvodpy (Modern)

**Already Migrated:**
- ✅ RINEX reading → `canvod-readers`
- ✅ SP3/CLK handling → `canvod-aux`
- ✅ Product registry → `canvod-aux/products`
- ✅ Interpolation strategies → `canvod-aux/interpolation`
- ✅ Augmentation framework → `canvod-aux/augmentation`

**Still in gnssvodpy (to be migrated):**
- ⏳ Position calculations → Future: `canvod-core`
- ⏳ VOD algorithms → `canvod-vod`
- ⏳ Grid systems → `canvod-grids`
- ⏳ Visualization → `canvod-viz`
- ⏳ Icechunk storage → `canvod-store`

---

## Dependencies Status

### canvod-readers ✅
```toml
dependencies = [
    "xarray>=2025.9.0",
    "numpy>=2.0",
    "pint>=0.24",
]
```

### canvod-aux ✅
```toml
dependencies = [
    "xarray>=2025.9.0",
    "numpy>=2.0",
    "scipy>=1.15.0",
    "pint>=0.24",
    "pydantic>=2.10.0",
]
```

### Umbrella (canvodpy) ⏳
Currently depends on legacy gnssvodpy for:
- `gnssvodpy.position.position.ECEFPosition`
- `gnssvodpy.position.spherical_coords`

**Resolution:** Create `canvod-core` package or inline these utilities.

---

## Testing Status

### Package Tests
- ✅ `canvod-readers/tests/` - RINEX parsing tests
- ✅ `canvod-aux/tests/` - Download, interpolation tests
- ⏳ Integration tests needed

### Test Data Requirements
For the pipeline demo notebook to work, you need:

1. **RINEX Files** in test directory:
   ```
   ~/GNSS/test_data/rinex/
   ├── example_001.rnx
   ├── example_002.rnx
   └── ...
   ```

2. **Internet Connection** for downloading:
   - SP3 ephemeris files from ESA/NASA
   - CLK clock files from ESA/NASA

3. **Receiver Position** (approximate ECEF coordinates)

---

## Next Steps

### Immediate (Today)
1. ✅ Create pipeline demo notebook
2. ⏳ Test with real RINEX data
3. ⏳ Verify augmentation output

### Short Term (This Week)
1. Extract position utilities to avoid gnssvodpy dependency
2. Add integration tests
3. Document API with examples

### Medium Term (Next Week)
1. Migrate VOD calculations → `canvod-vod`
2. Migrate grid systems → `canvod-grids`
3. Complete monorepo structure

---

## Key Achievements

### Scientific Accuracy Preserved ✅
- Clock interpolation verified identical to gnssvodpy
- Hermite spline interpolation matches legacy
- SP3 coordinate transformations validated

### Architecture Improvements ✅
- Purpose-centric organization (ephemeris/clock vs formats/sp3)
- Configuration-based product registry (17 agencies, 39 products)
- Pluggable augmentation framework
- Type-safe with Pydantic validation

### Developer Experience ✅
- Interactive demo notebooks (marimo)
- Comprehensive documentation
- Clear package boundaries
- Modern tooling (uv, ruff, just)

---

## Running the Demo

```bash
# 1. Setup environment
cd /Users/work/Developer/GNSS/canvodpy/canvodpy
uv sync

# 2. (Optional) Configure NASA CDDIS fallback
export CDDIS_MAIL=your.email@example.com

# 3. Run interactive notebook
uv run marimo edit docs/notebooks/complete_pipeline.py

# 4. In the notebook:
#    - Configure RINEX directory path
#    - Select a file to read
#    - Download auxiliary data
#    - Enter receiver position
#    - Augment and visualize
```

---

## Architecture Diagram

```
canvodpy/
├── canvod-readers/        ← Read RINEX observations
│   └── Rnxv3Obs.to_ds()  → xarray.Dataset
│
├── canvod-aux/            ← Download & interpolate aux data
│   ├── Sp3File            → Satellite positions
│   ├── ClkFile            → Clock corrections
│   ├── Interpolators      → Hermite/Linear
│   └── AuxDataAugmenter   → Combine RINEX + Aux
│       └── augment()      → xarray.Dataset (augmented)
│
├── canvod-vod/            ← VOD calculations (future)
├── canvod-grids/          ← Spatial grids (future)
├── canvod-viz/            ← Visualization (future)
└── canvodpy/              ← Umbrella package
    └── docs/notebooks/    ← Demo notebooks
```

---

## Verification Checklist

- [x] RINEX reading works
- [x] SP3 download works
- [x] CLK download works
- [x] Product registry complete (17 agencies)
- [x] Interpolation strategies implemented
- [x] Augmentation framework functional
- [x] Demo notebook created
- [ ] Tested with real data
- [ ] Integration tests passing
- [ ] Dependencies fully resolved
