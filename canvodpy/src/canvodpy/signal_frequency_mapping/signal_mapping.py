from pathlib import Path
from tarfile import SYMTYPE
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pint

from canvodpy.globals import FREQ_UNIT, SPEEDOFLIGHT
from canvodpy.signal_frequency_mapping.bands import Bands
from canvodpy.signal_frequency_mapping.gnss_systems import (
    BEIDOU,
    GALILEO,
    GLONASS,
    GPS,
    IRNSS,
)
from canvodpy.validation_models.validation_models import (
    Observation,
    Rnxv3ObsEpochRecord,
    Satellite,
)


class SignalIDMapper:
    """
    Enhanced Signal ID mapper with X1 auxiliary observation support.

    Maps RINEX observation codes to Signal_IDs with bandwidth-aware properties.
    Handles special cases like X1 auxiliary observations.
    """

    def __init__(self, aggregate_glonass_fdma: bool = True) -> None:
        self.aggregate_glonass_fdma = aggregate_glonass_fdma
        self._bands = Bands(aggregate_glonass_fdma=self.aggregate_glonass_fdma)
        self.SYSTEM_BANDS = self._bands.SYSTEM_BANDS
        self.BAND_PROPERTIES = self._bands.BAND_PROPERTIES
        self.OVERLAPPING_GROUPS = self._bands.OVERLAPPING_GROUPS

    def create_signal_id(self, sv: str, obs_code: str) -> str:
        """
        Create a sid from satellite vehicle and observation code.

        Format: "sv|constellation_band|code"
        Example: "G01|L1|C" for GPS sv 01, L1 band, C/A code
        Special case: "G01|X1|X" for X1 auxiliary observations

        Parameters:
        -----------
        sv : str
            Satellite vehicle identifier (e.g., "G01", "E02")
        obs_code : str
            RINEX observation code (e.g., "G01|S1C", "E24|X1")

        Returns:
        --------
        str
            Formatted sid
        """
        try:
            sv, observation_code = obs_code.split('|')
            system = sv[0]

            # Special handling for X1 observation code
            if observation_code == 'X1':
                return f"{sv}|X1|X"  # Treat as auxiliary observation

            # Standard handling for 3-character observation codes
            if len(observation_code) >= 3:
                observation_type = observation_code[0]  # S, C, L, D
                band_num = observation_code[1]  # 1, 2, 5, etc.
                code = observation_code[2]  # C, P, W, etc.

                # Get system-specific band name
                if system in self.SYSTEM_BANDS:
                    band_name = self.SYSTEM_BANDS[system].get(
                        band_num, f'UnknownBand{band_num}')
                else:
                    band_name = f"UnknownBand{band_num}"

                return f"{sv}|{band_name}|{code}"

            # Fallback for unexpected observation code formats
            else:
                return f"{sv}|{observation_code}|Unknown"

        except (ValueError, IndexError) as e:
            # Fallback for malformed input
            print(
                f"Warning: Could not parse observation code '{obs_code}': {e}")
            return f"{sv}|Unknown|Unknown"

    def parse_signal_id(self, signal_id: str) -> tuple[str, str, str]:
        """
        Parse a sid back into its components.

        Parameters:
        -----------
        signal_id : str
            sid in format "sv|band|code"

        Returns:
        --------
        Tuple[str, str, str]
            (sv, band, code)
        """
        parts = signal_id.split('|')
        if len(parts) != 3:
            print(f"Invalid sid format: {signal_id}")
            return "", "", ""
        return parts[0], parts[1], parts[2]

    def get_band_frequency(self, band_name: str) -> float | None:
        """Get central frequency for a band name."""
        return self.BAND_PROPERTIES.get(band_name, {}).get('freq')

    def get_band_bandwidth(
            self, band_name: str) -> float | list[float] | None:
        """Get bandwidth for a band name."""
        return self.BAND_PROPERTIES.get(band_name, {}).get('bandwidth')

    def get_overlapping_group(self, band_name: str) -> str | None:
        """Get the overlapping group name for a band."""
        for group, bands in self.OVERLAPPING_GROUPS.items():
            if band_name in bands:
                return group
        return None

    def is_auxiliary_observation(self, signal_id: str) -> bool:
        """Check if a sid represents auxiliary data (like X1)."""
        _, band, _ = self.parse_signal_id(signal_id)
        band_props = self.BAND_PROPERTIES.get(band, {})
        return band_props.get('auxiliary', False)


if __name__ == "__main__":
    # Initialize unified mapper (uses existing constellation classes)
    mapper = SignalIDMapper()

    #show the differences
    # print("Differences in SYSTEM_BANDS:",
    #       set(mapper.SYSTEM_BANDS.items()) ^ set(mapper.SYSTEM_BANDS2.items()))
    # print(
    #     "Differences in BAND_PROPERTIES:",
    #     set(mapper.BAND_PROPERTIES.items())
    #     ^ set(mapper.BAND_PROPERTIES2.items()))
    # print(
    #     "Differences in OVERLAPPING_GROUPS:",
    #     set(mapper.OVERLAPPING_GROUPS.items())
    #     ^ set(mapper.OVERLAPPING_GROUPS2.items()))

    # # Example 1: Access original constellation classes directly
    # gps = mapper.get_constellation_class('G')
    # galileo = mapper.get_constellation_class('E')
    # print(f"GPS class: {gps}")
    # print(f"Galileo class: {galileo}")

    # # Example 2: Enhanced frequency mapping with satellite-specific handling
    # freq1 = mapper.get_frequency("G01|S1C")  # GPS L1C
    # freq2 = mapper.get_frequency("R01|S1C")  # GLONASS G1C (FDMA per-sv)
    # print(f"GPS G01 L1C frequency: {freq1}")
    # print(f"GLONASS R01 L1C frequency: {freq2}")

    # # Example 3: GLONASS FDMA handling using original GLONASS class
    # glonass_g1 = mapper.get_glonass_frequency("R01", "G1")
    # glonass_g2 = mapper.get_glonass_frequency("R01", "G2")
    # print(f"GLONASS R01 G1 FDMA frequency: {glonass_g1}")
    # print(f"GLONASS R01 G2 FDMA frequency: {glonass_g2}")

    # # Example 4: Signal ID functionality
    # sid = mapper.create_signal_id("G01", "S1C")  # returns 'G01|S1C'
    # sv, band, code = mapper.parse_signal_id(sid)  # ('G01','L1','C')
    # print(f"Signal ID: {sid} -> SV: {sv}, Band: {band}, Code: {code}")

    # # Example 5: Band properties derived from constellation classes
    # freq = mapper.get_band_frequency("L1")
    # bw = mapper.get_band_bandwidth("L1")
    # group = mapper.get_overlapping_group("L1")
    # print(f"L1 Band - Freq: {freq} MHz, BW: {bw} MHz, Group: {group}")

    # # Example 6: Auxiliary detection
    # is_aux = mapper.is_auxiliary_observation("G01|X1")
    # print(f"G01|X1 is auxiliary: {is_aux}")

    # # Example 7: Backward compatibility with old GnssFrequencyMapper interface
    # wavelength = mapper.get_wavelength("G01|L1C")
    # print(f"G01|L1C wavelength: {wavelength}")
