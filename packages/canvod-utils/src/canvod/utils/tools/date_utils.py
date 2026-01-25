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
    ValueError
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
    raise ValueError(msg)


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

    Attributes
    ----------
    date : datetime.date
        Calculated calendar date
    yydoy : str
        Two-digit year + DOY string representation
    doy : str
        Day of year as zero-padded string (e.g., "001")

    Examples
    --------
    >>> from canvod.utils.tools import YYYYDOY
    >>> date = YYYYDOY.from_str("2025001")
    >>> print(date.to_datetime())
    >>> print(date.to_str())  # "2025001"
    >>> print(date.doy)  # "001"
    >>> print(date.date)  # datetime.date(2025, 1, 1)
    """

    year: int = Field(..., ge=1)
    doy: int = Field(..., ge=1, le=366)
    yydoy: Optional[str] = None
    date: Optional[datetime.date] = None

    def __post_init__(self):
        """Calculate derived fields after initialization."""
        # Store original doy as int for calculations
        doy_int = self.doy
        
        # Convert doy to zero-padded string
        self.doy = f"{doy_int:03d}"
        
        # Calculate date
        self.date = datetime.date(self.year, 1, 1) + datetime.timedelta(days=doy_int - 1)
        
        # Set yydoy if not provided
        if self.yydoy is None:
            year_str = str(self.year)[2:]  # Last 2 digits
            self.yydoy = f"{year_str}{self.doy}"

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
        '001'
        """
        if len(yyyydoy) != 7:
            msg = f"Invalid date format. Expected 'YYYYDDD', got '{yyyydoy}'"
            raise ValueError(msg)

        year = int(yyyydoy[:4])
        doy = int(yyyydoy[4:])
        
        # Validate doy range
        if not 1 <= doy <= 366:
            raise ValueError(
                f"Day of year (DOY) must be in range [1, 366], got {doy}"
            )
        
        return cls(year=year, doy=doy)

    @classmethod
    def from_date(cls, dt: datetime.datetime | datetime.date) -> "YYYYDOY":
        """
        Create YYYYDOY from date.

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
        >>> date_obj = YYYYDOY.from_date(date(2025, 1, 24))
        >>> date_obj.year
        2025
        >>> date_obj.doy
        '024'
        """
        if isinstance(dt, datetime.datetime):
            dt = dt.date()

        year = dt.year
        doy = dt.timetuple().tm_yday
        return cls(year=year, doy=doy)

    @classmethod
    def from_datetime(cls, dt: datetime.datetime | datetime.date) -> "YYYYDOY":
        """
        Create YYYYDOY from datetime (alias for from_date).

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
        return cls.from_date(dt)

    @classmethod
    def from_int(cls, yyyydoy: int) -> "YYYYDOY":
        """
        Create YYYYDOY from integer.

        Parameters
        ----------
        yyyydoy : int
            Year + DOY as integer (e.g., 2025001)

        Returns
        -------
        YYYYDOY
            Date object

        Examples
        --------
        >>> date = YYYYDOY.from_int(2025001)
        >>> date.year
        2025
        """
        return cls.from_str(str(yyyydoy))

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
        return f"{self.year}{self.doy}"

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
        return datetime.datetime.combine(self.date, datetime.time.min)

    @property
    def gps_week(self) -> int:
        """
        GPS week number since GPS epoch (1980-01-06).
        
        Returns
        -------
        int
            GPS week number
            
        Examples
        --------
        >>> date = YYYYDOY.from_date(datetime.date(1980, 1, 6))
        >>> date.gps_week
        0
        """
        gps_start_date = datetime.date(1980, 1, 6)
        return (self.date - gps_start_date).days // 7

    @property
    def gps_day_of_week(self) -> int:
        """
        GPS day of week (0=Sunday, 6=Saturday).
        
        Returns
        -------
        int
            Day of week where 0=Sunday, 6=Saturday
            
        Examples
        --------
        >>> date = YYYYDOY.from_date(datetime.date(1980, 1, 6))  # Sunday
        >>> date.gps_day_of_week
        0
        """
        gps_start_date = datetime.date(1980, 1, 6)
        return (self.date - gps_start_date).days % 7

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
        return self.to_str() == other.to_str()

    def __lt__(self, other: "YYYYDOY") -> bool:
        """Less than comparison."""
        if not isinstance(other, YYYYDOY):
            return NotImplemented
        return self.date < other.date

    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        return hash(self.to_str())
