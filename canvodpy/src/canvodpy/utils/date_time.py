import datetime
from functools import total_ordering
from pathlib import Path
from typing import Optional, Tuple, Union

from pydantic import Field
from pydantic.dataclasses import dataclass


def get_gps_week_from_filename(file_name: Path):
    """
    Extracts the GPS week from various GNSS product filenames.
    """
    if file_name.suffix in [".clk", ".clk_05s", ".CLK", ".sp3", ".SP3"]:
        return (str(file_name)[3:-7] if file_name.suffix == ".clk" else str(
            gpsweekday(
                datetime.datetime.strptime(
                    str(file_name).split("_")[1], "%Y%j%H%M").date())[0]))
    elif any(ext in str(file_name) for ext in ("TRO", "IONEX")):
        return str(file_name).split("_")[1][:4]
    raise Warning(
        "Invalid file type. The filename must end with .clk, clk_05s, .CLK, .SP3, .TRO, or .IONEX"
    )


def gpsweekday(input_date: datetime.datetime | str,
               is_datetime: bool | None = False) -> tuple[int, int]:
    """
    Calculate the GPS week number and day of week from a given date.

    Parameters
    ----------
    input_date : datetime.datetime or str
        The date to calculate the GPS week number and day of week from.

    is_datetime : bool, optional
        Whether the input date is a datetime.datetime object. Default is False.

    Returns
    -------
    Tuple[int, int]
        The GPS week number and day of week.
    """
    gps_start_date = datetime.date(1980, 1, 6)
    if not is_datetime and isinstance(input_date, str):
        input_date = datetime.datetime.strptime(input_date, "%d-%m-%Y").date()

    return divmod((input_date - gps_start_date).days, 7)


@dataclass
class YYDOY:

    @classmethod
    def from_str(cls, yydoy: str) -> "YYYYDOY":
        date_str = f"20{yydoy}"
        return YYYYDOY.from_str(date_str)


@total_ordering
@dataclass
class YYYYDOY:
    """
    Small dataclass to handle year and day of year (DOY) dates.

    Parameters
    ----------
    year : int
        The year.

    doy : int
        The day of year (DOY).

    date : datetime.datetime
        The calculated date from the year and DOY.
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
        return (
            f"YYYYDOY(year={self.year}, doy={self.doy}, date={self.date}, " +
            f"yydoy={self.yydoy}, gps_week={self.gps_week}, " +
            f"gps_day_of_week={self.gps_day_of_week})")

    def __str__(self) -> str:
        return (
            f"YYYYDOY(year={self.year}, doy={self.doy}, date={self.date}, " +
            f"yydoy={self.yydoy}, gps_week={self.gps_week}, " +
            f"gps_day_of_week={self.gps_day_of_week})")

    def __eq__(self, other):
        """Define equality based on date string."""
        if not isinstance(other, YYYYDOY):
            return False
        return self.to_str() == other.to_str()

    def __lt__(self, other):
        """Less than comparison for sorting."""
        if not isinstance(other, YYYYDOY):
            return NotImplemented
        return self.date < other.date

    def __hash__(self):
        """Make YYYYDOY hashable for use in sets."""
        return hash(self.to_str())

    def _calculate_date(self):
        return datetime.date(self.year, 1,
                             1) + datetime.timedelta(days=self.doy - 1)

    def _validate_doy(doy):
        if not 1 <= doy <= 366:
            # doy < 1 or doy > 366:
            raise ValueError(
                f"Day of year (DOY) must be between in the interval [1, 366], but got {doy}"
            )

    @classmethod
    def from_date(cls, date: datetime.date) -> 'YYYYDOY':
        if isinstance(date, datetime.datetime):
            date = date.date()
        year = date.year
        doy = (date - datetime.date(year, 1, 1)).days + 1
        cls._validate_doy(doy)
        return cls(year=year, doy=doy)

    @classmethod
    def from_str(cls, yyyydoy: str) -> "YYYYDOY":
        if isinstance(yyyydoy, int):
            yyyydoy = str(yyyydoy)
        if len(yyyydoy) != 7:
            raise ValueError(
                f"Invalid date format. Expected 'YYYYDOY', but got '{yyyydoy}'"
            )
        year = int(yyyydoy[:4])
        doy = int(yyyydoy[4:])
        cls._validate_doy(doy)
        jan_first = datetime.datetime(year, 1, 1)

        final_date = jan_first + datetime.timedelta(days=doy - 1)
        date = final_date.date()
        return cls.from_date(date)

    @classmethod
    def from_int(cls, yyyydoy: int) -> "YYYYDOY":
        return cls.from_str(str(yyyydoy))

    @classmethod
    def from_yydoy_str(cls, yydoy: str) -> "YYYYDOY":
        current_millenium = str(datetime.datetime.now().year)[0:2]
        return cls.from_str(f"{current_millenium}{yydoy}")

    def to_str(self):
        return f"{self.year}{self.doy}"

    def _gpsweekday(self) -> tuple[int, int]:
        """
        Calculate the GPS week number and day of week from a  `datetime.date`.

        Parameters
        ----------
        input_date : datetime.datetime or str
            The date to calculate the GPS week number and day of week from.

        is_datetime : bool, optional
            Whether the input date is a datetime.datetime object. Default is False.

        Returns
        -------
        Tuple[int, int]
            The GPS week number and day of week.
        """
        gps_start_date = datetime.date(1980, 1, 6)

        return divmod((self.date - gps_start_date).days, 7)

    @property
    def gps_week(self) -> int:
        return self._gpsweekday()[0]

    @property
    def gps_day_of_week(self) -> int:
        return self._gpsweekday()[1]


if __name__ == "__main__":
    dd1 = YYYYDOY(year=2022, doy=100)
    print(dd1.yydoy)
    dd2 = YYYYDOY.from_date(datetime.datetime(2022, 4, 10))
    print(dd2)
    dd3 = YYYYDOY.from_str(2022010)
    print(dd3)
    dd3 = YYYYDOY.from_str("2022011")
    print(dd3)
    dd3 = YYYYDOY.from_int(2022012)
    print(dd3)
    dd3 = YYYYDOY.from_yydoy_str("24245")
    print(dd3)
