# CANVODPY Architecture Diagrams

Exported architecture diagrams in PNG and SVG formats.

## 📊 Available Diagrams

### 1. Package Structure Overview
**Files:** `01-package-structure.png` / `01-package-structure.svg`  
High-level view of all canvodpy packages and their relationships.

![Package Structure](01-package-structure.png)

---

### 2. Data Processing Pipeline
**Files:** `02-processing-pipeline.png` / `02-processing-pipeline.svg`  
Complete data flow from RINEX ingestion to visualization output.

![Processing Pipeline](02-processing-pipeline.png)

---

### 3. Package Dependencies (Detailed)
**Files:** `03-dependencies.png` / `03-dependencies.svg`  
Layered architecture showing dependencies between packages.

![Dependencies](03-dependencies.png)

---

### 4. VOD Calculation Workflow
**Files:** `04-vod-workflow.png` / `04-vod-workflow.svg`  
Sequence diagram of VOD calculation from raw data to visualization.

![VOD Workflow](04-vod-workflow.png)

---

## 📁 File Formats

- **PNG**: High-resolution raster images (2400x1600px, transparent background)
- **SVG**: Vector graphics (scalable, perfect for documentation)
- **MMD**: Source Mermaid files (editable)

## 🎨 Rendering

These diagrams were generated using:
- **[@mermaid-js/mermaid-cli](https://github.com/mermaid-js/mermaid-cli)** v11.4.1
- **Transparent backgrounds** for easy embedding
- **High resolution** optimized for presentations and documentation

## 🔄 Regenerating

To regenerate all diagrams:

```bash
cd docs/diagrams
mmdc -i 01-package-structure.mmd -o 01-package-structure.png -w 2400 -H 1600 -b transparent
mmdc -i 01-package-structure.mmd -o 01-package-structure.svg -b transparent
# ... repeat for all diagrams
```

Or use the batch script:

```bash
for file in *.mmd; do
    base="${file%.mmd}"
    mmdc -i "$file" -o "${base}.png" -w 2400 -H 1600 -b transparent
    mmdc -i "$file" -o "${base}.svg" -b transparent
done
```

## 📖 Source

These diagrams are extracted from `../ARCHITECTURE_DIAGRAMS.md` which contains the full documentation with additional diagrams and explanations.

---

*Generated: 2026-02-02*
