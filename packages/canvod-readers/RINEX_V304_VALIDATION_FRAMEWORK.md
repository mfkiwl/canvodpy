# RINEX v3.04 Pydantic Validation Framework Proposal

## Overview

Comprehensive validation framework for RINEX v3.04 files based on the official specification, catching irregularities during data reading and ensuring data integrity.

---

## 1. Header Validation Models

### 1.1 Core Header Records (Mandatory)

```python
class RinexVersionType(BaseModel):
    """RINEX VERSION / TYPE - Always first record."""
    version: confloat(ge=3.0, lt=4.0) = Field(..., description="RINEX version 3.0x")
    file_type: Literal['O', 'N', 'M', 'G', 'R', 'E', 'C', 'J', 'I', 'S']
    system: Literal['G', 'R', 'E', 'C', 'J', 'S', 'I', 'M'] | None
    
    @field_validator('file_type')
    def validate_file_type(cls, v):
        """Validate file type codes:
        O=Obs, N=Nav(GPS), G=Nav(GLO), E=Nav(GAL), C=Nav(BDS),
        J=Nav(QZSS), I=Nav(IRNSS), S=Nav(SBAS), M=Met
        """
        return v


class PgmRunByDate(BaseModel):
    """PGM / RUN BY / DATE."""
    program: str = Field(..., max_length=20)
    run_by: str = Field(..., max_length=20)
    date: datetime = Field(..., description="yyyymmdd hhmmss zone")
    timezone: str = Field(..., pattern=r'^[A-Z]{3,4}$')
    
    @field_validator('timezone')
    def recommend_utc(cls, v):
        """Recommend UTC as timezone."""
        if v not in ['UTC', 'LCL']:
            warnings.warn(f"Timezone {v} is not UTC or LCL")
        return v


class MarkerName(BaseModel):
    """MARKER NAME - Required for observation files."""
    name: str = Field(..., max_length=60)


class MarkerType(BaseModel):
    """MARKER TYPE - Required except for GEODETIC/NON_GEODETIC."""
    marker_type: Literal[
        'GEODETIC', 'NON_GEODETIC', 'NON_PHYSICAL',
        'SPACEBORNE', 'AIRBORNE', 'WATER_CRAFT',
        'GROUND_CRAFT', 'FIXED_BUOY', 'FLOATING_BUOY',
        'FLOATING_ICE', 'GLACIER', 'BALLISTIC',
        'ANIMAL', 'HUMAN'
    ]
```

### 1.2 System-Specific Observation Types

```python
class SysNumObsTypes(BaseModel):
    """SYS / # / OBS TYPES - System-dependent observation list."""
    system: Literal['G', 'R', 'E', 'C', 'J', 'S', 'I']
    num_obs_types: conint(ge=1, le=999)
    obs_types: List[str] = Field(..., min_length=1)
    
    @field_validator('obs_types')
    def validate_obs_codes(cls, v, info: ValidationInfo):
        """Validate observation codes per system.
        
        Format: tna where:
        t = observation type (C, L, D, S, I, X)
        n = band/frequency (1-9)
        a = attribute (tracking mode/channel)
        """
        system = info.data.get('system')
        valid_codes = VALID_OBS_CODES.get(system, {})
        
        for obs in v:
            if len(obs) != 3:
                raise ValueError(f"Obs code must be 3 chars: {obs}")
            
            obs_type, band, attr = obs[0], obs[1], obs[2]
            
            # Validate observation type
            if obs_type not in ['C', 'L', 'D', 'S', 'I', 'X']:
                raise ValueError(f"Invalid obs type: {obs_type}")
            
            # Validate band for system
            if band not in valid_codes.get('bands', []):
                raise ValueError(f"Invalid band {band} for system {system}")
            
            # Validate attribute for system/band
            valid_attrs = valid_codes.get(band, {}).get('attrs', [])
            if attr not in valid_attrs:
                raise ValueError(f"Invalid attribute {attr} for {system}/{band}")
        
        return v
    
    @model_validator(mode='after')
    def check_num_matches_list(self) -> 'SysNumObsTypes':
        """Validate number matches list length."""
        if self.num_obs_types != len(self.obs_types):
            raise ValueError(
                f"Number mismatch: {self.num_obs_types} vs {len(self.obs_types)}"
            )
        return self
```

### 1.3 Time System Records

```python
class TimeOfFirstObs(BaseModel):
    """TIME OF FIRST OBS - Required."""
    year: conint(ge=1980)
    month: conint(ge=1, le=12)
    day: conint(ge=1, le=31)
    hour: conint(ge=0, le=23)
    minute: conint(ge=0, le=59)
    second: confloat(ge=0.0, lt=60.0)
    time_system: Literal['GPS', 'GLO', 'GAL', 'QZS', 'BDT', 'IRN']
    
    @field_validator('time_system')
    def validate_time_system(cls, v, info: ValidationInfo):
        """Validate time system consistency with GNSS systems."""
        # For mixed files, time system must be specified
        # Pure files default to their native time system
        return v
    
    @model_validator(mode='after')
    def validate_date(self) -> 'TimeOfFirstObs':
        """Validate date is valid."""
        try:
            datetime(self.year, self.month, self.day, 
                    self.hour, self.minute, int(self.second))
        except ValueError as e:
            raise ValueError(f"Invalid date/time: {e}")
        return self


class LeapSeconds(BaseModel):
    """LEAP SECONDS - Optional but recommended."""
    delta_t_ls: int = Field(..., description="Current leap seconds")
    delta_t_lsf: int | None = Field(None, description="Future leap seconds")
    week_n: int | None = Field(None, description="Week number (continuous)")
    day_n: conint(ge=0, le=6) | conint(ge=1, le=7) | None = None
    time_system: Literal['GPS', 'BDT'] | None = None
    
    @field_validator('day_n')
    def validate_day_system(cls, v, info: ValidationInfo):
        """Validate day number based on time system.
        
        BeiDou: 0-6 (Sun=0)
        GPS/others: 1-7 (Sun=7)
        """
        time_sys = info.data.get('time_system')
        if v is not None:
            if time_sys == 'BDT' and not (0 <= v <= 6):
                raise ValueError("BDS day_n must be 0-6")
            elif time_sys != 'BDT' and not (1 <= v <= 7):
                raise ValueError("GPS/others day_n must be 1-7")
        return v
```

### 1.4 GLONASS-Specific Validation

```python
class GlonassSlotFreq(BaseModel):
    """GLONASS SLOT / FRQ # - Mandatory for GLONASS data."""
    num_slots: conint(ge=1, le=24)
    slot_freq_pairs: Dict[str, int] = Field(
        ..., 
        description="Map of R## to frequency number"
    )
    
    @field_validator('slot_freq_pairs')
    def validate_slots(cls, v, info: ValidationInfo):
        """Validate GLONASS slot/frequency pairs.
        
        Slot: R01-R24
        Freq: -7 to +12
        """
        for slot, freq in v.items():
            # Validate slot format
            if not re.match(r'^R\d{2}$', slot):
                raise ValueError(f"Invalid slot format: {slot}")
            
            slot_num = int(slot[1:])
            if not (1 <= slot_num <= 24):
                raise ValueError(f"Slot number must be 01-24: {slot_num}")
            
            # Validate frequency number
            if not (-7 <= freq <= 12):
                raise ValueError(f"Frequency must be -7 to +12: {freq}")
        
        return v
    
    @model_validator(mode='after')
    def check_count(self) -> 'GlonassSlotFreq':
        """Validate count matches entries."""
        if self.num_slots != len(self.slot_freq_pairs):
            raise ValueError(
                f"Count mismatch: {self.num_slots} vs {len(self.slot_freq_pairs)}"
            )
        return self


class GlonassCodePhaseBias(BaseModel):
    """GLONASS COD/PHS/BIS - Mandatory for GLONASS."""
    c1c: float | None = Field(None, description="L1C code-phase bias (m)")
    c1p: float | None = Field(None, description="L1P code-phase bias (m)")
    c2c: float | None = Field(None, description="L2C code-phase bias (m)")
    c2p: float | None = Field(None, description="L2P code-phase bias (m)")
    
    @model_validator(mode='after')
    def validate_known_or_all_blank(self) -> 'GlonassCodePhaseBias':
        """Either all specified or all blank (unknown)."""
        values = [self.c1c, self.c1p, self.c2c, self.c2p]
        if not (all(v is None for v in values) or all(v is not None for v in values)):
            raise ValueError(
                "GLONASS code/phase bias: either all known or all unknown"
            )
        return self
```

### 1.5 Phase Alignment Validation

```python
class SysPhaseShift(BaseModel):
    """SYS / PHASE SHIFT - Mandatory in RINEX 3.01+."""
    system: Literal['G', 'R', 'E', 'C', 'J', 'S', 'I']
    obs_code: str = Field(..., pattern=r'^[CLDS][1-9][A-Z]$')
    correction_cycles: float | None = Field(
        None, 
        description="Phase correction in cycles"
    )
    satellites: List[str] | None = Field(
        None,
        description="Specific satellites if not all"
    )
    
    @field_validator('correction_cycles')
    def validate_correction(cls, v):
        """Validate phase correction range.
        
        Typical: 0.00, 0.25, 0.50, 0.75 cycles
        """
        if v is not None and not (-1.0 <= v <= 1.0):
            raise ValueError(f"Phase correction must be -1.0 to 1.0: {v}")
        return v
    
    @field_validator('satellites')
    def validate_satellites(cls, v, info: ValidationInfo):
        """Validate satellite list format."""
        if v is not None:
            system = info.data.get('system')
            for sv in v:
                if not sv.startswith(system):
                    raise ValueError(f"SV {sv} doesn't match system {system}")
                if not re.match(r'^[GRECJSI]\d{2}$', sv):
                    raise ValueError(f"Invalid SV format: {sv}")
        return v
```

### 1.6 Antenna Information

```python
class AntennaType(BaseModel):
    """ANT # / TYPE."""
    antenna_number: str = Field(..., max_length=20)
    antenna_type: str = Field(..., max_length=20)
    
    @field_validator('antenna_type')
    def check_igs_format(cls, v):
        """Warn if not in IGS format."""
        # IGS format: NNNN+NNNNNNN AAAA
        if not re.match(r'^[A-Z0-9]+\+[A-Z0-9]+\s+[A-Z0-9]+$', v):
            warnings.warn(f"Antenna type not in IGS format: {v}")
        return v


class AntennaDelta(BaseModel):
    """ANTENNA: DELTA H/E/N or DELTA X/Y/Z."""
    delta_h: float = Field(..., description="Height/X (m)")
    delta_e: float = Field(..., description="East/Y (m)")  
    delta_n: float = Field(..., description="North/Z (m)")
    reference: Literal['HEN', 'XYZ']
    
    @field_validator('delta_h', 'delta_e', 'delta_n')
    def validate_range(cls, v):
        """Validate reasonable antenna offset range."""
        if not (-100.0 <= v <= 100.0):
            warnings.warn(f"Unusual antenna offset: {v}m")
        return v


class AntennaPhaseCenter(BaseModel):
    """ANTENNA: PHASECENTER - Optional."""
    system: Literal['G', 'R', 'E', 'C', 'J', 'S', 'I']
    obs_code: str = Field(..., pattern=r'^[CLDS][1-9][A-Z]$')
    north: float = Field(..., description="North/X (m)")
    east: float = Field(..., description="East/Y (m)")
    up: float = Field(..., description="Up/Z (m)")
    
    @field_validator('north', 'east', 'up')
    def validate_phase_center_offset(cls, v):
        """Validate reasonable phase center offset."""
        if not (-1.0 <= v <= 1.0):
            warnings.warn(f"Unusual phase center offset: {v}m")
        return v
```

---

## 2. Observation Data Validation

### 2.1 Epoch Record Validation

```python
class EpochRecord(BaseModel):
    """Epoch record validation per RINEX 3.04 spec."""
    indicator: Literal['>']
    year: conint(ge=1980)
    month: conint(ge=1, le=12)
    day: conint(ge=1, le=31)
    hour: conint(ge=0, le=23)
    minute: conint(ge=0, le=59)
    second: confloat(ge=0.0, lt=61.0)  # Allow leap second
    epoch_flag: conint(ge=0, le=6)
    num_satellites: conint(ge=0)
    receiver_clock_offset: float | None = None
    
    @field_validator('epoch_flag')
    def validate_epoch_flag(cls, v):
        """Validate epoch flag values.
        
        0: OK
        1: Power failure
        2: Start moving antenna
        3: New site occupation
        4: Header info follows
        5: External event
        6: Cycle slip
        """
        valid_flags = {0, 1, 2, 3, 4, 5, 6}
        if v not in valid_flags:
            raise ValueError(f"Invalid epoch flag: {v}")
        return v
    
    @model_validator(mode='after')
    def validate_datetime(self) -> 'EpochRecord':
        """Validate date/time is reasonable."""
        try:
            dt = datetime(self.year, self.month, self.day,
                         self.hour, self.minute, int(self.second))
            
            # Check not in future
            if dt > datetime.utcnow():
                warnings.warn(f"Epoch in future: {dt}")
            
            # Check not before GPS epoch
            gps_epoch = datetime(1980, 1, 6)
            if dt < gps_epoch:
                raise ValueError(f"Epoch before GPS start: {dt}")
                
        except ValueError as e:
            raise ValueError(f"Invalid date/time: {e}")
        
        return self


class ObservationValue(BaseModel):
    """Single observation value validation."""
    value: float | None
    lli: conint(ge=0, le=9) | None = None
    signal_strength: conint(ge=0, le=9) | None = None
    
    @field_validator('value')
    def validate_observation_range(cls, v, info: ValidationInfo):
        """Validate observation value ranges."""
        if v is not None:
            # Reasonable ranges based on observation type
            obs_type = info.context.get('obs_type', '')
            
            # Pseudorange: 15M to 30M km
            if obs_type.startswith('C'):
                if not (15e6 <= v <= 30e6):
                    warnings.warn(f"Unusual pseudorange: {v}m")
            
            # Phase: reasonable cycle count
            elif obs_type.startswith('L'):
                if not (-1e9 <= v <= 1e9):
                    warnings.warn(f"Unusual phase: {v} cycles")
            
            # Doppler: -50 kHz to +50 kHz
            elif obs_type.startswith('D'):
                if not (-50000 <= v <= 50000):
                    warnings.warn(f"Unusual doppler: {v} Hz")
            
            # Signal strength: positive dBHz
            elif obs_type.startswith('S'):
                if not (0 <= v <= 60):
                    warnings.warn(f"Unusual signal strength: {v} dBHz")
        
        return v
    
    @field_validator('lli')
    def validate_lli_bits(cls, v):
        """Validate Loss of Lock Indicator bits.
        
        Bit 0 (LSB): Loss of lock
        Bit 1: Half-cycle ambiguity
        Bit 2: BOC tracking (Galileo), AS on (GPS - obsolete)
        """
        if v is not None and not (0 <= v <= 7):
            raise ValueError(f"LLI must be 0-7: {v}")
        return v
```

### 2.2 Complete Observation Record

```python
class ObservationEpoch(BaseModel):
    """Complete epoch with all satellite observations."""
    epoch_info: EpochRecord
    satellites: Dict[str, Dict[str, ObservationValue]]
    
    @model_validator(mode='after')
    def validate_satellite_count(self) -> 'ObservationEpoch':
        """Validate satellite count matches epoch header."""
        if len(self.satellites) != self.epoch_info.num_satellites:
            raise ValueError(
                f"Satellite count mismatch: expected {self.epoch_info.num_satellites}, "
                f"got {len(self.satellites)}"
            )
        return self
    
    @field_validator('satellites')
    def validate_satellite_ids(cls, v):
        """Validate all satellite IDs."""
        for sv in v.keys():
            if not re.match(r'^[GRECJSI]\d{2}$', sv):
                raise ValueError(f"Invalid satellite ID: {sv}")
        return v
```

---

## 3. File-Level Validation

### 3.1 Complete File Validator

```python
class RinexObservationFile(BaseModel):
    """Complete RINEX observation file validation."""
    header: RinexObsHeader
    epochs: List[ObservationEpoch]
    
    @model_validator(mode='after')
    def validate_consistency(self) -> 'RinexObservationFile':
        """Cross-validate header and data consistency."""
        
        # Check time system consistency
        if self.header.time_of_first_obs:
            first_epoch_time = self.epochs[0].epoch_info if self.epochs else None
            # Validate first epoch matches TIME OF FIRST OBS
        
        # Check observation types used match header
        obs_types_used = set()
        for epoch in self.epochs:
            for sv, obs_dict in epoch.satellites.items():
                system = sv[0]
                obs_types_used.update(obs_dict.keys())
        
        # Validate against SYS / # / OBS TYPES
        header_obs_types = set()
        for sys_obs in self.header.sys_obs_types:
            header_obs_types.update(sys_obs.obs_types)
        
        missing = obs_types_used - header_obs_types
        if missing:
            raise ValueError(f"Obs types in data but not header: {missing}")
        
        return self


class RinexNavigationFile(BaseModel):
    """RINEX navigation message file validation."""
    header: RinexNavHeader  
    messages: List[NavigationMessage]
    
    @model_validator(mode='after')
    def validate_message_consistency(self) -> 'RinexNavigationFile':
        """Validate navigation messages."""
        
        # Check systems match header
        systems_in_data = {msg.system for msg in self.messages}
        # Cross-check with header ION CORR, TIME SYS CORR, etc.
        
        return self
```

---

## 4. System-Specific Validators

### 4.1 GPS-Specific

```python
class GPSObservationCodes(BaseModel):
    """GPS observation code validator."""
    obs_codes: List[str]
    
    @field_validator('obs_codes')
    def validate_gps_codes(cls, v):
        """Validate GPS-specific observation codes per Table 4."""
        valid_l1 = {'C', 'S', 'L', 'X', 'P', 'W', 'Y', 'M', 'N'}
        valid_l2 = {'C', 'D', 'S', 'L', 'X', 'P', 'W', 'Y', 'M', 'N'}
        valid_l5 = {'I', 'Q', 'X'}
        
        for code in v:
            if len(code) != 3:
                raise ValueError(f"Code must be 3 chars: {code}")
            
            band = code[1]
            attr = code[2]
            
            if band == '1' and attr not in valid_l1:
                raise ValueError(f"Invalid GPS L1 attribute: {attr}")
            elif band == '2' and attr not in valid_l2:
                raise ValueError(f"Invalid GPS L2 attribute: {attr}")
            elif band == '5' and attr not in valid_l5:
                raise ValueError(f"Invalid GPS L5 attribute: {attr}")
        
        return v
```

### 4.2 GLONASS-Specific

```python
class GLONASSValidator(BaseModel):
    """GLONASS-specific validation."""
    
    @staticmethod
    def validate_frequency_number(slot: str, freq_num: int):
        """Validate GLONASS frequency number.
        
        Frequency offset: k * 9/16 MHz (L1), k * 7/16 MHz (L2)
        k = -7 to +12
        """
        if not (-7 <= freq_num <= 12):
            raise ValueError(f"Invalid GLONASS freq number: {freq_num}")
    
    @staticmethod
    def compute_l1_frequency(freq_num: int) -> float:
        """Compute GLONASS L1 frequency.
        
        f_L1(k) = 1602 + k * 9/16 MHz
        """
        return 1602.0 + freq_num * 9.0 / 16.0
    
    @staticmethod
    def compute_l2_frequency(freq_num: int) -> float:
        """Compute GLONASS L2 frequency.
        
        f_L2(k) = 1246 + k * 7/16 MHz
        """
        return 1246.0 + freq_num * 7.0 / 16.0
```

---

## 5. Validation Configuration

### 5.1 Validation Levels

```python
class ValidationLevel(Enum):
    """Validation strictness levels."""
    STRICT = "strict"      # Fail on any violation
    WARNING = "warning"    # Warn but continue
    PERMISSIVE = "permissive"  # Log only


class ValidationConfig(BaseModel):
    """Configuration for validation behavior."""
    level: ValidationLevel = ValidationLevel.WARNING
    check_time_continuity: bool = True
    check_cycle_slips: bool = True
    check_phase_alignment: bool = True
    check_code_phase_bias: bool = True
    validate_observation_ranges: bool = True
    validate_signal_strength: bool = True
    max_time_gap_seconds: float = 300.0  # 5 minutes
    

class RinexValidator:
    """Main validator orchestrator."""
    
    def __init__(self, config: ValidationConfig = None):
        self.config = config or ValidationConfig()
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_file(self, filepath: Path) -> ValidationResult:
        """Validate complete RINEX file."""
        # Parse and validate header
        # Validate each epoch
        # Cross-validate consistency
        # Generate report
        pass
```

---

## 6. Testing Strategy

### 6.1 Unit Tests per Validator

```python
def test_epoch_record_valid():
    """Test valid epoch record."""
    epoch = EpochRecord(
        indicator='>',
        year=2025,
        month=1,
        day=9,
        hour=12,
        minute=30,
        second=15.0,
        epoch_flag=0,
        num_satellites=10
    )
    assert epoch.year == 2025


def test_epoch_record_invalid_date():
    """Test invalid date detection."""
    with pytest.raises(ValueError):
        EpochRecord(
            indicator='>',
            year=2025,
            month=13,  # Invalid
            day=9,
            hour=12,
            minute=30,
            second=15.0,
            epoch_flag=0,
            num_satellites=10
        )


def test_glonass_slot_frequency():
    """Test GLONASS slot/frequency validation."""
    glonass = GlonassSlotFreq(
        num_slots=2,
        slot_freq_pairs={'R01': 1, 'R02': -4}
    )
    assert glonass.slot_freq_pairs['R01'] == 1
    
    # Test invalid frequency
    with pytest.raises(ValueError):
        GlonassSlotFreq(
            num_slots=1,
            slot_freq_pairs={'R01': 15}  # Out of range
        )
```

### 6.2 Integration Tests

```python
def test_complete_file_validation(test_rinex_file):
    """Test validation of complete RINEX file."""
    validator = RinexValidator(
        ValidationConfig(level=ValidationLevel.STRICT)
    )
    
    result = validator.validate_file(test_rinex_file)
    
    assert result.is_valid
    assert len(result.errors) == 0


def test_detect_missing_glonass_bias():
    """Test detection of missing GLONASS code/phase bias."""
    # Create file with GLONASS data but no bias record
    with pytest.raises(ValueError, match="GLONASS COD/PHS/BIS"):
        validator.validate_file(rinex_file_without_bias)
```

---

## 7. Implementation Priority

### Phase 1 (Immediate)
1. ✅ Core header validation (version, marker, obs types)
2. ✅ Epoch record validation  
3. ✅ Basic observation value range checking
4. ✅ Satellite ID validation

### Phase 2 (Next)
5. ⏳ System-specific observation codes
6. ⏳ GLONASS slot/frequency + code/phase bias
7. ⏳ Phase alignment validation
8. ⏳ Time system consistency

### Phase 3 (Future)
9. ⏳ Navigation message validation
10. ⏳ Antenna information validation
11. ⏳ Meteorological data validation
12. ⏳ Advanced cross-validation

---

## 8. Benefits

### Data Quality
- Early detection of format violations
- Catch corruption during file creation
- Ensure spec compliance

### Processing Reliability
- Prevent crashes from malformed data
- Clear error messages for debugging
- Automated data quality reports

### Standard Compliance
- Full RINEX 3.04 spec implementation
- System-specific validations
- Version-aware validation

### Developer Experience
- Type-safe data structures
- Auto-completion in IDEs
- Self-documenting code

---

## Summary

This framework provides:
- **20+ Pydantic models** for comprehensive validation
- **System-specific validators** for GPS, GLONASS, Galileo, BeiDou, QZSS, IRNSS, SBAS
- **Multi-level validation** (header, epoch, observation, file)
- **Configurable strictness** levels
- **Clear error reporting** with context
- **100% RINEX 3.04 compliance**

Ready for implementation in phases, starting with core functionality.
