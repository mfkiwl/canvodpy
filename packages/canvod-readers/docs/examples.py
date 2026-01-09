import marimo

__generated_with = "0.19.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md("""
    # canvod-readers Examples

    GNSS data format readers for the canVODpy ecosystem.

    This package provides readers for various GNSS data formats, with a focus on RINEX v3.04 observation files.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Installation

    ```bash
    uv pip install canvod-readers
    ```

    For development:
    ```bash
    git clone https://github.com/nfb2021/canvodpy.git
    cd canvodpy
    uv sync
    ```
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Import the Package
    """)
    return


@app.cell
def _():
    from pathlib import Path

    from canvod.readers import Rnxv3Obs
    return Path, Rnxv3Obs


@app.cell
def _(mo):
    mo.md(r"""
    ## Reading RINEX v3.04 Files

    The main class for reading RINEX v3.04 observation files is `Rnxv3Obs`.
    It automatically parses the header and validates the file structure.
    """)
    return


@app.cell
def _(Path, Rnxv3Obs):
    # Example file path (adjust to your actual data location)
    rinex_file = Path(
        "tests/test_data/01_Rosalia/01_reference/01_GNSS/01_raw/25001/rref001a00.25o"
    )

    # Check if file exists
    if rinex_file.exists():
        # Create reader instance by passing the file path
        reader = Rnxv3Obs(fpath=rinex_file)
        print(f"✓ Successfully loaded: {rinex_file.name}")
        print(f"✓ RINEX version: {reader.header.version}")
        print(f"✓ Marker name: {reader.header.marker_name}")
        print(f"✓ Systems: {reader.header.systems}")
    else:
        print(f"✗ File not found: {rinex_file}")
        reader = None
    return (reader,)


@app.cell
def _(mo):
    mo.md(r"""
    ## Header Information

    The RINEX header contains important metadata about the observation file.
    """)
    return


@app.cell
def _(reader):
    if reader:
        # Access header information
        header = reader.header

        print("Header Information:")
        print(f"  Observer: {header.observer}")
        print(f"  Agency: {header.agency}")
        print(f"  Receiver: {header.receiver_type}")
        print(f"  Antenna: {header.antenna_type}")
        print(f"  Position: {header.approx_position}")
        print(f"  First observation: {header.t0}")
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Convert to xarray Dataset

    The `to_ds()` method converts RINEX observations into an xarray Dataset
    with proper metadata and coordinates.
    """)
    return


@app.cell
def _(reader):
    if reader:
        # Convert to xarray Dataset with signal IDs
        ds = reader.to_ds(
            keep_rnx_data_vars=["SNR"],  # Keep only SNR observations
            write_global_attrs=True,  # Include comprehensive metadata
        )
        print(ds)
    else:
        ds = None
    return (ds,)


@app.cell
def _(ds, mo):
    if ds:
        mo.md(f"""
            ## Dataset Structure

            The dataset has dimensions:
            - **epochs**: {len(ds.epoch)} time steps
            - **signal IDs**: {len(ds.sid)} unique GNSS signals

            Each signal ID has the format: `SV|BAND|CODE` (e.g., `G01|L1|C` for GPS PRN 01, L1 band, C/A code)
            """)
    return


@app.cell
def _(ds):
    if ds:
        # Examine signal IDs
        print("Sample signal IDs:")
        for sid in ds.sid.values[:10]:
            print(f"  {sid}")
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Filtering Data

    You can filter the dataset by system, band, or code.
    """)
    return


@app.cell
def _(ds):
    if ds:
        # Filter by GNSS system
        gps_only = ds.where(ds.system == 'G', drop=True)
        print(f"GPS signals: {len(gps_only.sid)}")

        # Filter by frequency band
        l1_signals = ds.where(ds.band == 'L1', drop=True)
        print(f"L1 band signals: {len(l1_signals.sid)}")

        # Filter by code type
        ca_code = ds.where(ds.code == 'C', drop=True)
        print(f"C/A code signals: {len(ca_code.sid)}")
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Epoch Iteration

    For memory-efficient processing, you can iterate through epochs:
    """)
    return


@app.cell
def _(reader):
    if reader:
        # Iterate through first 5 epochs
        for i, epoch in enumerate(reader.iter_epochs()):
            if i >= 5:
                break
            print(
                f"Epoch {i}: {epoch.info.year}-{epoch.info.month:02d}-{epoch.info.day:02d} "
                f"{epoch.info.hour:02d}:{epoch.info.minute:02d}:{epoch.info.seconds:02d}"
            )
            print(f"  Satellites: {len(list(epoch.data))}")
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Validation

    The reader automatically validates epoch completeness:
    """)
    return


@app.cell
def _(reader):
    if reader:
        try:
            # Validate that all expected epochs are present
            reader.validate_epoch_completeness(
                sampling_interval="30 s",  # Expected sampling rate
                dump_interval="15 min"  # Expected file duration
            )
            print("✓ All epochs present and valid")
        except Exception as e:
            print(f"✗ Validation error: {e}")
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Summary

    Key features of `canvod-readers`:

    - **Automatic validation**: Header parsing and file structure validation
    - **Signal IDs**: Unique identifiers for each GNSS signal
    - **xarray integration**: Convert to xarray Datasets for analysis
    - **Memory efficient**: Lazy iteration through epochs
    - **Flexible filtering**: Filter by system, band, or code
    - **Metadata rich**: Comprehensive attributes and coordinates

    For more information, see the [API documentation](../README.md).
    """)
    return


if __name__ == "__main__":
    app.run()
