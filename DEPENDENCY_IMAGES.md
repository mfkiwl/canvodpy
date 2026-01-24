# Dependency Graph Images

## ✅ Your Images Are Ready!

**Location:** `/Users/work/Developer/GNSS/canvodpy/`

- `dependency-graph.png` - High-resolution image (28KB)
- `dependency-graph.svg` - Vector format (6KB)
- `dependency-graph.pdf` - Print quality (19KB)

---

## 🎨 What You See

Your dependency graph shows:

**Foundation Packages** (Green):
- `canvod-readers` (I=0.00) - Most stable
- `canvod-grids` (I=0.00) - Most stable
- `canvod-vod` (I=0.00) - Independent
- `canvod-utils` (I=0.00) - Independent

**Consumer Packages** (Pink):
- `canvod-aux` (I=1.00) → depends on canvod-readers
- `canvod-viz` (I=1.00) → depends on canvod-grids
- `canvod-store` (I=1.00) → depends on canvod-grids

**Legend:**
- **I = Instability** (0.00 = stable/foundation, 1.00 = unstable/leaf)
- **Green** = Stable foundation packages
- **Pink** = Leaf packages (consumers)

---

## 🚀 Regenerate Anytime

```bash
# Simple - generates PNG, SVG, PDF and opens PNG
just deps

# Or manually:
python3 scripts/analyze_dependencies.py --format dot > dependency-graph.dot
dot -Tpng dependency-graph.dot -o dependency-graph.png
dot -Tsvg dependency-graph.dot -o dependency-graph.svg  
dot -Tpdf dependency-graph.dot -o dependency-graph.pdf
```

---

## 📊 Your Architecture Summary

```
✅ No circular dependencies
✅ Maximum dependency depth: 1
✅ 4 foundation packages (0 dependencies)
✅ 3 consumer packages (1 dependency each)
✅ Total internal dependencies: 3

Result: EXCELLENT architecture! 🟢
```

---

## 📁 Using in Documentation

**PNG** - Use in READMEs, presentations:
```markdown
![Dependency Graph](dependency-graph.png)
```

**SVG** - Use in web documentation (scales perfectly):
```html
<img src="dependency-graph.svg" alt="Dependency Graph">
```

**PDF** - Use in papers, reports (print quality)

---

**Generated:** January 24, 2026
**Command:** `just deps`
