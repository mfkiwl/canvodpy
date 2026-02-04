#!/usr/bin/env python3
"""Run new integration tests."""

import subprocess
import sys

tests = [
    "canvodpy/tests/test_factory_validation.py",
    "canvodpy/tests/test_workflow_integration.py",
    "canvodpy/tests/test_backward_compatibility.py",
]

print("Running new integration tests...")
print("=" * 60)

for test in tests:
    print(f"\n📝 {test}")
    print("-" * 60)
    result = subprocess.run(
        ["uv", "run", "pytest", test, "-v"],
        cwd="/Users/work/Developer/GNSS/canvodpy",
    )
    if result.returncode != 0:
        print(f"❌ Tests failed in {test}")
        sys.exit(1)

print("\n" + "=" * 60)
print("✅ All integration tests passed!")
