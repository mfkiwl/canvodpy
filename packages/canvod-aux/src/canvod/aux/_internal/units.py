"""
Unit registry for canvod-aux package.

Canonical source: This file is the authoritative version.
See /DUPLICATION_TRACKER.md for copy locations.
"""
import pint

# Use application registry to avoid redefinition warnings in multiprocessing
UREG: pint.UnitRegistry = pint.get_application_registry()

# Define custom units only if not already defined (idempotent)
# Note: 'dB' (decibel) already exists in pint by default, so we don't redefine it
if "dBHz" not in UREG:
    UREG.define("dBHz = 10 * log10(hertz)")

# Physical constants
SPEEDOFLIGHT: pint.Quantity = 299792458 * UREG.meter / UREG.second
