"""
Internal utilities for canvod-aux package.

Date utilities are imported from canvod.utils.tools (canonical location).
Logger and units are specific to canvod-aux package.
"""

# Import date utilities from canonical location
from canvod.utils.tools import YYYYDOY, get_gps_week_from_filename

# Import aux-specific utilities
from canvod.auxiliary._internal.logger import (
    get_logger,
    reset_context,
    set_file_context,
)
from canvod.auxiliary._internal.units import SPEEDOFLIGHT, UREG

__all__ = [
    # Units
    "UREG",
    "SPEEDOFLIGHT",
    # Date utilities (re-exported from canvod.utils.tools)
    "YYYYDOY",
    "get_gps_week_from_filename",
    # Logging
    "get_logger",
    "set_file_context",
    "reset_context",
]
