"""
Utility tools for canVODpy packages.

This module provides common utilities used across all canVODpy packages:
- Version management
- Date/time utilities for GNSS data
- Validation helpers
- File hashing

Examples
--------
>>> from canvod.utils.tools import get_version_from_pyproject
>>> version = get_version_from_pyproject()

>>> from canvod.utils.tools import YYYYDOY
>>> date = YYYYDOY.from_str("2025024")
>>> print(date.to_datetime())

>>> from canvod.utils.tools import isfloat
>>> isfloat("3.14")  # True
"""

from .date_utils import YYDOY, YYYYDOY, get_gps_week_from_filename, gpsweekday
from .hashing import rinex_file_hash
from .validation import isfloat
from .version import get_version_from_pyproject

__all__ = [
    # Version
    "get_version_from_pyproject",
    # Date/time
    "YYYYDOY",
    "YYDOY",
    "gpsweekday",
    "get_gps_week_from_filename",
    # Validation
    "isfloat",
    # Hashing
    "rinex_file_hash",
]
