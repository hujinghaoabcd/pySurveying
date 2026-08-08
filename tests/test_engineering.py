import math

from pysurveying.engineering import (
    chainage_offset,
    grade_elevation,
    height_difference_from_slope_distance,
    horizontal_distance_from_slope,
    polygon_area,
    slope,
)


def test_polygon_area():
    assert math.isclose(polygon_area([(0, 0), (10, 0), (10, 10), (0, 10)]), 100.0)


def test_slope_percent():
    assert math.isclose(slope(100, 2), 2.0)


def test_chainage_offset_right_side():
    result = chainage_offset((3.0, 5.0), (0.0, 0.0), (0.0, 10.0))
    assert math.isclose(result["chainage"], 5.0, abs_tol=1e-12)
    assert math.isclose(result["offset"], 3.0, abs_tol=1e-12)
    assert math.isclose(result["foot_x"], 0.0, abs_tol=1e-12)
    assert math.isclose(result["foot_y"], 5.0, abs_tol=1e-12)


def test_grade_elevation():
    assert math.isclose(grade_elevation(100.0, 50.0, 2.0), 101.0)


def test_slope_distance_components():
    dh = height_difference_from_slope_distance(100.0, 30.0)
    horizontal = horizontal_distance_from_slope(100.0, 30.0)
    assert math.isclose(dh, 50.0, abs_tol=1e-12)
    assert math.isclose(horizontal, 86.6025403784, abs_tol=1e-9)
