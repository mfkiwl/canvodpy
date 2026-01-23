"""
Configuration loader for canvodpy.

Loads configuration from multiple YAML files with priority:
1. Package defaults (lowest priority)
2. User configuration files (highest priority)
"""

import sys
from pathlib import Path
from typing import Optional

import yaml
from pydantic import ValidationError

from .models import CanvodConfig, ProcessingConfig, SidsConfig, SitesConfig


class ConfigLoader:
    """Load and merge configuration from YAML files."""

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration loader.

        Args:
            config_dir: Directory containing config files (default: ./config)
        """
        self.config_dir = Path(config_dir or Path.cwd() / "config")
        self.defaults_dir = Path(__file__).parent / "defaults"

    def load(self) -> CanvodConfig:
        """
        Load complete configuration.

        Priority: Package defaults < User config files

        Returns:
            Validated CanvodConfig object

        Raises:
            SystemExit: If configuration is invalid or required files missing
        """
        # Load each section
        processing = self._load_processing()
        sites = self._load_sites()
        sids = self._load_sids()

        # Build complete config
        try:
            config = CanvodConfig(
                processing=processing,
                sites=sites,
                sids=sids,
            )
        except ValidationError as e:
            self._show_validation_error(e)
            sys.exit(1)

        return config

    def _load_processing(self) -> ProcessingConfig:
        """Load processing config with merge."""
        # Load defaults
        defaults = self._load_yaml(self.defaults_dir / "processing.yaml")

        # Load user config (if exists)
        user_file = self.config_dir / "processing.yaml"
        if user_file.exists():
            user_config = self._load_yaml(user_file)
            defaults = self._deep_merge(defaults, user_config)
        else:
            print(f"\n⚠️  Warning: {user_file} not found, using defaults")
            print("   Run: canvodpy config init\n")

        return ProcessingConfig(**defaults)

    def _load_sites(self) -> SitesConfig:
        """Load sites config."""
        user_file = self.config_dir / "sites.yaml"

        if not user_file.exists():
            print(f"\n❌ Required configuration file missing: {user_file}")
            print("   Run: canvodpy config init\n")
            sys.exit(1)

        data = self._load_yaml(user_file)
        return SitesConfig(**data)

    def _load_sids(self) -> SidsConfig:
        """Load SIDs config with defaults."""
        defaults = self._load_yaml(self.defaults_dir / "sids.yaml")

        user_file = self.config_dir / "sids.yaml"
        if user_file.exists():
            user_config = self._load_yaml(user_file)
            defaults = self._deep_merge(defaults, user_config)

        return SidsConfig(**defaults)

    def _load_yaml(self, path: Path) -> dict:
        """
        Load YAML file.

        Args:
            path: Path to YAML file

        Returns:
            Dictionary with YAML content (empty dict if file empty)
        """
        with open(path) as f:
            return yaml.safe_load(f) or {}

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """
        Deep merge override dictionary into base dictionary.

        Args:
            base: Base dictionary
            override: Override dictionary

        Returns:
            Merged dictionary
        """
        result = base.copy()
        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _show_validation_error(self, error: ValidationError):
        """Show user-friendly validation error."""
        print("\n" + "=" * 70)
        print("❌ Configuration Validation Error")
        print("=" * 70)
        print(f"\nConfig directory: {self.config_dir}\n")
        print(error)
        print("\n" + "=" * 70)


def load_config(config_dir: Optional[Path] = None) -> CanvodConfig:
    """
    Load configuration from YAML files.

    This is the main entry point for loading configuration.

    Args:
        config_dir: Directory containing config files (default: ./config)

    Returns:
        Validated CanvodConfig object

    Example:
        >>> from canvod.utils.config import load_config
        >>> config = load_config()
        >>> print(config.gnss_root_dir)
        >>> print(config.processing.aux_data.agency)
    """
    loader = ConfigLoader(config_dir)
    return loader.load()
