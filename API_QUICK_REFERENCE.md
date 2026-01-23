# 🚀 canvodpy API Quick Reference

**Three ways to use canvodpy - choose based on your needs!**

---

## 📊 API Comparison

| Your Need | API Level | Complexity | Code Lines |
|-----------|-----------|------------|------------|
| Just process data | Level 1 | ⭐️ Simple | 1-2 lines |
| Need more control | Level 2 | ⭐️⭐️ Medium | 3-5 lines |
| Full customization | Level 3 | ⭐️⭐️⭐️ Advanced | 10+ lines |

---

## Level 1: Convenience Functions ⭐️

**Best for:** Quick scripts, Jupyter notebooks, getting started

**Pattern:** Simple functions - like pandas `pd.read_csv()`

```python
from canvodpy import process_date, calculate_vod

# Process one day (1 line!)
data = process_date("Rosalia", "2025001")
# Returns: {'canopy_01': xr.Dataset, 'reference_01': xr.Dataset, ...}

# Calculate VOD (1 line!)
vod = calculate_vod("Rosalia", "canopy_01", "reference_01", "2025001")
# Returns: xr.Dataset with VOD results

# With custom settings
data = process_date(
    site="Rosalia",
    date="2025001",
    keep_vars=["C1C", "L1C"],  # GPS L1 only
    aux_agency="ESA",           # Use ESA products
    n_workers=8                 # 8 parallel workers
)
```

**Pros:**
- ✅ Simplest possible
- ✅ One function = one task
- ✅ Sensible defaults
- ✅ Great for learning

**Cons:**
- ❌ Less control
- ❌ Can't reuse configuration

---

## Level 2: Object-Oriented API ⭐️⭐️

**Best for:** Production scripts, batch processing, repeated tasks

**Pattern:** Objects with methods - like requests `Session()`

```python
from canvodpy import Site, Pipeline

# Create site (loads config, validates)
site = Site("Rosalia")

# Inspect configuration
print(f"Active receivers: {len(site.active_receivers)}")
print(f"VOD analyses: {len(site.vod_analyses)}")

# Create pipeline (reusable!)
pipeline = site.pipeline(
    aux_agency="COD",
    keep_vars=["C1C", "L1C", "S1C"],
    n_workers=12
)

# Process single date
data = pipeline.process_date("2025001")

# Process range (iterator!)
for date, datasets in pipeline.process_range("2025001", "2025007"):
    print(f"✓ Processed {date}: {len(datasets)} receivers")
    
    # Calculate VOD for each date
    vod = pipeline.calculate_vod("canopy_01", "reference_01", date)
    print(f"  Mean VOD: {vod.vod.mean().values:.3f}")

# Preview before processing
plan = pipeline.preview()
print(f"Will process {plan['total_files']} RINEX files")

# Access stores directly
site.rinex_store.list_groups()
site.vod_store.read_group("canopy_01_vs_reference_01")
```

**Pros:**
- ✅ Reusable objects
- ✅ More control
- ✅ Access to internals
- ✅ Better for batch jobs

**Cons:**
- ❌ Slightly more verbose
- ❌ Need to understand objects

---

## Level 3: Low-Level Access ⭐️⭐️⭐️

**Best for:** Advanced users, custom workflows, research

**Pattern:** Direct access to internals - no magic

```python
from canvod.store import GnssResearchSite, IcechunkDataReader
from canvod.vod import VODCalculator, TauOmegaZerothOrder
from canvod.readers import Rnxv3Obs
from canvod.aux import get_ephemerides, get_clocks
from canvodpy.processor.pipeline_orchestrator import PipelineOrchestrator

# Direct access to all components
site = GnssResearchSite("Rosalia")

# Custom orchestrator configuration
orchestrator = PipelineOrchestrator(
    site=site,
    receiver_subpath_template="{receiver_dir}/custom/path",
    n_max_workers=16,
    dry_run=False
)

# Manual processing with full control
for date_key, datasets, timing in orchestrator.process_by_date(
    keep_vars=["C1C", "L1C"],
    start_from="2025001",
    end_at="2025007"
):
    # Custom logic here
    for receiver_name, ds in datasets.items():
        print(f"{receiver_name}: {timing[receiver_name]:.2f}s")

# Custom VOD calculation
calculator = VODCalculator(
    model=TauOmegaZerothOrder(),
    # Custom parameters
)

# Direct RINEX parsing
reader = Rnxv3Obs(fpath="data.rnx")
ds = reader.to_ds()
```

**Pros:**
- ✅ Full control
- ✅ Customize everything
- ✅ Access all internals
- ✅ Research workflows

**Cons:**
- ❌ More complex
- ❌ Need deep understanding
- ❌ More code to write

---

## 🎯 Which Level Should You Use?

### Start with Level 1 if:
- You're new to canvodpy
- You want quick results
- You're exploring in Jupyter
- You need a simple script

**Example:** Process one day of data
```python
from canvodpy import process_date
data = process_date("Rosalia", "2025001")
```

### Move to Level 2 when:
- You process data regularly
- You need batch processing
- You want more control
- You're building production scripts

**Example:** Process a week of data
```python
from canvodpy import Pipeline
pipeline = Pipeline("Rosalia")
for date, data in pipeline.process_range("2025001", "2025007"):
    # Your processing logic
    pass
```

### Use Level 3 if:
- You need custom workflows
- You're doing research
- You want maximum control
- Standard API doesn't fit

**Example:** Custom processing pipeline
```python
from canvodpy.processor import PipelineOrchestrator
# Build custom workflow
```

---

## 🔄 Mixing Levels

**You can mix levels!** Use the best tool for each task:

```python
from canvodpy import Site, process_date  # Levels 1 & 2
from canvod.viz import HemisphereVisualizer  # Level 3

# Level 2: Create site
site = Site("Rosalia")

# Level 1: Quick processing
data = process_date("Rosalia", "2025001")

# Level 3: Custom visualization
viz = HemisphereVisualizer()
fig = viz.plot_2d(data['canopy_01'])
```

---

## 📚 Common Patterns

### Pattern 1: Process and Store

```python
from canvodpy import Pipeline

pipeline = Pipeline("Rosalia")

# Process stores automatically
for date, datasets in pipeline.process_range("2025001", "2025031"):
    print(f"✓ {date} stored in Icechunk")
```

### Pattern 2: Process and Calculate VOD

```python
from canvodpy import Site

site = Site("Rosalia")
pipeline = site.pipeline()

for date, datasets in pipeline.process_range("2025001", "2025007"):
    # Calculate VOD for each analysis pair
    for analysis, config in site.vod_analyses.items():
        vod = pipeline.calculate_vod(
            config['canopy_receiver'],
            config['reference_receiver'],
            date
        )
        print(f"✓ VOD for {analysis}: {vod.vod.mean().values:.3f}")
```

### Pattern 3: Preview Before Processing

```python
from canvodpy import Pipeline

pipeline = Pipeline("Rosalia", dry_run=True)
plan = pipeline.preview()

print(f"Will process:")
print(f"  {len(plan['dates'])} dates")
print(f"  {plan['total_receivers']} receivers")
print(f"  {plan['total_files']} RINEX files")

# If OK, run for real
pipeline = Pipeline("Rosalia", dry_run=False)
data = pipeline.process_date("2025001")
```

---

## 🎓 Learning Path

**Beginner:**
1. Start with `process_date()` function
2. Try `calculate_vod()` function
3. Experiment with parameters

**Intermediate:**
4. Learn `Site` class
5. Use `Pipeline` for batch processing
6. Access stores directly

**Advanced:**
7. Use `PipelineOrchestrator` directly
8. Customize VOD calculations
9. Build custom workflows

---

## 💡 Tips

1. **Use type hints** - IDEs will show you available methods
2. **Check examples** - Look at docstrings with `help(process_date)`
3. **Start simple** - Begin with Level 1, add complexity as needed
4. **Read errors** - Error messages guide you to solutions
5. **Check config** - Verify `RESEARCH_SITES` in `research_sites_config.py`

---

## 🚀 Next Steps

**Try it:**

```python
# Install
pip install -e /path/to/canvodpy

# Run
python
>>> from canvodpy import process_date
>>> data = process_date("Rosalia", "2025001")
>>> print(data.keys())
```

**Learn more:**
- API Reference: See docstrings with `help()`
- Examples: Check `demo/` directory
- Documentation: Read `docs/` for details

---

**Remember:** All three levels work together. Choose what fits your task! 🎉
