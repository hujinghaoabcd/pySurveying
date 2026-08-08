import math

from pysurveying.adjustment import adjust_control_network, adjust_control_network_robust
from pysurveying.models import Observation, Point


def test_distance_control_network():
    points = [
        Point("A", 0.0, 0.0, fixed=True),
        Point("B", 100.0, 0.0, fixed=True),
        Point("C", 0.0, 100.0, fixed=True),
        Point("P", 39.0, 31.0),
    ]
    observations = [
        Observation("distance", "A", "P", 50.0, sigma=0.01),
        Observation("distance", "B", "P", math.hypot(60.0, 30.0), sigma=0.01),
        Observation("distance", "C", "P", math.hypot(40.0, 70.0), sigma=0.01),
    ]

    result = adjust_control_network(points, observations)
    x, y = result.metadata["adjusted_points"]["P"]
    assert result.converged
    assert math.isclose(x, 40.0, abs_tol=1e-6)
    assert math.isclose(y, 30.0, abs_tol=1e-6)


def test_direction_set_solves_station_orientation():
    points = [
        Point("A", 0.0, 0.0, fixed=True),
        Point("B", 0.0, 100.0, fixed=True),
        Point("P", 48.0, 52.0),
    ]
    observations = [
        Observation("direction", "A", "B", 10.0, sigma=0.001),
        Observation("direction", "A", "P", 55.0, sigma=0.001),
        Observation("distance", "A", "P", math.hypot(50.0, 50.0), sigma=0.01),
    ]

    result = adjust_control_network(points, observations)
    x, y = result.metadata["adjusted_points"]["P"]
    orientation = result.metadata["orientations"]["A"]

    assert result.converged
    assert math.isclose(x, 50.0, abs_tol=1e-5)
    assert math.isclose(y, 50.0, abs_tol=1e-5)
    assert math.isclose(orientation, 350.0, abs_tol=1e-5)


def test_robust_network_reduces_outlier_effect():
    points = [
        Point("A", 0.0, 0.0, fixed=True),
        Point("B", 100.0, 0.0, fixed=True),
        Point("C", 0.0, 100.0, fixed=True),
        Point("D", 100.0, 100.0, fixed=True),
        Point("P", 38.0, 32.0),
    ]
    true_x, true_y = 40.0, 30.0
    observations = [
        Observation("distance", "A", "P", math.hypot(40.0, 30.0), sigma=1.0),
        Observation("distance", "B", "P", math.hypot(60.0, 30.0), sigma=1.0),
        Observation("distance", "C", "P", math.hypot(40.0, 70.0), sigma=1.0),
        Observation("distance", "D", "P", math.hypot(60.0, 70.0) + 10.0, sigma=1.0),
    ]

    ordinary = adjust_control_network(points, observations)
    robust = adjust_control_network_robust(points, observations, huber_k=1.5)
    ox, oy = ordinary.metadata["adjusted_points"]["P"]
    rx, ry = robust.metadata["adjusted_points"]["P"]
    ordinary_error = math.hypot(ox - true_x, oy - true_y)
    robust_error = math.hypot(rx - true_x, ry - true_y)

    assert robust.converged
    assert robust_error < ordinary_error
    assert min(robust.metadata["robust_weights"]) < 1.0
