import math

import numpy as np

from pysurveying.adjustment import least_squares
from pysurveying.quality import data_snooping, error_ellipse, robust_least_squares


def test_error_ellipse_axes():
    result = error_ellipse(np.diag([4.0, 1.0]), confidence=0.95)
    assert result["semi_major"] > result["semi_minor"] > 0


def test_huber_reduces_outlier_influence():
    A = np.ones((5, 1))
    L = np.array([10.0, 10.0, 10.0, 10.0, 30.0])
    result = robust_least_squares(A, L, f_scale=1.0)
    assert math.isclose(result.parameters[0], 10.25, abs_tol=0.3)


def test_data_snooping_uses_redundancy():
    A = np.ones((5, 1))
    L = np.array([10.0, 10.0, 10.0, 10.0, 20.0])
    result = least_squares(A, L)
    rows = data_snooping(result, threshold=1.5)
    assert len(rows) == 5
    assert rows[-1]["flagged"]
    assert 0.0 <= rows[-1]["redundancy"] <= 1.0
