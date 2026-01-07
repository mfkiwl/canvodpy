"""
canvodpy - Umbrella package for the canVOD ecosystem.

This package provides convenient access to all canvod.* subpackages.

Example:
    >>> import canvodpy
    >>> from canvod.readers import Rnxv3Obs
    >>> from canvod.grids import HemiGrid
"""

__version__ = "0.1.0"

# Re-export subpackages for convenience
try:
    from canvod import readers, aux, grids, vod, store, viz
except ImportError:
    # Subpackages not yet installed
    pass

__all__ = ["readers", "aux", "grids", "vod", "store", "viz"]
