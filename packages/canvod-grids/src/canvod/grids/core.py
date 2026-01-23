"""Hemisphere grid data structures and factory functions.

Provides various hemispherical grid types for GNSS signal observation analysis.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np


@dataclass
class GridCell:
    """Represents a single cell in a hemisphere grid.
    
    Parameters
    ----------
    phi : float
        Azimuth angle (radians, 0 to 2π)
    theta : float
        Elevation angle (radians, 0 to π/2 for hemisphere)
    phi_lims : tuple[float, float]
        Azimuth angle limits (min, max)
    theta_lims : tuple[float, float]
        Elevation angle limits (min, max)
    htm_vertices : np.ndarray or None
        3D Cartesian vertices for HTM/triangular cells (Nx3 array)
    """
    
    phi: float
    theta: float
    phi_lims: tuple[float, float]
    theta_lims: tuple[float, float]
    htm_vertices: np.ndarray | None = None


class HemiGrid:
    """Hemisphere grid with multiple cell types.
    
    Provides uniform interface for different grid types used in
    GNSS signal analysis and VOD calculations.
    
    Parameters
    ----------
    cells : list[GridCell]
        List of grid cells
    grid_type : str
        Type of grid ('equal_area', 'HTM', 'geodesic', 'healpix', 'fibonacci')
    
    Attributes
    ----------
    ncells : int
        Number of cells in grid
    cells : list[GridCell]
        Grid cells
    grid_type : str
        Grid type identifier
    
    Examples
    --------
    >>> grid = create_hemigrid('equal_area', angular_resolution=10.0)
    >>> print(f"Grid has {grid.ncells} cells")
    >>> for cell in grid.cells[:5]:
    ...     print(f"Cell at phi={cell.phi:.2f}, theta={cell.theta:.2f}")
    """
    
    def __init__(self, cells: list[GridCell], grid_type: str):
        """Initialize hemisphere grid.
        
        Parameters
        ----------
        cells : list[GridCell]
            Grid cells
        grid_type : str
            Grid type identifier
        """
        self.cells = cells
        self.grid_type = grid_type
    
    @property
    def ncells(self) -> int:
        """Number of cells in grid."""
        return len(self.cells)
    
    def __repr__(self) -> str:
        return f"HemiGrid(type={self.grid_type}, ncells={self.ncells})"


def create_hemigrid(
    grid_type: Literal['equal_area', 'rectangular', 'HTM', 'geodesic', 'healpix', 'fibonacci'],
    angular_resolution: float = 10.0,
    **kwargs,
) -> HemiGrid:
    """Create hemisphere grid of specified type.
    
    Factory function for creating various hemisphere grid types commonly
    used in GNSS analysis.
    
    Parameters
    ----------
    grid_type : str
        Type of grid to create:
        - 'equal_area' or 'rectangular': Regular lat/lon grid
        - 'HTM': Hierarchical Triangular Mesh
        - 'geodesic': Geodesic sphere subdivision
        - 'healpix': HEALPix grid (placeholder)
        - 'fibonacci': Fibonacci sphere (placeholder)
    angular_resolution : float, default 10.0
        Angular resolution in degrees (for equal_area/rectangular)
    **kwargs
        Additional grid-specific parameters
    
    Returns
    -------
    HemiGrid
        Hemisphere grid object
    
    Examples
    --------
    >>> # Equal area grid with 10° resolution
    >>> grid = create_hemigrid('equal_area', angular_resolution=10.0)
    >>> 
    >>> # HTM grid
    >>> grid = create_hemigrid('HTM', subdivision_level=3)
    
    Notes
    -----
    Grid coordinates use standard spherical convention:
    - phi: azimuth angle, 0 to 2π (0 = North, π/2 = East)
    - theta: elevation angle, 0 to π/2 (0 = zenith, π/2 = horizon)
    """
    grid_type_lower = grid_type.lower()
    
    if grid_type_lower in ['equal_area', 'rectangular']:
        return _create_equal_area_grid(angular_resolution)
    elif grid_type_lower == 'htm':
        level = kwargs.get('subdivision_level', 3)
        return _create_htm_grid(level)
    elif grid_type_lower == 'geodesic':
        level = kwargs.get('subdivision_level', 2)
        return _create_geodesic_grid(level)
    elif grid_type_lower == 'healpix':
        raise NotImplementedError("HEALPix grid not yet implemented")
    elif grid_type_lower == 'fibonacci':
        raise NotImplementedError("Fibonacci grid not yet implemented")
    else:
        raise ValueError(f"Unknown grid type: {grid_type}")


def _create_equal_area_grid(angular_resolution: float) -> HemiGrid:
    """Create regular equal-area grid.
    
    Parameters
    ----------
    angular_resolution : float
        Angular resolution in degrees
    
    Returns
    -------
    HemiGrid
        Equal area hemisphere grid
    """
    res_rad = np.radians(angular_resolution)
    
    # Create elevation bands
    n_theta = int(np.ceil((np.pi / 2) / res_rad))
    theta_edges = np.linspace(0, np.pi / 2, n_theta + 1)
    
    cells = []
    
    for i in range(n_theta):
        theta_min = theta_edges[i]
        theta_max = theta_edges[i + 1]
        theta_center = (theta_min + theta_max) / 2
        
        # Calculate azimuth divisions for this elevation band
        # More divisions near horizon (larger theta)
        n_phi = max(4, int(np.ceil(2 * np.pi * np.sin(theta_center) / res_rad)))
        phi_edges = np.linspace(0, 2 * np.pi, n_phi + 1)
        
        for j in range(n_phi):
            phi_min = phi_edges[j]
            phi_max = phi_edges[j + 1]
            phi_center = (phi_min + phi_max) / 2
            
            cell = GridCell(
                phi=phi_center,
                theta=theta_center,
                phi_lims=(phi_min, phi_max),
                theta_lims=(theta_min, theta_max),
                htm_vertices=None
            )
            cells.append(cell)
    
    return HemiGrid(cells=cells, grid_type='equal_area')


def _create_htm_grid(subdivision_level: int) -> HemiGrid:
    """Create Hierarchical Triangular Mesh grid.
    
    Parameters
    ----------
    subdivision_level : int
        Subdivision level (higher = more cells)
    
    Returns
    -------
    HemiGrid
        HTM hemisphere grid
    """
    # Start with octahedron (8 base triangles)
    # Northern hemisphere uses 4 triangles
    
    # Base vertices (unit sphere)
    v_top = np.array([0, 0, 1])
    v_north = np.array([1, 0, 0])
    v_east = np.array([0, 1, 0])
    v_south = np.array([-1, 0, 0])
    v_west = np.array([0, -1, 0])
    
    # 4 base triangles for northern hemisphere
    base_triangles = [
        [v_top, v_north, v_east],
        [v_top, v_east, v_south],
        [v_top, v_south, v_west],
        [v_top, v_west, v_north],
    ]
    
    triangles = base_triangles.copy()
    
    # Subdivide
    for _ in range(subdivision_level):
        new_triangles = []
        for tri in triangles:
            # Get midpoints
            m01 = (tri[0] + tri[1]) / 2
            m01 = m01 / np.linalg.norm(m01)
            m12 = (tri[1] + tri[2]) / 2
            m12 = m12 / np.linalg.norm(m12)
            m20 = (tri[2] + tri[0]) / 2
            m20 = m20 / np.linalg.norm(m20)
            
            # Create 4 sub-triangles
            new_triangles.append([tri[0], m01, m20])
            new_triangles.append([tri[1], m12, m01])
            new_triangles.append([tri[2], m20, m12])
            new_triangles.append([m01, m12, m20])
        
        triangles = new_triangles
    
    # Convert to GridCell objects
    cells = []
    for tri in triangles:
        vertices = np.array(tri)
        
        # Calculate center in spherical coordinates
        center = np.mean(vertices, axis=0)
        center = center / np.linalg.norm(center)
        
        x, y, z = center
        theta = np.arccos(np.clip(z, -1, 1))
        phi = np.arctan2(y, x)
        phi = np.mod(phi, 2 * np.pi)
        
        # Skip if below horizon
        if theta > np.pi / 2:
            continue
        
        # Approximate limits (use triangle bounding box)
        thetas = np.array([np.arccos(np.clip(v[2], -1, 1)) for v in vertices])
        phis = np.array([np.mod(np.arctan2(v[1], v[0]), 2 * np.pi) for v in vertices])
        
        cell = GridCell(
            phi=phi,
            theta=theta,
            phi_lims=(phis.min(), phis.max()),
            theta_lims=(thetas.min(), thetas.max()),
            htm_vertices=vertices
        )
        cells.append(cell)
    
    return HemiGrid(cells=cells, grid_type='HTM')


def _create_geodesic_grid(subdivision_level: int) -> HemiGrid:
    """Create geodesic sphere grid (icosahedron subdivision).
    
    Parameters
    ----------
    subdivision_level : int
        Subdivision level
    
    Returns
    -------
    HemiGrid
        Geodesic hemisphere grid
    """
    # Use HTM as approximation for now
    # True geodesic would start from icosahedron
    return _create_htm_grid(subdivision_level)
