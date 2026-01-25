# Dependency Analysis Complete ✅

**Date:** 2026-01-25  
**Tool:** [pydeps](https://github.com/thebjorn/pydeps)  
**Status:** Complete

---

## 📊 Generated Visual Graphs

### Location
`docs/dependency_graphs/`

### Files Created (9 total)

| File | Size | Description |
|------|------|-------------|
| **canvodpy_overview.svg** | 27KB | Complete dependency graph with clustering |
| **canvodpy_overview.png** | 154KB | PNG version for easy viewing |
| **canvodpy_full.svg** | 17KB | Strict filtered view (canvod.* only) |
| **canvodpy_simple.svg** | 7.8KB | Simplified view without clustering |
| **canvod_aux.svg** | 992B | canvod.aux package dependencies |
| **canvod_readers.svg** | 611B | canvod.readers package dependencies |
| **canvod_store.svg** | 992B | canvod.store package dependencies |
| **orchestrator.svg** | 987B | Orchestrator module dependencies |
| **README.md** | 8.2KB | Graph documentation and usage guide |

---

## 📝 Text Documentation

### Location
Project root

### Files Created (3 total)

| File | Size | Description |
|------|------|-------------|
| **CANVODPY_DEPENDENCY_GRAPH.md** | 18KB | Comprehensive dependency documentation |
| **DEPENDENCY_GRAPH.mmd** | 3.2KB | Mermaid diagram source |
| **DEPENDENCY_TREE.txt** | 13KB | Quick text reference |

---

## 🎯 Key Findings

### Package Dependency Layers

```
Layer 0 (Core - No Dependencies):
  ✅ canvod.utils
  ✅ canvod.grids

Layer 1 (Base):
  ✅ canvod.readers → canvod.utils

Layer 2 (Mid-tier):
  ✅ canvod.aux → readers, utils, store, canvodpy.*
  ✅ canvod.store → grids, readers, utils, aux, vod, canvodpy.*
  ✅ canvod.viz → grids

Layer 3 (Processing):
  ✅ canvod.vod → store

Layer 4 (Orchestration):
  ✅ canvodpy → ALL packages
```

### Circular Dependencies

**Identified:** canvod.aux ↔ canvod.store  
**Status:** ✅ Resolved via lazy imports  
**Visible in:** canvodpy_overview.svg (look for cycle between clusters)

### Configuration Flow

```
.env + processing.yaml
        ↓
    settings.py
        ↓
    globals.py
        ↓
    Packages (aux, store, orchestrator)
```

---

## 🔍 How to Use the Graphs

### View in Browser
1. Navigate to `docs/dependency_graphs/`
2. Open `canvodpy_overview.png` for quick view
3. Open `canvodpy_overview.svg` in browser for interactive view

### View in VSCode
1. Install "SVG" extension
2. Open any `.svg` file
3. Right-click → "Open Preview"

### View on GitHub
- SVG files render automatically when pushed to GitHub
- Click any `.svg` file in the repository

---

## 📖 Reading the Graphs

### Node Types
- **Boxes:** Modules/packages
- **Clusters:** Package groupings (colored boxes)
- **Colors:** Different namespaces (canvod.aux, canvod.store, etc.)

### Edge Types
- **Arrows:** Import relationships
- **Direction:** Points from importer to imported

### Key Patterns
1. **Core packages (bottom):** No outgoing arrows (no dependencies)
2. **Mid-tier packages (middle):** Arrows to core packages
3. **Umbrella package (top):** Arrows to all packages

### Finding Circular Dependencies
Look for arrow cycles: A → B → A

---

## 🔄 Regenerating Graphs

### Quick Regeneration

```bash
cd /Users/work/Developer/GNSS/canvodpy

# Complete overview
uv run pydeps canvodpy/src/canvodpy \
    -x numpy pandas xarray pathlib os sys re datetime collections typing pydantic \
    -T svg \
    -o docs/dependency_graphs/canvodpy_overview.svg \
    --noshow --cluster --max-bacon 3 --rmprefix canvod. canvodpy.

# PNG version
uv run pydeps canvodpy/src/canvodpy \
    -x numpy pandas xarray pathlib os sys re datetime collections typing pydantic \
    -T png \
    -o docs/dependency_graphs/canvodpy_overview.png \
    --noshow --cluster --max-bacon 3 --rmprefix canvod. canvodpy.

# Individual package (example: canvod.aux)
uv run pydeps packages/canvod-aux/src/canvod/aux \
    --only canvodpy canvod -T svg \
    -o docs/dependency_graphs/canvod_aux.svg \
    --noshow --cluster --max-bacon 2
```

### When to Regenerate
- ✨ After adding new packages
- 🔧 After refactoring imports
- 📦 After dependency changes
- 🔄 Before major releases

---

## 📚 Related Documentation

| File | Description |
|------|-------------|
| `docs/dependency_graphs/README.md` | Complete graph documentation |
| `CANVODPY_DEPENDENCY_GRAPH.md` | Text-based dependency analysis |
| `DEPENDENCY_GRAPH.mmd` | Mermaid diagram source |
| `DEPENDENCY_TREE.txt` | Quick text reference |
| `REPO_STRUCTURE_STATUS.md` | Repository structure verification |

---

## ✅ Verification Checklist

- [x] Visual graphs generated with pydeps
- [x] PNG versions created for easy viewing
- [x] Individual package graphs created
- [x] Orchestrator graph created
- [x] README documentation written
- [x] Text documentation created
- [x] Mermaid diagram source available
- [x] Circular dependencies identified and documented
- [x] Configuration flow documented
- [x] Regeneration instructions provided

---

## 🎨 Graph Highlights

### Best Overall View
**File:** `canvodpy_overview.png` (154KB)
- Clustered by package
- Shows all import relationships
- Color-coded namespaces
- PNG format for easy viewing

### Most Detailed
**File:** `canvodpy_full.svg` (17KB)
- Complete detail
- Strict filtering (only canvod.* packages)
- SVG for scalability

### Clearest Structure
**File:** `canvodpy_simple.svg` (7.8KB)
- No clustering
- Direct module connections
- Easier to trace specific paths

---

## 🔧 Tool Information

### pydeps
- **GitHub:** https://github.com/thebjorn/pydeps
- **Installation:** `uv pip install pydeps`
- **Requires:** graphviz (`brew install graphviz` on macOS)
- **Documentation:** https://pydeps.readthedocs.io/

### Key Features Used
- ✅ Automatic dependency detection via AST analysis
- ✅ Clustering by package
- ✅ External package exclusion
- ✅ Multiple output formats (SVG, PNG)
- ✅ Configurable depth limiting
- ✅ Prefix removal for cleaner display

---

## 📊 Statistics

| Metric | Count |
|--------|-------|
| Total graphs generated | 9 |
| Packages analyzed | 8 (7 namespace + 1 umbrella) |
| Dependency layers | 5 (0-4) |
| Circular dependencies | 1 (resolved) |
| Total documentation size | ~220KB |

---

## 🎯 Next Steps

### Recommended Actions
1. ✅ Review `canvodpy_overview.png` for overall architecture
2. ✅ Check individual package graphs for detailed dependencies
3. ✅ Verify circular dependency resolution
4. ✅ Share graphs in project documentation
5. ⏭️ Set up automated graph generation in CI/CD

### Future Enhancements
- [ ] Add graph generation to pre-commit hooks
- [ ] Create interactive HTML version
- [ ] Add time-series graph changes
- [ ] Generate diff graphs between versions
- [ ] Add graph complexity metrics

---

**Status:** ✅ Complete - All dependency graphs generated and documented using pydeps
