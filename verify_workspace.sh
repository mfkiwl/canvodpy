#!/bin/bash
# Verify Workspace Dependency Configuration

echo "🔍 Verifying Workspace Dependency Setup"
echo "========================================"
echo ""

# 1. Check workspace configuration
echo "1. Root workspace configuration:"
if grep -q "\[tool.uv.workspace\]" pyproject.toml; then
    echo "   ✅ Workspace configured at root"
    grep -A3 "\[tool.uv.workspace\]" pyproject.toml
else
    echo "   ❌ No workspace configuration found"
fi
echo ""

# 2. Check umbrella package dependencies
echo "2. Umbrella package dependencies:"
if grep -q "canvod-readers" canvodpy/pyproject.toml; then
    echo "   ✅ Sub-packages declared in dependencies"
    grep -A5 "^dependencies =" canvodpy/pyproject.toml
else
    echo "   ❌ Sub-packages not in dependencies"
fi
echo ""

# 3. Check workspace sources
echo "3. Workspace sources configuration:"
if grep -q "\[tool.uv.sources\]" canvodpy/pyproject.toml; then
    echo "   ✅ Workspace sources configured"
    grep -A3 "\[tool.uv.sources\]" canvodpy/pyproject.toml
else
    echo "   ❌ No workspace sources configured"
fi
echo ""

# 4. Check lock file
echo "4. Lock file status:"
if [ -f "uv.lock" ]; then
    echo "   ✅ Lock file exists at root"
    echo "   Size: $(du -h uv.lock | cut -f1)"
else
    echo "   ⚠️  No lock file (run 'uv sync' to create)"
fi
echo ""

# 5. Test sync command
echo "5. Testing uv sync (dry-run):"
echo "   Run this manually: cd $(pwd) && uv sync"
echo ""

echo "========================================"
echo "✅ Configuration verification complete!"
echo ""
echo "Next steps:"
echo "1. Run: uv sync"
echo "2. Test: uv run python -c 'from canvod.readers import Rnxv3Obs'"
echo "3. Test: uv run python -c 'from canvod.aux import Sp3File'"
