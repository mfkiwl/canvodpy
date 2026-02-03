import marimo

__generated_with = "0.19.2"
app = marimo.App(width="columns")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # canvod-aux Interactive Demo

    Explore GNSS auxiliary data product registry, download, and read functionality.

    This notebook demonstrates:
    - Product registry exploration
    - Available analysis centers and products
    - Product specifications and metadata
    - Latency comparisons across products
    - **File downloads from ESA and NASA servers**
    - **Opening and exploring downloaded datasets**
    - **Complete workflow: from_datetime_date() and from_file()**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Product Registry
    """)
    return


@app.cell
def _():
    from canvod.aux.products import (
        get_product_spec,
        get_products_for_agency,
        list_agencies,
        list_available_products,
    )

    return (
        get_product_spec,
        get_products_for_agency,
        list_agencies,
        list_available_products,
    )


@app.cell
def _(list_agencies, list_available_products):
    # List available agencies and products
    agencies = list_agencies()
    all_products = list_available_products()

    print(f"Available Analysis Centers: {len(agencies)}")
    print(f"Total Products: {len(all_products)}")
    print(f"\nAgencies: {', '.join(sorted(agencies))}")
    return (agencies,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Agency Selection
    """)
    return


@app.cell
def _(agencies, mo):
    # Interactive agency selector
    selected_agency = mo.ui.dropdown(
        options=sorted(agencies), value="COD", label="Select Analysis Center:"
    )
    selected_agency
    return (selected_agency,)


@app.cell
def _(get_products_for_agency, selected_agency):
    # Show products for selected agency
    agency_products = get_products_for_agency(selected_agency.value)

    print(f"\n{selected_agency.value} Products:")
    for _product_key in sorted(agency_products):
        print(f"  • {_product_key}")
    return (agency_products,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Product Selection
    """)
    return


@app.cell
def _(agency_products, mo):
    # Product type selector
    selected_product = mo.ui.dropdown(
        options=sorted(agency_products) if agency_products else [],
        value=sorted(agency_products)[0] if agency_products else None,
        label="Select Product Type:",
    )
    selected_product
    return (selected_product,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Product Details
    """)
    return


@app.cell
def _(get_product_spec, mo, selected_agency, selected_product):
    # Show detailed product specifications
    product_spec = None
    if selected_product.value:
        product_spec = get_product_spec(selected_agency.value, selected_product.value)

        details = f"""
        ### {product_spec.prefix}

        **Agency:** {product_spec.agency_name}
        **Latency:** {product_spec.latency_hours} hours
        **Sampling Rate:** {product_spec.sampling_rate}
        **Duration:** {product_spec.duration}
        **Available Formats:** {", ".join(product_spec.available_formats)}

        **Description:** {product_spec.description}

        **FTP Path Pattern:**
        `{product_spec.ftp_path_pattern}`
        """

        mo.md(details)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Product Type Comparison
    """)
    return


@app.cell
def _(mo):
    # Compare different product types
    product_types = ["final", "rapid"]
    comparison_selector = mo.ui.multiselect(
        options=product_types, value=["rapid"], label="Compare Product Types:"
    )
    comparison_selector
    return (comparison_selector,)


@app.cell
def _(comparison_selector, get_product_spec, selected_agency):
    import polars as pl

    # Show comparison table
    _comparison_data = []
    for _ptype in comparison_selector.value:
        try:
            _pspec = get_product_spec(selected_agency.value, _ptype)
            _comparison_data.append(
                {
                    "Type": _ptype,
                    "Prefix": _pspec.prefix,
                    "Latency (h)": _pspec.latency_hours,
                    "Sampling": _pspec.sampling_rate,
                    "Duration": _pspec.duration,
                    "Formats": ", ".join(_pspec.available_formats),
                }
            )
        except Exception:
            pass

    if _comparison_data:
        comparison_df = pl.DataFrame(_comparison_data)
        print(comparison_df)
    return (pl,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. All Analysis Centers Overview
    """)
    return


@app.cell
def _(get_product_spec, get_products_for_agency, list_agencies, pl):
    # Create overview of all agencies
    _overview_data = []
    for _agn in sorted(list_agencies()):
        _prods = get_products_for_agency(_agn)
        # Get sample product for agency name
        if _prods:
            _sample = get_product_spec(_agn, _prods[0])
            _overview_data.append(
                {
                    "Code": _agn,
                    "Agency": _sample.agency_name,
                    "Products": len(_prods),
                    "Types": ", ".join(sorted(_prods)),
                }
            )

    overview_df = pl.DataFrame(_overview_data)
    print(overview_df)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Latency Visualization
    """)
    return


@app.cell
def _(get_product_spec, list_agencies):
    import matplotlib.pyplot as plt
    import numpy as np

    # Collect latency data for all products
    _latency_data = {}
    for _ag in list_agencies():
        for _pt in ["final", "rapid"]:
            try:
                _psp = get_product_spec(_ag, _pt)
                _key = f"{_ag}/{_pt}"
                _latency_data[_key] = _psp.latency_hours
            except Exception:
                pass

    # Create bar chart
    if _latency_data:
        fig, ax = plt.subplots(figsize=(12, 6))

        # Sort by latency
        _sorted_items = sorted(_latency_data.items(), key=lambda x: x[1])
        _labels = [item[0] for item in _sorted_items]
        _values = [item[1] for item in _sorted_items]

        # Color by product type
        _colors = []
        for _lbl in _labels:
            if "final" in _lbl:
                _colors.append("#2E86AB")
            elif "rapid" in _lbl:
                _colors.append("#A23B72")
            else:
                _colors.append("#F18F01")

        bars = ax.barh(range(len(_labels)), _values, color=_colors)
        ax.set_yticks(range(len(_labels)))
        ax.set_yticklabels(_labels, fontsize=8)
        ax.set_xlabel("Latency (hours)")
        ax.set_title("Product Latency by Analysis Center")
        ax.grid(axis="x", alpha=0.3)

        # Add legend
        from matplotlib.patches import Patch

        _legend_elements = [
            Patch(facecolor="#2E86AB", label="Final"),
            Patch(facecolor="#A23B72", label="Rapid"),
        ]
        ax.legend(handles=_legend_elements, loc="lower right")

        plt.tight_layout()
        plt.show()
    return np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Sampling Rate Distribution
    """)
    return


@app.cell
def _(get_product_spec, list_available_products, plt):
    # Analyze sampling rates across all products
    _sampling_data = {}
    for _ag_code, _prod_type in list_available_products():
        _ps = get_product_spec(_ag_code, _prod_type)
        _sampling_data[f"{_ag_code}/{_prod_type}"] = _ps.sampling_rate

    # Count occurrences
    from collections import Counter

    _rate_counts = Counter(_sampling_data.values())

    # Create pie chart
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    _rates = list(_rate_counts.keys())
    _counts = list(_rate_counts.values())

    ax2.pie(_counts, labels=_rates, autopct="%1.1f%%", startangle=90)
    ax2.set_title("Sampling Rate Distribution Across Products")
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 9. Download Configuration

    Configure directory and parameters for testing downloads.

    **Note:** Some FTP servers may have different directory structures or file availability.
    If downloads fail, try different dates or set `CDDIS_MAIL` environment variable for NASA fallback.
    """)
    return


@app.cell
def _(mo):
    import os
    import tempfile
    from pathlib import Path

    # Directory configuration
    default_dir = Path(tempfile.gettempdir()) / "canvod_aux_demo"

    # Show CDDIS status
    _cddis_status = os.environ.get("CDDIS_MAIL")
    if _cddis_status:
        print(f"✓ CDDIS Fallback: Enabled ({_cddis_status})")
    else:
        print("ℹ CDDIS Fallback: Disabled (ESA only)")

    dir_input = mo.ui.text(
        value=str(default_dir), label="Download Directory:", full_width=True
    )
    dir_input
    return dir_input, os


@app.cell
def _(mo):
    import datetime

    # Date selection with dropdown for year
    date_year = mo.ui.dropdown(
        options=[2020, 2021, 2022, 2023, 2024], value=2023, label="Year:"
    )

    date_month = mo.ui.number(value=9, start=1, stop=12, step=1, label="Month:")

    date_day = mo.ui.number(value=11, start=1, stop=31, step=1, label="Day:")

    mo.hstack([date_year, date_month, date_day])
    return date_day, date_month, date_year, datetime


@app.cell
def _(date_day, date_month, date_year, datetime):
    # Construct date
    selected_date = datetime.date(date_year.value, date_month.value, date_day.value)
    print(f"Selected date: {selected_date} (DOY: {selected_date.timetuple().tm_yday})")
    return (selected_date,)


@app.cell
def _(mo):
    # Server selection
    server_selector = mo.ui.radio(
        options=["ESA", "NASA+ESA"], value="ESA", label="FTP Server:"
    )
    server_selector
    return (server_selector,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 10. State Definition (Critical!)

    **Marimo State Explanation:**

    `mo.state()` creates persistent storage that exists across cell executions.
    - The container (`sp3_state`) is ALWAYS defined
    - The contents (`sp3_state.value`) start as `None` and can be updated
    - Other cells can read `sp3_state.value` without conditional errors

    This is the ONLY cell where state is initialized.
    """)
    return


@app.cell
def _(mo):
    from canvod.aux.clock.reader import ClkFile
    from canvod.aux.core.downloader import FtpDownloader
    from canvod.aux.ephemeris.reader import Sp3File

    # State containers (always exist, even when value is None)
    sp3_state = mo.state(None)  # Holds Sp3File instance or None
    clk_state = mo.state(None)  # Holds ClkFile instance or None

    return FtpDownloader, Sp3File, ClkFile, sp3_state, clk_state


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 11. SP3 Download

    **Download Logic:**
    - Button click triggers download
    - Success: Store `Sp3File` instance in `sp3_state.value`
    - Failure: Keep `sp3_state.value` as `None`, show error
    """)
    return


@app.cell
def _(mo):
    # Download button
    download_sp3_button = mo.ui.button(label="Download SP3")
    download_sp3_button
    return (download_sp3_button,)


@app.cell
def _(
    FtpDownloader,
    Sp3File,
    dir_input,
    download_sp3_button,
    mo,
    os,
    selected_agency,
    selected_date,
    selected_product,
    server_selector,
    sp3_state,
):
    # Download handler - runs when button is clicked
    if download_sp3_button.value:
        _download_dir = dir_input.value
        os.makedirs(_download_dir, exist_ok=True)

        try:
            # Setup downloader
            _user_email = (
                os.environ.get("CDDIS_MAIL")
                if server_selector.value == "NASA+ESA"
                else None
            )
            _downloader = FtpDownloader(user_email=_user_email)

            # Download file using from_datetime_date()
            _sp3_file = Sp3File.from_datetime_date(
                date=selected_date,
                agency=selected_agency.value,
                product_type=selected_product.value,
                ftp_server="ftp://gssc.esa.int/gnss",
                local_dir=_download_dir,
                downloader=_downloader,
            )

            # CRITICAL: Store in state so other cells can access it
            sp3_state.value = _sp3_file

            # Display success message
            sp3_download_output = mo.md(f"""
            ✅ **Downloaded SP3 File**

            - Path: `{_sp3_file.fpath}`
            - Agency: {_sp3_file.agency}
            - Product: {_sp3_file.product_type}

            *Click "Read SP3 Dataset" below to load data*
            """)
        except Exception as _e:
            # On error: keep state as None, show error
            sp3_state.value = None
            sp3_download_output = mo.md(f"""
            ❌ **Download Failed**

            Error: {str(_e)[:400]}

            *Tip: Try a different date or enable NASA CDDIS fallback*
            """)
    else:
        # Button not clicked yet
        sp3_download_output = mo.md("⬇️ Click **Download SP3** to fetch a file.")

    sp3_download_output
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 12. SP3 Read Dataset

    **Read Logic:**
    - Check if `sp3_state.value` is not None (file was downloaded)
    - Call `.data` property to lazy-load xarray Dataset
    - Display dataset information
    """)
    return


@app.cell
def _(mo):
    # Read button
    read_sp3_button = mo.ui.button(label="Read SP3 Dataset")
    read_sp3_button
    return (read_sp3_button,)


@app.cell
def _(mo, read_sp3_button, sp3_state):
    # Read handler - accesses sp3_state.value
    if read_sp3_button.value:
        if sp3_state.value is not None:
            try:
                # Access .data property to load dataset
                _sp3_ds = sp3_state.value.data

                _info = f"""
                ### SP3 Dataset (from_datetime_date)

                **Dimensions:** {dict(_sp3_ds.sizes)}
                **Variables:** {list(_sp3_ds.data_vars)}
                **Coordinates:** {list(_sp3_ds.coords)}

                **Time Range:**
                {_sp3_ds.epoch.values[0]} to {_sp3_ds.epoch.values[-1]}

                **Satellites:** {len(_sp3_ds.sv)} total

                **Attributes:**
                """
                for _k, _v in _sp3_ds.attrs.items():
                    _info += f"\n- `{_k}`: {_v}"

                sp3_read_output = mo.md(_info)

                print("\nDataset Preview:")
                print(_sp3_ds)
            except Exception as _e:
                sp3_read_output = mo.md(f"❌ **Error:** {str(_e)}")
        else:
            # State is None - file not downloaded yet
            sp3_read_output = mo.md("⚠️ Download an SP3 file first")
    else:
        # Button not clicked yet
        sp3_read_output = mo.md("👆 Click **Read SP3 Dataset** to load data")

    sp3_read_output
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 13. CLK Download

    Same pattern as SP3: button → download → store in `clk_state.value`
    """)
    return


@app.cell
def _(mo):
    download_clk_button = mo.ui.button(label="Download CLK")
    download_clk_button
    return (download_clk_button,)


@app.cell
def _(
    ClkFile,
    FtpDownloader,
    clk_state,
    dir_input,
    download_clk_button,
    mo,
    os,
    selected_agency,
    selected_date,
    selected_product,
    server_selector,
):
    if download_clk_button.value:
        _download_dir = dir_input.value
        os.makedirs(_download_dir, exist_ok=True)

        try:
            _user_email = (
                os.environ.get("CDDIS_MAIL")
                if server_selector.value == "NASA+ESA"
                else None
            )
            _downloader = FtpDownloader(user_email=_user_email)

            _clk_file = ClkFile.from_datetime_date(
                date=selected_date,
                agency=selected_agency.value,
                product_type=selected_product.value,
                ftp_server="ftp://gssc.esa.int/gnss",
                local_dir=_download_dir,
                downloader=_downloader,
            )

            clk_state.value = _clk_file

            clk_download_output = mo.md(f"""
            ✅ **Downloaded CLK File**

            - Path: `{_clk_file.fpath}`
            - Agency: {_clk_file.agency}
            - Product: {_clk_file.product_type}

            *Click "Read CLK Dataset" below to load data*
            """)
        except Exception as _e:
            clk_state.value = None
            clk_download_output = mo.md(f"""
            ❌ **Download Failed**

            Error: {str(_e)[:400]}

            *Tip: Try a different date or enable NASA CDDIS fallback*
            """)
    else:
        clk_download_output = mo.md("⬇️ Click **Download CLK** to fetch a file.")

    clk_download_output
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 14. CLK Read Dataset
    """)
    return


@app.cell
def _(mo):
    read_clk_button = mo.ui.button(label="Read CLK Dataset")
    read_clk_button
    return (read_clk_button,)


@app.cell
def _(clk_state, mo, read_clk_button):
    if read_clk_button.value:
        if clk_state.value is not None:
            try:
                _clk_ds = clk_state.value.data

                _info = f"""
                ### CLK Dataset (from_datetime_date)

                **Dimensions:** {dict(_clk_ds.sizes)}
                **Variables:** {list(_clk_ds.data_vars)}
                **Coordinates:** {list(_clk_ds.coords)}

                **Clock Offset Range:**
                {float(_clk_ds.clock_offset.min()):.6e} to {float(_clk_ds.clock_offset.max()):.6e} seconds

                **Attributes:**
                """
                for _k, _v in _clk_ds.attrs.items():
                    _info += f"\n- `{_k}`: {_v}"

                clk_read_output = mo.md(_info)

                print("\nDataset Preview:")
                print(_clk_ds)
            except Exception as _e:
                clk_read_output = mo.md(f"❌ **Error:** {str(_e)}")
        else:
            clk_read_output = mo.md("⚠️ Download a CLK file first")
    else:
        clk_read_output = mo.md("👆 Click **Read CLK Dataset** to load data")

    clk_read_output
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 15. Advanced: from_file() with Custom Parameters

    Read existing files using `from_file()` with custom parameters like velocities and dimensionless output.
    """)
    return


@app.cell
def _(Sp3File, mo, np, sp3_state):
    read_sp3_velocities_button = mo.ui.button(label="Read SP3 with Velocities")

    if read_sp3_velocities_button.value:
        if sp3_state.value is not None:
            try:
                # Use from_file() to reload with different parameters
                _sp3_with_vel = Sp3File.from_file(
                    sp3_state.value.fpath,
                    add_velocities=True,
                    dimensionless=True,
                )

                _sp3_vel_ds = _sp3_with_vel.data

                _info = f"""
                ### SP3 with Velocities (from_file)

                **Variables:** {list(_sp3_vel_ds.data_vars)}
                **Has Velocities:** {"Vx" in _sp3_vel_ds.data_vars}
                """

                if "Vx" in _sp3_vel_ds.data_vars:
                    _v_mag = np.sqrt(
                        _sp3_vel_ds.Vx**2 + _sp3_vel_ds.Vy**2 + _sp3_vel_ds.Vz**2
                    )
                    _info += f"""

                    **Velocity Statistics:**
                    - Mean magnitude: {float(_v_mag.mean()):.2f} m/s
                    - Min magnitude: {float(_v_mag.min()):.2f} m/s
                    - Max magnitude: {float(_v_mag.max()):.2f} m/s

                    *(Typical GNSS orbital velocity: ~3,874 m/s)*
                    """

                read_vel_output = mo.md(_info)

                print("\nDataset with Velocities:")
                print(_sp3_vel_ds)
            except Exception as _e:
                read_vel_output = mo.md(f"❌ **Error:** {str(_e)}")
        else:
            read_vel_output = mo.md("⚠️ Download an SP3 file first")
    else:
        read_vel_output = mo.vstack(
            [
                read_sp3_velocities_button,
                mo.md(
                    "👆 Click to demonstrate `from_file()` with velocity calculation"
                ),
            ]
        )

    read_vel_output
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Summary

    **Marimo State Management Key Takeaways:**

    1. **Define state ONCE** in its own cell: `sp3_state = mo.state(None)`
    2. **Write to state**: `sp3_state.value = downloaded_file`
    3. **Read from state**: `if sp3_state.value is not None:`
    4. **State persists** across button clicks and cell re-runs
    5. **State container always exists**, even when `.value` is `None`

    This demo demonstrated the complete canvod-aux workflow:

    **Product Registry:**
    1. Multiple analysis centers and product types
    2. Product specifications and metadata
    3. Latency and sampling rate comparisons

    **File Operations:**
    4. Download using `from_datetime_date()` class method
    5. Read existing files using `from_file()` class method
    6. Lazy-load datasets with `.data` property
    7. Custom parameters (velocities, dimensionless output)

    **Key Features:**
    - Centralized product registry for GNSS auxiliary data
    - Automatic download with fallback servers (ESA → NASA)
    - SP3 ephemeris and CLK clock correction handling
    - xarray-based dataset interface for analysis
    - Computed velocities from position data

    For complete documentation, visit [canvodpy.readthedocs.io](https://canvodpy.readthedocs.io/canvod-aux).
    """)
    return


if __name__ == "__main__":
    app.run()
