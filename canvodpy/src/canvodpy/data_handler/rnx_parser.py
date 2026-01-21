#%%
import concurrent
from concurrent.futures import ProcessPoolExecutor, as_completed
import gc
from multiprocessing import cpu_count
import os
from pathlib import Path
import time
from typing import Dict, List, Optional, Union

import dask
from dask.diagnostics import ProgressBar
from natsort import natsorted
import numpy as np
import pint
from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass
from tqdm import tqdm
import xarray as xr

from canvodpy.data_handler.data_handler import DataDirMatcher, MatchedDirs
from canvodpy.globals import (
    CANOPY_DS_PREFIX,
    N_MAX_THREADS,
    SKY_DS_PREFIX,
    TIME_AGGR,
    UREG,
)
from canvodpy.rinexreader.rinex_reader import Rnxv3Obs


@dataclass(frozen=True, kw_only=True)
# @enforce_keyword_only_methods
class RinexFilesParser:
    """
    Immutable container class to store the paths of RINEX files.

    Parameters:
    ----------
    canopy_files: List[Path]
        List of paths to the canopy RINEX files.
    sky_files: List[Path]
        List of paths to the sky RINEX files.
    """

    matched_dirs: MatchedDirs

    def get_rnx_file_list(self, pth: Path) -> list[Path]:
        """
        Get a list of RINEX files in the specified directory.

        Parameters:
        ----------
        pth : Path
            The directory path to search for RINEX files.

        Returns:
        -------
            List[Path]: List of RINEX files in the specified directory.
        """
        return natsorted(pth.glob("*.2?o"))

    def make_rnx2ds_outname(self,
                            filepath: Path,
                            outdirname: str = '02_processed') -> Path:
        filename = Path(filepath).stem + ".nc"
        parent = Path(filepath).parent
        grand_parent = parent.parent
        outdir = grand_parent / outdirname / parent
        if not outdir.exists():
            outdir.mkdir(exist_ok=True)
        return outdir / filename

    def make_concated_outnames(self,
                               outdirname: str = '02_processed'
                               ) -> dict[str, Path]:
        yydoy: str = self.matched_dirs.yyyydoy.yydoy

        canopy_data_dir: str = self.matched_dirs.canopy_data_dir.parent.parent
        processed_canopy_dir: Path = Path(canopy_data_dir) / outdirname
        if not processed_canopy_dir.exists():
            processed_canopy_dir.mkdir(exist_ok=True)

        sky_data_dir: str = self.matched_dirs.sky_data_dir.parent.parent
        processed_sky_dir: Path = Path(sky_data_dir) / outdirname
        if not processed_sky_dir.exists():
            processed_sky_dir.mkdir(exist_ok=True)

        return {
            'canopy': processed_canopy_dir / f'{CANOPY_DS_PREFIX}_{yydoy}.nc',
            'sky': processed_sky_dir / f'{SKY_DS_PREFIX}_{yydoy}.nc',
        }

    def rnx2ds(
        self,
        filepath: Path,
        keep_vars: list[str] = ['SNR'],
        write_global_attrs: bool = True,
        return_ds: bool = False,
        outname: Path | None = None,
    ) -> xr.Dataset | Path:

        if not outname:
            outname = self.make_rnx2ds_outname(filepath)

        # rnx = Rnxv3Obs(filepath)

        # ds: xr.Dataset = rnx.to_freq_ds2(
        #     keep_data_vars=keep_vars,
        #     write_global_attrs=write_global_attrs,
        #     outname=outname,
        #     include_lli=include_lli,
        #     include_ssi=include_ssi,
        # )

        rnx: Rnxv3Obs = Rnxv3Obs(fpath=filepath)

        ds: xr.Dataset = rnx.to_ds_with_oft(
            outname=outname,
            keep_data_vars=keep_vars,
            write_global_attrs=write_global_attrs,
        )

        if not return_ds:
            return outname

        return ds

    # def parallel_process_rinex_files(
    #     self,
    #     rinex_files: List[Path],
    #     return_ds: bool = False,
    #     keep_vars: list[str] = ['SNR', 'Pseudorange', 'Phase', 'Doppler'],
    # ) -> Union[List[xr.Dataset], List[Path]]:

    #     print(f'\nPocessing {len(rinex_files)} RINEX Observation files.\n\t \
    #             For each file, the following data variables are kept: {keep_vars}\n'
    #           )

    #     results = [None] * len(
    #         rinex_files)  # Pre-allocate a list to ensure correct order

    #     # Create the progress bar instance outside of the ThreadPoolExecutor context
    #     with tqdm(total=len(rinex_files),
    #               desc="Processing RINEX Files") as pbar:
    #         # Use ThreadPoolExecutor for concurrent processing
    #         with concurrent.futures.ProcessPoolExecutor() as executor:
    #             # Submit each file to the executor with its index
    #             futures = {
    #                 executor.submit(self.rnx2ds,
    #                                 filepath=file,
    #                                 keep_vars=keep_vars,
    #                                 return_ds=return_ds):
    #                 i
    #                 for i, file in enumerate(rinex_files)
    #             }
    #             # Iterate over completed futures to update the progress bar
    #             for future in concurrent.futures.as_completed(futures):
    #                 idx = futures[
    #                     future]  # Get the original index of this future
    #                 try:
    #                     result = future.result()
    #                     if result is not None:
    #                         results[
    #                             idx] = result  # Store the result in the correct position
    #                 except Exception as e:
    #                     print(f"Error processing file at index {idx}: {e}")
    #                 pbar.update(
    #                     1
    #                 )  # Update the progress bar after each completed future

    #     return results

    # def parallel_process_rinex_files(
    #     self,
    #     rinex_files: List[Path],
    #     return_ds: bool = False,
    #     keep_vars: list[str] = ['SNR', 'Pseudorange', 'Phase', 'Doppler'],
    #     # New parameter for controlling batch size
    # ) -> Union[List[xr.Dataset], List[Path]]:
    #     """
    #     Process RINEX files in parallel with resource management.

    #     Parameters
    #     ----------
    #     rinex_files : List[Path]
    #         List of RINEX file paths to process
    #     return_ds : bool
    #         Whether to return datasets or file paths
    #     keep_vars : list[str]
    #         Variables to keep from RINEX files
    #     max_workers : int, optional
    #         Maximum number of parallel processes. If None, will use CPU count - 1
    #     chunk_size : int
    #         Number of files to process in each batch

    #     Returns
    #     -------
    #     Union[List[xr.Dataset], List[Path]]
    #         Processed results in the same order as input files
    #     """
    #     # # Calculate optimal number of workers based on system resources
    #     # if max_workers is None:
    #     #     max_workers = max(1, os.cpu_count() - 1)  # Leave one CPU core free

    #     # print(
    #     #     f'\nProcessing {len(rinex_files)} RINEX Observation files in batches.'
    #     #     f'\nUsing {max_workers} parallel processes.'
    #     #     f'\nKeeping variables: {keep_vars}\n')

    #     # Calculate optimal number of threads
    #     n_cores = (os.cpu_count() - 2)  # This will be 8 on your system
    #     n_threads = n_cores * 2  # Using 3 threads per core for I/O-bound work

    #     print(f'System has {os.cpu_count()} CPU cores, using {n_cores} cores')
    #     print(
    #         f'\nProcessing {len(rinex_files)} RINEX files using {n_threads} threads (2 threads per core).'
    #     )
    #     print(f'Keeping variables: {keep_vars}\n')

    #     def get_system_memory_usage():
    #         """Monitor system memory usage"""
    #         import psutil
    #         memory = psutil.virtual_memory()
    #         return memory.percent

    #     # Initialize results list
    #     results = [None] * len(rinex_files)

    #     # # Process files in chunks to manage memory usage
    #     # with tqdm(total=len(rinex_files),
    #     #           desc="Processing RINEX Files") as pbar:
    #     #     # Split files into chunks
    #     #     for chunk_start in range(0, len(rinex_files), chunk_size):
    #     #         chunk_end = min(chunk_start + chunk_size, len(rinex_files))
    #     #         chunk_files = rinex_files[chunk_start:chunk_end]

    #     #         # Process each chunk with controlled parallelism
    #     #         with concurrent.futures.ProcessPoolExecutor(
    #     #                 max_workers=max_workers) as executor:
    #     #             # Submit chunk of files to executor
    #     #             futures = {
    #     #                 executor.submit(self.rnx2ds,
    #     #                                 filepath=file,
    #     #                                 keep_vars=keep_vars,
    #     #                                 return_ds=return_ds): (i + chunk_start)
    #     #                 for i, file in enumerate(chunk_files)
    #     #             }

    #     #             # Process completed futures
    #     #             for future in concurrent.futures.as_completed(futures):
    #     #                 idx = futures[future]
    #     #                 try:
    #     #                     result = future.result()
    #     #                     if result is not None:
    #     #                         results[idx] = result
    #     #                 except Exception as e:
    #     #                     print(f"Error processing file at index {idx}: {e}")
    #     #                 pbar.update(1)

    #     with tqdm(total=len(rinex_files),
    #               desc="Processing RINEX Files") as pbar:
    #         with concurrent.futures.ProcessPoolExecutor(
    #                 max_workers=n_threads) as executor:
    #             # Submit all files to the executor
    #             futures = {
    #                 executor.submit(self.rnx2ds,
    #                                 filepath=file,
    #                                 keep_vars=keep_vars,
    #                                 return_ds=return_ds):
    #                 i
    #                 for i, file in enumerate(rinex_files)
    #             }

    #             # Process completed futures as they finish
    #             for future in concurrent.futures.as_completed(futures):
    #                 idx = futures[future]
    #                 try:
    #                     result = future.result()
    #                     if result is not None:
    #                         results[idx] = result
    #                 except Exception as e:
    #                     print(f"Error processing file at index {idx}: {e}")
    #                 if get_system_memory_usage(
    #                 ) > 90:  # If memory usage is above 90%
    #                     time.sleep(5)
    #                 pbar.update(1)

    #             # Optional: Add a small delay between chunks to allow memory cleanup
    #             time.sleep(1)

    #     return results

    def parallel_process_rinex_files(
        self,
        rinex_files: list[Path],
        return_ds: bool = False,
        keep_vars: list[str] = ['SNR', 'Pseudorange', 'Phase', 'Doppler']
    ) -> list[xr.Dataset] | list[Path]:
        """
        Process RINEX files using thread-based parallelism optimized for 2.5MB files.

        This implementation uses threads because:
        1. RINEX files are small (2.5MB), so memory isn't our bottleneck
        2. The work is mostly I/O bound (reading files and parsing text)
        3. Threads share memory space, reducing overall memory usage
        4. Thread creation is much lighter than process creation
        """
        # Calculate optimal number of threads
        # For I/O bound work, we can use more threads than CPU cores
        n_threads = min(N_MAX_THREADS, 4 * os.cpu_count())

        print(
            f'\nProcessing {len(rinex_files)} RINEX files using {n_threads} threads with {os.cpu_count()} CPU cores.'
        )
        # print(f'Each file is approximately 2.5MB')
        print(f'\tKeeping variables: {keep_vars}\n')

        # Pre-allocate results list to maintain order
        results = [None] * len(rinex_files)

        # Use ThreadPoolExecutor for efficient I/O handling
        with tqdm(total=len(rinex_files),
                  desc="Processing RINEX Files") as pbar:
            with ProcessPoolExecutor(max_workers=n_threads) as executor:
                # Submit all files to the executor
                futures = {
                    executor.submit(self.rnx2ds,
                                    filepath=file,
                                    keep_vars=keep_vars,
                                    return_ds=return_ds):
                    i
                    for i, file in enumerate(rinex_files)
                }

                # Process completed futures as they finish
                for future in concurrent.futures.as_completed(futures):
                    idx = futures[future]
                    try:
                        result = future.result()
                        if result is not None:
                            results[idx] = result
                    except Exception as e:
                        print(f"Error processing file at index {idx}: {e}")
                    pbar.update(1)

                gc.collect()  # Force garbage collection to free up memory
                time.sleep(1)  # Add a small delay to allow memory cleanup

        return results

    def concatentate_datasets(
        self,
        datasets: list[xr.Dataset],
        outname: Path,
        resample: bool = False,
    ) -> xr.Dataset:
        """
        Concatenate multiple datasets with OFT-based structure using memory-efficient processing.

        This method first tries to use file paths (much more efficient) if available,
        then falls back to in-memory concatenation for the OFT structure.
        """
        print(f"Concatenating {len(datasets)} datasets with OFT structure...")

        # Check if we have file paths and can use the efficient file-based approach
        file_paths = []
        if isinstance(datasets[0], xr.Dataset):
            print("Detected netCDF dataset, extracting file path...")
            for ds in datasets:
                # Check for file path in various locations
                file_path = None
                if hasattr(ds, 'encoding') and 'source' in ds.encoding:
                    file_path = ds.encoding['source']
                elif 'File Path' in ds.attrs:
                    file_path = ds.attrs['File Path']

                if file_path:
                    file_paths.append(
                        str(Path(file_path)).split('.')[0] + '.nc')
        elif isinstance(datasets[0], Path) or isinstance(datasets[0], str):
            print("Detected file paths directly in datasets list.")
            file_paths = [Path(ds) for ds in datasets]

        # If we have file paths for all datasets, use the efficient file-based concatenation
        # if len(file_paths) == len(datasets) and all(fp.exists() and fp.suffix == '.nc' for fp in file_paths):
        print(
            "Using efficient file-based concatenation with xr.open_mfdataset..."
        )

        return self.concatenate_datasets_from_files(file_paths, outname,
                                                    resample)

        # Fall back to in-memory concatenation
        print("Using in-memory concatenation...")

        # Check if datasets use the new OFT structure
        if datasets and 'OFT' in datasets[0].dims:
            print("Detected OFT-based dataset structure")

            # For large numbers of datasets, use chunked processing to avoid memory issues
            if len(datasets) > 50:
                print(
                    f"Large number of datasets detected ({len(datasets)}). Using chunked concatenation..."
                )
                combined_dataset = self._concatenate_oft_datasets_chunked(
                    datasets)
            else:
                combined_dataset = self._concatenate_oft_datasets_standard(
                    datasets)
        else:
            # Fallback for old structure (frequency-based)
            print("Using standard concatenation for frequency-based structure")
            combined_dataset: xr.Dataset = xr.concat(datasets, dim='Epoch')

        # Add encoding for OFT and Frequency coordinates if they exist
        if 'OFT' in combined_dataset.coords:
            combined_dataset.coords['OFT'].encoding = {
                'dtype': 'S4',
                'zlib': True
            }
        if 'Frequency' in combined_dataset.coords:
            combined_dataset.coords['Frequency'].encoding = {
                'dtype': 'f8',
                'zlib': True
            }

        print(f"Final concatenated dataset shape: {combined_dataset.dims}")
        return combined_dataset

    def _concatenate_oft_datasets_chunked(
            self, datasets: list[xr.Dataset]) -> xr.Dataset:
        """
        Smart concatenation for OFT-based datasets.

        First tries to use xr.open_mfdataset (much faster for file-based datasets),
        then falls back to chunked concatenation for in-memory datasets.
        """
        # Check if datasets have file paths we can use with open_mfdataset
        file_paths = []
        for ds in datasets:
            if hasattr(ds, 'encoding') and 'source' in ds.encoding:
                file_paths.append(ds.encoding['source'])
            elif hasattr(ds, 'attrs') and 'File Path' in ds.attrs:
                file_paths.append(ds.attrs['File Path'])

        # If we have file paths for all datasets, use xr.open_mfdataset (much simpler!)
        if len(file_paths) == len(datasets):
            print(f"Using xr.open_mfdataset for {len(file_paths)} files...")
            try:
                combined_dataset = xr.open_mfdataset(file_paths,
                                                     combine='nested',
                                                     concat_dim='Epoch',
                                                     engine='netcdf4')
                print(
                    f"✓ Successfully concatenated {len(file_paths)} files using xr.open_mfdataset"
                )
                return combined_dataset
            except Exception as e:
                print(f"xr.open_mfdataset failed: {e}")
                print("Falling back to manual concatenation...")

        # Fall back to manual concatenation for in-memory datasets
        print("Using manual chunked concatenation for in-memory datasets...")

        # Get the union of all OFT values across datasets
        print("Computing union of all OFTs...")
        all_ofts = set()
        for i, ds in enumerate(datasets):
            all_ofts.update(ds.coords['OFT'].values.tolist())
            if (i + 1) % 20 == 0:
                print(
                    f"  Processed {i + 1}/{len(datasets)} datasets, found {len(all_ofts)} unique OFTs so far"
                )

        all_ofts_sorted = sorted(list(all_ofts))
        n_ofts = len(all_ofts_sorted)
        print(f"Total unique OFTs across all datasets: {n_ofts}")

        if n_ofts > 800:
            print(f"WARNING: Very large OFT set ({n_ofts} codes) detected!")
            print("Using disk-based concatenation approach...")

            # For very large OFT sets, use disk-based approach
            return self._concatenate_oft_disk_based(datasets, all_ofts_sorted)

        # For smaller OFT sets, use the existing chunked approach
        chunk_size = 5 if n_ofts > 500 else 10
        print(f"Using chunk size: {chunk_size}")

        chunk_results: list[xr.Dataset] = []

        for chunk_start in range(0, len(datasets), chunk_size):
            chunk_end = min(chunk_start + chunk_size, len(datasets))
            chunk_datasets = datasets[chunk_start:chunk_end]

            print(
                f"Processing chunk {chunk_start//chunk_size + 1}/{(len(datasets) + chunk_size - 1)//chunk_size} "
                f"(datasets {chunk_start+1}-{chunk_end})")

            # Reindex and concatenate in one step to save memory
            reindexed_chunk: list[xr.Dataset] = []
            for i, ds in enumerate(chunk_datasets):
                print(
                    f"  Reindexing dataset {chunk_start + i + 1}/{len(datasets)}"
                )
                reindexed_ds: xr.Dataset = ds.reindex(OFT=all_ofts_sorted,
                                                      fill_value=np.nan)
                reindexed_chunk.append(reindexed_ds)
                del ds  # Clear original immediately

            print("  Concatenating chunk along Epoch dimension...")
            chunk_result: xr.Dataset = xr.concat(reindexed_chunk, dim='Epoch')
            chunk_results.append(chunk_result)

            # Clear chunk from memory
            del reindexed_chunk
            del chunk_datasets
            gc.collect()
            time.sleep(0.1)

        # Concatenate all results
        print("Final concatenation...")
        combined_dataset: xr.Dataset = xr.concat(chunk_results, dim='Epoch')

        del chunk_results
        gc.collect()

        return combined_dataset

    def _concatenate_oft_disk_based(self, datasets: list[xr.Dataset],
                                    all_ofts_sorted: list[str]) -> xr.Dataset:
        """
        Disk-based incremental concatenation approach for very large OFT sets.

        Uses temporary files to avoid keeping the entire result in memory.
        """
        import os
        import tempfile

        print("Using disk-based incremental concatenation approach...")

        # Create temporary directory for intermediate files
        temp_dir = tempfile.mkdtemp(prefix="gnss_concat_")
        print(f"Using temporary directory: {temp_dir}")

        try:
            # Process datasets in batches and write to temporary files
            batch_size = 5
            temp_files = []

            for batch_start in range(0, len(datasets), batch_size):
                batch_end = min(batch_start + batch_size, len(datasets))
                batch_datasets = datasets[batch_start:batch_end]

                print(
                    f"Processing batch {batch_start//batch_size + 1}/{(len(datasets) + batch_size - 1)//batch_size} "
                    f"(datasets {batch_start+1}-{batch_end})")

                # Reindex and concatenate this batch
                reindexed_batch = []
                for i, ds in enumerate(batch_datasets):
                    print(
                        f"  Reindexing dataset {batch_start + i + 1}/{len(datasets)}"
                    )
                    reindexed_ds = ds.reindex(OFT=all_ofts_sorted,
                                              fill_value=np.nan)
                    reindexed_batch.append(reindexed_ds)
                    del ds

                # Concatenate this batch
                print("  Concatenating batch...")
                batch_result = xr.concat(reindexed_batch, dim='Epoch')

                # Write batch to temporary file
                temp_file = os.path.join(
                    temp_dir, f"batch_{batch_start//batch_size}.nc")
                print(f"  Writing batch to {temp_file}")
                batch_result.to_netcdf(temp_file)
                temp_files.append(temp_file)

                # Clean up batch from memory
                del reindexed_batch
                del batch_result
                del batch_datasets
                gc.collect(
                )  # Now read and concatenate all temporary files using a binary tree approach
            print(
                f"Final concatenation of {len(temp_files)} temporary files using binary tree approach..."
            )

            # Start with all temporary files
            current_files = temp_files[:]
            round_num = 0

            while len(current_files) > 1:
                round_num += 1
                print(
                    f"  Round {round_num}: concatenating {len(current_files)} files..."
                )

                next_files = []

                # Process files in pairs
                for i in range(0, len(current_files), 2):
                    if i + 1 < len(current_files):
                        # Concatenate pair
                        file1, file2 = current_files[i], current_files[i + 1]
                        print(
                            f"    Concatenating {os.path.basename(file1)} + {os.path.basename(file2)}"
                        )

                        # Load both files
                        ds1 = xr.open_dataset(file1)
                        ds2 = xr.open_dataset(file2)

                        # Concatenate them
                        combined = xr.concat([ds1, ds2], dim='Epoch')

                        # Write result
                        output_file = os.path.join(
                            temp_dir, f"round{round_num}_{i//2}.nc")
                        combined.to_netcdf(output_file)
                        next_files.append(output_file)

                        # Clean up
                        ds1.close()
                        ds2.close()
                        del ds1, ds2, combined
                        gc.collect()

                    else:
                        # Odd file out, carry forward to next round
                        next_files.append(current_files[i])

                # Update for next round
                current_files = next_files

                # Clean up previous round files (except if they're original batch files)
                if round_num > 1:
                    for f in temp_files:
                        if f not in current_files and os.path.exists(f):
                            try:
                                os.remove(f)
                            except:
                                pass

            # Load the final result
            print("Loading final concatenated result...")
            combined_dataset = xr.open_dataset(current_files[0])

            return combined_dataset

        finally:
            # Clean up temporary files
            print("Cleaning up temporary files...")
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(
                    f"Warning: Could not clean up temporary directory {temp_dir}: {e}"
                )

        print("Incremental concatenation completed!")
        return combined_dataset

    def _concatenate_oft_datasets_standard(
            self, datasets: list[xr.Dataset]) -> xr.Dataset:
        """
        Standard concatenation for smaller numbers of OFT-based datasets.
        """
        # Get the union of all OFT values across datasets
        all_ofts = set()
        for ds in datasets:
            all_ofts.update(ds.coords['OFT'].values.tolist())
        all_ofts_sorted = sorted(list(all_ofts))

        print(f"Total unique OFTs across all datasets: {len(all_ofts_sorted)}")

        # Reindex all datasets to have the same OFT coordinates
        print("Reindexing datasets to common OFT set...")
        reindexed_datasets: list[xr.Dataset] = []
        for i, ds in enumerate(datasets):
            print(f"  Reindexing dataset {i+1}/{len(datasets)}")
            reindexed_ds: xr.Dataset = ds.reindex(OFT=all_ofts_sorted,
                                                  fill_value=np.nan)
            reindexed_datasets.append(reindexed_ds)

        # Now concatenate along the Epoch dimension
        print("Concatenating along Epoch dimension...")
        combined_dataset: xr.Dataset = xr.concat(reindexed_datasets,
                                                 dim='Epoch')
        return combined_dataset

        attrs_to_drop = ['File Path', 'File Type']
        for attr in attrs_to_drop:
            if attr in combined_dataset.attrs:
                del combined_dataset.attrs[attr]

        new_attrs = {
            'Producer': 'Nicolas F. Bader',
            'Contact': 'nicolas.bader@tuwien.ac.at',
            'Webpage': 'https://www.tuwien.at/en/mg/geo/climers/',
        }

        # Add new attributes from a dictionary
        if resample:
            if isinstance(TIME_AGGR, pint.Quantity):
                print(
                    f'\n\tResampling the combined dataset to {TIME_AGGR.magnitude} {TIME_AGGR.units:~}\n'
                )
                _time_aggr = TIME_AGGR.to(
                    UREG.s
                )  # Convert to seconds, independent of the original (time) unit

                combined_dataset = combined_dataset.resample(
                    Epoch=f'{_time_aggr.to(UREG.s).magnitude}s').mean()
                new_attrs.update({
                    'Resampling':
                    f'from original sampling interval of 5s to {TIME_AGGR.magnitude}{TIME_AGGR.units:~}',
                })

        combined_dataset.attrs.update(new_attrs)

        # Update encoding to handle both old and new data structures
        encoding = {
            var: {
                "zlib": True,
                "complevel": 5,
                "dtype": np.float32,
            }
            for var in combined_dataset.data_vars
        }

        # Add coordinate encoding for OFT-based datasets
        if 'OFT' in combined_dataset.dims:
            encoding.update({
                'OFT': {
                    'dtype': 'S32'
                },  # String encoding for OFT
                'Frequency': {
                    'dtype': np.float32
                }  # Float encoding for Frequency coordinate
            })

        print(f"Saving combined dataset with Dask to {outname}...")
        print(f"Dataset shape: {dict(combined_dataset.dims)}")
        print(f"Data variables: {list(combined_dataset.data_vars.keys())}")
        if 'OFT' in combined_dataset.dims:
            print(
                f"Using OFT-based structure with {len(combined_dataset.coords['OFT'])} observation types"
            )

        # Use Dask to write the dataset to disk with a progress bar
        with dask.config.set(scheduler='threads'):
            with ProgressBar():
                combined_dataset.to_netcdf(str(outname),
                                           encoding=encoding,
                                           engine="netcdf4",
                                           compute=True)

        return combined_dataset

    def concatenate_datasets_from_files(self,
                                        file_paths: list[Path],
                                        outname: Path,
                                        resample: bool = False) -> xr.Dataset:
        """
        Simple concatenation using xr.open_mfdataset for NetCDF files.

        This is much more efficient than loading datasets into memory first.
        """
        print(
            f"Concatenating {len(file_paths)} NetCDF files using xr.open_mfdataset..."
        )
        print(f"Files to be concatenated: {file_paths[0]}, ...")
        try:
            # Use xr.open_mfdataset - this handles OFT alignment automatically!
            combined_dataset = xr.open_mfdataset(file_paths,
                                                 combine='nested',
                                                 concat_dim='Epoch',
                                                 engine='netcdf4')

            print(f"✓ Successfully concatenated {len(file_paths)} files")
            print(f"Combined dataset shape: {dict(combined_dataset.dims)}")
            print(f"Data variables: {list(combined_dataset.data_vars.keys())}")

            if 'OFT' in combined_dataset.dims:
                print(f"Total OFTs: {len(combined_dataset.OFT)}")

            # Update attributes
            attrs_to_drop = ['File Path', 'File Type']
            for attr in attrs_to_drop:
                if attr in combined_dataset.attrs:
                    del combined_dataset.attrs[attr]

            new_attrs = {
                'Producer': 'Nicolas F. Bader',
                'Contact': 'nicolas.bader@tuwien.ac.at',
                'Webpage': 'https://www.tuwien.at/en/mg/geo/climers/',
            }

            # Handle resampling if requested
            if resample:
                if isinstance(TIME_AGGR, pint.Quantity):
                    print(
                        f'\n\tResampling the combined dataset to {TIME_AGGR.magnitude} {TIME_AGGR.units:~}\n'
                    )
                    _time_aggr = TIME_AGGR.to(UREG.s)
                    combined_dataset = combined_dataset.resample(
                        Epoch=f'{_time_aggr.to(UREG.s).magnitude}s').mean()
                    new_attrs.update({
                        'Resampling':
                        f'from original sampling interval of 5s to {TIME_AGGR.magnitude}{TIME_AGGR.units:~}',
                    })

            combined_dataset.attrs.update(new_attrs)

            # Update encoding to handle both old and new data structures
            encoding = {
                var: {
                    "zlib": True,
                    "complevel": 5,
                    "dtype": np.float32,
                }
                for var in combined_dataset.data_vars
            }

            # Add coordinate encoding for OFT-based datasets
            if 'OFT' in combined_dataset.dims:
                encoding.update({
                    'OFT': {
                        'dtype': 'S32'
                    },  # String encoding for OFT
                    'Frequency': {
                        'dtype': np.float32
                    }  # Float encoding for Frequency coordinate
                })

            print(f"Saving combined dataset to {outname}...")
            print(f"Dataset shape: {dict(combined_dataset.dims)}")

            if 'OFT' in combined_dataset.dims:
                print(
                    f"Using OFT-based structure with {len(combined_dataset.coords['OFT'])} observation types"
                )

            # Use Dask to write the dataset to disk
            with dask.config.set(scheduler='threads'):
                with ProgressBar():
                    combined_dataset.to_netcdf(str(outname),
                                               encoding=encoding,
                                               engine="netcdf4",
                                               compute=True)

            return combined_dataset

        except Exception as e:
            print(f"Error in file-based concatenation: {e}")
            raise


if __name__ == '__main__':
    matcher = DataDirMatcher.from_root(
        Path('/home/nbader/Music/snr_analysis/01_Rosalia'))
    for md in matcher:
        parser = RinexFilesParser(matched_dirs=md)

        canopy_files = parser.get_rnx_file_list(pth=md.canopy_data_dir)
        sky_files = parser.get_rnx_file_list(pth=md.sky_data_dir)

        canopy_results = parser.parallel_process_rinex_files(
            rinex_files=canopy_files,
            return_ds=False,
            keep_vars=['SNR', 'Pseudorange', 'Phase', 'Doppler'],
            # max_workers=(os.cpu_count() - 2),
            # chunk_size=4,
        )

        sky_results = parser.parallel_process_rinex_files(
            rinex_files=sky_files,
            return_ds=False,
            keep_vars=['SNR', 'Pseudorange', 'Phase', 'Doppler'],
            # max_workers=(os.cpu_count() - 2),
            # chunk_size=4,
        )

        _ds_outnames = parser.make_concated_outnames()

        # Cast to List[xr.Dataset] since return_ds=True ensures datasets are returned
        from typing import cast
        canopy_datasets = cast(list[xr.Dataset], canopy_results)
        sky_datasets = cast(list[xr.Dataset], sky_results)

        canopy_ds = parser.concatentate_datasets(
            datasets=canopy_datasets,
            outname=_ds_outnames['canopy'],
            resample=False)
        sky_ds = parser.concatentate_datasets(datasets=sky_datasets,
                                              outname=_ds_outnames['sky'],
                                              resample=False)
