# Modern Interactive Store Viewer Design

Research findings for building xarray/marimo-style interactive HTML representation for `MyIcechunkStore`.

---

## **Key Patterns from xarray**

### **Architecture**
```
Dataset._repr_html_() → formatting_html.dataset_repr()
                      ↓
├── Static files loaded once (SVG icons + CSS)
├── Collapsible sections (checkbox hack)
├── Grid-based layout (CSS Grid)
└── Unique IDs (uuid.uuid4()) for each expandable item
```

### **CSS Strategy**
- **CSS Variables** for theme compatibility:
  - `--xr-font-color0`, `--xr-font-color2`, `--xr-background-color`
  - Auto-detects Jupyter/VSCode/PyData themes
  - Explicit dark mode support: `body.vscode-dark`, `html[theme="dark"]`
  
- **Pure CSS interactivity** (no JavaScript!):
  - `<input type="checkbox">` + `<label>` for expand/collapse
  - CSS sibling selectors (`input:checked ~ .content { display: block; }`)
  - Grid layout for consistent spacing

### **HTML Structure**
```html
<div class="xr-wrap">
  <div class="xr-header">
    <div class="xr-obj-type">xarray.Dataset</div>
  </div>
  
  <!-- Each section is collapsible -->
  <input id="section-{uuid}" type="checkbox" checked />
  <label for="section-{uuid}">Dimensions (3)</label>
  <div class="xr-section-details">...</div>
  
  <!-- Variables as nested items -->
  <ul class="xr-var-list">
    <li class="xr-var-item">
      <div class="xr-var-name">temperature</div>
      <div class="xr-var-dims">(time, lat, lon)</div>
      <div class="xr-var-dtype">float64</div>
      <div class="xr-var-preview">...</div>
      
      <!-- Expandable data/attrs -->
      <input id="data-{uuid}" type="checkbox" />
      <label for="data-{uuid}">📊</label>
      <div class="xr-var-data">array([[...]])</div>
    </li>
  </ul>
</div>
```

### **Key Features**
1. **No JavaScript** - Pure CSS + HTML checkboxes
2. **SVG Icons** - Inline SVG sprites (`<use xlink:href="#icon-name">`)
3. **Grid Layout** - CSS Grid for perfect alignment
4. **Lazy Loading** - Static files loaded once via `@lru_cache`
5. **Nested Expansion** - Each variable can expand independently

---

## **Key Patterns from marimo**

### **Architecture**
```
mo.ui.table(data) → TableManager → React component (frontend)
                                 ↓
                    Sends columnar data via Arrow/JSON
                    Frontend handles sorting/filtering/pagination
```

### **Interactivity Model**
- **Backend:** Python `UIElement` subclass
- **Frontend:** React component receives data + config
- **Communication:** Uses `marimo._output.mime.MIME` for rendering
- **Data format:** Apache Arrow (efficient columnar format)

### **Features**
```python
mo.ui.table(
    data=df,
    pagination=True,        # Client-side pagination
    selection="multi",      # Row selection
    page_size=10,          # Rows per page
    show_column_summaries=True,  # Stats on hover
    frozen_columns=["id"]  # Pin columns
)
```

### **What Makes It "Modern"**
1. **Reactive** - Selecting rows updates Python state
2. **Performant** - Uses Arrow for large datasets
3. **Rich UI** - Sorting, filtering, search built-in
4. **Integrated** - Can chain with other `mo.ui.*` components

### **Limitation for Our Use Case**
⚠️ **Requires marimo runtime** - Can't use `mo.ui.table()` in plain Jupyter/VSCode
- marimo UI elements need the marimo kernel running
- Won't work in standard IPython/Jupyter notebooks

---

## **Design for IcechunkStore Viewer**

### **Goals**
1. ✅ **Tree structure** showing branches → groups hierarchy
2. ✅ **Expandable sections** like xarray (pure CSS)
3. ✅ **Embedded content** when expanding:
   - Metadata group → Display as Polars DataFrame HTML repr
   - Data group → Display as xarray Dataset HTML repr
4. ✅ **Marimo compatibility** (when available)
5. ✅ **Modern aesthetic** matching xarray's style

---

## **Proposed Architecture**

### **Three-Level Hierarchy**
```
MyIcechunkStore
├── 🌿 Branch: main
│   ├── 📁 Group: canopy_01
│   │   ├── 📊 Dataset (xarray)     ← Lazy load on expand
│   │   └── 📋 metadata/table       ← Lazy load on expand
│   └── 📁 Group: canopy_02
│       └── ...
└── 🌿 Branch: experiment_v2
    └── ...
```

### **HTML Structure Pattern**
```html
<div class="icechunk-store">
  <div class="store-header">
    <div class="store-title">🛰️ RINEX IceChunk Store</div>
    <div class="store-stats">3 branches • 12 groups • 1.2M obs</div>
  </div>
  
  <!-- Branch level -->
  <input id="branch-{uuid}" type="checkbox" checked />
  <label for="branch-{uuid}" class="branch-label">
    🌿 <strong>main</strong> <span class="count">(4 groups)</span>
  </label>
  
  <div class="branch-content">
    <!-- Group level -->
    <input id="group-{uuid}" type="checkbox" />
    <label for="group-{uuid}" class="group-label">
      📁 <strong>canopy_01</strong> 
      <span class="dims">epoch: 86400, sid: 120</span>
    </label>
    
    <div class="group-content">
      <!-- Embedded xarray Dataset HTML -->
      <div class="embedded-dataset">
        {dataset._repr_html_()}
      </div>
      
      <!-- Embedded Polars metadata table -->
      <div class="embedded-metadata">
        <h4>Metadata Table</h4>
        {metadata_df._repr_html_()}
      </div>
    </div>
  </div>
</div>
```

### **CSS Strategy**
1. **Inherit xarray variables** for consistency:
   ```css
   .icechunk-store {
     --store-bg: var(--xr-background-color, white);
     --store-border: var(--xr-border-color, #ddd);
     --store-text: var(--xr-font-color0, black);
   }
   ```

2. **Use CSS Grid** for alignment
3. **Pure checkbox expansion** (no JS)
4. **Smooth transitions** for modern feel
5. **Dark mode** via xarray variables

---

## **Implementation Strategy**

### **Phase 1: Structure (Pure HTML/CSS)**
```python
def _repr_html_(self) -> str:
    # Use xarray's pattern
    from xarray.core.formatting_html import _load_static_files
    
    # Load xarray's CSS/icons (for consistency)
    icons, xr_css = _load_static_files()
    
    # Add our custom CSS on top
    custom_css = self._get_store_css()
    
    # Build tree
    branches_html = self._build_branches_tree()
    
    return f"""
    {icons}
    <style>{xr_css}</style>
    <style>{custom_css}</style>
    <div class="icechunk-store">
      {branches_html}
    </div>
    """
```

### **Phase 2: Lazy Content Loading**
```python
def _build_group_section(self, branch, group_name):
    """Generate HTML for a single group (collapsed by default)."""
    group_id = f"group-{uuid.uuid4()}"
    
    # Don't load data until expanded
    # Instead, use data-* attributes for lazy loading
    return f"""
    <input id="{group_id}" type="checkbox" 
           data-branch="{branch}" 
           data-group="{group_name}" />
    <label for="{group_id}">📁 {group_name}</label>
    <div class="group-content">
      {self._render_group_content(branch, group_name)}
    </div>
    """

def _render_group_content(self, branch, group_name):
    """Render xarray Dataset + metadata table."""
    try:
        # Load actual data
        ds = self.read_group(group_name, branch=branch)
        metadata_df = self.load_metadata_as_polars(group_name, branch=branch)
        
        # Use native HTML reprs
        return f"""
        <div class="dataset-section">
          <h4>📊 Dataset</h4>
          {ds._repr_html_()}
        </div>
        <div class="metadata-section">
          <h4>📋 Metadata Table</h4>
          {metadata_df._repr_html_()}
        </div>
        """
    except Exception as e:
        return f'<div class="error">{e}</div>'
```

### **Phase 3: Marimo Integration (Optional)**
```python
def to_marimo_table(self, group_name, branch="main"):
    """Convert metadata to marimo interactive table."""
    try:
        import marimo as mo
    except ImportError:
        print("⚠️ marimo not available")
        return None
    
    metadata_df = self.load_metadata_as_polars(group_name, branch)
    return mo.ui.table(
        data=metadata_df,
        pagination=True,
        page_size=50,
        show_column_summaries=True,
    )

# In marimo notebook:
# store.to_marimo_table("canopy_01")
```

---

## **Visual Design Mockup**

```
╔══════════════════════════════════════════════════════════════╗
║ 🛰️ RINEX IceChunk Store                                     ║
║ /data/gnss/rinex_store                                       ║
║ 📊 3 branches • 📍 12 sites • 📡 1,234,567 observations     ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║ ▼ 🌿 main (4 groups)                                        ║
║   ├─ ▶ 📁 canopy_01  epoch: 86400, sid: 120                ║
║   ├─ ▼ 📁 canopy_02  epoch: 86400, sid: 120                ║
║   │     ╔════════════════════════════════════════════╗      ║
║   │     ║ 📊 Dataset                                ║      ║
║   │     ╠════════════════════════════════════════════╣      ║
║   │     ║ Dimensions:  epoch: 86400, sid: 120      ║      ║
║   │     ║ Coordinates: * epoch (86400) datetime64  ║      ║
║   │     ║              * sid (120) int64           ║      ║
║   │     ║ Data vars:   SNR (86400, 120) float32    ║      ║
║   │     ║              phi (86400, 120) float32    ║      ║
║   │     ╚════════════════════════════════════════════╝      ║
║   │     ╔════════════════════════════════════════════╗      ║
║   │     ║ 📋 Metadata Table (24 rows × 8 columns)  ║      ║
║   │     ╠════════════════════════════════════════════╣      ║
║   │     ║ rinex_hash │ start      │ end        │...║      ║
║   │     ║ abc123     │ 2024-01-01 │ 2024-01-02 │...║      ║
║   │     ║ def456     │ 2024-01-02 │ 2024-01-03 │...║      ║
║   │     ╚════════════════════════════════════════════╝      ║
║   ├─ ▶ 📁 vienna_01  epoch: 86400, sid: 130                ║
║   └─ ▶ 📁 vienna_02  epoch: 86400, sid: 130                ║
║                                                              ║
║ ▶ 🌿 experiment_v2 (2 groups)                               ║
║ ▶ 🌿 rechunked_temp (4 groups)                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## **Key Improvements Over Current Implementation**

| Feature | Current | Proposed |
|---------|---------|----------|
| **Layout** | Linear tree | Hierarchical collapsible |
| **Content** | Static text tree | Embedded xarray/polars HTML |
| **Expansion** | All expanded | Collapsed by default |
| **Styling** | Custom gradients | xarray-compatible variables |
| **Dark mode** | Partial | Full via xarray CSS vars |
| **Alignment** | Flexbox | CSS Grid (better) |
| **Icons** | Emoji only | SVG icons + emoji |
| **Performance** | Loads all data | Lazy load on expand |
| **Integration** | Standalone | Works with xarray ecosystem |

---

## **Next Steps**

1. **Review** this design with you
2. **Refactor** `viewer.py` to use xarray patterns
3. **Add** lazy loading for group content
4. **Test** in Jupyter/VSCode/marimo notebooks
5. **Polish** CSS for modern aesthetic

**Question:** Should we proceed with this design? Any preferences on styling or features?
