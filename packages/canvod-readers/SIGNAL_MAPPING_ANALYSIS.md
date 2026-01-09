# 🔍 Signal Mapping Migration Analysis

## Current Status: ❌ **CRITICAL ISSUE FOUND**

### Problem: signals.py has WRONG CODE
The file `gnss_specs/signals.py` currently contains the **ORIGINAL gnssvodpy code** with imports from `gnssvodpy.*` instead of the cleaned canvod version!

```python
# ❌ CURRENT (WRONG):
from gnssvodpy.globals import FREQ_UNIT, SPEEDOFLIGHT
from gnssvodpy.signal_frequency_mapping.bands import Bands
from gnssvodpy.signal_frequency_mapping.gnss_systems import (...)
```

This will **BREAK** when we try to run tests because it's importing from the old package!

---

## 📊 What's Missing

### Files to Migrate (1,517 lines total):

| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| **gnss_systems.py** | 993 | Constellation classes (GPS, Galileo, etc.) | ❌ Not migrated |
| **bands.py** | 338 | Band registry & properties aggregation | ❌ Not migrated |
| **signal_mapping.py** | 186 | SignalIDMapper class | ❌ Wrong version |
| **Total** | **1,517** | Complete signal mapping system | **0% done** |

---

## 🏗️ Architecture Overview

### Current gnssvodpy Structure:
```
gnssvodpy/signal_frequency_mapping/
├── __init__.py
├── gnss_systems.py (993 lines)
│   ├── WikipediaCache (satellite list caching)
│   ├── GNSSConstellation (abstract base)
│   ├── GPS (class)
│   ├── GALILEO (class)
│   ├── GLONASS (class with FDMA)
│   ├── BEIDOU (class)
│   ├── IRNSS (class)
│   ├── QZSS (class)
│   └── SBAS (class)
│
├── bands.py (338 lines)
│   └── Bands (aggregates all constellations)
│       ├── BAND_PROPERTIES
│       ├── SYSTEM_BANDS
│       └── OVERLAPPING_GROUPS
│
└── signal_mapping.py (186 lines)
    └── SignalIDMapper (uses Bands)
        ├── create_signal_id()
        ├── parse_signal_id()
        ├── get_band_frequency()
        ├── get_band_bandwidth()
        └── get_overlapping_group()
```

### What v3_04.py Actually Uses:

From the RINEX reader, we use:
```python
# In __init__:
self._signal_mapper = SignalIDMapper(aggregate_glonass_fdma=...)

# Throughout the code:
sid = self._signal_mapper.create_signal_id(sv, obs_code)
sv, band, code = self._signal_mapper.parse_signal_id(sid)
freq = self._signal_mapper.get_band_frequency(band)
bw = self._signal_mapper.get_band_bandwidth(band)
group = self._signal_mapper.get_overlapping_group(band)
```

---

## 🎯 Required Classes & Data

### 1. GNSSConstellation Classes (gnss_systems.py)

Each constellation class provides:
```python
class GPS:
    SYSTEM_ABBR = "G"
    BAND_PROPERTIES = {
        "L1": {
            "freq": 1575.42,      # MHz
            "bandwidth": 24.0,     # MHz
            "channel": "L",        # Signal type
        },
        "L2": {...},
        "L5": {...},
    }
    SYSTEM_BANDS = {
        "1": "L1",
        "2": "L2",
        "5": "L5",
    }
```

**7 constellation classes needed:**
- GPS
- GALILEO  
- GLONASS (special: FDMA frequency shift per satellite)
- BEIDOU
- IRNSS
- QZSS
- SBAS

### 2. Bands Class (bands.py)

Aggregates all constellations:
```python
class Bands:
    BAND_PROPERTIES = {
        # All bands from all constellations
        "L1": {"freq": 1575.42, "bandwidth": 24.0, ...},
        "E1": {"freq": 1575.42, "bandwidth": 24.0, ...},
        "G1": {"freq": 1602.00, "bandwidth": ..., ...},
        ...
    }
    
    SYSTEM_BANDS = {
        "G": {"1": "L1", "2": "L2", "5": "L5"},
        "E": {"1": "E1", "5": "E5a", "7": "E5b", ...},
        "R": {"1": "G1", "2": "G2", "3": "G3"},
        ...
    }
    
    OVERLAPPING_GROUPS = {
        "L1_E1_B1I": ["L1", "E1", "B1I"],    # ~1575 MHz
        "L5_E5a": ["L5", "E5a"],              # ~1176 MHz
        "L2_E5b_B2b": ["L2", "E5b", "B2b"],  # ~1207-1227 MHz
    }
```

### 3. SignalIDMapper (signal_mapping.py)

Uses Bands to provide the interface:
```python
class SignalIDMapper:
    def __init__(self, aggregate_glonass_fdma=True):
        self._bands = Bands(aggregate_glonass_fdma)
        self.SYSTEM_BANDS = self._bands.SYSTEM_BANDS
        self.BAND_PROPERTIES = self._bands.BAND_PROPERTIES
        self.OVERLAPPING_GROUPS = self._bands.OVERLAPPING_GROUPS
    
    def create_signal_id(sv, obs_code) -> str: ...
    def parse_signal_id(sid) -> tuple: ...
    def get_band_frequency(band) -> float: ...
    def get_band_bandwidth(band) -> float: ...
    def get_overlapping_group(band) -> str: ...
```

---

## 🔧 Dependencies Analysis

### External Dependencies (already in pyproject.toml):
- ✅ `pint` - For unit handling
- ✅ `numpy` - For numerical operations
- ❌ `pandas` - Used in WikipediaCache (optional feature)
- ❌ `natsort` - Used in WikipediaCache (optional feature)  
- ❌ `requests` - Used in WikipediaCache (optional feature)
- ❌ `matplotlib` - Used in Bands for visualization (optional feature)

### Internal Dependencies:
- ✅ `canvod.readers.gnss_specs.constants` - UREG, FREQ_UNIT, SPEEDOFLIGHT
- ✅ `canvod.readers.gnss_specs.exceptions` - (not used in signal mapping)

---

## 📝 Migration Options

### Option 1: Full Migration (Recommended)
**Pros:**
- Complete functionality
- All features available
- Future-proof

**Cons:**
- 1,517 lines to migrate
- More dependencies (pandas, natsort, requests, matplotlib)
- More complex

**What to migrate:**
1. `gnss_systems.py` → `gnss_specs/constellations.py` (993 lines)
2. `bands.py` → `gnss_specs/bands.py` (338 lines)
3. `signal_mapping.py` → `gnss_specs/signals.py` (186 lines)

### Option 2: Simplified Core (Quick Fix)
**Pros:**
- Minimal code (~300 lines)
- No extra dependencies
- Just the data needed for RINEX reading

**Cons:**
- No WikipediaCache (satellite list updates)
- No visualization
- No GLONASS FDMA per-satellite frequencies
- Harder to extend later

**What to create:**
1. Static band definitions
2. Simple SignalIDMapper
3. No constellation classes

### Option 3: Hybrid Approach (BEST)
**Pros:**
- Core functionality immediately
- Can add advanced features later
- Manageable migration

**Cons:**
- Need to migrate in phases

**Phase 1 (NOW):**
- Create static BAND_PROPERTIES dict (~50 lines)
- Create static SYSTEM_BANDS dict (~30 lines)
- Create static OVERLAPPING_GROUPS dict (~10 lines)
- Create simplified SignalIDMapper (~100 lines)
- **Total: ~200 lines**

**Phase 2 (LATER):**
- Migrate full constellation classes
- Add WikipediaCache
- Add visualization
- Add GLONASS FDMA

---

## 🚀 Recommended Action Plan

### Immediate (Today):
1. **Fix signals.py** - Replace with clean simplified version (~200 lines)
   - Static band data for all GNSS systems
   - SignalIDMapper with all required methods
   - No external dependencies beyond pint

2. **Update imports** in v3_04.py (if needed)

3. **Test** - Run pytest to verify it works

### Future (Phase 2):
1. Migrate full constellation classes (when needed)
2. Add WikipediaCache for satellite list updates
3. Add visualization features

---

## 📋 Implementation Checklist

### Phase 1: Simplified Signal Mapping (Immediate)

**File: `gnss_specs/signals.py` (NEW, ~200 lines)**
- [ ] Band frequency definitions (GPS, Galileo, GLONASS, BeiDou, IRNSS, QZSS, SBAS)
- [ ] System-to-band mappings
- [ ] Overlapping group definitions
- [ ] SignalIDMapper class with all required methods
- [ ] Imports from canvod.readers.gnss_specs.constants only

**Data needed:**
```python
BAND_PROPERTIES = {
    # GPS
    "L1": {"freq": 1575.42, "bandwidth": 24.0},
    "L2": {"freq": 1227.60, "bandwidth": 24.0},
    "L5": {"freq": 1176.45, "bandwidth": 24.0},
    
    # Galileo
    "E1": {"freq": 1575.42, "bandwidth": 24.0},
    "E5a": {"freq": 1176.45, "bandwidth": 20.46},
    "E5b": {"freq": 1207.14, "bandwidth": 20.46},
    "E5": {"freq": 1191.795, "bandwidth": 51.15},
    "E6": {"freq": 1278.75, "bandwidth": 40.92},
    
    # GLONASS
    "G1": {"freq": 1602.00, "bandwidth": 9.0},  # Center freq
    "G2": {"freq": 1246.00, "bandwidth": 9.0},
    "G3": {"freq": 1202.025, "bandwidth": 20.0},
    
    # BeiDou
    "B1I": {"freq": 1561.098, "bandwidth": 4.092},
    "B2I": {"freq": 1207.14, "bandwidth": 4.092},
    "B3I": {"freq": 1268.52, "bandwidth": 20.46},
    
    # IRNSS
    # ... etc
}

SYSTEM_BANDS = {
    "G": {"1": "L1", "2": "L2", "5": "L5"},
    "E": {"1": "E1", "5": "E5a", "7": "E5b", "8": "E5", "6": "E6"},
    "R": {"1": "G1", "2": "G2", "3": "G3"},
    "C": {"2": "B1I", "7": "B2I", "6": "B3I"},
    # ... etc
}

OVERLAPPING_GROUPS = {
    "L1_E1_B1I": ["L1", "E1", "B1I"],
    "L5_E5a": ["L5", "E5a"],
    "L2_E5b_B2b": ["L2", "E5b", "B2b"],
}
```

---

## ⚡ Estimated Time

### Phase 1 (Simplified):
- Write static data structures: **30 min**
- Write SignalIDMapper class: **30 min**
- Test and fix: **30 min**
- **Total: 1-1.5 hours**

### Phase 2 (Full):
- Migrate constellation classes: **2 hours**
- Migrate Bands class: **1 hour**
- Add WikipediaCache: **1 hour**
- Testing: **1 hour**
- **Total: 5 hours**

---

## 💡 Recommendation

**START WITH PHASE 1** (Simplified, ~200 lines)

This gives us:
- ✅ Working signal mapping immediately
- ✅ No extra dependencies
- ✅ All functionality needed for RINEX reading
- ✅ Can test and commit today
- ✅ Easy to extend later with Phase 2

**Then do Phase 2 later** when we need:
- Advanced GLONASS FDMA per-satellite frequencies
- Satellite list updates from Wikipedia
- Visualization features
- More detailed band information

---

## 🎯 Next Steps

**Ready to implement?**

1. I'll create the simplified `signals.py` with complete band data
2. Update any imports if needed
3. Run tests to verify
4. Commit and move forward

**Say the word and I'll start!**
