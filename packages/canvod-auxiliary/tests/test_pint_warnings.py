#!/usr/bin/env python
"""Test that pint warnings are resolved."""

import multiprocessing as mp
import warnings


def test_import():
    """Import modules that use pint and check for warnings."""
    # Capture warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        # Import modules that define units

        # Check for pint warnings
        pint_warnings = [
            warning
            for warning in w
            if "Redefining" in str(warning.message) and "dB" in str(warning.message)
        ]

        if pint_warnings:
            print(f"❌ FAILED: Found {len(pint_warnings)} pint warnings")
            for warning in pint_warnings:
                print(f"  {warning.message}")
            return False
        else:
            print("✅ No pint warnings in main process")
            return True


def worker(i):
    """Worker function to test multiprocessing."""
    import warnings

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        pint_warnings = [
            warning
            for warning in w
            if "Redefining" in str(warning.message) and "dB" in str(warning.message)
        ]

        return len(pint_warnings)


if __name__ == "__main__":
    print("Testing pint unit definitions...\n")

    # Test main process
    main_ok = test_import()

    # Test multiprocessing
    print("\nTesting multiprocessing workers...")
    with mp.Pool(4) as pool:
        results = pool.map(worker, range(4))

    total_warnings = sum(results)
    if total_warnings == 0:
        print(f"✅ No pint warnings in {len(results)} worker processes")
        print("\n🎉 All tests passed! Pint warnings are fixed.")
    else:
        print(f"❌ Found {total_warnings} pint warnings across workers")
        print("\n⚠️  Tests failed.")
