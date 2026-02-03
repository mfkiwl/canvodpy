"""Debug script to find what imports canvod.store."""

import sys

# Hook to trace imports
original_import = __builtins__.__import__


def trace_import(name, *args, **kwargs):
    result = original_import(name, *args, **kwargs)

    # Check if canvod.store got imported
    if name == "canvod.store" or (
        name.startswith("canvod.store") and "canvod.store" not in sys.modules
    ):
        print(f"\n🔍 FOUND IT! Import of: {name}")
        import traceback

        print("Import stack:")
        for line in traceback.format_stack()[:-1]:
            if "/canvodpy/" in line or "/canvod-" in line:
                print(line.strip())
        print("---\n")

    return result


__builtins__.__import__ = trace_import

print("=" * 60)
print("Tracing who imports canvod.store...")
print("=" * 60)


print("\n" + "=" * 60)
print("Done importing canvodpy.api")
print(f"canvod.store in sys.modules: {'canvod.store' in sys.modules}")
if "canvod.store" in sys.modules:
    print("❌ canvod.store was imported!")
else:
    print("✅ canvod.store was NOT imported")
print("=" * 60)
