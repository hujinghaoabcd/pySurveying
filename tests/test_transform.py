import math

from pysurveying.transform import (
    ecef_to_geodetic,
    enu_to_geodetic,
    geodetic_to_ecef,
    geodetic_to_enu,
)


def test_geodetic_ecef_roundtrip():
    xyz = geodetic_to_ecef(118.7969, 32.0603, 25.0)
    lon, lat, height = ecef_to_geodetic(*xyz)
    assert math.isclose(lon, 118.7969, abs_tol=1e-9)
    assert math.isclose(lat, 32.0603, abs_tol=1e-9)
    assert math.isclose(height, 25.0, abs_tol=1e-5)


def test_enu_origin_and_roundtrip():
    enu = geodetic_to_enu(118.7969, 32.0603, 25.0, 118.7969, 32.0603, 25.0)
    assert all(abs(value) < 1e-6 for value in enu)

    lon, lat, height = enu_to_geodetic(10.0, 20.0, 5.0, 118.7969, 32.0603, 25.0)
    back = geodetic_to_enu(lon, lat, height, 118.7969, 32.0603, 25.0)
    assert math.isclose(back[0], 10.0, abs_tol=1e-5)
    assert math.isclose(back[1], 20.0, abs_tol=1e-5)
    assert math.isclose(back[2], 5.0, abs_tol=1e-5)
