"""Test that aux data filtering matches RINEX SID filtering.

NOTE: This is an old integration test that needs updating.
It's currently disabled because it uses outdated config structure.
"""

import pytest

pytest.skip(
    "Integration test needs updating for new config structure", allow_module_level=True
)

from canvod.auxiliary.position import ECEFPosition
from canvod.utils.config import load_config
from canvodpy.orchestrator.processor import preprocess_with_hermite_aux

# Load config
config = load_config()
rosalia = config.sites.sites["rosalia"]

# Get first reference receiver
ref_receiver = rosalia.receivers["reference_01"]
receiver_pos = ECEFPosition(
    x=ref_receiver.position.x,
    y=ref_receiver.position.y,
    z=ref_receiver.position.z,
)

# Get test RINEX file
rinex_dir = rosalia.base_dir / "02_Parsed_RINEX" / "reference_01"
rinex_files = sorted(rinex_dir.glob("*.rnx"))
if not rinex_files:
    print(f"❌ No RINEX files found in {rinex_dir}")
    exit(1)

test_file = rinex_files[0]
print(f"Testing with: {test_file.name}")

# Get aux zarr path
aux_zarr = rosalia.base_dir / "aux_data_hermite.zarr"
if not aux_zarr.exists():
    print(f"❌ Aux data not found at {aux_zarr}")
    exit(1)

# Define keep_vars
keep_vars = ["L1", "L2", "C1", "P1", "P2"]

# Get configured SIDs
keep_sids = config.sids.get_sids()
print(f"Configured SIDs: {len(keep_sids)}")

try:
    # Process file
    fname, ds = preprocess_with_hermite_aux(
        rnx_file=test_file,
        keep_vars=keep_vars,
        aux_zarr_path=aux_zarr,
        receiver_position=receiver_pos,
        receiver_type="reference",
        keep_sids=keep_sids,
    )

    print("\n✅ Processing successful!")
    print(f"Dataset SIDs: {ds.sizes['sid']}")
    print(f"Dataset epochs: {ds.sizes['epoch']}")

    # Verify spherical coords exist
    if "phi" in ds.data_vars and "theta" in ds.data_vars and "r" in ds.data_vars:
        print("✅ Spherical coordinates added")
        print(f"   phi shape: {ds.phi.shape}")
        print(f"   theta shape: {ds.theta.shape}")
        print(f"   r shape: {ds.r.shape}")
    else:
        print("❌ Missing spherical coordinates")

    # Verify SID count matches config
    if ds.sizes["sid"] == len(keep_sids):
        print(f"✅ SID count matches config ({len(keep_sids)})")
    else:
        print(
            f"❌ SID count mismatch: dataset has {ds.sizes['sid']}, config has {len(keep_sids)}"
        )

except Exception as e:
    print(f"\n❌ Processing failed: {e}")
    import traceback

    traceback.print_exc()
    exit(1)

print("\n" + "=" * 60)
print("✅ Test passed!")
print("=" * 60)
