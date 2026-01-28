"""Research site and Icechunk store configuration.

This file contains all site-specific configuration including receiver
setups, store paths, and analysis configurations. Pure configuration only -
no logic or functions.

All paths are relative to GNSS_ROOT_DIR which is loaded from the .env file.
This ensures no personal/absolute paths are committed to version control.

File: src/gnssvodpy/research_sites_config.py
"""

import os
from pathlib import Path
from typing import Any

# Get the directory two levels up from this file for the env file
_ENV_DIR = Path(__file__).parent.parent.parent

# Load environment variables from .env file in _ENV_DIR
try:
    from dotenv import load_dotenv
    load_dotenv(_ENV_DIR / ".env")
except ImportError:
    # dotenv not available, skip loading
    pass

# Get GNSS_ROOT_DIR from environment or use relative default
# User must set this in .env file for their local environment
_GNSS_ROOT_DIR = Path(os.getenv("GNSS_ROOT_DIR", Path.cwd() / "data"))

# ----------------------------- Research Sites Configuration --------------------

RESEARCH_SITES: dict[str, dict[str, Any]] = {
    "Rosalia": {
        "base_dir": _GNSS_ROOT_DIR / "01_Rosalia",
        "rinex_store_path": _GNSS_ROOT_DIR / "01_Rosalia" / "03_Rinex_Testing",
        "vod_store_path": _GNSS_ROOT_DIR / "01_Rosalia" / "04_VOD_Testing",
        "receivers": {
            "reference_01": {
                "type": "reference",
                "directory": "01_reference",
                "description": "First reference receiver (open sky)",
            },
            "canopy_01": {
                "type": "canopy",
                "directory": "02_canopy",
                "description": "First canopy receiver (under vegetation)",
            },
            "canopy_02": {
                "type": "canopy",
                "directory": "03_canopy_ext1",
                "description": "Second canopy receiver (under vegetation)",
            }
        },
        "vod_analyses": {
            "canopy_01_vs_reference_01": {
                "canopy_receiver": "canopy_01",
                "reference_receiver": "reference_01",
                "description":
                "VOD analysis: canopy_01 compared to reference_01",
            },
            "canopy_02_vs_reference_01": {
                "canopy_receiver": "canopy_02",
                "reference_receiver": "reference_01",
                "description":
                "VOD analysis: canopy_02 compared to reference_01",
            }
        }
    }

    # Future sites can be added here
}

# ----------------------------- Default Settings -----------------------------

# Default site for backward compatibility and convenience
DEFAULT_RESEARCH_SITE: str = "Rosalia"
