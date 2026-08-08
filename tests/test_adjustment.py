import numpy as np

from pysurveying.adjustment import least_squares


def test_least_squares_mean():
    A = np.ones((3, 1))
    L = np.array([10.01, 9.99, 10.00])
    result = least_squares(A, L)
    assert np.allclose(result.parameters, [10.0])
    assert result.dof == 2
    assert result.sigma0 is not None


def test_weighted_least_squares():
    A = np.ones((2, 1))
    L = np.array([10.0, 20.0])
    result = least_squares(A, L, P=[9.0, 1.0])
    assert np.allclose(result.parameters, [11.0])
