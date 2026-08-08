import math

from pysurveying import Observation, Point, adjust_control_network, control_network_precision


def test_control_network_precision_reports_coordinate_sigmas_and_ellipse():
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
    rows = control_network_precision(result, confidence=0.95)

    assert len(rows) == 1
    row = rows[0]
    assert row["name"] == "P"
    assert row["sigma_x"] > 0
    assert row["sigma_y"] > 0
    assert row["sigma_position"] >= max(row["sigma_x"], row["sigma_y"])
    assert row["ellipse_semi_major"] >= row["ellipse_semi_minor"] > 0
    assert 0.0 <= row["ellipse_azimuth"] < 180.0
    assert row["confidence"] == 0.95
