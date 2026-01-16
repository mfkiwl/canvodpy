"""Abstract base class for GNSS data readers.

Defines interface that all readers (RINEX v3, RINEX v2, future formats)
must implement to ensure compatibility with downstream pipeline:
- VOD calculation (canvod-vod)
- Storage (canvod-store / MyIcechunkStore)
- Grid operations (canvod-grids)
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any

import xarray as xr
from pydantic import BaseModel, ConfigDict, Field


class DatasetStructureValidator(BaseModel):
    """Validates xarray.Dataset structure for pipeline compatibility.

    All readers must produce Datasets that pass this validation
    to ensure compatibility with downstream VOD and storage operations.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    dataset: xr.Dataset

    def validate_dimensions(self) -> None:
        """Validate required dimensions exist."""
        required_dims = {"epoch", "sid"}
        missing_dims = required_dims - set(self.dataset.dims)
        if missing_dims:
            raise ValueError(f"Missing required dimensions: {missing_dims}")

    def validate_coordinates(self) -> None:
        """Validate required coordinates exist and have correct types."""
        required_coords = {
            "epoch": "datetime64[ns]",
            "sid": "object",  # string
            "sv": "object",
            "system": "object",
            "band": "object",
            "code": "object",
            "freq_center": "float64",
            "freq_min": "float64",
            "freq_max": "float64",
        }

        for coord, expected_dtype in required_coords.items():
            if coord not in self.dataset.coords:
                raise ValueError(f"Missing required coordinate: {coord}")

            actual_dtype = str(self.dataset[coord].dtype)
            if expected_dtype == "object":
                # String coordinates can be stored as object or Unicode string (<U)
                if actual_dtype not in [
                        "object"
                ] and not actual_dtype.startswith("<U"):
                    raise ValueError(f"Coordinate {coord} has wrong dtype: "
                                     f"expected string, got {actual_dtype}")
            elif expected_dtype not in actual_dtype:
                raise ValueError(
                    f"Coordinate {coord} has wrong dtype: "
                    f"expected {expected_dtype}, got {actual_dtype}")

    def validate_data_variables(self, required_vars: list[str] = None) -> None:
        """Validate required data variables exist.

        Parameters
        ----------
        required_vars : list of str, optional
            List of required variables. If None, uses default minimum set.
        """
        if required_vars is None:
            # Minimum required for VOD calculation
            required_vars = ["SNR", "Phase"]

        missing_vars = set(required_vars) - set(self.dataset.data_vars)
        if missing_vars:
            raise ValueError(
                f"Missing required data variables: {missing_vars}")

        # Validate all data vars have (epoch, sid) dimensions
        for var in self.dataset.data_vars:
            expected_dims = ("epoch", "sid")
            actual_dims = self.dataset[var].dims
            if actual_dims != expected_dims:
                raise ValueError(
                    f"Data variable {var} has wrong dimensions: "
                    f"expected {expected_dims}, got {actual_dims}")

    def validate_attributes(self) -> None:
        """Validate required global attributes for storage."""
        required_attrs = {
            "Created",
            "Software",
            "Institution",
            "RINEX File Hash",  # Required for MyIcechunkStore deduplication
        }

        missing_attrs = required_attrs - set(self.dataset.attrs.keys())
        if missing_attrs:
            raise ValueError(f"Missing required attributes: {missing_attrs}")

    def validate_all(self, required_vars: list[str] = None) -> None:
        """Run all validations."""
        self.validate_dimensions()
        self.validate_coordinates()
        self.validate_data_variables(required_vars)
        self.validate_attributes()


class GNSSDataReader(ABC):
    """Abstract base class for all GNSS data format readers.

    All readers must:
    1. Inherit from this class
    2. Implement all abstract methods
    3. Return xarray.Dataset that passes DatasetStructureValidator
    4. Provide file hash for deduplication

    This ensures compatibility with:
    - canvod-vod: VOD calculation
    - canvod-store: MyIcechunkStore storage
    - canvod-grids: Grid projection operations

    Examples
    --------
    >>> class Rnxv3Obs(GNSSDataReader):
    ...     def to_ds(self, **kwargs) -> xr.Dataset:
    ...         # Implementation
    ...         return dataset
    ...
    >>> reader = Rnxv3Obs(fpath="station.24o")
    >>> ds = reader.to_ds()
    >>> reader.validate_output(ds)  # Automatic validation
    """

    # Note: fpath is not @abstractmethod because Pydantic models define it as a field
    # which provides the same interface
    fpath: Path

    @property
    @abstractmethod
    def file_hash(self) -> str:
        """Return SHA256 hash of file for deduplication.

        Used by MyIcechunkStore to avoid duplicate ingestion.
        Must be deterministic and reproducible.

        Returns
        -------
        str
            Short hash (16 chars) or full hash of file content
        """
        pass

    @abstractmethod
    def to_ds(self,
              keep_rnx_data_vars: list[str] | None = None,
              **kwargs: Any) -> xr.Dataset:
        """Convert data to xarray.Dataset.

        Must return Dataset with structure:
        - Dims: (epoch, sid)
        - Coords: epoch, sid, sv, system, band, code, freq_*
        - Data vars: At minimum SNR, Phase
        - Attrs: Must include "RINEX File Hash"

        Parameters
        ----------
        keep_rnx_data_vars : list of str, optional
            Data variables to include. If None, includes all available.
        **kwargs
            Implementation-specific parameters

        Returns
        -------
        xr.Dataset
            Dataset that passes DatasetStructureValidator
        """
        pass

    @abstractmethod
    def iter_epochs(self):
        """Iterate over epochs in the file.

        Yields
        ------
        Epoch
            Parsed epoch with satellites and observations
        """
        pass

    def validate_output(self,
                        dataset: xr.Dataset,
                        required_vars: list[str] | None = None) -> None:
        """Validate output Dataset structure.

        Called automatically by to_ds() to ensure compatibility.
        Can be called manually for testing.

        Parameters
        ----------
        dataset : xr.Dataset
            Dataset to validate
        required_vars : list of str, optional
            Required data variables. If None, uses minimum set.

        Raises
        ------
        ValueError
            If Dataset doesn't meet requirements
        """
        validator = DatasetStructureValidator(dataset=dataset)
        validator.validate_all(required_vars=required_vars)

    @property
    @abstractmethod
    def start_time(self) -> datetime:
        """Return start time of observations."""
        pass

    @property
    @abstractmethod
    def end_time(self) -> datetime:
        """Return end time of observations."""
        pass

    @property
    @abstractmethod
    def systems(self) -> list[str]:
        """Return list of GNSS systems in file.

        Returns
        -------
        list of str
            System identifiers: 'G', 'R', 'E', 'C', 'J', 'S', 'I'
        """
        pass

    @property
    @abstractmethod
    def num_epochs(self) -> int:
        """Return number of epochs in file."""
        pass

    @property
    @abstractmethod
    def num_satellites(self) -> int:
        """Return total number of unique satellites observed."""
        pass

    def __repr__(self) -> str:
        """String representation."""
        return (f"{self.__class__.__name__}("
                f"file='{self.fpath.name}', "
                f"systems={self.systems}, "
                f"epochs={self.num_epochs})")


class ReaderFactory:
    """Factory for creating appropriate reader based on file format.

    Automatically detects format and instantiates correct reader.

    Examples
    --------
    >>> reader = ReaderFactory.create("station.24o")
    >>> isinstance(reader, Rnxv3Obs)
    True

    >>> reader = ReaderFactory.create("station.10o")
    >>> isinstance(reader, Rnxv2Obs)
    True
    """

    _readers: dict[str, type] = {}

    @classmethod
    def register(cls, format_name: str, reader_class: type) -> None:
        """Register a reader class for a format.

        Parameters
        ----------
        format_name : str
            Format identifier (e.g., 'rinex_v3', 'rinex_v2')
        reader_class : type
            Reader class (must inherit from GNSSDataReader)
        """
        if not issubclass(reader_class, GNSSDataReader):
            raise TypeError(f"{reader_class} must inherit from GNSSDataReader")
        cls._readers[format_name] = reader_class

    @classmethod
    def create(cls, fpath: Path | str, **kwargs) -> GNSSDataReader:
        """Create appropriate reader for file.

        Parameters
        ----------
        fpath : Path or str
            Path to data file
        **kwargs
            Parameters to pass to reader constructor

        Returns
        -------
        GNSSDataReader
            Instantiated reader

        Raises
        ------
        ValueError
            If file format cannot be determined
        """
        fpath = Path(fpath)

        if not fpath.exists():
            raise FileNotFoundError(f"File not found: {fpath}")

        # Detect format from file
        format_name = cls._detect_format(fpath)

        if format_name not in cls._readers:
            raise ValueError(
                f"No reader registered for format: {format_name}. "
                f"Available: {list(cls._readers.keys())}")

        reader_class = cls._readers[format_name]
        return reader_class(fpath=fpath, **kwargs)

    @staticmethod
    def _detect_format(fpath: Path) -> str:
        """Detect file format.

        Parameters
        ----------
        fpath : Path
            Path to file

        Returns
        -------
        str
            Format name
        """
        # Check RINEX version from first line
        with open(fpath, 'r') as f:
            first_line = f.readline()

        # RINEX version is in columns 1-9
        try:
            version_str = first_line[:9].strip()
            version = float(version_str)

            if 3.0 <= version < 4.0:
                return 'rinex_v3'
            elif 2.0 <= version < 3.0:
                return 'rinex_v2'
            else:
                raise ValueError(f"Unsupported RINEX version: {version}")
        except (ValueError, IndexError) as e:
            raise ValueError(f"Cannot determine file format: {e}")

    @classmethod
    def list_formats(cls) -> list[str]:
        """List available formats."""
        return list(cls._readers.keys())


# Backwards compatibility aliases
GNSSReader = GNSSDataReader
RinexReader = GNSSDataReader

__all__ = [
    'GNSSDataReader',
    'DatasetStructureValidator',
    'ReaderFactory',
    # Backwards compatibility
    'GNSSReader',
    'RinexReader',
]
