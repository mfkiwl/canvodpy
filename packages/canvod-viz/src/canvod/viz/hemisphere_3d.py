"""3D hemisphere visualization using plotly for interactive exploration.

Provides interactive 3D sphere surface plots with zoom, pan, and rotation capabilities.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import plotly.graph_objects as go
from canvod.viz.styles import PlotStyle
from plotly.colors import sample_colorscale

if TYPE_CHECKING:
    from canvod.grids import HemiGrid


class HemisphereVisualizer3D:
    """3D hemisphere visualization using plotly.
    
    Creates interactive 3D plots with rotation, zoom, and hover capabilities.
    Designed for exploratory data analysis and presentations.
    
    Parameters
    ----------
    grid : HemiGrid
        Hemisphere grid to visualize
    
    Examples
    --------
    >>> from canvod.grids import create_hemigrid
    >>> from canvod.viz import HemisphereVisualizer3D
    >>> 
    >>> grid = create_hemigrid(grid_type='equal_area', angular_resolution=10.0)
    >>> viz = HemisphereVisualizer3D(grid)
    >>> fig = viz.plot_hemisphere_surface(data=vod_data, title="Interactive VOD")
    >>> fig.show()

    """

    def __init__(self, grid: HemiGrid):
        """Initialize 3D hemisphere visualizer.
        
        Parameters
        ----------
        grid : HemiGrid
            Hemisphere grid to visualize

        """
        self.grid = grid

    def plot_hemisphere_surface(
        self,
        data: np.ndarray | None = None,
        style: PlotStyle | None = None,
        title: str | None = None,
        colorscale: str = "Viridis",
        opacity: float = 0.8,
        show_wireframe: bool = True,
        show_colorbar: bool = True,
        width: int = 800,
        height: int = 600,
        **kwargs,
    ) -> go.Figure:
        """Create 3D surface plot on hemisphere.
        
        Parameters
        ----------
        data : np.ndarray, optional
            Data values per cell. If None, shows grid structure.
        style : PlotStyle, optional
            Styling configuration. If None, uses defaults.
        title : str, optional
            Plot title
        colorscale : str, default 'Viridis'
            Plotly colorscale name
        opacity : float, default 0.8
            Surface opacity (0=transparent, 1=opaque)
        show_wireframe : bool, default True
            Show grid lines on surface
        show_colorbar : bool, default True
            Display colorbar
        width : int, default 800
            Figure width in pixels
        height : int, default 600
            Figure height in pixels
        **kwargs
            Additional plotly trace parameters
        
        Returns
        -------
        plotly.graph_objects.Figure
            Interactive 3D figure
        
        Examples
        --------
        >>> fig = viz.plot_hemisphere_surface(
        ...     data=vod_data,
        ...     title="VOD Distribution 3D",
        ...     colorscale='Plasma',
        ...     opacity=0.9
        ... )
        >>> fig.write_html("vod_3d.html")

        """
        # Initialize style
        if style is None:
            style = PlotStyle()
            colorscale = colorscale  # Use parameter
        else:
            colorscale = style.colorscale

        # Get cell centers in 3D
        theta = np.array([cell.theta for cell in self.grid.cells])
        phi = np.array([cell.phi for cell in self.grid.cells])

        # Convert to 3D Cartesian coordinates
        x = np.sin(theta) * np.cos(phi)
        y = np.sin(theta) * np.sin(phi)
        z = np.cos(theta)

        # Prepare data values
        if data is None:
            values = np.ones(len(self.grid.cells)) * 0.5
        else:
            values = data

        # Filter hemisphere only
        hemisphere_mask = theta <= np.pi / 2
        x = x[hemisphere_mask]
        y = y[hemisphere_mask]
        z = z[hemisphere_mask]
        values = values[hemisphere_mask]

        # Create scatter3d trace
        trace = go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode="markers",
            marker=dict(
                size=6,
                color=values,
                colorscale=colorscale,
                opacity=opacity,
                colorbar=dict(title="Value") if show_colorbar else None,
                cmin=np.nanmin(values),
                cmax=np.nanmax(values),
            ),
            text=[f"Cell {i}<br>Value: {v:.3f}" for i, v in enumerate(values)],
            hoverinfo="text",
            **kwargs
        )

        fig = go.Figure(data=[trace])

        # Apply layout
        layout_config = style.to_plotly_layout() if style else {}
        layout_config.update({
            "title": title or "Hemisphere 3D",
            "scene": dict(
                aspectmode="data",
                xaxis=dict(title="East", showbackground=False),
                yaxis=dict(title="North", showbackground=False),
                zaxis=dict(title="Up", showbackground=False),
                bgcolor=layout_config.get("plot_bgcolor", "white")
            ),
            "width": width,
            "height": height,
            "margin": dict(l=0, r=0, b=0, t=40),
        })

        fig.update_layout(**layout_config)

        return fig

    def plot_hemisphere_scatter(
        self,
        data: np.ndarray | None = None,
        title: str | None = None,
        colorscale: str = "Viridis",
        marker_size: int | np.ndarray = 6,
        opacity: float = 0.8,
        width: int = 800,
        height: int = 600,
    ) -> go.Figure:
        """Create 3D scatter plot of cell centers.
        
        Parameters
        ----------
        data : np.ndarray, optional
            Data values per cell
        title : str, optional
            Plot title
        colorscale : str, default 'Viridis'
            Plotly colorscale name
        marker_size : int or np.ndarray, default 6
            Marker size (constant or per-point array)
        opacity : float, default 0.8
            Marker opacity
        width : int, default 800
            Figure width
        height : int, default 600
            Figure height
        
        Returns
        -------
        plotly.graph_objects.Figure
            Interactive scatter plot

        """
        # Create figure using parent method, updating marker size
        fig = self.plot_hemisphere_surface(
            data=data,
            title=title,
            colorscale=colorscale,
            opacity=opacity,
            width=width,
            height=height
        )

        # Update marker size if different from default
        if marker_size != 6:
            fig.data[0].marker.size = marker_size

        return fig

    def plot_cell_mesh(
        self,
        data: np.ndarray | None = None,
        title: str | None = None,
        colorscale: str = "Viridis",
        opacity: float = 0.7,
        show_edges: bool = True,
        width: int = 800,
        height: int = 600,
    ) -> go.Figure:
        """Create 3D mesh plot showing cell boundaries.
        
        Parameters
        ----------
        data : np.ndarray, optional
            Data values per cell
        title : str, optional
            Plot title
        colorscale : str, default 'Viridis'
            Plotly colorscale name
        opacity : float, default 0.7
            Mesh opacity
        show_edges : bool, default True
            Show cell edges
        width : int, default 800
            Figure width
        height : int, default 600
            Figure height
        
        Returns
        -------
        plotly.graph_objects.Figure
            Interactive mesh plot
        
        Notes
        -----
        This method requires grid cells with vertex information.
        Currently supports HTM and geodesic grids.

        """
        traces = []

        # Prepare data
        if data is None:
            values = np.ones(len(self.grid.cells)) * 0.5
        else:
            values = data

        # Sample colorscale
        colors = sample_colorscale(
            colorscale,
            [v / (np.nanmax(values) - np.nanmin(values)) for v in values]
        )

        # Create mesh for each cell
        for idx, cell in enumerate(self.grid.cells):
            if cell.htm_vertices is None:
                continue

            vertices = cell.htm_vertices
            if vertices.shape[0] != 3:
                continue  # Skip non-triangular cells

            # Check hemisphere
            z_coords = vertices[:, 2]
            if np.all(z_coords < 0):
                continue

            # Create triangle mesh
            trace = go.Mesh3d(
                x=vertices[:, 0],
                y=vertices[:, 1],
                z=vertices[:, 2],
                i=[0],
                j=[1],
                k=[2],
                color=colors[idx],
                opacity=opacity,
                flatshading=True,
                showscale=False,
                hoverinfo="skip"
            )
            traces.append(trace)

        # Add colorbar trace
        if values is not None and len(traces) > 0:
            dummy_trace = go.Scatter3d(
                x=[None],
                y=[None],
                z=[None],
                mode="markers",
                marker=dict(
                    size=0.1,
                    color=[np.nanmin(values), np.nanmax(values)],
                    colorscale=colorscale,
                    colorbar=dict(title="Value"),
                ),
                showlegend=False,
                hoverinfo="skip"
            )
            traces.append(dummy_trace)

        fig = go.Figure(data=traces)

        # Update layout
        fig.update_layout(
            title=title or "Hemisphere Mesh 3D",
            scene=dict(
                aspectmode="data",
                xaxis=dict(title="East", showbackground=False),
                yaxis=dict(title="North", showbackground=False),
                zaxis=dict(title="Up", showbackground=False),
            ),
            width=width,
            height=height,
            margin=dict(l=0, r=0, b=0, t=40),
        )

        return fig
