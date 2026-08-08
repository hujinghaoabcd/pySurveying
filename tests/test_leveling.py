import math

from pysurveying.leveling import leveling_route


def test_leveling_route_closes():
    result = leveling_route(10.0, [1.0, -0.4, -0.61], end_height=10.0)
    assert math.isclose(result["heights"][-1], 10.0, abs_tol=1e-12)
