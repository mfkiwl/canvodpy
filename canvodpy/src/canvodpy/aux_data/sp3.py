#%%
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import warnings

import numpy as np
from pint import Quantity
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
import xarray as xr

from canvodpy.aux_data.reader import AuxFile
from canvodpy.globals import UREG
from canvodpy.processor.interpolator import (
    Interpolator,
    Sp3Config,
    Sp3InterpolationStrategy,
)
from canvodpy.utils.date_time import get_gps_week_from_filename


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Sp3File(AuxFile):
    """
    Handler for SP3 (Standard Product 3) orbit files.

    This class provides functionality to read, parse, and process SP3 format files
    containing precise satellite orbit data. The data is stored in Earth-Centered
    Earth-Fixed (ECEF) coordinates and can be accessed with or without units.

    Currently only implemented for CODE agency's final & GFZ's rapid products with:
    - 01D (one day) coverage
    - 05M (5 minute) temporal resolution

    Attributes:
    ----------

    date: str
        String in YYYYDOY format representing the start date
    agency: str
        String identifying the analysis center (e.g., 'COD' for CODE)
    product_type: str
        String indicating product type ('final' or 'rapid')
    ftp_server: str
        String containing the base URL for file downloads
    local_dir: Path
        Path object pointing to local storage directory
    add_velocities: Optional[bool]
        Optional boolean to control whether velocity data is added, default is True
    dimensionless: Optional[bool]
        Optional boolean to control whether output has units attached, default is True
    """
    date: str
    agency: str
    product_type: str
    ftp_server: str
    local_dir: Path
    add_velocities: bool | None = True
    dimensionless: bool | None = True

    def __post_init__(self):
        """
        Initialize the SP3 file handler by setting up directories and file paths.

        This method runs after dataclass initialization to:
        1. Set the file type to 'orbit'
        2. Ensure the local directory exists
        3. Call the parent class initialization
        """
        self.file_type = ["orbit"]
        self.local_dir = Path(self.local_dir)
        self.local_dir.mkdir(parents=True, exist_ok=True)
        super().__post_init__()

    def get_interpolation_strategy(self) -> Interpolator:
        """Get the appropriate interpolation strategy for SP3 files."""
        config = Sp3Config(use_velocities=self.add_velocities,
                           fallback_method='linear')
        return Sp3InterpolationStrategy(config=config)

    def generate_filename_based_on_type(self) -> Path:
        """
        Generate the standard SP3 filename based on metadata.

        SP3 filenames follow the pattern:

        COD0MGXFIN_YYYYDOY0000_01D_05M_ORB.SP3.gz
        |--|-----|_|---------|_|-|_|-|_|--|---|--|
        |  |     | |         | | | | | |  |   |gz compression
        |  |     | |         | | | | | |  |SP3 format
        |  |     | |         | | | | | |ORB (orbit file)
        |  |     | |         | | | |Time resolution (05 minutes)
        |  |     | |         | |Duration (01 days)
        |  |     | |Time tag (year, day of year, hour from - to)
        |  |     |Product version
        |  |Analysis center (CODE)
        """

        product_prefix = {
            "final": "COD0MGXFIN",
            "rapid": "GFZ0MGXRAP",  # COD0OPSRAP
            "final_gfz": "GFZ0MGXFIN",
        }[self.product_type]

        return Path(f"{product_prefix}_{self.date}0000_01D_05M_ORB.SP3")

    # def download_aux_file(self) -> None:
    #     """
    #     Download SP3 file from the specified FTP server.

    #     The method:
    #     1. Generates the appropriate filename
    #     2. Calculates the GPS week for directory structure
    #     3. Constructs the full URL including intermediate directories
    #     4. Downloads and extracts the compressed file

    #     The file structure on the server is organized by GPS weeks, with
    #     different subdirectories based on the GPS week number.

    #     Raises:
    #     -------
    #     RuntimeError:
    #         If no downloader is configured
    #     ValueError:
    #         If the GPS week calculation fails
    #     """
    #     orbit_file = self.generate_filename_based_on_type()
    #     gps_week = get_gps_week_from_filename(orbit_file)

    #     # Determine intermediate directory based on GPS week
    #     intermediate_dir = ("" if int(gps_week) < 2038 else
    #                         "mgex" if int(gps_week) < 2247 else "")

    #     # Construct the full URL
    #     full_url = f"{self.ftp_server}/products/{gps_week}/{intermediate_dir}/{orbit_file}.gz"
    #     destination = self.local_dir / orbit_file

    #     # Use our integrated downloader
    #     self.download_file(full_url, destination)
    #     print(f"Downloaded orbit file for {self.agency} on date {self.date}")

    def download_aux_file(self) -> None:
        """
        Download SP3 file from the specified FTP server with fallback to NASA CDDIS.

        The method:
        1. Generates the appropriate filename
        2. Calculates the GPS week for directory structure
        3. Constructs the full URL including intermediate directories
        4. Attempts to download from primary server
        5. Falls back to NASA CDDIS if necessary

        Raises:
        -------
        RuntimeError:
            If file cannot be downloaded from any server
        ValueError:
            If the GPS week calculation fails
        """
        orbit_file = self.generate_filename_based_on_type()
        gps_week = get_gps_week_from_filename(orbit_file)

        # Determine intermediate directory based on GPS week
        intermediate_dir = ("" if int(gps_week) < 2038 else
                            "mgex" if int(gps_week) < 2247 else "")

        # Construct the full URL
        full_url = f"{self.ftp_server}/products/{gps_week}/{intermediate_dir}/{orbit_file}.gz"
        destination = self.local_dir / orbit_file

        # File info for NASA CDDIS URL construction
        file_info = {
            'gps_week': gps_week,
            'filename': orbit_file,
            'type': 'orbit',
            'agency': self.agency
        }

        try:
            # Use our enhanced downloader with NASA fallback
            self.download_file(full_url, destination, file_info)
            print(
                f"Downloaded orbit file for {self.agency} on date {self.date}")
        except Exception as e:
            raise RuntimeError(
                f"Failed to download SP3 file from all available servers: {str(e)}"
            )

    def read_file(self) -> xr.Dataset:
        """
        Read and parse SP3 file data into an xarray Dataset.

        This method implements an optimized single-pass reading strategy that:
        1. Collects epoch and satellite data efficiently using simple lists
        2. Pre-allocates numpy arrays for coordinate data
        3. Converts units in bulk for better performance
        4. Optionally strips units for dimensionless output

        Returns:
        -------
        xr.Dataset:
            Contains satellite positions with dimensions (epoch, sv)
            and coordinates for each satellite. Values are in meters.

        Raises:
        -------
        ValueError:
             If the file format is invalid or parsing fails
        FileNotFoundError:
             If the SP3 file cannot be opened
        """
        # Initialize simple lists for temporary storage
        epochs: list[datetime.datetime] = []
        epoch_data: list[tuple[Any]] = [
        ]  # Will store tuples of (epoch_index, sv_code, x, y, z)
        svs: set[str] = set()
        current_epoch = None
        current_epoch_idx: int = -1

        with open(self.fpath) as f:
            # Skip header until first epoch marker
            for line in f:
                if line.startswith('*'):
                    current_epoch = self._parse_epoch_line(line)
                    epochs.append(current_epoch)
                    current_epoch_idx += 1
                    break

            # Single pass through file with minimal processing
            for line in f:
                if line.startswith('*'):
                    current_epoch = self._parse_epoch_line(line)
                    epochs.append(current_epoch)
                    current_epoch_idx += 1

                elif line.startswith('P'):
                    # Parse only what we need
                    sv_code = line[1:4].strip()
                    svs.add(sv_code)

                    # Store raw coordinate data with epoch index
                    x = self._parse_coordinate(line[4:18])
                    y = self._parse_coordinate(line[18:32])
                    z = self._parse_coordinate(line[32:46])

                    # Store as simple tuple - much faster than nested dictionaries
                    epoch_data.append((
                        current_epoch_idx,
                        sv_code,
                        x if x is not None else
                        np.nan,  # Convert to meters immediately
                        y if y is not None else np.nan,
                        z if z is not None else np.nan))

                elif line.startswith('EOF'):
                    break

        # Create arrays only once with final dimensions
        sv_list = sorted(svs)
        sv_idx = {sv: i for i, sv in enumerate(sv_list)}
        shape = (len(epochs), len(sv_list))

        # Pre-allocate final arrays
        x_data = np.full(shape, np.nan)
        y_data = np.full(shape, np.nan)
        z_data = np.full(shape, np.nan)

        # Fill arrays directly from our simple list
        for epoch_idx, sv, x, y, z in epoch_data:
            j = sv_idx[sv]
            x_data[epoch_idx, j] = x
            y_data[epoch_idx, j] = y
            z_data[epoch_idx, j] = z

        x_data = (x_data * UREG.kilometer).to(UREG.meter)
        y_data = (y_data * UREG.kilometer).to(UREG.meter)
        z_data = (z_data * UREG.kilometer).to(UREG.meter)

        if self.dimensionless:
            x_data = x_data.magnitude
            y_data = y_data.magnitude
            z_data = z_data.magnitude

        # Create the dataset directly with data in meters
        ds = self._prepare_dataset(
            xr.Dataset(data_vars={
                'X': (('epoch', 'sv'), x_data),
                'Y': (('epoch', 'sv'), y_data),
                'Z': (('epoch', 'sv'), z_data)
            },
                       coords={
                           'epoch': np.array(epochs, dtype='datetime64[ns]'),
                           'sv': np.array(sv_list)
                       }))

        if self.add_velocities:
            ds = self.compute_velocity(ds)

        return ds

    def _parse_coordinate(self, coord_str: str) -> float | None:
        """
        Parse a coordinate field from an SP3 file, handling various format edge cases.

        The SP3 format specifies coordinates in a 14-character fixed-width field.
        However, some implementations may deviate from this standard by:
        - Omitting spaces between large numbers
        - Using different spacing around the decimal point
        - Using '999999.999999' to indicate missing or invalid data

        Parameters:
        ----------
        coord_str: str
            A 14-character string containing the coordinate value
            in the SP3 fixed-width format

        Returns:
        -------
        float or None:
            The parsed coordinate value in kilometers if valid,
            None if the value represents missing data

        Raises:
        -------
        ValueError:
            If the coordinate string cannot be parsed as a valid float

        Examples:
        --------
        >>> _parse_coordinate("  -11044.805800")
        -11044.805800
        >>> _parse_coordinate(" 999999.999999")
        None
        >>> _parse_coordinate("21929.418200  ")
        21929.418200
        """
        coord_str = coord_str.strip()
        if not coord_str or coord_str == '999999.999999':
            return None

        try:
            return float(coord_str)
        except ValueError:
            # Some SP3 files might have missing spaces between fields
            # Try to handle this case by finding the decimal point
            if '.' in coord_str:
                parts = coord_str.split('.')
                if len(parts) == 2:
                    integer_part = parts[0].replace(' ', '')
                    return float(f"{integer_part}.{parts[1]}")
            raise

    def _convert_to_meters(
            self, x_data: Quantity, y_data: Quantity,
            z_data: Quantity) -> tuple[Quantity, Quantity, Quantity]:
        """
        Convert coordinate arrays from kilometers to meters using Pint quantities.

        This method handles unit conversion in bulk for better performance.
        It ensures all coordinates are in consistent SI units (meters) for
        further processing.

        Parameters:
        ----------
        x_data: Quantity
            Array of X coordinates with units (typically kilometers)
        y_data: Quantity
            Array of Y coordinates with units (typically kilometers)
        z_data: Quantity
            Array of Z coordinates with units (typically kilometers)

        Returns:
        -------
        Tuple
            Tuple containing three arrays (x, y, z) converted to meters

        Note:
        -----
        This method expects input arrays to have units attached through
        the Pint library. The conversion is handled by Pint's unit conversion
        system.
        """
        x_data = x_data.to(UREG.meter)
        y_data = y_data.to(UREG.meter)
        z_data = z_data.to(UREG.meter)
        return x_data, y_data, z_data

    def _prepare_dataset(self, ds: xr.Dataset) -> xr.Dataset:
        """
        Prepare the xarray Dataset by adding metadata and variable attributes.

        This method enriches the dataset with:
        1. File-level metadata (source, agency, etc.)
        2. Variable-specific attributes (units, descriptions)
        3. Coordinate system information

        Parameters:
        ----------
        ds: xr.Dataset
            The raw xarray Dataset containing position data

        Returns:
        -------
        xr.Dataset
            The enhanced dataset with complete metadata

        Note:
        -----
        The metadata follows CF (Climate and Forecast) conventions where
            applicable to maintain compatibility with common data analysis tools.
        """

        # Add metadata
        ds.attrs = {
            'file': str(self.fpath.name),
            'agency': self.agency,
            'product_type': self.product_type,
            'ftp_server': self.ftp_server,
            'date': self.date,
        }
        # Add variable attributes
        for var, attrs in self._get_variable_attributes().items():
            if var in ds:
                ds[var].attrs = attrs

        return ds

    def _get_variable_attributes(self) -> dict[str, dict[str, str]]:
        """
        Define standardized attributes for each variable in the dataset.

        This method provides a consistent set of metadata for the X, Y, and Z
        coordinates, following both CF conventions and GNSS-specific standards.
        Each coordinate gets a complete set of attributes describing its:
        - Long name (human-readable description)
        - Standard name (for interoperability)
        - Units (SI units in meters)
        - Coordinate system information
        - Additional descriptive text

        Returns:
        -------
        Dict[str, Dict[str, str]]
            Nested dictionary containing attribute
            definitions for each coordinate variable

        Note:
        -----
        The attributes follow GNSS community conventions for describing
            ECEF coordinate system variables.
        """
        _variable_attributes = {
            'X': {
                'long_name':
                'x-coordinate in ECEF',
                'standard_name':
                r'x_{ECEF}',
                'short_name':
                'x',
                'units':
                'm',
                'axis':
                'x',
                'description':
                'x-coordinate in ECEF (Earth-Centered, Earth-Fixed) frame',
            },
            'Y': {
                'long_name':
                'y-coordinate in ECEF',
                'standard_name':
                r'y_{ECEF}',
                'short_name':
                'y',
                'units':
                'm',
                'axis':
                'y',
                'description':
                'y-coordinate in ECEF (Earth-Centered, Earth-Fixed) frame',
            },
            'Z': {
                'long_name':
                'z-coordinate in ECEF',
                'standard_name':
                r'z_{ECEF}',
                'short_name':
                'z',
                'units':
                'm',
                'axis':
                'z',
                'description':
                'z-coordinate in ECEF (Earth-Centered, Earth-Fixed) frame',
            },
        }

        return _variable_attributes

    def _parse_epoch_line(self, line: str) -> datetime.datetime:
        """
        Parse a timestamp from an SP3 epoch marker line.

        SP3 files mark each epoch with a line starting with '*' followed by
        the timestamp components (year, month, day, hour, minute, second).
        This method extracts these components and creates a datetime object.

        Parameters:
        ----------
        line: str
            A line from the SP3 file starting with '*' and containing
            space-separated timestamp components

        Returns:
        -------
        datetime.datetime
            The parsed timestamp

        Raises:
        -------
        ValueError
            If the line format is invalid or contains non-numeric values
        IndexError
            If the line doesn't contain enough fields

        Example:
        --------
        >>> _parse_epoch_line("* 2024 1 15 0 0 0.00000000")
            datetime.datetime(2024, 1, 15, 0, 0)
        """
        parts = line.split()
        return datetime.datetime(
            year=int(parts[1]),
            month=int(parts[2]),
            day=int(parts[3]),
            hour=int(parts[4]),
            minute=int(parts[5]),
            second=0,
        )

    # def compute_velocity(self, ds: xr.Dataset) -> xr.Dataset:
    #     """
    #     Compute velocity as the first derivative of position with respect to time
    #     using matrix operations, storing X, Y, Z as a single 3D vector.

    #     Parameters
    #     ----------
    #     ds : xr.Dataset
    #         Dataset with 'epoch' as a coordinate and 'X', 'Y', 'Z' as data variables
    #         with dimensions (epoch, sv).

    #     Returns
    #     -------
    #     xr.Dataset
    #         Dataset with position and velocity stored as 3D vectors.
    #     """
    #     # Ensure correct data format
    #     assert 'epoch' in ds.coords, "The dataset must have 'epoch' as a coordinate."
    #     assert ds[
    #         'epoch'].dtype == 'datetime64[ns]', "The 'epoch' coordinate must be of type datetime64[ns]."
    #     assert all(
    #         var in ds.data_vars
    #         for var in ['X', 'Y', 'Z']), "Missing X, Y, or Z data variables."

    #     # Convert 'epoch' to seconds relative to the first timestamp
    #     t = (ds['epoch'] - ds['epoch'].isel(epoch=0)
    #          ).astype(float) / 1e9  # Convert to seconds
    #     t_1d = t.values  # Ensure it's a 1D array of shape (epoch,)

    #     Vx = np.gradient(ds['X'].values, t_1d, axis=0)
    #     Vy = np.gradient(ds['Y'].values, t_1d, axis=0)
    #     Vz = np.gradient(ds['Z'].values, t_1d, axis=0)

    #     if not self.dimensionless:
    #         Vx = Vx * (UREG.meter / UREG.second)
    #         Vy = Vy * (UREG.meter / UREG.second)
    #         Vz = Vz * (UREG.meter / UREG.second)

    #     # Assign computed velocities back into the dataset
    #     ds = ds.assign(
    #         Vx=(('epoch', 'sv'), Vx),  # Extract X component of velocity
    #         Vy=(('epoch', 'sv'), Vy),  # Extract Y component of velocity
    #         Vz=(('epoch', 'sv'), Vz)  # Extract Z component of velocity
    #     )
    #     for var, attrs in {
    #             'Vx': {
    #                 'long_name': 'x-component of velocity',
    #                 'standard_name': 'v_x',
    #                 'short_name': 'v_x',
    #                 'units': 'm/s',
    #                 'axis': 'v_x'
    #             },
    #             'Vy': {
    #                 'long_name': 'y-component of velocity',
    #                 'standard_name': 'v_y',
    #                 'short_name': 'v_y',
    #                 'units': 'm/s',
    #                 'axis': 'v_y'
    #             },
    #             'Vz': {
    #                 'long_name': 'z-component of velocity',
    #                 'standard_name': 'v_z',
    #                 'short_name': 'v_z',
    #                 'units': 'm/s',
    #                 'axis': 'v_z'
    #             },
    #     }.items():
    #         if var in ds:
    #             ds[var].attrs = attrs

    #     return ds

    def compute_velocity(self, ds: xr.Dataset) -> xr.Dataset:
        """
        Compute satellite velocities from position data using central differences.

        This function is specifically designed for GNSS satellite velocity computation,
        taking into account the typical orbital characteristics and SP3 data sampling.

        Parameters
        ----------
        ds : xr.Dataset
            Dataset containing satellite positions with dimensions (epoch, sv)
            Must include 'X', 'Y', 'Z' coordinates in meters

        Returns
        -------
        xr.Dataset
            Original dataset augmented with 'Vx', 'Vy', 'Vz' velocity components
        """
        # First, calculate our time step in seconds
        # SP3 files typically have 300-second (5-minute) intervals
        time_diffs = np.diff(ds['epoch'].values)
        dt = np.median(time_diffs).astype('timedelta64[s]').astype(float)

        # Initialize velocity arrays
        # We use the same shape as our position data
        # Compute velocities with explicit time step
        Vx = np.zeros_like(ds['X'].values)
        Vy = np.zeros_like(ds['Y'].values)
        Vz = np.zeros_like(ds['Z'].values)

        # Central difference with explicit dt
        Vx[1:-1] = (ds['X'].values[2:] - ds['X'].values[:-2]) / (2 * dt)
        Vy[1:-1] = (ds['Y'].values[2:] - ds['Y'].values[:-2]) / (2 * dt)
        Vz[1:-1] = (ds['Z'].values[2:] - ds['Z'].values[:-2]) / (2 * dt)

        # Add validation
        velocity_magnitude = np.sqrt(Vx**2 + Vy**2 + Vz**2)
        mean_velocity = np.mean(velocity_magnitude)
        print(f"Mean velocity magnitude: {mean_velocity:.2f} m/s")

        # Handle endpoints using forward and backward differences
        # First point - forward difference
        Vx[0] = (ds['X'].values[1] - ds['X'].values[0]) / dt
        Vy[0] = (ds['Y'].values[1] - ds['Y'].values[0]) / dt
        Vz[0] = (ds['Z'].values[1] - ds['Z'].values[0]) / dt

        # Last point - backward difference
        Vx[-1] = (ds['X'].values[-1] - ds['X'].values[-2]) / dt
        Vy[-1] = (ds['Y'].values[-1] - ds['Y'].values[-2]) / dt
        Vz[-1] = (ds['Z'].values[-1] - ds['Z'].values[-2]) / dt

        # Add quality checks specific to GNSS satellites
        velocity_magnitude = np.sqrt(Vx**2 + Vy**2 + Vz**2)
        expected_velocity = 3874  # meters per second (typical GPS satellite velocity)
        tolerance = 1000  # meters per second

        questionable_velocities = np.abs(velocity_magnitude -
                                         expected_velocity) > tolerance
        if np.any(questionable_velocities):
            warnings.warn(
                f"Found {np.sum(questionable_velocities)} velocities that deviate "
                f"significantly from typical GNSS orbital velocities")

        if not self.dimensionless:
            Vx = Vx * (UREG.meter / UREG.second)
            Vy = Vy * (UREG.meter / UREG.second)
            Vz = Vz * (UREG.meter / UREG.second)

        # Add the computed velocities to the dataset
        ds = ds.assign(Vx=(('epoch', 'sv'), Vx),
                       Vy=(('epoch', 'sv'), Vy),
                       Vz=(('epoch', 'sv'), Vz))

        for var, attrs in {
                'Vx': {
                    'long_name': 'x-component of velocity',
                    'standard_name': 'v_x',
                    'short_name': 'v_x',
                    'units': 'm/s',
                    'axis': 'v_x',
                    'computation_method': 'central_difference',
                    'time_step': float(dt),
                    'reference_frame': 'ECEF'  # Earth-Centered, Earth-Fixed
                },
                'Vy': {
                    'long_name': 'y-component of velocity',
                    'standard_name': 'v_y',
                    'short_name': 'v_y',
                    'units': 'm/s',
                    'axis': 'v_y',
                    'computation_method': 'central_difference',
                    'time_step': float(dt),
                    'reference_frame': 'ECEF'  # Earth-Centered, Earth-Fixed
                },
                'Vz': {
                    'long_name': 'z-component of velocity',
                    'standard_name': 'v_z',
                    'short_name': 'v_z',
                    'units': 'm/s',
                    'axis': 'v_z',
                    'computation_method': 'central_difference',
                    'time_step': float(dt),
                    'reference_frame': 'ECEF'  # Earth-Centered, Earth-Fixed
                },
        }.items():
            if var in ds:
                ds[var].attrs = attrs

        return ds


# Usage example
if __name__ == "__main__":
    sp3_file = Sp3File.from_datetime_date(
        date=datetime.date(2023, 9, 11),
        agency="GFZ",
        product_type="final",
        ftp_server="ftp://gssc.esa.int/gnss",
        local_dir=Path("/tmp/tmpfiles"),
    )
    sp3_file = Sp3File.from_datetime_date(
        date=datetime.date(2023, 9, 12),
        agency="GFZ",
        product_type="rapid",
        ftp_server="ftp://gssc.esa.int/gnss",
        local_dir=Path("/tmp/tmpfiles"),
    )

    sp3_file = Sp3File.from_datetime_date(
        date=datetime.date(2023, 9, 11),
        agency="COD",
        product_type="final",
        ftp_server="ftp://gssc.esa.int/gnss",
        local_dir=Path("/tmp/tmpfiles"),
    )
    sp3_file = Sp3File.from_datetime_date(
        date=datetime.date(2023, 9, 12),
        agency="COD",
        product_type="rapid",
        ftp_server="ftp://gssc.esa.int/gnss",
        local_dir=Path("/tmp/tmpfiles"),
    )

    # print(sp3_file.data)
    # dsout = sp3_file.data.resample(epoch='1min').interpolate('linear')
    # dsout.to_netcdf('/tmp/tmpfiles/orbit.nc')

    sp3_path = Path(
        '/home/nbader/shares/climers/Studies/GNSS_Vegetation_Study/05_data/01_Rosalia/00_aux_files/01_SP3/COD0MGXFIN_20241880000_01D_05M_ORB.SP3'
    )

    sp31 = Sp3File.from_file(sp3_path)
    sp32 = Sp3File.from_file(sp3_path,
                             dimensionless=False,
                             add_velocities=True)
    sp33 = Sp3File.from_file(sp3_path, add_velocities=True)
