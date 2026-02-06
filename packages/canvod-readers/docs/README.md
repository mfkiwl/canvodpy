# Documentation for canvod-readers

This directory contains the complete MyST/Sphinx documentation for canvod-readers.

## Documentation Structure

```
docs/
├── Makefile              # Build commands
├── source/               # Source documentation files
│   ├── conf.py          # Sphinx configuration
│   ├── index.md         # Main documentation hub
│   ├── overview.md      # Detailed introduction
│   ├── architecture.md  # ABC pattern & design
│   ├── rinex_reader.md  # RINEX v3.04 implementation (678 lines)
│   ├── pydantic_guide.md  # Comprehensive Pydantic tutorial (775 lines)
│   ├── testing.md       # Testing guide (561 lines)
│   ├── extending_readers.md  # Adding new readers (693 lines)
│   └── api_reference.md # API documentation
└── build/               # Generated HTML (gitignored)
    └── *.html
```

## Building Documentation

### Prerequisites

Documentation dependencies are already installed in the virtual environment:
- sphinx
- myst-parser (MyST Markdown support)
- sphinx-design (cards, grids, tabs)
- furo (clean, modern theme)
- linkify-it-py (auto-link URLs)

### Build Commands

**Build HTML:**
```bash
cd docs
make html
```

**View in browser (macOS):**
```bash
make serve
```

**Or manually:**
```bash
open build/index.html
```

**Clean build:**
```bash
make clean
make html
```

**Alternative (without Makefile):**
```bash
cd docs
../.venv/bin/sphinx-build -b html source build
```

## Documentation Features

### MyST Markdown Syntax

All documentation uses MyST (Markedly Structured Text):

**Directives:**
```markdown
:::{note}
This is a note
:::

:::{warning}
This is a warning
:::
```

**Code blocks with syntax highlighting:**
```markdown
​```python
from canvod.readers import Rnxv3Obs
reader = Rnxv3Obs(fpath="file.24o")
​```
```

**Grids and cards:**
```markdown
::::{grid} 2
:::{grid-item-card} Title
Content
:::
::::
```

### Mermaid Diagrams

Documentation includes 15+ Mermaid diagrams:

```markdown
​```{mermaid}
graph LR
    A[Input] --> B[Process]
    B --> C[Output]
​```
```

Diagrams cover:
- Architecture layers
- Data flow
- Component interactions
- Class hierarchies
- Parsing pipelines

### Cross-References

Internal links between pages:
```markdown
See the [Architecture Guide](architecture.md) for details.
Next: Learn about [Testing](testing.md).
```

## Documentation Content

### 1. index.md - Main Hub
- Quick start guide
- Core concepts (Signal IDs, Dataset structure)
- Installation instructions
- canVODpy ecosystem overview

### 2. overview.md - Detailed Introduction
- Problem statement & solution
- Design philosophy (3 principles)
- Use cases (4 detailed examples)
- Performance characteristics
- Comparison with other tools

### 3. architecture.md - ABC Pattern
- Why use Abstract Base Classes?
- Complete GNSSDataReader interface
- Layered architecture (5 layers)
- Design principles
- DatasetStructureValidator
- ReaderFactory pattern

### 4. rinex_reader.md - Implementation (678 lines)
- RINEX format overview
- Class hierarchy
- Complete parsing pipeline
- Pydantic models in detail
- Signal ID creation
- Performance optimizations
- Error handling

### 5. pydantic_guide.md - Comprehensive Tutorial (775 lines)
**Most detailed section as requested**
- Why Pydantic? (before/after comparison)
- 6 core concepts
- 3 complete real-world examples
- Advanced patterns (computed fields, factories)
- Error handling
- 5 best practices
- Debugging & performance

### 6. testing.md - Testing Guide (561 lines)
- Test structure
- 4 test categories
- Test fixtures
- Coverage reports
- Best practices
- CI/CD integration

### 7. extending_readers.md - Adding Readers (693 lines)
- Step-by-step guide
- Complete RINEX v2 example
- Validation requirements
- Testing checklist
- Common pitfalls

### 8. api_reference.md - API Documentation
- Auto-generated from docstrings
- All modules, classes, functions
- NumPy-style docstrings

## Theme: Furo

Documentation uses the **Furo** theme:
- Clean, modern design
- Light/dark mode support
- Mobile-friendly
- Fast and accessible
- Good code highlighting

Color scheme:
- Light mode: Blue (#0066cc)
- Dark mode: Light blue (#3399ff)

## Statistics

- **8 documentation files**
- **4,500+ lines of content**
- **15+ Mermaid diagrams**
- **80+ code examples**
- **5+ complete tutorials**

## Viewing Documentation

After building, open in browser:
```bash
open build/index.html
```

Or use Python's built-in server:
```bash
cd build
python -m http.server 8000
# Open http://localhost:8000
```

## Updating Documentation

1. Edit markdown files in `source/`
2. Rebuild with `make html`
3. Refresh browser

Changes are reflected immediately after rebuild.

## Publishing Documentation

### GitHub Pages

Add to `.github/workflows/docs.yml`:
```yaml
name: Documentation

on:
  push:
    branches: [main]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build docs
        run: |
          pip install sphinx myst-parser sphinx-design furo linkify-it-py
          cd docs
          make html
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/build
```

### Read the Docs

1. Create account at readthedocs.org
2. Import repository
3. Build automatically on push

Configuration in `.readthedocs.yml`:
```yaml
version: 2

build:
  os: ubuntu-22.04
  tools:
    python: "3.10"

sphinx:
  configuration: docs/source/conf.py

python:
  install:
    - requirements: docs/requirements.txt
```

## Troubleshooting

**Import errors during autodoc:**
- Install package: `pip install -e .`
- Check sys.path in conf.py

**Mermaid diagrams not rendering:**
- Check `myst_enable_extensions` includes necessary extensions
- Verify MyST parser version

**Missing modules:**
- Install documentation dependencies:
  ```bash
  pip install sphinx myst-parser sphinx-design furo linkify-it-py
  ```

**Build warnings:**
- Most autodoc warnings are normal
- Fix broken cross-references
- Check markdown syntax

## Help

For Sphinx help:
- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [MyST Parser](https://myst-parser.readthedocs.io/)
- [Sphinx Design](https://sphinx-design.readthedocs.io/)
- [Furo Theme](https://pradyunsg.me/furo/)

## Summary

✅ Complete MyST documentation with Sphinx
✅ 8 comprehensive guides
✅ 15+ Mermaid diagrams
✅ 80+ code examples
✅ Modern Furo theme
✅ Ready for deployment

Built documentation is in `build/index.html`
