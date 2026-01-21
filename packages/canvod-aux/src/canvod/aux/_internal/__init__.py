"""
Internal utilities for canvod-aux package.

These modules contain minimal copies of shared utilities to maintain
package independence. See /DUPLICATION_TRACKER.md at monorepo root
for canonical sources and copy locations.
"""
from canvod.aux._internal.date_utils import (
    YYYYDOY,
    get_gps_week_from_filename,
    gpsweekday,
)
from canvod.aux._internal.logger import get_logger, reset_context, set_file_context
from canvod.aux._internal.units import SPEEDOFLIGHT, UREG

__all__ = [
    # Units
    "UREG",
    "SPEEDOFLIGHT",
    # Date utilities
    "YYYYDOY",
    "get_gps_week_from_filename",
    "gpsweekday",
    # Logging
    "get_logger",
    "set_file_context",
    "reset_context",
]
