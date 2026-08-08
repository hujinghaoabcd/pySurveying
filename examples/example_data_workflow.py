"""Run the reusable CSV examples shipped with pySurveying."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from pysurveying import (
    adjust_control_network,
    closed_traverse_from_angles,
    control_network_precision,
    control_network_quality,
    level_observations_from_dataframe,
    leveling_network,
    observations_from_dataframe,
    points_from_dataframe,
)

DATA = Path(__file__).with_name("data")


# 2D control network
point_table = pd.read_csv(DATA / "control_points.csv")
observation_table = pd.read_csv(DATA / "control_observations.csv")
network = adjust_control_network(
    points_from_dataframe(point_table),
    observations_from_dataframe(observation_table),
)
print("Adjusted control-network points:")
print(network.metadata["adjusted_points"])
print("Observation quality:")
for row in control_network_quality(network, observations_from_dataframe(observation_table)):
    print(row)
print("Point precision:")
for row in control_network_precision(network):
    print(row)


# Leveling network with unequal observation precision
fixed_table = pd.read_csv(DATA / "leveling_fixed.csv")
level_table = pd.read_csv(DATA / "leveling_observations.csv")
fixed_heights = dict(zip(fixed_table["name"], fixed_table["height"]))
level_result = leveling_network(
    level_observations_from_dataframe(level_table),
    fixed_heights,
)
print("\nAdjusted heights:")
print(level_result.metadata["adjusted_heights"])


# Closed traverse from measured interior angles
table = pd.read_csv(DATA / "traverse_angles.csv")
traverse = closed_traverse_from_angles(
    start=(0.0, 0.0),
    start_azimuth_deg=90.0,
    interior_angles_deg=table["angle_deg"],
    distances=table["distance"],
)
print("\nTraverse angular misclosure:", traverse["angle_adjustment"]["misclosure"])
print("Traverse linear misclosure:", traverse["linear_misclosure"])
print("Adjusted traverse coordinates:")
for coordinate in traverse["coordinates"]:
    print(coordinate)
