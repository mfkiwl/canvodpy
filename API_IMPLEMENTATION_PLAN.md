# Modern 2026 Python API Implementation Plan

## Architecture: Protocol-Based Plugin System

### Core Principles
- **Protocols over inheritance** - Structural typing (PEP 544)
- **Factory registration** - User-extensible components
- **Functional API** - Pure functions using factories
- **Type-safe** - Generics, type hints everywhere
- **Explicit** - Every transformation visible

---

## Phase 1: Protocol Definitions

### File: `canvodpy/protocols.py`

```python
"""Protocol definitions for pluggable components.

Protocols define structural interfaces without inheritance.
Any class matching the protocol structure works automatically.
"""

from __future__ import annotations
from typing import Protocol, runtime_checkable
from pathlib import Path
import pandas as pd
import xarray as xr
from canvod.grids import GridData

@runtime_checkable
class RinexReader(Protocol):
    """Protocol for RINEX file readers.
    
    Any reader matching this interface can be registered.
    Users can implement custom readers for different formats.
    """
    
    def read(
        self, 
        file_path: Path,
        *,
        keep_vars: list[str] | None = None,
    ) -> xr.Dataset:
        """Read RINEX file and return xarray Dataset.
        
        Parameters
        ----------
        file_path : Path
            Path to RINEX file
        keep_vars : list[str] | None
            Variables to keep (e.g., ['C1C', 'L1C', 'S1C'])
            
        Returns
        -------
        xr.Dataset
            Dataset with dimensions (epoch, sid) and variables
        """
        ...
    
    def get_receiver_position(self, file_path: Path) -> tuple[float, float, float]:
        """Extract receiver position (ECEF) from file header.
        
        Returns
        -------
        tuple[float, float, float]
            (x, y, z) in meters (ECEF coordinates)
        """
        ...


@runtime_checkable
class GridBuilder(Protocol):
    """Protocol for hemisphere grid builders.
    
    Supports different gridding methods (equal-area, regular, HEALPix, HTM, etc.)
    """
    
    def create(
        self,
        *,
        resolution: float,
        **kwargs,
    ) -> GridData:
        """Create hemisphere grid.
        
        Parameters
        ----------
        resolution : float
            Angular resolution in degrees
        **kwargs
            Additional grid-specific parameters
            
        Returns
        -------
        GridData
            Grid with cell centers, vertices, solid angles
        """
        ...


@runtime_checkable  
class VODCalculator(Protocol):
    """Protocol for VOD calculation algorithms.
    
    Supports different models (tau-omega, direct SNR, custom models)
    """
    
    def calculate(
        self,
        canopy: xr.Dataset,
        reference: xr.Dataset,
        grid: GridData,
        **kwargs,
    ) -> xr.Dataset:
        """Calculate VOD from canopy and reference observations.
        
        Parameters
        ----------
        canopy : xr.Dataset
            Canopy receiver observations (gridded + aggregated)
        reference : xr.Dataset
            Reference receiver observations (gridded + aggregated)
        grid : GridData
            Hemisphere grid
        **kwargs
            Model-specific parameters
            
        Returns
        -------
        xr.Dataset
            VOD results with variables: vod, tau, omega, etc.
        """
        ...


@runtime_checkable
class AggregationStrategy(Protocol):
    """Protocol for aggregating multiple observations per cell."""
    
    def aggregate(
        self,
        gridded_data: xr.Dataset,
        **kwargs,
    ) -> xr.Dataset:
        """Aggregate observations within each grid cell.
        
        Parameters
        ----------
        gridded_data : xr.Dataset
            Dataset with cell_id assigned to each observation
        **kwargs
            Strategy-specific parameters
            
        Returns
        -------
        xr.Dataset
            Aggregated data with one value per cell
        """
        ...
```

---

## Phase 2: Factory Classes

### File: `canvodpy/factories.py`

```python
"""Factory classes for component registration and creation.

Users register custom implementations, then functional API uses them.
"""

from __future__ import annotations
from typing import TypeVar, Generic, Type
from canvodpy.protocols import (
    RinexReader, 
    GridBuilder, 
    VODCalculator,
    AggregationStrategy,
)

T = TypeVar('T')

class ComponentFactory(Generic[T]):
    """Generic factory for registering and creating components.
    
    Type-safe factory using generics.
    """
    
    def __init__(self, component_type: str):
        self._registry: dict[str, Type[T]] = {}
        self._component_type = component_type
        
    def register(self, name: str, implementation: Type[T]) -> None:
        """Register a component implementation.
        
        Parameters
        ----------
        name : str
            Unique identifier for this implementation
        implementation : Type[T]
            Class implementing the protocol
            
        Examples
        --------
        >>> factory = ComponentFactory[RinexReader]("reader")
        >>> factory.register("rinex_v3", Rnxv3Reader)
        >>> factory.register("my_custom", MyCustomReader)
        """
        self._registry[name] = implementation
        
    def create(self, name: str, **kwargs) -> T:
        """Create instance of registered component.
        
        Parameters
        ----------
        name : str
            Registered component name
        **kwargs
            Arguments passed to component constructor
            
        Returns
        -------
        T
            Component instance
            
        Raises
        ------
        ValueError
            If component name not registered
        """
        if name not in self._registry:
            available = ", ".join(self._registry.keys())
            raise ValueError(
                f"{self._component_type} '{name}' not registered. "
                f"Available: {available}"
            )
        return self._registry[name](**kwargs)
    
    def list_registered(self) -> list[str]:
        """List all registered component names."""
        return list(self._registry.keys())
    
    def is_registered(self, name: str) -> bool:
        """Check if component is registered."""
        return name in self._registry


# Global factory instances
ReaderFactory = ComponentFactory[RinexReader]("reader")
GridFactory = ComponentFactory[GridBuilder]("grid")
VODFactory = ComponentFactory[VODCalculator]("vod_calculator")
AggregationFactory = ComponentFactory[AggregationStrategy]("aggregation")


# Register built-in implementations on import
def _register_builtins():
    """Register built-in implementations."""
    from canvodpy.readers import Rinexv3Reader
    from canvodpy.grids import EqualAreaGridBuilder, RegularGridBuilder
    from canvodpy.vod import TauOmegaCalculator
    from canvodpy.aggregation import MeanAggregation, MedianAggregation
    
    # Readers
    ReaderFactory.register("rinex_v3", Rinexv3Reader)
    ReaderFactory.register("rinex_v304", Rinexv3Reader)  # Alias
    
    # Grids
    GridFactory.register("equal_area", EqualAreaGridBuilder)
    GridFactory.register("regular", RegularGridBuilder)
    
    # VOD calculators
    VODFactory.register("tau_omega", TauOmegaCalculator)
    
    # Aggregation
    AggregationFactory.register("mean", MeanAggregation)
    AggregationFactory.register("median", MedianAggregation)

_register_builtins()
```

---

## Phase 3: Functional API

### File: `canvodpy/api.py`

```python
"""Functional API for VOD processing.

Each function is standalone, composable, and Airflow-compatible.
Functions use factory pattern internally for extensibility.
"""

from __future__ import annotations
from pathlib import Path
import xarray as xr
from canvod.grids import GridData

from canvodpy.factories import (
    ReaderFactory,
    GridFactory,
    VODFactory,
    AggregationFactory,
)


def process_rinex(
    file_path: str | Path,
    date: str,
    *,
    reader_type: str = "rinex_v3",
    keep_vars: list[str] | None = None,
    download_aux: bool = True,
) -> xr.Dataset:
    """Process RINEX file to observations with spherical coordinates.
    
    This function:
    1. Reads RINEX file using registered reader
    2. Downloads auxiliary data (ephemeris, clocks) if needed
    3. Augments with satellite positions
    4. Computes spherical coordinates (theta, phi, r)
    
    Parameters
    ----------
    file_path : str or Path
        Path to RINEX file
    date : str
        Date in YYYYDOY format (e.g., "2025001")
    reader_type : str, default "rinex_v3"
        Registered reader to use
    keep_vars : list[str] | None
        RINEX variables to keep (e.g., ['C1C', 'L1C', 'S1C'])
    download_aux : bool, default True
        Whether to download auxiliary data automatically
        
    Returns
    -------
    xr.Dataset
        Processed observations with dimensions (epoch, sid) and variables:
        - RINEX data (C1C, L1C, S1C, etc.)
        - phi : azimuth angle [0, 2π)
        - theta : zenith angle [0, π/2]
        - r : distance from receiver (meters)
        
    Examples
    --------
    >>> obs = process_rinex(
    ...     "data/canopy_2025001.rnx",
    ...     date="2025001",
    ...     reader_type="rinex_v3",
    ...     keep_vars=["S1C"],  # Keep only SNR
    ... )
    >>> obs
    <xarray.Dataset>
    Dimensions:  (epoch: 2880, sid: 32)
    Coordinates:
      * epoch    (epoch) datetime64[ns] ...
      * sid      (sid) object 'G01' 'G02' ...
    Data variables:
        S1C      (epoch, sid) float64 ...
        phi      (epoch, sid) float64 ...
        theta    (epoch, sid) float64 ...
        r        (epoch, sid) float64 ...
        
    Custom reader:
    
    >>> from canvodpy import ReaderFactory
    >>> ReaderFactory.register("my_format", MyCustomReader)
    >>> obs = process_rinex("data.dat", "2025001", reader_type="my_format")
    
    See Also
    --------
    create_grid : Create hemisphere grid
    assign_to_grid : Assign observations to grid cells
    """
    # Implementation uses existing RinexDataProcessor
    reader = ReaderFactory.create(reader_type)
    # ... actual processing ...
    pass


def create_grid(
    resolution: float,
    *,
    grid_type: str = "equal_area",
    **kwargs,
) -> GridData:
    """Create hemisphere grid for binning observations.
    
    Parameters
    ----------
    resolution : float
        Angular resolution in degrees (e.g., 5.0 for 5-degree cells)
    grid_type : str, default "equal_area"
        Registered grid type:
        - "equal_area": Cells have equal solid angle (recommended)
        - "regular": Regular lat-lon grid
        - Custom: Any user-registered grid type
    **kwargs
        Grid-specific parameters passed to builder
        
    Returns
    -------
    GridData
        Grid object with:
        - ncells : int - Number of cells
        - grid : DataFrame - Cell centers (phi, theta), solid angles
        - vertices : DataFrame - Cell boundary vertices
        
    Examples
    --------
    Standard equal-area grid:
    
    >>> grid = create_grid(resolution=5.0)
    >>> grid.ncells
    324
    
    Regular lat-lon grid:
    
    >>> grid = create_grid(resolution=5.0, grid_type="regular")
    
    Custom grid:
    
    >>> from canvodpy import GridFactory
    >>> GridFactory.register("healpix", HEALPixBuilder)
    >>> grid = create_grid(resolution=5.0, grid_type="healpix", nside=8)
    
    See Also
    --------
    assign_to_grid : Assign observations to grid cells
    process_rinex : Process RINEX to observations
    """
    builder = GridFactory.create(grid_type)
    return builder.create(resolution=resolution, **kwargs)


def assign_to_grid(
    observations: xr.Dataset,
    grid: GridData,
    *,
    method: str = "nearest",
) -> xr.Dataset:
    """Assign observations to grid cells.
    
    Parameters
    ----------
    observations : xr.Dataset
        Observations with phi, theta coordinates
    grid : GridData
        Target hemisphere grid
    method : str, default "nearest"
        Assignment method:
        - "nearest": Nearest grid cell (KDTree-based, fast)
        - "interpolate": Bilinear interpolation (future)
        
    Returns
    -------
    xr.Dataset
        Observations with added 'cell_id' coordinate variable
        
    Examples
    --------
    >>> canopy = process_rinex("canopy.rnx", "2025001")
    >>> grid = create_grid(resolution=5.0)
    >>> canopy_gridded = assign_to_grid(canopy, grid)
    >>> canopy_gridded.cell_id
    <xarray.DataArray 'cell_id' (epoch: 2880, sid: 32)>
    array([[142, 156, 201, ...], ...])
    
    See Also
    --------
    aggregate_cells : Aggregate multiple observations per cell
    """
    # Uses existing add_cell_ids_to_vod_fast
    pass


def aggregate_cells(
    gridded_observations: xr.Dataset,
    *,
    statistic: str = "mean",
    **kwargs,
) -> xr.Dataset:
    """Aggregate multiple observations within each grid cell.
    
    Parameters
    ----------
    gridded_observations : xr.Dataset
        Observations with cell_id assigned
    statistic : str, default "mean"
        Aggregation statistic:
        - "mean": Average (recommended)
        - "median": Median (robust to outliers)
        - "max": Maximum
        - Custom: Any user-registered strategy
    **kwargs
        Strategy-specific parameters
        
    Returns
    -------
    xr.Dataset
        Aggregated data with dimension (cell_id) instead of (epoch, sid)
        
    Examples
    --------
    >>> canopy_gridded = assign_to_grid(canopy, grid)
    >>> canopy_agg = aggregate_cells(canopy_gridded, statistic="mean")
    >>> canopy_agg
    <xarray.Dataset>
    Dimensions:  (cell_id: 324)
    Coordinates:
      * cell_id  (cell_id) int64 0 1 2 ... 323
    Data variables:
        S1C      (cell_id) float64 ...
        n_obs    (cell_id) int64 ...
        
    See Also
    --------
    assign_to_grid : Assign observations to cells
    calculate_vod : Calculate VOD from aggregated data
    """
    strategy = AggregationFactory.create(statistic)
    return strategy.aggregate(gridded_observations, **kwargs)


def calculate_vod(
    canopy: xr.Dataset,
    reference: xr.Dataset,
    grid: GridData,
    *,
    method: str = "tau_omega",
    **kwargs,
) -> xr.Dataset:
    """Calculate VOD from canopy and reference observations.
    
    Parameters
    ----------
    canopy : xr.Dataset
        Aggregated canopy observations (one value per cell)
    reference : xr.Dataset
        Aggregated reference observations (one value per cell)
    grid : GridData
        Hemisphere grid
    method : str, default "tau_omega"
        Calculation method:
        - "tau_omega": Tau-omega zeroth order model (recommended)
        - Custom: Any user-registered calculator
    **kwargs
        Method-specific parameters
        
    Returns
    -------
    xr.Dataset
        VOD results with variables:
        - vod : Vegetation optical depth (dB)
        - tau : Optical depth
        - omega : Single scattering albedo
        - n_obs_canopy : Observation counts
        - n_obs_reference : Observation counts
        
    Examples
    --------
    Full workflow:
    
    >>> # Process observations
    >>> canopy = process_rinex("canopy.rnx", "2025001")
    >>> reference = process_rinex("reference.rnx", "2025001")
    >>> 
    >>> # Grid and aggregate
    >>> grid = create_grid(resolution=5.0)
    >>> canopy_agg = aggregate_cells(assign_to_grid(canopy, grid))
    >>> reference_agg = aggregate_cells(assign_to_grid(reference, grid))
    >>> 
    >>> # Calculate VOD
    >>> vod = calculate_vod(canopy_agg, reference_agg, grid)
    >>> vod.vod.mean()
    0.42
    
    Custom calculator:
    
    >>> from canvodpy import VODFactory
    >>> VODFactory.register("my_model", MyVODCalculator)
    >>> vod = calculate_vod(canopy, reference, grid, method="my_model")
    
    See Also
    --------
    process_rinex : Process RINEX files
    aggregate_cells : Aggregate observations
    """
    calculator = VODFactory.create(method)
    return calculator.calculate(canopy, reference, grid, **kwargs)


def save_vod(
    vod: xr.Dataset,
    path: str | Path,
    *,
    format: str = "zarr",
) -> None:
    """Save VOD results to file.
    
    Parameters
    ----------
    vod : xr.Dataset
        VOD results
    path : str or Path
        Output path
    format : str, default "zarr"
        Output format: "zarr", "netcdf"
        
    Examples
    --------
    >>> save_vod(vod, "output/rosalia_2025001.zarr")
    """
    if format == "zarr":
        vod.to_zarr(path, mode="w")
    elif format == "netcdf":
        vod.to_netcdf(path)
    else:
        raise ValueError(f"Unknown format: {format}")
```

---

## Phase 4: Built-in Implementations

### File: `canvodpy/readers/rinex_v3.py`

```python
"""RINEX v3 reader implementation."""

from pathlib import Path
import xarray as xr
from canvod.readers import Rnxv3Obs
from canvod.aux.position import ECEFPosition

class Rinexv3Reader:
    """RINEX v3.04 reader using canvod-readers."""
    
    def read(
        self,
        file_path: Path,
        *,
        keep_vars: list[str] | None = None,
    ) -> xr.Dataset:
        """Read RINEX v3 file."""
        rnx = Rnxv3Obs(fpath=file_path, include_auxiliary=False)
        return rnx.to_ds(
            keep_rnx_data_vars=keep_vars,
            write_global_attrs=True,
        )
    
    def get_receiver_position(self, file_path: Path) -> tuple[float, float, float]:
        """Extract receiver position from header."""
        rnx = Rnxv3Obs(fpath=file_path, include_auxiliary=False)
        ds = rnx.to_ds(keep_rnx_data_vars=[], write_global_attrs=True)
        pos = ECEFPosition.from_ds_metadata(ds)
        return (pos.x, pos.y, pos.z)
```

### File: `canvodpy/grids/builders.py`

```python
"""Grid builder implementations."""

from canvod.grids import GridData, create_hemigrid

class EqualAreaGridBuilder:
    """Equal-area hemisphere grid builder."""
    
    def create(self, *, resolution: float, **kwargs) -> GridData:
        """Create equal-area grid."""
        return create_hemigrid(
            angular_resolution=resolution,
            grid_type="equal_area",
        )


class RegularGridBuilder:
    """Regular lat-lon grid builder."""
    
    def create(self, *, resolution: float, **kwargs) -> GridData:
        """Create regular grid."""
        return create_hemigrid(
            angular_resolution=resolution,
            grid_type="regular",
        )
```

### File: `canvodpy/vod/tau_omega.py`

```python
"""Tau-omega VOD calculator implementation."""

import xarray as xr
from canvod.grids import GridData
from canvod.vod import TauOmegaZerothOrder

class TauOmegaCalculator:
    """Tau-omega zeroth order VOD calculator."""
    
    def calculate(
        self,
        canopy: xr.Dataset,
        reference: xr.Dataset,
        grid: GridData,
        **kwargs,
    ) -> xr.Dataset:
        """Calculate VOD using tau-omega model."""
        calculator = TauOmegaZerothOrder()
        return calculator.calculate_vod(canopy, reference, grid)
```

---

## Phase 5: Example Usage

### Simple script (95% of users)

```python
"""simple_vod_analysis.py - Basic VOD calculation"""

from canvodpy import (
    process_rinex,
    create_grid,
    assign_to_grid,
    aggregate_cells,
    calculate_vod,
    save_vod,
)

# Process RINEX files
canopy = process_rinex("data/canopy.rnx", date="2025001")
reference = process_rinex("data/reference.rnx", date="2025001")

# Create grid and assign
grid = create_grid(resolution=5.0)
canopy_gridded = assign_to_grid(canopy, grid)
reference_gridded = assign_to_grid(reference, grid)

# Aggregate and calculate VOD
canopy_agg = aggregate_cells(canopy_gridded, statistic="mean")
reference_agg = aggregate_cells(reference_gridded, statistic="mean")
vod = calculate_vod(canopy_agg, reference_agg, grid)

# Save
save_vod(vod, "output/rosalia_2025001.zarr")
print(f"✓ VOD mean: {vod.vod.mean():.3f} dB")
```

### Custom reader example

```python
"""custom_reader.py - Using a custom data format"""

from canvodpy import ReaderFactory, process_rinex

# Define custom reader
class MyDataFormatReader:
    """Reader for my lab's custom data format."""
    
    def read(self, file_path, *, keep_vars=None):
        # Custom parsing logic
        import pandas as pd
        data = pd.read_csv(file_path)  # Or whatever format
        # Convert to xarray Dataset with required structure
        return xr.Dataset(...)
    
    def get_receiver_position(self, file_path):
        # Extract position from custom header
        return (x, y, z)

# Register it
ReaderFactory.register("my_format", MyDataFormatReader)

# Now use it
obs = process_rinex(
    "my_data/station_a.dat",
    date="2025001",
    reader_type="my_format",  # Use custom reader!
)
```

### Airflow DAG

```python
"""airflow_vod_dag.py - Production processing"""

from airflow.decorators import dag, task
from canvodpy import (
    process_rinex,
    create_grid,
    assign_to_grid,
    aggregate_cells,
    calculate_vod,
)

@dag(schedule="@daily")
def vod_processing():
    
    @task
    def process_canopy(date: str):
        return process_rinex(f"data/canopy_{date}.rnx", date)
    
    @task
    def process_reference(date: str):
        return process_rinex(f"data/reference_{date}.rnx", date)
    
    @task
    def create_grid_task():
        return create_grid(resolution=5.0)
    
    @task
    def assign_and_aggregate(obs, grid):
        gridded = assign_to_grid(obs, grid)
        return aggregate_cells(gridded, statistic="mean")
    
    @task
    def calculate_vod_task(canopy_agg, ref_agg, grid):
        return calculate_vod(canopy_agg, ref_agg, grid)
    
    # Build DAG
    date = "2025001"
    canopy = process_canopy(date)
    reference = process_reference(date)
    grid = create_grid_task()
    
    canopy_agg = assign_and_aggregate(canopy, grid)
    ref_agg = assign_and_aggregate(reference, grid)
    
    calculate_vod_task(canopy_agg, ref_agg, grid)

dag = vod_processing()
```

---

## Implementation Order

1. ✅ **Phase 1: Protocols** (`canvodpy/protocols.py`)
   - Define RinexReader, GridBuilder, VODCalculator, AggregationStrategy
   
2. ✅ **Phase 2: Factories** (`canvodpy/factories.py`)
   - ComponentFactory with generics
   - Global factory instances
   - Register built-ins
   
3. ✅ **Phase 3: Built-in implementations**
   - Rinexv3Reader wrapping Rnxv3Obs
   - EqualAreaGridBuilder wrapping create_hemigrid
   - TauOmegaCalculator wrapping TauOmegaZerothOrder
   - MeanAggregation, MedianAggregation
   
4. ✅ **Phase 4: Functional API** (`canvodpy/api.py`)
   - process_rinex() - wraps RinexDataProcessor
   - create_grid() - wraps create_hemigrid
   - assign_to_grid() - wraps add_cell_ids_to_vod_fast
   - aggregate_cells() - new implementation
   - calculate_vod() - wraps TauOmegaZerothOrder
   - save_vod() - simple xarray wrapper
   
5. ✅ **Phase 5: Examples**
   - examples/basic_workflow.py
   - examples/custom_reader.py
   - examples/airflow_dag.py
   - examples/batch_processing.py

6. ✅ **Phase 6: Tests**
   - tests/test_factories.py
   - tests/test_api.py
   - tests/test_protocols.py

7. ✅ **Phase 7: Documentation**
   - Update README with new API
   - API reference docs
   - User guide

---

## Benefits

✅ **Protocol-based** - No inheritance, structural typing
✅ **Extensible** - Users register custom components easily
✅ **Type-safe** - Full type hints, generics
✅ **Airflow-ready** - Pure functions, no state
✅ **Explicit** - Every step visible
✅ **Modern 2026 Python** - Latest best practices
✅ **Backward compatible** - Old API still works

---

## Next Steps

Should I start implementing Phase 1 (Protocols)?
