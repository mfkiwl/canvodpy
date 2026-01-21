"""
Date and time utilities for canvod-aux package.

Canonical source: This file is the authoritative version.
See /DUPLICATION_TRACKER.md for copy locations.
"""
import datetime
from functools import total_ordering
from pathlib import Path

from pydantic import Field
from pydantic.dataclasses import dataclass


def get_gps_week_from_filename(file_name: Path) -> str:
    """
    Extract GPS week from GNSS product filenames.
    
    Parameters
    ----------
    file_name : Path
        Path to the GNSS file (SP3, CLK, etc.)
        
    Returns
    -------
    str
        GPS week number as string
    """
    if file_name.suffix in [".clk", ".clk_05s", ".CLK", ".sp3", ".SP3"]:
        # For SP3/CLK files, extract date from filename and convert to GPS week
        date_str = str(file_name).split("_")[1]  # Format: YYYYDOY0000
        date = datetime.datetime.strptime(date_str, "%Y%j%H%M").date()
        gps_week, _ = gpsweekday(date)
        return str(gps_week)
    elif any(ext in str(file_name) for ext in ("TRO", "IONEX")):
        return str(file_name).split("_")[1][:4]
    raise ValueError(
        "Invalid file type. Filename must end with .clk, .CLK, .sp3, .SP3, .TRO, or .IONEX"
    )


def gpsweekday(input_date: datetime.date | str) -> tuple[int, int]:
    """
    Calculate GPS week number and day of week from a date.
    
    GPS time started on January 6, 1980.
    
    Parameters
    ----------
    input_date : datetime.date or str
        Date to convert. If string, format must be "%d-%m-%Y"
        
    Returns
    -------
    tuple[int, int]
        (GPS week number, day of week)
    """
    gps_start_date = datetime.date(1980, 1, 6)

    if isinstance(input_date, str):
        input_date = datetime.datetime.strptime(input_date, "%d-%m-%Y").date()

    return divmod((input_date - gps_start_date).days, 7)


@total_ordering
@dataclass
class YYYYDOY:
    """
    Year and Day-of-Year (DOY) date representation.
    
    Provides conversions between YYYYDOY format, datetime.date,
    and GPS week/day calculations.
    
    Parameters
    ----------
    year : int
        Year (must be >= 1)
    doy : int
        Day of year (1-366)
    """
    year: int = Field(..., ge=1)
    doy: int = Field(..., ge=1, le=366)
    yydoy: str = None
    date: datetime.date = None

    def __post_init__(self):
        self.date = self._calculate_date()
        self.doy = f"{self.doy:03}"
        self.yydoy = f"{str(self.year)[-2:]}{self.doy}"

    def __repr__(self) -> str:
        return f"YYYYDOY(year={self.year}, doy={self.doy}, date={self.date})"

    def __eq__(self, other):
        if not isinstance(other, YYYYDOY):
            return False
        return self.to_str() == other.to_str()

    def __lt__(self, other):
        if not isinstance(other, YYYYDOY):
            return NotImplemented
        return self.date < other.date

    def __hash__(self):
        return hash(self.to_str())

    def _calculate_date(self):
        return datetime.date(self.year, 1, 1) + datetime.timedelta(days=self.doy - 1)

    @staticmethod
    def _validate_doy(doy: int):
        if not 1 <= doy <= 366:
            raise ValueError(
                f"Day of year (DOY) must be between 1-366, got {doy}"
            )

    @classmethod
    def from_date(cls, date: datetime.date) -> 'YYYYDOY':
        """Create YYYYDOY from datetime.date object."""
        if isinstance(date, datetime.datetime):
            date = date.date()
        year = date.year
        doy = (date - datetime.date(year, 1, 1)).days + 1
        cls._validate_doy(doy)
        return cls(year=year, doy=doy)

    @classmethod
    def from_str(cls, yyyydoy: str) -> "YYYYDOY":
        """Create YYYYDOY from string format 'YYYYDOY'."""
        if isinstance(yyyydoy, int):
            yyyydoy = str(yyyydoy)
        if len(yyyydoy) != 7:
            raise ValueError(
                f"Invalid date format. Expected 'YYYYDOY', got '{yyyydoy}'"
            )
        year = int(yyyydoy[:4])
        doy = int(yyyydoy[4:])
        cls._validate_doy(doy)
        jan_first = datetime.datetime(year, 1, 1)
        final_date = jan_first + datetime.timedelta(days=doy - 1)
        return cls.from_date(final_date.date())

    @classmethod
    def from_int(cls, yyyydoy: int) -> "YYYYDOY":
        """Create YYYYDOY from integer format YYYYDOY."""
        return cls.from_str(str(yyyydoy))

    def to_str(self) -> str:
        """Convert to string format 'YYYYDOY'."""
        return f"{self.year}{self.doy}"

    def _gpsweekday(self) -> tuple[int, int]:
        """Calculate GPS week number and day of week."""
        gps_start_date = datetime.date(1980, 1, 6)
        return divmod((self.date - gps_start_date).days, 7)

    @property
    def gps_week(self) -> int:
        """GPS week number."""
        return self._gpsweekday()[0]

    @property
    def gps_day_of_week(self) -> int:
        """GPS day of week (0=Sunday, 6=Saturday)."""
        return self._gpsweekday()[1]
