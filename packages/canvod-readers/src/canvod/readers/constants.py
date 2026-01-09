"""Constants and global variables for RINEX readers."""

import pint

# Initialize unit registry
UREG = pint.UnitRegistry()
UREG.define("dBHz = 10 * log10(hertz)")
UREG.define("dB = 10 * log10(ratio)")

# Physical constants
SPEEDOFLIGHT: pint.Quantity = 299792458 * UREG.meter / UREG.second

# RINEX parsing
EPOCH_RECORD_INDICATOR: str = ">"

# Data variables to keep from RINEX files
KEEP_RNX_VARS: list[str] = [
    "SNR",
    # "Pseudorange",
    # "Phase",
    # "Doppler",
]  # Note: LLI, SSI and Auxiliary support is experimental

# NetCDF/Zarr compression settings
COMPRESSION: dict[str, bool | int] = {
    "zlib": True,
    "complevel": 5,
}

# GNSS frequency unit
FREQ_UNIT = UREG.MHz

# GLONASS FDMA aggregation
AGGREGATE_GLONASS_FDMA: bool = True  # Whether to aggregate GLONASS FDMA bands

# Septentrio receiver sampling intervals
SEPTENTRIO_SAMPLING_INTERVALS: list[pint.Quantity] = [
    100 * UREG.millisecond,
    200 * UREG.millisecond,
    500 * UREG.millisecond,
    1 * UREG.second,
    2 * UREG.second,
    5 * UREG.second,
    10 * UREG.second,
    15 * UREG.second,
    30 * UREG.second,
    60 * UREG.second,
    2 * UREG.minute,
    5 * UREG.minute,
    10 * UREG.minute,
    15 * UREG.minute,
    30 * UREG.minute,
    60 * UREG.minute,
]

# IGS RINEX dump intervals
IGS_RNX_DUMP_INTERVALS: list[pint.Quantity] = [
    15 * UREG.minute,
    1 * UREG.hour,
    6 * UREG.hour,
    24 * UREG.hour,
]

# Time aggregation
TIME_AGGR: pint.Quantity = 15 * UREG.second

# Metadata
AUTHOR: str = "Nicolas F. Bader"
EMAIL: str = "nicolas.bader@tuwien.ac.at"
INSTITUTION: str = "TU Wien"
DEPARTMENT: str = "Department of Geodesy and Geoinformation"
RESEARCH_GROUP: str = "Climate and Environment Remote Sensing"
WEBSITE: str = "https://www.tuwien.at/en/mg/geo/climers"
SOFTWARE: str = "canVODpy, https://github.com/nfb2021/canvodpy"
