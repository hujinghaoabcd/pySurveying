"""Reference-backed parameter-adjustment examples from 宋力杰《测量平差程序设计》.

The two examples reproduce Sections 3.1.5 and 3.2.5 using the package's
``least_squares`` routine. They are also covered by automated regression tests.
"""

from __future__ import annotations

import numpy as np

from pysurveying import least_squares


EXPECTED_QXX = np.array(
    [
        [0.3888888889, 0.2777777778, 0.0555555556],
        [0.2777777778, 0.5555555556, 0.1111111111],
        [0.0555555556, 0.1111111111, 0.2222222222],
    ]
)


def independent_observations():
    """Section 3.1.5: independent weighted parameter adjustment."""
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
    P = np.array([1.0, 1.0, 2.0, 1.0, 2.0, 2.0])
    return least_squares(A, L, P=P)


def correlated_observations():
    """Section 3.2.5: parameter adjustment with a full correlated weight matrix."""
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
    return least_squares(A, L, P=P)


def _print_result(title, result):
    print(title)
    print("X =", np.round(result.parameters, 10))
    print("V =", np.round(result.residuals, 10))
    print("sigma0 =", result.sigma0)
    print("Qxx =\n", np.round(result.metadata["qxx"], 10))
    print()


if __name__ == "__main__":
    _print_result("Section 3.1.5 — independent observations", independent_observations())
    _print_result("Section 3.2.5 — correlated observations", correlated_observations())
    print("Expected X = [2, 1, -4], sigma0 = 6")
    print("Expected Qxx =\n", EXPECTED_QXX)
