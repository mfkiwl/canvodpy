"""
Configuration management for canvodpy.

This package provides:
- Pydantic models for type-safe configuration
- YAML-based configuration loading
- CLI for configuration management
- Validation and error reporting

Examples
--------
>>> from canvod.utils.config import load_config
>>> config = load_config()
>>> print(config.gnss_root_dir)
>>> print(config.processing.aux_data.agency)
"""

from .loader import load_config
from .models import (
    CanvodConfig,
    MetadataConfig,
    ProcessingConfig,
    SidsConfig,
    SiteConfig,
    SitesConfig,
)

__all__ = [
    "load_config",
    "CanvodConfig",
    "MetadataConfig",
    "ProcessingConfig",
    "SiteConfig",
    "SitesConfig",
    "SidsConfig",
]
