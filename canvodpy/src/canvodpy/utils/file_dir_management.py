import gzip
from pathlib import Path
import shutil
from typing import Optional


def check_dir_exists(directory: Path) -> Path:
    """
    Checks if the directory exists and creates it if it doesn't.

    Parameters
    ----------
    directory : Path
        The directory path to check.

    Returns
    -------
    directory : Path
    """

    if isinstance(directory, str):
        directory = Path(directory)

    if not directory.exists():
        directory.mkdir(parents=True)
        print(f"Created directory: {directory}")

    return directory


def extract_file(file_path: Path, delete_archive: bool | None = True) -> Path:
    """
    Extracts a compressed file of type .gz or .Z.

    Parameters
    ----------
    file_path : Path
        The path to the compressed file.

    delete_archive : bool, optional
        Whether to delete the archive file after extraction. Default is True.

    Returns
    -------
    extracted_path : Path
        The path to the extracted file.
    """
    extracted_path = file_path.with_suffix("")
    if file_path.suffix in [".gz", ".Z"]:
        with gzip.open(file_path, "rb") as f_in:
            with open(extracted_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        if delete_archive:
            file_path.unlink()
        print(f"Extracted {file_path} to {extracted_path}")
    else:
        print(f"No extraction needed for {file_path}")
    return extracted_path
