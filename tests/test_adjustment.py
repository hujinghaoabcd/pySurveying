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


def test_song_lijie_parameter_adjustment_example():
    """Regression against Section 3.1.5 of 测量平差程序设计.

    The textbook writes the residual model in the same practical form used by
    ``least_squares`` here: ``V = A X - L``. Its six independent observations have
    weights 1, 1, 2, 1, 2, 2 and the printed solution is X=(2, 1, -4),
    V=(2, 4, -1, 2, -4, 5), sigma0=6.
    """
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

    expected_qxx = np.array(
        [
            [0.3888888889, 0.2777777778, 0.0555555556],
            [0.2777777778, 0.5555555556, 0.1111111111],
            [0.0555555556, 0.1111111111, 0.2222222222],
        ]
    )
    assert np.allclose(result.parameters, [2.0, 1.0, -4.0], atol=1e-10)
    assert np.allclose(result.residuals, [2.0, 4.0, -1.0, 2.0, -4.0, 5.0], atol=1e-10)
    assert np.isclose(result.sigma0, 6.0, atol=1e-10)
    assert np.allclose(result.metadata["qxx"], expected_qxx, atol=1e-8)
