"""Utility functions for RINEX readers."""

import hashlib
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def get_version_from_pyproject(pyproject_path: Path | None = None) -> str:
    """Get package version from pyproject.toml.

    Args:
        pyproject_path: Path to pyproject.toml. If None, auto-detects.

    Returns:
        Version string
    """
    if pyproject_path is None:
        # Auto-find pyproject.toml (3 levels up from this file)
        pyproject_path = Path(__file__).resolve().parents[4] / "pyproject.toml"

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    return data["project"]["version"]


def rinex_file_hash(path: Path, chunk_size: int = 8192) -> str:
    """Compute SHA256 hash of a RINEX file's content.

    Args:
        path: Path to RINEX file
        chunk_size: Chunk size for reading file

    Returns:
        First 16 characters of SHA256 hex digest
    """
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)

    digest = h.hexdigest()[:16]
    return digest


def isfloat(value: str) -> bool:
    """Check if a string value can be converted to float.

    Args:
        value: String to check

    Returns:
        True if convertible to float, False otherwise
    """
    try:
        float(value)
        return True
    except ValueError:
        return False
