"""Styling configuration for visualizations.

Provides consistent styling across 2D matplotlib and 3D plotly visualizations.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PolarPlotStyle:
    """Configuration for 2D polar plot styling (matplotlib).
    
    Parameters
    ----------
    cmap : str, default 'viridis'
        Matplotlib colormap name
    edgecolor : str, default 'black'
        Edge color for grid cells
    linewidth : float, default 0.5
        Line width for cell edges
    alpha : float, default 1.0
        Transparency (0=transparent, 1=opaque)
    vmin : float or None, optional
        Minimum value for colormap
    vmax : float or None, optional
        Maximum value for colormap
    title : str or None, optional
        Plot title
    figsize : tuple of float, default (10, 10)
        Figure size in inches (width, height)
    dpi : int, default 100
        Dots per inch for figure
    colorbar_label : str, default 'Value'
        Label for colorbar
    colorbar_shrink : float, default 0.8
        Colorbar size relative to axis
    colorbar_pad : float, default 0.1
        Space between axis and colorbar
    colorbar_fontsize : int, default 11
        Font size for colorbar label
    show_grid : bool, default True
        Show polar grid lines
    grid_alpha : float, default 0.3
        Grid line transparency
    grid_linestyle : str, default '--'
        Grid line style
    show_degree_labels : bool, default True
        Show degree labels on radial axis
    theta_labels : list of int, default [0, 30, 60, 90]
        Elevation angles for labels (degrees)
    """
    
    cmap: str = 'viridis'
    edgecolor: str = 'black'
    linewidth: float = 0.5
    alpha: float = 1.0
    vmin: float | None = None
    vmax: float | None = None
    title: str | None = None
    figsize: tuple[float, float] = (10, 10)
    dpi: int = 100
    colorbar_label: str = 'Value'
    colorbar_shrink: float = 0.8
    colorbar_pad: float = 0.1
    colorbar_fontsize: int = 11
    show_grid: bool = True
    grid_alpha: float = 0.3
    grid_linestyle: str = '--'
    show_degree_labels: bool = True
    theta_labels: list[int] = field(default_factory=lambda: [0, 30, 60, 90])


@dataclass
class PlotStyle:
    """Unified styling configuration for both 2D and 3D plots.
    
    Parameters
    ----------
    colormap : str, default 'viridis'
        Colormap name (matplotlib or plotly)
    colorscale : str, default 'Viridis'
        Plotly colorscale name
    background_color : str, default 'white'
        Background color
    text_color : str, default 'black'
        Text color
    grid_color : str, default 'lightgray'
        Grid line color
    font_family : str, default 'sans-serif'
        Font family
    font_size : int, default 11
        Base font size
    title_size : int, default 14
        Title font size
    label_size : int, default 12
        Axis label font size
    edge_linewidth : float, default 0.5
        Edge line width for cells
    opacity : float, default 0.8
        3D surface opacity
    marker_size : int, default 8
        3D marker size
    line_width : int, default 1
        3D line width
    wireframe_opacity : float, default 0.2
        3D wireframe transparency
    dark_mode : bool, default False
        Use dark theme
    """
    
    colormap: str = 'viridis'
    colorscale: str = 'Viridis'
    background_color: str = 'white'
    text_color: str = 'black'
    grid_color: str = 'lightgray'
    font_family: str = 'sans-serif'
    font_size: int = 11
    title_size: int = 14
    label_size: int = 12
    edge_linewidth: float = 0.5
    opacity: float = 0.8
    marker_size: int = 8
    line_width: int = 1
    wireframe_opacity: float = 0.2
    dark_mode: bool = False
    
    def to_polar_style(self) -> PolarPlotStyle:
        """Convert to PolarPlotStyle for 2D matplotlib plots.
        
        Returns
        -------
        PolarPlotStyle
            Equivalent 2D styling configuration
        """
        return PolarPlotStyle(
            cmap=self.colormap,
            edgecolor='white' if self.dark_mode else self.text_color,
            linewidth=self.edge_linewidth,
            alpha=1.0,
            colorbar_fontsize=self.font_size,
        )
    
    def to_plotly_layout(self) -> dict[str, Any]:
        """Convert to plotly layout configuration.
        
        Returns
        -------
        dict
            Plotly layout settings
        """
        if self.dark_mode:
            return {
                'template': 'plotly_dark',
                'paper_bgcolor': '#111111',
                'plot_bgcolor': '#111111',
                'font': {
                    'family': self.font_family,
                    'size': self.font_size,
                    'color': 'white'
                }
            }
        else:
            return {
                'template': 'plotly',
                'paper_bgcolor': self.background_color,
                'plot_bgcolor': self.background_color,
                'font': {
                    'family': self.font_family,
                    'size': self.font_size,
                    'color': self.text_color
                }
            }


def create_publication_style() -> PlotStyle:
    """Create styling optimized for publication-quality figures.
    
    Returns
    -------
    PlotStyle
        Publication-optimized styling configuration
    
    Examples
    --------
    >>> style = create_publication_style()
    >>> viz.plot_2d(data=vod_data, style=style)
    """
    return PlotStyle(
        colormap='viridis',
        colorscale='Viridis',
        background_color='white',
        text_color='black',
        font_family='sans-serif',
        font_size=12,
        title_size=16,
        label_size=14,
        edge_linewidth=0.3,
        opacity=0.9,
        dark_mode=False
    )


def create_interactive_style(dark_mode: bool = True) -> PlotStyle:
    """Create styling optimized for interactive exploration.
    
    Parameters
    ----------
    dark_mode : bool, default True
        Use dark theme for better screen viewing
    
    Returns
    -------
    PlotStyle
        Interactive-optimized styling configuration
    
    Examples
    --------
    >>> style = create_interactive_style(dark_mode=True)
    >>> viz.plot_3d(data=vod_data, style=style)
    """
    return PlotStyle(
        colormap='plasma' if dark_mode else 'viridis',
        colorscale='Plasma' if dark_mode else 'Viridis',
        background_color='#111111' if dark_mode else 'white',
        text_color='white' if dark_mode else 'black',
        font_family='Open Sans, sans-serif',
        font_size=11,
        title_size=14,
        label_size=12,
        edge_linewidth=0.5,
        opacity=0.85,
        marker_size=6,
        wireframe_opacity=0.15,
        dark_mode=dark_mode
    )
