"""GNSS signal and frequency mapping.

Simplified version for initial migration.
Full migration of bands.py (338 lines) + gnss_systems.py (993 lines) + signal_mapping.py (186 lines)
pending in Phase 2 expansion.

TODO: Migrate complete signal mapping system from gnssvodpy/signal_frequency_mapping/
"""

from typing import Dict, List, Optional, Tuple

import pint
from canvod.readers._shared.constants import FREQ_UNIT, SPEEDOFLIGHT


class SignalIDMapper:
    """Simplified Signal ID mapper for RINEX v3.04.

    Maps RINEX observation codes to Signal IDs with frequency properties.

    TODO: Full implementation requires:
    - bands.py (338 lines) - Band definitions and properties
    - gnss_systems.py (993 lines) - GNSS constellation classes
    - Complete signal_mapping.py (186 lines)
    """

    def __init__(self, aggregate_glonass_fdma: bool = True) -> None:
        self.aggregate_glonass_fdma = aggregate_glonass_fdma

        # Simplified band mapping - expand with full migration
        self.SYSTEM_BANDS = {
            'G': {
                '1': 'L1',
                '2': 'L2',
                '5': 'L5'
            },  # GPS
            'E': {
                '1': 'E1',
                '5': 'E5a',
                '7': 'E5b',
                '8': 'E5'
            },  # Galileo
            'R': {
                '1': 'G1',
                '2': 'G2',
                '3': 'G3'
            },  # GLONASS
            'C': {
                '2': 'B1I',
                '7': 'B2I',
                '6': 'B3I'
            },  # BeiDou
            'J': {
                '1': 'L1',
                '2': 'L2',
                '5': 'L5'
            },  # QZSS
            'I': {
                '5': 'L5',
                '9': 'S'
            },  # IRNSS
            'S': {
                '1': 'L1',
                '5': 'L5'
            },  # SBAS
        }

        # Simplified frequency properties
        self.BAND_PROPERTIES = {
            'L1': {
                'freq': 1575.42
            },
            'L2': {
                'freq': 1227.60
            },
            'L5': {
                'freq': 1176.45
            },
            'E1': {
                'freq': 1575.42
            },
            'E5a': {
                'freq': 1176.45
            },
            'E5b': {
                'freq': 1207.14
            },
            'G1': {
                'freq': 1602.00
            },
            'G2': {
                'freq': 1246.00
            },
            'B1I': {
                'freq': 1561.098
            },
            'B2I': {
                'freq': 1207.14
            },
            'B3I': {
                'freq': 1268.52
            },
        }

    def create_signal_id(self, sv: str, obs_code: str) -> str:
        """Create Signal ID from satellite and observation code.

        Format: "sv|band|code"
        Example: "G01|L1|C" for GPS sv 01, L1 band, C/A code

        Args:
            sv: Satellite identifier (e.g., "G01", "E05")
            obs_code: RINEX observation code (e.g., "G01|S1C")

        Returns:
            Formatted signal ID
        """
        try:
            sv, observation_code = obs_code.split('|')
            system = sv[0]

            # Special handling for X1 auxiliary observations
            if observation_code == 'X1':
                return f"{sv}|X1|X"

            # Standard 3-character observation codes
            if len(observation_code) >= 3:
                band_num = observation_code[1]
                code = observation_code[2]

                # Get system-specific band name
                band_name = self.SYSTEM_BANDS.get(system, {}).get(
                    band_num, f'UnknownBand{band_num}')

                return f"{sv}|{band_name}|{code}"

            # Fallback
            return f"{sv}|{observation_code}|Unknown"

        except (ValueError, IndexError) as e:
            return f"{sv}|Unknown|Unknown"

    def parse_signal_id(self, signal_id: str) -> tuple[str, str, str]:
        """Parse Signal ID into components.

        Args:
            signal_id: Signal ID in format "sv|band|code"

        Returns:
            Tuple of (sv, band, code)
        """
        parts = signal_id.split('|')
        if len(parts) != 3:
            return "", "", ""
        return parts[0], parts[1], parts[2]

    def get_band_frequency(self, band_name: str) -> float | None:
        """Get central frequency for a band name in MHz."""
        return self.BAND_PROPERTIES.get(band_name, {}).get('freq')

    def is_auxiliary_observation(self, signal_id: str) -> bool:
        """Check if signal ID represents auxiliary data (like X1)."""
        _, band, _ = self.parse_signal_id(signal_id)
        return band == 'X1'
