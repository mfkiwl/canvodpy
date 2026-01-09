"""Abstract base class for GNSS data readers.

All GNSS reader implementations must inherit from GNSSReader and implement
the required interface. This ensures consistent API across different formats
(RINEX, SINEX, SBF, etc.) and enables format-agnostic processing pipelines.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar

import xarray as xr


class GNSSReader(ABC):
    """Abstract base class for all GNSS data format readers.
    
    All readers must return standardized xarray Datasets with:
    - Coordinates: (epoch, sv, sid)
    - Consistent variable naming and metadata
    - CF-compliant attributes where applicable
    
    This enables format-agnostic processing in downstream packages.
    """

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Human-readable format identifier.
        
        Examples:
            - "RINEX v3.04"
            - "RINEX v2.11"
            - "Septentrio SBF"
            - "SINEX"
        """
        pass

    @property
    @abstractmethod
    def format_version(self) -> str:
        """Format version string.
        
        Examples:
            - "3.04"
            - "2.11"
            - "1.0"
        """
        pass

    @property
    @abstractmethod
    def file_extensions(self) -> list[str]:
        """Supported file extensions (including dot).
        
        Examples:
            - [".rnx", ".24o", ".obs"]
            - [".sbf"]
            - [".snx"]
        """
        pass

    @abstractmethod
    def read(self, filepath: Path, **kwargs) -> xr.Dataset:
        """Read GNSS data file and return standardized xarray Dataset.
        
        Args:
            filepath: Path to GNSS data file
            **kwargs: Format-specific options
        
        Returns:
            xr.Dataset with standardized structure:
                Coordinates:
                    - epoch: datetime64[ns] - Observation epochs
                    - sv: str - Space vehicle identifier (e.g., "G01", "E05")
                    - sid: str - Signal ID (sv|band|code, e.g., "G01|L1|C")
                
                Data variables (format-dependent, but commonly):
                    - SNR: Signal-to-Noise Ratio
                    - Pseudorange: Pseudorange observations
                    - Phase: Carrier phase observations
                    - Doppler: Doppler shift observations
                
                Attributes:
                    - reader_name: Name of reader class
                    - format_name: Format identifier
                    - format_version: Version string
                    - source_file: Original file path
                    - ... (format-specific attributes)
        
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is invalid or unsupported
        """
        pass

    @abstractmethod
    def validate_file(self, filepath: Path) -> bool:
        """Check if file is valid for this reader.
        
        Args:
            filepath: Path to file to validate
        
        Returns:
            True if file can be read by this reader
        """
        pass

    @abstractmethod
    def read_header(self, filepath: Path) -> dict:
        """Extract header/metadata without reading full dataset.
        
        Args:
            filepath: Path to GNSS data file
        
        Returns:
            Dictionary with header information (format-specific)
        """
        pass

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(format={self.format_name} v{self.format_version})"


class RinexReader(GNSSReader):
    """Base class for RINEX format readers.
    
    Provides common functionality for RINEX v2, v3, v4 readers.
    """

    @property
    def format_name(self) -> str:
        """RINEX format identifier."""
        return f"RINEX v{self.format_version}"

    @property
    def file_extensions(self) -> list[str]:
        """Common RINEX extensions."""
        return [
            ".rnx",   # Generic RINEX
            ".obs",   # Observation
            ".nav",   # Navigation (if supported)
            # Year-specific patterns handled in validate_file
        ]

    def validate_file(self, filepath: Path) -> bool:
        """Validate RINEX file.
        
        Checks:
        1. File exists
        2. Extension matches RINEX patterns
        3. Version matches this reader (delegated to subclass)
        """
        if not filepath.exists():
            return False
        
        # Check extension
        ext = filepath.suffix.lower()
        
        # Generic extensions
        if ext in self.file_extensions:
            return True
        
        # Year-specific: .YYo (e.g., .24o for 2024)
        if len(ext) == 4 and ext[1:3].isdigit() and ext[3] == 'o':
            return True
        
        return False
