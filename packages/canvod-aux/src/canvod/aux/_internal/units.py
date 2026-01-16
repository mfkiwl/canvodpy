"""
Unit registry for canvod-aux package.

Canonical source: This file is the authoritative version.
See /DUPLICATION_TRACKER.md for copy locations.
"""
import pint

# Create unit registry
UREG = pint.UnitRegistry()

# Define custom units
UREG.define("dBHz = 10 * log10(hertz)")
UREG.define("dB = 10 * log10(ratio)")

# Physical constants
SPEEDOFLIGHT: pint.Quantity = 299792458 * UREG.meter / UREG.second
