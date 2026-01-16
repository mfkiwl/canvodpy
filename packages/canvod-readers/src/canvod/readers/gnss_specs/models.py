"""Pydantic validation models for RINEX data structures.

These models provide runtime validation for RINEX data parsing,
ensuring data integrity and correct formats.
"""

import re
import warnings
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pint
import xarray as xr
from canvod.readers.gnss_specs.constants import (
    EPOCH_RECORD_INDICATOR,
    IGS_RNX_DUMP_INTERVALS,
    SEPTENTRIO_SAMPLING_INTERVALS,
)
from canvod.readers.gnss_specs.constants import UREG as ureg
from canvod.readers.gnss_specs.exceptions import IncompleteEpochError, MissingEpochError
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic.dataclasses import dataclass


@dataclass(kw_only=True, config=ConfigDict(arbitrary_types_allowed=True))
class Observation:
    """Represents a single GNSS observation."""

    observation_freq_tag: str  # Combination of SV and Observation code (e.g. 'G01|L1C')
    obs_type: str | None
    value: float | None
    lli: int | None
    ssi: int | None
    frequency: pint.Quantity | None = None

    @field_validator("observation_freq_tag")
    def validate_observation_code(cls, v: str) -> str:
        """Validate RINEX v3 observation code format.

        Examples:
            'G01|L1C'  (GPS L1C observation)
            'R02|C1P'  (GLONASS C1P observation)
            'E01|S5Q'  (Galileo S5Q observation)
            'I06|X1'   (IRNSS observation)
        """
        try:
            sv, obs_type = v.split("|")

            # Validate satellite part
            if not re.match(r"^[GRECJSI]\d{2}$", sv):
                raise ValueError(
                    f"Invalid satellite identifier in observation code: {sv}")

            # More permissive observation type validation to handle all systems
            if not re.match(r"^[A-Z0-9][A-Z0-9\d]?[A-Z0-9]?$", obs_type):
                raise ValueError(
                    f"Invalid observation type in code: {obs_type}")

            return v
        except ValueError as e:
            raise ValueError(
                f'Invalid observation code format: {v}. Should be "SVN|OBSCODE"'
            ) from e

    @field_validator("frequency")
    def validate_frequency(cls,
                           v: pint.Quantity | None) -> pint.Quantity | None:
        """Validate that frequency is a proper pint.Quantity with frequency units."""
        if v is not None and not isinstance(v, pint.Quantity):
            raise ValueError("Frequency must be a pint.Quantity")
        if v is not None and not v.check("[frequency]"):
            raise ValueError("Frequency must have frequency units")
        return v

    @field_validator("lli", "ssi")
    def validate_indicators(cls, v: int | None) -> int | None:
        """Validate LLI and SSI values."""
        if v is not None and not (0 <= v <= 9):
            raise ValueError("Indicator values must be between 0 and 9")
        return v


@dataclass(kw_only=True)
class Satellite:
    """Represents a GNSS satellite with its observations.

    Supports all major GNSS constellations including IRNSS.
    """

    sv: str
    observations: list[Observation] = Field(default_factory=list)

    @field_validator("sv")
    def validate_sv(cls, v: str) -> str:
        """Validate satellite vehicle identifier format.

        Supports:
        - G: GPS
        - R: GLONASS
        - E: Galileo
        - C: BeiDou
        - J: QZSS
        - S: SBAS
        - I: IRNSS
        """
        if not re.match(r"^[GRECJSI]\d{2}$", v):
            raise ValueError(f"Invalid satellite identifier format: {v}")
        return v

    def add_observation(self, observation: Observation) -> None:
        """Add an observation to the satellite."""
        self.observations.append(observation)

    def get_observation(self, observation_freq_tag: str) -> Observation | None:
        """Get an observation by its code."""
        return next(
            (obs for obs in self.observations
             if obs.observation_freq_tag == observation_freq_tag),
            None,
        )

    def get_observation_values(self, obs_code: str) -> list[float]:
        """Get all values for a specific observation code."""
        return [
            obs.value for obs in self.observations
            if obs.observation_freq_tag == obs_code and obs.value is not None
        ]


@dataclass(kw_only=True)
class Epoch:
    """Represents a GNSS epoch with its timestamp and satellites."""

    timestamp: datetime
    num_satellites: int
    satellites: list[Satellite] = Field(default_factory=list)

    def add_satellite(self, satellite: Satellite) -> None:
        """Add a satellite to the epoch."""
        self.satellites.append(satellite)

    def get_satellite(self, sv: str) -> Satellite | None:
        """Get a satellite by its identifier."""
        return next((sat for sat in self.satellites if sat.sv == sv), None)

    def get_satellites_by_system(self, system: str) -> list[Satellite]:
        """Get all satellites for a specific system."""
        return [sat for sat in self.satellites if sat.sv.startswith(system)]


class Quantity(pint.Quantity):
    """Pydantic-compatible pint Quantity wrapper."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value, field=None, config=None):
        if isinstance(value, pint.Quantity):
            return value
        try:
            return ureg.Quantity(value)
        except pint.errors.UndefinedUnitError:
            raise ValueError(f"Invalid unit for {value}")


class RnxObsFileModel(BaseModel):
    """Validates RINEX observation file paths."""

    fpath: Path

    @field_validator("fpath")
    def file_must_exist(cls, v):
        if not v.exists():
            raise ValueError(f"File {v} does not exist.")
        return v

    @field_validator("fpath")
    def file_must_have_correct_suffix(cls, v):
        rinex_suffix_pattern = re.compile(
            r"\.2\d[o]$")  # Ensures the format ".2Xo"

        if not (rinex_suffix_pattern.fullmatch(v.suffix) or v.suffix == ".o"):
            raise ValueError(
                f"File {v} does not appear to be of Rinex observation file format. "
                f"Rinex observation files should have suffix '.2?o' or '.o', where '?' is a digit."
            )
        return v


class RnxVersion3Model(BaseModel):
    """Validates RINEX version 3."""

    version: float

    @field_validator("version")
    def version_must_be_3(cls, v):
        if not 3 <= v < 4:
            raise ValueError("Rinex version must be 3.0x")
        return v


class Rnxv3ObsEpochRecordCompletenessModel(BaseModel):
    """Validates completeness of RINEX v3 epoch records."""

    epoch_records_indeces: list[tuple[int, int]]
    rnx_file_dump_interval: str | Quantity
    sampling_interval: str | Quantity

    @field_validator("rnx_file_dump_interval")
    def rnx_file_dump_interval(cls, value):
        if not isinstance(value, pint.Quantity):
            value = ureg.Quantity(value).to(ureg.minutes)
        if value not in IGS_RNX_DUMP_INTERVALS:
            warnings.warn(
                f"Unexpected dump interval: {value}. "
                f"Expected one of: {[str(v) for v in IGS_RNX_DUMP_INTERVALS]}")
        return value

    @field_validator("sampling_interval")
    def check_sampling_interval_units(cls, value):
        if not isinstance(value, pint.Quantity):
            value = ureg.Quantity(value).to(ureg.seconds)
        if value not in SEPTENTRIO_SAMPLING_INTERVALS:
            raise ValueError(
                f"sampling_interval={value.magnitude} {value.units}, "
                f"but must be one of: {[str(v) for v in SEPTENTRIO_SAMPLING_INTERVALS]}"
            )
        return value

    @model_validator(mode="after")
    def check_intervals(self):
        """Validate epoch intervals consistency."""
        epoch_records_indeces = self.epoch_records_indeces
        rnx_file_dump_interval = self.rnx_file_dump_interval
        sampling_interval = self.sampling_interval

        if epoch_records_indeces and rnx_file_dump_interval and sampling_interval:
            total_sampling_time = len(
                epoch_records_indeces) * sampling_interval.to(ureg.seconds)
            rnx_file_dump_interval_in_seconds = rnx_file_dump_interval.to(
                ureg.seconds)
            if total_sampling_time != rnx_file_dump_interval_in_seconds:
                warnings.warn(f"Mismatch in expected dump interval: "
                              f"total_sampling_time={total_sampling_time}, "
                              f"expected={rnx_file_dump_interval_in_seconds}")
                raise MissingEpochError(
                    f"The total sampling time ({total_sampling_time}) does not equal "
                    f"the rnx_file_dump_interval ({rnx_file_dump_interval_in_seconds}). "
                    f"This might indicate missing epochs.")
        return self


class Rnxv3ObsEpochRecordLineModel(BaseModel):
    """Parses and validates RINEX v3 epoch record line."""

    epoch: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    seconds: float
    epoch_flag: int
    num_satellites: int
    epoch_record_indicator: str | None = EPOCH_RECORD_INDICATOR
    reserved: int | None = None
    receiver_clock_offset: float | None = None

    @model_validator(mode="before")
    def parse_epoch(cls, values):
        epoch = values["epoch"]
        pattern = r"^(?P<epoch_record_indicator>>)\s*(?P<year>\d{4})\s+(?P<month>\d{2})\s+(?P<day>\d{2})\s+(?P<hour>\d{2})\s+(?P<minute>\d{2})\s+(?P<seconds>\d+\.\d+)\s+(?P<epoch_flag>\d+)\s+(?P<num_satellites>\d+)\s*(?P<reserved>\d*)\s*(?P<receiver_clock_offset>-?\d*\.\d*)?\s*$"
        match = re.match(pattern, epoch)
        if not match:
            raise ValueError(
                f"Invalid epoch format: {epoch}. "
                f'A valid format is "> yyyy mm dd hh mm ss.sss epoch_flag num_satellites [reserved] [receiver_clock_offset]"'
            )

        values["epoch_record_indicator"] = match.group(
            "epoch_record_indicator")
        values["year"] = int(match.group("year"))
        values["month"] = int(match.group("month"))
        values["day"] = int(match.group("day"))
        values["hour"] = int(match.group("hour"))
        values["minute"] = int(match.group("minute"))
        values["seconds"] = float(match.group("seconds"))
        values["epoch_flag"] = int(match.group("epoch_flag"))
        values["num_satellites"] = int(match.group("num_satellites"))
        values["reserved"] = int(
            match.group("reserved")) if match.group("reserved") else None
        values["receiver_clock_offset"] = (
            float(match.group("receiver_clock_offset"))
            if match.group("receiver_clock_offset") else None)

        return values


@dataclass(frozen=True, kw_only=True)
class Rnxv3ObsEpochRecord:
    """Represents a complete epoch record in RINEX v3 format."""

    info: Rnxv3ObsEpochRecordLineModel
    data: list[Satellite]

    @model_validator(mode="after")
    def check_num_satellites_matches_data(self) -> "Rnxv3ObsEpochRecord":
        """Validate that the number of satellites matches the data."""
        if not self.info.num_satellites:
            raise IncompleteEpochError(
                "Number of satellites is automatically specified in the epoch record. "
                "Thus, your data seems to be incorrect. Please check the validity of your data."
            )

        if self.info.num_satellites != len(self.data):
            raise IncompleteEpochError(
                f"Number of satellites mismatch in epoch record. "
                f"Expected: {self.info.num_satellites}, Got: {len(self.data)}. "
                f"Please check the validity of your data of epoch '{self.info.epoch}'."
            )

        return self

    def get_satellites_by_system(self, system: str) -> list[Satellite]:
        """Get all satellites for a specific system (G, R, E, etc.)."""
        return [sat for sat in self.data if sat.sv.startswith(system)]


class VodDataValidator(BaseModel):
    """Validates VOD (Vegetation Optical Depth) data structure."""

    vod_data: xr.Dataset

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("vod_data", mode="before")
    def validate_vod_data(cls, value: xr.Dataset):
        """Validate the VOD data."""
        if value is None:
            raise ValueError(
                "vod_data has not been calculated yet. "
                "Please implement a `calculate_vod()` method, which should return an `xr.Dataset`"
            )

        if not isinstance(value, xr.Dataset):
            raise ValueError("vod_data must be an instance of `xr.Dataset`.")

        # Validate required variables
        required_vars = ["Elevation", "Azimuth"]
        for var in required_vars:
            if var not in value.data_vars:
                raise ValueError(
                    f"Missing required data variable '{var}' in vod_data.")

        # Validate VOD variable
        if "VOD" not in value.data_vars:
            raise ValueError(
                "Missing required data variable 'VOD' in the VOD data.")

        # Validate VOD coordinates
        vod = value["VOD"]
        required_coords = ["Epoch", "SV", "Frequency"]

        for coord in required_coords:
            if coord not in vod.coords:
                raise ValueError(
                    f"VOD is missing required coordinate '{coord}'.")

        return value
