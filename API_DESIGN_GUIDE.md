# 🎨 Modern Python API Design for canvodpy

**Purpose:** Design a clean, Pythonic public API that wraps gnssvodpy's proven logic  
**Date:** 2025-01-21

---

## 🎯 API Design Principles

### The Three Levels of API Design

Modern scientific Python packages follow a **progressive disclosure** pattern:

```
Level 1: Simple functions    ← 80% of users, 1-2 lines
Level 2: Object-oriented     ← 15% of users, more control
Level 3: Low-level internals ← 5% of users, full control
```

**Examples from popular packages:**

```python
# pandas - Three levels
df = pd.read_csv("data.csv")                    # Level 1: Simple
df = pd.DataFrame(data, columns=cols)           # Level 2: More control
df = pd.core.frame.DataFrame(...)               # Level 3: Internals

# requests - Three levels
r = requests.get(url)                           # Level 1: Simple
s = requests.Session(); r = s.get(url)          # Level 2: Sessions
r = requests.adapters.HTTPAdapter(...)          # Level 3: Internals

# xarray - Three levels
ds = xr.open_dataset("data.nc")                 # Level 1: Simple
ds = xr.Dataset(data_vars, coords)              # Level 2: Manual
ds = xr.backends.NetCDF4DataStore(...)          # Level 3: Internals
```

---

## 🏗️ Proposed canvodpy API

### Level 1: Simple Functions (Most Users)

**80% of users want this - make it dead simple:**

```python
from canvodpy import process_date, calculate_vod, visualize

# Process one day of RINEX data
data = process_date(
    site="Rosalia",
    date="2025001"
)
# Returns: dict[str, xr.Dataset] with all receivers

# Calculate VOD
vod = calculate_vod(
    site="Rosalia",
    canopy="canopy_01",
    reference="reference_01", 
    date="2025001"
)
# Returns: xr.Dataset with VOD values

# Visualize
fig = visualize.hemisphere_2d(vod, title="VOD 2025-01-01")
fig.savefig("vod.png")
```

**Why this works:**
- ✅ No classes to instantiate
- ✅ Self-documenting parameter names
- ✅ Sensible defaults
- ✅ One function = one task
- ✅ Similar to pandas/xarray patterns

---

### Level 2: Object-Oriented (Power Users)

**15% of users need more control:**

```python
from canvodpy import Site, Pipeline

# Create site (loads config, initializes stores)
site = Site("Rosalia")

# Inspect configuration
print(site.receivers)        # List all receivers
print(site.active_receivers) # Only active ones
print(site.vod_analyses)     # Configured VOD pairs

# Create pipeline
pipeline = Pipeline(site, aux_agency="COD", keep_vars=["C1C", "L1C"])

# Process single date
data = pipeline.process_date("2025001")

# Process range
for date, datasets in pipeline.process_range("2025001", "2025007"):
    print(f"Processed {date}")

# Calculate VOD
vod = pipeline.calculate_vod(
    canopy="canopy_01",
    reference="reference_01",
    date="2025001"
)

# Access stores directly
site.rinex_store.list_groups()
site.vod_store.read_group("canopy_01_vs_reference_01")
```

**Why this works:**
- ✅ More control over configuration
- ✅ Reusable objects (create once, use many times)
- ✅ Access to internals when needed
- ✅ Familiar OOP patterns
- ✅ Similar to scikit-learn, requests.Session

---

### Level 3: Low-Level (Advanced Users)

**5% of users need full control:**

```python
from canvod.store import GnssResearchSite, IcechunkDataReader
from canvod.vod import VODCalculator, TauOmegaZerothOrder
from canvod.readers import Rnxv3Obs
from canvod.aux import get_ephemerides, get_clocks

# Direct access to all components
site = GnssResearchSite("Rosalia")
reader = Rnxv3Obs("file.rnx")
calculator = VODCalculator(model=TauOmegaZerothOrder())

# Full manual control
# (existing gnssvodpy-style workflow)
```

**Why this works:**
- ✅ Full control for experts
- ✅ Direct access to implementations
- ✅ No magic, no hiding
- ✅ Power users can optimize

---

## 💡 Design Patterns to Use

### 1. Context Managers for Resources

```python
# Bad - manual cleanup
site = Site("Rosalia")
data = site.process_date("2025001")
site.close()  # Easy to forget!

# Good - automatic cleanup
with Site("Rosalia") as site:
    data = site.process_date("2025001")
# Automatically closes stores
```

### 2. Builder Pattern for Complex Config

```python
# Bad - too many parameters
pipeline = Pipeline(
    site, keep_vars=["C1C"], aux_agency="COD", 
    aux_product="rapid", n_workers=8, dry_run=False,
    progress=True, log_level="INFO"
)

# Good - builder pattern
pipeline = (
    Pipeline(site)
    .with_aux_config(agency="COD", product="rapid")
    .with_processing(keep_vars=["C1C"], n_workers=8)
    .with_options(dry_run=False, progress=True)
    .build()
)
```

### 3. Sensible Defaults (Convention over Configuration)

```python
# Don't make users specify everything
pipeline = Pipeline(site)  
# Defaults:
# - aux_agency="COD" (most common)
# - keep_vars=KEEP_RNX_VARS (from globals)
# - n_workers=os.cpu_count()
# - progress=True (helpful)

# But allow overrides
pipeline = Pipeline(site, aux_agency="ESA", keep_vars=["S1C"])
```

### 4. Method Chaining for Workflows

```python
# Fluent interface
results = (
    Site("Rosalia")
    .pipeline()
    .process_date("2025001")
    .calculate_vod("canopy_01", "reference_01")
    .visualize()
    .save("output.png")
)
```

### 5. Type Hints for IDE Support

```python
from typing import Literal
from datetime import date

def process_date(
    site: str | Site,
    date: str | date,
    keep_vars: list[str] | None = None,
    aux_agency: Literal["COD", "ESA", "GFZ", "JPL"] = "COD",
) -> dict[str, xr.Dataset]:
    """Process RINEX data for one date.
    
    Parameters
    ----------
    site : str or Site
        Site name (e.g., "Rosalia") or Site object
    date : str or date
        Date in YYYYDOY format or datetime.date
    keep_vars : list[str], optional
        RINEX variables to keep (default: KEEP_RNX_VARS)
    aux_agency : str, default "COD"
        Analysis center for auxiliary data
        
    Returns
    -------
    dict[str, xr.Dataset]
        Processed data for each receiver
    
    Examples
    --------
    >>> data = process_date("Rosalia", "2025001")
    >>> print(data.keys())
    dict_keys(['canopy_01', 'canopy_02', 'reference_01'])
    """
    ...
```

---

## 🎨 Wrapping gnssvodpy Logic

### Pattern: Thin Wrapper Around Proven Code

**Don't rewrite - wrap cleanly!**

```python
# canvodpy/src/canvodpy/api.py

from canvod.store import GnssResearchSite
from canvodpy.processor.pipeline_orchestrator import PipelineOrchestrator
from canvodpy.globals import KEEP_RNX_VARS

class Site:
    """User-friendly site wrapper.
    
    Thin wrapper around GnssResearchSite with better API.
    """
    
    def __init__(self, name: str):
        """Initialize site.
        
        Parameters
        ----------
        name : str
            Site name from config (e.g., "Rosalia")
        """
        # Use proven gnssvodpy implementation
        self._site = GnssResearchSite(name)
        self.name = name
    
    @property
    def receivers(self) -> dict:
        """Get all configured receivers."""
        return self._site.receivers
    
    @property
    def active_receivers(self) -> dict:
        """Get only active receivers."""
        return self._site.active_receivers
    
    @property
    def rinex_store(self):
        """Access RINEX data store."""
        return self._site.rinex_store
    
    @property
    def vod_store(self):
        """Access VOD results store."""
        return self._site.vod_store
    
    def pipeline(self, **kwargs) -> "Pipeline":
        """Create a processing pipeline for this site.
        
        Parameters
        ----------
        **kwargs : dict
            Pipeline configuration options
            
        Returns
        -------
        Pipeline
            Configured pipeline object
        """
        return Pipeline(self, **kwargs)
    
    def __repr__(self) -> str:
        return f"Site('{self.name}', receivers={len(self.active_receivers)})"


class Pipeline:
    """User-friendly pipeline wrapper.
    
    Thin wrapper around PipelineOrchestrator with better API.
    """
    
    def __init__(
        self,
        site: Site | str,
        keep_vars: list[str] | None = None,
        aux_agency: str = "COD",
        aux_product: str = "rapid",
        n_workers: int = 12,
        dry_run: bool = False,
        progress: bool = True,
    ):
        """Initialize pipeline.
        
        Parameters
        ----------
        site : Site or str
            Site object or site name
        keep_vars : list[str], optional
            RINEX variables to keep (default: KEEP_RNX_VARS)
        aux_agency : str, default "COD"
            Analysis center for auxiliary data
        aux_product : str, default "rapid"
            Product type ('final', 'rapid', 'ultra-rapid')
        n_workers : int, default 12
            Number of parallel workers
        dry_run : bool, default False
            If True, only simulate processing
        progress : bool, default True
            Show progress bars
        """
        # Handle both Site object and string
        if isinstance(site, str):
            site = Site(site)
        
        self.site = site
        self.keep_vars = keep_vars or KEEP_RNX_VARS
        self.aux_agency = aux_agency
        self.aux_product = aux_product
        self.n_workers = n_workers
        self.dry_run = dry_run
        self.progress = progress
        
        # Use proven gnssvodpy implementation
        self._orchestrator = PipelineOrchestrator(
            site=site._site,  # Pass internal GnssResearchSite
            n_max_workers=n_workers,
            dry_run=dry_run,
        )
    
    def process_date(self, date: str) -> dict:
        """Process one date.
        
        Parameters
        ----------
        date : str
            Date in YYYYDOY format (e.g., "2025001")
            
        Returns
        -------
        dict[str, xr.Dataset]
            Processed data for each receiver
        """
        # Use proven orchestrator logic
        for date_key, datasets, timing in self._orchestrator.process_by_date(
            keep_vars=self.keep_vars,
            start_from=date,
            end_at=date
        ):
            return datasets  # Return first (only) date
        
        return {}  # No data
    
    def process_range(self, start: str, end: str):
        """Process date range.
        
        Parameters
        ----------
        start : str
            Start date (YYYYDOY)
        end : str
            End date (YYYYDOY)
            
        Yields
        ------
        tuple[str, dict]
            (date_key, datasets) for each date
        """
        # Use proven orchestrator logic
        for date_key, datasets, timing in self._orchestrator.process_by_date(
            keep_vars=self.keep_vars,
            start_from=start,
            end_at=end
        ):
            yield date_key, datasets
    
    def calculate_vod(
        self,
        canopy: str,
        reference: str,
        date: str,
    ):
        """Calculate VOD for a receiver pair.
        
        Parameters
        ----------
        canopy : str
            Canopy receiver name
        reference : str
            Reference receiver name
        date : str
            Date in YYYYDOY format
            
        Returns
        -------
        xr.Dataset
            VOD results
        """
        from canvod.vod import VODCalculator
        
        # Load processed data
        canopy_data = self.site.rinex_store.read_group(canopy, date=date)
        ref_data = self.site.rinex_store.read_group(reference, date=date)
        
        # Calculate VOD using proven algorithm
        calculator = VODCalculator()
        vod_results = calculator.compute(canopy_data, ref_data)
        
        return vod_results


# Convenience functions (Level 1 API)

def process_date(site: str, date: str, **kwargs) -> dict:
    """Process one day of RINEX data (convenience function).
    
    Parameters
    ----------
    site : str
        Site name (e.g., "Rosalia")
    date : str
        Date in YYYYDOY format
    **kwargs : dict
        Additional pipeline options
        
    Returns
    -------
    dict[str, xr.Dataset]
        Processed data for each receiver
        
    Examples
    --------
    >>> data = process_date("Rosalia", "2025001")
    >>> print(data.keys())
    dict_keys(['canopy_01', 'reference_01'])
    """
    pipeline = Pipeline(site, **kwargs)
    return pipeline.process_date(date)


def calculate_vod(
    site: str,
    canopy: str,
    reference: str,
    date: str,
    **kwargs
):
    """Calculate VOD (convenience function).
    
    Parameters
    ----------
    site : str
        Site name
    canopy : str
        Canopy receiver name
    reference : str
        Reference receiver name
    date : str
        Date in YYYYDOY format
    **kwargs : dict
        Additional pipeline options
        
    Returns
    -------
    xr.Dataset
        VOD results
        
    Examples
    --------
    >>> vod = calculate_vod("Rosalia", "canopy_01", "reference_01", "2025001")
    >>> print(vod.vod.mean())
    0.42
    """
    pipeline = Pipeline(site, **kwargs)
    return pipeline.calculate_vod(canopy, reference, date)
```

---

## 🎯 Key Design Decisions

### 1. Thin Wrappers, Not Rewrites

**Don't rewrite gnssvodpy's proven logic!**

✅ **DO:** Wrap existing classes with better API  
❌ **DON'T:** Reimplement everything from scratch

### 2. Progressive Disclosure

**Match complexity to user needs:**

- Beginners: `process_date("Rosalia", "2025001")`
- Intermediate: `Pipeline(site).process_date("2025001")`
- Advanced: Direct access to `PipelineOrchestrator`

### 3. Consistency

**Same patterns everywhere:**

```python
# All "process" methods return data
data = process_date(...)
data = pipeline.process_date(...)
data = orchestrator.process_by_date(...)

# All "calculate" methods return results
vod = calculate_vod(...)
vod = pipeline.calculate_vod(...)
vod = calculator.compute(...)
```

### 4. Discoverability

**IDE autocomplete should work:**

```python
site = Site("Rosalia")
site.  # <-- IDE shows: receivers, active_receivers, pipeline(), etc.

pipeline = site.pipeline()
pipeline.  # <-- IDE shows: process_date(), process_range(), calculate_vod()
```

---

## 📚 API Design References

### Excellent Python API Examples

1. **requests** - Simple, clean, progressive
   ```python
   requests.get(url)                    # Simple
   session = requests.Session()         # More control
   adapter = requests.adapters.HTTPAdapter()  # Full control
   ```

2. **pathlib** - Fluent, chainable
   ```python
   Path("data").read_text()             # Fluent
   Path("data").glob("*.csv")           # Chainable
   ```

3. **polars** - Builder pattern
   ```python
   pl.scan_csv("data.csv")
      .filter(pl.col("x") > 0)
      .collect()
   ```

4. **scikit-learn** - Consistent interface
   ```python
   model.fit(X, y)                      # Always "fit"
   model.predict(X)                     # Always "predict"
   ```

### API Design Resources

- [The Zen of Python](https://peps.python.org/pep-0020/) - Guiding principles
- [PEP 8](https://peps.python.org/pep-0008/) - Style guide
- [API Design Patterns](https://learning.oreilly.com/library/view/api-design-patterns/9781617295850/) - Book
- [Fluent Python](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/) - Pythonic patterns

---

## 🚀 Implementation Plan

### Step 1: Create `canvodpy/api.py` (2 days)

Implement:
- `Site` class (wrapper around `GnssResearchSite`)
- `Pipeline` class (wrapper around `PipelineOrchestrator`)
- Convenience functions (`process_date`, `calculate_vod`)

### Step 2: Update `canvodpy/__init__.py` (1 day)

```python
# canvodpy/src/canvodpy/__init__.py

from canvodpy.api import (
    Site,
    Pipeline,
    process_date,
    calculate_vod,
)

# Re-export subpackages for advanced users
from canvod import readers, aux, grids, vod, viz, store

__all__ = [
    # High-level API
    "Site",
    "Pipeline",
    "process_date",
    "calculate_vod",
    
    # Subpackages
    "readers",
    "aux",
    "grids",
    "vod",
    "viz",
    "store",
]
```

### Step 3: Documentation & Examples (2 days)

Create:
- Quick start guide
- API reference
- Example notebooks
- Migration guide from gnssvodpy

---

## ✅ Success Criteria

After implementation, users should be able to:

```python
# Level 1: One-liner (most users)
from canvodpy import process_date
data = process_date("Rosalia", "2025001")

# Level 2: More control (power users)
from canvodpy import Site, Pipeline
site = Site("Rosalia")
pipeline = site.pipeline(aux_agency="ESA")
data = pipeline.process_date("2025001")

# Level 3: Full control (experts)
from canvod.store import GnssResearchSite
from canvodpy.processor import PipelineOrchestrator
# Direct access to internals
```

**All three levels work! Choose based on your needs!** 🎉

---

**Next Steps:** Implement `canvodpy/api.py` with these patterns?
