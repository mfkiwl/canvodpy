# ABC + Factory Pattern: Design Analysis

## Question: Is this proper 2026 Python design + Airflow-compatible?

---

## ✅ YES - Here's Why

### 1. Modern Python Design Principles (2026)

#### Type Safety ✅
```python
class ComponentFactory(Generic[T]):
    def create(self, name: str, **kwargs) -> T:
        # Type-safe: T is bound to ABC at creation
        return self._registry[name](**kwargs)

# Type checker knows this returns BaseGridBuilder
grid_builder = GridFactory.create("equal_area")
```

#### Open/Closed Principle ✅
```python
# Open for extension (users can register new types)
GridFactory.register("healpix", HEALPixBuilder)

# Closed for modification (no need to change canvodpy code)
grid = create_grid(5.0, grid_type="healpix")
```

#### Dependency Injection ✅
```python
# Functional API doesn't hardcode implementations
def create_grid(resolution: float, grid_type: str = "equal_area"):
    # Injected via factory at runtime
    builder = GridFactory.create(grid_type)
    return builder.build()
```

#### Single Responsibility ✅
- Factory: Creates instances
- ABC: Defines contract + shared code
- API: Provides simple interface
- User code: Implements custom logic

---

### 2. Airflow Compatibility ✅

#### Pure Functions (Airflow Requirement) ✅

```python
# Each function is stateless and pure
@task
def process_rinex_task(file_path: str, date: str):
    # No instance state, creates fresh objects each call
    return read_rinex(file_path, date=date, reader_type="rinex_v3")

@task
def create_grid_task(resolution: float):
    # Factory creates new instance each time
    return create_grid(resolution, grid_type="equal_area")

@task
def calculate_vod_task(canopy, reference):
    # No side effects, just computation
    return calculate_vod(canopy, reference, method="tau_omega")
```

#### Worker Process Compatibility ✅

**Potential Issue:** Factory registration happens at import time.
- In Airflow, each worker imports modules independently
- Factory registration must happen in EVERY worker process

**Solution:** Module-level registration

```python
# canvodpy/__init__.py
from canvodpy.factories import ReaderFactory, GridFactory, VODFactory

# This runs when module is imported (happens in every worker)
def _register_builtins():
    from canvod.readers import Rnxv3Obs
    from canvod.grids import EqualAreaGridBuilder
    from canvod.vod import TauOmegaZerothOrder
    
    ReaderFactory.register("rinex_v3", Rnxv3Obs)
    GridFactory.register("equal_area", EqualAreaGridBuilder)
    VODFactory.register("tau_omega", TauOmegaZerothOrder)

_register_builtins()  # Runs on import in every worker ✅
```

#### Serialization (XCom between tasks) ⚠️

**Issue:** Passing large xarray Datasets between Airflow tasks

```python
@task
def process_rinex_task():
    obs = read_rinex(...)  # Returns xr.Dataset
    return obs  # ⚠️ Could be large (100MB+)

@task
def create_grid_task():
    grid = create_grid(...)  # Returns GridData (small)
    return grid  # ⚠️ Has DataFrame inside

@task
def calculate_vod_task(obs, grid):  # ⚠️ obs might be too large for XCom
    ...
```

**Solutions:**

**Option A: File-based XCom** (Recommended)
```python
from pathlib import Path
from tempfile import gettempdir

@task
def process_rinex_task(file_path: str, date: str) -> str:
    """Return path to saved dataset instead of dataset itself."""
    obs = read_rinex(file_path, date=date)
    
    # Save to temp location
    output = Path(gettempdir()) / f"obs_{date}.zarr"
    obs.to_zarr(output, mode="w")
    
    return str(output)  # Return path (small, serializable) ✅

@task
def calculate_vod_task(canopy_path: str, ref_path: str) -> str:
    """Load from paths, compute, save result."""
    import xarray as xr
    
    canopy = xr.open_zarr(canopy_path)
    reference = xr.open_zarr(ref_path)
    
    vod = calculate_vod(canopy, reference)
    
    output = Path(gettempdir()) / f"vod_{datetime.now()}.zarr"
    vod.to_zarr(output, mode="w")
    
    return str(output)
```

**Option B: Custom XCom Backend**
```python
# airflow.cfg
[core]
xcom_backend = canvodpy.airflow.ZarrXComBackend

# canvodpy/airflow.py
from airflow.models.xcom import BaseXCom
import xarray as xr

class ZarrXComBackend(BaseXCom):
    """Store xarray Datasets as Zarr files."""
    
    @staticmethod
    def serialize_value(value):
        if isinstance(value, xr.Dataset):
            # Save to Zarr, return reference
            ...
        return BaseXCom.serialize_value(value)
    
    @staticmethod
    def deserialize_value(result):
        if is_zarr_reference(result):
            return xr.open_zarr(result)
        return BaseXCom.deserialize_value(result)
```

**Option C: TaskFlow API with S3** (Production)
```python
@task
def process_rinex_task(file_path: str, date: str) -> str:
    obs = read_rinex(file_path, date=date)
    
    # Save to S3
    s3_path = f"s3://bucket/processed/obs_{date}.zarr"
    obs.to_zarr(s3_path, mode="w")
    
    return s3_path

@task
def calculate_vod_task(canopy_s3: str, ref_s3: str) -> str:
    canopy = xr.open_zarr(canopy_s3)
    reference = xr.open_zarr(ref_s3)
    
    vod = calculate_vod(canopy, reference)
    
    s3_path = f"s3://bucket/vod/vod_{datetime.now()}.zarr"
    vod.to_zarr(s3_path, mode="w")
    
    return s3_path
```

---

### 3. Complete Airflow Example

#### Simple DAG (Local Files)

```python
"""vod_processing_dag.py - Production-ready Airflow DAG"""

from airflow.decorators import dag, task
from datetime import datetime
from pathlib import Path

# Factory registration happens on import in each worker ✅
from canvodpy import (
    read_rinex,
    create_grid,
    assign_to_grid,
    aggregate_cells,
    calculate_vod,
)

@dag(
    dag_id="vod_processing",
    schedule="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False,
)
def vod_processing_pipeline():
    """VOD calculation pipeline."""
    
    @task
    def process_rinex_task(
        file_path: str, 
        date: str,
        reader_type: str = "rinex_v3"
    ) -> str:
        """Process RINEX → save to Zarr → return path."""
        obs = read_rinex(file_path, date=date, reader_type=reader_type)
        
        output = f"/data/processed/obs_{date}.zarr"
        obs.to_zarr(output, mode="w")
        
        return output
    
    @task
    def create_grid_task(resolution: float, grid_type: str = "equal_area") -> str:
        """Create grid → pickle → return path."""
        import pickle
        
        grid = create_grid(resolution, grid_type=grid_type)
        
        output = f"/data/grids/grid_{resolution}_{grid_type}.pkl"
        with open(output, "wb") as f:
            pickle.dump(grid, f)
        
        return output
    
    @task
    def assign_and_aggregate_task(obs_path: str, grid_path: str) -> str:
        """Load obs + grid → assign → aggregate → save."""
        import pickle
        import xarray as xr
        
        obs = xr.open_zarr(obs_path)
        with open(grid_path, "rb") as f:
            grid = pickle.load(f)
        
        gridded = assign_to_grid(obs, grid)
        aggregated = aggregate_cells(gridded, statistic="mean")
        
        output = obs_path.replace("obs_", "agg_")
        aggregated.to_zarr(output, mode="w")
        
        return output
    
    @task
    def calculate_vod_task(
        canopy_path: str, 
        ref_path: str,
        method: str = "tau_omega"
    ) -> str:
        """Load aggregated data → calculate VOD → save."""
        import xarray as xr
        
        canopy = xr.open_zarr(canopy_path)
        reference = xr.open_zarr(ref_path)
        
        # Grid not needed if data already aggregated per cell
        vod = calculate_vod(canopy, reference, method=method)
        
        output = f"/data/vod/vod_{datetime.now().date()}.zarr"
        vod.to_zarr(output, mode="w")
        
        return output
    
    # Build DAG
    date = "{{ ds_nodash }}"  # Airflow template
    
    # Process both receivers
    canopy = process_rinex_task(
        f"/data/rinex/canopy_{date}.rnx",
        date,
        reader_type="rinex_v3"
    )
    reference = process_rinex_task(
        f"/data/rinex/reference_{date}.rnx",
        date,
        reader_type="rinex_v3"
    )
    
    # Create grid once (reused)
    grid = create_grid_task(resolution=5.0, grid_type="equal_area")
    
    # Assign and aggregate both receivers
    canopy_agg = assign_and_aggregate_task(canopy, grid)
    ref_agg = assign_and_aggregate_task(reference, grid)
    
    # Calculate VOD
    vod_result = calculate_vod_task(canopy_agg, ref_agg, method="tau_omega")
    
    # Optional: Add notification task
    @task
    def notify_complete(vod_path: str):
        print(f"✅ VOD processing complete: {vod_path}")
    
    notify_complete(vod_result)

# Instantiate DAG
dag = vod_processing_pipeline()
```

#### With Custom Reader Registration

```python
"""custom_dag.py - Using custom reader in Airflow"""

from airflow.decorators import dag, task
from canvodpy import ReaderFactory, read_rinex
from canvod.readers import GNSSDataReader
import xarray as xr
from pathlib import Path

# Define custom reader
class MyLabReader(GNSSDataReader):
    """Custom reader for our lab's format."""
    def to_ds(self, keep_rnx_data_vars=None) -> xr.Dataset:
        # Custom parsing
        return xr.Dataset(...)

# Register BEFORE DAG definition
# This runs in each worker process when module imports
ReaderFactory.register("mylab_v1", MyLabReader)

@dag(dag_id="custom_reader_vod", schedule="@daily")
def custom_reader_pipeline():
    
    @task
    def process_custom_data(file_path: str, date: str) -> str:
        # Uses custom reader via factory!
        obs = read_rinex(
            file_path, 
            date=date, 
            reader_type="mylab_v1"  # Custom reader ✅
        )
        
        output = f"/data/obs_{date}.zarr"
        obs.to_zarr(output, mode="w")
        return output
    
    # ... rest of DAG

dag = custom_reader_pipeline()
```

---

### 4. Design Alternatives Comparison

#### Current Proposal: ABC + Factory

**Pros:**
- ✅ Leverages existing ABCs (no refactor)
- ✅ Type-safe (Generic[T] with ABC validation)
- ✅ Simple to understand (no frameworks)
- ✅ Airflow-compatible (pure functions)
- ✅ Extensible (register custom implementations)

**Cons:**
- ⚠️ Module-level registration (must happen in all workers)
- ⚠️ Not "discoverable" (users must know to call register)

#### Alternative 1: Dependency Injection Framework

```python
from injector import Injector, Module, provider

class CanvodpyModule(Module):
    @provider
    def provide_reader(self) -> GNSSDataReader:
        return Rnxv3Obs()
    
    @provider
    def provide_grid_builder(self) -> BaseGridBuilder:
        return EqualAreaGridBuilder()

injector = Injector([CanvodpyModule()])
reader = injector.get(GNSSDataReader)
```

**Pros:**
- More "enterprise" pattern
- Better for large teams

**Cons:**
- ❌ Overkill for scientific package
- ❌ Adds dependency
- ❌ Harder for scientists to understand
- ❌ More complex Airflow setup

#### Alternative 2: Entry Points (Plugin Discovery)

```python
# setup.py
entry_points={
    'canvodpy.readers': [
        'rinex_v3 = canvod.readers:Rnxv3Obs',
        'mylab = mypackage:MyLabReader',
    ],
}

# Auto-discovery
from importlib.metadata import entry_points
for ep in entry_points(group='canvodpy.readers'):
    ReaderFactory.register(ep.name, ep.load())
```

**Pros:**
- ✅ Auto-discovery (no manual registration)
- ✅ Standard Python packaging

**Cons:**
- ❌ More complex setup
- ❌ Requires separate package for extensions
- ❌ Still need factory under the hood

#### Alternative 3: Configuration-Based

```python
# canvodpy.yaml
readers:
  rinex_v3: canvod.readers.Rnxv3Obs
  mylab: mypackage.MyLabReader

grids:
  equal_area: canvod.grids.EqualAreaGridBuilder
```

**Pros:**
- ✅ No code for registration
- ✅ Easy to see all options

**Cons:**
- ❌ Requires YAML parsing
- ❌ Less type-safe
- ❌ Config file management

---

### 5. Recommendation

## ✅ **ABC + Factory is the RIGHT choice for your use case**

**Why:**

1. **Scientific package priorities:**
   - Simple > Complex ✅
   - Explicit > Magic ✅
   - No framework dependencies ✅
   - Scientists can understand it ✅

2. **Airflow compatibility:**
   - Pure functions ✅
   - Stateless ✅
   - Works with file-based XCom ✅
   - Each worker imports & registers ✅

3. **Matches your architecture:**
   - ABCs already exist ✅
   - No refactoring needed ✅
   - Adds extensibility layer ✅

4. **Modern Python (2026):**
   - Type-safe (Generic[T]) ✅
   - Open/closed principle ✅
   - Dependency injection ✅
   - Single responsibility ✅

**Minor improvements:**

1. **Add entry points for plugin discovery** (optional, later)
2. **Document Airflow patterns** clearly
3. **Provide XCom backend** for xarray (optional)

---

### 6. Final Answer

**YES - This is proper 2026 Python design AND Airflow-compatible!**

The ABC + Factory pattern is:
- ✅ Modern Python design
- ✅ Airflow-compatible with file-based XCom
- ✅ Simple for scientists
- ✅ Type-safe and extensible
- ✅ Matches your existing architecture

Just need to handle large data serialization in Airflow (use file paths, not in-memory datasets).

Should I implement this?
