import math

from pysurveying.leveling import leveling_network, leveling_route
from pysurveying.models import LevelObservation


def test_leveling_route_closes():
    result = leveling_route(10.0, [1.0, -0.4, -0.61], end_height=10.0)
    assert math.isclose(result["heights"][-1], 10.0, abs_tol=1e-12)


def test_leveling_network():
    observations = [
        LevelObservation("BM", "A", 1.0, sigma=0.001),
        LevelObservation("A", "B", 2.0, sigma=0.001),
        LevelObservation("BM", "B", 3.001, sigma=0.001),
    ]
    result = leveling_network(observations, {"BM": 100.0})
    heights = result.metadata["adjusted_heights"]
    assert math.isclose(heights["A"], 101.0003333333, abs_tol=1e-6)
    assert math.isclose(heights["B"], 103.0006666667, abs_tol=1e-6)
    assert result.dof == 1
