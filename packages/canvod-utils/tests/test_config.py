#!/usr/bin/env python3
"""
Test script to verify configuration system imports and basic functionality.
Run this after installing canvod-utils to ensure everything works.
"""

import sys
from pathlib import Path

print("Testing configuration system imports...")
print("=" * 70)

# Test imports
try:
    from canvod.utils.config import load_config
    from canvod.utils.config.models import (
        CanvodConfig,
        ProcessingConfig,
        SidsConfig,
        SitesConfig,
    )
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test model instantiation
try:
    from canvod.utils.config.models import (
        AuxDataConfig,
        CredentialsConfig,
    )

    # Create test config
    creds = CredentialsConfig(
        cddis_mail="test@example.com",
        gnss_root_dir=Path.cwd(),
    )
    print(f"✓ Created CredentialsConfig: {creds.cddis_mail}")

    aux_data = AuxDataConfig(agency="COD", product_type="final")
    print(f"✓ Created AuxDataConfig: {aux_data.agency}")

    # Test FTP server selection
    servers = aux_data.get_ftp_servers(creds.cddis_mail)
    print(f"✓ FTP servers (with CDDIS): {len(servers)} servers")
    for server, auth in servers:
        print(f"    - {server} (auth: {auth is not None})")

    servers_no_cddis = aux_data.get_ftp_servers(None)
    print(f"✓ FTP servers (without CDDIS): {len(servers_no_cddis)} servers")

except Exception as e:
    print(f"✗ Model test failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("✓ All tests passed!")
print("\nNext steps:")
print("  1. Run: canvodpy config init")
print("  2. Edit config/processing.yaml")
print("  3. Edit config/sites.yaml")
print("  4. Run: canvodpy config validate")
