import marimo

__generated_with = "0.19.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import datetime
    import os
    import tempfile
    from pathlib import Path

    import numpy as np

    from canvod.aux.clock.reader import ClkFile
    from canvod.aux.core.downloader import FtpDownloader
    from canvod.aux.ephemeris.reader import Sp3File
    from canvod.aux.products import get_products_for_agency, list_agencies

    return (
        datetime,
        os,
        Path,
        tempfile,
        np,
        list_agencies,
        get_products_for_agency,
        Sp3File,
        ClkFile,
        FtpDownloader,
    )


@app.cell
def _(mo):
    mo.md("""
    # canvod-aux File Viewer

    Select file type, configure parameters, download, and view dataset.
    """)
    return


@app.cell
def _(mo):
    # File state - persists downloaded file object
    file_state = mo.state(None)
    return (file_state,)


@app.cell
def _(mo):
    mo.md("## 1. Select File Type")
    return


@app.cell
def _(mo):
    # File type selector
    file_type_selector = mo.ui.radio(
        options=["SP3 Ephemeris", "CLK Clock"],
        value="SP3 Ephemeris",
        label="File Type:",
    )
    file_type_selector
    return (file_type_selector,)


@app.cell
def _(mo):
    mo.md("## 2. Configure Download")
    return


@app.cell
def _(list_agencies, mo):
    # Agency selector
    _agencies = sorted(list_agencies())
    agency_selector = mo.ui.dropdown(
        options=_agencies, value="COD", label="Analysis Center:"
    )
    agency_selector
    return (agency_selector,)


@app.cell
def _(agency_selector, get_products_for_agency, mo):
    # Product selector (depends on agency)
    _products = get_products_for_agency(agency_selector.value)
    product_selector = mo.ui.dropdown(
        options=sorted(_products) if _products else [],
        value=sorted(_products)[0] if _products else None,
        label="Product Type:",
    )
    product_selector
    return (product_selector,)


@app.cell
def _(datetime, mo):
    # Date selector
    date_selector = mo.ui.date(value=datetime.date(2023, 9, 11), label="Date:")
    date_selector
    return (date_selector,)


@app.cell
def _(mo, os):
    # Server selector
    server_selector = mo.ui.radio(
        options=["ESA", "NASA+ESA"], value="ESA", label="FTP Server:"
    )

    _cddis_status = "✓ Enabled" if os.environ.get("CDDIS_MAIL") else "✗ Disabled"

    mo.vstack([server_selector, mo.md(f"*NASA CDDIS fallback: {_cddis_status}*")])
    return (server_selector,)


@app.cell
def _(mo):
    # Download button
    download_button = mo.ui.button(label="Download File", kind="success")
    download_button
    return (download_button,)


@app.cell
def _(
    ClkFile,
    FtpDownloader,
    Path,
    Sp3File,
    agency_selector,
    date_selector,
    download_button,
    file_state,
    file_type_selector,
    mo,
    os,
    product_selector,
    server_selector,
    tempfile,
):
    # Download handler - runs when button clicked
    _download_status = None

    if download_button.value:
        _download_dir = Path(tempfile.gettempdir()) / "canvod_aux_demo"
        _download_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Setup downloader
            _user_email = (
                os.environ.get("CDDIS_MAIL")
                if server_selector.value == "NASA+ESA"
                else None
            )
            _downloader = FtpDownloader(user_email=_user_email)

            # Download based on file type
            if file_type_selector.value == "SP3 Ephemeris":
                _file = Sp3File.from_datetime_date(
                    date=date_selector.value,
                    agency=agency_selector.value,
                    product_type=product_selector.value,
                    ftp_server="ftp://gssc.esa.int/gnss",
                    local_dir=_download_dir,
                    downloader=_downloader,
                )
            else:  # CLK Clock
                _file = ClkFile.from_datetime_date(
                    date=date_selector.value,
                    agency=agency_selector.value,
                    product_type=product_selector.value,
                    ftp_server="ftp://gssc.esa.int/gnss",
                    local_dir=_download_dir,
                    downloader=_downloader,
                )

            # Store in state
            file_state.value = _file

            _download_status = mo.md(f"""
            ✅ **Download Complete**

            - **File:** `{_file.fpath.name}`
            - **Path:** `{_file.fpath}`
            - **Agency:** {_file.agency}
            - **Product:** {_file.product_type}
            """)

        except Exception as _e:
            file_state.value = None
            _download_status = mo.callout(
                mo.md(f"**Download Failed:** {str(_e)[:400]}"), kind="danger"
            )
    else:
        if file_state.value is None:
            _download_status = mo.md("*Click Download to fetch file*")
        else:
            _download_status = mo.md(f"*Current file: `{file_state.value.fpath.name}`*")

    _download_status
    return


@app.cell
def _(file_state, mo):
    mo.md("---")

    if file_state.value is None:
        mo.md("*Download a file to view dataset*")
    else:
        mo.md("## 3. View Dataset")
    return


@app.cell
def _(file_state, mo):
    # Read button - only shown if file exists
    read_button = (
        mo.ui.button(label="Load Dataset", kind="success") if file_state.value else None
    )

    read_button if read_button else None
    return (read_button,)


@app.cell
def _(file_state, mo, read_button):
    # Dataset viewer - runs when read button clicked
    _dataset_view = None

    if read_button and read_button.value:
        if file_state.value is not None:
            try:
                _ds = file_state.value.data

                # Build info display
                _info_lines = [
                    f"**Dimensions:** {dict(_ds.sizes)}",
                    f"**Variables:** {', '.join(list(_ds.data_vars))}",
                    f"**Coordinates:** {', '.join(list(_ds.coords))}",
                ]

                # Add type-specific info
                if "epoch" in _ds.coords:
                    _info_lines.append(
                        f"**Time Range:** {_ds.epoch.values[0]} to {_ds.epoch.values[-1]}"
                    )

                if "sv" in _ds.sizes:
                    _info_lines.append(f"**Satellites:** {len(_ds.sv)}")

                if "clock_offset" in _ds.data_vars:
                    _min_clk = float(_ds.clock_offset.min())
                    _max_clk = float(_ds.clock_offset.max())
                    _info_lines.append(
                        f"**Clock Range:** {_min_clk:.6e} to {_max_clk:.6e} s"
                    )

                _dataset_view = mo.vstack(
                    [
                        mo.md("### Dataset Information"),
                        mo.md("\n\n".join(_info_lines)),
                        mo.md("### Attributes"),
                        mo.md(
                            "\n".join([f"- `{k}`: {v}" for k, v in _ds.attrs.items()])
                        ),
                    ]
                )

                print("\nFull Dataset:")
                print(_ds)

            except Exception as _e:
                _dataset_view = mo.callout(
                    mo.md(f"**Error loading dataset:** {str(_e)}"), kind="danger"
                )
    else:
        _dataset_view = (
            mo.md("*Click Load Dataset to view*") if file_state.value else None
        )

    _dataset_view if _dataset_view else None
    return


@app.cell
def _(file_state, file_type_selector, mo):
    # Advanced options - only for SP3
    _advanced = None

    if file_state.value and file_type_selector.value == "SP3 Ephemeris":
        mo.md("---")
        _advanced = mo.md("## 4. Advanced: Load with Velocities")

    _advanced if _advanced else None
    return


@app.cell
def _(file_state, file_type_selector, mo):
    # Velocity button - only for SP3
    velocity_button = (
        mo.ui.button(label="Load with Velocities", kind="neutral")
        if (file_state.value and file_type_selector.value == "SP3 Ephemeris")
        else None
    )

    velocity_button if velocity_button else None
    return (velocity_button,)


@app.cell
def _(Sp3File, file_state, mo, np, velocity_button):
    # Velocity viewer
    _velocity_view = None

    if velocity_button and velocity_button.value:
        if file_state.value:
            try:
                # Reload with velocities using from_file
                _sp3_vel = Sp3File.from_file(
                    file_state.value.fpath,
                    add_velocities=True,
                    dimensionless=True,
                )

                _ds_vel = _sp3_vel.data

                _info = [
                    f"**Variables:** {', '.join(list(_ds_vel.data_vars))}",
                    f"**Has Velocities:** {'Vx' in _ds_vel.data_vars}",
                ]

                if "Vx" in _ds_vel.data_vars:
                    _v_mag = np.sqrt(_ds_vel.Vx**2 + _ds_vel.Vy**2 + _ds_vel.Vz**2)
                    _info.extend(
                        [
                            "",
                            "**Velocity Statistics:**",
                            f"- Mean: {float(_v_mag.mean()):.2f} m/s",
                            f"- Min: {float(_v_mag.min()):.2f} m/s",
                            f"- Max: {float(_v_mag.max()):.2f} m/s",
                            "",
                            "*Typical GNSS orbital velocity: ~3,874 m/s*",
                        ]
                    )

                _velocity_view = mo.vstack(
                    [
                        mo.md("### SP3 with Computed Velocities"),
                        mo.md("\n\n".join(_info)),
                    ]
                )

                print("\nDataset with Velocities:")
                print(_ds_vel)

            except Exception as _e:
                _velocity_view = mo.callout(
                    mo.md(f"**Error:** {str(_e)}"), kind="danger"
                )
    else:
        _velocity_view = (
            mo.md("*Click to compute velocities from position data*")
            if velocity_button
            else None
        )

    _velocity_view if _velocity_view else None
    return


@app.cell
def _(mo):
    mo.md("""
    ---

    ### How This Works

    **Marimo Reactive Pattern:**
    1. `file_state = mo.state(None)` - persistent storage container
    2. Download button → store file in `file_state.value`
    3. Read button → access `file_state.value.data`
    4. All cells react automatically to state changes

    **Why State is Needed:**
    - Download is expensive, shouldn't re-run on UI changes
    - Multi-step workflow: download → inspect → read
    - File object must persist across button clicks

    **Key Pattern:**
    ```python
    # Define once
    state = mo.state(None)

    # Write
    if download_btn.value:
        state.value = downloaded_file

    # Read
    if state.value:
        use(state.value)
    ```
    """)
    return


if __name__ == "__main__":
    app.run()
