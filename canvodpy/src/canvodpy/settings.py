"""
Application settings management.

This module provides centralized configuration management for gnssvodpy,
including FTP server credentials and other environment-based settings.

File: src/gnssvodpy/settings.py
"""

import os
from pathlib import Path
from typing import Optional

# Load .env file from project root before anything else
try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).parent.parent.parent / '.env'
    if _env_path.exists():
        load_dotenv(_env_path)
except ImportError:
    pass  # dotenv not available


class AppSettings:
    """
    Application settings loaded from environment variables.

    This class handles configuration for:
    - CDDIS FTP authentication (optional, enables NASA CDDIS fallback)
    - ESA FTP server (default, no authentication required)
    - Root directory for GNSS data

    FTP Server Strategy:
    -------------------
    The application uses a two-tier FTP server architecture:

    1. **ESA (Primary)**: ftp://gssc.esa.int/gnss
       - No authentication required
       - Works out-of-the-box without any configuration
       - Default server for all downloads

    2. **NASA CDDIS (Optional Fallback)**: ftp://gdc.cddis.eosdis.nasa.gov
       - Requires user registration and email for authentication
       - Automatically enabled when CDDIS_MAIL is configured
       - Used as fallback if ESA server fails
       - Register at: https://urs.earthdata.nasa.gov/users/new

    Configuration:
    -------------
    Set environment variables in a .env file or export them:

    ```bash
    # Optional: Enable NASA CDDIS fallback (requires registration)
    CDDIS_MAIL=your.email@example.com

    # Optional: Override default data directory
    GNSS_ROOT_DIR=/path/to/your/data
    ```

    Without CDDIS_MAIL, the application will:
    - Use ESA FTP server exclusively (works perfectly fine)
    - Skip NASA CDDIS fallback attempts
    - Log informational messages about CDDIS being unavailable
    """

    def __init__(self):
        """Initialize settings from environment variables."""
        self.cddis_mail: Optional[str] = self._load_email()
        self.gnss_root_dir: Optional[str] = os.getenv('GNSS_ROOT_DIR')

    def _load_email(self) -> Optional[str]:
        """Load and validate email from environment."""
        email = os.getenv('CDDIS_MAIL')
        if email and '@' in email:
            return email
        return None

    @property
    def has_cddis_credentials(self) -> bool:
        """Check if valid CDDIS credentials are configured."""
        return self.cddis_mail is not None

    @property
    def gnss_root_path(self) -> Path:
        """Get GNSS root directory as Path object."""
        if self.gnss_root_dir:
            return Path(self.gnss_root_dir)
        # Default fallback
        return Path.cwd() / "data"

    def get_user_email(self) -> Optional[str]:
        """
        Get user email for FTP authentication.

        Returns:
            Email string if configured and valid, None otherwise.
        """
        return self.cddis_mail

    def log_configuration_status(self, logger=None) -> None:
        """
        Log the current configuration status.

        Args:
            logger: Optional logger instance. If None, uses print().
        """
        log_fn = logger.info if logger else print

        if self.has_cddis_credentials:
            log_fn(f"✓ CDDIS credentials configured: {self.cddis_mail}")
            log_fn("  NASA CDDIS fallback enabled")
        else:
            log_fn("ℹ No CDDIS credentials configured")
            log_fn("  Using ESA FTP server exclusively (no authentication required)")
            log_fn("  To enable NASA CDDIS fallback, set CDDIS_MAIL environment variable")
            log_fn("  Register at: https://urs.earthdata.nasa.gov/users/new")


# Global settings instance
_settings: Optional[AppSettings] = None


def get_settings() -> AppSettings:
    """
    Get the global settings instance (singleton pattern).

    Returns:
        AppSettings instance loaded from environment.
    """
    global _settings
    if _settings is None:
        _settings = AppSettings()
    return _settings


def reload_settings() -> AppSettings:
    """
    Force reload settings from environment.

    Useful for testing or when environment variables change.

    Returns:
        New AppSettings instance.
    """
    global _settings
    # Reload .env file
    try:
        from dotenv import load_dotenv
        _env_path = Path(__file__).parent.parent.parent / '.env'
        if _env_path.exists():
            load_dotenv(_env_path, override=True)
    except ImportError:
        pass
    
    _settings = AppSettings()
    return _settings
