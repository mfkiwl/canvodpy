"""SP3 orbit file reader with multi-product support."""

from pathlib import Path

import numpy as np
import xarray as xr
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from canvod.aux._internal import UREG, get_gps_week_from_filename
from canvod.aux.core.base import AuxFile
from canvod.aux.ephemeris.parser import Sp3Parser
from canvod.aux.ephemeris.validator import Sp3Validator
from canvod.aux.interpolation import Interpolator, Sp3Config, Sp3InterpolationStrategy
from canvod.aux.products.registry import ProductSpec, get_product_spec


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Sp3File(AuxFile):
    """
    Handler for SP3 orbit files with multi-product support.

    Now supports all IGS analysis centers via product registry:
    COD, GFZ, ESA, JPL, IGS, WHU, GRG, SHA

    Attributes:
        date: String in YYYYDOY format
        agency: Agency code (e.g., 'COD', 'GFZ', 'ESA')
        product_type: Product type ('final', 'rapid')
        ftp_server: Base URL for downloads
        local_dir: Local storage directory
        add_velocities: Whether to compute velocities (default: True)
        dimensionless: Whether to strip units (default: True)
    """

    date: str
    agency: str
    product_type: str
    ftp_server: str
    local_dir: Path
    add_velocities: bool | None = True
    dimensionless: bool | None = True
    product_spec: ProductSpec | None = None

    def __post_init__(self):
        """Initialize with product validation."""
        self.file_type = ["orbit"]
        self.local_dir = Path(self.local_dir)
        self.local_dir.mkdir(parents=True, exist_ok=True)

        # Validate product exists in registry
        self.product_spec = get_product_spec(self.agency, self.product_type)

        super().__post_init__()

    def get_interpolation_strategy(self) -> Interpolator:
        """Get appropriate interpolation strategy for SP3 files."""
        config = Sp3Config(
            use_velocities=self.add_velocities,
            fallback_method='linear',
        )
        return Sp3InterpolationStrategy(config=config)

    def generate_filename_based_on_type(self) -> Path:
        """
        Generate filename using product registry.

        Pattern: {PREFIX}_{YYYYDOY}0000_{DURATION}_{SAMPLING}_ORB.SP3

        Example: COD0MGXFIN_20240150000_01D_05M_ORB.SP3
        """
        prefix = self.product_spec.prefix
        duration = self.product_spec.duration
        sampling = self.product_spec.sampling_rate

        return Path(f"{prefix}_{self.date}0000_{duration}_{sampling}_ORB.SP3")

    def download_aux_file(self) -> None:
        """
        Download using product-specific path pattern.

        Raises:
            RuntimeError: If download fails from all servers
            ValueError: If GPS week calculation fails
        """
        orbit_file = self.generate_filename_based_on_type()
        gps_week = get_gps_week_from_filename(orbit_file)

        # Use product spec's path pattern
        ftp_path = self.product_spec.ftp_path_pattern.format(
            gps_week=gps_week,
            file=f"{orbit_file}.gz",
        )

        full_url = f"{self.ftp_server}{ftp_path}"
        destination = self.local_dir / orbit_file

        file_info = {
            'gps_week': gps_week,
            'filename': orbit_file,
            'type': 'orbit',
            'agency': self.agency,
            'latency': self.product_spec.latency_hours,
        }

        try:
            self.download_file(full_url, destination, file_info)
            print(
                f"Downloaded orbit file for {self.agency} on date {self.date}")
        except Exception as e:
            raise RuntimeError(
                f"Failed to download SP3 file from all available servers: {str(e)}"
            )

    def read_file(self) -> xr.Dataset:
        """
        Read and validate SP3 file.

        Returns:
            Dataset with satellite positions (X, Y, Z) in meters

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If validation fails
        """
        # Use dedicated parser
        parser = Sp3Parser(self.fpath, dimensionless=self.dimensionless)
        dataset = parser.parse()

        # Validate format
        validator = Sp3Validator(dataset, self.fpath)
        result = validator.validate()

        if not result.is_valid:
            raise ValueError(f"SP3 validation failed:\n{result.summary()}")

        # Add metadata
        dataset = self._add_metadata(dataset)

        # Compute velocities if requested
        if self.add_velocities:
            dataset = self.compute_velocity(dataset)

        return dataset

    def _add_metadata(self, ds: xr.Dataset) -> xr.Dataset:
        """Add file-level metadata to dataset."""
        ds.attrs = {
            'file': str(self.fpath.name),
            'agency': self.agency,
            'agency_name': self.product_spec.agency_name,
            'product_type': self.product_type,
            'ftp_server': self.ftp_server,
            'date': self.date,
            'sampling_rate': self.product_spec.sampling_rate,
            'duration': self.product_spec.duration,
        }
        return ds

    def compute_velocity(self, ds: xr.Dataset) -> xr.Dataset:
        """
        Compute satellite velocities from position data.

        Uses central differences for interior points, forward/backward
        differences for endpoints.

        Args:
            ds: Dataset with X, Y, Z coordinates

        Returns:
            Dataset augmented with Vx, Vy, Vz velocities
        """
        # Calculate time step
        time_diffs = np.diff(ds['epoch'].values)
        dt = np.median(time_diffs).astype('timedelta64[s]').astype(float)

        # Initialize velocity arrays
        Vx = np.zeros_like(ds['X'].values)
        Vy = np.zeros_like(ds['Y'].values)
        Vz = np.zeros_like(ds['Z'].values)

        # Central difference for interior points
        Vx[1:-1] = (ds['X'].values[2:] - ds['X'].values[:-2]) / (2 * dt)
        Vy[1:-1] = (ds['Y'].values[2:] - ds['Y'].values[:-2]) / (2 * dt)
        Vz[1:-1] = (ds['Z'].values[2:] - ds['Z'].values[:-2]) / (2 * dt)

        # Forward difference for first point
        Vx[0] = (ds['X'].values[1] - ds['X'].values[0]) / dt
        Vy[0] = (ds['Y'].values[1] - ds['Y'].values[0]) / dt
        Vz[0] = (ds['Z'].values[1] - ds['Z'].values[0]) / dt

        # Backward difference for last point
        Vx[-1] = (ds['X'].values[-1] - ds['X'].values[-2]) / dt
        Vy[-1] = (ds['Y'].values[-1] - ds['Y'].values[-2]) / dt
        Vz[-1] = (ds['Z'].values[-1] - ds['Z'].values[-2]) / dt

        # Add units if needed
        if not self.dimensionless:
            Vx = Vx * (UREG.meter / UREG.second)
            Vy = Vy * (UREG.meter / UREG.second)
            Vz = Vz * (UREG.meter / UREG.second)

        # Add to dataset
        ds = ds.assign(
            Vx=(('epoch', 'sv'), Vx),
            Vy=(('epoch', 'sv'), Vy),
            Vz=(('epoch', 'sv'), Vz),
        )

        # Add velocity attributes
        for var, attrs in self._get_velocity_attributes(dt).items():
            if var in ds:
                ds[var].attrs = attrs

        return ds

    def _get_velocity_attributes(
            self, dt: float) -> dict[str, dict[str, str | float]]:
        """Get standardized attributes for velocity variables."""
        base_attrs = {
            'units': 'm/s',
            'computation_method': 'central_difference',
            'time_step': float(dt),
            'reference_frame': 'ECEF',
        }

        return {
            'Vx': {
                'long_name': 'x-component of velocity',
                'standard_name': 'v_x',
                'short_name': 'v_x',
                'axis': 'v_x',
                **base_attrs,
            },
            'Vy': {
                'long_name': 'y-component of velocity',
                'standard_name': 'v_y',
                'short_name': 'v_y',
                'axis': 'v_y',
                **base_attrs,
            },
            'Vz': {
                'long_name': 'z-component of velocity',
                'standard_name': 'v_z',
                'short_name': 'v_z',
                'axis': 'v_z',
                **base_attrs,
            },
        }
