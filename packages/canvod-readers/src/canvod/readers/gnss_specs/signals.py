"""Signal ID mapping for GNSS observations.

Maps RINEX observation codes to standardized Signal IDs with frequency
and bandwidth information. Handles all major GNSS constellations and
special cases like auxiliary observations.
"""


from canvod.readers.gnss_specs.bands import Bands

OBS_CODE_LEN = 3
SIGNAL_ID_PARTS = 3


class SignalIDMapper:
    """Signal ID mapper with bandwidth-aware properties.

    Maps RINEX observation codes to standardized Signal IDs (sids) with
    associated frequency and bandwidth information. Handles all major GNSS
    constellations (GPS, GLONASS, Galileo, BeiDou, QZSS, IRNSS, SBAS)
    and special cases like X1 auxiliary observations.

    Signal ID Format
    ----------------
    Standard: ``"SV|BAND|CODE"``
        Example: ``"G01|L1|C"`` for GPS satellite 1, L1 band, C/A code

    Auxiliary: ``"SV|X1|X"``
        Example: ``"G01|X1|X"`` for GPS satellite 1, X1 auxiliary observation

    Parameters
    ----------
    aggregate_glonass_fdma : bool, optional
        If True, aggregate GLONASS FDMA channels into G1/G2 bands.
        If False, keep individual FDMA channels separate. Default is True.

    Attributes
    ----------
    SYSTEM_BANDS : dict[str, dict[str, str]]
        Mapping of GNSS system codes to band names.
    BAND_PROPERTIES : dict[str, dict[str, float | str | bool]]
        Band properties including frequency, bandwidth, system.
    OVERLAPPING_GROUPS : dict[str, list[str]]
        Groups of overlapping frequency bands.

    Examples
    --------
    >>> mapper = SignalIDMapper()
    >>> sid = mapper.create_signal_id("G01", "G01|S1C")
    >>> sid
    'G01|L1|C'

    >>> sv, band, code = mapper.parse_signal_id(sid)
    >>> (sv, band, code)
    ('G01', 'L1', 'C')

    >>> freq = mapper.get_band_frequency("L1")
    >>> freq
    1575.42

    """

    def __init__(
        self,
        aggregate_glonass_fdma: bool = True,  # noqa: FBT001, FBT002
    ) -> None:
        """Initialize SignalIDMapper."""
        self.aggregate_glonass_fdma = aggregate_glonass_fdma
        self._bands = Bands(aggregate_glonass_fdma=self.aggregate_glonass_fdma)
        self.SYSTEM_BANDS: dict[str, dict[str, str]] = self._bands.SYSTEM_BANDS
        self.BAND_PROPERTIES: dict[str, dict[str, float | str | bool]] = (
            self._bands.BAND_PROPERTIES
        )
        self.OVERLAPPING_GROUPS: dict[str, list[str]] = (
            self._bands.OVERLAPPING_GROUPS
        )

    def create_signal_id(self, sv: str, obs_code: str) -> str:
        """Create standardized signal ID from satellite and observation code.

        Converts RINEX observation codes to standardized format for
        downstream processing. Handles special cases like X1 auxiliary
        observations.

        Parameters
        ----------
        sv : str
            Satellite vehicle identifier (e.g., "G01", "E02", "R24").
        obs_code : str
            RINEX observation code (e.g., "G01|S1C", "E24|X1").
            Format: "SV|OBSERVATION_CODE" where observation code is
            typically 3 characters: type (S/C/L/D) + band + code.

        Returns
        -------
        str
            Standardized signal ID in format "SV|BAND|CODE".

        Notes
        -----
        Special cases:
        - X1 observations → "SV|X1|X"
        - Unknown bands → "SV|UnknownBandN|Code"
        - Malformed input → "SV|Unknown|Unknown"

        Examples
        --------
        >>> mapper = SignalIDMapper()
        >>> mapper.create_signal_id("G01", "G01|S1C")
        'G01|L1|C'

        >>> mapper.create_signal_id("E05", "E05|X1")
        'E05|X1|X'

        >>> mapper.create_signal_id("R12", "R12|S1C")
        'R12|G1|C'

        """
        try:
            sv, observation_code = obs_code.split("|")
            system = sv[0]

            # Special handling for X1 observation code
            if observation_code == "X1":
                return f"{sv}|X1|X"  # Treat as auxiliary observation

            # Standard handling for 3-character observation codes
            if len(observation_code) >= OBS_CODE_LEN:
                band_num = observation_code[1]  # 1, 2, 5, etc.
                code = observation_code[2]  # C, P, W, etc.

                # Get system-specific band name
                if system in self.SYSTEM_BANDS:
                    band_name = self.SYSTEM_BANDS[system].get(
                        band_num, f"UnknownBand{band_num}")
                else:
                    band_name = f"UnknownBand{band_num}"

                return f"{sv}|{band_name}|{code}"

            # Fallback for unexpected observation code formats
            return f"{sv}|{observation_code}|Unknown"  # noqa: TRY300

        except (ValueError, IndexError) as e:
            # Fallback for malformed input
            print(
                f"Warning: Could not parse observation code '{obs_code}': {e}")
            return f"{sv}|Unknown|Unknown"

    def parse_signal_id(self, signal_id: str) -> tuple[str, str, str]:
        """Parse signal ID into components.

        Parameters
        ----------
        signal_id : str
            Signal ID in format "SV|BAND|CODE" (e.g., "G01|L1|C").

        Returns
        -------
        sv : str
            Satellite vehicle identifier.
        band : str
            Band name.
        code : str
            Code identifier.

        Examples
        --------
        >>> mapper = SignalIDMapper()
        >>> sv, band, code = mapper.parse_signal_id("G01|L1|C")
        >>> (sv, band, code)
        ('G01', 'L1', 'C')

        >>> mapper.parse_signal_id("invalid")
        ('', '', '')

        """
        parts = signal_id.split("|")
        if len(parts) != SIGNAL_ID_PARTS:
            print(f"Invalid signal ID format: {signal_id}")
            return "", "", ""
        return parts[0], parts[1], parts[2]

    def get_band_frequency(self, band_name: str) -> float | None:
        """Get central frequency for a band.

        Parameters
        ----------
        band_name : str
            Band identifier (e.g., "L1", "E5a", "B2b").

        Returns
        -------
        float or None
            Central frequency in MHz, or None if band not found.

        Examples
        --------
        >>> mapper = SignalIDMapper()
        >>> mapper.get_band_frequency("L1")
        1575.42

        >>> mapper.get_band_frequency("E5a")
        1176.45

        """
        return self.BAND_PROPERTIES.get(band_name, {}).get("freq")

    def get_band_bandwidth(self, band_name: str) -> float | list[float] | None:
        """Get bandwidth for a band.

        Parameters
        ----------
        band_name : str
            Band identifier (e.g., "L1", "E5a", "B2b").

        Returns
        -------
        float or list of float or None
            Bandwidth in MHz. Returns list for bands with multiple
            components. Returns None if band not found.

        Examples
        --------
        >>> mapper = SignalIDMapper()
        >>> mapper.get_band_bandwidth("L1")
        30.69

        >>> mapper.get_band_bandwidth("UnknownBand")
        None

        """
        return self.BAND_PROPERTIES.get(band_name, {}).get("bandwidth")

    def get_overlapping_group(self, band_name: str) -> str | None:
        """Get overlapping group for a band.

        Bands in the same overlapping group have frequency overlap
        and may cause interference.

        Parameters
        ----------
        band_name : str
            Band identifier (e.g., "L1", "E1", "B1I").

        Returns
        -------
        str or None
            Group identifier (e.g., "group_1"), or None if not in any group.

        Examples
        --------
        >>> mapper = SignalIDMapper()
        >>> mapper.get_overlapping_group("L1")
        'group_1'

        >>> mapper.get_overlapping_group("E1")
        'group_1'

        >>> mapper.get_overlapping_group("X1")
        'group_aux'

        """
        for group, bands in self.OVERLAPPING_GROUPS.items():
            if band_name in bands:
                return group
        return None

    def is_auxiliary_observation(self, signal_id: str) -> bool:
        """Check if signal ID represents auxiliary data.

        Auxiliary observations like X1 contain metadata rather than
        standard GNSS observables.

        Parameters
        ----------
        signal_id : str
            Signal ID to check (e.g., "G01|X1|X", "G01|L1|C").

        Returns
        -------
        bool
            True if signal represents auxiliary data, False otherwise.

        Examples
        --------
        >>> mapper = SignalIDMapper()
        >>> mapper.is_auxiliary_observation("G01|X1|X")
        True

        >>> mapper.is_auxiliary_observation("G01|L1|C")
        False

        """
        _, band, _ = self.parse_signal_id(signal_id)
        band_props = self.BAND_PROPERTIES.get(band, {})
        return band_props.get("auxiliary", False)
