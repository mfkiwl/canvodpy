"""
Research site manager that coordinates RINEX and VOD Icechunk stores.

This module provides the GnssResearchSite class that manages both stores
for a research site and provides high-level operations across them.

Module: src/gnssvodpy/icechunk_manager/manager.py
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

import numpy as np
import xarray as xr

if TYPE_CHECKING:
    from canvod.vod import VODCalculator

from canvodpy.globals import RINEX_STORE_STRATEGY
from canvod.store.store import (
    MyIcechunkStore,
    create_rinex_store,
    create_vod_store,
)
from canvodpy.logging.context import get_logger
from canvodpy.research_sites_config import DEFAULT_RESEARCH_SITE, RESEARCH_SITES


class GnssResearchSite:
    """
    High-level manager for a GNSS research site with dual Icechunk stores.

    This class coordinates between RINEX data storage (Level 1) and
    VOD analysis storage (Level 2), providing a unified interface
    for site-wide operations.

    Architecture:
    - RINEX Store: Raw/standardized observations per receiver
    - VOD Store: Analysis products comparing receiver pairs

    Features:
    - Automatic store initialization from config
    - Receiver management and validation
    - Analysis workflow coordination
    - Unified logging and error handling
    """

    def __init__(self, site_name: str) -> None:
        """
        Initialize a research site manager.

        Parameters
        ----------
        site_name : str
            Name of the research site (must exist in config).

        Raises
        ------
        KeyError
            If ``site_name`` is not found in the RESEARCH_SITES config.
        """

        if site_name not in RESEARCH_SITES:
            available_sites = list(RESEARCH_SITES.keys())
            raise KeyError(f"Site '{site_name}' not found in config. "
                           f"Available sites: {available_sites}")

        self.site_name = site_name
        self.site_config = RESEARCH_SITES[site_name]
        self._logger = get_logger().bind(site=site_name)

        # Initialize stores
        self.rinex_store = create_rinex_store(
            self.site_config["rinex_store_path"])
        self.vod_store = create_vod_store(self.site_config["vod_store_path"])

        self._logger.info(f"Initialized GNSS research site: {site_name}")

    @property
    def receivers(self) -> dict[str, dict[str, Any]]:
        """Get all configured receivers for this site."""
        return self.site_config["receivers"]

    @property
    def active_receivers(self) -> dict[str, dict[str, Any]]:
        """Get only active receivers for this site."""
        return {
            name: config
            for name, config in self.receivers.items()
            if config.get("active", True)
        }

    @property
    def vod_analyses(self) -> dict[str, dict[str, Any]]:
        """Get all configured VOD analyses for this site."""
        return self.site_config["vod_analyses"]

    @property
    def active_vod_analyses(self) -> dict[str, dict[str, Any]]:
        """Get only active VOD analyses for this site."""
        return {
            name: config
            for name, config in self.vod_analyses.items()
            if config.get("active", True)
        }

    @classmethod
    def from_rinex_store_path(
        cls,
        rinex_store_path: Path,
    ) -> "GnssResearchSite":
        """
        Create a GnssResearchSite instance from a RINEX store path.

        Parameters
        ----------
        rinex_store_path : Path
            Path to the RINEX Icechunk store.

        Returns
        -------
        GnssResearchSite
            Initialized research site manager.

        Raises
        ------
        ValueError
            If no matching site is found for the given path.
        """
        for site_name, config in RESEARCH_SITES.items():
            if Path(config["rinex_store_path"]) == rinex_store_path:
                return cls(site_name)

        raise ValueError(f"No research site found for RINEX store path: "
                         f"{rinex_store_path}")

    def validate_site_config(self) -> bool:
        """
        Validate that the site configuration is consistent.


        Returns
        -------
        bool
            True if configuration is valid.

        Raises
        ------
        ValueError:
            If configuration is invalid
        """
        # Check that all VOD analyses reference valid receivers
        for analysis_name, analysis_config in self.vod_analyses.items():
            canopy_rx = analysis_config["canopy_receiver"]
            ref_rx = analysis_config["reference_receiver"]

            if canopy_rx not in self.receivers:
                raise ValueError(f"VOD analysis '{analysis_name}' references "
                                 f"unknown canopy receiver: {canopy_rx}")
            if ref_rx not in self.receivers:
                raise ValueError(f"VOD analysis '{analysis_name}' references "
                                 f"unknown reference receiver: {ref_rx}")

            # Check receiver types match their roles
            canopy_type = self.receivers[canopy_rx]["type"]
            ref_type = self.receivers[ref_rx]["type"]

            if canopy_type != "canopy":
                raise ValueError(f"Receiver '{canopy_rx}' used as canopy "
                                 f"but type is '{canopy_type}'")
            if ref_type != "reference":
                raise ValueError(f"Receiver '{ref_rx}' used as reference "
                                 f"but type is '{ref_type}'")

        self._logger.debug("Site configuration validation passed")
        return True

    def get_receiver_groups(self) -> list[str]:
        """
        Get list of receiver groups that exist in the RINEX store.

        Returns
        -------
        List[str]
            Existing receiver group names.
        """
        return self.rinex_store.list_groups()

    def get_vod_analysis_groups(self) -> list[str]:
        """
        Get list of VOD analysis groups that exist in the VOD store.

        Returns
        -------
        List[str]
            Existing VOD analysis group names.
        """
        return self.vod_store.list_groups()

    def ingest_rinex_data(self,
                          dataset: xr.Dataset,
                          receiver_name: str,
                          commit_message: str | None = None) -> None:
        """
        Ingest RINEX data for a specific receiver.

        Parameters
        ----------
        dataset : xr.Dataset
            Processed RINEX dataset to store.
        receiver_name : str
            Name of the receiver (must be configured).
        commit_message : str, optional
            Commit message to store with the data.

        Raises
        ------
        ValueError
            If ``receiver_name`` is not configured.
        """
        if receiver_name not in self.receivers:
            available_receivers = list(self.receivers.keys())
            raise ValueError(f"Receiver '{receiver_name}' not configured. "
                             f"Available: {available_receivers}")

        self._logger.info(
            f"Ingesting RINEX data for receiver '{receiver_name}'")

        self.rinex_store.write_or_append_group(dataset=dataset,
                                               group_name=receiver_name,
                                               commit_message=commit_message)

        self._logger.info(
            f"Successfully ingested data for receiver '{receiver_name}'")

    def read_receiver_data(
            self,
            receiver_name: str,
            time_range: tuple[datetime, datetime] | None = None) -> xr.Dataset:
        """
        Read data from a specific receiver.

        Parameters
        ----------
        receiver_name : str
            Name of the receiver.
        time_range : tuple of datetime, optional
            (start_time, end_time) for filtering the data.

        Returns
        -------
        xr.Dataset
            Dataset containing receiver observations.

        Raises
        ------
        ValueError
            If the receiver group does not exist.
        """
        if not self.rinex_store.group_exists(receiver_name):
            available_groups = self.get_receiver_groups()
            raise ValueError(f"No data found for receiver '{receiver_name}'. "
                             f"Available: {available_groups}")

        self._logger.info(f"Reading data for receiver '{receiver_name}'")

        if RINEX_STORE_STRATEGY == "append":
            ds = self.rinex_store.read_group_deduplicated(receiver_name,
                                                          keep='last')
        else:
            ds = self.rinex_store.read_group(receiver_name)

        # Apply time filtering if specified
        if time_range is not None:
            start_time, end_time = time_range
            ds = ds.where((ds.epoch >= np.datetime64(start_time, "ns")) &
                          (ds.epoch <= np.datetime64(end_time, "ns")),
                          drop=True)

            self._logger.debug(
                f"Applied time filter: {start_time} to {end_time}")

        return ds

    def store_vod_analysis(self,
                           vod_dataset: xr.Dataset,
                           analysis_name: str,
                           commit_message: str | None = None) -> None:
        """
        Store VOD analysis results.

        Parameters
        ----------
        vod_dataset : xr.Dataset
            Dataset containing VOD analysis results.
        analysis_name : str
            Name of the analysis (must be configured).
        commit_message : str, optional
            Commit message to store with the results.

        Raises
        ------
        ValueError
            If ``analysis_name`` is not configured.
        """
        if analysis_name not in self.vod_analyses:
            available_analyses = list(self.vod_analyses.keys())
            raise ValueError(f"VOD analysis '{analysis_name}' not configured. "
                             f"Available: {available_analyses}")

        self._logger.info(f"Storing VOD analysis results: '{analysis_name}'")

        self.vod_store.write_or_append_group(dataset=vod_dataset,
                                             group_name=analysis_name,
                                             commit_message=commit_message)

        self._logger.info(
            f"Successfully stored VOD analysis: '{analysis_name}'")

    def read_vod_analysis(
            self,
            analysis_name: str,
            time_range: tuple[datetime, datetime] | None = None) -> xr.Dataset:
        """
        Read VOD analysis results.

        Parameters
        ----------
        analysis_name : str
            Name of the analysis.
        time_range : tuple of datetime, optional
            (start_time, end_time) for filtering the results.

        Returns
        -------
        xr.Dataset
            Dataset containing VOD analysis results.

        Raises
        ------
        ValueError
            If the analysis group does not exist.
        """
        if not self.vod_store.group_exists(analysis_name):
            available_groups = self.get_vod_analysis_groups()
            raise ValueError(
                f"No VOD results found for analysis '{analysis_name}'. "
                f"Available: {available_groups}")

        self._logger.info(f"Reading VOD analysis: '{analysis_name}'")

        ds = self.vod_store.read_group(analysis_name)

        # Apply time filtering if specified
        if time_range is not None:
            start_time, end_time = time_range
            ds = ds.sel(epoch=slice(start_time, end_time))
            self._logger.debug(
                f"Applied time filter: {start_time} to {end_time}")

        return ds

    def prepare_vod_input_data(
        self,
        analysis_name: str,
        time_range: tuple[datetime, datetime] | None = None
    ) -> tuple[xr.Dataset, xr.Dataset]:
        """
        Prepare aligned input data for VOD analysis.

        Reads data from both receivers specified in the analysis configuration
        and returns them aligned for VOD processing.

        Parameters
        ----------
        analysis_name : str
            Name of the VOD analysis configuration.
        time_range : tuple of datetime, optional
            (start_time, end_time) for filtering the data.

        Returns
        -------
        tuple of (xr.Dataset, xr.Dataset)
            Tuple of (canopy_dataset, reference_dataset).

        Raises
        ------
        ValueError
            If the analysis is not configured or data is missing.
        """
        if analysis_name not in self.vod_analyses:
            available_analyses = list(self.vod_analyses.keys())
            raise ValueError(f"VOD analysis '{analysis_name}' not configured. "
                             f"Available: {available_analyses}")

        analysis_config = self.vod_analyses[analysis_name]
        canopy_receiver = analysis_config["canopy_receiver"]
        reference_receiver = analysis_config["reference_receiver"]

        self._logger.info(
            f"Preparing VOD input data: {canopy_receiver} vs {reference_receiver}"
        )

        # Read data from both receivers
        canopy_data = self.read_receiver_data(canopy_receiver, time_range)
        reference_data = self.read_receiver_data(reference_receiver,
                                                 time_range)

        self._logger.info(f"Loaded data - Canopy: {dict(canopy_data.dims)}, "
                          f"Reference: {dict(reference_data.dims)}")

        return canopy_data, reference_data

    def calculate_vod(
        self,
        analysis_name: str,
        calculator_class: type[VODCalculator] | None = None,
        time_range: tuple[datetime, datetime] | None = None,
    ) -> xr.Dataset:
        """
        Calculate VOD for a configured analysis pair.

        Parameters
        ----------
        analysis_name : str
            Analysis name from config (e.g., 'canopy_01_vs_reference_01')
        calculator_class : type[VODCalculator], optional
            VOD calculator class to use. If None, uses TauOmegaZerothOrder.
        time_range : tuple of datetime, optional
            (start_time, end_time) for filtering the data

        Returns
        -------
        xr.Dataset
            VOD dataset
            
        Note
        ----
        Requires canvod-vod to be installed.
        """
        if calculator_class is None:
            try:
                from canvod.vod import TauOmegaZerothOrder
                calculator_class = TauOmegaZerothOrder
            except ImportError as e:
                raise ImportError(
                    "canvod-vod package required for VOD calculation. "
                    "Install with: pip install canvod-vod"
                ) from e
        
        canopy_ds, reference_ds = self.prepare_vod_input_data(
            analysis_name, time_range)

        # Use the calculator's class method for calculation
        vod_ds = calculator_class.from_datasets(canopy_ds,
                                                reference_ds,
                                                align=True)

        # Add metadata
        analysis_config = self.vod_analyses[analysis_name]
        vod_ds.attrs["analysis_name"] = analysis_name
        vod_ds.attrs["canopy_receiver"] = analysis_config["canopy_receiver"]
        vod_ds.attrs["reference_receiver"] = analysis_config[
            "reference_receiver"]
        vod_ds.attrs["calculator"] = calculator_class.__name__
        vod_ds.attrs["canopy_hash"] = canopy_ds.attrs.get(
            "RINEX File Hash", "unknown")
        vod_ds.attrs["reference_hash"] = reference_ds.attrs.get(
            "RINEX File Hash", "unknown")

        self._logger.info(
            f"VOD calculated for {analysis_name} using {calculator_class.__name__}"
        )
        return vod_ds

    def store_vod(
        self,
        vod_ds: xr.Dataset,
        analysis_name: str,
    ) -> str:
        """
        Store VOD dataset in VOD store.

        Parameters
        ----------
        vod_ds : xr.Dataset
            VOD dataset to store
        analysis_name : str
            Analysis name (group name in store)

        Returns
        -------
        str
            Snapshot ID
        """
        from icechunk.xarray import to_icechunk

        from gnssvodpy.utils.tools import get_version_from_pyproject

        canopy_hash = vod_ds.attrs.get("canopy_hash", "unknown")
        reference_hash = vod_ds.attrs.get("reference_hash", "unknown")
        combined_hash = f"{canopy_hash}_{reference_hash}"

        with self.vod_store.writable_session() as session:
            groups = self.vod_store.list_groups() or []

            if analysis_name not in groups:
                to_icechunk(vod_ds, session, group=analysis_name, mode="w")
                action = "write"
            else:
                to_icechunk(vod_ds,
                            session,
                            group=analysis_name,
                            append_dim="epoch")
                action = "append"

            version = get_version_from_pyproject()
            commit_msg = f"[v{version}] VOD for {analysis_name}"
            snapshot_id = session.commit(commit_msg)

        self.vod_store.append_metadata(group_name=analysis_name,
                                       rinex_hash=combined_hash,
                                       start=vod_ds["epoch"].values[0],
                                       end=vod_ds["epoch"].values[-1],
                                       snapshot_id=snapshot_id,
                                       action=action,
                                       commit_msg=commit_msg,
                                       dataset_attrs=dict(vod_ds.attrs))

        self._logger.info(
            f"VOD stored for {analysis_name}, snapshot={snapshot_id[:8]}...")
        return snapshot_id

    def get_site_summary(self) -> dict[str, Any]:
        """
        Get a comprehensive summary of the research site.

        Returns
        -------
        dict
            Dictionary with site statistics, data availability, and store paths.
        """
        rinex_groups = self.get_receiver_groups()
        vod_groups = self.get_vod_analysis_groups()

        summary = {
            "site_name": self.site_name,
            "site_config": {
                "total_receivers": len(self.receivers),
                "active_receivers": len(self.active_receivers),
                "total_vod_analyses": len(self.vod_analyses),
                "active_vod_analyses": len(self.active_vod_analyses)
            },
            "data_status": {
                "rinex_groups_exist": len(rinex_groups),
                "rinex_groups": rinex_groups,
                "vod_groups_exist": len(vod_groups),
                "vod_groups": vod_groups
            },
            "stores": {
                "rinex_store_path": str(self.site_config["rinex_store_path"]),
                "vod_store_path": str(self.site_config["vod_store_path"])
            }
        }

        # Add receiver details
        summary["receivers"] = {}
        for receiver_name, receiver_config in self.active_receivers.items():
            has_data = receiver_name in rinex_groups
            summary["receivers"][receiver_name] = {
                "type": receiver_config["type"],
                "description": receiver_config["description"],
                "has_data": has_data
            }

            if has_data:
                try:
                    info = self.rinex_store.get_group_info(receiver_name)
                    summary["receivers"][receiver_name]["data_info"] = {
                        "dimensions": info["dimensions"],
                        "variables": len(info["variables"]),
                        "temporal_info": info.get("temporal_info", {})
                    }
                except Exception as e:
                    self._logger.warning(
                        f"Failed to get info for {receiver_name}: {e}")

        # Add VOD analysis details
        summary["vod_analyses"] = {}
        for analysis_name, analysis_config in self.active_vod_analyses.items():
            has_results = analysis_name in vod_groups
            summary["vod_analyses"][analysis_name] = {
                "canopy_receiver": analysis_config["canopy_receiver"],
                "reference_receiver": analysis_config["reference_receiver"],
                "description": analysis_config["description"],
                "has_results": has_results
            }

            if has_results:
                try:
                    info = self.vod_store.get_group_info(analysis_name)
                    summary["vod_analyses"][analysis_name]["results_info"] = {
                        "dimensions": info["dimensions"],
                        "variables": len(info["variables"]),
                        "temporal_info": info.get("temporal_info", {})
                    }
                except Exception as e:
                    self._logger.warning(
                        f"Failed to get VOD info for {analysis_name}: {e}")

        return summary

    def is_day_complete(self,
                        yyyydoy: str,
                        receiver_types: list[str] | None = None,
                        completeness_threshold: float = 0.95) -> bool:
        """
        Check if a day has complete data coverage for all receiver types.

        Parameters
        ----------
        yyyydoy : str
            Date in YYYYDOY format (e.g., "2024256")
        receiver_types : List[str], optional
            Receiver types to check. Defaults to ['canopy', 'reference']
        completeness_threshold : float
            Fraction of expected epochs that must exist (default 0.95 = 95%)
            Allows for small gaps due to receiver issues

        Returns
        -------
        bool
            True if all receiver types have complete data for this day
        """
        if receiver_types is None:
            receiver_types = ['canopy', 'reference']

        from gnssvodpy.utils.date_time import YYYYDOY
        yyyydoy_obj = YYYYDOY.from_str(yyyydoy)

        # Expected epochs for 24h at 30s sampling
        expected_epochs = int(24 * 3600 / 30)  # 2880 epochs
        required_epochs = int(expected_epochs * completeness_threshold)

        for receiver_type in receiver_types:
            # Get receiver name for this type
            receiver_name = None
            for name, config in self.active_receivers.items():
                if config.get('type') == receiver_type:
                    receiver_name = name
                    break

            if not receiver_name:
                self._logger.warning(
                    f"No receiver configured for type {receiver_type}")
                return False

            try:
                # Try to read data for this day
                time_range = (yyyydoy_obj.start_datetime(),
                              yyyydoy_obj.end_datetime())

                ds = self.read_receiver_data(receiver_name=receiver_name,
                                             time_range=time_range)

                # Check epoch count
                n_epochs = ds.sizes.get('epoch', 0)

                if n_epochs < required_epochs:
                    self._logger.info(
                        f"{receiver_name} {yyyydoy}: Only {n_epochs}/{expected_epochs} epochs "
                        f"({n_epochs/expected_epochs*100:.1f}%) - incomplete")
                    return False

                self._logger.debug(
                    f"{receiver_name} {yyyydoy}: {n_epochs}/{expected_epochs} epochs - complete"
                )

            except (ValueError, KeyError, Exception) as e:
                # No data exists or error reading
                self._logger.debug(
                    f"{receiver_name} {yyyydoy}: No data found - {e}")
                return False

        # All receiver types have complete data
        return True

    def __repr__(self) -> str:
        return f"GnssResearchSite(site_name='{self.site_name}')"

    def __str__(self) -> str:
        rinex_groups = len(self.get_receiver_groups())
        vod_groups = len(self.get_vod_analysis_groups())
        return (
            f"GNSS Research Site: {self.site_name}\n"
            f"  Receivers: {len(self.active_receivers)} configured, {rinex_groups} with data\n"
            f"  VOD Analyses: {len(self.active_vod_analyses)} configured, {vod_groups} with results"
        )


# Convenience function for default site
def create_default_site() -> GnssResearchSite:
    """
    Create a `GnssResearchSite` instance for the default site.

    Returns
    -------
    GnssResearchSite
        Instance for the ``DEFAULT_RESEARCH_SITE``.
    """
    return GnssResearchSite(DEFAULT_RESEARCH_SITE)


# Example usage and testing
if __name__ == "__main__":
    import tempfile

    from gnssvodpy.research_sites_config import DEFAULT_RESEARCH_SITE, RESEARCH_SITES

    print(RESEARCH_SITES['Rosalia']['rinex_store_path'])

    # # Create site manager
    # try:
    #     site = GnssResearchSite("Rosalia")
    #     print(f"Created site manager: {site}")
    #     print()

    #     # Validate configuration
    #     print("Validating site configuration...")
    #     site.validate_site_config()
    #     print("✓ Configuration is valid")
    #     print()

    #     # Get site summary
    #     summary = site.get_site_summary()
    #     print("Site Summary:")
    #     print(f"  Site: {summary['site_name']}")
    #     print(
    #         f"  Active receivers: {summary['site_config']['active_receivers']}"
    #     )
    #     print(
    #         f"  Active VOD analyses: {summary['site_config']['active_vod_analyses']}"
    #     )
    #     print(
    #         f"  RINEX groups with data: {summary['data_status']['rinex_groups_exist']}"
    #     )
    #     print(
    #         f"  VOD groups with results: {summary['data_status']['vod_groups_exist']}"
    #     )
    #     print()

    #     # Show configured receivers
    #     print("Configured Receivers:")
    #     for name, config in site.active_receivers.items():
    #         print(f"  {name}: {config['type']} - {config['description']}")
    #     print()

    #     # Show configured analyses
    #     print("Configured VOD Analyses:")
    #     for name, config in site.active_vod_analyses.items():
    #         print(
    #             f"  {name}: {config['canopy_receiver']} vs {config['reference_receiver']}"
    #         )

    # except Exception as e:
    #     print(f"Error: {e}")
