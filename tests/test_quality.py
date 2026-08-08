import math

import numpy as np

from pysurveying.adjustment import least_squares
from pysurveying.quality import (
    data_snooping,
    equivalent_weight_factor,
    error_ellipse,
    iterative_data_snooping,
    robust_least_squares,
    robust_least_squares_irls,
)


def test_error_ellipse_axes():
    result = error_ellipse(np.diag([4.0, 1.0]), confidence=0.95)
    assert result["semi_major"] > result["semi_minor"] > 0
    assert math.isclose(result["semi_major"] / result["semi_minor"], 2.0, rel_tol=1e-12)
    assert math.isclose(result["azimuth"], 90.0, abs_tol=1e-12)
    assert 0.0 <= result["azimuth"] < 180.0


def test_error_ellipse_axis_uses_180_degree_equivalence():
    covariance = np.array([[2.5, 1.5], [1.5, 2.5]])
    result = error_ellipse(covariance, confidence=0.95)
    assert 0.0 <= result["azimuth"] < 180.0
    assert math.isclose(result["azimuth"], 45.0, abs_tol=1e-12)


def test_huber_reduces_outlier_influence():
    A = np.ones((5, 1))
    L = np.array([10.0, 10.0, 10.0, 10.0, 30.0])
    result = robust_least_squares(A, L, f_scale=1.0)
    assert math.isclose(result.parameters[0], 10.25, abs_tol=0.3)


def test_equivalent_weight_functions_match_piecewise_definitions():
    assert equivalent_weight_factor(0.5, method="huber", k0=1.5) == 1.0
    assert math.isclose(
        equivalent_weight_factor(3.0, method="huber", k0=1.5),
        0.5,
    )
    assert math.isclose(
        equivalent_weight_factor(2.0, method="igg1", k0=1.5, k1=2.5),
        0.75,
    )
    assert equivalent_weight_factor(2.5, method="igg1", k0=1.5, k1=2.5) == 0.0
    assert math.isclose(
        equivalent_weight_factor(2.0, method="igg3", k0=1.5, k1=2.5),
        0.1875,
    )


def test_surveying_irls_downweights_gross_residual():
    A = np.ones((8, 1))
    L = np.array([10.00, 10.01, 9.99, 10.02, 9.98, 10.00, 10.01, 12.00])
    ordinary = least_squares(A, L)
    robust = robust_least_squares_irls(
        A,
        L,
        method="igg3",
        k0=1.0,
        k1=2.8,
    )
    weights = np.asarray(robust.metadata["robust_weights"])
    assert weights[-1] < np.median(weights[:-1])
    assert abs(robust.parameters[0] - 10.0) < abs(ordinary.parameters[0] - 10.0)


def test_data_snooping_uses_redundancy():
    A = np.ones((5, 1))
    L = np.array([10.0, 10.0, 10.0, 10.0, 20.0])
    result = least_squares(A, L)
    rows = data_snooping(result, threshold=1.5)
    assert len(rows) == 5
    assert rows[-1]["flagged"]
    assert 0.0 <= rows[-1]["redundancy"] <= 1.0


def test_iterative_data_snooping_removes_largest_gross_error():
    A = np.ones((8, 1))
    L = np.array([10.00, 10.01, 9.99, 10.02, 9.98, 10.00, 10.01, 20.00])
    report = iterative_data_snooping(A, L, threshold=2.5)
    assert report["removed_indices"] == [7]
    assert report["converged"]
    final = report["result"]
    assert final is not None
    assert math.isclose(final.parameters[0], 10.0014, abs_tol=0.01)
