"""Date and time utilities for GNSS data processing."""

import datetime
from functools import total_ordering
from pathlib import Path

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
            return str(YYYYDOY.gpsweekday(date)[0])
    elif any(ext in str(file_name) for ext in ("TRO", "IONEX")):
        return str(file_name).split("_")[1][:4]

    msg = ("Invalid file type. The filename must end with "
           ".clk, clk_05s, .CLK, .SP3, .TRO, or .IONEX")
    raise ValueError(msg)


@total_ordering
@dataclass
class YYYYDOY:
    """Year and day-of-year (DOY) date representation.

    Used throughout canvodpy for GNSS data organization and file naming.

    Notes
    -----
    This is a Pydantic dataclass and uses ``total_ordering`` for comparisons.

    Attributes
    ----------
    year : int
        The year (e.g., 2025).
    doy : int
        Day of year (1-366).
    date : datetime.date
        Calculated calendar date.
    yydoy : str
        Short format (YYDDD, e.g., "25001").

    Examples
    --------
    >>> # From components
    >>> d = YYYYDOY(year=2025, doy=1)
    >>> d.to_str()
    '2025001'

    >>> # From date object
    >>> import datetime
    >>> d = YYYYDOY.from_date(datetime.date(2025, 1, 1))
    >>> d.doy
    '001'

    >>> # From string
    >>> d = YYYYDOY.from_str("2025001")
    >>> d.year
    2025

    >>> # From short string (YYDDD)
    >>> d = YYYYDOY.from_yydoy_str("25001")
    >>> d.to_str()
    '2025001'

    """

    year: int = Field(..., ge=1)
    doy: int = Field(..., ge=1, le=366)
    yydoy: str | None = None
    date: datetime.date | None = None

    def __post_init__(self) -> None:
        """Calculate derived fields after initialization.

        Returns
        -------
        None
        """
        self.date = self._calculate_date()
        self.doy = f"{self.doy:03}"
        self.yydoy = f"{str(self.year)[-2:]}{self.doy}"

    def __repr__(self) -> str:
        return (f"YYYYDOY(year={self.year}, doy={self.doy}, date={self.date}, "
                f"yydoy={self.yydoy}, gps_week={self.gps_week}, "
                f"gps_day_of_week={self.gps_day_of_week})")

    def __str__(self) -> str:
        return self.to_str()

    def __eq__(self, other: object) -> bool:
        """Equality based on date string."""
        if not isinstance(other, YYYYDOY):
            return False
        return self.to_str() == other.to_str()

    def __lt__(self, other: object) -> bool:
        """Less than comparison for sorting."""
        if not isinstance(other, YYYYDOY):
            return NotImplemented
        return self.date < other.date

    def __hash__(self) -> int:
        """Make hashable for use in sets and dicts."""
        return hash(self.to_str())

    def _calculate_date(self) -> datetime.date:
        """Calculate calendar date from year and DOY."""
        return datetime.date(self.year, 1,
                             1) + datetime.timedelta(days=int(self.doy) - 1)

    @staticmethod
    def _validate_doy(doy: int) -> None:
        """Validate day of year is in range [1, 366]."""
        if not 1 <= doy <= 366:
            raise ValueError(
                f"Day of year (DOY) must be in range [1, 366], got {doy}")

    @classmethod
    def from_date(cls, date: datetime.date) -> "YYYYDOY":
        """Create from datetime.date object.

        Parameters
        ----------
        date : datetime.date
            Calendar date

        Returns
        -------
        YYYYDOY
        """
        if isinstance(date, datetime.datetime):
            date = date.date()
        year = date.year
        doy = (date - datetime.date(year, 1, 1)).days + 1
        cls._validate_doy(doy)
        return cls(year=year, doy=doy)

    @classmethod
    def from_str(cls, yyyydoy: str | int) -> "YYYYDOY":
        """Create from YYYYDDD string.

        Parameters
        ----------
        yyyydoy : str or int
            Date in YYYYDDD format (e.g., "2025001" or 2025001)

        Returns
        -------
        YYYYDOY
        """
        if isinstance(yyyydoy, int):
            yyyydoy = str(yyyydoy)
        if len(yyyydoy) != 7:
            raise ValueError(
                f"Invalid format. Expected 'YYYYDDD', got '{yyyydoy}'")
        year = int(yyyydoy[:4])
        doy = int(yyyydoy[4:])
        cls._validate_doy(doy)
        jan_first = datetime.datetime(year, 1, 1)
        final_date = jan_first + datetime.timedelta(days=doy - 1)
        return cls.from_date(final_date.date())

    @classmethod
    def from_int(cls, yyyydoy: int) -> "YYYYDOY":
        """Create from YYYYDDD integer.

        Parameters
        ----------
        yyyydoy : int
            Date as integer (e.g., 2025001)

        Returns
        -------
        YYYYDOY
        """
        return cls.from_str(str(yyyydoy))

    @classmethod
    def from_yydoy_str(cls, yydoy: str) -> "YYYYDOY":
        """Create from YYDDD short string.

        Assumes current millennium (20XX).

        Parameters
        ----------
        yydoy : str
            Short date format (e.g., "25001" for 2025 DOY 001)

        Returns
        -------
        YYYYDOY
        """
        current_millennium = str(datetime.datetime.now().year)[0:2]
        return cls.from_str(f"{current_millennium}{yydoy}")

    def to_str(self) -> str:
        """Convert to YYYYDDD string.

        Returns
        -------
        str
            Date in YYYYDDD format (e.g., "2025001").

        """
        return f"{self.year}{self.doy}"

    @staticmethod
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
        """
        gps_start_date = datetime.date(1980, 1, 6)

        # Convert string to date if needed
        if not is_datetime and isinstance(input_date, str):
            input_date = datetime.datetime.strptime(input_date,
                                                    "%d-%m-%Y").date()
        elif isinstance(input_date, datetime.datetime):
            input_date = input_date.date()

        # Calculate weeks and days since GPS epoch
        return divmod((input_date - gps_start_date).days, 7)

    @property
    def gps_week(self) -> int:
        """GPS week number.

        Returns
        -------
        int
            GPS week number since GPS epoch (1980-01-06).
        """
        return self.gpsweekday(self.date)[0]

    @property
    def gps_day_of_week(self) -> int:
        """GPS day of week (0=Sunday, 6=Saturday).

        Returns
        -------
        int
            Day of week where 0=Sunday, 6=Saturday.
        """
        return self.gpsweekday(self.date)[1]


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
