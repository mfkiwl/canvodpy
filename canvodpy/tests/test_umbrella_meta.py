"""Meta tests for canvodpy package."""

def test_package_imports():
    """Test that package can be imported."""
    import canvodpy
    assert canvodpy is not None
    assert canvodpy.__version__ is not None
