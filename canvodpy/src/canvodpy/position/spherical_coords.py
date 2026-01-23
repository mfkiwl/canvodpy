"""
Shared coordinate computation utilities.

This module provides a single source of truth for computing spherical
coordinates in physics convention, used by both the augmentation framework
and the optimized parallel processor.
"""

import numpy as np
import pymap3d as pm
import xarray as xr

from canvodpy.position.position import ECEFPosition


def compute_spherical_coordinates(
    sat_x: np.ndarray,
    sat_y: np.ndarray,
    sat_z: np.ndarray,
    rx_pos: ECEFPosition,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute spherical coordinates (r, theta, phi) in physics convention.

    Physics Convention (ENU frame):
    - theta: polar angle from +z axis (zenith), [0, π/2] radians for visible satellites
      * theta = 0 → zenith (straight up)
      * theta = π/2 → horizon
    - phi: azimuthal angle from North, [0, 2π) radians, CLOCKWISE
      * phi = 0 → North
      * phi = π/2 → East
      * phi = π → South
      * phi = 3π/2 → West
    - r: radial distance in meters
    """
    rx_x = rx_pos.x.magnitude
    rx_y = rx_pos.y.magnitude
    rx_z = rx_pos.z.magnitude

    # Convert receiver ECEF to geodetic (lat, lon, alt)
    lat, lon, alt = pm.ecef2geodetic(rx_x, rx_y, rx_z)

    e, n, u = pm.ecef2enu(sat_x, sat_y, sat_z, lat, lon, alt)

    # Compute spherical coordinates
    r = np.sqrt(e**2 + n**2 + u**2)

    # theta: polar angle from +z (Up) axis
    cos_theta = np.clip(u / r, -1.0, 1.0)
    theta = np.arccos(cos_theta)

    # Mask satellites below horizon
    below_horizon = (u < 0)

    # phi: azimuthal angle from NORTH (not East), clockwise
    # OLD: phi = np.arctan2(n, e)  # This gives φ=0° at East
    # NEW: Rotate by -90° so φ=0° points North
    phi = np.arctan2(e, n)  # Swap arguments: φ=0° at North, clockwise
    phi = np.mod(phi, 2 * np.pi)

    # Set below-horizon satellites to NaN
    r = np.where(below_horizon, np.nan, r)
    theta = np.where(below_horizon, np.nan, theta)
    phi = np.where(below_horizon, np.nan, phi)

    return r, theta, phi


def compute_spherical_coordinates_north_3oclock(
    sat_x: np.ndarray,
    sat_y: np.ndarray,
    sat_z: np.ndarray,
    rx_pos: ECEFPosition,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute spherical coordinates (r, theta, phi) in physics convention.

    Physics Convention (ENU frame):
    - theta: polar angle from +z axis (zenith), [0, π/2] radians for visible satellites
      * theta = 0 → zenith (straight up)
      * theta = π/2 → horizon
      * theta > π/2 → below horizon (satellite not visible)
    - phi: azimuthal angle from +x axis (East), [0, 2π) radians
    - r: radial distance in meters

    Satellites below horizon (theta > π/2) are set to NaN.
    """
    # Receiver position
    rx_x = rx_pos.x.magnitude
    rx_y = rx_pos.y.magnitude
    rx_z = rx_pos.z.magnitude

    # Convert receiver ECEF to geodetic (lat, lon, alt)
    lat, lon, alt = pm.ecef2geodetic(rx_x, rx_y, rx_z)

    # Convert satellite ECEF to ENU (East-North-Up) relative to receiver
    e, n, u = pm.ecef2enu(sat_x, sat_y, sat_z, lat, lon, alt)

    # Compute spherical coordinates
    r = np.sqrt(e**2 + n**2 + u**2)

    # theta: polar angle from +z (Up) axis
    # Clamp u/r to [-1, 1] to handle numerical errors
    cos_theta = np.clip(u / r, -1.0, 1.0)
    theta = np.arccos(cos_theta)

    # Mask satellites below horizon (u < 0 means below horizon)
    below_horizon = (u < 0)

    # phi: azimuthal angle from +x (East) axis
    phi = np.arctan2(n, e)
    phi = np.mod(phi, 2 * np.pi)

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
    Add spherical coordinates to an xarray Dataset with proper metadata.

    Parameters
    ----------
    ds : xr.Dataset
        Dataset with 'epoch' and 'sid' dimensions
    r : np.ndarray
        Radial distances [m]
    theta : np.ndarray
        Polar angles [rad]
    phi : np.ndarray
        Azimuthal angles [rad]

    Returns
    -------
    xr.Dataset
        Dataset with phi, theta, r added
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
        # "r":
        # xr.DataArray(
        #     r,
        #     coords=[ds["epoch"], ds["sid"]],
        #     dims=["epoch", "sid"],
        #     attrs={
        #         "long_name": "Distance",
        #         "short_name": "r",
        #         "units": "m",
        #         "description": "Distance between satellite and receiver",
        #     },
        # ),
    })
    return ds
