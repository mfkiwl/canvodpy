#!/bin/bash
# Add and commit marimo notebooks to demo subrepo

set -e

cd /Users/work/Developer/GNSS/canvodpy/demo

echo "=========================================="
echo "Committing Marimo Notebooks to demo/"
echo "=========================================="
echo ""

# Check git status
echo "📋 Current demo/ git status:"
git status --short
echo ""

# Add notebooks
echo "➕ Adding marimo notebooks..."
git add 01_factory_basics.py \
        02_workflow_usage.py \
        03_functional_api.py \
        04_custom_components.py \
        API_NOTEBOOKS_README.md

echo "✅ Files staged"
echo ""

# Commit
echo "💾 Committing..."
git commit -m "feat: add marimo notebooks for API redesign

Four interactive notebooks demonstrating the new API:

1. 01_factory_basics.py
   - List and create components
   - Interactive parameter selection
   - Grid visualization

2. 02_workflow_usage.py
   - VODWorkflow initialization
   - Structured logging context
   - Complete pipeline demo

3. 03_functional_api.py
   - Pure functions for notebooks
   - Airflow integration pattern
   - Path-returning variants

4. 04_custom_components.py
   - Implement custom grid builder
   - Register with factory
   - Extension best practices

All notebooks use marimo's reactive programming model
with polars, altair, and the redesigned canVODpy API.

Run: marimo edit 01_factory_basics.py"

echo "✅ Committed to demo/ subrepo"
echo ""

echo "=========================================="
echo "✅ Demo Notebooks Complete!"
echo "=========================================="
echo ""
echo "To use:"
echo "  cd demo"
echo "  marimo edit 01_factory_basics.py"
echo ""
echo "Next: Update main canvodpy repo README to link to demos"
