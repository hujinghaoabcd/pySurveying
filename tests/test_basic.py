import math

from pysurveying.basic import (
    azimuth,
    distance,
    distance_intersection,
    forward_coordinate,
    forward_intersection,
)


def test_distance_and_azimuth():
    assert math.isclose(distance((0, 0), (3, 4)), 5.0)
    assert math.isclose(azimuth((0, 0), (0, 10)), 0.0)
    assert math.isclose(azimuth((0, 0), (10, 0)), 90.0)


def test_forward_coordinate():
    x, y = forward_coordinate(0, 0, 90, 10)
    assert math.isclose(x, 10.0, abs_tol=1e-10)
    assert math.isclose(y, 0.0, abs_tol=1e-10)


def test_forward_intersection():
    x, y = forward_intersection((0, 0), 45, (100, 0), 315)
    assert math.isclose(x, 50.0, abs_tol=1e-8)
    assert math.isclose(y, 50.0, abs_tol=1e-8)


def test_distance_intersection():
    q1, q2 = distance_intersection((0, 0), 5, (6, 0), 5)
    assert q2 is not None
    assert math.isclose(q1[0], 3.0, abs_tol=1e-10)
    assert math.isclose(abs(q1[1]), 4.0, abs_tol=1e-10)
