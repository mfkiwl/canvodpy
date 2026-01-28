"""Global constants and defaults for canvodpy."""

from pathlib import Path

import pint

N_MAX_THREADS = 20

UREG = pint.UnitRegistry()
UREG.define("dBHz = 10 * log10(hertz)")
UREG.define("dB = 10 * log10(ratio)")

SPEEDOFLIGHT: pint.Quantity = 299792458 * UREG.meter / UREG.second

TIME_AGGR: pint.Quantity = 15 * UREG.second
KEEP_RNX_VARS: list[str] = [
    "SNR",
    # 'Pseudorange',
    # 'Phase',
    # 'Doppler',
]
# Support for LLI, SSI, and Auxiliary is experimental and not fully tested.
# Use with caution.

EPOCH_RECORD_INDICATOR: str = ">"

SEPTENTRIO_SAMPLING_INTERVALS: list[pint.Quantity] = [
    100 * UREG.millisecond,
    200 * UREG.millisecond,
    500 * UREG.millisecond,
    1 * UREG.second,
    2 * UREG.second,
    5 * UREG.second,
    10 * UREG.second,
    15 * UREG.second,
    30 * UREG.second,
    60 * UREG.second,
    2 * UREG.minute,
    5 * UREG.minute,
    10 * UREG.minute,
    15 * UREG.minute,
    30 * UREG.minute,
    60 * UREG.minute,
]

IGS_RNX_DUMP_INTERVALS: list[pint.Quantity] = [
    15 * UREG.minute,
    1 * UREG.hour,
    6 * UREG.hour,
    24 * UREG.hour,
]

#--------------------GNSS Frequency-------------------
# define the unit you want to handle the frequencies in
FREQ_UNIT = UREG.MHz

#-------------------Logging-------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Ensure `.logs` directory exists
LOG_DIR = PROJECT_ROOT / ".logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Final log file
LOG_FILE: Path = LOG_DIR / "gnssvodpy.log"

LOG_PATH_DEPTH: int = 6
# Number of path parts of the RINEX files to include in log context, e.g. the
# last 5 parts of
# /home/user/shares/directory/subdir/moredirs/05_data/01_Rosalia/02_canopy/
# 01_GNSS/01_raw/25246/ract246a15.25o

#-----------------------------Data Directories-------------------------------

CANOPY_DS_PREFIX: str = "canopy"
SKY_DS_PREFIX: str = "sky"
LOCATION_NAME: str = "Rosalia"

#--------FTP Server Settings for fetching aux data (e.g. SP3, CLK)--------
FTP_SERVER: str = "ftp://gssc.esa.int/gnss"
AGENCY: str = "COD"
PRODUCT_TYPE: str = "final"
AUX_FILE_PATH: Path = Path("00_aux_files")
SP3_FILE_PATH: Path = AUX_FILE_PATH / "01_SP3"
CLK_FILE_PATH: Path = AUX_FILE_PATH / "02_CLK"
IONEX_FILE_PATH: Path = AUX_FILE_PATH / "03_IONEX"
#----------------------------------------------------------------------
OUT_DIR: Path = Path("03_GNSS_paired")

#-----------------------------netCDF compression settings-------------------------------
COMPRESSION: dict[str, bool | int] = {
    "zlib": True,
    "complevel": 5,
}

#-----------------------------Author & Software Information---------------------
AUTHOR: str = "Nicolas François Bader"
EMAIL: str = "nicolas.bader@tuwien.ac.at"
INSTITUTION: str = "TU Wien"
DEPARTMENT: str = "Department of Geodesy and Geoinformation"
RESEARCH_GROUP: str = "Climate and Environment Remote Sensing"
WEBSITE: str = "https://www.tuwien.at/en/mg/geo/climers"
SOFTWARE: str = "gnssvodpy, https://github.com/nfb2021/gnssvodpy"

# ----------------------------- Icechunk Store Settings -----------------------------

# Compression settings for all Icechunk stores
ICECHUNK_COMPRESSION_LEVEL: int = 5
ICECHUNK_COMPRESSION_ALGORITHM: str = "zstd"
# Will be converted to icechunk.CompressionAlgorithm enum.
ICECHUNK_INLINE_THRESHOLD: int = 512
ICECHUNK_GET_CONCURRENCY: int = 1  # Default chunking strategies
ICECHUNK_CHUNK_STRATEGIES: dict[str, dict[str, int]] = {
    "rinex_store": {
        "epoch": 34560,  # two days of 5s
        "sid": -1  # Don't chunk along sid dimension
    },
    "vod_store": {
        "epoch": 34560,  # two days of 5s
        "sid": -1  # Don't chunk along sid dimension
    }
}

ICECHUNK_MANIFEST_PRELOAD_ENABLED: bool = False  # Disable by default
ICECHUNK_MANIFEST_PRELOAD_MAX_REFS: int = 100_000_000
ICECHUNK_MANIFEST_PRELOAD_PATTERN: str = "epoch|sid"  # Coordinates only

#-----------------------------Metadata Attributes--------------------------------
AGGREGATE_GLONASS_FDMA: bool = True  # Whether to aggregate GLONASS FDMA bands

#-----------------------------Data Storage Strategy--------------------------------
# Strategy for handling duplicate RINEX ingests
# "overwrite" → always replace existing entries with new data. This is
# expensive, because icechunk/zarr does not support in-place updates, so the
# entire datastore has to be rewritten and the metadata table stored somewhere
# in between, before writing again.
# "skip"      → keep existing data, don't ingest duplicates
# "append"    → append new data to existing data. This may result in duplicate
# epochs if the new data overlaps with existing data.
RINEX_STORE_STRATEGY = "skip"  # or "skip", "append"
RINEX_STORE_EXPIRE_DAYS = 2
# Number of days after which old snapshots are expired and eligible for garbage
# collection.
VOD_STORE_STRATEGY = "overwrite"  # or "skip", "append"

#------Define SIDs to keep-------------------------------
# Empty list means keep all SIDs possible in Rinex v3.04, otherwise only keep
# listed SIDs.
#    that are also found in the possible Rinex v3.04 SIDs
KEEP_SIDS: list[str] = [
    "C05|B1I|I", "C05|B2b|I", "C05|B3I|I", "C06|B1I|I", "C06|B2b|I",
    "C06|B3I|I", "C07|B1I|I", "C07|B2b|I", "C07|B3I|I", "C08|B1I|I",
    "C08|B2b|I", "C08|B3I|I", "C09|B1I|I", "C09|B2b|I", "C09|B3I|I",
    "C10|B1I|I", "C10|B2b|I", "C10|B3I|I", "C11|B1I|I", "C11|B2b|I",
    "C11|B3I|I", "C12|B1I|I", "C12|B2b|I", "C12|B3I|I", "C13|B1I|I",
    "C13|B2b|I", "C13|B3I|I", "C14|B1I|I", "C14|B2b|I", "C14|B3I|I",
    "C16|B1I|I", "C16|B2b|I", "C16|B3I|I", "C19|B1I|I", "C19|B3I|I",
    "C20|B1I|I", "C20|B3I|I", "C21|B1I|I", "C21|B3I|I", "C22|B1I|I",
    "C22|B3I|I", "C23|B1I|I", "C23|B3I|I", "C24|B1I|I", "C24|B3I|I",
    "C25|B1I|I", "C25|B3I|I", "C26|B1I|I", "C26|B3I|I", "C27|B1I|I",
    "C27|B3I|I", "C28|B1I|I", "C28|B3I|I", "C29|B1I|I", "C29|B3I|I",
    "C30|B1I|I", "C30|B3I|I", "C32|B1I|I", "C32|B3I|I", "C33|B1I|I",
    "C33|B3I|I", "C34|B1I|I", "C34|B3I|I", "C35|B1I|I", "C35|B3I|I",
    "C36|B1I|I", "C36|B3I|I", "C37|B1I|I", "C37|B3I|I", "C38|B1I|I",
    "C38|B3I|I", "C39|B1I|I", "C39|B3I|I", "C40|B1I|I", "C40|B3I|I",
    "C41|B1I|I", "C41|B3I|I", "C42|B1I|I", "C42|B3I|I", "C43|B1I|I",
    "C43|B3I|I", "C44|B1I|I", "C44|B3I|I", "C45|B1I|I", "C45|B3I|I",
    "C47|B1I|I", "C47|B3I|I", "C48|B1I|I", "C48|B3I|I", "C49|B1I|I",
    "C49|B3I|I", "C50|B1I|I", "C50|B3I|I", "E02|E1|C", "E02|E5a|Q",
    "E02|E5b|Q", "E03|E1|C", "E03|E5a|Q", "E03|E5b|Q", "E04|E1|C", "E04|E5a|Q",
    "E04|E5b|Q", "E05|E1|C", "E05|E5a|Q", "E05|E5b|Q", "E06|E1|C", "E06|E5a|Q",
    "E06|E5b|Q", "E07|E1|C", "E07|E5a|Q", "E07|E5b|Q", "E08|E1|C", "E08|E5a|Q",
    "E08|E5b|Q", "E09|E1|C", "E09|E5a|Q", "E09|E5b|Q", "E10|E1|C", "E10|E5a|Q",
    "E10|E5b|Q", "E11|E1|C", "E11|E5a|Q", "E11|E5b|Q", "E12|E1|C", "E12|E5a|Q",
    "E12|E5b|Q", "E13|E1|C", "E13|E5a|Q", "E13|E5b|Q", "E14|E1|C", "E14|E5a|Q",
    "E14|E5b|Q", "E15|E1|C", "E15|E5a|Q", "E15|E5b|Q", "E16|E1|C", "E16|E5a|Q",
    "E16|E5b|Q", "E18|E1|C", "E18|E5a|Q", "E18|E5b|Q", "E19|E1|C", "E19|E5a|Q",
    "E19|E5b|Q", "E21|E1|C", "E21|E5a|Q", "E21|E5b|Q", "E23|E1|C", "E23|E5a|Q",
    "E23|E5b|Q", "E24|E1|C", "E24|E5a|Q", "E24|E5b|Q", "E25|E1|C", "E25|E5a|Q",
    "E25|E5b|Q", "E26|E1|C", "E26|E5a|Q", "E26|E5b|Q", "E27|E1|C", "E27|E5a|Q",
    "E27|E5b|Q", "E29|E1|C", "E29|E5a|Q", "E29|E5b|Q", "E30|E1|C", "E30|E5a|Q",
    "E30|E5b|Q", "E31|E1|C", "E31|E5a|Q", "E31|E5b|Q", "E33|E1|C", "E33|E5a|Q",
    "E33|E5b|Q", "E34|E1|C", "E34|E5a|Q", "E34|E5b|Q", "E36|E1|C", "E36|E5a|Q",
    "E36|E5b|Q", "G01|L1|C", "G01|L2|L", "G01|L2|W", "G02|L1|C", "G02|L2|W",
    "G03|L1|C", "G03|L2|L", "G03|L2|W", "G04|L1|C", "G04|L2|L", "G04|L2|W",
    "G05|L1|C", "G05|L2|L", "G05|L2|W", "G06|L1|C", "G06|L2|L", "G06|L2|W",
    "G07|L1|C", "G07|L2|L", "G07|L2|W", "G08|L1|C", "G08|L2|L", "G08|L2|W",
    "G09|L1|C", "G09|L2|L", "G09|L2|W", "G10|L1|C", "G10|L2|L", "G10|L2|W",
    "G11|L1|C", "G11|L2|L", "G11|L2|W", "G12|L1|C", "G12|L2|L", "G12|L2|W",
    "G13|L1|C", "G13|L2|W", "G14|L1|C", "G14|L2|L", "G14|L2|W", "G15|L1|C",
    "G15|L2|L", "G15|L2|W", "G16|L1|C", "G16|L2|W", "G17|L1|C", "G17|L2|L",
    "G17|L2|W", "G18|L1|C", "G18|L2|L", "G18|L2|W", "G19|L1|C", "G19|L2|W",
    "G20|L1|C", "G20|L2|W", "G21|L1|C", "G21|L2|L", "G21|L2|W", "G22|L1|C",
    "G22|L2|W", "G23|L1|C", "G23|L2|L", "G23|L2|W", "G24|L1|C", "G24|L2|L",
    "G24|L2|W", "G25|L1|C", "G25|L2|L", "G25|L2|W", "G26|L1|C", "G26|L2|L",
    "G26|L2|W", "G27|L1|C", "G27|L2|L", "G27|L2|W", "G28|L1|C", "G28|L2|L",
    "G28|L2|W", "G29|L1|C", "G29|L2|L", "G29|L2|W", "G30|L1|C", "G30|L2|L",
    "G30|L2|W", "G31|L1|C", "G31|L2|L", "G31|L2|W", "G32|L1|C", "G32|L2|L",
    "G32|L2|W", "I02|L5|A", "I06|L5|A", "I09|L5|A", "R01|G1|C", "R01|G2|C",
    "R02|G1|C", "R02|G2|C", "R03|G1|C", "R03|G2|C", "R04|G1|C", "R04|G2|C",
    "R05|G1|C", "R05|G2|C", "R06|G1|C", "R07|G1|C", "R07|G2|C", "R08|G1|C",
    "R08|G2|C", "R09|G1|C", "R09|G2|C", "R10|G1|C", "R11|G1|C", "R11|G2|C",
    "R12|G1|C", "R12|G2|C", "R13|G1|C", "R14|G1|C", "R14|G2|C", "R15|G1|C",
    "R15|G2|C", "R16|G1|C", "R16|G2|C", "R17|G1|C", "R17|G2|C", "R18|G1|C",
    "R18|G2|C", "R19|G1|C", "R19|G2|C", "R20|G1|C", "R20|G2|C", "R21|G1|C",
    "R21|G2|C", "R22|G1|C", "R22|G2|C", "R23|G1|C", "R24|G1|C", "R24|G2|C",
    "S21|L1|C", "S23|L1|C", "S27|L1|C", "S36|L1|C"
]
