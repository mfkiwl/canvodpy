# Dependency Visualization - Complete Solution ✅

## 🎯 You're Right - Use pydeps!

**pydeps** is the professional tool for Python dependency visualization. It analyzes **actual imports** in your code, not just package metadata.

---

## 📊 What You Get

### 1. **Package-Level** (Simple - What We Have)
Shows how packages depend on each other via pyproject.toml

**Tool:** `scripts/analyze_dependencies.py`
**Command:** `just deps-report`
**Output:** Metrics + simple graph

### 2. **Module/Class-Level** (Detailed - What You Want)
Shows how classes/modules **within** each package interact

**Tool:** `pydeps`
**Command:** Manual (see below)
**Output:** Beautiful SVG graphs

### 3. **API Orchestration** (High-Level)
Shows how umbrella package uses everything + config flow

**Tool:** `pydeps` (when umbrella implemented)
**Command:** Manual
**Output:** Complete system view

---

## 🚀 Quick Start

### Install pydeps
```bash
cd /Users/work/Developer/GNSS/canvodpy
~/.local/bin/uv pip install pydeps
```

### Ensure Packages Are Installed
```bash
~/.local/bin/uv sync
```

### Generate Graph for One Package
```bash
# Example: canvod-readers internal dependencies
cd packages/canvod-readers
~/.local/bin/uv run pydeps canvod.readers \
  --max-bacon=2 \
  --cluster \
  --rmprefix canvod. \
  -o ../../dependency-graphs/canvod-readers-internal.svg

# Open it
open ../../dependency-graphs/canvod-readers-internal.svg
```

---

## 📁 Output Structure

```
dependency-graphs/
├── canvod-readers-internal.svg    # Classes/modules in canvod-readers
├── canvod-aux-internal.svg        # Classes/modules in canvod-aux
├── canvod-grids-internal.svg      # Classes/modules in canvod-grids
├── canvod-store-internal.svg      # Classes/modules in canvod-store
├── canvod-utils-internal.svg      # Classes/modules in canvod-utils
├── canvod-viz-internal.svg        # Classes/modules in canvod-viz
├── canvod-vod-internal.svg        # Classes/modules in canvod-vod
├── cross-package.svg               # How packages import each other
└── api-orchestration.svg           # How umbrella uses everything
```

---

## 🎨 For Documentation

Once you have the SVGs:

```markdown
# In docs/architecture.md

## canvod-readers Architecture

![canvod-readers internal dependencies](../dependency-graphs/canvod-readers-internal.svg)

## Cross-Package Dependencies

![Cross-package dependencies](../dependency-graphs/cross-package.svg)
```

---

## 💡 Why Two Tools?

| Tool | Purpose | Shows | Speed |
|------|---------|-------|-------|
| **analyze_dependencies.py** | Quick metrics | Package relationships | ⚡ Instant |
| **pydeps** | Detailed analysis | Actual imports/classes | 🐢 Slower |

**Use both:**
- Quick checks: `just deps-report`
- Deep analysis: `pydeps` (during dev/docs)
- Documentation: Both (metrics + graphs)

---

## 📝 What I've Created

### 1. Quick Metrics Tool ✅
**File:** `scripts/analyze_dependencies.py`
- Package-level dependency analysis
- Independence metrics
- Circular dependency detection
- Fast (instant)

**Commands:**
```bash
just deps-report    # Show metrics
just deps-graph     # Mermaid diagram
```

### 2. pydeps Guide ✅
**File:** `PYDEPS_GUIDE.md`
- Complete pydeps tutorial
- All commands explained
- Troubleshooting tips
- Best practices

### 3. Documentation ✅
**File:** `docs/dependencies.md`
- Interactive Mermaid graph
- Metrics tables
- Architecture analysis
- Sollbruchstellen evaluation

---

## 🎯 Your Development Workflow

### During Development
```bash
# Quick check: Are packages still independent?
just deps-report

# Deep dive: How does this module connect?
cd packages/canvod-aux
uv run pydeps canvod.aux.preprocessing -o temp.svg
open temp.svg
```

### Before Committing
```bash
# Check for circular imports
cd packages/canvod-aux
uv run pydeps canvod.aux --show-cycles
```

### For Documentation
```bash
# Generate all graphs for docs
mkdir -p dependency-graphs

# Per-package internal graphs
cd packages/canvod-readers
uv run pydeps canvod.readers \
  --cluster \
  --rmprefix canvod. \
  -o ../../dependency-graphs/canvod-readers-internal.svg

# Repeat for other packages...

# Cross-package view
uv run pydeps packages \
  --only canvod \
  -o dependency-graphs/cross-package.svg
```

---

## ✅ Current Status

**Working Now:**
- ✅ Package-level metrics (`just deps-report`)
- ✅ Simple dependency graph
- ✅ Independence analysis
- ✅ Mermaid diagrams in docs
- ✅ pydeps installed

**Next Steps (When You Need Deep Analysis):**
1. Ensure packages are importable: `uv sync`
2. Generate per-package graphs with pydeps
3. Add SVGs to documentation
4. Set up automatic generation in CI/CD

---

## 📚 Documentation

- **Quick Start:** This file
- **pydeps Details:** `PYDEPS_GUIDE.md`
- **Package Metrics:** `just deps-report`
- **Interactive Docs:** `just docs` → Dependencies section

---

**Summary:** You have both tools ready. Use `analyze_dependencies.py` for quick checks, `pydeps` for deep analysis and beautiful documentation graphs!
