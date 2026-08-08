from pathlib import Path

import numpy as np
import pandas as pd

from pysurveying import (
    adjust_control_network,
    closed_traverse_from_angles,
    level_observations_from_dataframe,
    leveling_network,
    observations_from_dataframe,
    points_from_dataframe,
)


DATA = Path(__file__).parents[1] / "examples" / "data"


def test_control_network_example_data_recovers_unknown_point():
    points = points_from_dataframe(pd.read_csv(DATA / "control_points.csv"))
    observations = observations_from_dataframe(pd.read_csv(DATA / "control_observations.csv"))
    result = adjust_control_network(points, observations)

    assert result.converged
    assert np.allclose(result.metadata["adjusted_points"]["P"], [40.0, 30.0], atol=1e-7)


def test_leveling_example_data_is_redundant_and_adjusts():
    fixed = pd.read_csv(DATA / "leveling_fixed.csv")
    fixed_heights = dict(zip(fixed["name"], fixed["height"]))
    observations = level_observations_from_dataframe(
        pd.read_csv(DATA / "leveling_observations.csv")
    )
    result = leveling_network(observations, fixed_heights)

    assert result.dof == 1
    assert result.sigma0 is not None
    assert abs(result.metadata["adjusted_heights"]["A"] - 101.0) < 0.001
    assert abs(result.metadata["adjusted_heights"]["B"] - 103.0) < 0.001


def test_traverse_example_data_closes_after_adjustment():
    table = pd.read_csv(DATA / "traverse_angles.csv")
    result = closed_traverse_from_angles(
        start=(0.0, 0.0),
        start_azimuth_deg=90.0,
        interior_angles_deg=table["angle_deg"],
        distances=table["distance"],
    )

    assert np.isclose(sum(result["angle_adjustment"]["adjusted_angles"]), 360.0)
    assert np.allclose(result["coordinates"][-1], [0.0, 0.0], atol=1e-10)
