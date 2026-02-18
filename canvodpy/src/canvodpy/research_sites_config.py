"""Research site configuration loaded from YAML config.

Sites are defined in config/sites.yaml and managed via the CLI:
    canvodpy config init    # Create default config files
    canvodpy config show    # Show current configuration

This module re-exports RESEARCH_SITES and DEFAULT_RESEARCH_SITE for
backward compatibility. All site data comes from the YAML config —
nothing is hardcoded here.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any


@lru_cache(maxsize=1)
def _load_sites() -> dict[str, dict[str, Any]]:
    """Load research sites from YAML config (sites.yaml).

    Returns
    -------
    dict[str, dict[str, Any]]
        Site name -> site config dict with keys: base_dir, receivers,
        vod_analyses.
    """
    from canvod.utils.config import load_config

    config = load_config()
    sites: dict[str, dict[str, Any]] = {}
    for name, site_cfg in config.sites.sites.items():
        site_dict = site_cfg.model_dump()
        # Ensure base_dir stays a string (consistent with previous format)
        sites[name] = site_dict
    return sites


def _get_default_site() -> str:
    """Return the first site name from config as default."""
    sites = _load_sites()
    return next(iter(sites))


class _SitesProxy:
    """Lazy proxy that behaves like a dict but loads on first access.

    This avoids importing the full config system at module import time,
    which prevents circular imports and speeds up initial import.
    """

    def __getitem__(self, key: str) -> dict[str, Any]:
        return _load_sites()[key]

    def __contains__(self, key: object) -> bool:
        return key in _load_sites()

    def __iter__(self):
        return iter(_load_sites())

    def __len__(self) -> int:
        return len(_load_sites())

    def keys(self):
        return _load_sites().keys()

    def values(self):
        return _load_sites().values()

    def items(self):
        return _load_sites().items()

    def get(self, key: str, default=None):
        return _load_sites().get(key, default)

    def __repr__(self) -> str:
        return repr(_load_sites())


class _DefaultSiteProxy:
    """Lazy proxy for DEFAULT_RESEARCH_SITE string."""

    def __str__(self) -> str:
        return _get_default_site()

    def __repr__(self) -> str:
        return repr(_get_default_site())

    def __eq__(self, other: object) -> bool:
        return str(self) == other

    def __hash__(self) -> int:
        return hash(str(self))


# Module-level exports — these are lazy proxies that load config on first use
RESEARCH_SITES: dict[str, dict[str, Any]] = _SitesProxy()  # type: ignore[assignment]
DEFAULT_RESEARCH_SITE: str = _DefaultSiteProxy()  # type: ignore[assignment]
