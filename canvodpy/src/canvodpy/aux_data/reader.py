from abc import ABC, abstractmethod
import datetime
from pathlib import Path
from typing import Any, Optional

from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass
import xarray as xr

from canvodpy.aux_data.container import FileDownloader, FtpDownloader
from canvodpy.error_handling.error_handling import FileNotExistError
from canvodpy.processor.interpolator import Interpolator
from canvodpy.utils.date_time import YYYYDOY


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class AuxFile(ABC):
    """
    Abstract base class for GNSS auxiliary files (SP3, CLK, IONEX, etc.).

    This class provides two ways to create instances:
    1. from_datetime_date(): Create from a datetime.date object and metadata
    2. from_file(): Create directly from an existing file path

    The class handles both newly downloaded files and existing local files,
    maintaining consistent behavior regardless of how the instance is created.

    FTP Server Configuration:
    ------------------------
    - user_email: Optional email for NASA CDDIS authentication
      - If None: Uses ESA FTP server exclusively (no authentication required)
      - If provided: Enables NASA CDDIS as fallback server (requires registration)
      - To enable CDDIS, set CDDIS_MAIL environment variable
    """
    date: str
    agency: str
    product_type: str
    ftp_server: str
    local_dir: Path
    file_type: list[str] = Field(default_factory=list)
    fpath: Path | None = None
    user_email: Optional[
        str] = None  # Optional email for NASA CDDIS authentication
    downloader: FileDownloader | None = None
    _data: xr.Dataset | None = Field(default=None, init=False)

    def __post_init__(self):
        """Initialize after dataclass creation, setting up paths and checking file existence."""
        if not self.file_type:
            self.file_type = ["unknown"]
        self.local_dir = Path(self.local_dir)
        self.local_dir.mkdir(parents=True, exist_ok=True)

        # Initialize downloader if not provided
        if self.downloader is None:
            self.downloader = FtpDownloader(user_email=self.user_email)

        self.fpath = self.check_file_exists()

    @classmethod
    def from_datetime_date(cls, date: datetime.date, agency: str,
                           product_type: str, ftp_server: str, local_dir: Path,
                           **kwargs: Any) -> "AuxFile":
        """
        Create an AuxFile instance from a datetime.date object.

        This method converts a standard Python date object into the YYYYDOY format
        required for GNSS file naming conventions. It provides a convenient way to
        create instances when working with standard datetime objects.

        Args:
            date: A datetime.date object representing the desired date
            agency: Agency providing the data (e.g., 'COD', 'IGS')
            product_type: Type of product ('final', 'rapid', 'ultrarapid')
            ftp_server: Base URL for file downloads
            local_dir: Directory for storing files locally

        Returns:
            A new instance of the AuxFile subclass

        Example:
            aux_file = Sp3File.from_datetime_date(
                date=datetime.date(2024, 1, 15),
                agency="COD",
                product_type="final",
                ftp_server="ftp://example.com",
                local_dir=Path("/data")
            )
        """
        yyyydoy = YYYYDOY.from_date(date=date).to_str()
        return cls(
            date=yyyydoy,
            agency=agency,
            product_type=product_type,
            ftp_server=ftp_server,
            local_dir=local_dir,
            **kwargs,
        )

    @classmethod
    def from_file(cls, fpath: Path, **kwargs: Any) -> "AuxFile":
        """
        Create an AuxFile instance from an existing file path.

        This method extracts necessary metadata from the filename, following standard
        GNSS file naming conventions. It's useful when working with existing files
        where you don't need to download anything.

        The method parses the filename to extract:
        - Agency (first 3 characters)
        - Date in YYYYDOY format (from the second segment after splitting on '_')

        Args:
            fpath: Path to the existing GNSS file

        Returns:
            A new instance of the AuxFile subclass

        Raises:
            FileNotFoundError: If the specified file doesn't exist

        Example:
            aux_file = Sp3File.from_file(Path("/data/COD0MGXFIN_20241880000_01D_05M_ORB.SP3"))
        """
        if not fpath.exists():
            raise FileNotFoundError(f"File not found: {fpath}")

        # Extract metadata from filename
        fname = fpath.name
        agency = fname[0:3]  # First 3 characters are the agency code

        # Parse the date portion (YYYYDOY)
        yyyydoy = fname.split("_")[1][0:7]  # Get YYYYDOY from filename

        # Create instance with extracted metadata
        return cls(
            date=yyyydoy,  # Date extracted from filename
            agency=agency,  # Agency code from filename
            product_type="final",  # Default to 'final' for existing files
            ftp_server="N/A",  # No FTP needed for local files
            local_dir=fpath.parent,  # Use the file's directory
            fpath=fpath,  # Provide the full path
            **kwargs)

    def download_file(self,
                      url: str,
                      destination: Path,
                      file_info: dict | None = None) -> Path:
        """
        Download a file using the configured downloader.

        Args:
            url: URL to download from
            destination: Path to save the file
            file_info: Additional information about the file for alternative server URLs

        Returns:
            Path to the downloaded file

        Raises:
            RuntimeError: If no downloader is configured
        """
        if self.downloader is None:
            raise RuntimeError("No downloader configured")
        return self.downloader.download(url, destination, file_info)

    @abstractmethod
    def read_file(self) -> xr.Dataset:
        """
        Read and parse the auxiliary file.
        Must be implemented by subclasses to handle specific file formats.
        """
        pass

    @abstractmethod
    def get_interpolation_strategy(self) -> Interpolator:
        """
        Get the appropriate interpolation strategy for this file type.

        Returns
        -------
        InterpolationStrategy
            The strategy object that knows how to interpolate this type of data

        Notes
        -----
        Each derived class must implement this method to return its specific
        interpolation strategy.
        """
        pass

    @property
    def data(self) -> xr.Dataset:
        """
        Access the file's data, loading it if necessary.
        Implements lazy loading to conserve memory.
        """
        if self._data is None:
            self._data = self.read_file()
            # Store the interpolation strategy configuration
            strategy = self.get_interpolation_strategy()
            self._data.attrs['interpolator_config'] = strategy.to_attrs()
        return self._data

    def check_file_exists(self) -> Path:
        """
        Verify file exists locally or download it if needed.
        Returns the path to the local file.
        """
        filename = self.generate_filename_based_on_type()
        file_path = self.local_dir / filename
        if not file_path.exists():
            print(f"File {file_path} does not exist. Downloading...")
            self.download_aux_file()
        else:
            print(f"File {file_path} exists.")
        return file_path

    @abstractmethod
    def generate_filename_based_on_type(self) -> Path:
        """
        Generate the appropriate filename for this type of auxiliary file.
        Must be implemented by subclasses to handle specific naming conventions.
        """
        pass

    @abstractmethod
    def download_aux_file(self) -> None:
        """
        Download the auxiliary file from the specified FTP server.
        Must be implemented by subclasses to handle specific download requirements.
        """
        pass
