import marimo

__generated_with = "0.19.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # GNSS VOD Analysis - Complete Pipeline
    
    This notebook demonstrates the complete pipeline for GNSS Vegetation Optical Depth (VOD) analysis:
    
    1. **Setup** - Configure data directories and paths
    2. **Read RINEX** - Load observation data
    3. **Download Auxiliary Data** - Get ephemeris (SP3) and clock (CLK) files
    4. **Augment Data** - Compute satellite positions and clock corrections
    5. **Complete Workflow** - End-to-end processing
    
    ## Prerequisites
    
    - RINEX observation files in a test directory
    - Internet connection for downloading auxiliary data
    - Configured receiver position
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 1. Setup - Data Directories
    
    Configure paths to your RINEX data and output directories.
    """)
    return


@app.cell
def _(mo):
    from pathlib import Path
    import tempfile
    
    # Default directories
    default_rinex_dir = Path.home() / "GNSS" / "test_data" / "rinex"
    default_aux_dir = Path(tempfile.gettempdir()) / "canvod_aux"
    default_output_dir = Path(tempfile.gettempdir()) / "canvod_output"
    
    # Directory inputs
    rinex_dir_input = mo.ui.text(
        value=str(default_rinex_dir),
        label="RINEX Data Directory:",
        full_width=True
    )
    
    aux_dir_input = mo.ui.text(
        value=str(default_aux_dir),
        label="Auxiliary Data Directory:",
        full_width=True
    )
    
    output_dir_input = mo.ui.text(
        value=str(default_output_dir),
        label="Output Directory:",
        full_width=True
    )
    
    mo.vstack([rinex_dir_input, aux_dir_input, output_dir_input])
    return (Path, aux_dir_input, default_aux_dir, default_output_dir, default_rinex_dir, output_dir_input, rinex_dir_input, tempfile)


@app.cell
def _(Path, aux_dir_input, mo, output_dir_input, rinex_dir_input):
    # Parse paths
    def get_paths():
        rinex_dir = Path(rinex_dir_input.value)
        aux_dir = Path(aux_dir_input.value)
        output_dir = Path(output_dir_input.value)
        
        # Create directories if they don't exist
        aux_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if RINEX directory exists
        if not rinex_dir.exists():
            mo.md(f"⚠️ **Warning:** RINEX directory does not exist: `{rinex_dir}`")
            return None, None, None
        
        return rinex_dir, aux_dir, output_dir
    
    _rinex_dir, _aux_dir, _output_dir = get_paths()
    
    if _rinex_dir:
        mo.md(f"""
        ✅ **Directories Configured**
        
        - RINEX: `{_rinex_dir}`
        - Auxiliary: `{_aux_dir}`
        - Output: `{_output_dir}`
        """)
    return (get_paths,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 2. Read RINEX Files
    
    Scan for RINEX files in the configured directory and read observation data.
    """)
    return


@app.cell
def _(_rinex_dir):
    def scan_rinex_files(directory):
        """Scan directory for RINEX files."""
        from pathlib import Path
        
        rinex_patterns = ['*.rnx', '*.RNX', '*.o', '*.O', '*.crx', '*.CRX']
        rinex_files = []
        
        for pattern in rinex_patterns:
            rinex_files.extend(directory.glob(pattern))
        
        return sorted(rinex_files)
    
    if _rinex_dir:
        _found_rinex_files = scan_rinex_files(_rinex_dir)
        print(f"Found {len(_found_rinex_files)} RINEX files")
        
        if _found_rinex_files:
            print("\nFirst 5 files:")
            for f in _found_rinex_files[:5]:
                print(f"  • {f.name}")
    return (scan_rinex_files,)


@app.cell
def _(mo):
    # File selector
    rinex_file_selector = mo.ui.dropdown(
        options=[],
        label="Select RINEX file to read:",
    )
    rinex_file_selector
    return (rinex_file_selector,)


@app.cell
def _(_found_rinex_files, mo, rinex_file_selector):
    # Update dropdown options
    if _found_rinex_files:
        rinex_file_selector._update_options([str(f) for f in _found_rinex_files])
        rinex_file_selector._update_value(str(_found_rinex_files[0]))
    return


@app.cell
def _(mo, rinex_file_selector):
    # Read button
    read_rinex_button = mo.ui.run_button(label="Read RINEX File")
    read_rinex_button
    return (read_rinex_button,)


@app.cell
def _(Path, mo, read_rinex_button, rinex_file_selector):
    # Read RINEX file
    def read_rinex_file(fpath):
        """Read RINEX file and return dataset."""
        from canvod.readers import Rnxv3Obs
        
        try:
            obs = Rnxv3Obs(fpath=fpath)
            ds = obs.to_ds()
            return ds, None
        except Exception as e:
            return None, str(e)
    
    _rinex_ds = None
    _read_output = None
    
    if read_rinex_button.value and rinex_file_selector.value:
        _fpath = Path(rinex_file_selector.value)
        _rinex_ds, _error = read_rinex_file(_fpath)
        
        if _error:
            _read_output = mo.md(f"""
            ❌ **Error reading RINEX file**
            
            {_error}
            """)
        elif _rinex_ds:
            _read_output = mo.md(f"""
            ✅ **RINEX file loaded successfully**
            
            - File: `{_fpath.name}`
            - Dimensions: {dict(_rinex_ds.dims)}
            - Variables: {list(_rinex_ds.data_vars)[:10]}...
            - Time range: {_rinex_ds.epoch.min().values} to {_rinex_ds.epoch.max().values}
            """)
    else:
        _read_output = read_rinex_button
    
    _read_output
    return (read_rinex_file,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 3. Download Auxiliary Data
    
    Download ephemeris (SP3) and clock (CLK) files for the observation date.
    """)
    return


@app.cell
def _(_rinex_ds):
    def extract_date_from_rinex(ds):
        """Extract date from RINEX dataset."""
        import datetime
        
        # Get first epoch
        first_epoch = ds.epoch.min().values
        dt = datetime.datetime.utcfromtimestamp(first_epoch.astype('datetime64[s]').astype(int))
        
        return dt.date()
    
    if _rinex_ds is not None:
        _obs_date = extract_date_from_rinex(_rinex_ds)
        print(f"Observation date: {_obs_date}")
    return (extract_date_from_rinex,)


@app.cell
def _(_aux_dir, _obs_date, mo):
    # Agency and product type selectors
    agency_selector = mo.ui.dropdown(
        options=["COD", "GFZ", "ESA", "JPL", "IGS"],
        value="COD",
        label="Analysis Center:"
    )
    
    product_selector = mo.ui.dropdown(
        options=["final", "rapid"],
        value="rapid",
        label="Product Type:"
    )
    
    mo.hstack([agency_selector, product_selector])
    return (agency_selector, product_selector)


@app.cell
def _(mo):
    # Download button
    download_aux_button = mo.ui.run_button(label="Download Auxiliary Data")
    download_aux_button
    return (download_aux_button,)


@app.cell
def _(_aux_dir, _obs_date, agency_selector, download_aux_button, mo, product_selector):
    # Download auxiliary data
    def download_aux_data(date, agency, product_type, aux_dir):
        """Download SP3 and CLK files."""
        import os
        from canvod.aux.ephemeris.reader import Sp3File
        from canvod.aux.clock.reader import ClkFile
        from canvod.aux.core.downloader import FtpDownloader
        
        results = {}
        
        # Setup downloader
        user_email = os.environ.get("CDDIS_MAIL")
        downloader = FtpDownloader(user_email=user_email)
        ftp_server = "ftp://ftp.aiub.unibe.ch"  # ESA server
        
        try:
            # Download SP3
            sp3_file = Sp3File.from_datetime_date(
                date=date,
                agency=agency,
                product_type=product_type,
                ftp_server=ftp_server,
                local_dir=aux_dir,
                downloader=downloader,
            )
            results['sp3'] = sp3_file
            results['sp3_error'] = None
        except Exception as e:
            results['sp3'] = None
            results['sp3_error'] = str(e)
        
        try:
            # Download CLK
            clk_file = ClkFile.from_datetime_date(
                date=date,
                agency=agency,
                product_type=product_type,
                ftp_server=ftp_server,
                local_dir=aux_dir,
                downloader=downloader,
            )
            results['clk'] = clk_file
            results['clk_error'] = None
        except Exception as e:
            results['clk'] = None
            results['clk_error'] = str(e)
        
        return results
    
    _aux_files = None
    _download_output = None
    
    if download_aux_button.value and _obs_date:
        _aux_files = download_aux_data(
            _obs_date,
            agency_selector.value,
            product_selector.value,
            _aux_dir
        )
        
        # Build output message
        messages = []
        
        if _aux_files['sp3']:
            messages.append(f"✅ **SP3 Downloaded:** `{_aux_files['sp3'].fpath.name}`")
        elif _aux_files['sp3_error']:
            messages.append(f"❌ **SP3 Error:** {_aux_files['sp3_error'][:200]}")
        
        if _aux_files['clk']:
            messages.append(f"✅ **CLK Downloaded:** `{_aux_files['clk'].fpath.name}`")
        elif _aux_files['clk_error']:
            messages.append(f"❌ **CLK Error:** {_aux_files['clk_error'][:200]}")
        
        _download_output = mo.md("\n\n".join(messages))
    else:
        _download_output = download_aux_button
    
    _download_output
    return (download_aux_data,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 4. Augment RINEX Data
    
    Augment RINEX observations with satellite positions and clock corrections.
    """)
    return


@app.cell
def _(mo):
    # Receiver position inputs
    mo.md("""
    ### Receiver Position (ECEF)
    
    Enter approximate receiver position in ECEF coordinates (meters):
    """)
    return


@app.cell
def _(mo):
    receiver_x = mo.ui.number(
        value=4194304.678,
        label="X (m):",
        step=0.001
    )
    
    receiver_y = mo.ui.number(
        value=1162205.267,
        label="Y (m):",
        step=0.001
    )
    
    receiver_z = mo.ui.number(
        value=4647245.201,
        label="Z (m):",
        step=0.001
    )
    
    mo.hstack([receiver_x, receiver_y, receiver_z])
    return (receiver_x, receiver_y, receiver_z)


@app.cell
def _(mo):
    # Augmentation button
    augment_button = mo.ui.run_button(label="Augment Data")
    augment_button
    return (augment_button,)


@app.cell
def _(_aux_files, _rinex_ds, augment_button, mo, receiver_x, receiver_y, receiver_z):
    # Augment data
    def augment_rinex_data(rinex_ds, sp3_file, clk_file, receiver_pos):
        """Augment RINEX with auxiliary data."""
        from canvod.aux.augmentation import AuxDataAugmenter, AugmentationContext
        from dataclasses import dataclass
        import numpy as np
        
        # Simple ECEF position class (temporary until moved to canvod-core)
        @dataclass
        class ECEFPosition:
            """ECEF (Earth-Centered, Earth-Fixed) position in meters."""
            x: float
            y: float
            z: float
        
        # Create receiver position
        ecef_pos = ECEFPosition(
            x=receiver_pos[0],
            y=receiver_pos[1],
            z=receiver_pos[2]
        )
        
        # Load auxiliary datasets
        sp3_ds = sp3_file.data
        clk_ds = clk_file.data
        
        # Create augmentation context
        context = AugmentationContext(
            receiver_position=ecef_pos,
            receiver_type="test",
            matched_datasets={
                'ephemeris': sp3_ds,
                'clock': clk_ds
            }
        )
        
        # Create augmenter
        augmenter = AuxDataAugmenter()
        
        # Augment dataset
        augmented_ds = augmenter.augment(rinex_ds, context)
        
        return augmented_ds
    
    _augmented_ds = None
    _augment_output = None
    
    if augment_button.value and _rinex_ds is not None and _aux_files:
        if _aux_files['sp3'] and _aux_files['clk']:
            try:
                _receiver_pos = (
                    receiver_x.value,
                    receiver_y.value,
                    receiver_z.value
                )
                
                _augmented_ds = augment_rinex_data(
                    _rinex_ds,
                    _aux_files['sp3'],
                    _aux_files['clk'],
                    _receiver_pos
                )
                
                # Get new variables
                new_vars = set(_augmented_ds.data_vars) - set(_rinex_ds.data_vars)
                
                _augment_output = mo.md(f"""
                ✅ **Data Augmented Successfully**
                
                **New Variables Added:**
                {chr(10).join(f"- `{var}`" for var in sorted(new_vars))}
                
                **Dataset Info:**
                - Dimensions: {dict(_augmented_ds.dims)}
                - Total Variables: {len(_augmented_ds.data_vars)}
                """)
            except Exception as e:
                _augment_output = mo.md(f"""
                ❌ **Augmentation Error**
                
                {str(e)[:500]}
                """)
        else:
            _augment_output = mo.md("⚠️ **Cannot augment:** Missing auxiliary files")
    else:
        _augment_output = augment_button
    
    _augment_output
    return (augment_rinex_data,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 5. Visualize Results
    
    Explore the augmented dataset.
    """)
    return


@app.cell
def _(_augmented_ds):
    if _augmented_ds is not None:
        print("Augmented Dataset Structure:")
        print(_augmented_ds)
    return


@app.cell
def _(_augmented_ds, mo):
    # Variable selector for plotting
    if _augmented_ds is not None:
        plot_var_selector = mo.ui.dropdown(
            options=sorted([str(v) for v in _augmented_ds.data_vars]),
            label="Select variable to plot:"
        )
        plot_var_selector
    return (plot_var_selector,)


@app.cell
def _(_augmented_ds, mo, plot_var_selector):
    # Plot selected variable
    if _augmented_ds is not None and plot_var_selector.value:
        import matplotlib.pyplot as plt
        import numpy as np
        
        var = plot_var_selector.value
        data = _augmented_ds[var]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot first satellite as example
        if 'sv' in data.dims or 'sid' in data.dims:
            sv_dim = 'sv' if 'sv' in data.dims else 'sid'
            first_sv = data[sv_dim].values[0]
            subset = data.sel({sv_dim: first_sv})
            
            ax.plot(subset.epoch.values, subset.values, marker='.')
            ax.set_xlabel('Epoch')
            ax.set_ylabel(var)
            ax.set_title(f'{var} for {first_sv}')
            ax.grid(True, alpha=0.3)
        else:
            ax.plot(data.epoch.values, data.values, marker='.')
            ax.set_xlabel('Epoch')
            ax.set_ylabel(var)
            ax.set_title(var)
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    return (ax, data, fig, first_sv, plt, subset, sv_dim, var)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 6. Save Results
    
    Save the augmented dataset to NetCDF format.
    """)
    return


@app.cell
def _(mo):
    save_button = mo.ui.run_button(label="Save Augmented Dataset")
    save_button
    return (save_button,)


@app.cell
def _(_augmented_ds, _output_dir, mo, save_button):
    # Save dataset
    if save_button.value and _augmented_ds is not None:
        output_file = _output_dir / "augmented_rinex.nc"
        _augmented_ds.to_netcdf(output_file)
        
        mo.md(f"""
        ✅ **Dataset Saved**
        
        File: `{output_file}`
        Size: {output_file.stat().st_size / 1024 / 1024:.2f} MB
        """)
    else:
        save_button
    return (output_file,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Summary
    
    This notebook demonstrated the complete GNSS VOD analysis pipeline:
    
    ✅ **Setup** - Configured data directories  
    ✅ **Read RINEX** - Loaded observation data  
    ✅ **Download Auxiliary** - Retrieved SP3 and CLK files  
    ✅ **Augment Data** - Computed satellite positions and corrections  
    ✅ **Visualize** - Explored augmented variables  
    ✅ **Save** - Exported results to NetCDF
    
    ### Next Steps
    
    - **VOD Calculation**: Use canvod-vod package to compute vegetation optical depth
    - **Grid Analysis**: Apply canvod-grids for spatial aggregation
    - **Visualization**: Create maps and time series with canvod-viz
    - **Storage**: Store results in Icechunk format for efficient access
    
    ### Package Documentation
    
    - [canvod-readers](https://canvodpy.readthedocs.io/canvod-readers) - RINEX parsing
    - [canvod-aux](https://canvodpy.readthedocs.io/canvod-aux) - Auxiliary data
    - [canvod-vod](https://canvodpy.readthedocs.io/canvod-vod) - VOD calculations
    - [canvod-grids](https://canvodpy.readthedocs.io/canvod-grids) - Spatial grids
    - [canvod-viz](https://canvodpy.readthedocs.io/canvod-viz) - Visualization
    """)
    return


if __name__ == "__main__":
    app.run()
