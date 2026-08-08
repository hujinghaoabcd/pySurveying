import math

from pysurveying.traverse import (
    adjust_angles,
    closed_traverse,
    closed_traverse_from_angles,
    connected_traverse,
)


def test_closed_square():
    result = closed_traverse((0, 0), [90, 0, 270, 180], [100, 100, 100, 100])
    assert math.isclose(result["linear_misclosure"], 0.0, abs_tol=1e-10)
    assert math.isclose(result["coordinates"][-1][0], 0.0, abs_tol=1e-10)
    assert math.isclose(result["coordinates"][-1][1], 0.0, abs_tol=1e-10)


def test_connected_traverse_hits_endpoint():
    result = connected_traverse((0, 0), (100, 100), [90, 0], [100, 100])
    x, y = result["coordinates"][-1]
    assert math.isclose(x, 100.0, abs_tol=1e-10)
    assert math.isclose(y, 100.0, abs_tol=1e-10)


def test_adjust_angles_closes_polygon():
    result = adjust_angles([90.01, 89.99, 90.02, 90.00])
    assert math.isclose(sum(result["adjusted_angles"]), 360.0, abs_tol=1e-12)
    assert math.isclose(sum(result["corrections"]), -0.02, abs_tol=1e-12)


def test_closed_traverse_from_angles():
    result = closed_traverse_from_angles(
        (0.0, 0.0),
        90.0,
        [90.0, 90.0, 90.0, 90.0],
        [100.0, 100.0, 100.0, 100.0],
        turn="right",
    )
    assert math.isclose(result["linear_misclosure"], 0.0, abs_tol=1e-10)
    assert math.isclose(result["direction_misclosure"], 0.0, abs_tol=1e-10)
