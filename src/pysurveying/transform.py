from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np
from pyproj import CRS, Transformer


def transform_coordinates(
    x: float | Sequence[float],
    y: float | Sequence[float],
    from_crs: str | int,
    to_crs: str | int,
    *,
    always_xy: bool = True,
):
    """Transform one coordinate or coordinate arrays between two CRS definitions."""
    transformer = Transformer.from_crs(
        CRS.from_user_input(from_crs),
        CRS.from_user_input(to_crs),
        always_xy=always_xy,
    )
    return transformer.transform(x, y)


def geodetic_to_ecef(lon: float, lat: float, height: float = 0.0) -> tuple[float, float, float]:
    """Convert WGS84 longitude, latitude and ellipsoidal height to ECEF XYZ."""
    transformer = Transformer.from_crs("EPSG:4979", "EPSG:4978", always_xy=True)
    x, y, z = transformer.transform(lon, lat, height)
    return float(x), float(y), float(z)


def ecef_to_geodetic(x: float, y: float, z: float) -> tuple[float, float, float]:
    """Convert WGS84 ECEF XYZ to longitude, latitude and ellipsoidal height."""
    transformer = Transformer.from_crs("EPSG:4978", "EPSG:4979", always_xy=True)
    lon, lat, height = transformer.transform(x, y, z)
    return float(lon), float(lat), float(height)


def _ecef_to_enu_rotation(lon0: float, lat0: float) -> np.ndarray:
    lon = math.radians(lon0)
    lat = math.radians(lat0)
    return np.array(
        [
            [-math.sin(lon), math.cos(lon), 0.0],
            [
                -math.sin(lat) * math.cos(lon),
                -math.sin(lat) * math.sin(lon),
                math.cos(lat),
            ],
            [
                math.cos(lat) * math.cos(lon),
                math.cos(lat) * math.sin(lon),
                math.sin(lat),
            ],
        ],
        dtype=float,
    )


def ecef_to_enu(
    x: float,
    y: float,
    z: float,
    lon0: float,
    lat0: float,
    height0: float = 0.0,
) -> tuple[float, float, float]:
    """Convert ECEF XYZ to local east, north, up coordinates."""
    origin = np.asarray(geodetic_to_ecef(lon0, lat0, height0), dtype=float)
    delta = np.asarray([x, y, z], dtype=float) - origin
    east, north, up = _ecef_to_enu_rotation(lon0, lat0) @ delta
    return float(east), float(north), float(up)


def enu_to_ecef(
    east: float,
    north: float,
    up: float,
    lon0: float,
    lat0: float,
    height0: float = 0.0,
) -> tuple[float, float, float]:
    """Convert local east, north, up coordinates to WGS84 ECEF XYZ."""
    origin = np.asarray(geodetic_to_ecef(lon0, lat0, height0), dtype=float)
    local = np.asarray([east, north, up], dtype=float)
    xyz = origin + _ecef_to_enu_rotation(lon0, lat0).T @ local
    return float(xyz[0]), float(xyz[1]), float(xyz[2])


def geodetic_to_enu(
    lon: float,
    lat: float,
    height: float,
    lon0: float,
    lat0: float,
    height0: float = 0.0,
) -> tuple[float, float, float]:
    """Convert WGS84 geodetic coordinates directly to a local ENU frame."""
    return ecef_to_enu(*geodetic_to_ecef(lon, lat, height), lon0, lat0, height0)


def enu_to_geodetic(
    east: float,
    north: float,
    up: float,
    lon0: float,
    lat0: float,
    height0: float = 0.0,
) -> tuple[float, float, float]:
    """Convert local ENU coordinates directly to WGS84 geodetic coordinates."""
    return ecef_to_geodetic(*enu_to_ecef(east, north, up, lon0, lat0, height0))
