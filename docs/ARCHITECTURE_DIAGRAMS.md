# CANVODPY Architecture Diagrams

> **Beautiful Mermaid diagrams for the CANVODPY GNSS VOD processing pipeline**

This document provides comprehensive visual architecture documentation using Mermaid diagrams.
View with [beautiful-mermaid](https://github.com/lukilabs/beautiful-mermaid) or [Mermaid Live Editor](https://mermaid.live).

---

## 📦 Package Structure Overview

```mermaid
graph TB
    subgraph "User Interface"
        Config["🔧 Configuration<br/>.env, YAML files"]
    end

    subgraph "Umbrella Package"
        Canvodpy["📦 canvodpy<br/>Orchestrator & API"]
    end

    subgraph "Core Processing Packages"
        Readers["📖 canvod-readers<br/>RINEX v3.04 Parsing"]
        Aux["📡 canvod-auxiliary<br/>SP3/CLK/Position"]
        Store["💾 canvod-store<br/>Icechunk Storage"]
        Utils["🛠️ canvod-utils<br/>Config & Tools"]
    end

    subgraph "Analysis & Output Packages"
        VOD["🌳 canvod-vod<br/>VOD Calculator"]
        Grids["🔲 canvod-grids<br/>Hemisphere Grids"]
        Viz["📊 canvod-viz<br/>2D/3D Visualization"]
    end

    Config --> Canvodpy
    Canvodpy --> Readers
    Canvodpy --> Aux
    Canvodpy --> Store
    Canvodpy --> VOD
    Canvodpy --> Grids
    Canvodpy --> Viz

    Readers --> Utils
    Aux --> Readers
    Aux --> Utils
    Store --> Aux
    Store --> Readers
    Store --> Utils
    Grids --> Store
    Grids --> Utils
    Viz --> Grids

    style Canvodpy fill:#e1f5ff,stroke:#01579b,stroke-width:3px
    style Readers fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style Aux fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style Store fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style VOD fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    style Grids fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    style Viz fill:#e0f2f1,stroke:#004d40,stroke-width:2px
    style Utils fill:#fce4ec,stroke:#880e4f,stroke-width:2px
```

---

## 🔄 Data Processing Pipeline

```mermaid
flowchart TD
    Start([🚀 Start Processing]) --> Input

    subgraph Input["📥 Data Ingestion"]
        RINEX["📄 RINEX Files<br/>(Observations)"]
        SP3["🛰️ SP3 Files<br/>(Orbits)"]
        CLK["⏰ CLK Files<br/>(Clocks)"]
    end

    subgraph Reading["🔍 Reading & Parsing"]
        RinexReader["Rnxv3Obs<br/>Parse RINEX v3.04"]
        AuxReader["SP3/CLK Parsers<br/>Load Auxiliary Data"]
    end

    subgraph Processing["⚙️ Processing"]
        Interp["Interpolation<br/>Orbit/Clock to Obs Times"]
        Position["Position Calculation<br/>ECEF → Spherical (r,θ,φ)"]
        Augment["Dataset Augmentation<br/>Merge RINEX + Aux"]
    end

    subgraph Storage["💾 Storage"]
        Icechunk["Icechunk Store<br/>Versioned Datasets"]
    end

    subgraph Analysis["📊 Analysis"]
        GridAssign["Grid Assignment<br/>Map to Hemisphere Cells"]
        VODCalc["VOD Calculation<br/>Tau-Omega Model"]
        Aggregate["Aggregation<br/>Per-cell Statistics"]
    end

    subgraph Output["📈 Output"]
        Viz2D["2D Hemisphere Plots<br/>Polar Projection"]
        Viz3D["3D Interactive Plots<br/>Plotly Surface"]
        Export["Data Export<br/>NetCDF/CSV"]
    end

    RINEX --> RinexReader
    SP3 --> AuxReader
    CLK --> AuxReader

    RinexReader --> Augment
    AuxReader --> Interp
    Interp --> Position
    Position --> Augment

    Augment --> Icechunk
    Icechunk --> GridAssign
    GridAssign --> VODCalc
    VODCalc --> Aggregate

    Aggregate --> Viz2D
    Aggregate --> Viz3D
    Aggregate --> Export

    Viz2D --> End([✅ Complete])
    Viz3D --> End
    Export --> End

    style Start fill:#4caf50,stroke:#1b5e20,stroke-width:3px,color:#fff
    style End fill:#4caf50,stroke:#1b5e20,stroke-width:3px,color:#fff
    style Input fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style Reading fill:#ffecb3,stroke:#f57c00,stroke-width:2px
    style Processing fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    style Storage fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style Analysis fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style Output fill:#e0f2f1,stroke:#00695c,stroke-width:2px
```

---

## 🏗️ Package Dependencies (Detailed)

```mermaid
graph LR
    subgraph Foundation["🔧 Foundation Layer"]
        Utils["canvod-utils<br/>━━━━━━━━<br/>• Config<br/>• YYYYDOY<br/>• Tools"]
    end

    subgraph DataIO["📥 Data I/O Layer"]
        Readers["canvod-readers<br/>━━━━━━━━<br/>• Rnxv3Obs<br/>• SignalID<br/>• DataDir"]
        Aux["canvod-auxiliary<br/>━━━━━━━━<br/>• SP3<br/>• CLK<br/>• Interpolator"]
    end

    subgraph Storage["💾 Storage Layer"]
        Store["canvod-store<br/>━━━━━━━━<br/>• Icechunk<br/>• ResearchSite<br/>• Reader"]
    end

    subgraph Computation["🧮 Computation Layer"]
        VOD["canvod-vod<br/>━━━━━━━━<br/>• VODCalculator<br/>• TauOmega"]
        Grids["canvod-grids<br/>━━━━━━━━<br/>• HEALPix<br/>• Geodesic<br/>• Fibonacci"]
    end

    subgraph Presentation["📊 Presentation Layer"]
        Viz["canvod-viz<br/>━━━━━━━━<br/>• 2D Plots<br/>• 3D Surface<br/>• Styles"]
    end

    subgraph Orchestration["🎯 Orchestration Layer"]
        Canvodpy["canvodpy<br/>━━━━━━━━<br/>• Pipeline<br/>• Processor<br/>• API"]
    end

    Readers -.->|uses| Utils
    Aux -.->|uses| Readers
    Aux -.->|uses| Utils
    Store -.->|uses| Aux
    Store -.->|uses| Readers
    Store -.->|uses| Utils
    Grids -.->|optional| Store
    Grids -.->|uses| Utils
    Viz -.->|uses| Grids

    Canvodpy ==>|coordinates| Readers
    Canvodpy ==>|coordinates| Aux
    Canvodpy ==>|coordinates| Store
    Canvodpy ==>|coordinates| VOD
    Canvodpy ==>|coordinates| Grids
    Canvodpy ==>|coordinates| Viz

    style Utils fill:#fce4ec,stroke:#880e4f,stroke-width:3px
    style Readers fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style Aux fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style Store fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style VOD fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    style Grids fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    style Viz fill:#e0f2f1,stroke:#004d40,stroke-width:2px
    style Canvodpy fill:#e3f2fd,stroke:#0d47a1,stroke-width:4px
```

---

## 🎯 Orchestrator Component Architecture

```mermaid
graph TB
    subgraph API["🌐 Public API (canvodpy)"]
        Site["Site<br/>━━━━<br/>Wrapper around<br/>GnssResearchSite"]
        Pipeline["Pipeline<br/>━━━━<br/>High-level<br/>processing"]
        Functions["Functions<br/>━━━━<br/>process_date()<br/>calculate_vod()"]
    end

    subgraph Core["⚙️ Orchestrator Core"]
        PipelineOrch["PipelineOrchestrator<br/>━━━━━━━━<br/>• Multi-date coordination<br/>• Parallel execution<br/>• Progress tracking"]
        Processor["RinexDataProcessor<br/>━━━━━━━━<br/>• RINEX → Dataset<br/>• Aux augmentation<br/>• Icechunk write"]
        Matcher["DatasetMatcher<br/>━━━━━━━━<br/>• Canopy/Reference<br/>• SID alignment"]
    end

    subgraph Backend["💾 Backend Services"]
        StoreService["GnssResearchSite<br/>━━━━━━━━<br/>• Multi-receiver<br/>• Version control"]
        ReaderService["IcechunkDataReader<br/>━━━━━━━━<br/>• Lazy loading<br/>• Preprocessing"]
    end

    Site --> PipelineOrch
    Pipeline --> PipelineOrch
    Functions --> PipelineOrch

    PipelineOrch --> Processor
    PipelineOrch --> Matcher

    Processor --> StoreService
    Matcher --> ReaderService
    ReaderService --> StoreService

    style Site fill:#bbdefb,stroke:#1565c0,stroke-width:2px
    style Pipeline fill:#bbdefb,stroke:#1565c0,stroke-width:2px
    style Functions fill:#bbdefb,stroke:#1565c0,stroke-width:2px
    style PipelineOrch fill:#c5e1a5,stroke:#558b2f,stroke-width:3px
    style Processor fill:#c5e1a5,stroke:#558b2f,stroke-width:2px
    style Matcher fill:#c5e1a5,stroke:#558b2f,stroke-width:2px
    style StoreService fill:#f8bbd0,stroke:#c2185b,stroke-width:2px
    style ReaderService fill:#f8bbd0,stroke:#c2185b,stroke-width:2px
```

---

## 🔬 VOD Calculation Workflow

```mermaid
sequenceDiagram
    participant User
    participant Pipeline as PipelineOrchestrator
    participant Store as GnssResearchSite
    participant VODCalc as VODCalculator
    participant Grid as HemiGrid
    participant Viz as Visualizer

    User->>Pipeline: calculate_vod("site", "canopy", "ref", date)

    Pipeline->>Store: Load canopy dataset
    Store-->>Pipeline: Canopy Dataset (φ, θ, SNR)

    Pipeline->>Store: Load reference dataset
    Store-->>Pipeline: Reference Dataset (φ, θ, SNR)

    Pipeline->>VODCalc: calculate(canopy_ds, ref_ds)

    VODCalc->>VODCalc: Apply Tau-Omega Model<br/>τ = -ln(SNR_canopy/SNR_ref)

    VODCalc-->>Pipeline: VOD Dataset (τ per sid, epoch)

    Pipeline->>Grid: assign_cells(vod_ds)
    Grid->>Grid: Map (φ,θ) → cell_id
    Grid-->>Pipeline: Gridded VOD

    Pipeline->>Viz: plot_hemisphere(gridded_vod)
    Viz-->>User: 📊 2D/3D Visualization

    Note over User,Viz: Complete VOD workflow<br/>from raw RINEX to visualization
```

---

## 📊 Grid System Architecture

```mermaid
classDiagram
    class GridData {
        +DataFrame cells
        +DataFrame vertices
        +int n_cells
        +create_hemigrid()
        +assign_cell_ids()
        +aggregate()
    }

    class HEALPixGrid {
        +int nside
        +hierarchical indexing
    }

    class GeodesicGrid {
        +int subdivision_level
        +icosahedron base
    }

    class FibonacciGrid {
        +int n_points
        +golden ratio spiral
    }

    class EqualAreaGrid {
        +float cell_area
        +uniform density
    }

    class HTMGrid {
        +int depth
        +recursive triangles
    }

    class GridFactory {
        +create_hemigrid(type, params)
    }

    GridData <|-- HEALPixGrid
    GridData <|-- GeodesicGrid
    GridData <|-- FibonacciGrid
    GridData <|-- EqualAreaGrid
    GridData <|-- HTMGrid

    GridFactory ..> GridData : creates

    note for GridData "All grids store:\n• Cell centroids (φ,θ)\n• Vertices (polygons)\n• Neighbor relations"
    note for HEALPixGrid "Default grid for\nastrophysics/CMB"
    note for FibonacciGrid "Uniform distribution\nvia golden spiral"
```

---

## 🔐 Storage & Versioning

```mermaid
stateDiagram-v2
    [*] --> RawData: RINEX + SP3/CLK

    state "Processing" as Proc {
        [*] --> Parse
        Parse --> Augment: Add auxiliary data
        Augment --> Validate: Check integrity
    }

    RawData --> Proc

    state "Icechunk Storage" as Store {
        state "Branch: main" as Main {
            [*] --> Snapshot1
            Snapshot1 --> Snapshot2: Append data
            Snapshot2 --> Snapshot3: Update
        }

        state "Branch: experiment" as Exp {
            Snapshot2 --> ExpSnap1: Fork
            ExpSnap1 --> ExpSnap2: Test algorithm
        }
    }

    Proc --> Store: Write versioned dataset

    state "Analysis" as Analysis {
        [*] --> LoadData
        LoadData --> VOD: Calculate VOD
        LoadData --> GridAssign: Assign to grid
        VOD --> Export
        GridAssign --> Export
    }

    Store --> Analysis: Read snapshot

    Analysis --> [*]: Results

    note right of Store
        Immutable snapshots
        Branch for experiments
        Time-travel debugging
    end note
```

---

## 🚀 Performance Optimization Targets

```mermaid
mindmap
  root((Performance<br/>Optimization))
    I/O Operations
      Metadata Writes
        **CRITICAL**
        Batch writes
        100+ files
        Save 20-30s
      RINEX Validation
        Parallel validation
        Fast pre-checks
        Cache results
        Save 5-15s
    Memory Management
      Dataset Copying
        Avoid .copy()
        Selective attrs
        50-200ms/file
      .values Calls
        Use vectorized ops
        Lazy evaluation
        5-10% memory
    Parallelization
      Nested ThreadPools
        **LOW PRIORITY**
        Once per 24h
        Minimal impact
```

---

## 📐 Spherical Coordinate System

```mermaid
graph TD
    subgraph "Navigation Convention"
        North["φ = 0°<br/>North"]
        East["φ = 90°<br/>East"]
        South["φ = 180°<br/>South"]
        West["φ = 270°<br/>West"]
    end

    subgraph "Polar Angle θ"
        Zenith["θ = 0°<br/>Zenith<br/>(straight up)"]
        Horizon["θ = 90°<br/>Horizon"]
        Below["θ > 90°<br/>Below horizon<br/>(NaN)"]
    end

    subgraph "ENU Frame"
        E["East (e)"]
        N["North (n)"]
        U["Up (u)"]
    end

    E --> |arctan2| Phi["φ = arctan2(e, n)"]
    N --> |arctan2| Phi
    U --> |arccos| Theta["θ = arccos(u/r)"]

    Phi --> North
    Theta --> Zenith

    style North fill:#4caf50,stroke:#1b5e20,color:#fff
    style Zenith fill:#2196f3,stroke:#0d47a1,color:#fff
    style Below fill:#f44336,stroke:#b71c1c,color:#fff
```

---

## 📝 Key Architectural Principles

1. **🔹 Namespace Package Pattern**: All packages use `canvod.*` namespace for clean separation
2. **🔹 Lazy Imports**: Umbrella package uses `__getattr__` to avoid circular dependencies
3. **🔹 Independent Packages**: Each `canvod-*` can be used standalone
4. **🔹 Configuration-Driven**: YAML configs and `.env` for reproducibility
5. **🔹 Versioned Storage**: Icechunk enables time-travel debugging
6. **🔹 Parallel-Ready**: PipelineOrchestrator supports configurable workers
7. **🔹 Type-Safe**: Modern Python with type hints throughout

---

## 🎨 Viewing These Diagrams

For best results, view these diagrams using:
- **[beautiful-mermaid](https://github.com/lukilabs/beautiful-mermaid)** - Beautiful rendering ⭐
- **[Mermaid Live Editor](https://mermaid.live)** - Interactive editing
- **GitHub** - Native Mermaid support in Markdown
- **VS Code** - Mermaid preview extensions

---

*Generated: 2026-02-02 | CANVODPY Architecture Documentation v1.0*
