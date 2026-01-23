from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Generator

import xarray as xr

from canvodpy.data_handler.data_handler import PairDataDirMatcher, PairMatchedDirs
from canvod.store import GnssResearchSite
from canvodpy.logging.context import get_logger
from canvodpy.orchestrator.processor import RinexDataProcessor
from canvodpy.utils.date_time import YYYYDOY


class PipelineOrchestrator:
    """
    Orchestrate RINEX processing pipeline for all receiver pairs at a site.

    Processes each unique receiver once per day, regardless of how many
    pairs it's involved in.

    Parameters
    ----------
    site : GnssResearchSite
        Research site configuration
    receiver_subpath_template : str
        Template for receiver subdirectory structure
    n_max_workers : int
        Maximum parallel workers per day
    dry_run : bool
        If True, only simulate processing without executing
    """

    def __init__(
        self,
        site: GnssResearchSite,
        receiver_subpath_template: str = "{receiver_dir}/01_GNSS/01_raw",
        n_max_workers: int = 12,
        dry_run: bool = False,
    ):
        self.site = site
        self.n_max_workers = n_max_workers
        self.dry_run = dry_run
        self._logger = get_logger().bind(site=site.site_name)

        self.pair_matcher = PairDataDirMatcher(
            site=site, receiver_subpath_template=receiver_subpath_template)

        self._logger.info(
            f"Initialized pipeline for site '{site.site_name}' "
            f"with {len(site.active_vod_analyses)} analysis pairs"
            f"{' [DRY RUN]' if dry_run else ''}")

    def _group_by_date_and_receiver(
            self) -> dict[str, dict[str, tuple[Path, str]]]:
        """
        Group receivers by date to avoid duplicate processing.

        Returns
        -------
        dict[str, dict[str, tuple[Path, str]]]
            {date: {receiver_name: (data_dir, receiver_type)}}
        """
        grouped = defaultdict(dict)

        for pair_dirs in self.pair_matcher:
            date_key = pair_dirs.yyyydoy.to_str()

            # Add canopy receiver if not already present
            if pair_dirs.canopy_receiver not in grouped[date_key]:
                grouped[date_key][pair_dirs.canopy_receiver] = (
                    pair_dirs.canopy_data_dir, 'canopy')

            # Add reference receiver if not already present
            if pair_dirs.reference_receiver not in grouped[date_key]:
                grouped[date_key][pair_dirs.reference_receiver] = (
                    pair_dirs.reference_data_dir, 'reference')

        return grouped

    def preview_processing_plan(self) -> dict:
        """
        Preview what would be processed without executing.

        Returns
        -------
        dict
            Summary of dates, receivers, and files to process
        """
        grouped = self._group_by_date_and_receiver()

        plan = {
            'site': self.site.site_name,
            'dates': [],
            'total_receivers': 0,
            'total_files': 0
        }

        for date_key, receivers in sorted(grouped.items()):
            date_info = {'date': date_key, 'receivers': []}

            for receiver_name, (data_dir,
                                receiver_type) in sorted(receivers.items()):
                files = list(data_dir.glob("*.2*o"))

                receiver_info = {
                    'name': receiver_name,
                    'type': receiver_type,
                    'files': len(files),
                    'dir': str(data_dir)
                }

                date_info['receivers'].append(receiver_info)
                plan['total_files'] += len(files)

            plan['dates'].append(date_info)
            plan['total_receivers'] += len(receivers)

        return plan

    def print_preview(self) -> None:
        """Print a formatted preview of the processing plan."""
        plan = self.preview_processing_plan()

        print(f"\n{'='*70}")
        print(f"PROCESSING PLAN FOR SITE: {plan['site']}")
        print(f"{'='*70}")
        print(f"Total unique receivers to process: {plan['total_receivers']}")
        print(f"Total RINEX files: {plan['total_files']}")
        print(f"{'='*70}\n")

        for date_info in plan['dates']:
            print(f"Date: {date_info['date']}")
            for receiver_info in date_info['receivers']:
                print(f"  {receiver_info['name']} ({receiver_info['type']}): "
                      f"{receiver_info['files']} files")
                print(f"    {receiver_info['dir']}")
            print()

    def process_by_date(
        self,
        keep_vars: list[str] | None = None,
        start_from: str | None = None,
        end_at: str | None = None,
    ) -> Generator[tuple[str, dict[str, xr.Dataset]], None, None]:
        """
        Process all receivers grouped by date.

        Each unique receiver is processed once per day with its actual name
        as the Icechunk group name.

        Parameters
        ----------
        keep_vars : list[str], optional
            Variables to keep in datasets
        start_from : str, optional
            YYYYDOY string to start from
        end_at : str, optional
            YYYYDOY string to end at

        Yields
        ------
        tuple[str, dict[str, xr.Dataset]]
            Date string and dict of {receiver_name: dataset}
        """
        if self.dry_run:
            self._logger.info(
                "DRY RUN: Simulating processing without execution")
            self.print_preview()
            return

        grouped = self._group_by_date_and_receiver()

        for date_key, receivers in sorted(grouped.items()):
            # Filter dates before processing
            if start_from and date_key < start_from:
                self._logger.info(f"Skipping {date_key} - before {start_from}")
                continue

            if end_at and date_key > end_at:
                self._logger.info(f"Stopping at {date_key} - after {end_at}")
                break

            self._logger.info(
                f"Processing date {date_key} with {len(receivers)} unique receivers"
            )

            # Build receiver_configs for this date
            receiver_configs = [
                (receiver_name, receiver_type, data_dir)
                for receiver_name, (data_dir,
                                    receiver_type) in sorted(receivers.items())
            ]

            # Convert to MatchedDirs for aux data (use any dir, aux is date-based)
            from canvodpy.data_handler.data_handler import MatchedDirs
            from canvodpy.utils.date_time import YYYYDOY

            first_data_dir = receiver_configs[0][2]
            matched_dirs = MatchedDirs(
                canopy_data_dir=first_data_dir,
                sky_data_dir=first_data_dir,  # Dummy, only date matters for aux
                yyyydoy=YYYYDOY.from_str(date_key))

            # Process all receivers for this date in one go
            try:
                processor = RinexDataProcessor(
                    matched_data_dirs=matched_dirs,
                    site=self.site,
                    n_max_workers=self.n_max_workers)
            except RuntimeError as e:
                if "Failed to download" in str(e):
                    self._logger.warning(
                        f"Skipping {date_key} - auxiliary files not available: {e}"
                    )
                    continue
                else:
                    raise

            # Process with actual receiver names and directories
            datasets = {}
            timings = {}
            try:
                for receiver_name, ds, proc_time in processor.parsed_rinex_data_gen(
                        keep_vars=keep_vars,
                        receiver_configs=receiver_configs):
                    # Don't overwrite receiver_name - it's already correct from the generator
                    datasets[receiver_name] = ds
                    timings[receiver_name] = proc_time
            except Exception as e:
                self._logger.error(
                    f"Error processing RINEX data for date {date_key}: {e}")
                continue

            yield date_key, datasets, timings


class SingleReceiverProcessor:
    """
    Process a single receiver for one day.

    Parameters
    ----------
    receiver_name : str
        Actual receiver name (e.g., 'canopy_01', 'reference_01')
    receiver_type : str
        Receiver type ('canopy' or 'reference')
    data_dir : Path
        Directory containing RINEX files
    yyyydoy : YYYYDOY
        Date to process
    site : GnssResearchSite
        Research site
    n_max_workers : int
        Maximum parallel workers
    """

    def __init__(self,
                 receiver_name: str,
                 receiver_type: str,
                 data_dir: Path,
                 yyyydoy: YYYYDOY,
                 site: GnssResearchSite,
                 n_max_workers: int = 12):
        self.receiver_name = receiver_name
        self.receiver_type = receiver_type
        self.data_dir = data_dir
        self.yyyydoy = yyyydoy
        self.site = site
        self.n_max_workers = n_max_workers
        self._logger = get_logger().bind(receiver=receiver_name,
                                         date=yyyydoy.to_str())

    def _get_rinex_files(self) -> list[Path]:
        """Get sorted list of RINEX files."""
        files = sorted(self.data_dir.glob("*.2*o"))
        return files

    def process(self, keep_vars: list[str] | None = None) -> xr.Dataset:
        """
        Process all RINEX files for this receiver and write to Icechunk.

        Parameters
        ----------
        keep_vars : list[str], optional
            Variables to keep in datasets

        Returns
        -------
        xr.Dataset
            Final daily dataset for this receiver
        """
        rinex_files = self._get_rinex_files()

        if not rinex_files:
            raise ValueError(f"No RINEX files found in {self.data_dir}")

        self._logger.info(f"Processing {len(rinex_files)} RINEX files")

        # Create matched dirs for aux data (using first available dir as dummy)
        from canvodpy.data_handler.data_handler import MatchedDirs
        matched_dirs = MatchedDirs(
            canopy_data_dir=self.data_dir,
            sky_data_dir=self.data_dir,  # Dummy, aux data is date-based
            yyyydoy=self.yyyydoy)

        # Initialize processor with receiver name override
        processor = RinexDataProcessor(matched_data_dirs=matched_dirs,
                                       site=self.site,
                                       n_max_workers=self.n_max_workers)

        # Process with actual receiver name (NOT type)
        # This requires modifying RinexDataProcessor to accept receiver_name parameter
        ds = processor._process_receiver(
            rinex_files=rinex_files,
            receiver_name=self.receiver_name,  # Use actual name as group
            receiver_type=self.receiver_type,
            keep_vars=keep_vars)

        return ds


if __name__ == "__main__":

    # from pathlib import Path

    # from canvodpy.globals import KEEP_RNX_VARS

    # # from canvodpy.orchestrator.pipeline_orchestrator import PipelineOrchestrator

    # # Initialize site
    # site = GnssResearchSite(site_name="Rosalia")

    # # # Process only 1 file per receiver
    # orchestrator = PipelineOrchestrator(site=site)
    # # orchestrator.print_preview()
    # for pair_dirs, datasets in orchestrator.process_all_pairs():
    #     print(f"Processed: {pair_dirs.pair_name}")

    from canvodpy.globals import KEEP_RNX_VARS
    from canvod.store import GnssResearchSite

    site = GnssResearchSite(site_name="Rosalia")

    # Test with dry run first
    orchestrator = PipelineOrchestrator(
        site=site,
        dry_run=False,
    )

    # Process all dates
    for date_key, datasets in orchestrator.process_by_date(
            keep_vars=KEEP_RNX_VARS):
        print(f"\nProcessed date: {date_key}")
        for receiver_name, ds in datasets.items():
            print(f"  {receiver_name}: {dict(ds.sizes)}")
