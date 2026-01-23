#%%
import datetime
from pathlib import Path
from typing import Optional, Set

import numpy as np
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
import xarray as xr

from canvodpy.aux_data.reader import AuxFile
from canvodpy.globals import UREG
from canvodpy.processor.interpolator import (
    ClockConfig,
    ClockInterpolationStrategy,
    Interpolator,
)
from canvodpy.utils.date_time import get_gps_week_from_filename

# @dataclass(config=ConfigDict(arbitrary_types_allowed=True))
# class ClkFile(AuxFile):
#     date: str
#     agency: str
#     product_type: str
#     ftp_server: str
#     local_dir: Path

#     def __post_init__(self):
#         self.file_type = ["clock"]
#         self.local_dir = Path(self.local_dir)
#         self.local_dir.mkdir(parents=True, exist_ok=True)
#         super().__post_init__()

#     @cls_timer(msg="\nRead CLK file {attr_value}", attr="fpath")
#     def read_file(self) -> Dict[str, Union[pd.DataFrame, xr.Dataset]]:
#         """Read Clock file, taken from V. Humphrey's code"""
#         with open(self.fpath) as f:
#             clk = f.readlines()
#             line = 0
#             prnlist = []
#             while True:
#                 if "OF SOLN SATS" not in clk[line]:
#                     del clk[line]
#                 else:
#                     noprn = int(clk[line][4:6])
#                     line += 1
#                     break
#             while True:
#                 if "PRN LIST" in clk[line]:
#                     prnlist.extend(clk[line])
#                     prnlist = "".join(prnlist)
#                     prnlist = prnlist.split()
#                     prnlist.remove("PRN")
#                     prnlist.remove("LIST")
#                     line += 1
#                 else:
#                     break
#             sv = []
#             for a in range(0, len(prnlist[0]), 3):
#                 sv.extend([prnlist[0][a:a + 3]])

#             if len(prnlist) > 1:
#                 sv.extend(prnlist[1:])

#             line = 0
#             while True:
#                 if "END OF HEADER" not in clk[line]:
#                     line += 1
#                 else:
#                     del clk[0:line + 1]
#                     break

#             timelist = []
#             for i in range(len(clk)):
#                 if clk[i][0:2] == "AS":
#                     timelist.append(clk[i].split())
#             Sat = []
#             Epochlist = []
#             SVtime = []
#             for i in range(len(timelist)):
#                 Sat.append(timelist[i][1])
#                 Epochlist.append((datetime.datetime(
#                     year=int(timelist[i][2]),
#                     month=int(timelist[i][3]),
#                     day=int(timelist[i][4]),
#                     hour=int(timelist[i][5]),
#                     minute=int(timelist[i][6]),
#                     second=int(float(timelist[i][7])),
#                 )))
#                 SVtime.append(float(timelist[i][9]))
#             SVTimelist = pd.DataFrame(list(zip(Sat, Epochlist, SVtime)),
#                                       columns=["sv", "epoch", "DeltaTSV"])
#             SVTimelist.set_index("sv", inplace=True)
#             SVTimelist.set_index("epoch", append=True, inplace=True)
#             SVTimelist = SVTimelist.reorder_levels(["epoch", "sv"])

#             ds = xr.Dataset.from_dataframe(SVTimelist)

#         return {"df": SVTimelist, "ds": ds}


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class ClkFile(AuxFile):
    """
    Handler for GNSS clock files in CLK format.

    This class reads and processes clock offset files containing satellite clock
    corrections. It handles the parsing of CLK format files and provides the data
    in both xarray Dataset format for analysis.

    Currently implemented for CODE agency products with support for:
    - 30-second sampling rate
    - Daily files (01D coverage)
    - Final and rapid products

    Attributes:
        date: String in YYYYDOY format representing the start date
        agency: String identifying the analysis center (e.g., 'COD' for CODE)
        product_type: String indicating product type ('final' or 'rapid')
        ftp_server: String containing the base URL for file downloads
        local_dir: Path object pointing to local storage directory
        dimensionless: Optional boolean to control whether output has units attached
    """
    date: str
    agency: str
    product_type: str
    ftp_server: str
    local_dir: Path
    dimensionless: bool | None = True

    def __post_init__(self) -> None:
        """
        Initialize the CLK file handler by setting up directories and file paths.

        This method runs after dataclass initialization to:
        1. Set the file type to 'clock'
        2. Ensure the local directory exists
        3. Call the parent class initialization
        """
        self.file_type = ["clock"]
        self.local_dir = Path(self.local_dir)
        self.local_dir.mkdir(parents=True, exist_ok=True)
        super().__post_init__()

    def get_interpolation_strategy(self) -> Interpolator:
        """Get the appropriate interpolation strategy for clock files."""
        config = ClockConfig(window_size=9, jump_threshold=1e-6)
        return ClockInterpolationStrategy(config=config)

    def generate_filename_based_on_type(self) -> Path:
        """
        Generate the standard CLK filename based on metadata.

        The method creates filenames following the CLK naming convention:
        COD0MGXFIN_YYYYDOY0000_01D_30S_CLK.CLK
        where:
        - COD0MGXFIN indicates final products from CODE
        - YYYYDOY is the year and day of year
        - 01D indicates daily file
        - 30S indicates 30-second sampling
        - CLK.CLK indicates clock file format

        Returns:
            Path: Complete filename constructed according to CLK conventions

        Raises:
            KeyError: If the product_type is not 'final' or 'rapid'
        """
        product_prefix = {
            "final": "COD0MGXFIN",
            "rapid": "GFZ0MGXRAP",  #COD0OPSRAP
        }[self.product_type]

        return Path(f"{product_prefix}_{self.date}0000_01D_30S_CLK.CLK")

    def download_aux_file(self) -> None:
        """
        Download CLK file from the specified FTP server with fallback to NASA CDDIS.

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
        clock_file = self.generate_filename_based_on_type()
        gps_week = get_gps_week_from_filename(clock_file)

        # Determine intermediate directory based on GPS week
        intermediate_dir = ("" if int(gps_week) < 2038 else
                            "mgex" if int(gps_week) < 2247 else "")

        # Construct the full URL
        full_url = f"{self.ftp_server}/products/{gps_week}/{intermediate_dir}/{clock_file}.gz"
        destination = self.local_dir / clock_file

        # File info for NASA CDDIS URL construction
        file_info = {
            'gps_week': gps_week,
            'filename': clock_file,
            'type': 'clock',
            'agency': self.agency
        }

        try:
            # Use our enhanced downloader with NASA fallback
            self.download_file(full_url, destination, file_info)
            print(
                f"Downloaded clock file for {self.agency} on date {self.date}")
        except Exception as e:
            raise RuntimeError(
                f"Failed to download CLK file from all available servers: {str(e)}"
            )

    def read_file(self) -> xr.Dataset:
        """
        Read and parse CLK file data into an xarray Dataset.

        This method implements a two-pass reading strategy:
        1. First pass collects all satellites and epochs that appear in the data
        2. Second pass fills the data arrays with clock offsets

        This approach ensures we don't miss any satellites, even if they aren't
        listed in the header, and handles cases where satellites might appear
        or disappear during the time period.

        Returns:
            xarray.Dataset: Contains clock offsets with dimensions (epoch, sv)
                        Values are in microseconds
        """
        # First pass: collect all epochs and satellites
        epochs = []
        satellites = set()
        clock_records = []
        current_epoch = None

        with open(self.fpath) as f:
            # Skip header
            for line in f:
                if 'END OF HEADER' in line:
                    break

            # Process data records
            for line in f:
                if line.startswith('AS'):
                    parts = line.split()

                    # Parse epoch
                    epoch = datetime.datetime(year=int(parts[2]),
                                              month=int(parts[3]),
                                              day=int(parts[4]),
                                              hour=int(parts[5]),
                                              minute=int(parts[6]),
                                              second=int(float(parts[7])))

                    # Store unique epochs and satellites
                    if epoch != current_epoch:
                        current_epoch = epoch
                        epochs.append(epoch)

                    sv_code = parts[1]
                    satellites.add(sv_code)

                    # Store the complete record
                    clock_offset = float(parts[9])  # microseconds
                    clock_records.append((epoch, sv_code, clock_offset))

        # Create lookup dictionaries for efficient indexing
        epoch_idx = {epoch: i for i, epoch in enumerate(epochs)}
        sv_list = sorted(satellites)
        sv_idx = {sv: i for i, sv in enumerate(sv_list)}

        # Pre-allocate array with known dimensions
        shape = (len(epochs), len(sv_list))
        clock_offsets = np.full(shape, np.nan)

        # Fill array using collected records
        for epoch, sv, offset in clock_records:
            i = epoch_idx[epoch]
            j = sv_idx[sv]
            clock_offsets[i, j] = offset

        clock_offsets = (UREG.microsecond * clock_offsets).to('s')

        if self.dimensionless:
            clock_offsets = clock_offsets.magnitude

        # Create dataset
        ds = xr.Dataset(
            data_vars={'clock_offset': (('epoch', 'sv'), clock_offsets)},
            coords={
                'epoch': np.array(epochs, dtype='datetime64[ns]'),
                'sv': np.array(sv_list)
            })

        return self._prepare_dataset(ds)

    def _parse_header(self, file_handle) -> set[str]:
        """
        Parse the CLK file header to extract the list of satellites.

        Args:
            file_handle: Open file object positioned at the start

        Returns:
            Set[str]: Set of satellite identifiers (e.g., 'G01', 'R01')

        Raises:
            ValueError: If the header format is invalid
        """
        satellites = set()

        for line in file_handle:
            if 'OF SOLN SATS' in line:
                num_sats = int(line[4:6])
            elif 'PRN LIST' in line:
                # Parse PRN list line(s)
                parts = line.split()[2:]  # Skip 'PRN' and 'LIST'
                for prn in parts:
                    if len(prn) == 3:  # Valid PRN format (e.g., G01)
                        satellites.add(prn)
            elif 'END OF HEADER' in line:
                break

        return satellites

    def _prepare_dataset(self, ds: xr.Dataset) -> xr.Dataset:
        """Add metadata and attributes to the dataset."""
        ds.attrs = {
            'file': str(self.fpath.name),
            'agency': self.agency,
            'product_type': self.product_type,
            'ftp_server': self.ftp_server,
            'date': self.date,
        }

        # Add variable attributes
        ds.clock_offset.attrs = {
            'long_name': 'Satellite clock offset',
            'standard_name': 'clock_offset',
            'units': 'seconds',
            'description': 'Clock correction for each satellite'
        }

        return ds


# Usage example
if __name__ == "__main__":
    clk_file = ClkFile.from_datetime_date(
        date=datetime.date(2024, 9, 1),
        agency="COD",
        product_type="final",
        ftp_server="ftp://gssc.esa.int/gnss",
        local_dir=Path("/tmp/tmpfiles"),
    )
    clk_file.data
    # dsout = sp3_file.data.resample(epoch='1min').interpolate('linear')
    # dsout.to_netcdf('/tmp/tmpfiles/orbit.nc')
