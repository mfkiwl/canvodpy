# Build Backend: 100% uv-based Solution ✅

## Final Configuration: uv_build with Namespace Packages

Thanks to discovering the `module-name` configuration in uv_build, we achieved a **pure uv solution**!

### Configuration

Each namespace package uses:

```toml
[build-system]
requires = ["uv_build>=0.9.17,<0.10.0"]
build-backend = "uv_build"

[tool.uv.build-backend]
module-name = "canvod.readers"  # Dotted name = namespace package
```

### Structure

```
packages/canvod-readers/
  src/
    canvod/                 # NO __init__.py (PEP 420 implicit)
      readers/
        __init__.py        # Regular package
```

### How It Works

From [uv build backend docs](https://docs.astral.sh/uv/concepts/build-backend/):

> "Namespace packages are intended for use-cases where multiple packages write modules into a shared namespace. Namespace package modules are identified by a `.` in the module-name."

**Key insight:** The `.` (dot) in `module-name = "canvod.readers"` tells uv_build this is a namespace package.

### All Packages

- `canvod-readers` → `module-name = "canvod.readers"`
- `canvod-aux` → `module-name = "canvod.aux"`
- `canvod-grids` → `module-name = "canvod.grids"`
- `canvod-vod` → `module-name = "canvod.vod"`
- `canvod-store` → `module-name = "canvod.store"`
- `canvod-viz` → `module-name = "canvod.viz"`
- `canvodpy` → Regular package (no namespace)

### Benefits

✅ **100% uv-based** - No setuptools or hatchling needed
✅ **Follows TUW-GEO standards** - Uses uv_build as intended
✅ **PEP 420 compliant** - Modern implicit namespace packages
✅ **Works perfectly** - All imports functional

### Working Imports

```python
from canvod.readers import Rnxv3Obs
from canvod.aux import AuxData
from canvod.grids import HemiGrid
import canvodpy
```

## Thanks to GitHub Issue #6575

The solution was documented in uv's build backend documentation but the GitHub issue helped find it.
