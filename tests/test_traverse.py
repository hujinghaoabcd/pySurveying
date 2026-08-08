import math

from pysurveying.traverse import closed_traverse, connected_traverse


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
