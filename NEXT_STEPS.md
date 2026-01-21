# Next Steps: Complete CANVOD-READERS Documentation

## Files Ready to Commit (6)
```bash
git add src/canvod/readers/base.py
git add src/canvod/readers/utils/date_utils.py
git add src/canvod/readers/matching/dir_matcher.py
git add src/canvod/readers/_shared/signals.py
git add src/canvod/readers/gnss_specs/bands.py
git add src/canvod/readers/gnss_specs/constellations.py
git commit -F COMMIT_MESSAGE.md
```

## Quick Reference: Remaining Work

### Priority 1: Validators (15 minutes)
**File:** `src/canvod/readers/gnss_specs/models.py`

Add `-> None` to these 11 functions:
```python
# Lines to fix:
def file_must_exist(v) -> None:                      # line 188
def file_must_have_correct_suffix(v) -> None:        # line 194  
def version_must_be_3(v) -> None:                    # line 212
def rnx_file_dump_interval(value) -> None:           # line 226
def check_sampling_interval_units(value) -> None:    # line 236
def check_intervals(...) -> None:                    # line 247
def parse_epoch(values) -> Epoch:                    # line 286 (needs return type)
def validate_vod_data(...) -> None:                  # line 353
```

Also add type hints to parameters (6 validators):
```python
def file_must_exist(v: Path) -> None:
def file_must_have_correct_suffix(v: Path) -> None:
def version_must_be_3(v: str) -> None:
def rnx_file_dump_interval(value: int) -> None:
def check_sampling_interval_units(value: str) -> None:
def parse_epoch(values: list[str]) -> Epoch:
```

### Priority 2: RINEX Implementation (60 minutes)
**File:** `src/canvod/readers/rinex/v3_04.py` (1,218 lines)

22 functions need complete NumPy docstrings:
- Properties: `header`, `file_hash`, `start_time`, `end_time`, `systems`, `num_epochs`, `num_satellites`, `epochs`
- Parsing: `parse_marker_number`, `get_epoch_record_batches`, `parse_observation_slice`, `process_satellite_data`
- Iteration: `iter_epochs`, `iter_epochs_in_range`
- Utilities: `get_datetime_from_epoch_record_info`, `epochrecordinfo_dt_to_numpy_dt`, `infer_dump_interval`, `validate_epoch_completeness`, `filter_by_overlapping_groups`, `create_rinex_netcdf_with_signal_id`, `safe_float`
- Main: `to_ds`

Pattern for properties:
```python
@property
def property_name(self) -> ReturnType:
    """Brief description.
    
    Returns
    -------
    ReturnType
        Description of what is returned
    """
```

Pattern for methods:
```python
def method_name(self, param: Type) -> ReturnType:
    """Brief description.
    
    Parameters
    ----------
    param : Type
        Description
    
    Returns
    -------
    ReturnType
        Description
        
    Raises
    ------
    ExceptionType
        When this happens
    """
```

### Priority 3: Models Docstrings (15 minutes)
**File:** `src/canvod/readers/gnss_specs/models.py`

17 functions need Parameter/Returns sections:
- Validators: Add Returns section with "None" and Raises section
- Methods: Add Parameters section for all arguments

## Automated Check Script

Run this to verify progress:
```bash
cd /Users/work/Developer/GNSS/canvodpy
python3 analyze_readers.py
```

## IDE Testing Checklist

After completing each file:
1. Open in VSCode/PyCharm
2. Hover over function names - should show full signature
3. Hover over return statements - should show return type
4. Hover over parameters - should show parameter type
5. Type `function_name(` - should show parameter hints

## Completion Targets

- **Phase 1 (Current)**: 40% - Core interfaces ✅
- **Phase 2**: 55% - Add all `-> None` hints (+15 min)
- **Phase 3**: 85% - Complete rinex/v3_04.py (+60 min)
- **Phase 4**: 100% - Full documentation (+15 min)

## Notes

- **No old typing**: Already using modern `X | None` syntax ✅
- **NumPy style**: Use "Parameters", "Returns", "Raises" sections
- **Returns for None**: Even `-> None` needs Returns section in docstring
- **Property pattern**: Properties always get Returns section, no Parameters
