"""RINEX processing orchestration and Icechunk writing helpers."""

import json
import os
import time
from collections.abc import Generator
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from datetime import time as dt_time
from pathlib import Path
from tempfile import gettempdir

import dotenv
import numpy as np
import polars as pl
import pydantic_core
import xarray as xr
import zarr
from canvod.auxiliary.pipeline import AuxDataPipeline
from canvod.auxiliary.position import (
    ECEFPosition,
    add_spherical_coords_to_dataset,
    compute_spherical_coordinates,
)
from canvod.readers import DataDirMatcher, MatchedDirs, Rnxv3Obs
from canvod.store import GnssResearchSite
from canvod.utils.config import load_config
from canvod.utils.tools import get_version_from_pyproject
from icechunk.session import ForkSession
from icechunk.xarray import to_icechunk
from natsort import natsorted
from pydantic import ValidationError
from tqdm import tqdm

from canvodpy.globals import (
    AGENCY,
    FTP_SERVER,
    KEEP_RNX_VARS,
    PRODUCT_TYPE,
    RINEX_STORE_STRATEGY,
)
from canvodpy.logging import get_logger
from canvodpy.orchestrator.interpolator import (
    ClockConfig,
    ClockInterpolationStrategy,
    Sp3Config,
    Sp3InterpolationStrategy,
)
from canvodpy.settings import get_settings

dotenv.load_dotenv()

# ============================================================================
# MODULE-LEVEL FUNCTIONS (Required for ProcessPoolExecutor)
# ============================================================================


def preprocess_with_hermite_aux(
    rnx_file: Path,
    keep_vars: list[str] | None,
    aux_zarr_path: Path,
    receiver_position: ECEFPosition,
    receiver_type: str,
    keep_sids: list[str] | None = None,
) -> tuple[Path, xr.Dataset]:
    """Read RINEX and compute coordinates using Hermite-interpolated aux data from Zarr.

    This function runs in separate processes, so it must be at module level.
    The aux data has already been interpolated using proper Hermite splines.

    Parameters
    ----------
    rnx_file : Path
        RINEX file path
    keep_vars : List[str]
        Variables to keep
    aux_zarr_path : Path
        Path to preprocessed aux data Zarr store (with Hermite interpolation)
    receiver_position : ECEFPosition
        Receiver position (computed once)
    receiver_type : str
        Receiver type
    keep_sids : list[str] | None, default None
        List of specific SIDs to keep. If None, keeps all possible SIDs.

    Returns
    -------
    tuple[Path, xr.Dataset]
        File path and augmented dataset with phi, theta, r

    """
    _ = receiver_type
    log = get_logger(__name__).bind(file=str(rnx_file.name), receiver_type=receiver_type)
    
    try:
        start_time = time.time()
        log.info("rinex_preprocessing_started")

        # 1. Read RINEX file
        rnx = Rnxv3Obs(fpath=rnx_file, include_auxiliary=False)
        ds = rnx.to_ds(
            keep_rnx_data_vars=keep_vars,
            write_global_attrs=True,
            keep_sids=keep_sids,
        )
        ds.attrs["RINEX File Hash"] = rnx.file_hash

        # Filter variables
        if keep_vars:
            available_vars = [var for var in keep_vars if var in ds.data_vars]
            if available_vars:
                ds = ds[available_vars]

        # 2. Open preprocessed aux data (lazy - doesn't load everything into memory)
        aux_store = xr.open_zarr(aux_zarr_path, decode_timedelta=True)

        # 3. Select only the epochs matching this RINEX file (fast slice operation)
        # The aux data is already properly interpolated with Hermite splines
        aux_slice = aux_store.sel(epoch=ds.epoch, method="nearest")

        # 4. Find common SIDs between RINEX and aux data (inner join)
        # Some satellites in RINEX may not have ephemeris data, and vice versa
        rinex_sids = set(ds.sid.values)
        aux_sids = set(aux_slice.sid.values)
        common_sids = sorted(rinex_sids.intersection(aux_sids))

        if not common_sids:
            log.error(
                "sid_intersection_empty",
                rinex_sids=len(rinex_sids),
                aux_sids=len(aux_sids),
            )
            raise ValueError(
                f"No common SIDs found between RINEX ({len(rinex_sids)} sids) "
                f"and aux data ({len(aux_sids)} sids)"
            )

        # Filter both datasets to common SIDs
        ds = ds.sel(sid=common_sids)
        aux_slice = aux_slice.sel(sid=common_sids)

        log.debug(
            "sid_filtering_complete",
            rinex_sids=len(rinex_sids),
            aux_sids=len(aux_sids),
            common_sids=len(common_sids),
        )

        # 5. Compute spherical coordinates (φ, θ, r) from ephemerides
        ds_augmented = _compute_spherical_coords_fast(
            ds,
            aux_slice,
            receiver_position,
        )

        duration = time.time() - start_time
        log.info(
            "rinex_preprocessing_complete",
            duration_seconds=round(duration, 2),
            dataset_size=dict(ds_augmented.sizes),
        )
    except (OSError, RuntimeError, ValueError, ValidationError) as e:
        log.error(
            "rinex_preprocessing_failed",
            error=str(e),
            exception=type(e).__name__,
            exc_info=True,
        )
        raise
    
    return rnx_file, ds_augmented


def _compute_spherical_coords_fast(
    rinex_ds: xr.Dataset,
    aux_ds: xr.Dataset,
    rx_pos: ECEFPosition,
) -> xr.Dataset:
    """Compute spherical coordinates using shared utility function.

    This function is used by the parallel processor and must remain
    at module level for ProcessPoolExecutor serialization.
    """
    # Get satellite positions (already interpolated with Hermite splines)
    sat_x = aux_ds["X"].values
    sat_y = aux_ds["Y"].values
    sat_z = aux_ds["Z"].values

    # Compute using shared function
    r, theta, phi = compute_spherical_coordinates(sat_x, sat_y, sat_z, rx_pos)

    # Add to dataset using shared function
    rinex_ds = add_spherical_coords_to_dataset(rinex_ds, r, theta, phi)

    # Optionally add clock corrections if available
    if "clock" in aux_ds.data_vars:
        rinex_ds = rinex_ds.assign({"clock": aux_ds["clock"]})

    return rinex_ds


# ============================================================================
# Coordinated Parallel Writing to Icechunk
# ============================================================================


def _sanitize_ds_for_write(ds: xr.Dataset) -> xr.Dataset:
    # Make a shallow copy and strip obviously non-serializable attrs
    ds = ds.copy()
    # Keep only simple types in .attrs
    clean_attrs = {}
    for k, v in list(ds.attrs.items()):
        if isinstance(v, (str, int, float, bool, type(None), np.generic)):
            clean_attrs[k] = v
        # allow numpy scalars
        elif isinstance(v, (np.integer, np.floating, np.bool_)):
            clean_attrs[k] = v.item()
        # else drop it silently
    ds.attrs = clean_attrs

    # Normalize encodings to be conservative (avoid dtype surprises)
    for vname in ds.data_vars:
        var = ds[vname]
        enc = var.encoding or {}
        # ensure dtype is a concrete numpy dtype if present
        if "dtype" in enc:
            enc["dtype"] = np.dtype(var.dtype)
        # drop object encodings we don't control
        for bad in ("compressor", "filters", "chunks", "preferred_chunks"):
            enc.pop(bad, None)
        var.encoding = enc
    return ds


def write_initial_rinex_ds_to_store(
    *,
    ds: xr.Dataset,
    fork: ForkSession,
    group: str,
) -> ForkSession:
    """Write a new receiver group to the store."""
    ds = _sanitize_ds_for_write(ds)
    ds.to_zarr(
        fork.store,
        group=group,
        consolidated=False,
        mode="w",  # create group
    )
    return fork


def append_rinex_ds_to_store(
    *,
    ds: xr.Dataset,
    fork: ForkSession,
    group: str,
) -> ForkSession:
    """Append to an existing receiver group in the store."""
    ds = _sanitize_ds_for_write(ds)
    ds.to_zarr(
        fork.store,
        region="auto",
        group=group,
        consolidated=False,
        mode="a",
    )
    return fork


def worker_task(
    rinex_file: Path,
    keep_vars: list[str],
    aux_zarr_path: Path,
    receiver_position: ECEFPosition,
    receiver_type: str,
    receiver_name: str,
    fork: ForkSession,
    is_first: bool,
    keep_sids: list[str] | None = None,
) -> tuple[Path, ForkSession]:
    """Build an augmented dataset and write it to the given fork."""
    # 1) build augmented dataset
    fname, ds_augmented = preprocess_with_hermite_aux(
        rinex_file,
        keep_vars,
        aux_zarr_path,
        receiver_position,
        receiver_type,
        keep_sids,
    )

    # 2) write to this fork (initial or append)
    if is_first:
        write_initial_rinex_ds_to_store(
            ds=ds_augmented,
            fork=fork,
            group=receiver_name,
        )
    else:
        append_rinex_ds_to_store(
            ds=ds_augmented,
            fork=fork,
            group=receiver_name,
        )

    # 3) return ONLY pickleable things (Path + ForkSession)
    return fname, fork


def worker_task_append_only(
    rinex_file: Path,
    keep_vars: list[str],
    aux_zarr_path: Path,
    receiver_position: ECEFPosition,
    receiver_type: str,
    receiver_name: str,
    fork: ForkSession,
    keep_sids: list[str] | None = None,
) -> tuple[Path, ForkSession]:
    """Worker that only appends (group already exists)."""
    fname, ds_augmented = preprocess_with_hermite_aux(
        rinex_file,
        keep_vars,
        aux_zarr_path,
        receiver_position,
        receiver_type,
        keep_sids,
    )

    ds_clean = _sanitize_ds_for_write(ds_augmented)
    ds_clean.to_zarr(
        fork.store,
        group=receiver_name,
        mode="a",
        append_dim="epoch",
    )

    return fname, fork


def worker_task_with_region_auto(
    rinex_file: Path,
    keep_vars: list[str],
    aux_zarr_path: Path,
    receiver_position: ECEFPosition,
    receiver_type: str,
    receiver_name: str,
    fork: ForkSession,
    keep_sids: list[str] | None = None,
) -> ForkSession:
    """Worker uses region='auto' to write to correct position."""
    _fname, ds = preprocess_with_hermite_aux(
        rinex_file,
        keep_vars,
        aux_zarr_path,
        receiver_position,
        receiver_type,
        keep_sids,
    )

    ds_clean = _sanitize_ds_for_write(ds)
    ds_clean.to_zarr(
        fork.store,
        group=receiver_name,
        mode="a",
        region="auto",  # ✅ Let xarray infer the region
        consolidated=False,
    )

    return fork  # Return the modified fork


# ============================================================================
# MAIN (HALF-PARALLEL) PROCESSOR CLASS
# ============================================================================


class RinexDataProcessor:
    """Orchestrates RINEX data processing with optimized parallelization.

    Pipeline:
    1. Initialize auxiliary data (ephemerides, clock) - ONCE
    2. Preprocess aux data with Hermite splines to disk - ONCE per day
    3. Parallel process RINEX files using ProcessPoolExecutor
    4. Each worker reads its time slice from preprocessed Zarr
    5. Compute spherical coordinates and append to Icechunk store
    6. Yield final daily datasets

    Parameters
    ----------
    matched_data_dirs : MatchedDirs
        Matched directories for canopy and reference data
    site : GnssResearchSite
        Research site with Icechunk stores
    aux_file_path : Path, optional
        Root path for auxiliary files
    n_max_workers : int, default 12
        Maximum parallel workers (CPUs) for RINEX processing

    """

    def __init__(
        self,
        matched_data_dirs: MatchedDirs,
        site: GnssResearchSite,
        aux_file_path: Path | None = None,
        n_max_workers: int = 12,
    ) -> None:
        self.matched_data_dirs = matched_data_dirs
        self.site = site
        self.aux_file_path = aux_file_path
        self.n_max_workers = min(n_max_workers, os.cpu_count() or 12)
        self._logger = get_logger(__name__).bind(
            site=site.site_name,
            workers=self.n_max_workers,
        )

        config = load_config()
        self.keep_sids = config.sids.get_sids()

        self._logger.info(
            "processor_initialized",
            aux_file_path=str(aux_file_path) if aux_file_path else None,
            sid_filtering=len(self.keep_sids) if self.keep_sids else "all",
            cpu_count=os.cpu_count(),
        )

        # Initialize auxiliary data pipeline (loads SP3 and CLK files)
        self.aux_pipeline = self._initialize_aux_pipeline()

    def _initialize_aux_pipeline(self) -> AuxDataPipeline:
        """Initialize and load auxiliary data pipeline.

        Returns
        -------
        AuxDataPipeline
            Loaded pipeline with ephemerides and clock data

        """
        start_time = time.time()
        self._logger.info(
            "aux_pipeline_initialization_started",
            agency=AGENCY,
            product_type=PRODUCT_TYPE,
        )

        # Get settings for email configuration
        settings = get_settings()

        pipeline = AuxDataPipeline.create_standard(
            matched_dirs=self.matched_data_dirs,
            aux_file_path=self.aux_file_path,
            agency=AGENCY,
            product_type=PRODUCT_TYPE,
            ftp_server=FTP_SERVER,
            user_email=settings.get_user_email(),
            keep_sids=self.keep_sids,
        )

        # Load all auxiliary files into memory
        pipeline.load_all()

        duration = time.time() - start_time
        self._logger.info(
            "aux_pipeline_initialization_complete",
            duration_seconds=round(duration, 2),
            products=list(pipeline._cache.keys())
            if hasattr(pipeline, "_cache")
            else [],
        )
        return pipeline

    def _preprocess_aux_data_with_hermite(
        self,
        rinex_files: list[Path],
        output_path: Path,
    ) -> float:
        """Preprocess auxiliary data using proper interpolation strategies."""
        start_time = time.time()
        self._logger.info(
            "aux_preprocessing_started",
            rinex_files=len(rinex_files),
            output_path=str(output_path),
            interpolation_method="hermite_cubic",
        )

        # 1. Read first RINEX file to infer temporal properties
        self._logger.debug(
            "sampling_detection_started",
            sample_file=rinex_files[0].name,
        )
        first_rnx = Rnxv3Obs(fpath=rinex_files[0], include_auxiliary=False)
        first_ds = first_rnx.to_ds(keep_rnx_data_vars=[], write_global_attrs=True)

        # 2. Detect sampling interval
        time_diff = (first_ds.epoch[1] - first_ds.epoch[0]).values
        sampling_interval = float(time_diff / np.timedelta64(1, "s"))
        self._logger.info(
            "sampling_detected",
            sampling_interval_seconds=sampling_interval,
        )

        # 3. ✅ FIX: Generate complete 24-hour epoch grid instead of just first file
        # Get the day boundaries
        first_epoch = first_ds.epoch.values[0]
        day_start = np.datetime64(first_epoch.astype("datetime64[D]"))
        _day_end = day_start + np.timedelta64(1, "D")

        # Create uniform epoch grid for entire day
        n_epochs = int(24 * 3600 / sampling_interval)
        target_epochs = day_start + np.arange(n_epochs) * np.timedelta64(
            int(sampling_interval), "s"
        )

        self._logger.info(
            "epoch_grid_generated",
            n_epochs=len(target_epochs),
            day_start=str(target_epochs[0]),
            day_end=str(target_epochs[-1]),
        )

        # 4. Get auxiliary datasets from pipeline
        ephem_ds = self.aux_pipeline.get("ephemerides")
        clock_ds = self.aux_pipeline.get("clock")

        # 5. Interpolate ephemerides using Hermite splines
        self._logger.info(
            "ephemeris_interpolation_started",
            method="hermite_cubic_with_velocities",
        )
        sp3_config = Sp3Config(use_velocities=True, fallback_method="linear")
        sp3_interpolator = Sp3InterpolationStrategy(config=sp3_config)
        ephem_interp = sp3_interpolator.interpolate(ephem_ds, target_epochs)

        # Store interpolation metadata
        ephem_interp.attrs["interpolator_config"] = sp3_interpolator.to_attrs()

        # 6. Interpolate clock corrections using piecewise linear
        self._logger.info(
            "clock_interpolation_started",
            method="piecewise_linear",
        )
        clock_config = ClockConfig(window_size=9, jump_threshold=1e-6)
        clock_interpolator = ClockInterpolationStrategy(config=clock_config)
        clock_interp = clock_interpolator.interpolate(clock_ds, target_epochs)

        # Store interpolation metadata
        clock_interp.attrs["interpolator_config"] = clock_interpolator.to_attrs()

        # 7. Merge ephemerides and clock into single dataset
        aux_processed = xr.merge([ephem_interp, clock_interp])

        # 8. Write to Zarr
        self._logger.info(
            "aux_zarr_write_started",
            output_path=str(output_path),
            data_size=dict(aux_processed.sizes),
        )
        aux_processed.to_zarr(output_path, mode="w")

        duration = time.time() - start_time
        self._logger.info(
            "aux_preprocessing_complete",
            duration_seconds=round(duration, 2),
            data_size=dict(aux_processed.sizes),
            output_path=str(output_path),
        )

        return sampling_interval

    def _get_rinex_files(self, rinex_dir: Path) -> list[Path]:
        """Get sorted list of RINEX files from directory."""
        if not rinex_dir.exists():
            self._logger.warning("Directory does not exist: %s", rinex_dir)
            return []

        patterns = ["*.??o", "*.??O", "*.rnx", "*.RNX"]
        rinex_files = []

        for pattern in patterns:
            files = list(rinex_dir.glob(pattern))
            rinex_files.extend(files)

        return natsorted(rinex_files)

    def _parallel_process_with_processpool(
        self,
        rinex_files: list[Path],
        keep_vars: list[str],
        aux_zarr_path: Path,
        receiver_position: ECEFPosition,
        receiver_type: str,
    ) -> list[tuple[Path, xr.Dataset]]:
        """Parallel process RINEX files using ProcessPoolExecutor.

        Uses TRUE parallelism (no GIL) with separate processes.
        Each worker reads only its time slice from the Zarr store.

        Parameters
        ----------
        rinex_files : List[Path]
            List of RINEX files to process
        keep_vars : List[str]
            Variables to keep
        aux_zarr_path : Path
            Path to preprocessed aux Zarr store (with Hermite interpolation)
        receiver_position : ECEFPosition
            Receiver position (computed once)
        receiver_type : str
            Receiver type

        Returns
        -------
        List[tuple[Path, xr.Dataset]]
            List of (filename, augmented_dataset) tuples, sorted chronologically

        """
        start_time = time.time()
        self._logger.info(
            "parallel_processing_started",
            workers=self.n_max_workers,
            files=len(rinex_files),
            receiver_type=receiver_type,
        )

        results = []

        with ProcessPoolExecutor(max_workers=self.n_max_workers) as executor:
            # Submit all tasks
            futures = {
                executor.submit(
                    preprocess_with_hermite_aux,
                    rinex_file,
                    keep_vars,
                    aux_zarr_path,
                    receiver_position,
                    receiver_type,
                    self.keep_sids,
                ): rinex_file
                for rinex_file in rinex_files
            }

            # Collect results with progress bar
            for fut in tqdm(
                as_completed(futures),
                total=len(futures),
                desc=f"Processing {receiver_type}",
                unit="file",
            ):
                try:
                    fname, ds_augmented = fut.result()
                    results.append((fname, ds_augmented))
                except (OSError, RuntimeError, ValueError) as e:
                    failed_file = futures[fut].name
                    self._logger.error(
                        "file_processing_failed",
                        file=failed_file,
                        error=str(e),
                        exception=type(e).__name__,
                        exc_info=True,
                    )

        # Sort chronologically by filename
        results.sort(key=lambda x: x[0].name)

        duration = time.time() - start_time
        self._logger.info(
            "parallel_processing_complete",
            files_processed=len(results),
            files_total=len(rinex_files),
            files_failed=len(rinex_files) - len(results),
            duration_seconds=round(duration, 2),
            avg_time_per_file=round(duration / len(rinex_files), 2)
            if rinex_files
            else 0,
        )
        return results

    def _append_to_icechunk_slow(
        self,
        augmented_datasets: list[tuple[Path, xr.Dataset]],
        receiver_name: str,
        rinex_files: list[Path],
    ) -> None:
        """Sequentially append augmented datasets to Icechunk store.

        Uses the IcechunkDataReader pattern for proper deduplication
        and metadata tracking.

        Parameters
        ----------
        augmented_datasets : list[tuple[Path, xr.Dataset]]
            List of (filename, dataset) tuples
        receiver_name : str
            Receiver name (e.g., 'canopy', 'reference')
        rinex_files : list[Path]
            Original list of RINEX files (for context)

        """
        _ = rinex_files
        start_time = time.time()
        self._logger.info(
            "icechunk_write_started",
            receiver=receiver_name,
            datasets=len(augmented_datasets),
            strategy=RINEX_STORE_STRATEGY,
            mode="sequential",
        )

        groups = self.site.rinex_store.list_groups() or []
        version = get_version_from_pyproject()

        write_count = 0
        skip_count = 0
        append_count = 0

        for idx, (fname, ds) in enumerate(
            tqdm(augmented_datasets, desc=f"Appending {receiver_name}")
        ):
            token = set_file_context(fname)
            try:
                log = get_logger()
                rel_path = self.site.rinex_store.rel_path_for_commit(fname)

                # Get file metadata
                rinex_hash = ds.attrs.get("RINEX File Hash")
                if not rinex_hash:
                    log.warning(
                        "file_missing_hash",
                        file=fname.name,
                        action="skip",
                    )
                    continue

                start_epoch = np.datetime64(ds.epoch.min().values)
                end_epoch = np.datetime64(ds.epoch.max().values)

                # Check if file already exists
                exists, _matches = self.site.rinex_store.metadata_row_exists(
                    receiver_name, rinex_hash, start_epoch, end_epoch
                )

                # Cleanse dataset attributes
                ds_clean = self.site.rinex_store._cleanse_dataset_attrs(
                    ds,
                )

                # Handle different strategies based on RINEX_STORE_STRATEGY
                match (exists, RINEX_STORE_STRATEGY):
                    case (False, _) if receiver_name not in groups and idx == 0:
                        # Initial commit
                        msg = f"[v{version}] Initial commit: {rel_path}"
                        self.site.rinex_store.write_initial_group(
                            dataset=ds_clean,
                            group_name=receiver_name,
                            commit_message=msg,
                        )
                        groups.append(receiver_name)
                        log.info("initial_write", file=fname.name, group=receiver_name)
                        write_count += 1

                    case (True, "skip"):
                        log.debug(
                            "file_skipped", file=fname.name, reason="already_exists"
                        )
                        self.site.rinex_store.append_metadata(
                            group_name=receiver_name,
                            rinex_hash=rinex_hash,
                            start=start_epoch,
                            end=end_epoch,
                            snapshot_id="none",
                            action="skip",
                            commit_msg=f"Skipped {rel_path}",
                            dataset_attrs=ds_clean.attrs,
                        )
                        skip_count += 1

                    case (True, "append"):
                        msg = f"[v{version}] Appended {rel_path}"
                        self.site.rinex_store.append_to_group(
                            dataset=ds_clean,
                            group_name=receiver_name,
                            append_dim="epoch",
                            action="append",
                            commit_message=msg,
                        )
                        log.info("file_appended", file=fname.name)
                        append_count += 1

                    case (False, _):
                        msg = f"[v{version}] Wrote {rel_path}"
                        self.site.rinex_store.append_to_group(
                            dataset=ds_clean,
                            group_name=receiver_name,
                            append_dim="epoch",
                            action="write",
                            commit_message=msg,
                        )
                        log.info("file_written", file=fname.name)
                        write_count += 1

            except (OSError, RuntimeError, ValueError) as e:
                log = get_logger()
                log.error(
                    "icechunk_write_failed",
                    file=fname.name,
                    error=str(e),
                    exception=type(e).__name__,
                    exc_info=True,
                )
            finally:
                reset_context(token)

        duration = time.time() - start_time
        self._logger.info(
            "icechunk_write_complete",
            receiver=receiver_name,
            duration_seconds=round(duration, 2),
            files_written=write_count,
            files_appended=append_count,
            files_skipped=skip_count,
            total_files=len(augmented_datasets),
        )

    def _append_to_icechunk_incrementally(
        self,
        augmented_datasets: list[tuple[Path, xr.Dataset]],
        receiver_name: str,
        rinex_files: list[Path],
    ) -> None:
        """Batch append with single commit.

        This method:
        1. Opens ONE session for all data writes
        2. Uses only to_icechunk() within the session (no nested sessions)
        3. Makes ONE commit for all data
        4. Writes metadata separately after commit succeeds
        """
        _ = rinex_files
        log = self._logger
        version = get_version_from_pyproject()

        t_start = time.time()

        # STEP 1: Batch check which files exist
        log.info("Batch checking %s files...", len(augmented_datasets))
        t1 = time.time()

        file_hash_map = {
            fname: ds.attrs.get("RINEX File Hash") for fname, ds in augmented_datasets
        }

        valid_hashes = [h for h in file_hash_map.values() if h]
        existing_hashes = self.site.rinex_store.batch_check_existing(
            receiver_name, valid_hashes
        )

        t2 = time.time()
        log.info(
            "Batch check complete in %.2fs: %s/%s existing",
            t2 - t1,
            len(existing_hashes),
            len(augmented_datasets),
        )

        # STEP 2: Open session ONCE
        log.info("Opening Icechunk session...")
        t3 = time.time()
        with self.site.rinex_store.writable_session() as session:
            groups = self.site.rinex_store.list_groups() or []
            t4 = time.time()
            log.info("Session opened in %.2fs", t4 - t3)

            actions = {"initial": 0, "skipped": 0, "appended": 0, "written": 0}
            metadata_records = []  # Collect metadata to write after commit

            try:
                # STEP 3: Process all datasets using ONLY to_icechunk()
                log.info(
                    "Processing %s datasets...",
                    len(augmented_datasets),
                )
                t5 = time.time()

                for idx, (fname, ds) in enumerate(augmented_datasets):
                    # Progress logging
                    if idx % 20 == 0 and idx > 0:
                        elapsed = time.time() - t5
                        rate = idx / elapsed if elapsed > 0 else 0
                        log.info(
                            "  Progress: %s/%s (%.1f files/s)",
                            idx,
                            len(augmented_datasets),
                            rate,
                        )

                    token = set_file_context(fname)
                    try:
                        rel_path = self.site.rinex_store.rel_path_for_commit(fname)
                        rinex_hash = file_hash_map[fname]

                        if not rinex_hash:
                            log.debug("No hash for %s, skipping", fname)
                            continue

                        # Get time range for metadata
                        start_epoch = np.datetime64(ds.epoch.min().values)
                        end_epoch = np.datetime64(ds.epoch.max().values)

                        # Fast hash check
                        exists = rinex_hash in existing_hashes

                        # Cleanse dataset
                        ds_clean = self.site.rinex_store._cleanse_dataset_attrs(
                            ds,
                        )

                        # Collect metadata for ALL files (write later)
                        metadata_records.append(
                            {
                                "fname": fname,
                                "rinex_hash": rinex_hash,
                                "start": start_epoch,
                                "end": end_epoch,
                                "dataset_attrs": ds.attrs.copy(),
                                "exists": exists,
                                "rel_path": rel_path,
                            }
                        )

                        # Handle data writes using ONLY to_icechunk() with our session
                        match (exists, RINEX_STORE_STRATEGY):
                            case (False, _) if receiver_name not in groups and idx == 0:
                                # Initial group creation
                                to_icechunk(ds_clean, session, group=receiver_name)
                                groups.append(receiver_name)
                                actions["initial"] += 1
                                log.debug("Initial: %s", rel_path)

                            case (True, "skip"):
                                # File exists, skip writing data
                                actions["skipped"] += 1
                                log.debug("Skipped: %s", rel_path)

                            case (True, "append"):
                                # File exists but append anyway
                                to_icechunk(
                                    ds_clean,
                                    session,
                                    group=receiver_name,
                                    append_dim="epoch",
                                )
                                actions["appended"] += 1
                                log.debug("Appended: %s", rel_path)

                            case (False, _):
                                # New file, write it
                                to_icechunk(
                                    ds_clean,
                                    session,
                                    group=receiver_name,
                                    append_dim="epoch",
                                )
                                actions["written"] += 1
                                log.debug("Wrote: %s", rel_path)

                    except (OSError, RuntimeError, ValueError):
                        log.exception("Failed to process %s", fname.name)
                    finally:
                        reset_context(token)

                t6 = time.time()
                log.info("Dataset processing complete in %.2fs", t6 - t5)

                # STEP 4: Single commit for all data
                summary = ", ".join(f"{k}={v}" for k, v in actions.items() if v > 0)
                commit_msg = (
                    f"[v{version}] {receiver_name} "
                    f"{self.matched_data_dirs.yyyydoy}: {summary}"
                )

                log.info("Committing: %s", summary)
                t7 = time.time()
                snapshot_id = session.commit(commit_msg)
                t8 = time.time()
                log.info(
                    "Commit complete in %.2fs (snapshot: %s...)",
                    t8 - t7,
                    snapshot_id[:8],
                )

                # STEP 5: Write metadata (separate transactions after data commit)
                log.info(
                    "Writing metadata for %s files...",
                    len(metadata_records),
                )
                t9 = time.time()

                for record in metadata_records:
                    action = "skip" if record["exists"] else "write"
                    try:
                        self.site.rinex_store.append_metadata(
                            group_name=receiver_name,
                            rinex_hash=record["rinex_hash"],
                            start=record["start"],
                            end=record["end"],
                            snapshot_id=snapshot_id,
                            action=action,
                            commit_msg=f"{action}: {record['rel_path']}",
                            dataset_attrs=record["dataset_attrs"],
                        )
                    except (OSError, RuntimeError, ValueError):
                        log.warning(
                            "Failed to write metadata for %s",
                            record["fname"].name,
                        )

                    t10 = time.time()
                    log.info("Metadata written in %.2fs", t10 - t9)

                    # Timing summary
                    t_end = time.time()
                    log.info("\nTIMING BREAKDOWN:")
                    log.info("  Batch check:    %.2fs", t2 - t1)
                    log.info("  Open session:   %.2fs", t4 - t3)
                    log.info("  Process data:   %.2fs", t6 - t5)
                    log.info("  Commit:         %.2fs", t8 - t7)
                    log.info("  Metadata:       %.2fs", t10 - t9)
                    log.info("  TOTAL:          %.2fs", t_end - t_start)

                    log.info(
                        "Successfully processed %s files for '%s'",
                        len(augmented_datasets),
                        receiver_name,
                    )

            except (OSError, RuntimeError, ValueError):
                log.exception("Batch append failed")
                raise

    def _append_to_icechunk(
        self,
        augmented_datasets: list[tuple[Path, xr.Dataset]],
        receiver_name: str,
        rinex_files: list[Path],
    ) -> None:
        """Batch append with single commit.

        This method:
        1. Opens ONE session for all data writes
        2. Uses only to_icechunk() within the session (no nested sessions)
        3. Makes ONE commit for all data
        4. Writes metadata separately after commit succeeds
        """
        _ = rinex_files
        log = self._logger
        version = get_version_from_pyproject()

        t_start = time.time()

        # STEP 1: Batch check which files exist
        log.info("Batch checking %s files...", len(augmented_datasets))
        t1 = time.time()

        file_hash_map = {
            fname: ds.attrs.get("RINEX File Hash") for fname, ds in augmented_datasets
        }

        valid_hashes = [h for h in file_hash_map.values() if h]
        existing_hashes = self.site.rinex_store.batch_check_existing(
            receiver_name, valid_hashes
        )

        t2 = time.time()
        log.info(
            "Batch check complete in %.2fs: %s/%s existing",
            t2 - t1,
            len(existing_hashes),
            len(augmented_datasets),
        )

        # STEP 2: Open session ONCE
        log.info("Opening Icechunk session...")
        t3 = time.time()
        session = self.site.rinex_store.repo.writable_session(branch="main")
        groups = self.site.rinex_store.list_groups() or []
        t4 = time.time()
        log.info("Session opened in %.2fs", t4 - t3)

        actions = {"initial": 0, "skipped": 0, "appended": 0, "written": 0}
        metadata_records = []  # Collect metadata to write after commit

        try:
            # STEP 3: Process all datasets using ONLY to_icechunk()
            log.info(
                "Processing %s datasets...",
                len(augmented_datasets),
            )
            t5 = time.time()

            for idx, (fname, ds) in enumerate(augmented_datasets):
                # Progress logging
                if idx % 20 == 0 and idx > 0:
                    elapsed = time.time() - t5
                    rate = idx / elapsed if elapsed > 0 else 0
                    log.info(
                        "  Progress: %s/%s (%.1f files/s)",
                        idx,
                        len(augmented_datasets),
                        rate,
                    )

                token = set_file_context(fname)
                try:
                    rel_path = self.site.rinex_store.rel_path_for_commit(fname)
                    rinex_hash = file_hash_map[fname]

                    if not rinex_hash:
                        log.debug("No hash for %s, skipping", fname)
                        continue

                    # Get time range for metadata
                    start_epoch = np.datetime64(ds.epoch.min().values)
                    end_epoch = np.datetime64(ds.epoch.max().values)

                    # Fast hash check
                    exists = rinex_hash in existing_hashes

                    # Cleanse dataset
                    ds_clean = self.site.rinex_store._cleanse_dataset_attrs(
                        ds,
                    )

                    # Collect metadata for ALL files (write later)
                    metadata_records.append(
                        {
                            "fname": fname,
                            "rinex_hash": rinex_hash,
                            "start": start_epoch,
                            "end": end_epoch,
                            "dataset_attrs": ds.attrs.copy(),
                            "exists": exists,
                            "rel_path": rel_path,
                        }
                    )

                    # Handle data writes using ONLY to_icechunk() with our session
                    match (exists, RINEX_STORE_STRATEGY):
                        case (False, _) if receiver_name not in groups and idx == 0:
                            # Initial group creation
                            to_icechunk(ds_clean, session, group=receiver_name)
                            groups.append(receiver_name)
                            actions["initial"] += 1
                            log.debug("Initial: %s", rel_path)

                        case (True, "skip"):
                            # File exists, skip writing data
                            actions["skipped"] += 1
                            log.debug("Skipped: %s", rel_path)

                        case (True, "append"):
                            # File exists but append anyway
                            to_icechunk(
                                ds_clean,
                                session,
                                group=receiver_name,
                                append_dim="epoch",
                            )
                            actions["appended"] += 1
                            log.debug("Appended: %s", rel_path)

                        case (False, _):
                            # New file, write it
                            to_icechunk(
                                ds_clean,
                                session,
                                group=receiver_name,
                                append_dim="epoch",
                            )
                            actions["written"] += 1
                            log.debug("Wrote: %s", rel_path)

                except (OSError, RuntimeError, ValueError):
                    log.exception("Failed to process %s", fname.name)
                finally:
                    reset_context(token)

            t6 = time.time()
            log.info("Dataset processing complete in %.2fs", t6 - t5)

            # STEP 4: Single commit for all data
            summary = ", ".join(f"{k}={v}" for k, v in actions.items() if v > 0)
            commit_msg = (
                f"[v{version}] {receiver_name} "
                f"{self.matched_data_dirs.yyyydoy}: {summary}"
            )

            log.info("Committing data: %s", summary)
            t7 = time.time()
            t8 = time.time()

            # STEP 5: Metadata in a separate commit
            log.info(
                "Writing metadata for %s files...",
                len(metadata_records),
            )
            t9 = time.time()
            try:
                self.site.rinex_store.append_metadata_bulk(
                    group_name=receiver_name,
                    rows=metadata_records,
                    session=session,  # link metadata to the data commit
                )
            except (OSError, RuntimeError, ValueError):
                log.warning("Metadata commit failed")
            t10 = time.time()
            log.info("Metadata commit complete in %.2fs", t10 - t9)

            log.info("Committing: %s", summary)
            t7 = time.time()
            snapshot_id = session.commit(commit_msg)
            t8 = time.time()
            log.info(
                "Commit complete in %.2fs (snapshot: %s...)",
                t8 - t7,
                snapshot_id[:8],
            )

            expired = self.site.rinex_store.expire_old_snapshots(days=7)

            if expired:
                print(f"Expired {len(expired)} snapshots for cleanup.")

            # Timing summary
            t_end = time.time()
            log.info("\nTIMING BREAKDOWN:")
            log.info("  Batch check:    %.2fs", t2 - t1)
            log.info("  Open session:   %.2fs", t4 - t3)
            log.info("  Process data:   %.2fs", t6 - t5)
            log.info("  Commit:         %.2fs", t8 - t7)
            log.info("  Metadata:       %.2fs", t10 - t9)
            log.info("  TOTAL:          %.2fs", t_end - t_start)

            log.info(
                "Successfully processed %s files for '%s'",
                len(augmented_datasets),
                receiver_name,
            )

        except (OSError, RuntimeError, ValueError):
            log.exception("Batch append failed")
            raise

    def _append_to_icechunk_parallel(
        self,
        augmented_datasets: list[tuple[Path, xr.Dataset]],
        receiver_name: str,
        rinex_files: list[Path],
    ) -> None:
        """Batch append with parallel writes and a single commit.

        May be slower than sequential writes due to locking overhead.

        Strategy:
        - One writable session
        - ThreadPoolExecutor for dataset writes (safe: GIL release in zarr/numcodecs IO)
        - One commit for data
        - One commit for metadata
        """
        _ = rinex_files
        log = self._logger
        version = get_version_from_pyproject()

        t_start = time.time()

        # STEP 1: Batch check which files exist
        log.info("Batch checking %s files...", len(augmented_datasets))
        t1 = time.time()
        file_hash_map = {
            fname: ds.attrs.get("RINEX File Hash") for fname, ds in augmented_datasets
        }
        valid_hashes = [h for h in file_hash_map.values() if h]
        existing_hashes = self.site.rinex_store.batch_check_existing(
            receiver_name, valid_hashes
        )
        t2 = time.time()
        log.info(
            "Batch check complete in %.2fs: %s/%s existing",
            t2 - t1,
            len(existing_hashes),
            len(augmented_datasets),
        )

        # STEP 2: Open session ONCE
        log.info("Opening Icechunk session...")
        t3 = time.time()
        session = self.site.rinex_store.repo.writable_session(branch="main")
        groups = self.site.rinex_store.list_groups() or []
        t4 = time.time()
        log.info("Session opened in %.2fs", t4 - t3)

        actions = {"initial": 0, "skipped": 0, "appended": 0, "written": 0}
        metadata_records = []  # Collect metadata to write after commit

        try:
            log.info(
                "Processing %s datasets...",
                len(augmented_datasets),
            )
            t5 = time.time()

            def write_one(
                fname: Path,
                ds: xr.Dataset,
                exists: bool,
                idx: int,
            ) -> str:
                ds_clean = self.site.rinex_store._cleanse_dataset_attrs(
                    ds,
                )
                rel_path = self.site.rinex_store.rel_path_for_commit(fname)

                # Collect metadata
                start_epoch = np.datetime64(ds.epoch.min().values)
                end_epoch = np.datetime64(ds.epoch.max().values)
                metadata_records.append(
                    {
                        "fname": fname,
                        "rinex_hash": file_hash_map[fname],
                        "start": start_epoch,
                        "end": end_epoch,
                        "dataset_attrs": ds.attrs.copy(),
                        "exists": exists,
                        "rel_path": rel_path,
                    }
                )

                # Decide write strategy
                match (exists, RINEX_STORE_STRATEGY):
                    case (False, _) if receiver_name not in groups and idx == 0:
                        to_icechunk(ds_clean, session, group=receiver_name)
                        groups.append(receiver_name)
                        return "initial"
                    case (True, "skip"):
                        return "skipped"
                    case (True, "append"):
                        to_icechunk(
                            ds_clean, session, group=receiver_name, append_dim="epoch"
                        )
                        return "appended"
                    case (False, _):
                        to_icechunk(
                            ds_clean, session, group=receiver_name, append_dim="epoch"
                        )
                        return "written"

            # --- THREADPOOL EXECUTION ---
            futures = []
            with ThreadPoolExecutor(max_workers=8) as pool:
                for idx, (fname, ds) in enumerate(augmented_datasets):
                    rinex_hash = file_hash_map[fname]
                    if not rinex_hash:
                        continue
                    exists = rinex_hash in existing_hashes
                    if exists and RINEX_STORE_STRATEGY == "skip":
                        actions["skipped"] += 1
                        continue
                    futures.append(pool.submit(write_one, fname, ds, exists, idx))

                for fut in as_completed(futures):
                    result = fut.result()
                    actions[result] += 1

            t6 = time.time()
            log.info("Dataset processing complete in %.2fs", t6 - t5)

            # STEP 4: Single commit for all data
            summary = ", ".join(f"{k}={v}" for k, v in actions.items() if v > 0)
            commit_msg = (
                f"[v{version}] {receiver_name} "
                f"{self.matched_data_dirs.yyyydoy}: {summary}"
            )
            log.info("Committing data: %s", summary)
            t7 = time.time()
            snapshot_id = session.commit(commit_msg)
            t8 = time.time()
            log.info(
                "Commit complete in %.2fs (snapshot: %s...)",
                t8 - t7,
                snapshot_id[:8],
            )

            # STEP 5: Metadata in a separate commit
            log.info(
                "Writing metadata for %s files...",
                len(metadata_records),
            )
            t9 = time.time()
            try:
                meta_session = self.site.rinex_store.repo.writable_session(
                    branch="main"
                )
                self.site.rinex_store.append_metadata_bulk(
                    group_name=receiver_name,
                    rows=metadata_records,
                    session=meta_session,
                    snapshot_id=snapshot_id,
                )
                meta_commit_msg = (
                    f"[v{version}] metadata for {receiver_name} "
                    f"{self.matched_data_dirs.yyyydoy}"
                )
                meta_session.commit(meta_commit_msg)
            except (OSError, RuntimeError, ValueError):
                log.warning("Metadata commit failed")
            t10 = time.time()
            log.info("Metadata commit complete in %.2fs", t10 - t9)

            # Timing summary
            t_end = time.time()
            log.info("\nTIMING BREAKDOWN:")
            log.info("  Batch check:    %.2fs", t2 - t1)
            log.info("  Open session:   %.2fs", t4 - t3)
            log.info("  Process data:   %.2fs", t6 - t5)
            log.info("  Commit:         %.2fs", t8 - t7)
            log.info("  Metadata:       %.2fs", t10 - t9)
            log.info("  TOTAL:          %.2fs", t_end - t_start)
            log.info(
                "Successfully processed %s files for '%s'",
                len(augmented_datasets),
                receiver_name,
            )

        except (OSError, RuntimeError, ValueError):
            log.exception("Batch append failed")
            raise

    def _resolve_receiver_paths(self, receiver_type: str) -> tuple[Path, str | None]:
        """Resolve paths and receiver name for receiver type.

        Parameters
        ----------
        receiver_type : str
            Type of receiver ('canopy' or 'reference')

        Returns
        -------
        tuple[Path, str | None]
            (rinex_dir, receiver_name)

        """
        if receiver_type == "canopy":
            rinex_dir = self.matched_data_dirs.canopy_data_dir
        elif receiver_type == "reference":
            rinex_dir = self.matched_data_dirs.reference_data_dir
        else:
            msg = f"Unknown receiver type: {receiver_type}"
            raise ValueError(msg)

        # Get receiver name from site configuration
        receiver_name = None
        for name, config in self.site.active_receivers.items():
            if config.get("type") == receiver_type:
                receiver_name = name
                break

        return rinex_dir, receiver_name

    def parsed_rinex_data_gen_2_receivers(
        self,
        keep_vars: list[str] | None = None,
        receiver_types: list[str] | None = None,
    ) -> Generator[xr.Dataset]:
        """Generate datasets from RINEX files and append to Icechunk stores.

        Pipeline:
        1. Preprocess aux data ONCE per day with Hermite splines → Zarr
        2. Compute receiver position ONCE (shared for all receivers)
        3. For each receiver type (canopy, reference):
           a. Get list of RINEX files
           b. Parallel process with ProcessPoolExecutor
           c. Each worker: read RINEX + slice Zarr + compute φ, θ, r
           d. Sequential append to Icechunk store
           e. Yield final daily dataset

        Parameters
        ----------
        keep_vars : List[str], optional
            Variables to keep in datasets (default: from globals)
        receiver_types : List[str], optional
            Receiver types to process (default: ['canopy', 'reference'])

        Yields
        ------
        xr.Dataset
            Processed and augmented daily dataset for each receiver type

        """
        if receiver_types is None:
            receiver_types = ["canopy", "reference"]

        if keep_vars is None:
            keep_vars = KEEP_RNX_VARS

        self._logger.info(
            "Starting RINEX processing pipeline for: %s",
            receiver_types,
        )

        # Pre-flight: Get canopy files to infer sampling and compute position
        canopy_dir = self.matched_data_dirs.canopy_data_dir
        canopy_files = self._get_rinex_files(canopy_dir)
        if not canopy_files:
            msg = "No canopy RINEX files found - cannot infer sampling rate"
            raise ValueError(msg)

        # ====================================================================
        # STEP 1: Preprocess aux data ONCE per day with Hermite splines
        # ====================================================================
        aux_zarr_path = Path(gettempdir()) / (
            f"aux_{self.matched_data_dirs.yyyydoy.to_str()}.zarr"
        )

        if not aux_zarr_path.exists():
            self._logger.info(
                "Preprocessing aux data with Hermite splines (once per day)"
            )
            _sampling_interval = self._preprocess_aux_data_with_hermite(
                canopy_files, aux_zarr_path
            )
        else:
            self._logger.info(
                "Using existing preprocessed aux data: %s",
                aux_zarr_path,
            )

        # ====================================================================
        # STEP 2: Compute receiver position ONCE (same for all receivers)
        # ====================================================================
        first_rnx = Rnxv3Obs(fpath=canopy_files[0], include_auxiliary=False)
        first_ds = first_rnx.to_ds(keep_rnx_data_vars=[], write_global_attrs=True)
        receiver_position = ECEFPosition.from_ds_metadata(first_ds)
        self._logger.info(
            "Computed receiver position (shared): %s",
            receiver_position,
        )

        # ====================================================================
        # STEP 3: Process each receiver type
        # ====================================================================
        for receiver_type in receiver_types:
            self._logger.info("Processing receiver type: %s", receiver_type)

            # 3a. Resolve directories and receiver name
            rinex_dir, receiver_name = self._resolve_receiver_paths(receiver_type)

            if not receiver_name:
                self._logger.warning(
                    "No configured receiver for %s, skipping",
                    receiver_type,
                )
                continue

            # 3b. Get RINEX files for this receiver type
            rinex_files = self._get_rinex_files(rinex_dir)
            if not rinex_files:
                self._logger.warning(
                    "No RINEX files found in %s",
                    rinex_dir,
                )
                continue

            self._logger.info(
                "Found %s RINEX files to process",
                len(rinex_files),
            )

            # 3c. Parallel process with ProcessPoolExecutor
            augmented_datasets = self._parallel_process_with_processpool(
                rinex_files=rinex_files,
                keep_vars=keep_vars,
                aux_zarr_path=aux_zarr_path,
                receiver_position=receiver_position,
                receiver_type=receiver_name,
            )

            # 3d. Sequential append to Icechunk store
            self._append_to_icechunk(
                augmented_datasets=augmented_datasets,
                receiver_name=receiver_name,
                rinex_files=rinex_files,
            )

            # 3e. Yield final daily dataset
            # Read back from store to get complete daily dataset
            date_obj = self.matched_data_dirs.yyyydoy.date
            start_time = datetime.combine(date_obj, datetime.min.time())
            end_time = datetime.combine(date_obj, datetime.max.time())
            time_range = (start_time, end_time)

            daily_dataset = self.site.read_receiver_data(
                receiver_name=receiver_name, time_range=time_range
            )

            self._logger.info(
                "Yielding daily dataset for %s ('%s'): %s",
                receiver_type,
                receiver_name,
                dict(daily_dataset.sizes),
            )

            yield daily_dataset

    def parsed_rinex_data_gen(
        self,
        keep_vars: list[str] | None = None,
        receiver_configs: list[tuple[str, str, Path]] | None = None,
    ) -> Generator[tuple[str, xr.Dataset, float], None, None]:
        """Generate datasets from RINEX files and append to Icechunk stores.

        Pipeline:
        1. Preprocess aux data ONCE per day with Hermite splines → Zarr
        2. For each receiver:
        a. Compute receiver position from its first file
        b. Parallel process RINEX files with ProcessPoolExecutor
        c. Append to Icechunk store with receiver_name as group
        d. Yield final daily dataset

        Parameters
        ----------
        keep_vars : list[str], optional
            Variables to keep in datasets (default: from globals)
        receiver_configs : list[tuple[str, str, Path]], optional
            List of (receiver_name, receiver_type, data_dir) tuples.
            If None, uses default behavior with matched_data_dirs

        Yields
        ------
        xr.Dataset
            Processed and augmented daily dataset for each receiver

        """
        if receiver_configs is None:
            receiver_configs = self._get_default_receiver_configs()

        if keep_vars is None:
            keep_vars = KEEP_RNX_VARS

        pipeline_start = time.time()
        self._logger.info(
            "rinex_pipeline_started",
            receivers=len(receiver_configs),
            date=self.matched_data_dirs.yyyydoy.to_str(),
            keep_vars=keep_vars,
        )

        # ====================================================================
        # STEP 1: Preprocess aux data ONCE per day with Hermite splines
        # ====================================================================
        # Get first receiver files to infer sampling rate
        first_receiver_name, _first_receiver_type, first_data_dir = receiver_configs[0]
        first_files = self._get_rinex_files(first_data_dir)

        if not first_files:
            msg = (
                f"No RINEX files found for {first_receiver_name} - "
                "cannot infer sampling rate"
            )
            self._logger.error(
                "pipeline_failed",
                reason="no_rinex_files",
                receiver=first_receiver_name,
            )
            raise ValueError(msg)

        aux_zarr_path = Path(gettempdir()) / (
            f"aux_{self.matched_data_dirs.yyyydoy.to_str()}.zarr"
        )

        if not aux_zarr_path.exists():
            _sampling_interval = self._preprocess_aux_data_with_hermite(
                first_files, aux_zarr_path
            )
        else:
            self._logger.info(
                "aux_cache_hit",
                aux_zarr_path=str(aux_zarr_path),
            )

        # ====================================================================
        # STEP 2: Process each receiver independently
        # ====================================================================
        for receiver_name, receiver_type, data_dir in receiver_configs:
            receiver_start = time.time()

            self._logger.info(
                "receiver_processing_started",
                receiver=receiver_name,
                receiver_type=receiver_type,
                data_dir=str(data_dir),
            )

            # Get RINEX files for this receiver
            rinex_files = self._get_rinex_files(data_dir)
            if not rinex_files:
                self._logger.warning(
                    "no_rinex_files_found",
                    receiver=receiver_name,
                    data_dir=str(data_dir),
                )
                continue

            self._logger.info(
                "rinex_files_discovered",
                receiver=receiver_name,
                files=len(rinex_files),
            )

            # Compute receiver position from THIS receiver's first file
            first_rnx = None
            for _f, ff in enumerate(rinex_files):
                try:
                    first_rnx = Rnxv3Obs(fpath=ff, include_auxiliary=False)
                    break
                except ValidationError as e:
                    # Handle Pydantic validation errors
                    self._logger.warning(
                        "Validation error for %s: %s",
                        ff.name,
                        e,
                    )
                    # You can access specific error details:
                    for error in e.errors():
                        self._logger.debug("Field: %s", error["loc"])
                        self._logger.debug("Message: %s", error["msg"])
                        self._logger.debug("Type: %s", error["type"])
                except pydantic_core.ValidationError as e:
                    # Handle lower-level pydantic_core validation errors
                    self._logger.warning(
                        "Core validation error for %s: %s",
                        ff.name,
                        e,
                    )
                except (OSError, RuntimeError, ValueError) as e:
                    # Handle any other unexpected errors
                    self._logger.warning(
                        "Unexpected error for %s: %s",
                        ff.name,
                        e,
                    )

            if first_rnx is None:
                self._logger.error(
                    "No valid RINEX files found for %s",
                    receiver_name,
                )
                continue

            first_ds = first_rnx.to_ds(keep_rnx_data_vars=[], write_global_attrs=True)
            receiver_position = ECEFPosition.from_ds_metadata(first_ds)
            self._logger.info(
                "Computed receiver position for %s: %s",
                receiver_name,
                receiver_position,
            )

            # Parallel process with ProcessPoolExecutor
            augmented_datasets = self._parallel_process_with_processpool(
                rinex_files=rinex_files,
                keep_vars=keep_vars,
                aux_zarr_path=aux_zarr_path,
                receiver_position=receiver_position,
                receiver_type=receiver_name,
            )

            # Append to Icechunk with receiver_name as group
            self._append_to_icechunk(
                augmented_datasets=augmented_datasets,
                receiver_name=receiver_name,  # Use actual receiver name as group
                rinex_files=rinex_files,
            )

            # Yield final daily dataset
            date_obj = self.matched_data_dirs.yyyydoy.date
            start_time = datetime.combine(date_obj, datetime.min.time())
            end_time = datetime.combine(date_obj, datetime.max.time())
            time_range = (start_time, end_time)

            daily_dataset = self.site.read_receiver_data(
                receiver_name=receiver_name, time_range=time_range
            )

            receiver_duration = time.time() - receiver_start

            self._logger.info(
                "receiver_processing_complete",
                receiver=receiver_name,
                duration_seconds=round(receiver_duration, 2),
                dataset_size=dict(daily_dataset.sizes),
                epochs=len(daily_dataset.epoch) if "epoch" in daily_dataset.dims else 0,
                sids=len(daily_dataset.sid) if "sid" in daily_dataset.dims else 0,
            )

            yield receiver_name, daily_dataset, receiver_duration

        pipeline_duration = time.time() - pipeline_start
        self._logger.info(
            "rinex_pipeline_complete",
            duration_seconds=round(pipeline_duration, 2),
            receivers=len(receiver_configs),
        )

    def _get_default_receiver_configs(self) -> list[tuple[str, str, Path]]:
        """Get default receiver configs from matched_data_dirs."""
        configs = []

        # Get canopy receiver
        for name, config in self.site.active_receivers.items():
            if config.get("type") == "canopy":
                configs.append((name, "canopy", self.matched_data_dirs.canopy_data_dir))
                break

        # Get reference receiver
        for name, config in self.site.active_receivers.items():
            if config.get("type") == "reference":
                configs.append(
                    (name, "reference", self.matched_data_dirs.reference_data_dir)
                )
                break

        return configs

    def should_skip_day(
        self,
        receiver_types: list[str] | None = None,
        completeness_threshold: float = 1,
    ) -> tuple[bool, dict]:
        """Check if this day should be skipped based on existing data coverage.

        Parameters
        ----------
        receiver_types : list[str], optional
            Receiver types to check. Defaults to ['canopy', 'reference']
        completeness_threshold : float
            Fraction of expected epochs (default 0.95 = 95%)

        Returns
        -------
        tuple[bool, dict]
            (should_skip, coverage_info) where coverage_info contains details
            per receiver.

        """
        if receiver_types is None:
            receiver_types = ["canopy", "reference"]

        # Expected epochs for 24h at 30s sampling
        expected_epochs = int(24 * 3600 / 30)  # 2880
        required_epochs = int(expected_epochs * completeness_threshold)

        # Get datetime objects from YYYYDOY.date
        yyyydoy_date = self.matched_data_dirs.yyyydoy.date
        day_start = np.datetime64(
            datetime.combine(yyyydoy_date, dt_time.min),
            "ns",
        )
        day_end = np.datetime64(
            datetime.combine(yyyydoy_date, dt_time.max),
            "ns",
        )

        coverage_info = {}

        for receiver_type in receiver_types:
            # Get receiver name
            receiver_name = None
            for name, config in self.site.active_receivers.items():
                if config.get("type") == receiver_type:
                    receiver_name = name
                    break

            if not receiver_name:
                coverage_info[receiver_type] = {
                    "exists": False,
                    "reason": "No receiver configured",
                }
                return False, coverage_info

            try:
                # Read metadata table
                with self.site.rinex_store.readonly_session("main") as session:
                    zmeta = zarr.open_group(session.store, mode="r")[
                        f"{receiver_name}/metadata/table"
                    ]
                    data = {col: zmeta[col][:] for col in zmeta.array_keys()}
                    df = pl.DataFrame(data)

                # Cast datetime columns
                df = df.with_columns(
                    [
                        pl.col("start").cast(pl.Datetime("ns")),
                        pl.col("end").cast(pl.Datetime("ns")),
                    ]
                )

                # Filter to this day
                day_rows = df.filter(
                    (pl.col("start") >= day_start) & (pl.col("end") <= day_end)
                )

                if day_rows.is_empty():
                    coverage_info[receiver_type] = {
                        "exists": False,
                        "epochs": 0,
                        "expected": expected_epochs,
                        "percent": 0.0,
                    }
                    return False, coverage_info

                # Calculate total epochs
                day_rows = day_rows.with_columns(
                    [
                        (
                            (pl.col("end") - pl.col("start")).dt.total_seconds() / 30
                        ).alias("n_epochs")
                    ]
                )

                total_epochs = int(day_rows["n_epochs"].sum())
                percent = total_epochs / expected_epochs * 100

                coverage_info[receiver_type] = {
                    "exists": True,
                    "epochs": total_epochs,
                    "expected": expected_epochs,
                    "percent": percent,
                    "complete": total_epochs >= required_epochs,
                }

                if total_epochs < required_epochs:
                    return False, coverage_info

            except (KeyError, OSError, RuntimeError, ValueError) as e:
                coverage_info[receiver_type] = {
                    "exists": False,
                    "reason": str(e),
                    "epochs": 0,
                    "expected": expected_epochs,
                    "percent": 0.0,
                }
                return False, coverage_info

        # All receivers are complete
        return True, coverage_info

    def __repr__(self) -> str:
        return (
            "RinexDataProcessor("
            f"date={self.matched_data_dirs.yyyydoy.to_str()}, "
            f"site={self.site.site_name}, "
            f"aux_pipeline={self.aux_pipeline})"
        )


class DistributedRinexDataProcessor(RinexDataProcessor):
    """Under development. Use with caution.

    In `MyIcechunkStore`, attrs `MyIcechunkStore.compression_algorithm` and
    `MyIcechunkStore.config` must be disabled, so that any instance becomes
    serializable.

    Subclass of RinexDataProcessor that uses cooperative distributed writing.

    See:
        https://icechunk.io/en/latest/parallel/#cooperative-distributed-writes

    """

    def __init__(
        self,
        matched_data_dirs: MatchedDirs,
        site: GnssResearchSite,
        aux_file_path: Path | None = None,
        n_max_workers: int = 12,
    ) -> None:
        super().__init__(matched_data_dirs, site, aux_file_path, n_max_workers)

    def __repr__(self) -> str:
        return (
            "DistributedRinexDataProcessor("
            f"date={self.matched_data_dirs.yyyydoy.to_str()}, "
            f"site={self.site.site_name}, "
            f"aux_pipeline={self.aux_pipeline})"
        )

    def _cooperative_distributed_writing(
        self,
        rinex_files: list[Path],
        keep_vars: list[str],
        aux_zarr_path: Path,
        receiver_position: ECEFPosition,
        receiver_type: str,
        receiver_name: str,
    ) -> list[Path]:
        version = get_version_from_pyproject()
        repo = self.site.rinex_store.repo
        rinex_files_sorted = sorted(rinex_files, key=lambda p: p.name)

        # STEP 1: Initialize dataset structure with ALL files' time coordinates
        # This creates the full epoch dimension upfront
        session = repo.writable_session("main")

        # Collect all epochs from all files (or create empty structure)
        # Option A: Process all files first to get full time range
        all_epochs = []
        for rinex_file in rinex_files_sorted:
            _fname, ds = preprocess_with_hermite_aux(
                rinex_file,
                keep_vars,
                aux_zarr_path,
                receiver_position,
                receiver_type,
                self.keep_sids,
            )
            all_epochs.extend(ds.epoch.values)

        # Create empty dataset with full structure
        _first_fname, first_ds = preprocess_with_hermite_aux(
            rinex_files_sorted[0],
            keep_vars,
            aux_zarr_path,
            receiver_position,
            receiver_type,
            self.keep_sids,
        )

        # Initialize with full epoch dimension
        empty_ds = first_ds.isel(epoch=[]).expand_dims({"epoch": len(all_epochs)})
        empty_ds = empty_ds.assign_coords({"epoch": np.sort(all_epochs)})

        to_icechunk(empty_ds, session, group=receiver_name, mode="w")
        session.commit(f"Initialize {receiver_name} structure")

        # STEP 2: Now do cooperative distributed writes
        session = repo.writable_session("main")
        fork = session.fork()  # ONE fork

        remote_sessions = []

        with ProcessPoolExecutor(max_workers=self.n_max_workers) as ex:
            futures = [
                ex.submit(
                    worker_task_with_region_auto,
                    rinex_file,
                    keep_vars,
                    aux_zarr_path,
                    receiver_position,
                    receiver_type,
                    receiver_name,
                    fork,  # SAME fork to all workers
                    self.keep_sids,  # Pass keep_sids to worker
                )
                for rinex_file in rinex_files_sorted
            ]

            for fut in tqdm(
                as_completed(futures),
                total=len(futures),
                desc=f"Writing {receiver_name}",
                unit="file",
            ):
                returned_fork = fut.result()
                remote_sessions.append(returned_fork)

        # Merge all remote sessions
        session.merge(*remote_sessions)
        _snapshot_id = session.commit(
            f"[v{version}] Cooperative write for {receiver_name}"
        )

        return [f.name for f in rinex_files_sorted]

    def _append_to_icechunk_native_context_manager(
        self,
        augmented_datasets: list[tuple[Path, xr.Dataset]],
        receiver_name: str,
        rinex_files: list[Path],
    ) -> None:
        _ = rinex_files
        log = self._logger
        version = get_version_from_pyproject()

        # 1) Pre-check which hashes already exist
        file_hash_map = {
            fname: ds.attrs.get("RINEX File Hash") for fname, ds in augmented_datasets
        }
        valid_hashes = [h for h in file_hash_map.values() if h]
        existing_hashes = self.site.rinex_store.batch_check_existing(
            receiver_name, valid_hashes
        )

        actions = {"initial": 0, "skipped": 0, "appended": 0, "written": 0}
        metadata_records: list[dict] = []

        # 2) Open native Icechunk transaction (auto-commit)
        commit_msg = f"[v{version}] {receiver_name} {self.matched_data_dirs.yyyydoy}"

        with self.site.rinex_store.repo.transaction(
            branch="main", message=commit_msg
        ) as store:
            groups = self.site.rinex_store.list_groups() or []

            # 2a) Synchronous initial write if group does not exist (avoid race)
            if receiver_name not in groups:
                for fname, ds in augmented_datasets:
                    rinex_hash = file_hash_map.get(fname)
                    if rinex_hash and rinex_hash not in existing_hashes:
                        ds_init = self.site.rinex_store._cleanse_dataset_attrs(
                            ds,
                        )
                        ds_init.to_zarr(store, group=receiver_name, mode="a")

                        actions["initial"] += 1
                        groups.append(receiver_name)
                        break

            # 3) Prepare metadata rows and thread tasks
            def write_one(
                _fname: Path,
                ds: xr.Dataset,
                exists: bool,
                _rel_path: str,
                receiver_name: str,
                store: zarr.storage.BaseStore,
            ) -> str:
                ds_clean = self.site.rinex_store._cleanse_dataset_attrs(
                    ds,
                )

                if not exists and receiver_name not in groups:
                    ds_clean.to_zarr(store, group=receiver_name, mode="w")
                    return "initial"
                if exists and RINEX_STORE_STRATEGY == "skip":
                    return "skipped"
                if exists and RINEX_STORE_STRATEGY == "append":
                    ds_clean.to_zarr(
                        store, group=receiver_name, mode="a", append_dim="epoch"
                    )
                    return "appended"
                ds_clean.to_zarr(
                    store, group=receiver_name, mode="a", append_dim="epoch"
                )
                return "written"

            with ThreadPoolExecutor(max_workers=12) as pool:
                futures = []
                for fname, ds in augmented_datasets:
                    rinex_hash = file_hash_map.get(fname)
                    if not rinex_hash:
                        continue

                    exists = rinex_hash in existing_hashes
                    start_epoch = np.datetime64(ds.epoch.min().values)
                    end_epoch = np.datetime64(ds.epoch.max().values)
                    rel_path = self.site.rinex_store.rel_path_for_commit(fname)

                    # full-schema metadata row (snapshot_id can stay None)
                    metadata_records.append(
                        {
                            "hash": rinex_hash,
                            "start": start_epoch,
                            "end": end_epoch,
                            "action": "skip" if exists else "write",
                            "commit_msg": f"{'skip' if exists else 'write'}: {rel_path}",
                            "written_at": datetime.now(timezone.utc).isoformat(),
                            "attrs": json.dumps(ds.attrs),
                            "snapshot_id": None,
                            "write_strategy": "skip" if exists else "append",
                        }
                    )

                    # skip writing if exists & skip strategy
                    if exists and RINEX_STORE_STRATEGY == "skip":
                        actions["skipped"] += 1
                        continue

                    # IMPORTANT: pass store explicitly; do NOT close over outer name
                    futures.append(
                        pool.submit(
                            write_one, fname, ds, exists, rel_path, receiver_name, store
                        )
                    )

                for fut in as_completed(futures):
                    result = fut.result()
                    actions[result] += 1

            # 4) Bulk metadata into SAME transaction
            self.site.rinex_store.append_metadata_bulk_store(
                receiver_name, metadata_records, store
            )

        # 5) committed on exit
        log.info("Committed: %s", actions)

    def _append_to_icechunk_coord_distrbtd(
        self,
        augmented_datasets: list[tuple[Path, xr.Dataset]],
        receiver_name: str,
        rinex_files: list[Path],
    ) -> None:
        """Cooperative distributed append with Icechunk.

        - Uses cooperative_transaction so multiple workers can contribute.
        - True parallel writes with ProcessPoolExecutor.
        - Produces a single commit at the end.
        """
        _ = rinex_files
        log = self._logger
        version = get_version_from_pyproject()

        t_start = time.time()

        # STEP 1: Batch check which files exist
        log.info("Batch checking %s files...", len(augmented_datasets))
        t1 = time.time()

        file_hash_map = {
            fname: ds.attrs.get("RINEX File Hash") for fname, ds in augmented_datasets
        }

        valid_hashes = [h for h in file_hash_map.values() if h]
        existing_hashes = self.site.rinex_store.batch_check_existing(
            receiver_name, valid_hashes
        )

        t2 = time.time()
        log.info(
            "Batch check complete in %.2fs: %s/%s existing",
            t2 - t1,
            len(existing_hashes),
            len(augmented_datasets),
        )

        # STEP 2: Open session ONCE
        log.info("Opening Icechunk session...")
        t3 = time.time()
        session = self.site.rinex_store.repo.writable_session(branch="main")
        groups = self.site.rinex_store.list_groups() or []
        t4 = time.time()
        log.info("Session opened in %.2fs", t4 - t3)

        actions = {"initial": 0, "skipped": 0, "appended": 0, "written": 0}
        metadata_records = []  # Collect metadata to write after commit

        try:
            # STEP 3: Process all datasets using ONLY to_icechunk()
            log.info(
                "Processing %s datasets...",
                len(augmented_datasets),
            )
            t5 = time.time()

            for idx, (fname, ds) in enumerate(augmented_datasets):
                # Progress logging
                if idx % 20 == 0 and idx > 0:
                    elapsed = time.time() - t5
                    rate = idx / elapsed if elapsed > 0 else 0
                    log.info(
                        "  Progress: %s/%s (%.1f files/s)",
                        idx,
                        len(augmented_datasets),
                        rate,
                    )

                token = set_file_context(fname)
                try:
                    rel_path = self.site.rinex_store.rel_path_for_commit(fname)
                    rinex_hash = file_hash_map[fname]

                    if not rinex_hash:
                        log.debug("No hash for %s, skipping", fname)
                        continue

                    # Get time range for metadata
                    start_epoch = np.datetime64(ds.epoch.min().values)
                    end_epoch = np.datetime64(ds.epoch.max().values)

                    # Fast hash check
                    exists = rinex_hash in existing_hashes

                    # Cleanse dataset
                    ds_clean = self.site.rinex_store._cleanse_dataset_attrs(
                        ds,
                    )

                    # Collect metadata for ALL files (write later)
                    metadata_records.append(
                        {
                            "fname": fname,
                            "rinex_hash": rinex_hash,
                            "start": start_epoch,
                            "end": end_epoch,
                            "dataset_attrs": ds.attrs.copy(),
                            "exists": exists,
                            "rel_path": rel_path,
                        }
                    )

                    # Handle data writes using ONLY to_icechunk() with our session
                    match (exists, RINEX_STORE_STRATEGY):
                        case (False, _) if receiver_name not in groups and idx == 0:
                            # Initial group creation
                            to_icechunk(ds_clean, session, group=receiver_name)
                            groups.append(receiver_name)
                            actions["initial"] += 1
                            log.debug("Initial: %s", rel_path)

                        case (True, "skip"):
                            # File exists, skip writing data
                            actions["skipped"] += 1
                            log.debug("Skipped: %s", rel_path)

                        case (True, "append"):
                            # File exists but append anyway
                            to_icechunk(
                                ds_clean,
                                session,
                                group=receiver_name,
                                append_dim="epoch",
                            )
                            actions["appended"] += 1
                            log.debug("Appended: %s", rel_path)

                        case (False, _):
                            # New file, write it
                            to_icechunk(
                                ds_clean,
                                session,
                                group=receiver_name,
                                append_dim="epoch",
                            )
                            actions["written"] += 1
                            log.debug("Wrote: %s", rel_path)

                except (OSError, RuntimeError, ValueError):
                    log.exception("Failed to process %s", fname.name)
                finally:
                    reset_context(token)

            t6 = time.time()
            log.info("Dataset processing complete in %.2fs", t6 - t5)

            # STEP 4: Single commit for all data
            summary = ", ".join(f"{k}={v}" for k, v in actions.items() if v > 0)
            commit_msg = (
                f"[v{version}] {receiver_name} "
                f"{self.matched_data_dirs.yyyydoy}: {summary}"
            )

            # STEP 5: Write metadata (separate transactions after data commit)
            log.info(
                "Writing metadata for %s files...",
                len(metadata_records),
            )
            t9 = time.time()

            self.site.rinex_store.append_metadata_bulk(
                group_name=receiver_name,
                rows=metadata_records,
                session=session,
            )

            t10 = time.time()
            log.info("Metadata written in %.2fs", t10 - t9)

            log.info("Committing: %s", summary)
            t7 = time.time()
            snapshot_id = session.commit(commit_msg)
            t8 = time.time()
            log.info(
                "Commit complete in %.2fs (snapshot: %s...)",
                t8 - t7,
                snapshot_id[:8],
            )

            # Timing summary
            t_end = time.time()
            log.info("\nTIMING BREAKDOWN:")
            log.info("  Batch check:    %.2fs", t2 - t1)
            log.info("  Open session:   %.2fs", t4 - t3)
            log.info("  Process data:   %.2fs", t6 - t5)
            log.info("  Commit:         %.2fs", t8 - t7)
            log.info("  Metadata:       %.2fs", t10 - t9)
            log.info("  TOTAL:          %.2fs", t_end - t_start)

            log.info(
                "Successfully processed %s files for '%s'",
                len(augmented_datasets),
                receiver_name,
            )

        except (OSError, RuntimeError, ValueError):
            log.exception("Batch append failed")
            raise

    def parsed_rinex_data_gen_parallel(
        self,
        keep_vars: list[str] | None = None,
        receiver_types: list[str] | None = None,
    ) -> Generator[xr.Dataset, None, None]:
        """Generate datasets from RINEX files and append to Icechunk stores.

        Pipeline:
        1. Preprocess aux data ONCE per day with Hermite splines → Zarr
        2. Compute receiver position ONCE (shared for all receivers)
        3. For each receiver type (canopy, reference):
           a. Get list of RINEX files
           b. Parallel process with ProcessPoolExecutor
           c. Each worker: read RINEX + slice Zarr + compute φ, θ, r
           d. Sequential append to Icechunk store
           e. Yield final daily dataset

        Parameters
        ----------
        keep_vars : List[str], optional
            Variables to keep in datasets (default: from globals)
        receiver_types : List[str], optional
            Receiver types to process (default: ['canopy', 'reference'])

        Yields
        ------
        xr.Dataset
            Processed and augmented daily dataset for each receiver type

        """
        if receiver_types is None:
            receiver_types = ["canopy", "reference"]

        if keep_vars is None:
            keep_vars = KEEP_RNX_VARS

        self._logger.info(
            "Starting RINEX processing pipeline for: %s",
            receiver_types,
        )

        # Pre-flight: Get canopy files to infer sampling and compute position
        canopy_dir = self.matched_data_dirs.canopy_data_dir
        canopy_files = self._get_rinex_files(canopy_dir)
        if not canopy_files:
            msg = "No canopy RINEX files found - cannot infer sampling rate"
            raise ValueError(msg)

        # ====================================================================
        # STEP 1: Preprocess aux data ONCE per day with Hermite splines
        # ====================================================================
        aux_zarr_path = Path(gettempdir()) / (
            f"aux_{self.matched_data_dirs.yyyydoy.to_str()}.zarr"
        )

        if not aux_zarr_path.exists():
            self._logger.info(
                "Preprocessing aux data with Hermite splines (once per day)"
            )
            _sampling_interval = self._preprocess_aux_data_with_hermite(
                canopy_files, aux_zarr_path
            )
        else:
            self._logger.info(
                "Using existing preprocessed aux data: %s",
                aux_zarr_path,
            )

        # ====================================================================
        # STEP 2: Compute receiver position ONCE (same for all receivers)
        # ====================================================================
        first_rnx = Rnxv3Obs(fpath=canopy_files[0], include_auxiliary=False)
        first_ds = first_rnx.to_ds(keep_rnx_data_vars=[], write_global_attrs=True)
        receiver_position = ECEFPosition.from_ds_metadata(first_ds)
        self._logger.info(
            "Computed receiver position (shared): %s",
            receiver_position,
        )

        # ====================================================================
        # STEP 3: Process each receiver type
        # ====================================================================
        for receiver_type in receiver_types:
            self._logger.info("Processing receiver type: %s", receiver_type)

            # 3a. Resolve directories and receiver name
            rinex_dir, receiver_name = self._resolve_receiver_paths(receiver_type)

            if not receiver_name:
                self._logger.warning(
                    "No configured receiver for %s, skipping",
                    receiver_type,
                )
                continue

            # 3b. Get RINEX files for this receiver type
            rinex_files = self._get_rinex_files(rinex_dir)
            if not rinex_files:
                self._logger.warning(
                    "No RINEX files found in %s",
                    rinex_dir,
                )
                continue

            self._logger.info(
                "Found %s RINEX files to process",
                len(rinex_files),
            )

            # 3c. Parallel process with ProcessPoolExecutor
            _ = self._cooperative_distributed_writing(
                rinex_files=rinex_files,
                keep_vars=keep_vars,
                aux_zarr_path=aux_zarr_path,
                receiver_position=receiver_position,
                receiver_type=receiver_type,
                receiver_name=receiver_name,
            )

            # 3e. Yield final daily dataset
            # Read back from store to get complete daily dataset
            date_obj = self.matched_data_dirs.yyyydoy.date
            start_time = datetime.combine(date_obj, datetime.min.time())
            end_time = datetime.combine(date_obj, datetime.max.time())
            time_range = (start_time, end_time)

            daily_dataset = self.site.read_receiver_data(
                receiver_name=receiver_name, time_range=time_range
            )

            self._logger.info(
                "Yielding daily dataset for %s ('%s'): %s",
                receiver_type,
                receiver_name,
                dict(daily_dataset.sizes),
            )

            yield daily_dataset


if __name__ == "__main__":
    print(f"stared main block at {datetime.now(timezone.utc)}")

    matcher = DataDirMatcher(
        sky_dir_pattern=Path("01_reference/01_GNSS/01_raw"),
        canopy_dir_pattern=Path("02_canopy/01_GNSS/01_raw"),
    )

    site = GnssResearchSite(site_name="Rosalia")

    stats = {"processed": 0, "skipped": 0, "failed": 0}

    for md in matcher:
        yyyydoy_str = md.yyyydoy.to_str()

        if yyyydoy_str != "2024258":
            continue

        try:
            print(
                f"instantiating processor for {yyyydoy_str}: "
                f"{datetime.now(timezone.utc)}"
            )
            # Create processor first to check completeness
            processor = RinexDataProcessor(
                matched_data_dirs=md, site=site, n_max_workers=12
            )

            # Check if should skip
            if RINEX_STORE_STRATEGY in ["skip", "append"]:
                should_skip, coverage = processor.should_skip_day()

                if should_skip:
                    print(f"✓ Skipping {yyyydoy_str} - already complete:")
                    for receiver_type, info in coverage.items():
                        print(
                            f"  {receiver_type}: {info['epochs']}/"
                            f"{info['expected']} ({info['percent']:.1f}%)"
                        )
                    stats["skipped"] += 1
                    continue
                else:
                    print(f"⚠ Processing {yyyydoy_str} - incomplete coverage:")
                    for receiver_type, info in coverage.items():
                        if info["exists"]:
                            print(
                                f"  {receiver_type}: {info['epochs']}/"
                                f"{info['expected']} ({info['percent']:.1f}%)"
                            )
                        else:
                            print(f"  {receiver_type}: No data")

            # Process data
            print(
                f"about to call parsed_rinex_data_gen for {yyyydoy_str}: "
                f"{datetime.now(timezone.utc)}"
            )
            data_generator = processor.parsed_rinex_data_gen()
            print(f"calling next for canopy: {datetime.now(timezone.utc)}")
            canopy_ds = next(data_generator)
            print(f"calling next for reference: {datetime.now(timezone.utc)}")
            reference_ds = next(data_generator)

            stats["processed"] += 1
            print(f"✓ Processed {yyyydoy_str}")

        except (OSError, RuntimeError, ValueError) as e:
            print(f"✗ Failed {yyyydoy_str}: {e}")
            stats["failed"] += 1
