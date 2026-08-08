# Validation notes

This project is intentionally small, so validation focuses on transparent surveying formulas, reproducible examples, and regression tests rather than a large hidden reference dataset.

## Reference workflow

The robust-estimation and gross-error-control implementation was checked against the organization used in Song Lijie's *测量平差程序设计*:

- Section 1.9: equivalent-weight functions Huber, IGG1 and IGG3
- Section 4.5: robust estimation by iteratively replacing the observation weights
- Section 4.7: gross-error detection using standardized residuals and repeated re-adjustment

The implementation follows those computational ideas while using NumPy/SciPy linear algebra instead of reproducing the book's C/C++ matrix routines.

The PDF scan available during this validation ends in Section 4.7.3. It therefore supports the robust-estimation and gross-error workflow above, but it is **not** being used as evidence for the package's traverse, leveling-network, horizontal-control-network, or instrument-format implementations. Those components require their own independently checkable examples.

## Automated checks

The test suite currently checks:

1. Huber / IGG1 / IGG3 piecewise weight factors at their interior and rejection regions.
2. Robust IRLS lowers the weight of an observation with a large standardized residual.
3. Robust IRLS moves the parameter estimate closer to the uncontaminated observations than ordinary least squares in a synthetic one-parameter example.
4. One-pass residual screening uses `Qvv` and redundancy information rather than raw residual magnitude alone.
5. Iterative linear-model gross-error screening removes the largest standardized residual, rebuilds the adjustment, and stops when the retained observations satisfy the selected threshold.
6. Error ellipses use the coordinate covariance matrix and a chi-square confidence scale; the undirected major-axis azimuth is canonicalized to `[0, 180)`.
7. A distance-only free triangle has the expected three-dimensional observable rank and reproduces all three observed side lengths after minimum-norm adjustment.
8. A redundant nonlinear distance control network exposes final-linearization `Qvv` and redundancy numbers whose sum agrees with the residual degrees of freedom.
9. `control_network_quality` maps those diagnostics back to individual observations and preserves residuals in both normalized and original observation units.
10. A mixed distance/azimuth/angle network verifies that linear residuals and angular residuals remain distinguishable in the per-observation quality report, and that the redundancy sum agrees with the residual degrees of freedom.
11. A synthetic ten-control-point distance network with one deliberately contaminated distance is re-adjusted iteratively and localizes the original gross observation index before recovering the unknown point close to its uncontaminated location.
12. Adjustment-result table/Excel export preserves quality metadata such as raw residuals, standardized residuals, redundancy numbers and robust weights when those quantities are available.

The latest diagnostic run for this validation cycle completed package installation, import, UI/example compilation, pytest, Ruff and package build successfully, with 45 tests passing.

## Important statistical scope

`iterative_data_snooping` and `control_network_data_snooping` implement computational elimination loops, not universal significance-level designs. The user remains responsible for choosing a threshold appropriate to the observation model, redundancy, false-alarm risk and applicable surveying specification.

For nonlinear control networks, `Qxx`, `Qvv`, redundancy numbers and standardized residuals are based on the final local linearization. They should be interpreted as local adjustment diagnostics rather than exact finite-nonlinearity quantities.

Likewise, covariance reported after robust equivalent weighting is a local approximation. Classical least-squares covariance interpretation does not transfer unchanged to robust estimates.

For a free 2D distance network, absolute coordinates are datum-dependent. Validation therefore compares observable internal geometry rather than expecting one unique translated/rotated coordinate realization.

## Remaining professional validation

The next validation targets are:

- published traverse examples with angular and coordinate closure
- leveling-network examples with unequal weights
- independently published mixed distance/direction/angle control-network reference examples
- gross-error localization tests involving angular observations as well as distances
- independent free-network datum checks beyond the current distance-triangle regression
- error-ellipse values against independent surveying software
- real instrument files for Leica GSI and LandXML edge cases

These should be added only when the source data and expected results are available and independently interpretable.
