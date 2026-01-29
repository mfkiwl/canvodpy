"""canvodpy: GNSS Vegetation Optical Depth Analysis.

A modern Python package for processing GNSS data and calculating
vegetation optical depth (VOD) using the tau-omega model.

Quick Start
-----------
Three levels of API to match your needs:

**Level 1: Simple (one-liners)**
    >>> from canvodpy import process_date, calculate_vod
    >>> data = process_date("Rosalia", "2025001")
    >>> vod = calculate_vod("Rosalia", "canopy_01", "reference_01", "2025001")

**Level 2: Object-oriented (more control)**
    >>> from canvodpy import Site, Pipeline
    >>> site = Site("Rosalia")
    >>> pipeline = site.pipeline()
    >>> data = pipeline.process_date("2025001")
    >>> vod = pipeline.calculate_vod("canopy_01", "reference_01", "2025001")

**Level 3: Low-level (full control)**
    >>> from canvod.store import GnssResearchSite
    >>> from canvod.vod import VODCalculator
    >>> # Direct access to all internals

Package Structure
-----------------
- canvod.readers - RINEX file parsing
- canvod.aux - Auxiliary data (ephemeris, clocks)
- canvod.grids - Hemisphere grid structures
- canvod.vod - VOD calculation algorithms
- canvod.viz - 2D/3D visualization
- canvod.store - Icechunk data storage

Configuration
-------------
Site configurations are stored in `research_sites_config.py`.
Default variables and settings are in `globals.py`.

Examples
--------
Process one day of data:
    >>> from canvodpy import process_date
    >>> data = process_date("Rosalia", "2025001")

Process a week:
    >>> from canvodpy import Pipeline
    >>> pipeline = Pipeline("Rosalia")
    >>> for date, datasets in pipeline.process_range("2025001", "2025007"):
    ...     print(f"Processed {date}")

Calculate and visualize VOD:
    >>> from canvodpy import calculate_vod
    >>> from canvod.viz import HemisphereVisualizer
    >>> vod = calculate_vod("Rosalia", "canopy_01", "reference_01", "2025001")
    >>> viz = HemisphereVisualizer()
    >>> fig = viz.plot_2d(vod)

"""

from canvodpy.api import (
    Pipeline,
    Site,
    calculate_vod,
    preview_processing,
    process_date,
)
from canvodpy.globals import KEEP_RNX_VARS
from canvodpy.research_sites_config import DEFAULT_RESEARCH_SITE, RESEARCH_SITES

# ============================================================================
# Level 3 API: Re-export subpackages for advanced users
# ============================================================================

# Lazy import subpackages on access to avoid circular dependencies
def __getattr__(name: str):
    """Lazy import subpackages when accessed."""
    _subpackages = {
        "aux": "canvod.aux",
        "grids": "canvod.grids", 
        "readers": "canvod.readers",
        "store": "canvod.store",
        "viz": "canvod.viz",
        "vod": "canvod.vod",
    }
    
    if name in _subpackages:
        import importlib
        import sys
        module = importlib.import_module(_subpackages[name])
        # Cache the imported module (can't use globals() as it's shadowed by canvodpy.globals)
        setattr(sys.modules[__name__], name, module)
        return module
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

# ============================================================================
# Version
# ============================================================================

__version__ = "0.1.0"

# ============================================================================
# Public API
# ============================================================================

__all__ = [  # noqa: RUF022
    # Version
    "__version__",

    # High-level API (most users)
    "Site",
    "Pipeline",
    "process_date",
    "calculate_vod",
    "preview_processing",

    # Configuration (useful for all users)
    "KEEP_RNX_VARS",
    "RESEARCH_SITES",
    "DEFAULT_RESEARCH_SITE",

    # Subpackages (advanced users)
    "readers",
    "aux",
    "grids",
    "vod",
    "viz",
    "store",
]
