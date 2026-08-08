import math

import numpy as np

from pysurveying.transform import (
    apply_affine_2d,
    apply_similarity_2d,
    ecef_to_geodetic,
    enu_to_geodetic,
    fit_affine_2d,
    fit_similarity_2d,
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


def test_similarity_fit_and_apply():
    source = np.array([[0.0, 0.0], [10.0, 0.0], [0.0, 10.0], [10.0, 10.0]])
    scale = 2.0
    rotation = math.radians(30.0)
    parameters = [100.0, 200.0, scale * math.cos(rotation), scale * math.sin(rotation)]
    target = apply_similarity_2d(source, parameters)

    fitted = fit_similarity_2d(source, target)
    assert np.allclose(fitted["parameters"], parameters, atol=1e-10)
    assert math.isclose(fitted["scale"], 2.0, abs_tol=1e-10)
    assert math.isclose(fitted["rotation_deg"], 30.0, abs_tol=1e-10)
    assert fitted["rmse"] < 1e-10


def test_affine_fit_and_apply():
    source = np.array([[0.0, 0.0], [10.0, 0.0], [0.0, 10.0], [10.0, 10.0]])
    parameters = [5.0, 1.2, 0.1, -3.0, -0.2, 0.9]
    target = apply_affine_2d(source, parameters)
    fitted = fit_affine_2d(source, target)
    assert np.allclose(fitted["parameters"], parameters, atol=1e-10)
    assert fitted["rmse"] < 1e-10
