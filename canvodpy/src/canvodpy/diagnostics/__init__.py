"""Diagnostic utilities for canvodpy.

This package contains diagnostic scripts for testing and verifying
the canvodpy implementation against the original gnssvodpy.
"""

from canvodpy.diagnostics.timing_diagnostics_script import diagnose_processing

__all__ = ["diagnose_processing"]
