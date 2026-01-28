"""Basic tests for canvod-vod package."""



def test_import():
    """Test that package can be imported."""
    import canvod.vod

    assert hasattr(canvod.vod, "VODCalculator")
    assert hasattr(canvod.vod, "TauOmegaZerothOrder")


def test_version():
    """Test that version is defined."""
    import canvod.vod

    assert hasattr(canvod.vod, "__version__")
    assert isinstance(canvod.vod.__version__, str)
