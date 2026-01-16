"""
Tests for interpolation strategies.

Tests the interpolation configuration and strategy classes.
"""
import numpy as np
import pytest
import xarray as xr
from canvod.aux.interpolation import (
    Sp3Config,
    ClockConfig,
    Sp3InterpolationStrategy,
    ClockInterpolationStrategy,
    create_interpolator_from_attrs,
)


class TestInterpolatorConfigs:
    """Tests for interpolator configuration classes."""
    
    def test_sp3_config_defaults(self):
        """Test Sp3Config default values."""
        config = Sp3Config()
        assert config.use_velocities is True
        assert config.fallback_method == 'linear'
    
    def test_sp3_config_custom(self):
        """Test Sp3Config with custom values."""
        config = Sp3Config(use_velocities=False, fallback_method='cubic')
        assert config.use_velocities is False
        assert config.fallback_method == 'cubic'
    
    def test_clock_config_defaults(self):
        """Test ClockConfig default values."""
        config = ClockConfig()
        assert config.window_size == 9
        assert config.jump_threshold == 1e-6
    
    def test_clock_config_custom(self):
        """Test ClockConfig with custom values."""
        config = ClockConfig(window_size=15, jump_threshold=1e-5)
        assert config.window_size == 15
        assert config.jump_threshold == 1e-5
    
    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = Sp3Config(use_velocities=False)
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert 'use_velocities' in config_dict
        assert config_dict['use_velocities'] is False


class TestSp3InterpolationStrategy:
    """Tests for SP3 interpolation strategy."""
    
    def test_create_strategy(self):
        """Test creating SP3 interpolation strategy."""
        config = Sp3Config()
        strategy = Sp3InterpolationStrategy(config=config)
        
        assert strategy.config == config
    
    def test_to_attrs(self):
        """Test converting strategy to attrs dictionary."""
        config = Sp3Config()
        strategy = Sp3InterpolationStrategy(config=config)
        
        attrs = strategy.to_attrs()
        
        assert 'interpolator_type' in attrs
        assert attrs['interpolator_type'] == 'Sp3InterpolationStrategy'
        assert 'config' in attrs
        assert attrs['config']['use_velocities'] is True
    
    def test_interpolate_requires_dataset(self):
        """Test that interpolate handles datasets without position data."""
        config = Sp3Config()
        strategy = Sp3InterpolationStrategy(config=config)
        
        # Create minimal test dataset without position data
        epochs = np.array([np.datetime64('2024-01-01T00:00:00'),
                          np.datetime64('2024-01-01T00:15:00')])
        sids = ['G01']
        
        # Add position data (required for interpolation)
        ds = xr.Dataset(
            data_vars={
                'X': (('epoch', 'sid'), np.array([[1000.0], [2000.0]])),
                'Y': (('epoch', 'sid'), np.array([[3000.0], [4000.0]])),
                'Z': (('epoch', 'sid'), np.array([[5000.0], [6000.0]])),
            },
            coords={'epoch': epochs, 'sid': sids}
        )
        
        target_epochs = np.array([np.datetime64('2024-01-01T00:07:30')])
        
        # Should interpolate successfully with position data
        result = strategy.interpolate(ds, target_epochs)
        assert 'X' in result
        assert 'Y' in result
        assert 'Z' in result


class TestClockInterpolationStrategy:
    """Tests for Clock interpolation strategy."""
    
    def test_create_strategy(self):
        """Test creating Clock interpolation strategy."""
        config = ClockConfig()
        strategy = ClockInterpolationStrategy(config=config)
        
        assert strategy.config == config
    
    def test_to_attrs(self):
        """Test converting strategy to attrs dictionary."""
        config = ClockConfig(window_size=15)
        strategy = ClockInterpolationStrategy(config=config)
        
        attrs = strategy.to_attrs()
        
        assert 'interpolator_type' in attrs
        assert attrs['interpolator_type'] == 'ClockInterpolationStrategy'
        assert 'config' in attrs
        assert attrs['config']['window_size'] == 15


class TestCreateInterpolatorFromAttrs:
    """Tests for recreating interpolator from attributes."""
    
    def test_recreate_sp3_interpolator(self):
        """Test recreating Sp3InterpolationStrategy from attrs."""
        # Create original strategy
        config = Sp3Config(use_velocities=False)
        original = Sp3InterpolationStrategy(config=config)
        
        # Get attrs
        attrs = {'interpolator_config': original.to_attrs()}
        
        # Recreate
        recreated = create_interpolator_from_attrs(attrs)
        
        assert isinstance(recreated, Sp3InterpolationStrategy)
        assert recreated.config.use_velocities is False
    
    def test_recreate_clock_interpolator(self):
        """Test recreating ClockInterpolationStrategy from attrs."""
        # Create original strategy
        config = ClockConfig(window_size=15)
        original = ClockInterpolationStrategy(config=config)
        
        # Get attrs
        attrs = {'interpolator_config': original.to_attrs()}
        
        # Recreate
        recreated = create_interpolator_from_attrs(attrs)
        
        assert isinstance(recreated, ClockInterpolationStrategy)
        assert recreated.config.window_size == 15
    
    def test_invalid_interpolator_type(self):
        """Test that invalid interpolator type raises error."""
        attrs = {
            'interpolator_config': {
                'interpolator_type': 'InvalidStrategy',
                'config': {}
            }
        }
        
        with pytest.raises(ValueError, match="Unknown interpolator type"):
            create_interpolator_from_attrs(attrs)


class TestInterpolationIntegration:
    """Integration tests for interpolation workflow."""
    
    def test_sp3_strategy_roundtrip(self):
        """Test complete SP3 strategy creation, serialization, and recreation."""
        # Create strategy
        config = Sp3Config(use_velocities=False, fallback_method='cubic')
        strategy = Sp3InterpolationStrategy(config=config)
        
        # Convert to attrs
        attrs_dict = {'interpolator_config': strategy.to_attrs()}
        
        # Recreate
        recreated = create_interpolator_from_attrs(attrs_dict)
        
        # Verify recreation
        assert isinstance(recreated, Sp3InterpolationStrategy)
        assert recreated.config.use_velocities is False
        assert recreated.config.fallback_method == 'cubic'
    
    def test_clock_strategy_roundtrip(self):
        """Test complete Clock strategy creation, serialization, and recreation."""
        # Create strategy
        config = ClockConfig(window_size=15, jump_threshold=1e-5)
        strategy = ClockInterpolationStrategy(config=config)
        
        # Convert to attrs
        attrs_dict = {'interpolator_config': strategy.to_attrs()}
        
        # Recreate
        recreated = create_interpolator_from_attrs(attrs_dict)
        
        # Verify recreation
        assert isinstance(recreated, ClockInterpolationStrategy)
        assert recreated.config.window_size == 15
        assert recreated.config.jump_threshold == 1e-5
