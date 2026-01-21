from collections.abc import Callable, Generator
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
import os
from pathlib import Path
from typing import Dict, Iterator, List

from natsort import natsorted
from pydantic.dataclasses import dataclass

from canvod.store import GnssResearchSite
from canvodpy.utils.date_time import YYYYDOY
from canvodpy.validation_models.validators import (
    RinexFilesPresentValidator,
    YYDOYValidator,
)


@dataclass(frozen=True)
class MatchedDirs:
    '''
    Immutable container class to store matched directory paths\
        of canopy and sky data as well as the corresponding `YYYYDOY` object.

    Parameters:
    ----------
    canopy_data_dir: Path
        Path to the canopy data directory.
    sky_data_dir: Path
        Path to the sky data directory.
    yyyydoy: YYYYDOY
        `YYYYDOY` object corresponding to the matched directories
    '''
    canopy_data_dir: Path
    sky_data_dir: Path
    yyyydoy: YYYYDOY


@dataclass(kw_only=True)
class DataDirMatcher:
    """
    Iterable, immutable class to handle directories for GNSS data processing.
    This class is used to match directories of both sky and canopy data.

    Iterating over this class will yield a `MatchedDirs` dataclass containing
    the matched directories of canopy and sky data.
    """
    site: str = "01_Rosalia"

    sky_dir_pattern: Path = Path("01_reference/01_GNSS/01_raw")
    canopy_dir_pattern: Path = Path("02_canopy/01_GNSS/01_raw")

    def __post_init__(self):
        # Validate root and subdirectories exist
        _root: Path = Path(
            os.getenv(
                "GNSS_ROOT_DIR",
                Path(
                    '/home/nbader/shares/climers/Studies/GNSS_Vegetation_Study/05_data/'
                )))

        self.root = self._validate_dir_exists(Path(_root) / self.site)

        self.sky_dir = self._validate_dir_exists(self.root /
                                                 self.sky_dir_pattern)
        self.canopy_dir = self._validate_dir_exists(self.root /
                                                    self.canopy_dir_pattern)

    def __iter__(self) -> Generator["MatchedDirs"]:
        """
        Iterate over the matched data directories of both canopy and sky data.

        Yields:
        -------
            `MatchedDirs`: A dataclass containing the matched directories of
                canopy and sky data.
        """
        for d in self.dirs_with_rnx_files_parallel():
            yield MatchedDirs(
                canopy_data_dir=self.get_data_root_dir("canopy") / d,
                sky_data_dir=self.get_data_root_dir("sky") / d,
                yyyydoy=YYYYDOY.from_yydoy_str(d),
            )

    @classmethod
    def from_root(cls, pth: Path) -> "DataDirMatcher":
        """Create a new instance of the class from a root directory."""
        return cls(root=pth)

    def get_data_root_dir(self, data_type: str) -> Path:
        """
        Get the root directory for a given data type (sky or canopy).

        Parameters:
        ----------
        data_type : str
            "sky" for sky data, "canopy" for canopy data.

        Returns:
        -------
            Path: The root directory for the specified data type.
        """
        dir_map = {
            "sky": self.sky_dir_pattern,
            "canopy": self.canopy_dir_pattern,
        }

        if data_type not in dir_map:
            raise ValueError(
                f"Invalid data type: {data_type}. Must be 'sky' or 'canopy'.")

        return self._validate_dir_exists(self.root / dir_map[data_type])

    def _validate_dir_exists(self, path: Path) -> Path:
        """
        Validate if a directory exists, raising an error if not.

        Parameters:
        ----------
        path : Path
            The directory path to check.

        Returns:
        -------
            Path: The validated path.
        """
        if not path.exists():
            raise FileNotFoundError(f"Directory does not exist: {path}")
        return path

    def get_dirs(self, data_type: str) -> list[Path]:
        """
        Get sorted list of directories for a given data type.

        Parameters:
        ----------
        data_type : str
            "sky" for sky data, "canopy" for canopy data.

        Returns:
        -------
            List[Path]: Sorted list of directories.
        """
        return natsorted([
            d for d in self.get_data_root_dir(data_type).iterdir()
            if d.is_dir()
        ])

    def common_data_dirs_parallel(self) -> list[str]:
        """
        Get the common data directories of both canopy and sky data \
            using parallel processing.

        Returns:
        -------
            List[str]: List of common data directories of both canopy and sky data.
        """
        sky_dirs = {d.name for d in self.get_dirs("sky")}
        canopy_dirs = {d.name for d in self.get_dirs("canopy")}
        common_dirs = sky_dirs & canopy_dirs
        common_dirs.discard("00000")

        return self._parallel_validate(YYDOYValidator.validate,
                                       list(common_dirs))

    def dirs_with_rnx_files_parallel(self) -> list[str]:
        """
        Get the directories with RINEX files present in both canopy and sky data\
            using parallel processing.

        Returns:
        -------
            List[str]: List of directories with RINEX files present in both
                canopy and sky data.
        """
        cdd = self.common_data_dirs_parallel()

        def validate_dir(d: str) -> bool:
            return (RinexFilesPresentValidator.validate(
                self.get_data_root_dir("canopy") / d)
                    and RinexFilesPresentValidator.validate(
                        self.get_data_root_dir("sky") / d))

        return self._parallel_validate(validate_dir, cdd)

    def _parallel_validate(self, validator: Callable[[str], bool],
                           items: list[str]) -> list[str]:
        """
        Run a validation function in parallel using ThreadPoolExecutor.

        Parameters:
        ----------
        validator : Callable
            The validation function to be applied to each item.

        items : List[str]
            The list of items to validate.

        Returns:
        -------
            List[str]: List of items that passed validation.
        """
        with ThreadPoolExecutor() as executor:
            future_to_item: dict[Future[bool], str] = {
                executor.submit(validator, item): item
                for item in items
            }
            return natsorted([
                future_to_item[f] for f in as_completed(future_to_item)
                if f.result()
            ])


@dataclass
class PairMatchedDirs:
    """Matched directories for a receiver pair on a specific date."""
    yyyydoy: YYYYDOY
    pair_name: str
    canopy_receiver: str
    reference_receiver: str
    canopy_data_dir: Path
    reference_data_dir: Path


class PairDataDirMatcher:
    """
    Match RINEX data directories for receiver pairs across dates.

    Iterates over dates and yields matched directories for each configured
    receiver pair that has data available.

    Parameters
    ----------
    site : GnssResearchSite
        Research site with configured receivers and analysis pairs
    receiver_subpath_template : str
        Template for receiver subdirectory structure. Use {receiver_type}
        and {receiver_num} placeholders.
        Example: "{receiver_type}/01_GNSS/01_raw"
        where receiver_type maps to "01_reference" or "02_canopy"
    """

    def __init__(
            self,
            site: GnssResearchSite,
            receiver_subpath_template: str = "{receiver_dir}/01_GNSS/01_raw"):
        self.site = site
        self.base_dir = site.site_config["base_dir"]
        self.subpath_template = receiver_subpath_template

        # Build receiver directory mapping
        self.receiver_dirs = self._build_receiver_dir_mapping()

    def _build_receiver_dir_mapping(self) -> dict[str, str]:
        """Map receiver names to their directory prefixes from config."""
        mapping = {}
        for receiver_name, config in self.site.receivers.items():
            if "directory" not in config:
                raise ValueError(
                    f"Receiver '{receiver_name}' missing 'directory' in config"
                )
            mapping[receiver_name] = config["directory"]
        return mapping

    def _get_receiver_path(self, receiver_name: str, yyyydoy: YYYYDOY) -> Path:
        """
        Build full path to receiver data for a specific date.

        Parameters
        ----------
        receiver_name : str
            Receiver name (e.g., "canopy_01")
        yyyydoy : YYYYDOY
            Date object

        Returns
        -------
        Path
            Full path to receiver's RINEX directory for the date
        """

        receiver_dir = self.receiver_dirs[receiver_name]
        subpath = self.subpath_template.format(receiver_dir=receiver_dir)

        # Convert YYYYDDD to YYDDD format for directory name
        yyyyddd_str = yyyydoy.to_str()  # e.g., "2024129"
        yyddd_str = yyyyddd_str[2:]  # e.g., "24129"

        return self.base_dir / subpath / yyddd_str

    def _get_all_dates(self) -> set[YYYYDOY]:
        """
        Find all dates that have data in any receiver directory.

        Returns
        -------
        set[YYYYDOY]
            Set of all dates with available data
        """

        all_dates = set()

        for receiver_name in self.site.receivers.keys():
            receiver_dir = self.receiver_dirs[receiver_name]
            subpath = self.subpath_template.format(receiver_dir=receiver_dir)
            receiver_base = self.base_dir / subpath

            if not receiver_base.exists():
                continue

            # Find all date directories (format: YYDDD - 5 digits)
            for date_dir in receiver_base.iterdir():
                if date_dir.is_dir() and len(
                        date_dir.name) == 5 and date_dir.name.isdigit():
                    # Skip placeholder directories like '00000'
                    if date_dir.name == '00000':
                        continue

                    try:
                        # Convert YYDDD to YYYYDDD
                        yyddd = date_dir.name
                        year_prefix = "20"  # Assuming 2000s
                        yyyyddd = year_prefix + yyddd

                        yyyydoy = YYYYDOY.from_str(yyyyddd)
                        all_dates.add(yyyydoy)
                    except ValueError:
                        continue

        return all_dates

    def __iter__(self) -> Iterator[PairMatchedDirs]:
        """
        Iterate over all date/pair combinations with available data.

        Yields
        ------
        PairMatchedDirs
            Matched directories for a receiver pair on a specific date
        """
        all_dates = sorted(self._get_all_dates())

        for yyyydoy in all_dates:
            # For each configured analysis pair
            for pair_name, pair_config in self.site.active_vod_analyses.items(
            ):
                canopy_rx = pair_config["canopy_receiver"]
                reference_rx = pair_config["reference_receiver"]

                # Build paths for this pair
                canopy_path = self._get_receiver_path(canopy_rx, yyyydoy)
                reference_path = self._get_receiver_path(reference_rx, yyyydoy)

                # Check for RINEX files (*.24o or *.25o)
                canopy_has_files = canopy_path.exists() and any(
                    canopy_path.glob("*.2*o"))
                reference_has_files = reference_path.exists() and any(
                    reference_path.glob("*.2*o"))

                # Only yield if both directories exist and have data
                if canopy_has_files and reference_has_files:
                    yield PairMatchedDirs(
                        yyyydoy=yyyydoy,
                        pair_name=pair_name,
                        canopy_receiver=canopy_rx,
                        reference_receiver=reference_rx,
                        canopy_data_dir=canopy_path,
                        reference_data_dir=reference_path,
                    )


if __name__ == "__main__":
    # matcher = DataDirMatcher()

    # for matched_dirs in matcher:
    #     print(matched_dirs)
    site = GnssResearchSite(site_name="Rosalia")
    pair_matcher = PairDataDirMatcher(site)

    print(f"Base dir: {pair_matcher.base_dir}")
    print(f"Receiver dirs: {pair_matcher.receiver_dirs}")

    # Check what dates are found
    all_dates = pair_matcher._get_all_dates()
    print(f"Found {len(all_dates)} dates: {sorted(all_dates)[:5]}..."
          )  # Show first 5

    # Check paths for a specific date (e.g., 2024270)
    if all_dates:
        test_date = sorted(all_dates)[-10]
        for rx_name in site.receivers.keys():
            path = pair_matcher._get_receiver_path(rx_name, test_date)
            print(f"{rx_name}: {path}")
            print(f"  Exists: {path.exists()}")
            if path.exists():
                print(f"  RINEX files: {len(list(path.rglob('*.25o')))}")

    print(f"\nTotal matched pairs: {sum(1 for _ in pair_matcher)}")
