"""Core abstractions for auxiliary file handling."""

from canvod.auxiliary.core.base import AuxFile
from canvod.auxiliary.core.downloader import FileDownloader, FtpDownloader

__all__ = [
    "AuxFile",
    "FileDownloader",
    "FtpDownloader",
]
