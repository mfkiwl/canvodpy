"""
Tests for internal unit utilities.

Tests the UREG unit registry and custom unit definitions.
"""
import pytest
from canvod.aux._internal import UREG, SPEEDOFLIGHT


def test_ureg_import():
    """Test that UREG can be imported and is a UnitRegistry."""
    import pint
    assert isinstance(UREG, pint.UnitRegistry)


def test_custom_db_unit():
    """Test that custom dB unit is defined."""
    # Create a quantity with dB units
    db_value = 10 * UREG.dB
    assert db_value.units == UREG.dB


def test_custom_dbhz_unit():
    """Test that custom dBHz unit is defined."""
    # Create a quantity with dBHz units
    dbhz_value = 40 * UREG.dBHz
    assert dbhz_value.units == UREG.dBHz


def test_speedoflight_constant():
    """Test that SPEEDOFLIGHT constant is defined correctly."""
    # Speed of light should be approximately 299792458 m/s
    assert SPEEDOFLIGHT.magnitude == pytest.approx(299792458, rel=1e-6)
    
    # Check units are meter/second
    expected_units = UREG.meter / UREG.second
    assert SPEEDOFLIGHT.units == expected_units


def test_kilometer_to_meter_conversion():
    """Test basic unit conversion using UREG."""
    distance_km = 1 * UREG.kilometer
    distance_m = distance_km.to(UREG.meter)
    assert distance_m.magnitude == 1000


def test_microsecond_to_second_conversion():
    """Test time unit conversion using UREG."""
    time_us = 1000 * UREG.microsecond
    time_s = time_us.to(UREG.second)
    assert time_s.magnitude == pytest.approx(0.001)


def test_ureg_dimensionless_operations():
    """Test that dimensionless operations work correctly."""
    value = 100 * UREG.meter
    dimensionless = value.magnitude
    assert dimensionless == 100
    assert isinstance(dimensionless, (int, float))
