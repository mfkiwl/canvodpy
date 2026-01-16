# canvodpy-test-data

Test fixtures with falsified data for validation testing.

## Purpose

This repository contains **intentionally corrupted and edge-case files** to test:
- Error handling and validation logic
- Boundary conditions
- Malformed input detection
- Recovery mechanisms

## ⚠️ Important

**These files are NOT for documentation or examples.**  
For clean demo data, see: [`canvodpy-examples`](https://github.com/your-org/canvodpy-examples)

---

## Structure

```
test-data/
├── valid/              # Known-good baseline files
│   ├── rinex/
│   └── aux/
├── corrupted/          # Intentionally broken files
│   ├── rinex/
│   │   ├── truncated_header.rnx
│   │   ├── invalid_epochs.rnx
│   │   ├── bad_satellites.rnx
│   │   ├── missing_end_marker.rnx
│   │   └── corrupt_observations.rnx
│   └── aux/
│       ├── truncated.SP3
│       ├── bad_coordinates.SP3
│       ├── discontinuous.CLK
│       └── negative_clock.CLK
└── edge_cases/         # Unusual but valid cases
    ├── minimal.rnx                # 1 epoch, 1 SV
    ├── single_satellite.rnx       # Only GPS G01
    ├── sparse_observations.rnx    # Large gaps
    ├── multi_gnss.rnx             # GPS+GLO+GAL+BDS
    └── leap_second.rnx            # Epoch at leap second
```

---

## Falsification Categories

### Corrupted RINEX Files

| File | Error Type | Expected Behavior |
|------|------------|-------------------|
| `truncated_header.rnx` | Missing "END OF HEADER" | Raise `HeaderParseError` |
| `invalid_epochs.rnx` | Non-monotonic timestamps | Raise `EpochOrderError` |
| `bad_satellites.rnx` | Invalid SV IDs (G99, R00) | Raise `SatelliteValidationError` |
| `missing_end_marker.rnx` | No file terminator | Raise `FileFormatError` |
| `corrupt_observations.rnx` | Malformed data lines | Raise `ObservationParseError` |

### Corrupted Auxiliary Files

| File | Error Type | Expected Behavior |
|------|------------|-------------------|
| `truncated.SP3` | Incomplete file | Raise `SP3FormatError` |
| `bad_coordinates.SP3` | Positions > 100,000 km | Raise `CoordinateValidationError` |
| `discontinuous.CLK` | Clock jumps > 1ms | Raise `ClockDiscontinuityError` |
| `negative_clock.CLK` | Negative clock values | Raise `ClockValidationError` |

### Edge Cases

| File | Tests | Notes |
|------|-------|-------|
| `minimal.rnx` | Minimum valid file | 1 epoch, 1 SV, 1 obs type |
| `single_satellite.rnx` | Single SV handling | Only G01 for full day |
| `sparse_observations.rnx` | Gap handling | 1-hour observation gaps |
| `multi_gnss.rnx` | Multi-constellation | All 4 major GNSS |
| `leap_second.rnx` | Time handling | Observation at leap second |

---

## Usage in Tests

```python
import pytest
from pathlib import Path

@pytest.fixture
def test_data_dir():
    return Path(__file__).parent / "test-data"

def test_truncated_header_raises_error(test_data_dir):
    from canvod.readers import Rnxv3Obs
    
    corrupted = test_data_dir / "corrupted/rinex/truncated_header.rnx"
    
    with pytest.raises(HeaderParseError):
        obs = Rnxv3Obs(fpath=corrupted)
        ds = obs.to_ds()

def test_bad_coordinates_detected(test_data_dir):
    from canvod.aux import Sp3File
    
    corrupted = test_data_dir / "corrupted/aux/bad_coordinates.SP3"
    
    with pytest.raises(CoordinateValidationError):
        sp3 = Sp3File.from_file(corrupted)
        ds = sp3.data  # Triggers validation
```

---

## Creating Falsified Files

### Guidelines

1. **Base on real files**: Start with valid data, then corrupt
2. **One error per file**: Test specific error conditions
3. **Document expected error**: Update manifest
4. **Create test case**: Each file needs corresponding test

### Example: Creating Truncated Header

```bash
# Start with valid RINEX
cp valid/rinex/2023_001_canopy.rnx corrupted/rinex/truncated_header.rnx

# Remove END OF HEADER marker
sed -i '' '/END OF HEADER/d' corrupted/rinex/truncated_header.rnx

# Verify it fails
pytest tests/test_readers.py::test_truncated_header
```

---

## Git LFS Configuration

Large binary files tracked with Git LFS:

```gitattributes
*.rnx filter=lfs diff=lfs merge=lfs -text
*.RNX filter=lfs diff=lfs merge=lfs -text
*.SP3 filter=lfs diff=lfs merge=lfs -text
*.CLK filter=lfs diff=lfs merge=lfs -text
```

---

## Contributing

When adding new test data:

1. Create the file in appropriate directory
2. Update this README manifest
3. Document expected error/behavior
4. Create corresponding test in main repo
5. Submit PR with descriptive commit message

---

## License

MIT (same as canvodpy)
