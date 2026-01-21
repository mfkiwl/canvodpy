"""
Storage integration helpers for working with `HemiGrid` via composition.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any
import warnings

import numpy as np
import polars as pl
import zarr

from gnssvodpy.hemigrid.storage.grid_storage import (write_grid_to_icechunk,
                                                     load_grid_from_icechunk,
                                                     LoadedGrid, GridMetadata)
from gnssvodpy.utils.tools import get_version_from_pyproject


class HemiGridStorageAdapter:
    """
    Composition-friendly adapter that knows how to persist a `HemiGrid`.

    Examples
    --------
    >>> adapter = HemiGridStorageAdapter(grid)
    >>> grid_hash = adapter.to_icechunk(session, grid_name='htm_10deg')
    """

    def __init__(self, grid):
        self._grid = grid

    def to_icechunk(self,
                    session,
                    grid_name: Optional[str] = None,
                    include_vertices: bool = True,
                    include_neighbors: bool = True,
                    overwrite: bool = False) -> str:
        """
        Write grid to an Icechunk store.

        Parameters
        ----------
        session :
            Open Icechunk writable session
        grid_name : str, optional
            Grid identifier. If None, generates from type and resolution.
        include_vertices : bool
            Include vertex data for visualization
        include_neighbors : bool
            Include neighbor adjacency data
        overwrite : bool
            Allow overwriting existing grid

        Returns
        -------
        str
            Grid hash for verification

        Examples
        --------
        >>> from gnssvodpy.icechunk_manager.store import create_vod_store
        >>>
        >>> # Create grid
        >>> grid = create_hemigrid(angular_resolution=10, grid_type='htm')
        >>>
        >>> # Open store
        >>> store = create_vod_store(Path('./vod_store'))
        >>>
        >>> adapter = HemiGridStorageAdapter(grid)
        >>> with store.writable_session() as session:
        >>>     grid_hash = adapter.to_icechunk(session, grid_name='htm_10deg')
        >>>     session.commit("Added htm_10deg grid")
        """
        # Generate grid name if not provided
        if grid_name is None:
            grid_name = f"{self._grid.grid_type}_{int(self._grid.angular_resolution)}deg"

        # Prepare cell data
        df_cells = self._prepare_cells_dataframe()

        # Prepare vertices if requested
        df_vertices = None
        if include_vertices:
            df_vertices = self._prepare_vertices_dataframe()

        # Prepare neighbors if requested
        df_neighbors = None
        if include_neighbors:
            df_neighbors = self._prepare_neighbors_dataframe()

        # Prepare metadata
        metadata = self._prepare_metadata()

        # Prepare grid-specific metadata
        specific_metadata = self._prepare_specific_metadata()

        grid_hash = write_grid_to_icechunk(session=session,
                                           grid_name=grid_name,
                                           df_cells=df_cells,
                                           df_vertices=df_vertices,
                                           df_neighbors=df_neighbors,
                                           metadata=metadata,
                                           specific_metadata=specific_metadata,
                                           overwrite=overwrite)

        return grid_hash

    @staticmethod
    def from_icechunk(session,
                      grid_name: str,
                      load_vertices: bool = True,
                      load_neighbors: bool = True) -> 'StoredHemiGrid':
        """
        Load a persisted grid and return a lightweight wrapper.
        """
        loaded = load_grid_from_icechunk(session=session,
                                         grid_name=grid_name,
                                         load_vertices=load_vertices,
                                         load_neighbors=load_neighbors)
        return StoredHemiGrid(loaded)

    # ------------------------------------------------------------------
    # Backwards-compatible adapters
    # ------------------------------------------------------------------

    def to_zarr(self, *args, **kwargs) -> str:  # pragma: no cover - legacy path
        warnings.warn(
            "HemiGridStorageAdapter.to_zarr is deprecated; "
            "use to_icechunk(session, ...) instead.",
            DeprecationWarning,
            stacklevel=2)
        if not args or not hasattr(args[0], 'store'):
            raise TypeError(
                "Legacy to_zarr usage is no longer supported. "
                "Pass an Icechunk session to to_icechunk(session, ...).")
        session = args[0]
        remaining_args = args[1:]
        return self.to_icechunk(session, *remaining_args, **kwargs)

    @staticmethod
    def from_zarr(*args, **kwargs):  # pragma: no cover - legacy path
        warnings.warn(
            "HemiGridStorageAdapter.from_zarr is deprecated; "
            "use from_icechunk(session, ...) instead.",
            DeprecationWarning,
            stacklevel=2)
        return HemiGridStorageAdapter.from_icechunk(*args, **kwargs)

    # -------------------------------------------------------------------------
    # Internal helper methods (implement based on your HemiGrid structure)
    # -------------------------------------------------------------------------

    def _prepare_cells_dataframe(self) -> pl.DataFrame:
        """
        Prepare cells DataFrame for storage.

        Must contain columns:
        - cell_id (int)
        - phi, theta (float) - cell centers
        - x, y, z (float) - Cartesian centers
        - solid_angle (float) - steradians
        - is_boundary (bool)
        - phi_min, phi_max, theta_min, theta_max (float, NaN for non-rectangular)

        Implement based on your internal grid structure.
        """
        df = self._grid.grid.clone()

        # Ensure required columns exist
        required = ['phi', 'theta']
        for col in required:
            if col not in df.columns:
                raise ValueError(f"Grid missing required column: {col}")

        # Add cell_id if not present
        if 'cell_id' not in df.columns:
            df = df.with_columns(pl.int_range(0, pl.len()).alias('cell_id'))

        # Ensure rectangular bounds columns exist (fill with NaN for irregular grids)
        for col in ['phi_min', 'phi_max', 'theta_min', 'theta_max']:
            if col not in df.columns:
                df = df.with_columns(pl.lit(float('nan')).alias(col))

        # Add Cartesian coordinates if not present
        if 'x' not in df.columns:
            df = df.with_columns([
                (pl.col('theta').sin() * pl.col('phi').cos()).alias('x'),
                (pl.col('theta').sin() * pl.col('phi').sin()).alias('y'),
                pl.col('theta').cos().alias('z')
            ])

        # Add solid angles from grid geometry
        if 'solid_angle' not in df.columns:
            solid_angles = self._grid.get_solid_angles()
            if solid_angles is None:
                raise ValueError("Unable to compute solid angles for grid")
            df = df.with_columns(
                pl.Series(name='solid_angle', values=solid_angles))

        # Add is_boundary flag
        if 'is_boundary' not in df.columns:
            cutoff_rad = np.deg2rad(self._grid.cutoff_theta)
            horizon_threshold = (np.pi / 2) - cutoff_rad - 1e-6
            if 'theta_max' in df.columns:
                theta_expr = pl.col('theta_max').fill_null(pl.col('theta'))
            else:
                theta_expr = pl.col('theta')
            df = df.with_columns(
                (theta_expr >= horizon_threshold).alias('is_boundary'))

        # Ensure column order roughly matches expectations
        desired_order = [
            'cell_id', 'phi', 'theta', 'x', 'y', 'z', 'solid_angle',
            'is_boundary', 'phi_min', 'phi_max', 'theta_min', 'theta_max'
        ]
        existing = [col for col in desired_order if col in df.columns]
        remaining = [col for col in df.columns if col not in desired_order]
        df = df.select(existing + remaining)
        return df

    def _prepare_vertices_dataframe(self) -> Optional[pl.DataFrame]:
        """
        Prepare vertices DataFrame for storage.

        Must contain columns:
        - cell_id (int) - which cell this vertex belongs to
        - vertex_idx (int) - vertex index within cell (0, 1, 2, ...)
        - phi, theta (float) - vertex coordinates
        - x, y, z (float) - Cartesian coordinates

        Returns None if vertices not computed/available.
        """
        grid_df = self._grid.grid
        records = []

        # Rectangular grids (equal-area, equal-angle, etc.)
        grid_type = self._grid.grid_type

        if grid_type in ['equal_area', 'equal_angle', 'equirectangular',
                         'healpix']:
            bounds_cols = {'phi_min', 'phi_max', 'theta_min', 'theta_max'}
            if bounds_cols.issubset(set(grid_df.columns)):
                for row in grid_df.iter_rows(named=True):
                    phi_min = row['phi_min']
                    phi_max = row['phi_max']
                    theta_min = row['theta_min']
                    theta_max = row['theta_max']

                    if any(np.isnan(val)
                           for val in [phi_min, phi_max, theta_min, theta_max]):
                        continue

                    corners = [
                        (phi_min, theta_min),
                        (phi_max, theta_min),
                        (phi_max, theta_max),
                        (phi_min, theta_max),
                    ]
                    for idx, (phi, theta) in enumerate(corners):
                        x = np.sin(theta) * np.cos(phi)
                        y = np.sin(theta) * np.sin(phi)
                        z = np.cos(theta)
                        records.append({
                            'cell_id': int(row['cell_id']),
                            'vertex_idx': idx,
                            'phi': float(np.mod(phi, 2 * np.pi)),
                            'theta': float(theta),
                            'x': float(x),
                            'y': float(y),
                            'z': float(z),
                        })

        # HTM triangular grids with per-cell vertex definitions
        elif grid_type == 'htm':
            vertex_cols = {'htm_vertex_0', 'htm_vertex_1', 'htm_vertex_2'}
            if vertex_cols.issubset(set(grid_df.columns)):
                for row in grid_df.iter_rows(named=True):
                    raw_vertices = [
                        np.asarray(row['htm_vertex_0'], dtype=float),
                        np.asarray(row['htm_vertex_1'], dtype=float),
                        np.asarray(row['htm_vertex_2'], dtype=float),
                    ]
                    for idx, vector in enumerate(raw_vertices):
                        norm = np.linalg.norm(vector)
                        if norm == 0:
                            continue
                        x, y, z = vector / norm
                        theta = np.arccos(np.clip(z, -1, 1))
                        phi = np.mod(np.arctan2(y, x), 2 * np.pi)
                        records.append({
                            'cell_id': int(row['cell_id']),
                            'vertex_idx': idx,
                            'phi': float(phi),
                            'theta': float(theta),
                            'x': float(x),
                            'y': float(y),
                            'z': float(z),
                        })

        # Geodesic grids share vertex arrays via metadata
        elif grid_type == 'geodesic':
            grid_data = getattr(self._grid, '_grid_data', None)
            shared_vertices = getattr(grid_data, 'vertices',
                                      None) if grid_data else None
            if shared_vertices is not None and 'geodesic_vertices' in grid_df.columns:
                shared_vertices = np.asarray(shared_vertices, dtype=float)
                for row in grid_df.iter_rows(named=True):
                    indices = row['geodesic_vertices']
                    for idx, vertex_idx in enumerate(indices):
                        vector = shared_vertices[int(vertex_idx)]
                        norm = np.linalg.norm(vector)
                        if norm == 0:
                            continue
                        x, y, z = vector / norm
                        theta = np.arccos(np.clip(z, -1, 1))
                        phi = np.mod(np.arctan2(y, x), 2 * np.pi)
                        records.append({
                            'cell_id': int(row['cell_id']),
                            'vertex_idx': idx,
                            'phi': float(phi),
                            'theta': float(theta),
                            'x': float(x),
                            'y': float(y),
                            'z': float(z),
                        })

        if not records:
            return None

        return pl.DataFrame(records)

    def _prepare_neighbors_dataframe(self) -> Optional[pl.DataFrame]:
        """
        Prepare neighbors DataFrame for storage.

        Must contain columns:
        - cell_id (int) - source cell
        - neighbor_id (int) - neighboring cell

        Returns None if neighbor relationships not computed/available.
        """
        # TODO: Implement based on your neighbor storage

        neighbors = getattr(self._grid, '_neighbors', None)

        if neighbors is None:
            return None

        # If neighbors already in correct format
        if isinstance(neighbors, pl.DataFrame):
            return neighbors.clone()
        else:
            # Convert from your internal format
            converter = getattr(self._grid, '_convert_neighbors_to_dataframe',
                                None)
            if converter is None:
                return None
            return converter()

    def _prepare_metadata(self) -> Dict[str, Any]:
        """Prepare grid metadata."""
        cutoff_rad = float(np.deg2rad(self._grid.cutoff_theta))
        return {
            'grid_type': self._grid.grid_type,
            'angular_resolution': float(self._grid.angular_resolution),
            'cutoff_theta': cutoff_rad,
            'ncells': int(self._grid.ncells),
            'creation_timestamp': datetime.now(timezone.utc).isoformat(),
            'creation_software': f"gnssvodpy=={get_version_from_pyproject()}",
            'immutable': True,
        }

    def _prepare_specific_metadata(self) -> Dict[str, Any]:
        """
        Prepare grid-type-specific metadata.

        Override in subclasses for grid-specific parameters.
        """
        metadata = {}

        builder = getattr(self._grid, '_builder', None)
        grid_type = self._grid.grid_type

        if grid_type == 'htm':
            if builder and hasattr(builder, 'htm_level'):
                metadata['htm_level'] = int(builder.htm_level)
            metadata['base_triangles'] = 8

        elif grid_type == 'equal_area':
            theta_lims = getattr(self._grid, 'theta_lims', None)
            if theta_lims is not None:
                metadata['theta_band_edges'] = [float(v) for v in theta_lims]
            metadata['cutoff_theta_deg'] = float(self._grid.cutoff_theta)

        elif grid_type == 'geodesic':
            if builder and hasattr(builder, 'subdivision_level'):
                metadata['subdivision_level'] = int(builder.subdivision_level)
            metadata['base_icosahedron'] = True

        elif grid_type == 'healpix':
            if 'healpix_nside' in self._grid.grid.columns:
                nside = int(self._grid.grid['healpix_nside'][0])
                metadata['healpix_nside'] = nside

        elif grid_type == 'fibonacci':
            grid_data = getattr(self._grid, '_grid_data', None)
            if grid_data and getattr(grid_data, 'points_xyz', None) is not None:
                metadata['n_points'] = int(len(grid_data.points_xyz))

        return metadata

    def _get_neighbors_dataframe(self) -> Optional[pl.DataFrame]:
        return self._prepare_neighbors_dataframe()


class StoredHemiGrid:
    """
    Lightweight wrapper around `LoadedGrid` providing a familiar interface.
    """

    def __init__(self, loaded_grid: LoadedGrid):
        self._loaded = loaded_grid

    @property
    def metadata(self) -> GridMetadata:
        return self._loaded.metadata

    @property
    def grid_type(self) -> str:
        return self._loaded.metadata.grid_type

    @property
    def angular_resolution(self) -> float:
        return self._loaded.metadata.angular_resolution

    @property
    def cutoff_theta(self) -> float:
        return self._loaded.metadata.cutoff_theta

    @property
    def cells(self) -> pl.DataFrame:
        return self._loaded.cells

    @property
    def ncells(self) -> int:
        return self._loaded.metadata.ncells

    @property
    def grid(self) -> pl.DataFrame:
        """
        Compatibility alias matching the original HemiGrid API.
        """
        return self._loaded.cells

    @property
    def vertices(self) -> Optional[pl.DataFrame]:
        return self._loaded.vertices

    @property
    def neighbors(self) -> Optional[pl.DataFrame]:
        return self._loaded.neighbors

    def query_point(self, phi: float, theta: float) -> int:
        return self._loaded.query_point(phi, theta)

    def query_points(self, phi: np.ndarray, theta: np.ndarray) -> np.ndarray:
        return self._loaded.query_points(phi, theta)

    def __repr__(self) -> str:
        return (f"StoredHemiGrid(name='{self._loaded.grid_name}', "
                f"type='{self.grid_type}', "
                f"ncells={self.metadata.ncells})")


# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================


def store_grid_to_vod_store(grid,
                            store_path: Path,
                            grid_name: Optional[str] = None,
                            branch: str = "main",
                            *,
                            include_vertices: bool = True,
                            include_neighbors: bool = False,
                            overwrite: bool = False) -> str:
    """
    Convenience function to store grid in VOD store.

    Parameters
    ----------
    grid : HemiGrid
        Grid instance to store
    store_path : Path
        Path to VOD store
    grid_name : str, optional
        Grid identifier (auto-generated if None)
    branch : str
        Branch name
    include_vertices : bool
        Whether to include vertex data in storage
    include_neighbors : bool
        Whether to include neighbor adjacency (requires precomputed data)
    overwrite : bool
        Allow overwriting an existing grid definition

    Returns
    -------
    str
        Snapshot ID

    Examples
    --------
    >>> from gnssvodpy.hemigrid.core.hemigrid import create_hemigrid
    >>>
    >>> grid = create_hemigrid(angular_resolution=10, grid_type='htm')
    >>> snapshot_id = store_grid_to_vod_store(
    ...     grid,
    ...     Path('./vod_store'),
    ...     grid_name='htm_10deg'
    ... )
    """
    from gnssvodpy.icechunk_manager.store import create_vod_store

    store = create_vod_store(store_path)

    with store.writable_session(branch) as session:
        if grid_name is None:
            grid_name = f"{grid.grid_type}_{int(grid.angular_resolution)}deg"

        adapter = HemiGridStorageAdapter(grid)

        grid_hash = adapter.to_icechunk(session,
                                        grid_name=grid_name,
                                        include_vertices=include_vertices,
                                        include_neighbors=include_neighbors,
                                        overwrite=overwrite)

        commit_msg = f"Added grid: {grid_name} (hash: {grid_hash[:8]})"
        snapshot_id = session.commit(commit_msg)

    print(f"✓ Grid stored: {grid_name}")
    print(f"  Snapshot: {snapshot_id[:8]}")
    print(f"  Hash: {grid_hash[:16]}")

    return snapshot_id


def load_grid_from_vod_store(store_path: Path,
                             grid_name: str,
                             branch: str = "main",
                             *,
                             load_vertices: bool = True,
                             load_neighbors: bool = True) -> StoredHemiGrid:
    """
    Convenience function to load grid from VOD store.

    Parameters
    ----------
    store_path : Path
        Path to VOD store
    grid_name : str
        Grid identifier
    branch : str
        Branch name

    Returns
    -------
    StoredHemiGrid
        Loaded grid wrapper

    Examples
    --------
    >>> grid = load_grid_from_vod_store(
    ...     Path('./vod_store'),
    ...     'htm_10deg'
    ... )
    >>> cell_id = grid.query_point(phi=1.5, theta=0.3)
    """
    from gnssvodpy.icechunk_manager.store import create_vod_store

    store = create_vod_store(store_path)

    with store.readonly_session(branch) as session:
        stored = HemiGridStorageAdapter.from_icechunk(
            session,
            grid_name,
            load_vertices=load_vertices,
            load_neighbors=load_neighbors,
        )

    print(f"✓ Grid loaded: {grid_name}")
    print(f"  Type: {stored.grid_type}")
    print(f"  Cells: {stored.metadata.ncells}")

    return stored


def list_available_grids(store_path: Path, branch: str = "main") -> list[str]:
    """
    List all available grids in a VOD store.

    Parameters
    ----------
    store_path : Path
        Path to VOD store
    branch : str
        Branch name

    Returns
    -------
    list[str]
        List of grid names

    Examples
    --------
    >>> grids = list_available_grids(Path('./vod_store'))
    >>> print(grids)
    ['htm_10deg', 'equal_area_10deg', 'htm_5deg']
    """
    from gnssvodpy.icechunk_manager.store import create_vod_store

    store = create_vod_store(store_path)

    with store.readonly_session(branch) as session:
        zroot = zarr.open_group(session.store, mode='r')

        if 'grids' not in zroot:
            return []

        grids_group = zroot['grids']
        return list(grids_group.group_keys())


# ==============================================================================
# EXAMPLE USAGE
# ==============================================================================

if __name__ == "__main__":
    from pathlib import Path
    from gnssvodpy.hemigrid.core.hemigrid import create_hemigrid

    # Create a grid
    print("Creating HTM grid...")
    grid = create_hemigrid(angular_resolution=10, grid_type='htm')

    # Store it
    store_path = Path("./test_vod_store")
    print(f"\nStoring grid to {store_path}...")
    snapshot_id = store_grid_to_vod_store(grid,
                                          store_path,
                                          grid_name='htm_10deg')

    # List available grids
    print("\nAvailable grids:")
    grids = list_available_grids(store_path)
    for g in grids:
        print(f"  - {g}")

    # Load it back
    print("\nLoading grid from store...")
    loaded_grid = load_grid_from_vod_store(store_path, 'htm_10deg')

    # Test query
    print("\nTesting point query...")
    phi_test = 1.5
    theta_test = 0.3
    cell_id = loaded_grid.query_point(phi_test, theta_test)
    print(f"  Point (φ={phi_test:.2f}, θ={theta_test:.2f}) → Cell {cell_id}")

    # Test vectorized query
    print("\nTesting vectorized query...")
    phi_arr = np.array([0.5, 1.0, 1.5, 2.0])
    theta_arr = np.array([0.2, 0.3, 0.4, 0.5])
    cell_ids = loaded_grid.query_points(phi_arr, theta_arr)
    print(f"  {len(cell_ids)} points assigned to cells: {cell_ids}")

    print("\n✓ All tests passed!")
