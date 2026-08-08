import math

import numpy as np

from pysurveying.adjustment import (
    adjust_control_network,
    adjust_control_network_robust,
    adjust_free_network,
)
from pysurveying.models import Observation, Point
from pysurveying.quality import control_network_data_snooping, control_network_quality


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


def test_free_network_preserves_observed_triangle_geometry():
    points = [
        Point("A", 2.0, -1.0),
        Point("B", 98.0, 3.0),
        Point("C", 42.0, 68.0),
    ]
    expected = {
        ("A", "B"): 100.0,
        ("A", "C"): math.hypot(40.0, 70.0),
        ("B", "C"): math.hypot(60.0, 70.0),
    }
    observations = [
        Observation("distance", start, end, value, sigma=0.01)
        for (start, end), value in expected.items()
    ]

    result = adjust_free_network(points, observations)
    adjusted = result.metadata["adjusted_points"]

    assert result.converged
    assert result.metadata["free_network"]
    assert result.metadata["rank"] == 3
    assert len(result.parameters) == 6
    for (start, end), value in expected.items():
        x1, y1 = adjusted[start]
        x2, y2 = adjusted[end]
        calculated = math.hypot(x2 - x1, y2 - y1)
        assert math.isclose(calculated, value, abs_tol=1e-7)


def test_control_network_exposes_qvv_and_redundancy():
    points = [
        Point("A", 0.0, 0.0, fixed=True),
        Point("B", 100.0, 0.0, fixed=True),
        Point("C", 0.0, 100.0, fixed=True),
        Point("D", 100.0, 100.0, fixed=True),
        Point("P", 39.0, 31.0),
    ]
    observations = [
        Observation("distance", "A", "P", 50.01, sigma=0.02),
        Observation("distance", "B", "P", math.hypot(60.0, 30.0) - 0.01, sigma=0.02),
        Observation("distance", "C", "P", math.hypot(40.0, 70.0) + 0.02, sigma=0.02),
        Observation("distance", "D", "P", math.hypot(60.0, 70.0) - 0.02, sigma=0.02),
    ]

    result = adjust_control_network(points, observations)
    qvv = np.asarray(result.metadata["qvv"])
    redundancy = np.asarray(result.metadata["redundancy_numbers"])
    rows = control_network_quality(result, observations, threshold=3.0)

    assert qvv.shape == (4, 4)
    assert redundancy.shape == (4,)
    assert np.all((0.0 <= redundancy) & (redundancy <= 1.0))
    assert math.isclose(float(redundancy.sum()), result.dof, rel_tol=1e-6, abs_tol=1e-6)
    assert len(rows) == 4
    assert all(row["kind"] == "distance" for row in rows)
    assert all("standardized_residual" in row for row in rows)


def test_control_network_data_snooping_locates_gross_distance():
    true_x, true_y = 40.0, 30.0
    points = [Point("P", 38.0, 32.0)]
    observations = []
    noise = [0.02, -0.01, 0.01, -0.02, 0.015, -0.015, 0.0, 0.01, -0.01, 10.0]

    for index in range(10):
        angle = 2.0 * math.pi * index / 10.0
        x = 50.0 + 100.0 * math.cos(angle)
        y = 50.0 + 100.0 * math.sin(angle)
        name = f"C{index}"
        points.append(Point(name, x, y, fixed=True))
        observed = math.hypot(x - true_x, y - true_y) + noise[index]
        observations.append(Observation("distance", name, "P", observed, sigma=1.0))

    report = control_network_data_snooping(
        points,
        observations,
        threshold=2.5,
        max_removals=2,
    )
    result = report["result"]
    assert result is not None
    assert report["removed_indices"] == [9]
    assert report["converged"]
    assert report["history"][0]["kind"] == "distance"
    x, y = result.metadata["adjusted_points"]["P"]
    assert math.isclose(x, true_x, abs_tol=0.02)
    assert math.isclose(y, true_y, abs_tol=0.02)
