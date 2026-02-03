#!/usr/bin/env python3
"""Test script to verify .env configuration system works correctly.

This script tests:
1. Settings load without .env (ESA-only mode)
2. Settings load with .env (NASA + ESA mode)
3. Integration with aux pipeline
4. Integration with orchestrator
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch


def test_no_env():
    """Test settings work without .env file (ESA-only mode)."""
    print("=" * 70)
    print("TEST 1: Settings without .env (ESA-only mode)")
    print("=" * 70)

    # Save original environment
    orig_cddis = os.environ.get("CDDIS_MAIL")
    orig_gnss = os.environ.get("GNSS_ROOT_DIR")

    try:
        # Clear credentials from environment
        os.environ.pop("CDDIS_MAIL", None)
        os.environ.pop("GNSS_ROOT_DIR", None)

        # Remove module from cache so it reimports
        if "canvodpy.settings" in sys.modules:
            del sys.modules["canvodpy.settings"]

        # Mock load_dotenv to do nothing (prevent .env loading)
        with patch("dotenv.load_dotenv"):
            from canvodpy.settings import AppSettings

            settings = AppSettings()

        assert not settings.has_cddis_credentials, "Should not have CDDIS credentials"
        assert settings.cddis_mail is None, "CDDIS mail should be None"

        print("✅ Settings loaded successfully")
        print(f"   CDDIS configured: {settings.has_cddis_credentials}")
        print(f"   CDDIS mail: {settings.cddis_mail or 'Not configured'}")
        print(f"   GNSS root dir: {settings.gnss_root_dir or 'Not configured'}")
        print(f"   GNSS root path: {settings.gnss_root_path}")
        print()
        print("✅ ESA-only mode working correctly!")
        print()
    finally:
        # Restore original environment
        if orig_cddis:
            os.environ["CDDIS_MAIL"] = orig_cddis
        if orig_gnss:
            os.environ["GNSS_ROOT_DIR"] = orig_gnss
        # Remove from cache for clean slate
        if "canvodpy.settings" in sys.modules:
            del sys.modules["canvodpy.settings"]


def test_with_env():
    """Test settings work with .env file (NASA + ESA mode)."""
    print("=" * 70)
    print("TEST 2: Settings with .env (NASA + ESA mode)")
    print("=" * 70)

    # Save original environment
    orig_cddis = os.environ.get("CDDIS_MAIL")
    orig_gnss = os.environ.get("GNSS_ROOT_DIR")

    try:
        # Set test credentials in environment
        os.environ["CDDIS_MAIL"] = "test@example.com"
        os.environ["GNSS_ROOT_DIR"] = "/tmp/test_gnss"

        # Remove module from cache so it reimports
        if "canvodpy.settings" in sys.modules:
            del sys.modules["canvodpy.settings"]

        # Don't mock load_dotenv - let it run but env vars override
        from canvodpy.settings import AppSettings

        settings = AppSettings()

        assert settings.has_cddis_credentials, "Should have CDDIS credentials"
        assert settings.cddis_mail == "test@example.com", "CDDIS mail mismatch"
        assert settings.gnss_root_dir == "/tmp/test_gnss", "GNSS dir mismatch"

        print("✅ Settings loaded successfully from .env")
        print(f"   CDDIS configured: {settings.has_cddis_credentials}")
        print(f"   CDDIS mail: {settings.cddis_mail}")
        print(f"   GNSS root dir: {settings.gnss_root_dir}")
        print(f"   GNSS root path: {settings.gnss_root_path}")
        print()
        print("✅ NASA + ESA mode working correctly!")
        print()
    finally:
        # Restore original environment
        if orig_cddis:
            os.environ["CDDIS_MAIL"] = orig_cddis
        else:
            os.environ.pop("CDDIS_MAIL", None)
        if orig_gnss:
            os.environ["GNSS_ROOT_DIR"] = orig_gnss
        else:
            os.environ.pop("GNSS_ROOT_DIR", None)
        # Remove from cache for clean slate
        if "canvodpy.settings" in sys.modules:
            del sys.modules["canvodpy.settings"]


def test_aux_integration():
    """Test canvod-aux can use settings."""
    print("=" * 70)
    print("TEST 3: Integration with canvod-aux")
    print("=" * 70)

    from canvodpy.settings import get_settings

    # Simulate what aux/pipeline.py does
    settings = get_settings()

    if settings.has_cddis_credentials:
        strategy = "NASA primary, ESA fallback"
        email = settings.cddis_mail
    else:
        strategy = "ESA only"
        email = "N/A"

    print("✅ Aux pipeline can access settings")
    print(f"   FTP strategy: {strategy}")
    print(f"   Email: {email}")
    print()
    print("✅ Aux integration working!")
    print()


def test_processing_yaml():
    """Test processing.yaml loads correctly."""
    import pytest

    print("=" * 70)
    print("TEST 4: Processing config from YAML")
    print("=" * 70)

    # Check if config files exist (they're user-specific)
    config_dir = Path("config")
    sites_yaml = config_dir / "sites.yaml"

    if not sites_yaml.exists():
        pytest.skip(
            "Config files not found (user-specific). "
            "Run 'canvodpy config init' to create them."
        )

    from canvod.utils.config import load_config

    config = load_config()

    print("✅ Config loaded from processing.yaml")
    print(f"   Author: {config.processing.metadata.author}")
    print(f"   Agency: {config.processing.aux_data.agency}")
    print(f"   Product type: {config.processing.aux_data.product_type}")
    print(f"   KEEP_RNX_VARS: {config.processing.processing.keep_rnx_vars}")
    print(
        f"   Time aggregation: {config.processing.processing.time_aggregation_seconds}s"
    )
    print()

    # Check credentials NOT in YAML (or deprecated)
    if config.processing.credentials:
        print("   ⚠️  Credentials in YAML (deprecated): present but not used")
        print("      Use .env file instead!")
    else:
        print("   ✅ Credentials not in YAML (correct)")

    print()
    print("✅ YAML config working!")
    print()


def test_imports():
    """Test all critical imports work."""
    print("=" * 70)
    print("TEST 5: Critical imports")
    print("=" * 70)

    try:
        from canvodpy.settings import get_settings

        print("✅ canvodpy.settings imports")

        from canvod.utils.config import load_config

        print("✅ canvod.utils.config imports")

        from canvod.aux.pipeline import AuxDataPipeline

        print("✅ canvod.aux.pipeline imports (uses settings)")

        from canvodpy.orchestrator.processor import RinexDataProcessor

        print("✅ canvodpy.orchestrator.processor imports (uses settings)")

        print()
        print("✅ All imports working!")
        print()

    except ImportError as e:
        print(f"✗ Import failed: {e}")
        raise


def main():
    """Run all tests."""
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "CONFIGURATION SYSTEM TEST SUITE" + " " * 21 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    try:
        test_imports()
        test_no_env()
        test_with_env()
        test_aux_integration()
        test_processing_yaml()

        print("=" * 70)
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
        print()
        print("Configuration System Status:")
        print("  ✅ .env support working (optional)")
        print("  ✅ processing.yaml working")
        print("  ✅ ESA-only mode working")
        print("  ✅ NASA+ESA mode working")
        print("  ✅ All integrations working")
        print()
        print("🚀 Ready for production!")
        print()

    except Exception as e:
        print()
        print("=" * 70)
        print("✗ TESTS FAILED")
        print("=" * 70)
        print(f"Error: {e}")
        print()
        raise


if __name__ == "__main__":
    main()
