"""Observation quality and iterative gross-error screening for a 2D network."""

from __future__ import annotations

import math

from pysurveying import (
    Observation,
    Point,
    adjust_control_network,
    control_network_data_snooping,
    control_network_quality,
)

true_x, true_y = 40.0, 30.0
points = [Point("P", 38.0, 32.0)]
observations: list[Observation] = []
noise = [0.02, -0.01, 0.01, -0.02, 0.015, -0.015, 0.0, 0.01, -0.01, 10.0]

for index in range(10):
    angle = 2.0 * math.pi * index / 10.0
    x = 50.0 + 100.0 * math.cos(angle)
    y = 50.0 + 100.0 * math.sin(angle)
    name = f"C{index}"
    points.append(Point(name, x, y, fixed=True))
    observed = math.hypot(x - true_x, y - true_y) + noise[index]
    observations.append(Observation("distance", name, "P", observed, sigma=1.0))

ordinary = adjust_control_network(points, observations)
print("Initial adjusted point:", ordinary.metadata["adjusted_points"]["P"])
print("Initial observation quality:")
for row in control_network_quality(ordinary, observations, threshold=2.5):
    print(row)

report = control_network_data_snooping(
    points,
    observations,
    threshold=2.5,
    max_removals=2,
)
print("Removed original observation indices:", report["removed_indices"])
print("Screening history:")
for row in report["history"]:
    print(row)

final = report["result"]
if final is not None:
    print("Final adjusted point:", final.metadata["adjusted_points"]["P"])
