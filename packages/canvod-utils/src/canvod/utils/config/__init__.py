"""
Configuration management for canvodpy.

This package provides:
- Pydantic models for type-safe configuration
- YAML-based configuration loading
- CLI for configuration management
- Validation and error reporting

Example:
    >>> from canvod.utils.config import load_config
    >>> config = load_config()
    >>> print(config.gnss_root_dir)
    >>> print(config.processing.aux_data.agency)
"""

from .loader import load_config
from .models import CanvodConfig, ProcessingConfig, SiteConfig, SitesConfig, SidsConfig

__all__ = [
    "load_config",
    "CanvodConfig",
    "ProcessingConfig",
    "SiteConfig",
    "SitesConfig",
    "SidsConfig",
]
