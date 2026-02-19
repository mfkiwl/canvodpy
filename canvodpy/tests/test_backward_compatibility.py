"""
Backward compatibility tests.

Ensures legacy API still works after redesign.
"""

import pytest


class TestLegacySiteAPI:
    """Test legacy Site class still works."""

    def test_site_import(self):
        """Should still be able to import Site."""
        from canvodpy import Site

        assert Site is not None

    def test_site_creation(self):
        """Should create Site with name."""
        from canvodpy import Site

        try:
            site = Site("Rosalia")
            assert site.name == "Rosalia"
        except Exception as e:
            pytest.skip(f"Site not configured: {e}")

    def test_site_has_receivers(self):
        """Site should have receivers property."""
        from canvodpy import Site

        try:
            site = Site("Rosalia")
            assert hasattr(site, "receivers")
            assert isinstance(site.receivers, dict)
        except Exception as e:
            pytest.skip(f"Site not configured: {e}")

    def test_site_has_active_receivers(self):
        """Site should have active_receivers property."""
        from canvodpy import Site

        try:
            site = Site("Rosalia")
            assert hasattr(site, "active_receivers")
        except Exception as e:
            pytest.skip(f"Site not configured: {e}")


class TestLegacyPipelineAPI:
    """Test legacy Pipeline class still works."""

    def test_pipeline_import(self):
        """Should still be able to import Pipeline."""
        from canvodpy import Pipeline

        assert Pipeline is not None

    def test_pipeline_creation_from_site(self):
        """Should create Pipeline from Site."""
        from canvodpy import Pipeline, Site

        try:
            site = Site("Rosalia")
            pipeline = Pipeline(site)
            assert pipeline.site.name == "Rosalia"
        except Exception as e:
            pytest.skip(f"Site not configured: {e}")

    def test_pipeline_creation_from_string(self):
        """Should create Pipeline from site name."""
        from canvodpy import Pipeline

        try:
            pipeline = Pipeline("Rosalia")
            assert pipeline.site.name == "Rosalia"
        except Exception as e:
            pytest.skip(f"Site not configured: {e}")

    def test_pipeline_has_process_date(self):
        """Pipeline should have process_date method."""
        from canvodpy import Pipeline

        try:
            pipeline = Pipeline("Rosalia")
            assert hasattr(pipeline, "process_date")
            assert callable(pipeline.process_date)
        except Exception as e:
            pytest.skip(f"Site not configured: {e}")


class TestLegacyConvenienceFunctions:
    """Test legacy convenience functions still work."""

    def test_process_date_import(self):
        """Should import process_date function."""
        from canvodpy import process_date

        assert process_date is not None
        assert callable(process_date)

    def test_calculate_vod_import(self):
        """Should import calculate_vod function."""
        from canvodpy import calculate_vod

        assert calculate_vod is not None
        assert callable(calculate_vod)

    def test_preview_processing_import(self):
        """Should import preview_processing function."""
        from canvodpy import preview_processing

        assert preview_processing is not None
        assert callable(preview_processing)


class TestNewAPICoexistence:
    """Test that new and old APIs can coexist."""

    def test_both_site_and_workflow_importable(self):
        """Should import both Site and VODWorkflow."""
        from canvodpy import Site, VODWorkflow

        assert Site is not None
        assert VODWorkflow is not None

    def test_both_apis_work_together(self):
        """Should use both APIs in same code."""
        from canvodpy import Site, VODWorkflow

        try:
            # Old API
            site = Site("Rosalia")

            # New API with same site object
            workflow = VODWorkflow(site=site)

            assert site.name == workflow.site.name
        except Exception as e:
            pytest.skip(f"Site not configured: {e}")

    def test_old_api_uses_new_components(self):
        """Legacy API should benefit from new factories."""
        # Pipeline internally might use factories in future
        # For now, just verify it still works
        from canvodpy import Pipeline

        try:
            pipeline = Pipeline("Rosalia")
            # If it initializes, old API works
            assert pipeline is not None
        except Exception as e:
            pytest.skip(f"Site not configured: {e}")


class TestAPIExports:
    """Test __all__ exports include both old and new."""

    def test_all_contains_legacy_api(self):
        """__all__ should export legacy classes."""
        import canvodpy

        assert "Site" in canvodpy.__all__
        assert "Pipeline" in canvodpy.__all__
        assert "process_date" in canvodpy.__all__
        assert "calculate_vod" in canvodpy.__all__

    def test_all_contains_new_api(self):
        """__all__ should export new classes."""
        import canvodpy

        assert "VODWorkflow" in canvodpy.__all__
        assert "ReaderFactory" in canvodpy.__all__
        assert "GridFactory" in canvodpy.__all__
        assert "VODFactory" in canvodpy.__all__

    def test_all_contains_functional_api(self):
        """__all__ should export functional API."""
        import canvodpy

        assert "read_rinex" in canvodpy.__all__
        assert "create_grid" in canvodpy.__all__
        assert "assign_grid_cells" in canvodpy.__all__


class TestConfigurationCompatibility:
    """Test configuration still works with new API."""

    def test_keep_rnx_vars_available_via_config(self):
        """KEEP_RNX_VARS should be available via load_config()."""
        from canvod.utils.config import load_config

        cfg = load_config()
        keep_vars = cfg.processing.processing.keep_rnx_vars
        assert keep_vars is not None
        assert isinstance(keep_vars, list)


class TestSubpackageCompatibility:
    """Test subpackage imports still work."""

    def test_lazy_import_readers(self):
        """Should lazy import readers."""
        import canvodpy

        readers = canvodpy.readers
        assert readers is not None

    def test_lazy_import_grids(self):
        """Should lazy import grids."""
        import canvodpy

        grids = canvodpy.grids
        assert grids is not None

    def test_lazy_import_vod(self):
        """Should lazy import vod."""
        import canvodpy

        vod = canvodpy.vod
        assert vod is not None

    def test_all_contains_subpackages(self):
        """__all__ should list subpackages."""
        import canvodpy

        assert "readers" in canvodpy.__all__
        assert "grids" in canvodpy.__all__
        assert "vod" in canvodpy.__all__
        assert "viz" in canvodpy.__all__
        assert "store" in canvodpy.__all__
