# canvod-vod

## Purpose

The `canvod-vod` package implements vegetation optical depth (VOD) estimation from GNSS signal-to-noise ratio (SNR) data. It provides the core scientific algorithms for the canVODpy analysis pipeline.

## Theoretical Background

The package implements the zeroth-order tau-omega radiative transfer model for GNSS-transmissometry, following Humphrey and Frankenberg (2022). In this model, the attenuation of GNSS signals passing through a vegetation canopy is related to the optical depth (tau) of the canopy layer.

The zeroth-order model assumes:
- Single-scattering approximation (no multiple scattering between canopy elements)
- Plane-parallel canopy layer
- Signal attenuation proportional to the path length through the canopy

## Multi-Receiver SCS Expansion

When a reference receiver serves multiple canopy receivers, its satellite geometry must be recomputed relative to each canopy position. The `scs_from` configuration controls this expansion, creating separate store groups and matched VOD analysis pairs.

```mermaid
flowchart TD
    subgraph FIELD["Field Setup"]
        C1["Canopy Receiver 1 (below canopy, NE)"]
        C2["Canopy Receiver 2 (below canopy, SW)"]
        R1["Reference Receiver (open sky)"]
    end

    subgraph SCS_CONFIG["SCS Configuration (sites.yaml)"]
        C1_CFG["canopy_01 type: canopy scs_from: null (uses own position)"]
        C2_CFG["canopy_02 type: canopy scs_from: null (uses own position)"]
        R1_CFG["reference_01 type: reference scs_from:   - canopy_01   - canopy_02"]
    end

    subgraph EXPANSION["SCS Processing Expansion"]
        C1_PROC["Process canopy_01 position: canopy_01"]
        C2_PROC["Process canopy_02 position: canopy_02"]
        R1_C1["Process reference_01 position: canopy_01 (satellite geometry relative to canopy_01)"]
        R1_C2["Process reference_01 position: canopy_02 (satellite geometry relative to canopy_02)"]
    end

    subgraph STORE_GROUPS["RINEX Store Groups"]
        SG1["canopy_01"]
        SG2["canopy_02"]
        SG3["reference_01_canopy_01"]
        SG4["reference_01_canopy_02"]
    end

    subgraph VOD_PAIRS["VOD Analysis Pairs"]
        VP1["canopy_01 vs reference_01_canopy_01"]
        VP2["canopy_02 vs reference_01_canopy_02"]
    end

    subgraph VOD_OUT["VOD Output"]
        V1["VOD (canopy_01) SNR attenuation by canopy at position 1"]
        V2["VOD (canopy_02) SNR attenuation by canopy at position 2"]
    end

    C1 --> C1_CFG
    C2 --> C2_CFG
    R1 --> R1_CFG

    C1_CFG --> C1_PROC
    C2_CFG --> C2_PROC
    R1_CFG --> R1_C1
    R1_CFG --> R1_C2

    C1_PROC --> SG1
    C2_PROC --> SG2
    R1_C1 --> SG3
    R1_C2 --> SG4

    SG1 --> VP1
    SG3 --> VP1
    SG2 --> VP2
    SG4 --> VP2

    VP1 --> V1
    VP2 --> V2
```

## Usage

### Direct instantiation

```python
from canvod.vod import TauOmegaZerothOrder

calculator = TauOmegaZerothOrder(canopy_ds=canopy_ds, sky_ds=sky_ds)
vod_result = calculator.calculate_vod()
```

### From aligned datasets

```python
from canvod.vod import TauOmegaZerothOrder

vod_result = TauOmegaZerothOrder.from_datasets(
    canopy_ds=canopy_ds,
    sky_ds=sky_ds,
    align=True,
)
```

### From Icechunk store

```python
from canvod.vod import TauOmegaZerothOrder

vod_result = TauOmegaZerothOrder.from_icechunkstore(
    icechunk_store_pth="path/to/store",
    canopy_group="canopy_01",
    sky_group="reference_01",
)
```

The calculator requires:

- **Canopy dataset** (`canopy_ds`): RINEX observations from a receiver beneath vegetation
- **Sky dataset** (`sky_ds`): RINEX observations from a nearby open-sky receiver
- Both datasets must contain an `SNR` data variable
- Both datasets should be augmented with spherical coordinates (from canvod-auxiliary) and assigned to grid cells (from canvod-grids)

## Output

`calculate_vod()` returns an `xr.Dataset` containing:

- `VOD` — vegetation optical depth values
- `phi` — azimuth angles (from canopy dataset)
- `theta` — polar angles from zenith (from canopy dataset)

## References

Humphrey, V. and Frankenberg, C. (2022). GNSS-transmissometry: A new approach for vegetation optical depth estimation. *Remote Sensing of Environment*.
