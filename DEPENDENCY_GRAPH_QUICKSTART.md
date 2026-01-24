# Dependency Graph - Quick Start

## 🚀 View Your Dependency Graph

### 1. In Documentation (Interactive Mermaid)

```bash
cd /Users/work/Developer/GNSS/canvodpy
just docs
# Or: uv run myst
```

Then navigate to: **Documentation > Package Dependencies**

You'll see:
- Interactive Mermaid diagram (click nodes!)
- Metrics table
- Architecture analysis
- Recommendations

---

### 2. Command Line Report

```bash
# Full metrics report
python3 scripts/analyze_dependencies.py --format report

# Just the Mermaid diagram
python3 scripts/analyze_dependencies.py --format mermaid

# Graphviz DOT format
python3 scripts/analyze_dependencies.py --format dot
```

---

### 3. Using Just Commands

```bash
# Show dependency report
just deps-report

# Generate Mermaid graph
just deps-graph

# Generate complete analysis
just deps-all

# Update documentation
just deps-update
```

---

## 📊 Your Current Architecture Summary

```
✅ No circular dependencies
✅ 4 packages with ZERO dependencies (57%)
✅ Only 3 total internal dependencies
✅ Maximum dependency depth: 1

Foundation (0 deps):          Consumers (1 dep):
  canvod-readers ────────────→ canvod-aux
  canvod-grids ──────────────→ canvod-viz
  canvod-grids ──────────────→ canvod-store
  canvod-vod
  canvod-utils
```

**Result: Excellent architecture! 🟢**

---

## 🎯 How to Increase Independence

Your packages are already highly independent! But if you want to improve further:

### Option 1: Make canvod-utils a Shared Dependency

Currently unused. Consider having other packages use it for:
- Configuration (`canvod.utils.config`)
- Metadata (`canvod.utils._meta`)
- Shared constants

**Impact:** Small increase in coupling, large reduction in duplication

### Option 2: Extract Shared Code

If you find the same code in multiple packages:
1. Move it to `canvod-utils`
2. Import from there
3. Run `just deps-report` to verify

### Option 3: Monitor as You Grow

```bash
# Run this regularly
python3 scripts/analyze_dependencies.py --format report

# Check for:
# - Circular dependencies (should stay 0)
# - Packages with >2 dependencies
# - Dependency chains >2 levels deep
```

---

## 📁 Files Created

```
scripts/
  └── analyze_dependencies.py      # Analysis script

docs/
  └── dependencies.md               # Documentation page

justfile                             # Added deps-* commands

DEPENDENCY_GRAPH_COMPLETE.md         # This summary
```

---

## 🔗 Links

- **Documentation:** http://localhost:3000/docs/dependencies (when docs running)
- **Analysis Script:** `scripts/analyze_dependencies.py`
- **Just Commands:** `just --list` (look for deps-*)

---

**Your dependency architecture is excellent! Keep it that way! 🎉**
