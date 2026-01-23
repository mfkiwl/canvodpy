from math import e
from typing import Any

import numpy as np
import pint
from pydantic import ConfigDict, Field, field_validator
from pydantic.dataclasses import dataclass
import pymap3d as pm
import xarray as xr

from canvodpy.globals import UREG

ureg = UREG


@dataclass(frozen=True,
           kw_only=True,
           config=ConfigDict(arbitrary_types_allowed=True))
class ECEFPosition:
    """
    Class to store position in ECEF coordinates.
    Converts input to meters (SI unit).
    """
    x: pint.Quantity  # X coordinate (will be checked and converted)
    y: pint.Quantity  # Y coordinate (will be checked and converted)
    z: pint.Quantity  # Z coordinate (will be checked and converted)

    @field_validator('x', 'y', 'z', mode='before')
    def convert_to_si(cls, value: Any) -> pint.Quantity:
        """Ensure that the coordinate is converted to SI units (meters for length)."""
        if isinstance(value, ureg.Quantity) and value.units != ureg.meter:
            return value.to(ureg.meter)
        return value

    def to_geodetic(self) -> 'GeodeticPosition':
        """
        Convert ECEF to Geodetic coordinates.
        """
        lat, lon, alt = pm.ecef2geodetic(self.x.magnitude, self.y.magnitude,
                                         self.z.magnitude)
        return GeodeticPosition(lat=(lat * ureg.degrees).to(ureg.radian),
                                lon=(lon * ureg.degrees).to(ureg.radian),
                                alt=alt * ureg.meter)

    def to_aer(self, lat: pint.Quantity, lon: pint.Quantity,
               alt: pint.Quantity) -> 'AERPosition':
        """
        Convert ECEF to AER coordinates.
        """
        azimuth, elevation, range_ = pm.ecef2aer(self.x.magnitude,
                                                 self.y.magnitude,
                                                 self.z.magnitude,
                                                 lat.magnitude, lon.magnitude,
                                                 alt.magnitude)
        return AERPosition(azimuth=(azimuth * ureg.degree).to(ureg.radian),
                           elevation=(elevation * ureg.degree).to(ureg.radian),
                           range=range_ * ureg.meter)

    def to_scs(self) -> 'SCSPosition':
        """
        Convert ECEF to Spherical Coordinate System (SCS).
        """
        geodetic_pos = self.to_geodetic()

        aer_pos = ecef_pos.to_aer(lat=geodetic_pos.lat,
                                  lon=geodetic_pos.lon,
                                  alt=geodetic_pos.alt)
        r = aer_pos.range.to(ureg.meter)
        theta = (np.pi / 2 - aer_pos.elevation).to(ureg.radian)
        phi = aer_pos.azimuth.to(ureg.radian)

        return SCSPosition(r=r, theta=theta, phi=phi)

    @classmethod
    def from_ds_metadata(cls, ds: xr.Dataset) -> 'ECEFPosition':
        """
        Create an ECEFPosition object from the metadata of an xarray Dataset.
        """
        pos = ds.attrs.get('Approximate Position')
        pos_parts = pos.split(',')

        def sanitize(s: str) -> float:
            return float(s.split('=')[1].strip().split()[0])

        x = sanitize(pos_parts[0]) * ureg.meter
        y = sanitize(pos_parts[1]) * ureg.meter
        z = sanitize(pos_parts[2]) * ureg.meter

        return cls(x=x, y=y, z=z)


@dataclass(frozen=True,
           kw_only=True,
           config=ConfigDict(arbitrary_types_allowed=True))
class GeodeticPosition:
    """
    Class to store position in Geodetic coordinates (lat, lon, alt).
    Converts input to SI units where necessary.
    """
    lat: pint.Quantity  # Latitude in radians (converted from degrees if needed)
    lon: pint.Quantity  # Longitude in radians (converted from degrees if needed)
    alt: pint.Quantity  # Altitude in meters (if not already in meters)

    @field_validator('lat', 'lon', mode='before')
    def convert_to_si(cls, value: Any) -> pint.Quantity:
        """Ensure that latitude, longitude are in radians, and altitude is in meters."""
        if isinstance(value, ureg.Quantity):
            if value.units == ureg.degrees:  # Convert from degrees to radians
                return value.to(ureg.radian)
        return value

    @field_validator('alt', mode='before')
    def convert_to_si(cls, value: Any) -> pint.Quantity:
        """Ensure that latitude, longitude are in radians, and altitude is in meters."""
        if isinstance(value, ureg.Quantity):
            if value.units != ureg.meter:  # Convert altitude to meters
                return value.to(ureg.meter)
        return value


@dataclass(frozen=True,
           kw_only=True,
           config=ConfigDict(arbitrary_types_allowed=True))
class AERPosition:
    """
    Class to store position in Azimuth-Elevation-Range (AER) coordinates.
    Converts input to SI units where necessary.
    """
    azimuth: pint.Quantity  # Azimuth in radians
    elevation: pint.Quantity  # Elevation in radians
    range: pint.Quantity  # Range in meters

    @field_validator('azimuth', 'elevation', mode='before')
    def convert_to_si(cls, value: Any) -> pint.Quantity:
        """Ensure that azimuth, elevation are in radians, and range in meters."""
        if isinstance(value, ureg.Quantity):
            # Convert angles to radians if not already in radians
            if value.units != ureg.radian:
                return value.to(ureg.radian)
        return value

    @field_validator('range', mode='before')
    def convert_to_si(cls, value: Any) -> pint.Quantity:
        """Ensure that azimuth, elevation are in radians, and range in meters."""
        if isinstance(value, ureg.Quantity):
            # Convert range to meters if not already in meters
            if value.units != ureg.meter:
                return value.to(ureg.meter)
        return value


@dataclass(frozen=True,
           kw_only=True,
           config=ConfigDict(arbitrary_types_allowed=True))
class SCSPosition:
    """
    Class to store position in Spherical Coordinate System (SCS).
    Converts input to SI units where necessary.
    """
    r: pint.Quantity  # Radial distance in meters
    theta: pint.Quantity  # Polar angle in radians
    phi: pint.Quantity  # Azimuthal angle in radians

    @field_validator('r', mode='before')
    def convert_to_si(cls, value: Any) -> pint.Quantity:
        """Ensure radial distance in meters and angles in radians."""
        if isinstance(value, ureg.Quantity):
            # Convert radial distance to meters if not in meters
            if value.units != ureg.meter:
                return value.to(ureg.meter)
        return value

    @field_validator('theta', 'phi', mode='before')
    def convert_to_si(cls, value: Any) -> pint.Quantity:
        """Ensure radial distance in meters and angles in radians."""
        if isinstance(value, ureg.Quantity):
            # Convert angles to radians if not in radians
            if value.units != ureg.radian:
                return value.to(ureg.radian)
        return value

    def to_ecef(self) -> 'ECEFPosition':
        """
        Convert from SCS to ECEF.
        """
        # Convert spherical coordinates to ECEF coordinates
        x = self.r.magnitude * pm.sind(self.theta.magnitude) * pm.cosd(
            self.phi.magnitude)
        y = self.r.magnitude * pm.sind(self.theta.magnitude) * pm.sind(
            self.phi.magnitude)
        z = self.r.magnitude * pm.cosd(self.theta.magnitude)
        return ECEFPosition(x=x * ureg.meter,
                            y=y * ureg.meter,
                            z=z * ureg.meter)


# Example usage:
if __name__ == '__main__':
    # Create an ECEF position with Pint units
    ecef_pos = ECEFPosition(x=1 * UREG.kilometer,
                            y=2 * UREG.nanometer,
                            z=3 * UREG.lightyear)

    print(f"ECEF Position: x={ecef_pos.x}, y={ecef_pos.y}, z={ecef_pos.z}")

    # Convert to Geodetic
    geodetic_pos = ecef_pos.to_geodetic()

    print(
        f"Geodetic Position: lat={geodetic_pos.lat}, lon={geodetic_pos.lon}, alt={geodetic_pos.alt}"
    )

    aer_pos = ecef_pos.to_aer(lat=geodetic_pos.lat,
                              lon=geodetic_pos.lon,
                              alt=geodetic_pos.alt)

    print(
        f"AER Position: azimuth={aer_pos.azimuth}, elevation={aer_pos.elevation}, range={aer_pos.range}"
    )

    scs_pos = ecef_pos.to_scs()
    print(
        f"SCS Position: r={scs_pos.r}, theta={scs_pos.theta}, phi={scs_pos.phi}"
    )

    ds = xr.open_dataset(
        '/home/nbader/Music/GNSS_Test/Heuberg/testdata/processed/NB_results_approxpos.nc'
    )
    ecef_pos = ECEFPosition.from_ds_metadata(ds)
    print(ecef_pos)
