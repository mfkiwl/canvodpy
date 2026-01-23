# 📊 gnssvodpy vs canvodpy - Component Comparison

**Purpose:** Detailed comparison showing migration status  
**Date:** 2025-01-21

---

## 🎯 Quick Summary

| Status | Component | gnssvodpy | canvodpy | Priority |
|--------|-----------|-----------|----------|----------|
| ✅ | RINEX Parsing | `rinexreader/` | `canvod-readers` | DONE |
| ✅ | Auxiliary Data | `aux_data/` | `canvod-aux` | DONE |
| ✅ | Grids | `hemigrid/grids/` | `canvod-grids` | DONE |
| ✅ | Visualization | `hemigrid/viz/` | `canvod-viz` | DONE |
| ❌ | Storage | `icechunk_manager/` | *missing* | **CRITICAL** |
| ❌ | VOD Calculations | `vod/` | *missing* | **CRITICAL** |
| ❌ | Site Management | `research_sites_config.py` | *missing* | **HIGH** |
| ❌ | Pipeline | `processor/` | *missing* | **HIGH** |
| ❌ | Configuration | `globals.py`, `settings.py` | *missing* | **MEDIUM** |
| ❌ | Logging | `logging/` | *missing* | **MEDIUM** |

---

## 📦 Detailed Component Mapping

### ✅ COMPLETED MIGRATIONS

#### 1. RINEX Parsing
**gnssvodpy → canvodpy**

```
gnssvodpy/rinexreader/               → canvod-readers/src/canvod/readers/
├── rinex_reader.py                  → ├── rinex_v3.py
├── rnx_header.py                    → ├── headers.py
├── rnx_observations.py              → ├── observations.py
└── rnx_validator.py                 → └── validators.py
```

**Status:** ✅ Complete (2,900 lines + tests)

---

#### 2. Auxiliary Data
**gnssvodpy → canvodpy**

```
gnssvodpy/aux_data/                  → canvod-aux/src/canvod/aux/
├── sp3.py                           → ├── ephemeris/sp3.py
├── clk.py                           → ├── clock/clk.py
├── base_aux.py                      → ├── base.py
├── pipeline.py                      → ├── pipeline.py
├── preprocessing/                   → └── preprocessing/
│   ├── clock_preprocessing.py       →     ├── clock.py
│   └── ephemeris_preprocessing.py   →     └── ephemeris.py
```

**Status:** ✅ Complete (2,500 lines + tests)

---

#### 3. Hemisphere Grids
**gnssvodpy → canvodpy**

```
gnssvodpy/hemigrid/grids/            → canvod-grids/src/canvod/grids/
├── (partial implementation)         → ├── core.py (NEW, clean implementation)
└── ...                              → └── builders/ (NEW)
```

**Status:** ✅ Complete (360 lines + tests, clean rewrite)

---

#### 4. Visualization
**gnssvodpy → canvodpy**

```
gnssvodpy/hemigrid/visualization/    → canvod-viz/src/canvod/viz/
├── visualizer.py                    → ├── visualizer.py
├── hemisphere_2d.py                 → ├── hemisphere_2d.py
├── hemisphere_3d.py                 → ├── hemisphere_3d.py
└── colorscale.py                    → └── styles.py (modernized)
```

**Status:** ✅ Complete (1,370 lines + tests)

---

### ❌ MISSING COMPONENTS (Need Migration)

#### 5. Storage Layer (CRITICAL)
**gnssvodpy → canvod-store (NEW PACKAGE)**

```
gnssvodpy/icechunk_manager/          → canvod-store/src/canvod/store/
├── store.py (880 lines)             → ├── base.py
├── manager.py (450 lines)           → ├── site.py
├── reader.py (400 lines)            → ├── reader.py
├── viewer.py (200 lines)            → ├── viewer.py
├── preprocessing.py (300 lines)     → ├── preprocessing.py
└── ...                              → └── metadata.py (NEW)
```

**Estimated:** ~500 lines (simplified) + 300 tests  
**Status:** ❌ NOT STARTED  
**Blocks:** Everything - this is the data persistence layer

**Key Classes to Migrate:**
- `MyIcechunkStore` - Core Icechunk wrapper
- `GnssResearchSite` - Site manager (receivers, stores)
- `IcechunkDataReader` - Data loading
- `StoreViewer` - Store inspection
- Helper functions: `create_rinex_store()`, `create_vod_store()`

---

#### 6. VOD Calculations (CRITICAL)
**gnssvodpy → canvod-vod (NEW PACKAGE)**

```
gnssvodpy/vod/                       → canvod-vod/src/canvod/vod/
├── vod.py (200 lines)               → ├── calculator.py
├── vod_new.py (300 lines)           → ├── models.py
└── ...                              → ├── signal.py (NEW)
                                     └── quality.py (NEW)
```

**Estimated:** ~400 lines + 250 tests  
**Status:** ❌ NOT STARTED  
**Blocks:** VOD analysis - the core algorithm

**Key Classes to Migrate:**
- `VODCalculator` - Main calculator
- `TauOmegaZerothOrder` - Tau-omega model
- Signal attenuation logic
- Quality metrics

---

#### 7. Pipeline Orchestration (HIGH)
**gnssvodpy → canvodpy (UMBRELLA)**

```
gnssvodpy/processor/                 → canvodpy/src/canvod/processor/
├── pipeline_orchestrator.py (400)   → ├── orchestrator.py
├── processor.py (600 lines)         → ├── processor.py
└── receiver_processor.py (200)      → └── receiver.py
```

**Estimated:** ~600 lines + 350 tests  
**Status:** ❌ NOT STARTED  
**Blocks:** Batch processing, automation

**Key Classes to Migrate:**
- `PipelineOrchestrator` - Coordinates processing
- `RinexDataProcessor` - RINEX → processed data
- `ReceiverProcessor` - Per-receiver logic
- `PairDataDirMatcher` - Data discovery

---

#### 8. Configuration System (HIGH)
**gnssvodpy → canvodpy (UMBRELLA)**

```
gnssvodpy/                           → canvodpy/src/canvod/
├── research_sites_config.py (150)   → ├── config/
├── globals.py (300 lines)           →     ├── sites.py
├── settings.py (100 lines)          →     ├── settings.py
└── ...                              →     └── globals.py
```

**Estimated:** ~200 lines + 100 tests  
**Status:** ❌ NOT STARTED  
**Blocks:** Site setup, user configuration

**Key Components:**
- `RESEARCH_SITES` - Site definitions
- `KEEP_RNX_VARS` - Processing configuration
- `Settings` - User settings
- Environment variable handling

---

#### 9. Data Matching/Discovery (MEDIUM)
**gnssvodpy → canvodpy (UMBRELLA)**

```
gnssvodpy/data_handler/              → canvodpy/src/canvod/data/
├── data_handler.py (300 lines)      → ├── matcher.py
└── ...                              → └── discovery.py
```

**Estimated:** ~200 lines + 100 tests  
**Status:** ❌ NOT STARTED  
**Blocks:** Data discovery for processing

**Key Classes:**
- `MatchedDirs` - Matched data directories
- `PairDataDirMatcher` - Pair matching
- `YYYYDOY` - Date handling

---

#### 10. Logging System (MEDIUM)
**gnssvodpy → canvodpy (UMBRELLA)**

```
gnssvodpy/logging/                   → canvodpy/src/canvod/logging/
├── context.py (200 lines)           → ├── context.py
├── setup.py (100 lines)             → ├── setup.py
└── ...                              → └── formatters.py
```

**Estimated:** ~150 lines + 50 tests  
**Status:** ❌ NOT STARTED  
**Blocks:** Debugging, monitoring

**Key Components:**
- Structured logging (structlog)
- Context managers
- File-specific logging
- Performance tracking

---

#### 11. Position/Coordinate Transforms (LOW)
**gnssvodpy → canvodpy (UMBRELLA)**

```
gnssvodpy/position/                  → canvodpy/src/canvod/position/
├── coordinate_systems.py (200)      → ├── transforms.py
└── ...                              → └── utils.py
```

**Estimated:** ~150 lines + 100 tests  
**Status:** ❌ NOT STARTED  
**Blocks:** Coordinate conversions

---

#### 12. Utilities (LOW)
**gnssvodpy → canvodpy (UMBRELLA)**

```
gnssvodpy/utils/                     → canvodpy/src/canvod/utils/
├── tools.py (200 lines)             → ├── tools.py
├── date_time.py (100 lines)         → ├── datetime.py
└── ...                              → └── helpers.py
```

**Estimated:** ~150 lines + 50 tests  
**Status:** ❌ NOT STARTED  

---

## 🎯 Implementation Roadmap

### Phase 1: Core Storage (Days 1-3) - CRITICAL
**Package:** canvod-store  
**Dependencies:** canvod-readers, canvod-grids  
**Effort:** 500 lines + 300 tests

1. Extract `MyIcechunkStore` from gnssvodpy
2. Create `RinexStore` and `VODStore` subclasses
3. Add metadata management
4. Implement time-based queries
5. Write comprehensive tests

**Deliverable:** Working Icechunk integration

---

### Phase 2: VOD Calculations (Days 3-5) - CRITICAL
**Package:** canvod-vod  
**Dependencies:** canvod-readers, canvod-aux  
**Effort:** 400 lines + 250 tests

1. Extract `VODCalculator` from gnssvodpy
2. Extract `TauOmegaZerothOrder` model
3. Clean up signal processing
4. Add quality metrics
5. Write comprehensive tests

**Deliverable:** Working VOD calculations

---

### Phase 3: Configuration (Days 5-6) - HIGH
**Package:** canvodpy (config module)  
**Dependencies:** None  
**Effort:** 200 lines + 100 tests

1. Design TOML-based configuration
2. Extract site definitions
3. Extract global settings
4. Add validation
5. Environment variable support

**Deliverable:** User-friendly configuration

---

### Phase 4: Site Management (Days 6-7) - HIGH
**Package:** canvodpy (site module)  
**Dependencies:** canvod-store, config  
**Effort:** 200 lines + 150 tests

1. Create `Site` class (user-facing)
2. Integrate with configuration
3. Manage stores
4. Receiver management
5. VOD analysis definitions

**Deliverable:** High-level site API

---

### Phase 5: Pipeline (Days 7-9) - HIGH
**Package:** canvodpy (processor module)  
**Dependencies:** All above  
**Effort:** 600 lines + 350 tests

1. Extract `PipelineOrchestrator`
2. Create `Pipeline` class (user-facing)
3. Batch processing
4. Progress tracking
5. Error handling

**Deliverable:** Complete processing pipeline

---

### Phase 6: Logging & Utils (Days 9-10) - MEDIUM
**Package:** canvodpy (logging/utils modules)  
**Effort:** 300 lines + 150 tests

1. Extract logging setup
2. Context managers
3. Utilities
4. Date/time handling

**Deliverable:** Complete infrastructure

---

### Phase 7: Integration & Testing (Days 10-11) - HIGH
**All Packages**  
**Effort:** Integration work

1. End-to-end testing
2. Demo notebooks
3. Documentation
4. Performance testing

**Deliverable:** Production-ready system

---

## 📊 Lines of Code Summary

| Component | gnssvodpy | canvodpy | Status |
|-----------|-----------|----------|--------|
| **Migrated** | | | |
| RINEX Readers | 2,500 | 2,900 | ✅ |
| Auxiliary Data | 2,000 | 2,500 | ✅ |
| Grids | ~200 | 360 | ✅ |
| Visualization | 1,200 | 1,370 | ✅ |
| **Subtotal** | **5,900** | **7,130** | ✅ |
| | | | |
| **To Migrate** | | | |
| Storage | 2,200 | ~500 | ❌ |
| VOD | 500 | ~400 | ❌ |
| Pipeline | 1,200 | ~600 | ❌ |
| Configuration | 550 | ~200 | ❌ |
| Logging | 300 | ~150 | ❌ |
| Data Matching | 300 | ~200 | ❌ |
| Position | 200 | ~150 | ❌ |
| Utils | 300 | ~150 | ❌ |
| **Subtotal** | **5,550** | **~2,350** | ❌ |
| | | | |
| **TOTAL** | **11,450** | **9,480** | 75% |

**Notes:**
- canvodpy is more concise due to modern design
- Comprehensive tests add ~50% more lines
- Documentation adds ~30% more lines
- Total with tests/docs: ~14,000 lines

---

## 🚀 Next Immediate Steps

### Step 1: Create canvod-store (CRITICAL)
```bash
cd ~/Developer/GNSS/canvodpy/packages
mkdir -p canvod-store/src/canvod/store
mkdir -p canvod-store/tests

# Start with base Icechunk wrapper
# Extract from gnssvodpy/icechunk_manager/store.py
```

### Step 2: Create canvod-vod (CRITICAL)
```bash
mkdir -p canvod-vod/src/canvod/vod
mkdir -p canvod-vod/tests

# Extract VOD algorithms
# From gnssvodpy/vod/
```

### Step 3: Create Configuration System
```bash
cd canvodpy
mkdir -p src/canvod/config

# Design TOML-based configuration
# Extract from gnssvodpy/research_sites_config.py
```

---

## 📝 Success Metrics

**After completing migrations:**

✅ Users can: `pip install canvodpy`  
✅ Simple workflow: 5 lines to process data  
✅ Test coverage: >90% for all packages  
✅ Documentation: Complete API docs + tutorials  
✅ Performance: Equal or better than gnssvodpy  
✅ Community-ready: Public repository, CI/CD  

---

**Status:** Gap analysis complete  
**Timeline:** 11 days for complete migration  
**Next Action:** Begin canvod-store package creation
