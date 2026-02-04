# Revised API Design: ABCs + Factory Pattern

## Keep Your Existing ABCs! They're Good!

Your codebase already has well-designed ABCs:
- `VODCalculator(ABC, BaseModel)` - Combines ABC with Pydantic validation
- `BaseGridBuilder(ABC)` - Shared initialization and common methods
- `GNSSDataReader(ABC)` - Enforces reader interface

**Don't replace them with Protocols. Instead, wrap them with a Factory + functional API.**

---

## Revised Architecture: ABC + Factory

### Your Existing ABCs (Keep These!)

```python
# canvod-vod/calculator.py (EXISTING)
class VODCalculator(ABC, BaseModel):
    """ABC + Pydantic for validation."""
    canopy_ds: xr.Dataset
    sky_ds: xr.Dataset
    
    @abstractmethod
    def calculate_vod(self) -> xr.Dataset:
        ...

# canvod-grids/grid_builder.py (EXISTING)
class BaseGridBuilder(ABC):
    """ABC with shared __init__ and helpers."""
    def __init__(self, angular_resolution, cutoff_theta, phi_rotation):
        self.angular_resolution = angular_resolution
        # ... shared initialization
    
    @abstractmethod
    def _build_grid(self):
        ...

# canvod-readers/base.py (EXISTING)
class GNSSDataReader(ABC):
    """ABC enforcing reader interface."""
    @abstractmethod
    def to_ds(self, keep_rnx_data_vars=None) -> xr.Dataset:
        ...
```

### Add Factory Registration (NEW)

```python
# canvodpy/factories.py (NEW)
from typing import TypeVar, Generic, Type

T = TypeVar('T')

class ComponentFactory(Generic[T]):
    """Generic factory for ABC-based components."""
    
    def __init__(self, base_class: Type[T], component_type: str):
        self._base_class = base_class
        self._registry: dict[str, Type[T]] = {}
        self._component_type = component_type
        
    def register(self, name: str, implementation: Type[T]) -> None:
        """Register a component that inherits from ABC.
        
        Validates that implementation is a subclass of the ABC.
        """
        if not issubclass(implementation, self._base_class):
            raise TypeError(
                f"{implementation} must inherit from {self._base_class.__name__}"
            )
        self._registry[name] = implementation
        
    def create(self, name: str, **kwargs) -> T:
        """Create instance of registered component."""
        if name not in self._registry:
            available = ", ".join(self._registry.keys())
            raise ValueError(
                f"{self._component_type} '{name}' not registered. "
                f"Available: {available}"
            )
        return self._registry[name](**kwargs)


# Create factory instances for your ABCs
from canvod.readers import GNSSDataReader
from canvod.grids import BaseGridBuilder
from canvod.vod import VODCalculator

ReaderFactory = ComponentFactory[GNSSDataReader](
    GNSSDataReader, "reader"
)
GridFactory = ComponentFactory[BaseGridBuilder](
    BaseGridBuilder, "grid_builder"
)
VODFactory = ComponentFactory[VODCalculator](
    VODCalculator, "vod_calculator"
)


# Register built-in implementations
from canvod.readers import Rnxv3Obs
from canvod.grids import EqualAreaGridBuilder, RegularGridBuilder
from canvod.vod import TauOmegaZerothOrder

ReaderFactory.register("rinex_v3", Rnxv3Obs)
GridFactory.register("equal_area", EqualAreaGridBuilder)
GridFactory.register("regular", RegularGridBuilder)
VODFactory.register("tau_omega", TauOmegaZerothOrder)
```

### Functional API Using Factories (NEW)

```python
# canvodpy/api.py (NEW)
from canvodpy.factories import ReaderFactory, GridFactory, VODFactory

def read_rinex(
    file_path: Path,
    *,
    reader_type: str = "rinex_v3",
    keep_vars: list[str] | None = None,
) -> xr.Dataset:
    """Read RINEX file using registered reader.
    
    Parameters
    ----------
    file_path : Path
        Path to RINEX file
    reader_type : str, default "rinex_v3"
        Registered reader type. Built-in:
        - "rinex_v3": RINEX v3.04 reader
        Custom readers can be registered via ReaderFactory
        
    Examples
    --------
    >>> obs = read_rinex("data.rnx", reader_type="rinex_v3")
    
    Custom reader:
    >>> class MyReader(GNSSDataReader):  # Must inherit ABC!
    ...     def to_ds(self, keep_rnx_data_vars=None):
    ...         # Custom implementation
    ...         return xr.Dataset(...)
    >>> 
    >>> ReaderFactory.register("my_format", MyReader)
    >>> obs = read_rinex("data.dat", reader_type="my_format")
    """
    reader = ReaderFactory.create(reader_type)
    reader_instance = reader(fpath=file_path, include_auxiliary=False)
    return reader_instance.to_ds(keep_rnx_data_vars=keep_vars)


def create_grid(
    resolution: float,
    *,
    grid_type: str = "equal_area",
    **kwargs,
) -> GridData:
    """Create hemisphere grid using registered builder.
    
    Parameters
    ----------
    resolution : float
        Angular resolution in degrees
    grid_type : str, default "equal_area"
        Registered grid type. Built-in:
        - "equal_area": Equal solid angle cells
        - "regular": Regular lat-lon grid
        
    Examples
    --------
    >>> grid = create_grid(5.0, grid_type="equal_area")
    
    Custom grid:
    >>> class MyGrid(BaseGridBuilder):  # Must inherit ABC!
    ...     def _build_grid(self):
    ...         # Custom implementation
    ...         return grid_df, theta_lims, phi_lims, cell_ids
    ...     
    ...     def get_grid_type(self):
    ...         return "my_grid"
    >>> 
    >>> GridFactory.register("my_grid", MyGrid)
    >>> grid = create_grid(5.0, grid_type="my_grid")
    """
    builder = GridFactory.create(grid_type, angular_resolution=resolution, **kwargs)
    return builder.build()


def calculate_vod(
    canopy: xr.Dataset,
    reference: xr.Dataset,
    *,
    method: str = "tau_omega",
    **kwargs,
) -> xr.Dataset:
    """Calculate VOD using registered calculator.
    
    Parameters
    ----------
    canopy : xr.Dataset
        Canopy observations (aggregated per cell)
    reference : xr.Dataset
        Reference observations (aggregated per cell)
    method : str, default "tau_omega"
        Registered calculator. Built-in:
        - "tau_omega": Tau-omega zeroth order model
        
    Examples
    --------
    >>> vod = calculate_vod(canopy_agg, reference_agg)
    
    Custom calculator:
    >>> class MyVOD(VODCalculator):  # Must inherit ABC + Pydantic!
    ...     def calculate_vod(self):
    ...         # Custom implementation
    ...         return xr.Dataset(...)
    >>> 
    >>> VODFactory.register("my_model", MyVOD)
    >>> vod = calculate_vod(canopy, reference, method="my_model")
    """
    calculator = VODFactory.create(
        method, 
        canopy_ds=canopy, 
        sky_ds=reference,
        **kwargs
    )
    return calculator.calculate_vod()
```

---

## User Extension Example

### Custom RINEX Reader (Must Inherit ABC)

```python
# user_extensions.py
from canvod.readers import GNSSDataReader
from canvodpy import ReaderFactory
import xarray as xr
from pathlib import Path

class RinexV2Reader(GNSSDataReader):
    """Custom RINEX v2 reader - inherits ABC."""
    
    def __init__(self, fpath: Path, include_auxiliary: bool = False):
        self.fpath = fpath
        self.include_auxiliary = include_auxiliary
    
    def to_ds(self, keep_rnx_data_vars=None, **kwargs) -> xr.Dataset:
        """Implement ABC's abstract method."""
        # Parse RINEX v2 format (different than v3)
        data = self._parse_rinex_v2(self.fpath)
        
        # Must return Dataset with required structure:
        # - Dimensions: (epoch, sid)
        # - Coordinates: epoch, sid, sv, system, band, code, freq_*
        # - Data vars: C1C, L1C, S1C, etc.
        return xr.Dataset(...)
    
    def _parse_rinex_v2(self, fpath):
        # Custom v2 parsing logic
        ...

# Register it
ReaderFactory.register("rinex_v2", RinexV2Reader)

# Use it immediately
from canvodpy import read_rinex
obs = read_rinex("old_data.rnx", reader_type="rinex_v2")
```

### Custom VOD Calculator (Must Inherit ABC + Pydantic)

```python
from canvod.vod import VODCalculator
from canvodpy import VODFactory
import xarray as xr

class DirectSNRDifference(VODCalculator):
    """Simple SNR difference - no tau-omega model."""
    
    # Inherits Pydantic validation from ABC!
    # canopy_ds and sky_ds validated automatically
    
    def calculate_vod(self) -> xr.Dataset:
        """Implement ABC's abstract method."""
        # Simple SNR difference
        snr_canopy = self.canopy_ds.SNR.mean(dim='epoch')
        snr_reference = self.sky_ds.SNR.mean(dim='epoch')
        
        vod = snr_reference - snr_canopy  # dB difference
        
        return xr.Dataset({
            'vod': vod,
            'phi': self.canopy_ds.phi.mean(dim='epoch'),
            'theta': self.canopy_ds.theta.mean(dim='epoch'),
        })

# Register it
VODFactory.register("direct_snr", DirectSNRDifference)

# Use it
from canvodpy import calculate_vod
vod = calculate_vod(canopy, reference, method="direct_snr")
```

---

## Benefits of This Approach

✅ **Keep your ABCs** - No refactoring needed, they're well-designed
✅ **ABC benefits preserved** - Shared code, validation, isinstance() checks
✅ **Factory extensibility** - Users register new implementations
✅ **Type safety** - Factory validates inheritance from ABC
✅ **Pydantic integration** - Your VODCalculator(ABC, BaseModel) keeps working!
✅ **Functional API** - Simple functions for Airflow
✅ **Consistency** - Matches your existing architecture

---

## Why Not Protocols?

**Protocols are great, but you don't need them because:**

1. Your ABCs have **shared implementation** (BaseGridBuilder.__init__)
2. Your ABCs have **Pydantic validation** (VODCalculator validates datasets)
3. You **want to enforce inheritance** (readers must follow structure)
4. You're building **internal architecture** (not third-party plugins)

**Protocols shine when:**
- No shared code (pure interface)
- Can't modify classes (third-party)
- Want true duck typing

**Your ABCs shine when:**
- Shared initialization/methods ✅
- Data validation needed ✅  
- Want to ensure correct inheritance ✅
- Combine with Pydantic ✅

---

## Implementation Order

1. ✅ **Factory classes** (`canvodpy/factories.py`)
   - ComponentFactory with ABC validation
   - ReaderFactory, GridFactory, VODFactory
   - Register built-in implementations

2. ✅ **Functional API** (`canvodpy/api.py`)
   - read_rinex() using ReaderFactory
   - create_grid() using GridFactory
   - calculate_vod() using VODFactory
   - process_rinex() (full pipeline)
   - assign_to_grid(), aggregate_cells()

3. ✅ **Examples**
   - Basic workflow
   - Custom reader (inherits ABC)
   - Custom VOD calculator (inherits ABC + Pydantic)
   - Airflow DAG

4. ✅ **Tests**
   - Factory registration
   - ABC inheritance validation
   - API functions

---

## Summary

**Keep ABCs + Add Factories = Best of Both Worlds**

Your ABCs are good architecture. Don't replace them with Protocols.
Instead, add a Factory layer on top for user extensibility + functional API.

This gives you:
- Strong contracts (ABC enforcement)
- Shared code (ABC base classes)
- Validation (Pydantic integration)
- Extensibility (Factory registration)
- Simple API (functional wrappers)

Should I implement this revised plan?
