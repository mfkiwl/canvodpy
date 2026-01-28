"""
Constants for RINEX readers.

This module contains only true physical/technical constants that should
never change. User-configurable settings have been moved to the configuration
system (canvod.utils.config).

Removed and moved to config:
- KEEP_RNX_VARS → processing.keep_rnx_vars
- COMPRESSION → compression.{zlib, complevel}
- TIME_AGGR → processing.time_aggregation_seconds
- AGGREGATE_GLONASS_FDMA → processing.aggregate_glonass_fdma
- AUTHOR, EMAIL, etc. → metadata.{author, email, ...}
- SOFTWARE → canvod.utils._meta.SOFTWARE_ATTRS
"""

import pint

# Initialize unit registry
UREG: pint.UnitRegistry = pint.UnitRegistry()
UREG.define("dBHz = 10 * log10(hertz)")
UREG.define("dB = 10 * log10(ratio)")

# Physical constants
SPEEDOFLIGHT: pint.Quantity = 299792458 * UREG.meter / UREG.second

# RINEX parsing
EPOCH_RECORD_INDICATOR: str = ">"

# GNSS frequency unit
FREQ_UNIT: pint.Unit = UREG.MHz

# Septentrio receiver sampling intervals (hardware capabilities)
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

# IGS RINEX dump intervals (data availability)
IGS_RNX_DUMP_INTERVALS: list[pint.Quantity] = [
    15 * UREG.minute,
    1 * UREG.hour,
    6 * UREG.hour,
    24 * UREG.hour,
]
