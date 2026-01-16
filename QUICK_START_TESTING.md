# Quick Start: Testing the Pipeline

## Prerequisites

1. **RINEX Test Data** (Create test directory):
```bash
mkdir -p ~/GNSS/test_data/rinex
# Copy some RINEX files there
```

2. **Environment Setup**:
```bash
cd /Users/work/Developer/GNSS/canvodpy
uv sync
```

3. **(Optional) NASA CDDIS Access**:
```bash
# Set in .env or export
export CDDIS_MAIL=your.email@example.com
```

---

## Test 1: Read RINEX File

```bash
cd /Users/work/Developer/GNSS/canvodpy
uv run python << 'EOF'
from pathlib import Path
from canvod.readers import Rnxv3Obs

# Point to your RINEX file
rinex_file = Path.home() / "GNSS" / "test_data" / "rinex" / "example.rnx"

if rinex_file.exists():
    obs = Rnxv3Obs(fpath=rinex_file)
    ds = obs.to_ds()
    print(f"✅ RINEX loaded: {dict(ds.dims)}")
    print(f"   Variables: {list(ds.data_vars)[:5]}...")
else:
    print(f"❌ File not found: {rinex_file}")
EOF
```

---

## Test 2: Download Auxiliary Data

```bash
cd /Users/work/Developer/GNSS/canvodpy
uv run python << 'EOF'
import datetime
from pathlib import Path
from canvod.aux.ephemeris.reader import Sp3File
from canvod.aux.clock.reader import ClkFile
from canvod.aux.core.downloader import FtpDownloader
import os

# Setup
date = datetime.date(2023, 9, 11)
aux_dir = Path("/tmp/canvod_aux_test")
aux_dir.mkdir(exist_ok=True)

# Create downloader
user_email = os.environ.get("CDDIS_MAIL")
downloader = FtpDownloader(user_email=user_email)

print("📥 Downloading SP3 ephemeris...")
sp3 = Sp3File.from_datetime_date(
    date=date,
    agency="COD",
    product_type="final",
    ftp_server="ftp://ftp.aiub.unibe.ch",
    local_dir=aux_dir,
    downloader=downloader,
)
print(f"✅ SP3: {sp3.fpath.name}")

print("\n📥 Downloading CLK clock...")
clk = ClkFile.from_datetime_date(
    date=date,
    agency="COD",
    product_type="final",
    ftp_server="ftp://ftp.aiub.unibe.ch",
    local_dir=aux_dir,
    downloader=downloader,
)
print(f"✅ CLK: {clk.fpath.name}")

# Verify data can be loaded
print(f"\n📊 SP3 dataset: {dict(sp3.data.dims)}")
print(f"📊 CLK dataset: {dict(clk.data.dims)}")
EOF
```

---

## Test 3: Complete Pipeline (Non-Interactive)

```bash
cd /Users/work/Developer/GNSS/canvodpy
uv run python << 'EOF'
import datetime
from pathlib import Path
from canvod.readers import Rnxv3Obs
from canvod.aux.ephemeris.reader import Sp3File
from canvod.aux.clock.reader import ClkFile
from canvod.aux.core.downloader import FtpDownloader
from canvod.aux.augmentation import AuxDataAugmenter, AugmentationContext
from gnssvodpy.position.position import ECEFPosition
import os

print("=" * 60)
print("COMPLETE PIPELINE TEST")
print("=" * 60)

# 1. Setup
rinex_file = Path.home() / "GNSS" / "test_data" / "rinex" / "example.rnx"
aux_dir = Path("/tmp/canvod_aux_test")
aux_dir.mkdir(exist_ok=True)

# 2. Read RINEX
print("\n1️⃣  Reading RINEX...")
obs = Rnxv3Obs(fpath=rinex_file)
rinex_ds = obs.to_ds()
print(f"   ✅ {dict(rinex_ds.dims)}")

# 3. Download Auxiliary
print("\n2️⃣  Downloading Auxiliary Data...")
date = datetime.date(2023, 9, 11)
user_email = os.environ.get("CDDIS_MAIL")
downloader = FtpDownloader(user_email=user_email)

sp3 = Sp3File.from_datetime_date(
    date=date, agency="COD", product_type="final",
    ftp_server="ftp://ftp.aiub.unibe.ch",
    local_dir=aux_dir, downloader=downloader,
)
print(f"   ✅ SP3: {sp3.fpath.name}")

clk = ClkFile.from_datetime_date(
    date=date, agency="COD", product_type="final",
    ftp_server="ftp://ftp.aiub.unibe.ch",
    local_dir=aux_dir, downloader=downloader,
)
print(f"   ✅ CLK: {clk.fpath.name}")

# 4. Augment
print("\n3️⃣  Augmenting RINEX...")
receiver_pos = ECEFPosition(
    x=4194304.678,
    y=1162205.267,
    z=4647245.201
)

context = AugmentationContext(
    receiver_position=receiver_pos,
    receiver_type="test",
    matched_datasets={
        'ephemeris': sp3.data,
        'clock': clk.data
    }
)

augmenter = AuxDataAugmenter()
augmented_ds = augmenter.augment(rinex_ds, context)

new_vars = set(augmented_ds.data_vars) - set(rinex_ds.data_vars)
print(f"   ✅ Added {len(new_vars)} variables:")
for var in sorted(new_vars):
    print(f"      - {var}")

# 5. Save
print("\n4️⃣  Saving Results...")
output_file = Path("/tmp/augmented_rinex.nc")
augmented_ds.to_netcdf(output_file)
print(f"   ✅ Saved: {output_file}")
print(f"   📦 Size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")

print("\n" + "=" * 60)
print("✅ PIPELINE TEST COMPLETE!")
print("=" * 60)
EOF
```

---

## Test 4: Interactive Demo (Marimo)

```bash
cd /Users/work/Developer/GNSS/canvodpy/canvodpy
uv run marimo edit docs/notebooks/complete_pipeline.py
```

**In the notebook:**
1. Enter your RINEX directory path
2. Select a file
3. Click "Read RINEX File"
4. Select agency (COD, GFZ, ESA)
5. Click "Download Auxiliary Data"
6. Enter receiver ECEF coordinates
7. Click "Augment Data"
8. Explore visualizations
9. Save results

---

## Troubleshooting

### Issue: RINEX file not found
**Solution:** 
```bash
# Check your path
ls ~/GNSS/test_data/rinex/

# Or create test directory
mkdir -p ~/GNSS/test_data/rinex
# Copy RINEX files there
```

### Issue: Download fails
**Solution:**
```bash
# Check internet connection
ping gssc.esa.int

# Try different server
export CDDIS_MAIL=your.email@example.com

# Check FTP access
ftp ftp.aiub.unibe.ch
# (should connect without auth)
```

### Issue: Import errors
**Solution:**
```bash
# Reinstall dependencies
cd /Users/work/Developer/GNSS/canvodpy
uv sync --reinstall

# Verify installation
uv run python -c "from canvod.readers import Rnxv3Obs; print('✅')"
uv run python -c "from canvod.aux import Sp3File; print('✅')"
```

### Issue: Augmentation fails
**Check:**
1. RINEX has valid epoch data
2. Auxiliary data covers same date
3. Receiver position is reasonable (ECEF meters)
4. gnssvodpy is installed (temporary dependency)

---

## Verification Commands

```bash
# Check package installations
uv run python -c "import canvod.readers; print('readers:', canvod.readers.__version__)"
uv run python -c "import canvod.aux; print('aux:', canvod.aux.__version__)"

# Check test data exists
ls -lh ~/GNSS/test_data/rinex/

# Check aux downloads
ls -lh /tmp/canvod_aux_test/

# Run package tests
cd packages/canvod-readers && just test
cd packages/canvod-aux && just test
```

---

## Success Criteria

✅ **Pipeline Working When:**
- RINEX file loads → xarray Dataset with observations
- SP3 downloads → satellite positions available
- CLK downloads → clock corrections available
- Augmentation adds → spherical coordinates, corrections
- Output saved → NetCDF file with all data

---

## Next Steps After Verification

1. **Test with your data:** Replace example paths with real RINEX
2. **Batch processing:** Loop over multiple files
3. **VOD calculation:** Use `canvod-vod` (when migrated)
4. **Grid analysis:** Apply spatial aggregation
5. **Visualization:** Create plots and maps

---

## Getting Help

- **Documentation:** https://canvodpy.readthedocs.io
- **Issues:** https://github.com/your-org/canvodpy/issues
- **Migration Guide:** `CANVODPY_MIGRATION_GUIDE.md`
