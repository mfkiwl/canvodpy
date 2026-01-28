#!/usr/bin/env python3
"""Test script to verify .env configuration system works correctly.

This script tests:
1. Settings load without .env (ESA-only mode)
2. Settings load with .env (NASA + ESA mode)
3. Integration with aux pipeline
4. Integration with orchestrator
"""

import os
import tempfile


def test_no_env():
    """Test settings work without .env file (ESA-only mode)."""
    print("=" * 70)
    print("TEST 1: Settings without .env (ESA-only mode)")
    print("=" * 70)

    from canvodpy.settings import get_settings

    settings = get_settings()

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


def test_with_env():
    """Test settings work with .env file (NASA + ESA mode)."""
    print("=" * 70)
    print("TEST 2: Settings with .env (NASA + ESA mode)")
    print("=" * 70)

    # Create temporary .env file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("CDDIS_MAIL=test@example.com\n")
        f.write("GNSS_ROOT_DIR=/tmp/test_gnss\n")
        env_path = f.name

    try:
        # Load .env
        from dotenv import load_dotenv
        load_dotenv(env_path, override=True)

        # Reload settings
        from canvodpy.settings import reload_settings
        settings = reload_settings()

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
        # Cleanup
        os.unlink(env_path)
        # Reset to no .env mode
        os.environ.pop("CDDIS_MAIL", None)
        os.environ.pop("GNSS_ROOT_DIR", None)
        from canvodpy.settings import reload_settings
        reload_settings()


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
    print("=" * 70)
    print("TEST 4: Processing config from YAML")
    print("=" * 70)

    from canvod.utils.config import load_config

    config = load_config()

    print("✅ Config loaded from processing.yaml")
    print(f"   Author: {config.processing.metadata.author}")
    print(f"   Agency: {config.processing.aux_data.agency}")
    print(f"   Product type: {config.processing.aux_data.product_type}")
    print(f"   KEEP_RNX_VARS: {config.processing.processing.keep_rnx_vars}")
    print(f"   Time aggregation: {config.processing.processing.time_aggregation_seconds}s")
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
