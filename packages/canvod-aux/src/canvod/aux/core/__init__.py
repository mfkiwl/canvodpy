"""Core abstractions for auxiliary file handling."""

from canvod.aux.core.base import AuxFile
from canvod.aux.core.downloader import FileDownloader, FtpDownloader

__all__ = [
    "AuxFile",
    "FileDownloader",
    "FtpDownloader",
]
