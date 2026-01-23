"""canvodpy: GNSS Vegetation Optical Depth Analysis

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

__version__ = "0.1.0"

# ============================================================================
# Level 1 & 2 API: High-level user interface
# ============================================================================

from canvodpy.api import (
    # Classes
    Site,
    Pipeline,
    # Convenience functions
    process_date,
    calculate_vod,
    preview_processing,
)

# ============================================================================
# Level 3 API: Re-export subpackages for advanced users
# ============================================================================

# Import subpackages (but don't expose everything in __all__)
try:
    from canvod import readers, aux, grids, vod, viz, store
except ImportError:
    # Subpackages not installed - that's okay
    pass

# ============================================================================
# Configuration and utilities
# ============================================================================

from canvodpy.globals import KEEP_RNX_VARS
from canvodpy.research_sites_config import RESEARCH_SITES, DEFAULT_RESEARCH_SITE

# ============================================================================
# Public API
# ============================================================================

__all__ = [
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
