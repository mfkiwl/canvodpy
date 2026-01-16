# canvodpy-examples

Public example datasets and tutorials for canvodpy ecosystem.

## 📊 Datasets

### Available Sites

#### 1. Rosalia, Austria
**Location:** 47.85°N, 16.29°E  
**Environment:** Mixed forest-grassland transition zone  
**Period:** Summer 2023 (DOY 180-220)  
**Setup:** Canopy receiver + reference receiver  
**Sampling:** 30-second epochs  

**Data includes:**
- 40 days of continuous RINEX observations
- Multi-GNSS (GPS+GLONASS+Galileo)
- Pre-downloaded auxiliary data (CODE final products)
- Site metadata (receiver positions, antenna info)

**Use cases:**
- Basic VOD pipeline tutorial
- Seasonal vegetation analysis
- Multi-GNSS processing

#### 2. Vienna Urban (Coming Soon)
**Location:** 48.21°N, 16.37°E  
**Environment:** Urban park with mixed vegetation  
**Period:** Q1 2024  

#### 3. Alpine Forest (Coming Soon)
**Location:** TBD  
**Environment:** Dense coniferous forest  

---

## 📁 Dataset Structure

Each dataset follows this structure:

```
dataset_name/
├── README.md              # Site-specific documentation
├── metadata.json          # Machine-readable metadata
├── rinex/
│   ├── canopy/
│   │   ├── YYYDDD_canopy.rnx
│   │   └── ...
│   └── reference/
│       ├── YYYDDD_reference.rnx
│       └── ...
├── aux/                   # Pre-downloaded auxiliary files
│   ├── ephemeris/
│   │   ├── COD0MGXFIN_*.SP3
│   │   └── ...
│   └── clock/
│       ├── COD0MGXFIN_*.CLK
│       └── ...
└── site_config.toml       # Configuration for canvodpy
```

---

## 📓 Notebooks

Interactive tutorials using marimo:

### Basic Tutorials
1. **`01_basic_workflow.py`** - Complete pipeline from RINEX to VOD
2. **`02_data_quality.py`** - Observation quality analysis
3. **`03_auxiliary_data.py`** - Working with SP3/CLK files

### Advanced Tutorials
4. **`04_multi_site.py`** - Processing multiple sites
5. **`05_seasonal_analysis.py`** - Time series analysis
6. **`06_custom_algorithms.py`** - Extending canvodpy

---

## 🚀 Quick Start

### Clone Repository

```bash
# Clone examples repository
git clone https://github.com/your-org/canvodpy-examples.git
cd canvodpy-examples
```

### Download Dataset (Git LFS)

```bash
# Install Git LFS if not already installed
git lfs install

# Pull LFS files
git lfs pull
```

### Run Notebooks

```bash
# Install canvodpy
pip install canvodpy

# Run a tutorial
marimo edit notebooks/01_basic_workflow.py
```

---

## 📦 Dataset Details

### Rosalia Summer 2023

**File Inventory:**
- RINEX files: 80 files (40 canopy + 40 reference)
- SP3 files: 40 files
- CLK files: 40 files
- Total size: ~2.5 GB (compressed with Git LFS)

**Data Quality:**
- Observation completeness: >95%
- Multi-path: Low (open environment)
- Signal strength: Strong (C/N0 > 45 dB-Hz)

**Receiver Configuration:**
```toml
[site]
name = "Rosalia"
latitude = 47.85
longitude = 16.29
elevation = 350.0

[receivers.canopy]
position = [4194304.678, 1162205.267, 4647245.201]  # ECEF (m)
antenna = "TRM59800.00"
type = "below-canopy"

[receivers.reference]
position = [4194354.123, 1162215.456, 4647255.789]  # ECEF (m)
antenna = "TRM59800.00"
type = "open-sky"
```

**Expected Results:**
- VOD range: 0.2 - 0.8 (dimensionless)
- Typical diurnal variation: ±0.05
- Correlation with leaf area index: r > 0.85

---

## 📝 Using Examples in Your Research

### Citation

If you use these datasets in your research, please cite:

```bibtex
@dataset{canvodpy_examples_2025,
  author = {Bader, Nicolas F. and TU Wien GEO},
  title = {canvodpy Example Datasets},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/your-org/canvodpy-examples}
}
```

### Data License

Example datasets are provided under **CC BY 4.0** license.  
You are free to:
- Share and adapt the data
- Use for commercial purposes
- With appropriate attribution

### Code License

Notebooks and scripts are under **MIT License** (same as canvodpy).

---

## 🤝 Contributing

### Adding New Datasets

We welcome contributions of additional example datasets! To contribute:

1. **Prepare your data:**
   - Follow the standard directory structure
   - Include comprehensive README
   - Add site_config.toml
   - Ensure data quality

2. **Documentation requirements:**
   - Site description and coordinates
   - Data collection period
   - Receiver configuration
   - Known data quality issues
   - Expected analysis results

3. **Submit:**
   - Create issue describing dataset
   - Fork repository
   - Add your dataset
   - Submit pull request

### Dataset Criteria

To maintain quality, contributed datasets should:
- ✅ Be scientifically valid and properly collected
- ✅ Include metadata and configuration
- ✅ Cover at least 7 days of observations
- ✅ Include corresponding auxiliary data
- ✅ Have documented expected results
- ✅ Be properly anonymized (if needed)
- ✅ Not exceed 10 GB (use compression)

---

## 📊 Pre-computed Results

For validation and comparison, we provide pre-computed results:

```bash
results/
├── rosalia_2023_summer_vod.nc     # VOD time series
├── rosalia_2023_summer_grid.nc    # Gridded results
└── processing_log.json             # Processing parameters
```

Use these to verify your pipeline produces consistent results.

---

## 🔗 Links

- **Main Repository:** https://github.com/your-org/canvodpy
- **Documentation:** https://canvodpy.readthedocs.io
- **Issue Tracker:** https://github.com/your-org/canvodpy-examples/issues

---

## 📧 Contact

Questions about datasets?  
Open an issue or contact: climers@geo.tuwien.ac.at

---

## 🗂️ Version History

### v0.1.0 (2025-01-16)
- Initial release
- Rosalia Summer 2023 dataset
- 6 tutorial notebooks

### Planned
- v0.2.0: Vienna Urban dataset
- v0.3.0: Alpine Forest dataset
- v0.4.0: Multi-year Rosalia data
