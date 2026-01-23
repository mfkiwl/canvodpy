# Migration Status - Configuration System

## ✅ Completed

### 1. Configuration System Implementation
- ✅ Pydantic models with validation
- ✅ YAML-based configuration files  
- ✅ CLI tools (canvodpy config init/validate/show/edit)
- ✅ MetadataConfig for author/email/institution
- ✅ StorageConfig with stores_root_dir
- ✅ Software metadata in `canvod.utils._meta`

### 2. Constants Cleanup
- ✅ Removed user settings from `canvod/readers/gnss_specs/constants.py`
- ✅ Kept only true constants (UREG, SPEEDOFLIGHT, FREQ_UNIT, etc.)
- ✅ Created cleaned version with proper documentation

### 3. Preprocessing Module Updates
- ✅ Updated `canvod-aux/preprocessing.py` to accept `aggregate_glonass_fdma` parameter
- ✅ Updated all preprocessing functions (map_aux_sv_to_sid, pad_to_global_sid, prep_aux_ds, preprocess_aux_for_interpolation)
- ✅ Updated `canvod-store/preprocessing.py` IcechunkPreprocessor to delegate to canvod-aux functions
- ✅ Removed gnssvodpy.globals imports from IcechunkPreprocessor

## 🔄 Pending Migration

### Files Still Importing from gnssvodpy.globals

**packages/canvod-aux/src/canvod/aux/pipeline.py**
- Imports: AGENCY, CLK_FILE_PATH, FTP_SERVER, PRODUCT_TYPE, SP3_FILE_PATH
- These are used as default values in the pipeline
- **Action needed:** Update AuxDataPipeline to accept config parameter
  ```python
  class AuxDataPipeline:
      def __init__(self, matched_dirs: MatchedDirs, config: CanvodConfig):
          self.config = config
          # Use config.processing.aux_data.agency instead of AGENCY
          # etc.
  ```

### Migration Strategy for Remaining Files

1. **Update function signatures to accept config:**
   ```python
   # Before
   def some_function():
       from gnssvodpy.globals import SETTING
       use_setting(SETTING)
   
   # After
   def some_function(config: CanvodConfig):
       use_setting(config.processing.setting_name)
   ```

2. **Load config at entry points:**
   ```python
   from canvod.utils.config import load_config
   
   config = load_config()
   pipeline = AuxDataPipeline(matched_dirs, config)
   ```

3. **For backward compatibility, make config optional:**
   ```python
   def some_function(config: CanvodConfig | None = None):
       if config is None:
           config = load_config()
       # use config...
   ```

## 📋 Migration Checklist

### Configuration Values Moved

| Old Location (gnssvodpy.globals) | New Location (config) | Status |
|----------------------------------|----------------------|--------|
| `AUTHOR` | `metadata.author` | ✅ Done |
| `EMAIL` | `metadata.email` | ✅ Done |
| `INSTITUTION` | `metadata.institution` | ✅ Done |
| `DEPARTMENT` | `metadata.department` | ✅ Done |
| `RESEARCH_GROUP` | `metadata.research_group` | ✅ Done |
| `WEBSITE` | `metadata.website` | ✅ Done |
| `SOFTWARE` | `canvod.utils._meta.SOFTWARE_ATTRS` | ✅ Done |
| `KEEP_RNX_VARS` | `processing.keep_rnx_vars` | ✅ Done |
| `COMPRESSION` | `compression.{zlib, complevel}` | ✅ Done |
| `TIME_AGGR` | `processing.time_aggregation_seconds` | ✅ Done |
| `AGGREGATE_GLONASS_FDMA` | `processing.aggregate_glonass_fdma` | ✅ Done |
| `AGENCY` | `aux_data.agency` | ⚠️  Pending (pipeline.py) |
| `PRODUCT_TYPE` | `aux_data.product_type` | ⚠️  Pending (pipeline.py) |
| `FTP_SERVER` | Auto-detected from `cddis_mail` | ⚠️  Pending (pipeline.py) |
| `CLK_FILE_PATH` | ? | ⚠️  Pending (needs investigation) |
| `SP3_FILE_PATH` | ? | ⚠️  Pending (needs investigation) |
| `GNSS_ROOT_DIR` | `credentials.gnss_root_dir` | ✅ Done |
| `CDDIS_MAIL` | `credentials.cddis_mail` | ✅ Done |
| `KEEP_SIDS` | `sids.get_sids()` | ✅ Done |

## 🎯 Next Steps

### Immediate (Required for Clean Migration)
1. Update `canvod-aux/pipeline.py` to use config instead of gnssvodpy.globals
2. Search for and update any remaining gnssvodpy.globals imports in the monorepo
3. Test that all preprocessing functions work with config parameters

### Future (When Ready to Remove gnssvodpy Dependency)
1. Update all entry points to load config and pass it through
2. Remove gnssvodpy from dependencies entirely
3. Ensure all tests pass with new config system

## 🧪 Testing

```bash
# Verify config system works
canvodpy config validate

# Test preprocessing with config
python -c "
from canvod.utils.config import load_config
from canvod.aux.preprocessing import prep_aux_ds

config = load_config()
aggregate = config.processing.processing.aggregate_glonass_fdma
print(f'GLONASS FDMA aggregation: {aggregate}')
"

# Test metadata
python -c "
from canvod.utils.config import load_config
from canvod.utils._meta import SOFTWARE_ATTRS

config = load_config()
print('Metadata:', config.processing.metadata.to_attrs_dict())
print('Software:', SOFTWARE_ATTRS)
"
```

## 📝 Notes

- All preprocessing functions now accept `aggregate_glonass_fdma` parameter with default=True
- IcechunkPreprocessor delegates to canvod-aux functions (no duplicate code)
- Configuration is backward compatible (defaults match old constants)
- Software version is centralized in `canvod.utils._meta.__version__`
