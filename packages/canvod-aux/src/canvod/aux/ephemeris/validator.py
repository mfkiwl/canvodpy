"""SP3 format validator."""

from pathlib import Path

import numpy as np
import xarray as xr

from canvod.aux.products.models import FileValidationResult


class Sp3Validator:
    """
    Validator for SP3 orbit files.

    Performs format and data quality checks on parsed SP3 datasets.
    """

    def __init__(self, dataset: xr.Dataset, fpath: Path):
        """
        Initialize validator.

        Args:
            dataset: Parsed SP3 dataset
            fpath: Path to original file
        """
        self.dataset = dataset
        self.fpath = Path(fpath)
        self.result = FileValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            file_path=self.fpath,
            file_type="SP3",
        )

    def validate(self) -> FileValidationResult:
        """
        Run all validation checks.

        Returns:
            Validation result with errors/warnings
        """
        self._check_required_variables()
        self._check_required_coordinates()
        self._check_data_quality()

        return self.result

    def _check_required_variables(self) -> None:
        """Check that required variables are present."""
        required = ['X', 'Y', 'Z']
        missing = [
            var for var in required if var not in self.dataset.data_vars
        ]

        if missing:
            self.result.add_error(f"Missing required variables: {missing}")

    def _check_required_coordinates(self) -> None:
        """Check that required coordinates are present."""
        required = ['epoch', 'sv']
        missing = [
            coord for coord in required if coord not in self.dataset.coords
        ]

        if missing:
            self.result.add_error(f"Missing required coordinates: {missing}")

    def _check_data_quality(self) -> None:
        """Check data quality metrics."""
        if 'X' not in self.dataset:
            return

        # Check for excessive NaN values
        for var in ['X', 'Y', 'Z']:
            nan_count = self.dataset[var].isnull().sum().item()
            total_count = self.dataset[var].size
            nan_percentage = (nan_count / total_count) * 100

            if nan_percentage > 50:
                self.result.add_error(
                    f"Variable {var} has {nan_percentage:.1f}% NaN values (>50% threshold)"
                )
            elif nan_percentage > 10:
                self.result.add_warning(
                    f"Variable {var} has {nan_percentage:.1f}% NaN values")

    def get_summary(self) -> str:
        """Get validation summary."""
        return self.result.summary()
