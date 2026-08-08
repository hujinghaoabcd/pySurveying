"""Robust equivalent weights and iterative gross-error screening."""

import numpy as np

from pysurveying import (
    iterative_data_snooping,
    least_squares,
    robust_least_squares_irls,
)

A = np.ones((8, 1))
L = np.array([10.00, 10.01, 9.99, 10.02, 9.98, 10.00, 10.01, 20.00])

ordinary = least_squares(A, L)
robust = robust_least_squares_irls(A, L, method="igg3", k0=1.0, k1=2.8)
snooping = iterative_data_snooping(A, L, threshold=2.5)

print("ordinary:", ordinary.parameters)
print("robust:", robust.parameters)
print("robust weights:", robust.metadata["robust_weights"])
print("removed observations:", snooping["removed_indices"])
print("final:", snooping["result"].parameters)
