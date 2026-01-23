"""Test that circular import is fixed - minimal version."""

import sys
import ast
from pathlib import Path

root = Path(__file__).parent

print("Analyzing import structure for circular dependencies...")
print("=" * 70)

# Read the api.py file
api_file = root / 'canvodpy' / 'src' / 'canvodpy' / 'api.py'
with open(api_file) as f:
    api_content = f.read()

# Parse to find top-level imports
tree = ast.parse(api_content)

top_level_imports = []
lazy_imports = []

for node in ast.walk(tree):
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        # Check if this import is at module level or inside a function/class
        # Top-level imports have col_offset == 0
        if hasattr(node, 'lineno'):
            line = api_content.split('\n')[node.lineno - 1]
            indent = len(line) - len(line.lstrip())
            
            if isinstance(node, ast.ImportFrom):
                module = node.module or ''
                names = [alias.name for alias in node.names]
                import_info = f"from {module} import {', '.join(names)}"
            else:
                names = [alias.name for alias in node.names]
                import_info = f"import {', '.join(names)}"
            
            if indent == 0:
                top_level_imports.append(import_info)
            else:
                lazy_imports.append((indent, import_info))

print("\n📦 TOP-LEVEL IMPORTS (loaded immediately):")
print("-" * 70)
for imp in top_level_imports:
    if 'canvod.store' in imp or 'canvod.vod' in imp:
        print(f"  ❌ {imp} (CIRCULAR DEPENDENCY RISK!)")
    elif 'TYPE_CHECKING' in imp:
        print(f"  ✅ {imp} (type hints only, safe)")
    else:
        print(f"  ✅ {imp}")

print("\n📦 LAZY IMPORTS (loaded when function/class is used):")
print("-" * 70)
for indent, imp in lazy_imports:
    spaces = ' ' * indent
    if 'canvod.store' in imp or 'canvod.vod' in imp:
        print(f"  ✅ {spaces}{imp} (LAZY - breaks circular dependency!)")
    else:
        print(f"  ⚠️  {spaces}{imp}")

# Check for problematic patterns
has_top_level_circular = any(
    'canvod.store' in imp or 'canvod.vod' in imp or 'PipelineOrchestrator' in imp
    for imp in top_level_imports
    if 'TYPE_CHECKING' not in imp
)

has_lazy_imports = any(
    'canvod.store' in imp or 'canvod.vod' in imp or 'PipelineOrchestrator' in imp
    for _, imp in lazy_imports
)

print("\n" + "=" * 70)
if has_top_level_circular:
    print("❌ CIRCULAR DEPENDENCY EXISTS!")
    print("   Found top-level imports of canvod.store or canvod.vod")
    sys.exit(1)
elif has_lazy_imports:
    print("✅ CIRCULAR DEPENDENCY IS FIXED!")
    print("   All problematic imports are lazy (inside functions/classes)")
    print("   This breaks the circular dependency chain.")
else:
    print("⚠️  No circular dependency imports found (neither top-level nor lazy)")

print("\n💡 How lazy imports work:")
print("   - Module loads: imports happen sequentially, no circle")
print("   - User creates Site: only THEN does it import GnssResearchSite")
print("   - Circle is broken! 🎉")
