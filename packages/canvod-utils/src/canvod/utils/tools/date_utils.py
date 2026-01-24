"""Date and time utilities for GNSS data processing."""

import datetime
from functools import total_ordering
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic.dataclasses import dataclass


def get_gps_week_from_filename(file_name: Path) -> str:
    """
    Extract GPS week from various GNSS product filenames.

    Parameters
    ----------
    file_name : Path
        GNSS product filename (e.g., SP3, CLK, TRO, IONEX)

    Returns
    -------
    str
        GPS week as string

    Raises
    ------
    Warning
        If file type is not recognized

    Examples
    --------
    >>> from pathlib import Path
    >>> week = get_gps_week_from_filename(Path("igs12345.sp3"))
    """
    if file_name.suffix in [".clk", ".clk_05s", ".CLK", ".sp3", ".SP3"]:
        if file_name.suffix == ".clk":
            return str(file_name)[3:-7]
        else:
            # Parse date from filename and convert to GPS week
            date_str = str(file_name).split("_")[1]
            date = datetime.datetime.strptime(date_str, "%Y%j%H%M").date()
            return str(gpsweekday(date)[0])
    elif any(ext in str(file_name) for ext in ("TRO", "IONEX")):
        return str(file_name).split("_")[1][:4]

    msg = (
        "Invalid file type. The filename must end with "
        ".clk, clk_05s, .CLK, .SP3, .TRO, or .IONEX"
    )
    raise Warning(msg)


def gpsweekday(
    input_date: datetime.datetime | datetime.date | str,
    is_datetime: bool = False,
) -> tuple[int, int]:
    """
    Calculate GPS week number and day of week from a given date.

    GPS time started on January 6, 1980.

    Parameters
    ----------
    input_date : datetime.datetime, datetime.date, or str
        The date to calculate GPS week for. If string, format: "dd-mm-yyyy"
    is_datetime : bool, optional
        Whether input_date is a datetime object (default: False)

    Returns
    -------
    tuple[int, int]
        (GPS week number, day of week)

    Examples
    --------
    >>> from datetime import date
    >>> week, day = gpsweekday(date(2025, 1, 24))
    >>> print(f"Week {week}, Day {day}")
    """
    gps_start_date = datetime.date(1980, 1, 6)

    # Convert string to date if needed
    if not is_datetime and isinstance(input_date, str):
        input_date = datetime.datetime.strptime(input_date, "%d-%m-%Y").date()
    elif isinstance(input_date, datetime.datetime):
        input_date = input_date.date()

    # Calculate weeks and days since GPS epoch
    return divmod((input_date - gps_start_date).days, 7)


@dataclass
class YYDOY:
    """
    Two-digit year + day of year (DOY) date representation.

    This is a compact format often used in GNSS filenames.

    Examples
    --------
    >>> date = YYDOY.from_str("25001")  # 2025, day 1
    """

    @classmethod
    def from_str(cls, yydoy: str) -> "YYYYDOY":
        """
        Convert two-digit year DOY string to four-digit YYYYDOY.

        Parameters
        ----------
        yydoy : str
            Two-digit year + DOY (e.g., "25001" for 2025-01-01)

        Returns
        -------
        YYYYDOY
            Four-digit year DOY object
        """
        date_str = f"20{yydoy}"
        return YYYYDOY.from_str(date_str)


@total_ordering
@dataclass
class YYYYDOY:
    """
    Year and day of year (DOY) date representation.

    This format is commonly used in GNSS data processing.

    Parameters
    ----------
    year : int
        The year (must be >= 1)
    doy : int
        Day of year (1-366)
    yydoy : str, optional
        Two-digit year + DOY string representation

    Examples
    --------
    >>> from canvod.utils.tools import YYYYDOY
    >>> date = YYYYDOY.from_str("2025001")
    >>> print(date.to_datetime())
    >>> print(date.to_str())  # "2025001"
    """

    year: int = Field(..., ge=1)
    doy: int = Field(..., ge=1, le=366)
    yydoy: Optional[str] = None

    def __post_init__(self):
        """Set yydoy if not provided."""
        if self.yydoy is None:
            year_str = str(self.year)[2:]  # Last 2 digits
            self.yydoy = f"{year_str}{self.doy:03d}"

    @classmethod
    def from_str(cls, yyyydoy: str) -> "YYYYDOY":
        """
        Create YYYYDOY from string.

        Parameters
        ----------
        yyyydoy : str
            Year + DOY string (e.g., "2025001" for January 1, 2025)

        Returns
        -------
        YYYYDOY
            Date object

        Examples
        --------
        >>> date = YYYYDOY.from_str("2025001")
        >>> date.year
        2025
        >>> date.doy
        1
        """
        if len(yyyydoy) != 7:
            msg = f"YYYYDOY string must be 7 characters, got {len(yyyydoy)}"
            raise ValueError(msg)

        year = int(yyyydoy[:4])
        doy = int(yyyydoy[4:])
        return cls(year=year, doy=doy)

    @classmethod
    def from_datetime(cls, dt: datetime.datetime | datetime.date) -> "YYYYDOY":
        """
        Create YYYYDOY from datetime.

        Parameters
        ----------
        dt : datetime.datetime or datetime.date
            Date to convert

        Returns
        -------
        YYYYDOY
            Date object

        Examples
        --------
        >>> from datetime import date
        >>> date_obj = YYYYDOY.from_datetime(date(2025, 1, 24))
        """
        if isinstance(dt, datetime.datetime):
            dt = dt.date()

        year = dt.year
        doy = dt.timetuple().tm_yday
        return cls(year=year, doy=doy)

    def to_str(self) -> str:
        """
        Convert to YYYYDOY string.

        Returns
        -------
        str
            Seven-character string (e.g., "2025024")

        Examples
        --------
        >>> date = YYYYDOY(year=2025, doy=24)
        >>> date.to_str()
        '2025024'
        """
        return f"{self.year}{self.doy:03d}"

    def to_datetime(self) -> datetime.datetime:
        """
        Convert to datetime.

        Returns
        -------
        datetime.datetime
            Datetime at midnight for this date

        Examples
        --------
        >>> date = YYYYDOY(year=2025, doy=1)
        >>> dt = date.to_datetime()
        """
        return datetime.datetime.strptime(self.to_str(), "%Y%j")

    def __str__(self) -> str:
        """String representation."""
        return self.to_str()

    def __repr__(self) -> str:
        """Repr."""
        return f"YYYYDOY(year={self.year}, doy={self.doy})"

    def __eq__(self, other: object) -> bool:
        """Equality comparison."""
        if not isinstance(other, YYYYDOY):
            return NotImplemented
        return self.year == other.year and self.doy == other.doy

    def __lt__(self, other: "YYYYDOY") -> bool:
        """Less than comparison."""
        if self.year != other.year:
            return self.year < other.year
        return self.doy < other.doy

    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        return hash((self.year, self.doy))
