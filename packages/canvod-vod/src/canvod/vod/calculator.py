"""VOD calculators based on Tau-Omega model variants."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import numpy as np
from pydantic import BaseModel, ConfigDict, field_validator
import xarray as xr


class VODCalculator(ABC, BaseModel):
    """
    Abstract base class for VOD calculation from RINEX store data.

    Notes
    -----
    This is an abstract base class (ABC) and a Pydantic model.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    canopy_ds: xr.Dataset
    sky_ds: xr.Dataset

    @field_validator('canopy_ds', 'sky_ds')
    @classmethod
    def validate_datasets(cls, v: xr.Dataset) -> xr.Dataset:
        if not isinstance(v, xr.Dataset):
            raise ValueError("Must be xr.Dataset")
        if "SNR" not in v.data_vars:
            raise ValueError("Dataset must contain 'SNR' variable")
        return v

    @abstractmethod
    def calculate_vod(self) -> xr.Dataset:
        """Calculate VOD and return dataset with VOD, phi, theta."""
        raise NotImplementedError

    @classmethod
    def from_icechunkstore(
        cls,
        icechunk_store_pth: Path,
        canopy_group: str = "canopy_01",
        sky_group: str = "reference_01",
        **open_kwargs: Any,
    ) -> xr.Dataset:
        """
        Convenience method to calculate VOD directly from an IcechunkStore.

        Parameters
        ----------
        icechunk_store_pth : Path
            Path to Icechunk store.
        canopy_group : str
            Canopy receiver group name.
        sky_group : str
            Sky/reference receiver group name.
        open_kwargs : dict[str, Any]
            Additional keyword arguments for IcechunkStore.open().
            Currently unused.

        Returns
        -------
        xr.Dataset
            VOD dataset

        Notes
        -----
        Requires canvod-store to be installed.
        """
        try:
            from canvod.store import MyIcechunkStore
        except ImportError as e:
            raise ImportError(
                "canvod-store package required for from_icechunkstore(). "
                "Install with: pip install canvod-store"
            ) from e

        store = MyIcechunkStore(icechunk_store_pth)

        with store.readonly_session() as session:
            canopy_ds = xr.open_zarr(store=session.store, group=canopy_group)
            sky_ds = xr.open_zarr(store=session.store, group=sky_group)

        return cls.from_datasets(canopy_ds=canopy_ds,
                                 sky_ds=sky_ds,
                                 align=True)

    @classmethod
    def from_datasets(
        cls,
        canopy_ds: xr.Dataset,
        sky_ds: xr.Dataset,
        align: bool = True,
    ) -> xr.Dataset:
        """
        Convenience method to calculate VOD directly from datasets.

        Parameters
        ----------
        canopy_ds : xr.Dataset
            Canopy receiver dataset.
        sky_ds : xr.Dataset
            Sky/reference receiver dataset.
        align : bool
            Whether to align datasets on common coordinates.

        Returns
        -------
        xr.Dataset
            VOD dataset.
        """
        if align:
            canopy_ds, sky_ds = xr.align(canopy_ds, sky_ds, join='inner')

        calculator = cls(canopy_ds=canopy_ds, sky_ds=sky_ds)
        return calculator.calculate_vod()


class TauOmegaZerothOrder(VODCalculator):
    """
    Calculate VOD using the zeroth-order approximation of the Tau-Omega model.

    Based on Humphrey, V., & Frankenberg, C. (2022).
    """

    def get_delta_snr(self) -> xr.DataArray:
        """Calculate delta SNR = SNR_canopy - SNR_sky."""
        return self.canopy_ds["SNR"] - self.sky_ds["SNR"]

    def decibel2linear(self, delta_snr_db: xr.DataArray) -> xr.DataArray:
        """Convert decibel values to linear values."""
        return np.power(10, delta_snr_db / 10)

    def calculate_vod(self) -> xr.Dataset:
        """Calculate VOD using the zeroth-order approximation."""
        delta_snr = self.get_delta_snr()

        if delta_snr.isnull().all():
            raise ValueError(
                "All delta_snr values are NaN - check data alignment")

        canopy_transmissivity = self.decibel2linear(delta_snr)

        if (canopy_transmissivity <= 0).any():
            n_invalid = (canopy_transmissivity <= 0).sum().item()
            total = canopy_transmissivity.size
            print(
                f"Warning: {n_invalid}/{total} transmissivity values <= 0 "
                "(will produce NaN)"
            )

        theta = self.canopy_ds["theta"]
        vod = -np.log(canopy_transmissivity) * np.cos(theta)

        vod_ds = xr.Dataset(
            {
                "VOD": vod,
                "phi": self.canopy_ds["phi"],
                "theta": self.canopy_ds["theta"]
            },
            coords=self.canopy_ds.coords)

        return vod_ds
