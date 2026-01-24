# Using pydeps for Dependency Visualization

## 🎯 What pydeps Does Better

**pydeps** analyzes actual Python imports (not just pyproject.toml), showing:
1. **Class-level dependencies** - How classes/modules within a package interact
2. **Cross-package imports** - Actual import relationships
3. **Circular imports** - Detection of import cycles

---

## 📦 Installation

```bash
~/.local/bin/uv pip install pydeps
```

---

## 🔍 Three Types of Graphs You Need

### 1. Per-Package Internal Dependencies

**Shows:** How modules/classes within ONE package depend on each other

```bash
# For canvod-readers
cd packages/canvod-readers
uv run pydeps canvod.readers \
  --max-bacon=2 \
  --cluster \
  -o ../../dependency-graphs/canvod-readers-internal.svg \
  --rmprefix canvod.

# For canvod-aux  
cd packages/canvod-aux
uv run pydeps canvod.aux \
  --max-bacon=2 \
  --cluster \
  -o ../../dependency-graphs/canvod-aux-internal.svg \
  --rmprefix canvod.

# Repeat for other packages...
```

**Options explained:**
- `--max-bacon=2` - Only show 2 levels deep (prevents overwhelming graphs)
- `--cluster` - Group by module/subpackage
- `--rmprefix canvod.` - Simplify node labels
- `-o file.svg` - Output as SVG (scales perfectly)

---

### 2. Cross-Package Dependencies

**Shows:** How packages import from each other

```bash
# From root
uv run pydeps packages \
  --max-bacon=2 \
  --cluster \
  --only canvod \
  -o dependency-graphs/cross-package.svg
```

**Options:**
- `--only canvod` - Only show canvod.* modules
- Analyzes all packages together

---

### 3. API Orchestration

**Shows:** How umbrella package (canvodpy) uses all other packages

```bash
# When umbrella package exists
uv run pydeps canvodpy \
  --max-bacon=3 \
  --cluster \
  --only canvod \
  -o dependency-graphs/api-orchestration.svg
```

---

## 🎨 Quick Commands (Once Packages Are Importable)

```bash
# Create output directory
mkdir -p dependency-graphs

# Generate all per-package graphs
for pkg in canvod-readers canvod-aux canvod-grids canvod-store canvod-utils canvod-viz canvod-vod; do
  cd packages/$pkg
  uv run pydeps canvod.${pkg#canvod-} \
    --max-bacon=2 \
    --cluster \
    --rmprefix canvod. \
    -o ../../dependency-graphs/$pkg-internal.svg
  cd ../..
done

# Cross-package view
uv run pydeps packages \
  --max-bacon=2 \
  --cluster \
  --only canvod \
  -o dependency-graphs/cross-package.svg

# API view (when available)
uv run pydeps canvodpy \
  --max-bacon=3 \
  --cluster \
  --only canvod \
  -o dependency-graphs/api-orchestration.svg
```

---

## 📊 Advanced Options

### Show Only Specific Modules

```bash
# Only show preprocessing module in canvod-aux
uv run pydeps canvod.aux.preprocessing \
  --max-bacon=2 \
  -o preprocessing-deps.svg
```

### Detect Circular Dependencies

```bash
# Check for circular imports
uv run pydeps canvod.aux \
  --show-cycles \
  -o cycles.svg
```

### Different Output Formats

```bash
# PNG (for embedding in docs)
uv run pydeps canvod.readers -T png -o readers.png

# PDF (for papers)
uv run pydeps canvod.readers -T pdf -o readers.pdf

# SVG (recommended - scales perfectly)
uv run pydeps canvod.readers -T svg -o readers.svg
```

### Control Graph Layout

```bash
# Left-to-right instead of top-to-bottom
uv run pydeps canvod.readers --rankdir=LR -o readers-lr.svg

# No clustering (flat view)
uv run pydeps canvod.readers --no-cluster -o readers-flat.svg
```

---

## 🚀 Practical Workflow for Development

### 1. During Development

```bash
# Quick check of a single module you're working on
cd packages/canvod-aux
uv run pydeps canvod.aux.preprocessing --max-bacon=1 -o temp.svg
open temp.svg  # Review dependencies
```

### 2. Before Committing

```bash
# Check for circular imports
uv run pydeps canvod.aux --show-cycles

# Ensure no unexpected cross-package deps
uv run pydeps packages --only canvod -o review.svg
```

### 3. For Documentation

```bash
# Generate clean, publication-quality graphs
uv run pydeps canvod.readers \
  --max-bacon=2 \
  --cluster \
  --rmprefix canvod. \
  --rankdir=TB \
  -T svg \
  -o docs/images/readers-architecture.svg
```

---

## 📝 Interpreting the Graphs

### Node Colors (default pydeps coloring)
- **Lighter colors** - Modules at package root
- **Darker colors** - Nested submodules
- **Clusters** - Subpackages grouped together

### Arrow Meanings
- **Solid arrow** - Direct import (`from X import Y`)
- **Thickness** - More imports = thicker arrow

### What to Look For

**Good signs:**
- ✅ Clear hierarchy (top-to-bottom or left-to-right flow)
- ✅ Minimal cross-cluster connections
- ✅ No circular arrows

**Warning signs:**
- ⚠️ Circular connections (import cycles)
- ⚠️ Dense spider webs (high coupling)
- ⚠️ Many cross-package imports (tight coupling)

---

## 🎯 Your Current Architecture Goals

Based on your Sollbruchstellen principle:

1. **Per-package graphs should show:**
   - Clear internal organization
   - Minimal internal circular dependencies
   - Logical module grouping

2. **Cross-package graph should show:**
   - Only necessary connections
   - No circular package dependencies
   - Clear foundation → consumer flow

3. **API graph should show:**
   - How umbrella package orchestrates everything
   - Configuration flow (config loaded → passed to packages)
   - Clean top-level API surface

---

## 💡 Tips & Best Practices

### Reduce Graph Complexity

```bash
# Exclude test files
uv run pydeps canvod.aux --exclude=test_* -o clean.svg

# Exclude external deps
uv run pydeps canvod.aux --no-externals -o internal-only.svg

# Focus on specific depth
uv run pydeps canvod.aux --max-bacon=1 -o shallow.svg  # Only direct deps
```

### For Large Packages

```bash
# Analyze only a submodule
uv run pydeps canvod.readers.rnxv3 -o rnxv3-only.svg

# Set minimum cluster size to reduce clutter
uv run pydeps canvod.aux --min-cluster-size=3 -o simplified.svg
```

### Compare Before/After

```bash
# Before refactoring
uv run pydeps canvod.aux -o before.svg

# ... make changes ...

# After refactoring
uv run pydeps canvod.aux -o after.svg

# Compare visually
open before.svg after.svg
```

---

## 🔧 Troubleshooting

### "No module named 'canvod.X'"

**Solution:** Run from package directory where module is importable:

```bash
cd packages/canvod-aux
uv run pydeps canvod.aux -o ../../output.svg
```

### "AttributeError: module has no attribute"

**Solution:** Package needs to be properly installed:

```bash
cd /path/to/canvodpy
uv sync  # Ensure all packages installed in editable mode
```

### Graphs Too Complex

**Solution:** Reduce scope:

```bash
# Lower bacon number
--max-bacon=1  # Only direct dependencies

# Increase cluster size  
--min-cluster-size=5  # Only show clusters with 5+ modules

# Focus on one module
uv run pydeps canvod.aux.preprocessing  # Just this module
```

---

## 📚 Further Reading

- **pydeps GitHub:** https://github.com/thebjorn/pydeps
- **Graphviz Documentation:** https://graphviz.org/documentation/
- **Your package metrics:** `python scripts/analyze_dependencies.py --format report`

---

**Remember:** pydeps analyzes actual imports, so packages must be importable!
