"""Small 2D control-network example."""

import math

from pysurveying import Observation, Point, adjust_control_network

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
print("adjusted points:", result.metadata["adjusted_points"])
print("residuals:", result.residuals)
print("sigma0:", result.sigma0)
