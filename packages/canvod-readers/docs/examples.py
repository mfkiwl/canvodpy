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
            keep_rnx_data_vars=["SNR", "Doppler", "Phase", "Pseudorange"],  # Keep only SNR observations
            write_global_attrs=True,  # Include comprehensive metadata
        )
        print(ds)
    else:
        ds = None
    return (ds,)


@app.cell
def _(ds):
    ds
    return


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
                f"Epoch {i}: {epoch.info.year}-{epoch.info.month}-{epoch.info.day} "
                f"{epoch.info.hour}:{epoch.info.minute}:{epoch.info.seconds}"
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


@app.cell
def _():
    import xarray as xr

    # See the version
    print(f"xarray version: {xr.__version__}")

    # See the installation location
    print(f"xarray location: {xr.__file__}")
    return (xr,)


@app.cell
def _(ds, mo):
    import numpy as np
    import plotly.graph_objects as go

    def _sorted_unique_str(a):
        return sorted(set(str(x) for x in np.asarray(a).tolist()))

    vars_ = list(ds.data_vars)
    var = mo.ui.dropdown(vars_, value=("SNR" if "SNR" in vars_ else vars_[0]), label="Variable")

    system = mo.ui.dropdown(["All"] + _sorted_unique_str(ds["system"].values), value="All", label="System")
    band   = mo.ui.dropdown(["All"] + _sorted_unique_str(ds["band"].values),   value="All", label="Band")
    code   = mo.ui.dropdown(["All"] + _sorted_unique_str(ds["code"].values),   value="All", label="Code")
    sv     = mo.ui.dropdown(["All"] + _sorted_unique_str(ds["sv"].values),     value="All", label="SV")

    epoch_range = mo.ui.range_slider(
        start=0,
        stop=ds.sizes["epoch"] - 1,
        value=(0, ds.sizes["epoch"] - 1),
        step=1,
        label="Epoch range (index)",
    )

    controls = mo.vstack(
        [
            mo.hstack([var, system, band, code, sv], gap=1),
            epoch_range,
        ],
        gap=1,
    )

    controls
    return band, code, epoch_range, go, sv, system, var


@app.cell
def _(band, code, ds, epoch_range, mo, sv, system, xr):
    def _filter_ds(ds, system, band, code, sv):
        mask = xr.ones_like(ds["sid"], dtype=bool)
        if system != "All":
            mask &= (ds["system"] == system)
        if band != "All":
            mask &= (ds["band"] == band)
        if code != "All":
            mask &= (ds["code"] == code)
        if sv != "All":
            mask &= (ds["sv"] == sv)
        return ds.sel(sid=ds["sid"].where(mask, drop=True))

    def _slice_epoch(ds, i0, i1):
        i0, i1 = sorted((int(i0), int(i1)))
        i0 = max(i0, 0)
        i1 = min(i1, ds.sizes["epoch"] - 1)
        return ds.isel(epoch=slice(i0, i1 + 1))

    ds_f = _slice_epoch(
        _filter_ds(ds, system.value, band.value, code.value, sv.value),
        *epoch_range.value
    )

    sid_list = [str(x) for x in ds_f["sid"].values.tolist()]
    sid_pick = mo.ui.dropdown(
        sid_list,
        value=(sid_list[0] if sid_list else None),
        label="sid (timeseries)",
    )

    # return the widget so it renders
    sid_pick
    return ds_f, sid_pick


@app.cell
def _(ds_f, go, mo, sid_pick, var):
    def _heatmap_fig(ds_f, varname):
        Z = ds_f[varname].transpose("sid", "epoch").values
        X = ds_f["epoch"].values
        Y = ds_f["sid"].values
        fig = go.Figure(
            go.Heatmap(
                z=Z, x=X, y=Y,
                hovertemplate="epoch=%{x}<br>sid=%{y}<br>value=%{z}<extra></extra>",
            )
        )
        fig.update_layout(
            height=420,
            margin=dict(l=10, r=10, t=35, b=10),
            title=f"{varname} — overview (sid × epoch)",
            xaxis_title="epoch",
            yaxis_title="sid",
        )
        return fig

    def _timeseries_fig(ds_f, varname, sid_value):
        da = ds_f.sel(sid=sid_value)[varname]
        fig = go.Figure(
            go.Scattergl(
                x=ds_f["epoch"].values,
                y=da.values,
                mode="lines+markers",
                hovertemplate="epoch=%{x}<br>value=%{y}<extra></extra>",
                name=str(sid_value),
            )
        )
        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=35, b=10),
            title=f"{varname} — {sid_value}",
            xaxis_title="epoch",
            yaxis_title=varname,
        )
        return fig

    if ds_f.sizes["sid"] == 0:
        stats = mo.md("**No signals match the current filters.**")
        hm = None
        ts = None
    else:
        da = ds_f[var.value]
        n_total = da.size
        n_valid = int(da.count().values)
        frac_nan = 1.0 - (n_valid / n_total if n_total else 0.0)

        stats = mo.md(
            f"""
    **Selection summary**
    - sids: `{ds_f.sizes["sid"]}` | epochs: `{ds_f.sizes["epoch"]}`
    - valid values: `{n_valid}` / `{n_total}` (NaN fraction ≈ `{frac_nan:.2%}`)
    """
        )
        hm = mo.ui.plotly(_heatmap_fig(ds_f, var.value))

        if sid_pick.value is None:
            ts = mo.md("_Select a sid to see the timeseries._")
        else:
            ts = mo.ui.plotly(_timeseries_fig(ds_f, var.value, sid_pick.value))

    if ds_f.sizes["sid"] == 0:
        stats = mo.md("**No signals match the current filters.**")
        hm = None
        ts = None
    else:
        da = ds_f[var.value]
        n_total = da.size
        n_valid = int(da.count().values)
        frac_nan = 1.0 - (n_valid / n_total if n_total else 0.0)

        stats = mo.md(
            f"""
    **Selection summary**
    - sids: `{ds_f.sizes["sid"]}` | epochs: `{ds_f.sizes["epoch"]}`
    - valid values: `{n_valid}` / `{n_total}` (NaN fraction ≈ `{frac_nan:.2%}`)
    """
        )

        hm = mo.ui.plotly(_heatmap_fig(ds_f, var.value))

        if sid_pick.value is None:
            ts = mo.md("_Select a sid to see the timeseries._")
        else:
            ts = mo.ui.plotly(_timeseries_fig(ds_f, var.value, sid_pick.value))

    parts = [stats]
    if hm is not None:
        parts.append(hm)
    if ts is not None:
        parts.append(ts)

    body = mo.vstack(parts, gap=1)
    body
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
