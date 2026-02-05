#!/bin/bash
# Final verification before committing API redesign

set -e

cd /Users/work/Developer/GNSS/canvodpy

echo "=========================================="
echo "API Redesign Final Verification"
echo "=========================================="
echo ""

echo "1️⃣  Running full test suite..."
echo "------------------------------------------"
uv run pytest -x --tb=short -q
echo "✅ Tests passing"
echo ""

echo "2️⃣  Checking code quality..."
echo "------------------------------------------"
uv run ruff check canvodpy/src/canvodpy/{factories,workflow,functional}.py
echo "✅ Ruff check clean"
echo ""

echo "3️⃣  Git status..."
echo "------------------------------------------"
git status --short | head -20
echo ""

echo "=========================================="
echo "✅ Ready to Commit!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. ./commit_phase11.sh"
echo "  2. ./commit_demo_notebooks.sh"
echo "  3. Review git log"
echo "  4. Ready for PR!"
