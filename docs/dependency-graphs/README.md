# Dependency Graphs

Visual dependency analysis for canVODpy packages.

## Package-Level Dependencies (Internal)

Shows how classes and modules import each other within each package:

### canvod-readers

![canvod-readers internal dependencies](canvod-readers-internal.svg)

### canvod-aux

![canvod-aux internal dependencies](canvod-aux-internal.svg)

### canvod-grids

![canvod-grids internal dependencies](canvod-grids-internal.svg)

### canvod-vod

![canvod-vod internal dependencies](canvod-vod-internal.svg)

### canvod-store

![canvod-store internal dependencies](canvod-store-internal.svg)

### canvod-viz

![canvod-viz internal dependencies](canvod-viz-internal.svg)

### canvod-utils

![canvod-utils internal dependencies](canvod-utils-internal.svg)

## API Orchestration

Shows how the umbrella package (canvodpy) orchestrates all components:

![API Orchestration](api-orchestration.svg)

## Configuration Flow

Shows how configuration flows through the system:

![Config Flow](config-flow.svg)

## Regenerating Graphs

```bash
# Regenerate all graphs
python scripts/generate_dependency_graphs.py --all

# Regenerate specific package
python scripts/generate_dependency_graphs.py --package canvod-readers

# Regenerate API graph only
python scripts/generate_dependency_graphs.py --api
```

## Reading the Graphs

- **Arrows** show import direction (A → B means A imports B)
- **Clusters** group related modules together
- **Colors** distinguish different modules/packages

**Generated:** Auto-updated during development