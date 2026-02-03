"""Quick test to verify configuration paths are correct."""

from canvodpy.research_sites_config import RESEARCH_SITES

print("=" * 60)
print("Configuration Path Test")
print("=" * 60)

rosalia_config = RESEARCH_SITES["Rosalia"]

print(f"\nbase_dir: {rosalia_config['base_dir']}")
print(f"rinex_store_path: {rosalia_config['rinex_store_path']}")
print(f"vod_store_path: {rosalia_config['vod_store_path']}")

# Check if paths are correct (not in packages/canvod-readers/)
base_dir_str = str(rosalia_config["base_dir"])

if "canvod-readers" in base_dir_str:
    print("\n❌ ERROR: Paths still point to canvod-readers!")
    print(f"   Found: {base_dir_str}")
elif "canvodpy-test-data" in base_dir_str:
    print("\n✅ SUCCESS: Paths correctly point to test data!")
else:
    print(f"\n⚠️  WARNING: Unexpected path: {base_dir_str}")

print("=" * 60)
