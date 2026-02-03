"""Grid type definitions for hemisphere tessellation."""

from enum import Enum


class GridType(Enum):
    """Available grid projection types for hemispherical tessellation."""

    EQUAL_AREA = "equal_area"  # Equal solid angle (ring-based)
    EQUAL_ANGLE = "equal_angle"  # Equal angular spacing
    EQUIRECTANGULAR = "equirectangular"  # Simple rectangular
    HEALPIX = "healpix"  # Hierarchical equal area
    GEODESIC = "geodesic"  # Icosahedral triangular
    FIBONACCI = "fibonacci"  # Golden spiral + Voronoi
    HTM = "htm"  # Hierarchical Triangular Mesh
