from abc import ABC, abstractmethod
from ftplib import FTP_TLS, error_perm, error_temp
import gzip
from pathlib import Path
import shutil
import sys
from typing import List, Optional, Union
from urllib import error as urllib_error, request

import pandas as pd
from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass
from tqdm import tqdm
import xarray as xr


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class GnssData:
    """Container for GNSS data that may include both xarray Dataset and pandas DataFrame."""
    dataset: xr.Dataset
    dataframe: pd.DataFrame | None = None


@dataclass
class FileMetadata:
    """Metadata required for GNSS auxiliary files."""
    date: str  # Format: YYYYDOY
    agency: str  # e.g., 'COD', 'IGS'
    product_type: str  # 'final', 'rapid', 'ultrarapid'
    local_dir: Path
    ftp_server: str


class FileDownloader(ABC):
    """Protocol defining the interface for file downloading implementations."""

    @abstractmethod
    def download(self, url: str, destination: Path) -> Path:
        """Download a file from url to destination."""
        pass


class FtpDownloader(FileDownloader):
    """Implementation of FileDownloader for FTP downloads with progress bar and fallback servers."""

    # NASA CDDIS FTP server URL - corrected path
    NASA_FTP = 'ftp://gdc.cddis.eosdis.nasa.gov'

    def __init__(self,
                 alt_servers: list[str] | None = None,
                 user_email: str | None = None):
        """
        Initialize downloader with optional alternate servers.

        FTP Server Strategy:
        ------------------
        - Primary: Uses the URL provided in download() call (typically ESA)
        - Fallback: NASA CDDIS (requires authentication with user_email)

        If user_email is None:
        - Only the primary server (ESA) will be used
        - NASA CDDIS will be skipped from fallback attempts
        - This is the default behavior and requires no configuration

        To enable NASA CDDIS fallback:
        - Set CDDIS_MAIL environment variable with your registered email
        - Register at: https://urs.earthdata.nasa.gov/users/new

        Args:
            alt_servers: List of alternative FTP server URLs to try if the primary fails
            user_email: Email to use for authenticated FTP servers (like NASA CDDIS)
                       If None, authenticated servers are skipped
        """
        # Build alternate servers list, but only include CDDIS if we have credentials
        if alt_servers is None:
            if user_email is not None:
                # User has CDDIS credentials, include NASA as fallback
                self.alt_servers = [self.NASA_FTP]
                print("ℹ NASA CDDIS fallback enabled (credentials configured)")
            else:
                # No credentials, skip CDDIS fallback
                self.alt_servers = []
                print("ℹ Using ESA FTP exclusively (no CDDIS credentials)")
                print(
                    "  To enable NASA CDDIS fallback, set CDDIS_MAIL environment variable"
                )
        else:
            # User explicitly provided alt_servers
            if user_email is None:
                # Filter out CDDIS servers if no credentials
                self.alt_servers = [
                    s for s in alt_servers if 'cddis' not in s.lower()
                ]
                if len(self.alt_servers) < len(alt_servers):
                    print(
                        "⚠ Skipping CDDIS servers from fallback list (no credentials)"
                    )
            else:
                self.alt_servers = alt_servers

        self.user_email = user_email

    def download(self,
                 url: str,
                 destination: Path,
                 file_info: dict | None = None) -> Path:
        """
        Download a file from FTP with progress tracking and fallback servers.
        Handles automatic decompression of .gz files.

        Args:
            url: Primary URL to download from
            destination: Local path to save the file
            file_info: Additional information about the file (agency, GPS week, etc.)

        Returns:
            Path to the downloaded file

        Raises:
            RuntimeError: If file cannot be downloaded from any server
        """
        # Create parent directories if they don't exist
        destination.parent.mkdir(parents=True, exist_ok=True)

        # Try primary URL first
        try:
            print(f"Attempting to download from primary server: {url}")
            return self._try_download_url(url, destination)
        except Exception as e:
            print(f"Primary download from {url} failed: {str(e)}")

            # If primary fails, try alternate servers
            all_errors = [f"Primary server error: {str(e)}"]

            # Check if we have any alternate servers to try
            if not self.alt_servers:
                print("ℹ No fallback servers available")
                raise RuntimeError(
                    f"Failed to download file from primary server. No fallback servers configured.\n"
                    f"Error: {str(e)}\n"
                    f"Tip: To enable NASA CDDIS fallback, set CDDIS_MAIL environment variable"
                )

            for alt_server in self.alt_servers:
                try:
                    # Use file_info to construct the correct alternate URL
                    if file_info and 'cddis' in alt_server.lower():
                        alt_url = self._construct_nasa_cddis_url(file_info)
                    else:
                        # Construct alternate URL for other servers
                        alt_url = self._construct_alternate_url(
                            url, alt_server)

                    print(f"Trying alternate server: {alt_url}")
                    return self._try_download_url(alt_url, destination)
                except Exception as alt_e:
                    error_msg = f"Alternate server {alt_server} error: {str(alt_e)}"
                    print(error_msg)
                    all_errors.append(error_msg)

            # If we get here, all servers failed
            raise RuntimeError(
                "Failed to download file from all servers. Errors:\n" +
                "\n".join(all_errors))

    def _try_download_url(self, url: str, destination: Path) -> Path:
        """
        Attempt to download from a specific URL with appropriate method.

        Args:
            url: URL to download from
            destination: Local path to save the file

        Returns:
            Path to the downloaded file

        Raises:
            Exception: If download fails
        """
        temp_path = destination.with_suffix(destination.suffix + '.tmp')

        # Check if URL is NASA CDDIS FTPS
        if 'cddis.eosdis.nasa.gov' in url:
            return self._download_from_nasa_cddis(url, destination)
        else:
            # Use urllib for standard FTP/HTTP
            with tqdm(unit='B', unit_scale=True,
                      desc=destination.name) as pbar:

                def update_pbar(count, block_size, total_size):
                    if total_size != -1:
                        pbar.total = total_size
                    pbar.update(block_size)

                request.urlretrieve(url, temp_path, reporthook=update_pbar)

        # Handle .gz files
        if url.endswith('.gz'):
            with gzip.open(temp_path, 'rb') as f_in:
                with open(destination, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            temp_path.unlink()
        else:
            temp_path.rename(destination)

        return destination

    def _download_from_nasa_cddis(self, url: str, destination: Path) -> Path:
        """
        Download file from NASA CDDIS server using FTPS.

        Args:
            url: URL to download from (must be NASA CDDIS)
            destination: Local path to save the file

        Returns:
            Path to the downloaded file

        Raises:
            Exception: If download fails or no credentials are configured
        """
        if self.user_email is None:
            raise RuntimeError(
                "NASA CDDIS requires authentication. Set CDDIS_MAIL environment variable.\n"
                "Register at: https://urs.earthdata.nasa.gov/users/new")

        # Parse URL to extract directory and filename
        parts = url.replace('ftp://', '').replace('ftps://', '').split('/')
        host = parts[0]
        directory = '/'.join(parts[1:-1])
        filename = parts[-1]

        print(f"Connecting to {host} using FTPS...")
        ftps = FTP_TLS(host=host)
        ftps.login(user='anonymous', passwd=self.user_email)
        ftps.prot_p()

        # Change directory one level at a time to avoid navigation issues
        # But don't print the directory contents
        for subdir in directory.split('/'):
            if subdir:  # Skip empty parts
                try:
                    ftps.cwd(subdir)
                except error_perm as e:
                    raise RuntimeError(
                        f"Failed to change to directory {subdir}: {str(e)}")

        # Check if the file exists without printing directory contents
        if filename not in ftps.nlst():
            raise RuntimeError(
                f"File {filename} not found in directory {directory}")

        temp_path = destination.with_suffix(destination.suffix + '.tmp')
        with open(temp_path, 'wb') as f:
            with tqdm(unit='B', unit_scale=True,
                      desc=destination.name) as pbar:
                # Define callback function to update progress bar
                def write_callback(data):
                    f.write(data)
                    pbar.update(len(data))

                # Estimate file size for progress bar if possible
                try:
                    size = ftps.size(filename)
                    if size:
                        pbar.total = size
                except:
                    pass

                print(f"Retrieving file: {filename}")
                # Download the file
                ftps.retrbinary(f"RETR {filename}", write_callback)

        ftps.quit()

        # Handle .gz files
        if filename.endswith('.gz'):
            with gzip.open(temp_path, 'rb') as f_in:
                with open(destination, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            temp_path.unlink()
        else:
            temp_path.rename(destination)

        return destination

    def _construct_alternate_url(self, original_url: str,
                                 alt_server: str) -> str:
        """
        Construct an alternate URL based on the server's directory structure.

        Args:
            original_url: Original URL
            alt_server: Alternate server base URL

        Returns:
            Constructed alternate URL
        """
        # Remove protocol and server from original URL to get the path
        _, _, server_path = original_url.partition('://')
        server, _, path = server_path.partition('/')

        # Extract filename
        filename = Path(path).name

        # Default for most servers (might need adjustment for specific servers)
        return f"{alt_server.rstrip('/')}/{path}"

    def _construct_nasa_cddis_url(self, file_info: dict) -> str:
        """
        Construct URL specifically for NASA CDDIS server.

        Args:
            file_info: Dictionary containing file information:
                - gps_week: GPS week
                - filename: Filename without path
                - type: 'orbit' or 'clock'
                - agency: Agency code (e.g., 'COD')

        Returns:
            Complete NASA CDDIS URL
        """
        gps_week = file_info.get('gps_week')
        filename = file_info.get('filename')
        file_type = file_info.get('type', 'orbit')
        agency = file_info.get('agency', '').upper()

        # NASA CDDIS directory structure for GNSS products
        # For orbits: /archive/gnss/products/{GPS_WEEK}/{FILENAME}.gz
        # Reference: https://cddis.nasa.gov/Data_and_Derived_Products/GNSS/orbit_products.html

        # For recent GPS weeks, we need to use the 'gnss/products' path
        base_path = f"{self.NASA_FTP}/gnss/products/{gps_week}/{filename}.gz"
        return base_path
