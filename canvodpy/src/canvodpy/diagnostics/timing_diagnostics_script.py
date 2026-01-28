"""
Diagnostic script for canvodpy - analogon to gnssvodpy
timing_diagnostics_script.py.

This script processes RINEX data using the new canvodpy architecture.
Compare results with gnssvodpy to verify correct implementation.
"""
import gc
import time
from datetime import datetime
from pathlib import Path

from canvod.store import GnssResearchSite
from dask.tests.test_base import da

from canvodpy.globals import KEEP_RNX_VARS
from canvodpy.orchestrator import PipelineOrchestrator


def diagnose_processing(
    start_from: str | None = None,
    end_at: str | None = None,
) -> None:
    """
    Run diagnostic processing with canvodpy pipeline.

    This is the analogon to gnssvodpy's timing_diagnostics_script.py.
    Use this to verify that the new implementation produces the same results.

    Parameters
    ----------
    start_from : str, optional
        YYYYDOY string to start from (e.g., "2025278"). If None, starts from
        beginning.
    end_at : str, optional
        YYYYDOY string to end at (e.g., "2025280"). If None, processes all
        remaining.

    Examples
    --------
    >>> # Process everything
    >>> diagnose_processing()

    >>> # Start from a specific date
    >>> diagnose_processing(start_from="2024183")  # July 1, 2024

    >>> # Process a specific range
    >>> diagnose_processing(start_from="2025278", end_at="2025280")
    """

    print("=" * 80)
    print("CANVODPY DIAGNOSTIC PROCESSING")
    print("=" * 80)
    print(f"Start time: {datetime.now()}")
    print(f"KEEP_RNX_VARS: {KEEP_RNX_VARS}")
    if start_from:
        print(f"Starting from: {start_from}")
    if end_at:
        print(f"Ending at: {end_at}")
    print()

    # Initialize site and orchestrator
    site = GnssResearchSite(site_name="Rosalia")
    orchestrator = PipelineOrchestrator(site=site, dry_run=False)

    counter = 0
    garbage_collect = 0
    days_since_rechunk = 0

    # Main processing loop
    for date_key, datasets, receiver_times in orchestrator.process_by_date(
            keep_vars=KEEP_RNX_VARS, start_from=start_from, end_at=end_at):

        day_start_time = datetime.now()

        print(f"\n{'='*80}")
        print(f"Processing {date_key}")
        print(f"{'='*80}\n")

        try:
            # Track timing per receiver
            for receiver_name, ds in datasets.items():
                print(f"\n{'─'*80}")
                print(f"{receiver_name.upper()} PROCESSING")
                print(f"{'─'*80}")
                print(f"  Dataset shape: {dict(ds.sizes)}")
                print(
                    "  Processing time: "
                    f"{receiver_times[receiver_name]:.2f}s"
                )

            day_end_time = datetime.now()
            # Calculate actual total from receiver times
            total_time = sum(receiver_times.values())

            # Summary
            print(f"\n{'='*80}")
            print("SUMMARY")
            print(f"{'='*80}")
            for receiver_name, ds in datasets.items():
                print(
                    f"{receiver_name}: {dict(ds.sizes)} "
                    f"({receiver_times[receiver_name]:.2f}s)"
                )
            print(f"Total time: {total_time:.2f}s")
            print(f"\n✓ Successfully processed {date_key}")

            days_since_rechunk += 1

        except Exception as e:
            print(f"\n✗ Failed {date_key}: {e}")
            import traceback
            traceback.print_exc()

        finally:
            counter += 1
            garbage_collect += 1

            # Rechunking logic commented out (as in original)
            # if days_since_rechunk >= 2:
            #     print(f"\n{'='*80}")
            #     print("🔄 RECHUNKING STORE (every 2 days)")
            #     print(f"{'='*80}\n")
            #     # Rechunking logic would go here
            #     days_since_rechunk = 0

        # Garbage collection every 5 days
        if garbage_collect % 5 == 0:
            print(f"\n💤 Pausing for 60s before garbage collection...")
            time.sleep(60)
            print(f"\n🗑️  Running garbage collection...")
            gc.collect()
            print(f"✓ Garbage collection done")

        # Optional: Stop after N days for diagnostics
        # if counter == 30:
        #     print(f"\n🛑 Reached 30 days of processing, stopping for diagnostics.")
        #     break

    print(f"\n{'='*80}")
    print(f"End time: {datetime.now()}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    # Process everything
    # diagnose_processing()

    # Start from a specific date
    # diagnose_processing(start_from="2024183")  # July 1, 2024

    # Process a specific range
    # diagnose_processing(start_from="2025278", end_at="2025280")

    # Process specific test range (Oct 26, 2025)
    # diagnose_processing(start_from="2025299", end_at="2025300")

    # Initialize site and orchestrator
    site = GnssResearchSite(site_name="Rosalia")
    orchestrator = PipelineOrchestrator(site=site, dry_run=False)

    counter = 0
    garbage_collect = 0
    days_since_rechunk = 0

    # Main processing loop

    for date_key, datasets, receiver_times in orchestrator.process_by_date(
            keep_vars=KEEP_RNX_VARS, start_from=None, end_at=None):
        print(date_key)
