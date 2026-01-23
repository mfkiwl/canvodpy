# MyST Documentation Architecture Strategy

## 🎯 Your Questions Answered

### Q1: Can packages have independent docs that get combined at the root?
**Yes!** MyST supports two architectural patterns:

#### Pattern A: Independent Package Docs (Recommended)
```
packages/canvod-aux/
├── myst.yml          # Builds standalone site
├── docs/             # Package-specific docs
└── justfile          # just docs-build, just docs-serve

Root:
├── myst.yml          # Links to package docs
└── docs/             # Root-level overview docs
```

**Benefits:**
- ✅ Each package can build/serve docs independently
- ✅ Packages can be extracted to separate repos easily
- ✅ CI/CD builds docs per package
- ✅ Root combines all via links/references

#### Pattern B: Monolithic Combined Docs
```
Root myst.yml includes ALL package content
```

**Benefits:**
- ✅ Single build command
- ✅ Unified search
- ✅ Easier cross-references

**We recommend Pattern A** for your monorepo architecture.

---

### Q2: Can styling be centralized?
**Yes!** Three approaches:

#### Approach 1: Shared Remote Config (Current)
```yaml
# All myst.yml files
extends:
  - https://github.com/TUW-GEO/cookiecutter-docs-config/raw/main/myst.yml
```
✅ Single source of truth  
✅ Update once, applies everywhere  
⚠️ Requires network access  

#### Approach 2: Local Shared Config File
```yaml
# All package myst.yml files
extends:
  - ../../docs/myst-base-config.yml
```
✅ No network dependency  
✅ Version controlled  
⚠️ Need to maintain sync  

#### Approach 3: CSS Variables (Recommended for custom styling)
```yaml
# Root myst.yml
site:
  options:
    style: docs/assets/canvod-style.css

# Package myst.yml
site:
  options:
    style: ../../docs/assets/canvod-style.css
```
✅ Centralized CSS  
✅ Easy to customize  

---

## 🏗️ Proposed Architecture

### Current State
```
✅ Root myst.yml + docs/
✅ canvod-aux: myst.yml + docs/
✅ canvod-readers: myst.yml + docs/
✅ canvod-grids: myst.yml + docs/
✅ canvod-viz: myst.yml + docs/
✅ canvod-vod: myst.yml + docs/
❌ canvod-store: MISSING
❌ canvod-utils: MISSING
```

### Target State (All Packages with Independent Docs)

```
canvodpy/
├── myst.yml                          # Root: combines all packages
├── docs/
│   ├── assets/
│   │   └── canvod-style.css         # Centralized styling
│   ├── index.md
│   └── ...
│
├── justfile                          # Root commands
│   ├── docs-build                   # Build root docs
│   ├── docs-build-all              # Build all package docs + root
│   ├── docs-serve                   # Serve root docs
│   └── docs-clean                   # Clean all builds
│
└── packages/
    ├── canvod-aux/
    │   ├── myst.yml                 # Independent build
    │   ├── docs/
    │   └── justfile                # Package-specific commands
    ├── canvod-readers/
    │   ├── myst.yml
    │   ├── docs/
    │   └── justfile
    ├── canvod-store/                # NEW
    │   ├── myst.yml
    │   ├── docs/
    │   └── justfile
    ├── canvod-utils/                # NEW
    │   ├── myst.yml
    │   ├── docs/
    │   └── justfile
    └── ...
```

---

## 🎨 Centralized Styling Strategy

### 1. Single CSS File (Recommended)
```
docs/assets/canvod-style.css   # Master style file

All myst.yml files reference this via relative path:
- Root:     docs/assets/canvod-style.css
- Packages: ../../docs/assets/canvod-style.css
```

### 2. CSS Variables for Theming
```css
/* docs/assets/canvod-style.css */
:root {
  --canvod-primary: #003366;
  --canvod-secondary: #66ccff;
  --canvod-accent: #ff6600;
  --font-family-base: 'Inter', sans-serif;
  --font-family-mono: 'JetBrains Mono', monospace;
}
```

### 3. TUW-GEO Base + Custom Overrides
```yaml
# All myst.yml files
extends:
  - https://github.com/TUW-GEO/cookiecutter-docs-config/raw/main/myst.yml

site:
  options:
    style: ../../docs/assets/canvod-style.css  # Custom overrides
```

---

## 📦 Package Documentation Template

### Standard Structure for Each Package
```
packages/<package-name>/
├── myst.yml
├── docs/
│   ├── index.md              # Package home
│   ├── installation.md       # How to install
│   ├── quickstart.md         # Quick start guide
│   ├── guide/                # User guides
│   │   ├── basic.md
│   │   └── advanced.md
│   ├── api/                  # API reference
│   │   └── reference.md
│   └── changelog.md          # Change log
└── justfile
    ├── docs-build
    ├── docs-serve
    └── docs-clean
```

---

## 🚀 Build Strategy

### Independent Builds (Each Package)
```bash
cd packages/canvod-aux
just docs-build              # Build this package only
just docs-serve              # Serve this package only
```

### Combined Build (Root)
```bash
cd /path/to/canvodpy
just docs-build              # Build root docs
just docs-build-all          # Build ALL packages + root
just docs-serve              # Serve complete site
```

### CI/CD Strategy
```yaml
# .github/workflows/docs.yml
jobs:
  build-package-docs:
    strategy:
      matrix:
        package: [canvod-aux, canvod-readers, ...]
    steps:
      - run: cd packages/${{ matrix.package }} && just docs-build
  
  build-root-docs:
    needs: build-package-docs
    steps:
      - run: just docs-build-all
```

---

## 🔗 Cross-Package References

### Option 1: Intersphinx-style Links
```markdown
# In canvod-aux docs
See [RINEX Reader](../../canvod-readers/docs/guide/rinex.md)
```

### Option 2: Root TOC with Deep Links
```yaml
# Root myst.yml
project:
  toc:
    - title: canvod-aux
      children:
        - file: packages/canvod-aux/docs/index.md
        - file: packages/canvod-aux/docs/preprocessing.md
```

---

## 📊 Pros & Cons

### Independent Package Docs

**Pros:**
- ✅ True modularity (Sollbruchstellen!)
- ✅ Packages can be extracted easily
- ✅ Parallel development
- ✅ Package-specific versioning
- ✅ Faster individual builds

**Cons:**
- ⚠️ More build commands
- ⚠️ Need to maintain consistency
- ⚠️ Cross-package links slightly complex

### Combined Monolithic Docs

**Pros:**
- ✅ Single build command
- ✅ Unified search
- ✅ Easier cross-references
- ✅ Single site

**Cons:**
- ❌ Slower builds (rebuild everything)
- ❌ Harder to extract packages
- ❌ All-or-nothing approach
- ❌ Violates Sollbruchstellen principle

---

## ✅ Recommended Approach

### Architecture: **Independent Package Docs + Root Aggregator**

```
1. Each package has complete standalone docs
2. Root myst.yml references package docs
3. Centralized styling via shared CSS
4. Just commands at both levels
```

### Styling: **Remote Base Config + Local CSS Overrides**

```yaml
extends:
  - https://github.com/TUW-GEO/cookiecutter-docs-config/raw/main/myst.yml

site:
  options:
    style: ../../docs/assets/canvod-style.css
```

---

## 🎯 Implementation Checklist

### Phase 1: Complete Missing Packages
- [ ] Create canvod-store/myst.yml + docs/
- [ ] Create canvod-utils/myst.yml + docs/
- [ ] Add Just commands to all packages

### Phase 2: Standardize Structure
- [ ] Ensure all packages follow same docs/ structure
- [ ] Centralize CSS styling
- [ ] Update all myst.yml to reference shared style

### Phase 3: Root Integration
- [ ] Update root myst.yml to link package docs
- [ ] Add just docs-build-all command
- [ ] Test cross-package navigation

### Phase 4: Documentation
- [ ] Document build process
- [ ] Add CONTRIBUTING section for docs
- [ ] Create docs style guide

---

## 📝 Next Steps

1. **Review this strategy** - Confirm it matches your vision
2. **Implement missing packages** - Create canvod-store & canvod-utils docs
3. **Standardize styling** - Centralize CSS
4. **Add Just commands** - Make docs easy to build
5. **Test workflow** - Ensure everything builds correctly

---

**Ready to implement?**
