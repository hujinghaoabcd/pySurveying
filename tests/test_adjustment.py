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


def _song_expected_qxx():
    return np.array(
        [
            [0.3888888889, 0.2777777778, 0.0555555556],
            [0.2777777778, 0.5555555556, 0.1111111111],
            [0.0555555556, 0.1111111111, 0.2222222222],
        ]
    )


def test_song_lijie_parameter_adjustment_example():
    """Regression against Section 3.1.5 of 测量平差程序设计."""
    A = np.array(
        [
            [1.0, 0.0, 0.0],
            [-1.0, 0.0, 0.0],
            [-1.0, 1.0, 0.0],
            [0.0, 1.0, -1.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0],
        ]
    )
    L = np.array([0.0, -6.0, 0.0, 3.0, 0.0, -9.0])
    weights = np.array([1.0, 1.0, 2.0, 1.0, 2.0, 2.0])

    result = least_squares(A, L, P=weights)

    assert np.allclose(result.parameters, [2.0, 1.0, -4.0], atol=1e-10)
    assert np.allclose(result.residuals, [2.0, 4.0, -1.0, 2.0, -4.0, 5.0], atol=1e-10)
    assert np.isclose(result.sigma0, 6.0, atol=1e-10)
    assert np.allclose(result.metadata["qxx"], _song_expected_qxx(), atol=1e-8)


def test_song_lijie_correlated_parameter_adjustment_example():
    """Regression against Section 3.2.5 with a full correlated weight matrix."""
    A = np.array(
        [
            [1.0, 0.0, 0.0],
            [-2.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [1.0, 0.0, -1.0],
            [0.0, -1.0, 2.0],
            [0.0, 0.0, 1.0],
        ]
    )
    L = np.array([0.0, -6.0, 6.0, 3.0, -3.0, -18.0])
    P = np.array(
        [
            [7.5, 6.5, 5.5, 3.5, 2.5, 0.5],
            [6.5, 6.5, 5.5, 3.5, 2.5, 0.5],
            [5.5, 5.5, 5.5, 3.5, 2.5, 0.5],
            [3.5, 3.5, 3.5, 3.5, 2.5, 0.5],
            [2.5, 2.5, 2.5, 2.5, 2.5, 0.5],
            [0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
        ]
    )

    result = least_squares(A, L, P=P)

    assert np.allclose(result.parameters, [2.0, 1.0, -4.0], atol=1e-10)
    assert np.allclose(result.residuals, [2.0, 2.0, -5.0, 3.0, -6.0, 14.0], atol=1e-10)
    assert np.isclose(result.sigma0, 6.0, atol=1e-10)
    assert np.allclose(result.metadata["qxx"], _song_expected_qxx(), atol=1e-8)
