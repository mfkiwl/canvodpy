"""Tests for canvod-grids package."""

import numpy as np
import pytest


# ============================================================================
# Import Tests
# ============================================================================

def test_imports():
    """Test that all modules can be imported."""
    from canvod.grids import GridCell, HemiGrid, create_hemigrid
    
    assert GridCell is not None
    assert HemiGrid is not None
    assert create_hemigrid is not None


def test_version():
    """Test that package has version."""
    from canvod.grids import __version__
    assert __version__ == "0.1.0"


# ============================================================================
# GridCell Tests
# ============================================================================

class TestGridCell:
    """Tests for GridCell dataclass."""
    
    def test_grid_cell_creation(self):
        """Test creating a grid cell."""
        from canvod.grids import GridCell
        
        cell = GridCell(
            phi=np.pi / 4,
            theta=np.pi / 6,
            phi_lims=(0, np.pi / 2),
            theta_lims=(0, np.pi / 4),
            htm_vertices=None
        )
        
        assert cell.phi == np.pi / 4
        assert cell.theta == np.pi / 6
        assert cell.phi_lims == (0, np.pi / 2)
        assert cell.theta_lims == (0, np.pi / 4)
        assert cell.htm_vertices is None
    
    def test_grid_cell_with_vertices(self):
        """Test grid cell with HTM vertices."""
        from canvod.grids import GridCell
        
        vertices = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])
        
        cell = GridCell(
            phi=np.pi / 4,
            theta=np.pi / 6,
            phi_lims=(0, np.pi / 2),
            theta_lims=(0, np.pi / 4),
            htm_vertices=vertices
        )
        
        assert cell.htm_vertices is not None
        assert cell.htm_vertices.shape == (3, 3)
        np.testing.assert_array_equal(cell.htm_vertices, vertices)


# ============================================================================
# HemiGrid Tests
# ============================================================================

class TestHemiGrid:
    """Tests for HemiGrid class."""
    
    def test_hemi_grid_creation(self):
        """Test creating a hemisphere grid."""
        from canvod.grids import GridCell, HemiGrid
        
        cells = [
            GridCell(0, 0, (0, 1), (0, 1), None),
            GridCell(1, 1, (1, 2), (1, 2), None),
        ]
        
        grid = HemiGrid(cells=cells, grid_type='test')
        
        assert grid.ncells == 2
        assert grid.grid_type == 'test'
        assert len(grid.cells) == 2
    
    def test_hemi_grid_repr(self):
        """Test grid representation."""
        from canvod.grids import GridCell, HemiGrid
        
        cells = [GridCell(0, 0, (0, 1), (0, 1), None)]
        grid = HemiGrid(cells=cells, grid_type='equal_area')
        
        repr_str = repr(grid)
        assert 'HemiGrid' in repr_str
        assert 'equal_area' in repr_str
        assert 'ncells=1' in repr_str


# ============================================================================
# Factory Function Tests
# ============================================================================

class TestCreateHemigrid:
    """Tests for create_hemigrid factory function."""
    
    def test_equal_area_grid(self):
        """Test creating equal area grid."""
        from canvod.grids import create_hemigrid
        
        grid = create_hemigrid('equal_area', angular_resolution=10.0)
        
        assert grid.grid_type == 'equal_area'
        assert grid.ncells > 0
        assert len(grid.cells) == grid.ncells
    
    def test_rectangular_grid(self):
        """Test creating rectangular grid (alias for equal_area)."""
        from canvod.grids import create_hemigrid
        
        grid = create_hemigrid('rectangular', angular_resolution=15.0)
        
        assert grid.grid_type == 'equal_area'
        assert grid.ncells > 0
    
    def test_htm_grid(self):
        """Test creating HTM grid."""
        from canvod.grids import create_hemigrid
        
        grid = create_hemigrid('HTM', subdivision_level=2)
        
        assert grid.grid_type == 'HTM'
        assert grid.ncells > 0
        
        # Check that cells have vertices
        assert all(cell.htm_vertices is not None for cell in grid.cells)
        assert all(cell.htm_vertices.shape == (3, 3) for cell in grid.cells)
    
    def test_geodesic_grid(self):
        """Test creating geodesic grid."""
        from canvod.grids import create_hemigrid
        
        grid = create_hemigrid('geodesic', subdivision_level=2)
        
        assert grid.grid_type == 'HTM'  # Currently uses HTM approximation
        assert grid.ncells > 0
    
    def test_healpix_not_implemented(self):
        """Test that HEALPix raises NotImplementedError."""
        from canvod.grids import create_hemigrid
        
        with pytest.raises(NotImplementedError, match="HEALPix"):
            create_hemigrid('healpix')
    
    def test_fibonacci_not_implemented(self):
        """Test that Fibonacci raises NotImplementedError."""
        from canvod.grids import create_hemigrid
        
        with pytest.raises(NotImplementedError, match="Fibonacci"):
            create_hemigrid('fibonacci')
    
    def test_unknown_grid_type(self):
        """Test that unknown grid type raises ValueError."""
        from canvod.grids import create_hemigrid
        
        with pytest.raises(ValueError, match="Unknown grid type"):
            create_hemigrid('invalid_type')
    
    def test_case_insensitive_grid_type(self):
        """Test that grid type is case insensitive."""
        from canvod.grids import create_hemigrid
        
        grid1 = create_hemigrid('equal_area', angular_resolution=10.0)
        grid2 = create_hemigrid('EQUAL_AREA', angular_resolution=10.0)
        grid3 = create_hemigrid('Equal_Area', angular_resolution=10.0)
        
        assert grid1.grid_type == grid2.grid_type == grid3.grid_type


# ============================================================================
# Equal Area Grid Tests
# ============================================================================

class TestEqualAreaGrid:
    """Tests for equal area grid generation."""
    
    def test_resolution_affects_cell_count(self):
        """Test that resolution affects number of cells."""
        from canvod.grids import create_hemigrid
        
        grid_coarse = create_hemigrid('equal_area', angular_resolution=20.0)
        grid_fine = create_hemigrid('equal_area', angular_resolution=10.0)
        
        # Finer resolution should have more cells
        assert grid_fine.ncells > grid_coarse.ncells
    
    def test_cells_within_hemisphere(self):
        """Test that all cells are within hemisphere bounds."""
        from canvod.grids import create_hemigrid
        
        grid = create_hemigrid('equal_area', angular_resolution=10.0)
        
        for cell in grid.cells:
            # Check phi in [0, 2π]
            assert 0 <= cell.phi <= 2 * np.pi
            # Check theta in [0, π/2]
            assert 0 <= cell.theta <= np.pi / 2
    
    def test_cell_limits_consistent(self):
        """Test that cell centers are within limits."""
        from canvod.grids import create_hemigrid
        
        grid = create_hemigrid('equal_area', angular_resolution=15.0)
        
        for cell in grid.cells:
            phi_min, phi_max = cell.phi_lims
            theta_min, theta_max = cell.theta_lims
            
            # Center should be within limits
            assert phi_min <= cell.phi <= phi_max
            assert theta_min <= cell.theta <= theta_max


# ============================================================================
# HTM Grid Tests
# ============================================================================

class TestHTMGrid:
    """Tests for HTM grid generation."""
    
    def test_subdivision_affects_cell_count(self):
        """Test that subdivision level affects cell count."""
        from canvod.grids import create_hemigrid
        
        grid_l1 = create_hemigrid('HTM', subdivision_level=1)
        grid_l2 = create_hemigrid('HTM', subdivision_level=2)
        grid_l3 = create_hemigrid('HTM', subdivision_level=3)
        
        # Higher subdivision = more cells (4x per level)
        assert grid_l2.ncells > grid_l1.ncells
        assert grid_l3.ncells > grid_l2.ncells
    
    def test_htm_cells_have_vertices(self):
        """Test that HTM cells have valid vertices."""
        from canvod.grids import create_hemigrid
        
        grid = create_hemigrid('HTM', subdivision_level=2)
        
        for cell in grid.cells:
            assert cell.htm_vertices is not None
            assert cell.htm_vertices.shape == (3, 3)  # 3 vertices, 3D coords
            
            # Vertices should be on unit sphere (approximately)
            for vertex in cell.htm_vertices:
                radius = np.linalg.norm(vertex)
                np.testing.assert_almost_equal(radius, 1.0, decimal=5)
    
    def test_htm_cells_in_hemisphere(self):
        """Test that HTM cells are in northern hemisphere."""
        from canvod.grids import create_hemigrid
        
        grid = create_hemigrid('HTM', subdivision_level=2)
        
        for cell in grid.cells:
            # All vertices should have z >= 0 (northern hemisphere)
            # Actually some might be slightly below due to subdivision
            # But center should definitely be above
            assert cell.theta <= np.pi / 2


# ============================================================================
# Integration Tests
# ============================================================================

class TestGridIntegration:
    """Integration tests with multiple grid types."""
    
    def test_grid_types_have_consistent_interface(self):
        """Test that all grid types have consistent interface."""
        from canvod.grids import create_hemigrid
        
        grid_types = ['equal_area', 'rectangular', 'HTM', 'geodesic']
        
        for grid_type in grid_types:
            if grid_type in ['HTM', 'geodesic']:
                grid = create_hemigrid(grid_type, subdivision_level=1)
            else:
                grid = create_hemigrid(grid_type, angular_resolution=20.0)
            
            # All should have these attributes
            assert hasattr(grid, 'ncells')
            assert hasattr(grid, 'cells')
            assert hasattr(grid, 'grid_type')
            assert grid.ncells > 0
            assert len(grid.cells) == grid.ncells
            
            # All cells should have required attributes
            for cell in grid.cells:
                assert hasattr(cell, 'phi')
                assert hasattr(cell, 'theta')
                assert hasattr(cell, 'phi_lims')
                assert hasattr(cell, 'theta_lims')
                assert hasattr(cell, 'htm_vertices')
    
    def test_grids_compatible_with_viz(self):
        """Test that grids work with viz package expectations."""
        from canvod.grids import create_hemigrid
        
        grid = create_hemigrid('equal_area', angular_resolution=15.0)
        
        # Viz expects these to work
        assert grid.ncells == len(grid.cells)
        assert isinstance(grid.grid_type, str)
        
        # Viz iterates over cells
        for cell in grid.cells:
            # These must exist for viz
            assert isinstance(cell.phi, (int, float, np.number))
            assert isinstance(cell.theta, (int, float, np.number))
            assert isinstance(cell.phi_lims, tuple)
            assert isinstance(cell.theta_lims, tuple)
            assert len(cell.phi_lims) == 2
            assert len(cell.theta_lims) == 2


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Basic performance tests."""
    
    @pytest.mark.slow
    def test_large_equal_area_grid(self):
        """Test creating large equal area grid."""
        from canvod.grids import create_hemigrid
        
        grid = create_hemigrid('equal_area', angular_resolution=5.0)
        
        # Should have many cells with 5° resolution
        assert grid.ncells > 100
        assert all(hasattr(cell, 'phi') for cell in grid.cells)
    
    @pytest.mark.slow
    def test_deep_htm_subdivision(self):
        """Test deep HTM subdivision."""
        from canvod.grids import create_hemigrid
        
        grid = create_hemigrid('HTM', subdivision_level=4)
        
        # Level 4 should have many cells
        assert grid.ncells > 100
        assert all(cell.htm_vertices is not None for cell in grid.cells)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
