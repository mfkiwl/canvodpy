# canvodpy-examples

Real-world example data for documentation and demonstrations.

## Purpose

This repository contains **clean, real GNSS data** for:
- Documentation examples
- Interactive notebooks (marimo)
- Tutorial walkthroughs
- API demonstrations

## ⚠️ Important

**These files are for learning and demos only.**  
For test data with falsified files, see: [`canvodpy-test-data`](https://github.com/your-org/canvodpy-test-data)

---

## Structure

```
examples/
├── README.md
├── site_metadata.json         # Site locations and configs
├── rosalia/                   # Rosalia, Austria site
│   ├── 2023/
│   │   └── 001/               # Day of year 001
│   │       ├── rinex/
│   │       │   ├── canopy_20230010000.rnx      # Canopy receiver
│   │       │   └── reference_20230010000.rnx   # Reference receiver
│   │       ├── aux/
│   │       │   ├── COD0MGXFIN_20230010000_01D_05M_ORB.SP3
│   │       │   └── COD0MGXFIN_20230010000_01D_30S_CLK.CLK
│   │       └── outputs/
│   │           ├── augmented_canopy.nc
│   │           └── augmented_reference.nc
│   └── site_info.md
├── tuwien/                    # TU Wien campus site
│   └── 2024/
│       └── 150/
│           └── rinex/
└── README.md                  # This file
```

---

## Site Information

### Rosalia, Austria

**Location**: Forest research site in eastern Austria  
**Coordinates**: 47.73°N, 16.30°E, ~350m elevation  
**Period**: January 2023 onwards  
**Receivers**:
- Canopy: Below-canopy GNSS receiver
- Reference: Open-sky reference receiver

**Data Characteristics**:
- 30-second observation rate
- Multi-GNSS: GPS + GLONASS + Galileo
- Both L1/L2 signals
- Complete 24-hour datasets

**Use Cases**:
- Vegetation optical depth (VOD) analysis
- Signal attenuation studies
- Dual-receiver comparisons

### TU Wien Campus

**Location**: Technical University Vienna campus  
**Coordinates**: 48.20°N, 16.37°E, ~180m elevation  
**Period**: May 2024 onwards  
**Receivers**:
- Single receiver in urban environment

**Data Characteristics**:
- 30-second observation rate
- GPS + Galileo
- L1/L2 signals
- Urban multipath present

**Use Cases**:
- Urban GNSS analysis
- Multipath detection
- Basic RINEX processing demos

---

## File Manifest

### Rosalia 2023-001 (Complete Example)

| File | Size | Purpose |
|------|------|---------|
| `rosalia/2023/001/rinex/canopy_20230010000.rnx` | ~50MB | Canopy observations |
| `rosalia/2023/001/rinex/reference_20230010000.rnx` | ~50MB | Reference observations |
| `rosalia/2023/001/aux/COD0MGXFIN_*.SP3` | ~10MB | CODE final ephemeris |
| `rosalia/2023/001/aux/COD0MGXFIN_*.CLK` | ~5MB | CODE final clocks |
| `rosalia/2023/001/outputs/augmented_*.nc` | ~100MB | Processed outputs |

### Site Metadata

```json
{
  "sites": {
    "rosalia": {
      "name": "Rosalia Forest Site",
      "country": "Austria",
      "location": {
        "lat": 47.73,
        "lon": 16.30,
        "elevation": 350.0
      },
      "receivers": {
        "canopy": {
          "type": "canopy",
          "position_ecef": {
            "x": 4194304.678,
            "y": 1162205.267,
            "z": 4647245.201
          }
        },
        "reference": {
          "type": "reference",
          "position_ecef": {
            "x": 4194354.123,
            "y": 1162180.456,
            "z": 4647290.789
          }
        }
      }
    }
  }
}
```

---

## Usage in Documentation

### Notebook Example

```python
from pathlib import Path
from canvod.readers import Rnxv3Obs

# Path to example data
EXAMPLES = Path("/path/to/examples")

# Load Rosalia canopy data
rinex_file = EXAMPLES / "rosalia/2023/001/rinex/canopy_20230010000.rnx"
obs = Rnxv3Obs(fpath=rinex_file)
ds = obs.to_ds()

print(f"Loaded {len(ds.epoch)} observations")
```

### Pipeline Demo

```python
from canvod.aux import Sp3File, ClkFile

# Load auxiliary data
sp3 = Sp3File.from_file(
    EXAMPLES / "rosalia/2023/001/aux/COD0MGXFIN_20230010000_01D_05M_ORB.SP3"
)
clk = ClkFile.from_file(
    EXAMPLES / "rosalia/2023/001/aux/COD0MGXFIN_20230010000_01D_30S_CLK.CLK"
)

# Augment RINEX with auxiliary data
# ... (see complete_pipeline.py notebook)
```

---

## Downloading Examples

### Via Git Submodule (Recommended)

```bash
# In main canvodpy repository
cd /path/to/canvodpy
git submodule add https://github.com/your-org/canvodpy-examples.git examples

# Clone with examples
git clone --recurse-submodules https://github.com/your-org/canvodpy.git

# Update examples
cd canvodpy
git submodule update --remote examples
```

### Direct Clone

```bash
git clone https://github.com/your-org/canvodpy-examples.git
cd canvodpy-examples
```

### Git LFS

Large files are tracked with Git LFS:

```bash
# Install Git LFS
brew install git-lfs  # macOS
# or: sudo apt install git-lfs  # Linux

# Initialize
git lfs install

# Pull LFS files
git lfs pull
```

---

## Adding New Examples

When contributing new example data:

1. **Organize by site and date**
   ```
   examples/
   └── new_site/
       └── YYYY/
           └── DDD/
               ├── rinex/
               └── aux/
   ```

2. **Update site_metadata.json**
   - Add site information
   - Include receiver positions
   - Document data characteristics

3. **Create site_info.md**
   - Describe the site
   - Explain data collection setup
   - Note any special considerations

4. **Keep file sizes reasonable**
   - Single-day datasets preferred
   - Consider compression
   - Use Git LFS for large files

5. **Submit PR**
   - Descriptive commit message
   - Update this README
   - Tag with data characteristics

---

## Data Quality

All example data should:
- ✅ Be from real observations (no synthetic data)
- ✅ Have complete metadata
- ✅ Include auxiliary files (SP3, CLK)
- ✅ Pass validation checks
- ✅ Be documented with site information

---

## License

MIT (same as canvodpy main repository)

**Data Attribution**: Data collected by TU Wien Department of Geodesy and Geoinformation.
