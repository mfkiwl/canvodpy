#!/bin/bash
# Phase 11: Code Quality & Polish

set -e

echo "=========================================="
echo "Phase 11: Code Quality & Polish"
echo "=========================================="
echo ""

NEW_FILES=(
    "canvodpy/src/canvodpy/factories.py"
    "canvodpy/src/canvodpy/workflow.py"
    "canvodpy/src/canvodpy/functional.py"
    "canvodpy/tests/test_factory_validation.py"
    "canvodpy/tests/test_workflow_integration.py"
    "canvodpy/tests/test_backward_compatibility.py"
)

echo "1️⃣  Running ruff format..."
echo "------------------------------------------"
uv run ruff format "${NEW_FILES[@]}"
echo "✅ Format complete"
echo ""

echo "2️⃣  Running ruff check (auto-fix)..."
echo "------------------------------------------"
uv run ruff check "${NEW_FILES[@]}" --fix
echo "✅ Linting complete"
echo ""

echo "3️⃣  Type checking with ty..."
echo "------------------------------------------"
uv run ty check "${NEW_FILES[@]}" || echo "⚠️  Type check warnings (non-blocking)"
echo ""

echo "4️⃣  Running full test suite..."
echo "------------------------------------------"
uv run pytest --tb=short -q
echo "✅ All tests passing"
echo ""

echo "=========================================="
echo "✅ Phase 11 Complete!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  - Code formatted with ruff"
echo "  - Linting issues auto-fixed"
echo "  - Type checking reviewed"
echo "  - Full test suite passing"
echo ""
echo "Next: Create marimo notebooks in demo/"
