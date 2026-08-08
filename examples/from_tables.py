"""Build a control network from ordinary pandas tables."""

import pandas as pd

from pysurveying import (
    adjust_control_network,
    observations_from_dataframe,
    points_from_dataframe,
)

point_table = pd.DataFrame(
    {
        "name": ["A", "B", "C", "P"],
        "x": [0.0, 100.0, 0.0, 39.0],
        "y": [0.0, 0.0, 100.0, 31.0],
        "fixed": [True, True, True, False],
    }
)

observation_table = pd.DataFrame(
    {
        "kind": ["distance", "distance", "distance"],
        "from_point": ["A", "B", "C"],
        "to_point": ["P", "P", "P"],
        "value": [50.0, 67.082039325, 80.622577483],
        "sigma": [0.01, 0.01, 0.01],
    }
)

points = points_from_dataframe(point_table)
observations = observations_from_dataframe(observation_table)
result = adjust_control_network(points, observations)

print(result.metadata["adjusted_points"])
