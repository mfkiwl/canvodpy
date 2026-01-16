"""File downloaders for auxiliary GNSS data."""

from abc import ABC, abstractmethod
from ftplib import FTP_TLS, error_perm
import gzip
from pathlib import Path
import shutil
from typing import Optional
from urllib import request

from tqdm import tqdm


class FileDownloader(ABC):
    """Protocol defining the interface for file downloading implementations."""

    @abstractmethod
    def download(self, url: str, destination: Path, file_info: dict | None = None) -> Path:
        """Download a file from url to destination."""
        pass


class FtpDownloader(FileDownloader):
    """Implementation of FileDownloader for FTP downloads with progress bar and fallback servers."""

    NASA_FTP = "ftp://gdc.cddis.eosdis.nasa.gov"

    def __init__(
        self,
        alt_servers: list[str] | None = None,
        user_email: str | None = None,
    ):
        """
        Initialize downloader with optional alternate servers.

        FTP Server Strategy:
        ------------------
        - Primary: Uses the URL provided in download() call (typically ESA)
        - Fallback: NASA CDDIS (requires authentication with user_email)

        Args:
            alt_servers: List of alternative FTP server URLs
            user_email: Email for authenticated FTP servers (NASA CDDIS)
        """
        if alt_servers is None:
            if user_email is not None:
                self.alt_servers = [self.NASA_FTP]
                print("ℹ NASA CDDIS fallback enabled")
            else:
                self.alt_servers = []
                print("ℹ Using ESA FTP exclusively")
                print("  To enable NASA CDDIS fallback, set CDDIS_MAIL environment variable")
        else:
            if user_email is None:
                self.alt_servers = [s for s in alt_servers if "cddis" not in s.lower()]
                if len(self.alt_servers) < len(alt_servers):
                    print("⚠ Skipping CDDIS servers (no credentials)")
            else:
                self.alt_servers = alt_servers

        self.user_email = user_email

    def download(
        self,
        url: str,
        destination: Path,
        file_info: dict | None = None,
    ) -> Path:
        """
        Download a file from FTP with progress tracking and fallback servers.

        Args:
            url: Primary URL to download from
            destination: Local path to save the file
            file_info: Additional information (agency, GPS week, etc.)

        Returns:
            Path to the downloaded file
        """
        destination.parent.mkdir(parents=True, exist_ok=True)

        try:
            print(f"Attempting to download from primary server: {url}")
            return self._try_download_url(url, destination)
        except Exception as e:
            print(f"Primary download failed: {str(e)}")

            all_errors = [f"Primary server error: {str(e)}"]

            if not self.alt_servers:
                print("ℹ No fallback servers available")
                raise RuntimeError(
                    f"Failed to download file from primary server.\n"
                    f"\nPrimary URL: {url}\n"
                    f"Error: {str(e)}\n"
                    f"\nPossible causes:\n"
                    f"  - File not yet available (check latency: {file_info.get('latency', 'unknown')} hours)\n"
                    f"  - Incorrect FTP path for server\n"
                    f"  - Temporary server issue\n"
                    f"\nTip: Set CDDIS_MAIL environment variable to enable NASA CDDIS fallback"
                )

            for alt_server in self.alt_servers:
                try:
                    if file_info and "cddis" in alt_server.lower():
                        alt_url = self._construct_nasa_cddis_url(file_info)
                    else:
                        alt_url = self._construct_alternate_url(url, alt_server)

                    print(f"Trying alternate server: {alt_url}")
                    return self._try_download_url(alt_url, destination)
                except Exception as alt_e:
                    error_msg = f"Alternate server {alt_server} error: {str(alt_e)}"
                    print(error_msg)
                    all_errors.append(error_msg)

            raise RuntimeError(
                "Failed to download from all servers. Errors:\n" + "\n".join(all_errors)
            )

    def _try_download_url(self, url: str, destination: Path) -> Path:
        """Attempt to download from a specific URL."""
        temp_path = destination.with_suffix(destination.suffix + ".tmp")

        if "cddis.eosdis.nasa.gov" in url:
            return self._download_from_nasa_cddis(url, destination)
        else:
            with tqdm(unit="B", unit_scale=True, desc=destination.name) as pbar:

                def update_pbar(count, block_size, total_size):
                    if total_size != -1:
                        pbar.total = total_size
                    pbar.update(block_size)

                request.urlretrieve(url, temp_path, reporthook=update_pbar)

        if url.endswith(".gz"):
            with gzip.open(temp_path, "rb") as f_in:
                with open(destination, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            temp_path.unlink()
        else:
            temp_path.rename(destination)

        return destination

    def _download_from_nasa_cddis(self, url: str, destination: Path) -> Path:
        """Download file from NASA CDDIS server using FTPS."""
        if self.user_email is None:
            raise RuntimeError(
                "NASA CDDIS requires authentication. Set CDDIS_MAIL environment variable.\n"
                "Register at: https://urs.earthdata.nasa.gov/users/new"
            )

        parts = url.replace("ftp://", "").replace("ftps://", "").split("/")
        host = parts[0]
        directory = "/".join(parts[1:-1])
        filename = parts[-1]

        print(f"Connecting to {host} using FTPS...")
        ftps = FTP_TLS(host=host)
        ftps.login(user="anonymous", passwd=self.user_email)
        ftps.prot_p()

        for subdir in directory.split("/"):
            if subdir:
                try:
                    ftps.cwd(subdir)
                except error_perm as e:
                    raise RuntimeError(f"Failed to change to directory {subdir}: {str(e)}")

        if filename not in ftps.nlst():
            raise RuntimeError(f"File {filename} not found in directory {directory}")

        temp_path = destination.with_suffix(destination.suffix + ".tmp")
        with open(temp_path, "wb") as f:
            with tqdm(unit="B", unit_scale=True, desc=destination.name) as pbar:

                def write_callback(data):
                    f.write(data)
                    pbar.update(len(data))

                try:
                    size = ftps.size(filename)
                    if size:
                        pbar.total = size
                except:
                    pass

                print(f"Retrieving file: {filename}")
                ftps.retrbinary(f"RETR {filename}", write_callback)

        ftps.quit()

        if filename.endswith(".gz"):
            with gzip.open(temp_path, "rb") as f_in:
                with open(destination, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            temp_path.unlink()
        else:
            temp_path.rename(destination)

        return destination

    def _construct_alternate_url(self, original_url: str, alt_server: str) -> str:
        """Construct an alternate URL based on server's directory structure."""
        _, _, server_path = original_url.partition("://")
        server, _, path = server_path.partition("/")
        return f"{alt_server.rstrip('/')}/{path}"

    def _construct_nasa_cddis_url(self, file_info: dict) -> str:
        """Construct URL specifically for NASA CDDIS server."""
        gps_week = file_info.get("gps_week")
        filename = file_info.get("filename")
        return f"{self.NASA_FTP}/gnss/products/{gps_week}/{filename}.gz"
