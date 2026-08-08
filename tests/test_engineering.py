import math

from pysurveying.engineering import polygon_area, slope


def test_polygon_area():
    assert math.isclose(polygon_area([(0, 0), (10, 0), (10, 10), (0, 10)]), 100.0)


def test_slope_percent():
    assert math.isclose(slope(100, 2), 2.0)
