"""2D hemisphere visualization using matplotlib for publication-quality plots.

Provides polar projection plotting of hemispherical grids with various rendering methods.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
from canvod.viz.styles import PolarPlotStyle
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon

if TYPE_CHECKING:
    from canvod.grids import HemiGrid
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


class HemisphereVisualizer2D:
    """2D hemisphere visualization using matplotlib.
    
    Creates publication-quality polar projection plots of hemispherical grids.
    Supports multiple grid types and rendering methods.
    
    Parameters
    ----------
    grid : HemiGrid
        Hemisphere grid to visualize
    
    Examples
    --------
    >>> from canvod.grids import create_hemigrid
    >>> from canvod.viz import HemisphereVisualizer2D
    >>> 
    >>> grid = create_hemigrid(grid_type='equal_area', angular_resolution=10.0)
    >>> viz = HemisphereVisualizer2D(grid)
    >>> fig, ax = viz.plot_grid_patches(data=vod_data, title="VOD Distribution")
    >>> plt.savefig("vod_plot.png", dpi=300, bbox_inches='tight')

    """

    def __init__(self, grid: HemiGrid):
        """Initialize 2D hemisphere visualizer.
        
        Parameters
        ----------
        grid : HemiGrid
            Hemisphere grid to visualize

        """
        self.grid = grid
        self._patches_cache: list[Polygon] | None = None
        self._cell_indices_cache: np.ndarray | None = None

    def plot_grid_patches(
        self,
        data: np.ndarray | None = None,
        style: PolarPlotStyle | None = None,
        ax: Axes | None = None,
        save_path: Path | str | None = None,
        **style_kwargs,
    ) -> tuple[Figure, Axes]:
        """Plot hemisphere grid as colored patches in polar projection.
        
        Parameters
        ----------
        data : np.ndarray, optional
            Data values per cell. If None, plots uniform grid.
        style : PolarPlotStyle, optional
            Styling configuration. If None, uses defaults.
        ax : matplotlib.axes.Axes, optional
            Existing polar axes to plot on. If None, creates new figure.
        save_path : Path or str, optional
            If provided, saves figure to this path
        **style_kwargs
            Override individual style parameters
        
        Returns
        -------
        fig : matplotlib.figure.Figure
            Figure object
        ax : matplotlib.axes.Axes
            Polar axes with plot
        
        Examples
        --------
        >>> fig, ax = viz.plot_grid_patches(
        ...     data=vod_data,
        ...     title="VOD Distribution",
        ...     cmap='plasma',
        ...     save_path="output.png"
        ... )

        """
        # Initialize style
        if style is None:
            style = PolarPlotStyle(**style_kwargs)
        else:
            # Override style with kwargs
            for key, value in style_kwargs.items():
                if hasattr(style, key):
                    setattr(style, key, value)

        # Create figure if needed
        if ax is None:
            fig, ax = plt.subplots(
                figsize=style.figsize,
                dpi=style.dpi,
                subplot_kw={"projection": "polar"}
            )
        else:
            fig = ax.figure

        # Get patches for grid
        patches, cell_indices = self._extract_grid_patches()

        # Map data to patches
        patch_data = self._map_data_to_patches(data, cell_indices)

        # Determine color limits
        vmin = style.vmin if style.vmin is not None else np.nanmin(patch_data)
        vmax = style.vmax if style.vmax is not None else np.nanmax(patch_data)

        # Create patch collection
        pc = PatchCollection(
            patches,
            cmap=style.cmap,
            edgecolor=style.edgecolor,
            linewidth=style.linewidth,
            alpha=style.alpha
        )
        pc.set_array(np.ma.masked_invalid(patch_data))
        pc.set_clim(vmin, vmax)

        # Add to axes
        ax.add_collection(pc)

        # Style polar axes
        self._apply_polar_styling(ax, style)

        # Add colorbar
        cbar = fig.colorbar(pc, ax=ax, shrink=style.colorbar_shrink, pad=style.colorbar_pad)
        cbar.set_label(style.colorbar_label, fontsize=style.colorbar_fontsize)

        # Set title
        if style.title:
            ax.set_title(style.title, y=1.08, fontsize=14)

        # Save if requested
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(
                save_path,
                dpi=style.dpi,
                bbox_inches="tight",
                facecolor="white",
                edgecolor="none"
            )

        return fig, ax

    def _extract_grid_patches(self) -> tuple[list[Polygon], np.ndarray]:
        """Extract 2D polygon patches from hemispherical grid.
        
        Returns
        -------
        patches : list of Polygon
            Matplotlib polygon patches
        cell_indices : np.ndarray
            Corresponding cell indices in grid

        """
        # Use cache if available
        if self._patches_cache is not None and self._cell_indices_cache is not None:
            return self._patches_cache, self._cell_indices_cache

        grid_type = self.grid.grid_type.lower()

        if "equal_area" in grid_type or "rectangular" in grid_type:
            patches, indices = self._extract_rectangular_patches()
        elif "htm" in grid_type:
            patches, indices = self._extract_htm_patches()
        elif "geodesic" in grid_type:
            patches, indices = self._extract_geodesic_patches()
        elif "healpix" in grid_type:
            patches, indices = self._extract_healpix_patches()
        elif "fibonacci" in grid_type:
            patches, indices = self._extract_fibonacci_patches()
        else:
            raise ValueError(f"Unsupported grid type: {grid_type}")

        # Cache results
        self._patches_cache = patches
        self._cell_indices_cache = indices

        return patches, indices

    def _extract_rectangular_patches(self) -> tuple[list[Polygon], np.ndarray]:
        """Extract patches from rectangular/equal-area grid."""
        patches = []
        cell_indices = []

        for idx, cell in enumerate(self.grid.cells):
            phi_min, phi_max = cell.phi_lims
            theta_min, theta_max = cell.theta_lims

            # Skip cells beyond hemisphere
            if theta_min > np.pi / 2:
                continue

            # Convert to polar coordinates (rho = sin(theta))
            rho_min = np.sin(theta_min)
            rho_max = np.sin(theta_max)

            # Create rectangular patch in polar coordinates
            vertices = np.array([
                [phi_min, rho_min],
                [phi_max, rho_min],
                [phi_max, rho_max],
                [phi_min, rho_max],
            ])

            patches.append(Polygon(vertices, closed=True))
            cell_indices.append(idx)

        return patches, np.array(cell_indices)

    def _extract_htm_patches(self) -> tuple[list[Polygon], np.ndarray]:
        """Extract triangular patches from HTM grid."""
        patches = []
        cell_indices = []

        for idx, cell in enumerate(self.grid.cells):
            # Get 3D vertices
            vertices_3d = cell.htm_vertices
            if vertices_3d is None:
                continue

            # Convert to spherical coordinates
            x, y, z = vertices_3d[:, 0], vertices_3d[:, 1], vertices_3d[:, 2]
            r = np.sqrt(x**2 + y**2 + z**2)
            theta = np.arccos(np.clip(z / r, -1, 1))
            phi = np.arctan2(y, x)
            phi = np.mod(phi, 2 * np.pi)

            # Skip if beyond hemisphere
            if np.all(theta > np.pi / 2):
                continue

            # Convert to polar coordinates
            rho = np.sin(theta)
            vertices_2d = np.column_stack([phi, rho])

            patches.append(Polygon(vertices_2d, closed=True))
            cell_indices.append(idx)

        return patches, np.array(cell_indices)

    def _extract_geodesic_patches(self) -> tuple[list[Polygon], np.ndarray]:
        """Extract patches from geodesic grid."""
        # Similar to HTM but may have different vertex structure
        return self._extract_htm_patches()

    def _extract_healpix_patches(self) -> tuple[list[Polygon], np.ndarray]:
        """Extract patches from HEALPix grid (placeholder)."""
        # HEALPix requires special handling
        raise NotImplementedError("HEALPix 2D visualization not yet implemented")

    def _extract_fibonacci_patches(self) -> tuple[list[Polygon], np.ndarray]:
        """Extract patches from Fibonacci grid (placeholder)."""
        # Fibonacci grid uses point-based representation
        raise NotImplementedError("Fibonacci 2D visualization not yet implemented")

    def _map_data_to_patches(self, data: np.ndarray | None, cell_indices: np.ndarray) -> np.ndarray:
        """Map data values to patches.
        
        Parameters
        ----------
        data : np.ndarray or None
            Data per grid cell
        cell_indices : np.ndarray
            Cell indices corresponding to patches
        
        Returns
        -------
        np.ndarray
            Data values for each patch

        """
        if data is None:
            return np.ones(len(cell_indices)) * 0.5

        return data[cell_indices]

    def _apply_polar_styling(self, ax: Axes, style: PolarPlotStyle):
        """Apply styling to polar axes.
        
        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Polar axes to style
        style : PolarPlotStyle
            Styling configuration

        """
        # Set rho limits (0 to 1 for hemisphere projection)
        ax.set_ylim(0, 1.0)

        # Configure polar axis orientation
        ax.set_theta_zero_location("N")  # North at top
        ax.set_theta_direction(-1)  # Clockwise (azimuth convention)

        # Add degree labels on radial axis
        if style.show_degree_labels:
            theta_labels = style.theta_labels
            rho_ticks = [np.sin(np.radians(t)) for t in theta_labels]
            ax.set_yticks(rho_ticks)
            ax.set_yticklabels([f"{t}°" for t in theta_labels])

        # Grid styling
        if style.show_grid:
            ax.grid(
                True,
                alpha=style.grid_alpha,
                linestyle=style.grid_linestyle,
                color="gray"
            )
        else:
            ax.grid(False)
