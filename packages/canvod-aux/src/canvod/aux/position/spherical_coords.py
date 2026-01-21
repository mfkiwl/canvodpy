"""Spherical coordinate computation for GNSS satellite-receiver geometry.

Computes spherical coordinates (φ, θ, r) in physics convention using
local ENU (East-North-Up) topocentric frame.

Migrated from gnssvodpy.position.spherical_coords
"""

import numpy as np
import pymap3d as pm
import xarray as xr

from canvod.aux.position.position import ECEFPosition


def compute_spherical_coordinates(
    sat_x: np.ndarray,
    sat_y: np.ndarray,
    sat_z: np.ndarray,
    rx_pos: ECEFPosition,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute spherical coordinates (r, theta, phi) in physics convention.

    Uses local ENU (East-North-Up) topocentric frame centered at receiver.

    Physics Convention:
    - theta: Polar angle from +z axis (zenith), [0, π] radians
      * theta = 0 → zenith (straight up)
      * theta = π/2 → horizon
      * theta > π/2 → below horizon (set to NaN)
    - phi: Azimuthal angle from +x (East), [0, 2π) radians, counter-clockwise
      * phi = 0 → East
      * phi = π/2 → North
      * phi = π → West
      * phi = 3π/2 → South
    - r: Radial distance in meters

    Parameters
    ----------
    sat_x : np.ndarray
        Satellite X coordinates in ECEF (meters)
    sat_y : np.ndarray
        Satellite Y coordinates in ECEF (meters)
    sat_z : np.ndarray
        Satellite Z coordinates in ECEF (meters)
    rx_pos : ECEFPosition
        Receiver position in ECEF

    Returns
    -------
    tuple[np.ndarray, np.ndarray, np.ndarray]
        (r, theta, phi) where:
        - r: distances in meters
        - theta: polar angles in radians [0, π]
        - phi: azimuthal angles in radians [0, 2π)

    Notes
    -----
    Satellites below horizon (theta > π/2) are set to NaN.

    Examples
    --------
    >>> from canvod.aux.position import ECEFPosition, compute_spherical_coordinates
    >>> 
    >>> # Receiver position
    >>> rx = ECEFPosition(x=4194304.0, y=176481.0, z=4780013.0)
    >>> 
    >>> # Satellite positions (example)
    >>> sat_x = np.array([16364123.0, 10205789.0])
    >>> sat_y = np.array([12123456.0, -8901234.0])
    >>> sat_z = np.array([18456789.0, 21234567.0])
    >>> 
    >>> r, theta, phi = compute_spherical_coordinates(sat_x, sat_y, sat_z, rx)
    >>> print(f"Distance: {r[0]/1e6:.2f} Mm")
    >>> print(f"Polar angle: {np.degrees(theta[0]):.1f}°")
    >>> print(f"Azimuth: {np.degrees(phi[0]):.1f}°")
    """
    # Receiver ECEF coordinates
    rx_x = rx_pos.x
    rx_y = rx_pos.y
    rx_z = rx_pos.z

    # Convert receiver ECEF to geodetic (lat, lon, alt)
    lat, lon, alt = pm.ecef2geodetic(rx_x, rx_y, rx_z)

    # Convert satellite ECEF to ENU (East-North-Up) relative to receiver
    e, n, u = pm.ecef2enu(sat_x, sat_y, sat_z, lat, lon, alt)

    # Compute radial distance
    r = np.sqrt(e**2 + n**2 + u**2)

    # Compute theta: polar angle from +z (Up) axis
    # Clamp u/r to [-1, 1] to handle numerical errors
    cos_theta = np.clip(u / r, -1.0, 1.0)
    theta = np.arccos(cos_theta)

    # Mask satellites below horizon (u < 0 means below horizon)
    below_horizon = (u < 0)

    # Compute phi: azimuthal angle from +x (East) axis, counter-clockwise
    phi = np.arctan2(n, e)
    phi = np.mod(phi, 2 * np.pi)  # Wrap to [0, 2π)

    # Set below-horizon satellites to NaN
    r = np.where(below_horizon, np.nan, r)
    theta = np.where(below_horizon, np.nan, theta)
    phi = np.where(below_horizon, np.nan, phi)

    return r, theta, phi


def add_spherical_coords_to_dataset(
    ds: xr.Dataset,
    r: np.ndarray,
    theta: np.ndarray,
    phi: np.ndarray,
) -> xr.Dataset:
    """
    Add spherical coordinates to xarray Dataset with proper metadata.

    Parameters
    ----------
    ds : xr.Dataset
        Dataset with 'epoch' and 'sid' dimensions
    r : np.ndarray
        Radial distances in meters
    theta : np.ndarray
        Polar angles in radians [0, π]
    phi : np.ndarray
        Azimuthal angles in radians [0, 2π)

    Returns
    -------
    xr.Dataset
        Dataset with phi, theta, r variables added

    Notes
    -----
    Variables are added with CF-compliant attributes following physics convention.

    Examples
    --------
    >>> # After computing spherical coordinates
    >>> r, theta, phi = compute_spherical_coordinates(sat_x, sat_y, sat_z, rx_pos)
    >>> 
    >>> # Add to RINEX dataset
    >>> augmented_ds = add_spherical_coords_to_dataset(rinex_ds, r, theta, phi)
    >>> print(augmented_ds.phi.attrs['description'])
    """
    ds = ds.assign({
        "phi":
        xr.DataArray(
            phi,
            coords=[ds["epoch"], ds["sid"]],
            dims=["epoch", "sid"],
            attrs={
                "long_name": "Azimuthal angle (physics convention)",
                "short_name": "φ",
                "units": "rad",
                "description":
                "Azimuthal angle from East (+x) in ENU frame, counter-clockwise",
                "valid_range": [0.0, 2 * np.pi],
                "convention":
                "physics (0=East, π/2=North, π=West, 3π/2=South)",
            },
        ),
        "theta":
        xr.DataArray(
            theta,
            coords=[ds["epoch"], ds["sid"]],
            dims=["epoch", "sid"],
            attrs={
                "long_name": "Polar angle (physics convention)",
                "short_name": "θ",
                "units": "rad",
                "description": "Polar angle from zenith (+z/Up)",
                "valid_range": [0.0, np.pi / 2],
                "convention": "physics (0=zenith, π/2=horizon)",
            },
        ),
        "r":
        xr.DataArray(
            r,
            coords=[ds["epoch"], ds["sid"]],
            dims=["epoch", "sid"],
            attrs={
                "long_name": "Distance",
                "short_name": "r",
                "units": "m",
                "description": "Distance between satellite and receiver",
            },
        ),
    })
    return ds
