"""
canvod-aux: Auxiliary data augmentation for GNSS VOD analysis

Handles downloading, parsing, and interpolating SP3 ephemerides and
clock corrections for GNSS satellite data processing.
"""

# Core abstractions
from canvod.aux.core.base import AuxFile
from canvod.aux.core.downloader import FileDownloader, FtpDownloader

# Container classes
from canvod.aux.container import GnssData

# File handlers by auxiliary data type
from canvod.aux.ephemeris import Sp3File
from canvod.aux.clock import ClkFile

# Product registry
from canvod.aux.products import (
    PRODUCT_REGISTRY,
    ProductSpec,
    get_product_spec,
    list_available_products,
    list_agencies,
    get_products_for_agency,
)

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
