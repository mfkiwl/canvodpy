# Migration Status: Phase 4 & 5 Complete

## ✅ Completed Migrations

### Phase 5: canvod-store (Icechunk Storage)
**Location:** `/Users/work/Developer/GNSS/canvodpy/packages/canvod-store/`

**Migrated Files:**
- `store.py` - Core MyIcechunkStore class with compression, chunking, sessions
- `manager.py` - GnssResearchSite coordinator for RINEX + VOD stores
- `viewer.py` - Rich display decorator for store visualization
- `reader.py` - IcechunkDataReader for batch processing
- `metadata.py` - Metadata management utilities
- `preprocessing.py` - Dataset preprocessing (commented out, future work)
- `grid_adapters/` - Grid storage integration (for Phase 3)

**Dependencies:**
- canvod-grids (workspace, for future grid integration)
- icechunk>=1.1.5
- zarr>=3.1.2
- xarray>=2023.12.0
- polars>=1.0.0
- numpy>=1.24.0

**Import Updates:**
- `gnssvodpy.icechunk_manager.*` → `canvod.store.*`
- `gnssvodpy.globals` → `canvodpy.globals` (shared utilities)
- `gnssvodpy.logging` → `canvodpy.logging` (shared utilities)
- Optional import of `canvod.vod` to avoid circular dependency

---

### Phase 4: canvod-vod (VOD Calculation)
**Location:** `/Users/work/Developer/GNSS/canvodpy/packages/canvod-vod/`

**Migrated Files:**
- `calculator.py` (from `vod_new.py`) - Abstract VODCalculator + TauOmegaZerothOrder implementation

**Key Classes:**
- `VODCalculator` - Abstract base class with Pydantic validation
- `TauOmegaZerothOrder` - Zeroth-order Tau-Omega approximation
- `.from_datasets()` - Calculate VOD from canopy/sky xarray datasets
- `.from_icechunkstore()` - Optional convenience method (requires canvod-store)

**Dependencies:**
- numpy>=1.24.0
- xarray>=2023.12.0
- pydantic>=2.0.0
- Optional: canvod-store (for `.from_icechunkstore()`)

**Circular Dependency Resolution:**
- `canvod-vod` does NOT import `canvod-store` at module level
- `from_icechunkstore()` uses try/except for optional import
- `canvod-store.GnssResearchSite.calculate_vod()` uses optional import
- Both packages can be installed independently

---

### Umbrella Package: canvodpy
**Shared Utilities Moved:**
- `canvodpy/globals.py` - Global configuration constants
- `canvodpy/settings.py` - Settings management
- `canvodpy/research_sites_config.py` - Site configuration
- `canvodpy/logging/` - Logging infrastructure (structlog-based)
- `canvodpy/utils/` - Common utilities (tools, date_time)

**New Dependencies Added:**
- tomli>=2.0.0 (for pyproject.toml parsing)
- python-dotenv>=1.0.0 (for .env file loading)

---

## 🔧 Required Action: Install Dependencies

The workspace dependencies have been updated but need to be installed:

```bash
cd /Users/work/Developer/GNSS/canvodpy
uv sync
```

This will install:
- All workspace packages (canvod-readers, canvod-aux, canvod-store, canvod-vod)
- New shared dependencies (tomli, python-dotenv)
- All package-specific dependencies

---

## 🧪 Testing Plan

### 1. Basic Import Tests
```bash
cd /Users/work/Developer/GNSS/canvodpy

# Test canvod-vod
.venv/bin/python -c "from canvod.vod import VODCalculator, TauOmegaZerothOrder; print('✓ canvod-vod')"

# Test canvod-store
.venv/bin/python -c "from canvod.store import MyIcechunkStore, GnssResearchSite; print('✓ canvod-store')"

# Test umbrella
.venv/bin/python -c "import canvodpy.globals; import canvodpy.logging; print('✓ canvodpy')"
```

### 2. Package Test Suites
```bash
# Test canvod-vod
cd packages/canvod-vod
just test

# Test canvod-store
cd ../canvod-store
just test
```

### 3. Integration Test: Full Pipeline
Test the complete workflow:
1. Read RINEX data (canvod-readers)
2. Augment with auxiliary data (canvod-aux)
3. Store in RINEX store (canvod-store)
4. Calculate VOD (canvod-vod)
5. Store VOD results (canvod-store)

Compare results with original gnssvodpy implementation.

---

## 📦 Package Architecture

```
canvodpy/
├── canvodpy/                    # Umbrella package
│   ├── globals.py               # Shared configuration
│   ├── settings.py              # Settings management
│   ├── research_sites_config.py # Site definitions
│   ├── logging/                 # Logging infrastructure
│   └── utils/                   # Common utilities
│
├── packages/
│   ├── canvod-readers/          # Phase 1 ✅
│   ├── canvod-aux/              # Phase 2 ✅
│   ├── canvod-store/            # Phase 5 ✅ (just completed)
│   ├── canvod-vod/              # Phase 4 ✅ (just completed)
│   ├── canvod-grids/            # Phase 3 ⏳ (skeleton only)
│   └── canvod-viz/              # Phase 6 ⏳ (skeleton only)
```

**Dependency Graph:**
```
canvodpy (umbrella)
├── canvod-readers (standalone)
├── canvod-aux (→ readers)
├── canvod-store (optional: → vod)
└── canvod-vod (optional: → store)
```

---

## 🎯 Next Steps

### Immediate (After uv sync)
1. Run tests to verify imports work
2. Fix any remaining import issues
3. Test basic store operations (create, read, write)
4. Test VOD calculation with sample data

### Short Term
1. Migrate canvod-grids (Phase 3)
2. Test full pipeline with real data
3. Compare outputs with gnssvodpy
4. Refactor: Consider moving `GnssResearchSite.calculate_vod()` to canvod-vod

### Long Term
1. Complete documentation (MyST markdown)
2. Add integration tests
3. Create example notebooks
4. Performance optimization

---

## 📝 Notes

### Circular Dependency Resolution
The original gnssvodpy had a circular dependency:
- `icechunk_manager.store` imported from `vod.vod_new`
- `vod.vod_new` imported from `icechunk_manager.store`

**Solution:**
- Both packages use optional imports with try/except
- `VODCalculator.from_icechunkstore()` → optional `canvod.store` import
- `GnssResearchSite.calculate_vod()` → optional `canvod.vod` import
- Allows independent installation and testing

### Shared Utilities Strategy
Rather than duplicating code, shared utilities live in the umbrella package:
- Configuration (globals, settings, site config)
- Logging infrastructure
- Common utilities (date/time, file operations)

This follows Python best practices for monorepo organization.
