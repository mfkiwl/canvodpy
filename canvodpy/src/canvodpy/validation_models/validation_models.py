from asyncio.log import logger
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
from typing import Dict, List, Optional, Tuple, Union

import pint
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic.dataclasses import dataclass
import xarray as xr

from canvodpy.error_handling.error_handling import (
    IncompleteEpochError,
    MissingEpochError,
)
from canvodpy.globals import (
    EPOCH_RECORD_INDICATOR,
    IGS_RNX_DUMP_INTERVALS,
    SEPTENTRIO_SAMPLING_INTERVALS,
    UREG as ureg,
)
from canvodpy.logging.context import get_logger


@dataclass(kw_only=True, config=ConfigDict(arbitrary_types_allowed=True))
class Observation:
    """Represents a single GNSS observation."""
    observation_freq_tag: str  # Combination of SV and Observation code (e.g. 'G01|L1C')
    obs_type: str | None
    value: float | None
    lli: int | None
    ssi: int | None
    frequency: pint.Quantity | None = None

    @field_validator('observation_freq_tag')
    def validate_observation_code(cls, v: str) -> str:
        """
        Validate RINEX v3 observation code format.
        Should accept formats like:
        - 'G01|L1C'  (GPS L1C observation)
        - 'R02|C1P'  (GLONASS C1P observation)
        - 'E01|S5Q'  (Galileo S5Q observation)
        - 'I06|X1'   (IRNSS observation)
        """
        try:
            sv, obs_type = v.split('|')

            # Validate satellite part
            if not re.match(r'^[GRECJSI]\d{2}$', sv):
                raise ValueError(
                    f'Invalid satellite identifier in observation code: {sv}')

            # More permissive observation type validation to handle all systems
            if not re.match(r'^[A-Z0-9][A-Z0-9\d]?[A-Z0-9]?$', obs_type):
                raise ValueError(
                    f'Invalid observation type in code: {obs_type}')

            return v
        except ValueError as e:
            raise ValueError(
                f'Invalid observation code format: {v}. Should be "SVN|OBSCODE"'
            ) from e

    @field_validator('frequency')
    def validate_frequency(
            cls, v: pint.Quantity | None) -> pint.Quantity | None:
        """Validate that frequency is a proper pint.Quantity with frequency units."""
        if v is not None and not isinstance(v, pint.Quantity):
            raise ValueError('Frequency must be a pint.Quantity')
        if v is not None and not v.check('[frequency]'):
            raise ValueError('Frequency must have frequency units')
        return v

    @field_validator('lli', 'ssi')
    def validate_indicators(cls, v: int | None) -> int | None:
        """Validate LLI and SSI values."""
        if v is not None and not (0 <= v <= 9):
            raise ValueError('Indicator values must be between 0 and 9')
        return v

    # @field_validator('obs_type')
    # def validate_obs_type(cls, v: Optional[str]) -> Optional[str]:
    #     """Validate observation type."""
    #     if v is not None and v in ['C', 'L', 'D', 'S']:
    #         raise ValueError(f'Invalid observation type: {v}')
    #     return v


@dataclass(kw_only=True)
class Satellite:
    """
    Represents a GNSS satellite with its observations.
    Supports all major GNSS constellations including IRNSS.
    """
    sv: str
    observations: list[Observation] = Field(default_factory=list)

    @field_validator('sv')
    def validate_sv(cls, v: str) -> str:
        """
        Validate satellite vehicle identifier format.

        Supports:
        - G: GPS
        - R: GLONASS
        - E: Galileo
        - C: BeiDou
        - J: QZSS
        - S: SBAS
        - I: IRNSS
        """
        if not re.match(r'^[GRECJSI]\d{2}$', v):
            raise ValueError(f'Invalid satellite identifier format: {v}')
        return v

    def add_observation(self, observation: Observation) -> None:
        """Add an observation to the satellite."""
        self.observations.append(observation)

    def get_observation(self,
                        observation_freq_tag: str) -> Observation | None:
        """Get an observation by its code."""
        return next((obs for obs in self.observations
                     if obs.observation_freq_tag == observation_freq_tag),
                    None)

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
                f"File {v} does not appear to be of Rinex observation file format.\
                Rinex observation files should have suffix '.2?o' or '.o', where '?' is a digit."
            )
        return v


class RnxVersion3Model(BaseModel):
    version: float

    @field_validator("version")
    def version_must_be_3(cls, v):
        if not 3 <= v < 4:
            raise ValueError("Rinex version must be 3.0x")
        return v


class Rnxv3ObsEpochRecordCompletenessModel(BaseModel):
    epoch_records_indeces: list[tuple[int, int]]
    rnx_file_dump_interval: str | Quantity
    sampling_interval: str | Quantity

    @field_validator("rnx_file_dump_interval")
    def rnx_file_dump_interval(cls, value):
        if not isinstance(value, pint.Quantity):
            value = ureg.Quantity(value).to(ureg.minutes)
        if value not in IGS_RNX_DUMP_INTERVALS:
            get_logger().warning(
                "Unexpected dump interval",
                value=str(value),
                allowed=[str(v) for v in IGS_RNX_DUMP_INTERVALS],
                validator="Rnxv3ObsEpochRecordCompletenessModel",
            )
        return value

    @field_validator("sampling_interval")
    def check_sampling_interval_units(cls, value):
        if not isinstance(value, pint.Quantity):
            value = ureg.Quantity(value).to(ureg.seconds)
        if value not in SEPTENTRIO_SAMPLING_INTERVALS:
            get_logger().error(
                "Invalid sampling interval",
                value=str(value),
                allowed=[str(v) for v in SEPTENTRIO_SAMPLING_INTERVALS],
                validator="Rnxv3ObsEpochRecordCompletenessModel",
            )
            raise ValueError(
                f'sampling_interval={value.magnitude} {value.units}, but must be one of the following: 100ms, 200ms, 500ms, 1s, 2s, 5s, 10s, 15s, 30s, 60s, 2min, 5min, 10min, 15min, 30min, 60min, but got "{value=}"'
            )
        return value

    @model_validator(mode="after")
    def check_intervals(cls, values):
        epoch_records_indeces = values.epoch_records_indeces
        rnx_file_dump_interval = values.rnx_file_dump_interval
        sampling_interval = values.sampling_interval

        if epoch_records_indeces and rnx_file_dump_interval and sampling_interval:
            total_sampling_time = len(
                epoch_records_indeces) * sampling_interval.to(ureg.seconds)
            rnx_file_dump_interval_in_seconds = rnx_file_dump_interval.to(
                ureg.seconds)
            if total_sampling_time != rnx_file_dump_interval_in_seconds:
                get_logger().warning(
                    "Mismatch in expected dump interval",
                    total_sampling_time=str(total_sampling_time),
                    expected=str(rnx_file_dump_interval_in_seconds),
                    validator="Rnxv3ObsEpochRecordCompletenessModel",
                )
                raise MissingEpochError(
                    f"The total sampling time ({total_sampling_time}) does not equal the rnx_file_dump_interval ({rnx_file_dump_interval_in_seconds}).\n This might indicate missing epochs."
                )
        return values


class Rnxv3ObsEpochRecordLineModel(BaseModel):
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
                f'Invalid epoch format: {epoch}.\nA valid format is "> yyyy mm dd hh mm ss.sss epoch_flag num_satellites [reserved] [receiver_clock_offset]"'
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
        values["reserved"] = (int(match.group("reserved"))
                              if match.group("reserved") else None)
        values["receiver_clock_offset"] = (
            float(match.group("receiver_clock_offset"))
            if match.group("receiver_clock_offset") else None)

        return values


@dataclass(frozen=True, kw_only=True)
class Rnxv3ObsEpochRecord:
    """Represents a complete epoch record in RINEX v3 format."""
    info: Rnxv3ObsEpochRecordLineModel
    data: list[Satellite]

    @model_validator(mode='after')
    def check_num_satellites_matches_data(self) -> 'Rnxv3ObsEpochRecord':
        """Validate that the number of satellites matches the data."""
        if not self.info.num_satellites:
            get_logger().error("Epoch missing satellite count",
                               epoch=self.info.epoch,
                               validator="Rnxv3ObsEpochRecord")
            raise IncompleteEpochError(
                "Number of satellites is automatically specified in the epoch record. "
                "Thus, your data seems to be incorrect. Please check the validity of your data."
            )

        if self.info.num_satellites != len(self.data):
            get_logger().warning("Satellite count mismatch",
                                 epoch=self.info.epoch,
                                 expected=self.info.num_satellites,
                                 got=len(self.data),
                                 validator="Rnxv3ObsEpochRecord")
            raise IncompleteEpochError(
                f"Number of satellites mismatch in epoch record. Expected: {self.info.num_satellites}, "
                f"Got: {len(self.data)}. Please check the validity of your data of epoch '{self.info.epoch}'."
            )

        return self

    def get_satellites_by_system(self, system: str) -> list[Satellite]:
        """Get all satellites for a specific system (G, R, E, etc.)."""
        return [sat for sat in self.data if sat.sv.startswith(system)]


# class DataTreeValidator(BaseModel):
#     """
#     This class handles the validation of the datatree structure.
#     """

#     datatree: xr.DataTree

#     class Config:
#         '''Due to a lack of a proper pydantic-core schema for xr.DataTree datatype,\
#             we allow arbitrary types.
#         '''
#         arbitrary_types_allowed = True  # Allow arbitrary types like xr.DataTree

#     @model_validator(mode='before')
#     def validate_datatree(
#             cls, values: Dict[str, xr.DataTree]) -> Dict[str, xr.DataTree]:
#         """
#         Validate the datatree structure to ensure it contains the necessary elements.

#         Parameters
#         ----------
#         values : dict
#             The dictionary containing the 'datatree' to validate.

#         Returns
#         -------
#         values : dict
#             The validated values, returned unmodified.

#         Raises
#         ------
#         ValueError
#             If any of the validation checks fail.
#         """
#         datatree = values.get('datatree')

#         # Validate the type of datatree
#         if not isinstance(datatree, xr.DataTree):
#             raise ValueError("datatree must be an instance of xr.DataTree.")

#         # Validate root-level coords
#         required_coords = ['Epoch', 'SV', 'Frequency']
#         for coord in required_coords:
#             if coord not in datatree['/'].dataset.coords:
#                 raise ValueError(
#                     f"Missing required coordinate '{coord}' at root level.")

#         # Validate root-level data_vars
#         required_data_vars = ['Azimuth', 'Elevation']
#         for var in required_data_vars:
#             if var not in datatree['/'].dataset.data_vars:
#                 raise ValueError(
#                     f"Missing required data variable '{var}' at root level.")

#         # Validate the existence of GNSS Sky and GNSS Canopy groups
#         required_groups = ['/GNSS Sky', '/GNSS Canopy']
#         for group in required_groups:
#             if group not in datatree.groups:
#                 raise ValueError(
#                     f"Missing required group '{group}' in the DataTree.")

#         # Validate 'SNR' in both GNSS Sky and GNSS Canopy
#         for group in required_groups:
#             if 'SNR' not in datatree[group].dataset.data_vars:
#                 raise ValueError(
#                     f"Missing 'SNR' data variable in group '{group}'.")

#         # Validate that 'SNR' has the correct coordinates at root level
#         for group in required_groups:
#             snr = datatree[group].dataset['SNR']
#             required_coords_in_snr = ['Epoch', 'SV', 'Frequency']
#             for coord in required_coords_in_snr:
#                 if coord not in snr.coords:
#                     raise ValueError(
#                         f"SNR in group '{group}' is missing required coordinate '{coord}'."
#                     )

#         # Additional validation: Ensure Azimuth and Elevation have the correct coordinates (SV, Epoch)
#         for var in ['Azimuth', 'Elevation']:
#             var_data = datatree['/'].dataset[var]
#             required_coords = ['SV', 'Epoch']
#             for coord in required_coords:
#                 if coord not in var_data.coords:
#                     raise ValueError(
#                         f"'{var}' data variable at root level is missing required coordinate '{coord}'."
#                     )

#         return values

# class VodDataValidator(BaseModel):
#     """
#     This class handles the validation of the (calculated) VOD data structure and type.
#     """

#     vod_data: xr.Dataset

#     class Config:
#         '''Due to a lack of a proper pydantic-core schema for xr.DataTree datatype,\
#             we allow arbitrary types.
#         '''
#         arbitrary_types_allowed = True  # Allow arbitrary types like xr.DataTree

#     @model_validator(mode='before')
#     def validate_vod_data(
#             cls, values: Dict[str, xr.Dataset]) -> Dict[str, xr.Dataset]:
#         """
#         Validate the VOD data structure to ensure it contains the necessary elements.

#         Parameters
#         ----------
#         values : dict
#             The dictionary containing the 'datatree' to validate.

#         Returns
#         -------
#         values : dict
#             The validated values, returned unmodified.

#         Raises
#         ------
#         ValueError
#             If any of the validation checks fail.
#         """
#         vod_data = values.get('vod_data')

#         # Validate the type of VOD
#         if not vod_data:
#             raise ValueError(
#                 "The vod_data attribute is required in any VOD data.\
#                 It cannot be None. Did you forget to implement a proper\
#                 `VODCalculator.calculate_vod()` method, that returns an `xr.Dataset`?"
#             )

#         if not isinstance(vod_data, xr.Dataset):
#             raise ValueError("vod_data must be an instance of `xr.Dataset`.")

#         # Validate the existence of 'VOD' data variable
#         if 'VOD' not in vod_data.data_vars:
#             raise ValueError(
#                 "Missing required data variable 'VOD' in the VOD data.")

#         # Validate 'VOD' has the correct coordinates
#         vod = vod_data['VOD']
#         required_coords = ['Epoch', 'SV', 'Frequency']

#         for coord in required_coords:
#             if coord not in vod.coords:
#                 raise ValueError(
#                     f"VOD is missing required coordinate '{coord}'.")

#         return values


class VodDataValidator(BaseModel):
    """
    This class handles the validation of the VOD data.
    """

    vod_data: xr.Dataset

    class Config:
        '''Due to a lack of a proper pydantic-core schema for xr.Dataset datatype,\
            we allow arbitrary types.'''
        arbitrary_types_allowed = True  # Allow arbitrary types like xr.Dataset

    @field_validator('vod_data', mode='before')
    def validate_vod_data(cls, value: xr.Dataset):
        """Validate the VOD data."""

        # If vod_data is None, raise an informative error message
        if value is None:
            raise ValueError(
                "vod_data has not been calculated yet. Please implement a `calculate_vod()` method, which should return an `xr.Dataset`"
            )

        # Ensure that 'vod_data' is an xarray Dataset
        if not isinstance(value, xr.Dataset):
            raise ValueError("vod_data must be an instance of `xr.Dataset`.")

        # Add any additional validation logic here, like checking the presence of certain variables
        required_vars = ['Elevation', 'Azimuth']
        for var in required_vars:
            if var not in value.data_vars:
                raise ValueError(
                    f"Missing required data variable '{var}' in vod_data.")

        # Validate the existence of 'VOD' data variable
        if 'VOD' not in value.data_vars:
            raise ValueError(
                "Missing required data variable 'VOD' in the VOD data.")

        # Validate 'VOD' has the correct coordinates
        vod = value['VOD']
        required_coords = ['Epoch', 'SV', 'Frequency']

        for coord in required_coords:
            if coord not in vod.coords:
                raise ValueError(
                    f"VOD is missing required coordinate '{coord}'.")

        return value
