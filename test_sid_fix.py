#!/usr/bin/env python3
"""Quick test to verify SID filtering works."""

import sys

print("=" * 80, flush=True)
print("SID FILTERING TEST", flush=True)
print("=" * 80, flush=True)

try:
    print("\n1. Importing modules...", flush=True)
    from canvodpy.globals import KEEP_RNX_VARS
    from canvod.store import GnssResearchSite
    from canvodpy.orchestrator.pipeline import PipelineOrchestrator
    
    print(f"   KEEP_RNX_VARS = {KEEP_RNX_VARS}", flush=True)
    
    print("\n2. Initializing site...", flush=True)
    site = GnssResearchSite(site_name="Rosalia")
    print(f"   Site: {site.site_name}", flush=True)
    
    print("\n3. Creating orchestrator...", flush=True)
    orchestrator = PipelineOrchestrator(site=site, dry_run=False)
    print("   Orchestrator created", flush=True)
    
    print("\n4. Starting processing loop (processing first date only)...", flush=True)
    counter = 0
    for date_key, _datasets, _receiver_times in orchestrator.process_by_date(
            keep_vars=KEEP_RNX_VARS, start_from=None, end_at=None):
        print(f"\n   ✅ Processed date: {date_key}", flush=True)
        counter += 1
        if counter >= 1:  # Only process first date
            print("   Stopping after first date for testing", flush=True)
            break
    
    print("\n" + "=" * 80, flush=True)
    print("✅ TEST COMPLETE - NO ERRORS!", flush=True)
    print("=" * 80, flush=True)

except Exception as e:
    print(f"\n❌ ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
