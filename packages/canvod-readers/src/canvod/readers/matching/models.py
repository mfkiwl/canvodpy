"""Data models for directory matching.

Contains dataclasses for representing matched RINEX data directories.
"""

from dataclasses import dataclass
from pathlib import Path

from canvod.utils.tools import YYYYDOY


@dataclass(frozen=True)
class MatchedDirs:
    """Matched directory paths for canopy and reference receivers.

    Immutable container representing a pair of directories containing
    RINEX data for the same date.

    Parameters
    ----------
    canopy_data_dir : Path
        Path to canopy receiver RINEX directory.
    reference_data_dir : Path
        Path to reference (open-sky) receiver RINEX directory.
    yyyydoy : YYYYDOY
        Date object for this matched pair.

    Examples
    --------
    >>> from pathlib import Path
    >>> from canvod.utils.tools import YYYYDOY
    >>> 
    >>> md = MatchedDirs(
    ...     canopy_data_dir=Path("/data/02_canopy/25001"),
    ...     reference_data_dir=Path("/data/01_reference/25001"),
    ...     yyyydoy=YYYYDOY.from_str("2025001")
    ... )
    >>> md.yyyydoy.to_str()
    '2025001'

    """

    canopy_data_dir: Path
    reference_data_dir: Path
    yyyydoy: YYYYDOY


@dataclass
class PairMatchedDirs:
    """Matched directories for a receiver pair on a specific date.

    Supports multi-receiver configurations where multiple canopy/reference
    pairs may exist at the same site.

    Parameters
    ----------
    yyyydoy : YYYYDOY
        Date for this matched pair.
    pair_name : str
        Identifier for this receiver pair (e.g., "pair_01").
    canopy_receiver : str
        Name of canopy receiver (e.g., "canopy_01").
    reference_receiver : str
        Name of reference receiver (e.g., "reference_01").
    canopy_data_dir : Path
        Path to canopy receiver RINEX directory.
    reference_data_dir : Path
        Path to reference receiver RINEX directory.

    Examples
    --------
    >>> pmd = PairMatchedDirs(
    ...     yyyydoy=YYYYDOY.from_str("2025001"),
    ...     pair_name="pair_01",
    ...     canopy_receiver="canopy_01",
    ...     reference_receiver="reference_01",
    ...     canopy_data_dir=Path("/data/canopy_01/25001"),
    ...     reference_data_dir=Path("/data/reference_01/25001")
    ... )
    >>> pmd.pair_name
    'pair_01'

    """

    yyyydoy: YYYYDOY
    pair_name: str
    canopy_receiver: str
    reference_receiver: str
    canopy_data_dir: Path
    reference_data_dir: Path
