#!/usr/bin/env python3
"""Test config loader works from any directory."""

import subprocess
from pathlib import Path

# Find monorepo root (has pyproject.toml)
def find_monorepo_root(start_path: Path) -> Path:
    current = start_path
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find monorepo root")

monorepo_root = find_monorepo_root(Path(__file__).parent)

# Test directories (relative to monorepo root)
test_dirs = [
    ".",
    "canvodpy",
    "packages/canvod-readers",
    "packages/canvod-readers/tests",
    "packages/canvod-utils/src/canvod/utils/config",
]

print("=" * 70)
print("Testing config loader from multiple directories")
print("=" * 70)

failed = []
for test_dir in test_dirs:
    full_path = monorepo_root / test_dir
    if not full_path.exists():
        print(f"\n📁 Testing from: {test_dir}")
        print(f"   ⏭️  SKIPPED (directory doesn't exist)")
        continue
        
    print(f"\n📁 Testing from: {test_dir}")
    
    result = subprocess.run(
        [str(Path.home() / ".local/bin/uv"), "run", "python", "-c", 
         "from canvod.utils.config import load_config; "
         "config = load_config(); "
         "print(f'✅ Sites: {list(config.sites.sites.keys())}')"],
        cwd=full_path,
        capture_output=True,
        text=True,
    )
    
    if result.returncode == 0 and "rosalia" in result.stdout:
        print(f"   ✅ SUCCESS")
        print(f"   {result.stdout.strip()}")
    else:
        print(f"   ❌ FAILED")
        print(f"   stdout: {result.stdout}")
        print(f"   stderr: {result.stderr}")
        failed.append(test_dir)

print("\n" + "=" * 70)
if failed:
    print(f"❌ FAILED: {len(failed)}/{len(test_dirs)} directories")
    for d in failed:
        print(f"   - {d}")
else:
    print(f"✅ SUCCESS: All {len(test_dirs)} directories passed!")
print("=" * 70)
