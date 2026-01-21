"""
canvod-aux: Auxiliary data augmentation for GNSS VOD analysis

Handles downloading, parsing, and interpolating SP3 ephemerides and
clock corrections for GNSS satellite data processing.
"""

# Core abstractions
from canvod.aux.clock import ClkFile

# Container classes
from canvod.aux.container import GnssData
from canvod.aux.core.base import AuxFile
from canvod.aux.core.downloader import FileDownloader, FtpDownloader

# File handlers by auxiliary data type
from canvod.aux.ephemeris import Sp3File

# Interpolation
from canvod.aux.interpolation import (
    ClockConfig,
    ClockInterpolationStrategy,
    Interpolator,
    InterpolatorConfig,
    Sp3Config,
    Sp3InterpolationStrategy,
    create_interpolator_from_attrs,
)

# Dataset matching
from canvod.aux.matching import DatasetMatcher

# Position and coordinates
from canvod.aux.position import (
    ECEFPosition,
    GeodeticPosition,
    add_spherical_coords_to_dataset,
    compute_spherical_coordinates,
)

# Preprocessing
from canvod.aux.preprocessing import (
    add_future_datavars,
    create_sv_to_sid_mapping,
    map_aux_sv_to_sid,
    normalize_sid_dtype,
    pad_to_global_sid,
    prep_aux_ds,
    preprocess_aux_for_interpolation,
    strip_fillvalue,
)

# Product registry
from canvod.aux.products import (
    PRODUCT_REGISTRY,
    ProductSpec,
    get_product_spec,
    get_products_for_agency,
    list_agencies,
    list_available_products,
)

__version__ = "0.1.0"

__all__ = [
    # File handlers
    "Sp3File",
    "ClkFile",
    "AuxFile",
    # Interpolation
    "Interpolator",
    "InterpolatorConfig",
    "Sp3Config",
    "ClockConfig",
    "Sp3InterpolationStrategy",
    "ClockInterpolationStrategy",
    "create_interpolator_from_attrs",
    # Dataset matching
    "DatasetMatcher",
    # Position and coordinates
    "ECEFPosition",
    "GeodeticPosition",
    "compute_spherical_coordinates",
    "add_spherical_coords_to_dataset",
    # Preprocessing
    "preprocess_aux_for_interpolation",
    "prep_aux_ds",
    "map_aux_sv_to_sid",
    "create_sv_to_sid_mapping",
    "pad_to_global_sid",
    "normalize_sid_dtype",
    "strip_fillvalue",
    "add_future_datavars",
    # Utilities
    "FileDownloader",
    "FtpDownloader",
    "GnssData",
    # Product registry
    "PRODUCT_REGISTRY",
    "ProductSpec",
    "get_product_spec",
    "list_available_products",
    "list_agencies",
    "get_products_for_agency",
]

# Try to import pipeline (requires gnssvodpy)
try:
    from canvod.aux.pipeline import AuxDataPipeline
    __all__.append("AuxDataPipeline")
except ImportError:
    pass

# Try to import augmentation (requires gnssvodpy)
try:
    from canvod.aux.augmentation import (
        AugmentationContext,
        AugmentationStep,
        AuxDataAugmenter,
        ClockCorrectionAugmentation,
        SphericalCoordinateAugmentation,
    )
    __all__.extend([
        "AuxDataAugmenter",
        "AugmentationStep",
        "AugmentationContext",
        "SphericalCoordinateAugmentation",
        "ClockCorrectionAugmentation",
    ])
except ImportError:
    pass
